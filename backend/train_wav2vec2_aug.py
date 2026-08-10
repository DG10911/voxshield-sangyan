import os, csv, time, argparse, random
from pathlib import Path
import numpy as np, torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
import soundfile as sf
from transformers import Wav2Vec2ForSequenceClassification
from sklearn.metrics import roc_auc_score, roc_curve
from telephony_aug import telephony_augment

SR, CLIP_SEC = 16000, 3.0
CLIP_LEN = int(SR * CLIP_SEC)

def load_clip(path):
    y, sr = sf.read(path)
    if y.ndim > 1: y = y.mean(1)
    y = y.astype("float32")
    if sr != SR:
        import torchaudio.functional as F
        y = F.resample(torch.from_numpy(y), sr, SR).numpy()
    if len(y) < CLIP_LEN:
        y = np.pad(y, (0, CLIP_LEN - len(y)))
    elif len(y) > CLIP_LEN:
        s = random.randint(0, len(y) - CLIP_LEN); y = y[s:s+CLIP_LEN]
    return y

class ITW(Dataset):
    def __init__(self, csv_path, augment=False, force_codec=False):
        self.rows = list(csv.DictReader(open(csv_path)))
        self.augment = augment
        self.force_codec = force_codec
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        r = self.rows[i]
        try: y = load_clip(r["path"])
        except Exception: y = np.zeros(CLIP_LEN, np.float32)
        if self.augment:
            y = telephony_augment(y, p=0.5)
        elif self.force_codec:
            y = telephony_augment(y, p=1.0)
        return torch.from_numpy(y), int(r["label"])

def eer(y_true, y_score):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    fnr = 1 - tpr
    idx = np.nanargmin(np.abs(fpr - fnr))
    return float((fpr[idx] + fnr[idx]) / 2)

def run_eval(model, loader, tag, device):
    model.eval(); scores, ys = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device, non_blocking=True)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_values=x).logits
            p = torch.softmax(logits, -1)[:, 1].float().cpu().numpy()
            scores.extend(p.tolist()); ys.extend(y.numpy().tolist())
    e = eer(np.array(ys), np.array(scores))
    a = roc_auc_score(ys, scores)
    print(f"    [{tag:12s}] EER={e*100:.2f}%  AUC={a*100:.2f}%")
    return e, a

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="manifests_dgx/itw_train_speakerdisjoint.csv")
    ap.add_argument("--test",  default="manifests_dgx/itw_test_speakerdisjoint.csv")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--model", default="facebook/wav2vec2-large-xlsr-53")
    ap.add_argument("--out", default=os.path.expanduser("~/checkpoints/voxshield/wav2vec2_xlsr_itw_aug"))
    args = ap.parse_args()

    device = torch.device("cuda")
    Path(args.out).mkdir(parents=True, exist_ok=True)
    print(f"[setup] device={device} out={args.out}")

    train_ds = ITW(args.train, augment=True)
    test_clean = ITW(args.test, augment=False)
    test_codec = ITW(args.test, force_codec=True)
    print(f"[data] train={len(train_ds)} test={len(test_clean)}")

    labels = np.array([int(r["label"]) for r in train_ds.rows])
    w = 1.0 / np.bincount(labels)[labels]
    sampler = WeightedRandomSampler(w, num_samples=len(train_ds), replacement=True)

    tl = DataLoader(train_ds, batch_size=args.bs, sampler=sampler,
                    num_workers=8, pin_memory=True, persistent_workers=True)
    vl_clean = DataLoader(test_clean, batch_size=args.bs, shuffle=False,
                          num_workers=4, pin_memory=True, persistent_workers=True)
    vl_codec = DataLoader(test_codec, batch_size=args.bs, shuffle=False,
                          num_workers=4, pin_memory=True, persistent_workers=True)

    print(f"[model] loading {args.model}")
    model = Wav2Vec2ForSequenceClassification.from_pretrained(
        args.model, num_labels=2, ignore_mismatched_sizes=True)
    model.freeze_feature_encoder()
    model.gradient_checkpointing_enable()
    model.to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs * len(tl))

    best_codec = 1.0
    for ep in range(args.epochs):
        model.train(); t0 = time.time(); losses = []
        for i, (x, y) in enumerate(tl):
            x = x.to(device, non_blocking=True); y = y.to(device, non_blocking=True)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = model(input_values=x, labels=y).loss
            opt.zero_grad(set_to_none=True)
            loss.backward(); opt.step(); sch.step()
            losses.append(loss.item())
            if i % 20 == 0:
                print(f"[e{ep} s{i:04d}/{len(tl)}] loss={loss.item():.4f} lr={sch.get_last_lr()[0]:.2e} t={time.time()-t0:.0f}s")
        print(f"[e{ep}] eval:")
        e_clean, a_clean = run_eval(model, vl_clean, "clean", device)
        e_codec, a_codec = run_eval(model, vl_codec, "G.711 8kHz", device)
        print(f"[e{ep}] epoch time={time.time()-t0:.0f}s  train_loss={np.mean(losses):.4f}")
        payload = {"model": model.state_dict(), "epoch": ep,
                   "eer_clean": e_clean, "eer_codec": e_codec,
                   "auc_clean": a_clean, "auc_codec": a_codec, "cfg": vars(args)}
        torch.save(payload, f"{args.out}/last.pt")
        if e_codec < best_codec:
            best_codec = e_codec
            torch.save(payload, f"{args.out}/best.pt")
            print(f"[e{ep}] *** NEW BEST CODEC EER = {e_codec*100:.2f}% ***")

    print(f"\n[done] best codec EER={best_codec*100:.2f}%")

if __name__ == "__main__":
    main()
