"""
VoxShield multi-cloner corpus trainer (parquet-native).

Loads IndicSynth (fakes) + IndicVoices (real) + DFADD (English fakes) via HuggingFace
`datasets` (memory-mapped, auto audio decode), assigns speaker-disjoint + generator-holdout
splits, applies on-the-fly telephony augmentation, fine-tunes wav2vec2-XLSR, and reports
cross-generator + per-language EER — the honest numbers the dossier called for.

Run on the DGX:
  python train_corpus.py --data-root ~/data/voxdata/raw --epochs 3 --bs 16 \
      --holdout-generator xtts --gpu 0

Deps: datasets, soundfile, scikit-learn (pip via `python -m pip install datasets`)
"""
import os, sys, time, argparse, random, hashlib
import numpy as np, torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from transformers import Wav2Vec2ForSequenceClassification
from sklearn.metrics import roc_auc_score, roc_curve

sys.path.insert(0, os.path.dirname(__file__))
from telephony_aug import telephony_augment  # noqa

SR, CLIP_LEN = 16000, 16000 * 3

# ---------------- corpus loading ----------------
def _split_of(speaker, holdout_gen, generator, dataset, seed="vox42"):
    if dataset == "mlaad":
        return "ood"
    if holdout_gen and holdout_gen in str(generator).lower():
        return "test_gen"
    h = int(hashlib.md5(f"{seed}:{speaker}".encode()).hexdigest(), 16) % 100
    return "train" if h < 70 else ("val" if h < 85 else "test")

def load_corpus(root, holdout_gen, langs, limit_per=None):
    """Return list of dict rows: {hf_ds, idx, label, speaker, lang, generator, split}."""
    from datasets import load_dataset, Audio
    import glob
    rows, stores = [], {}

    # IndicSynth (fake), per-language dirs
    isbase = os.path.join(root, "indicsynth")
    for lang in langs:
        cap = lang.capitalize()
        files = sorted(glob.glob(os.path.join(isbase, cap, "*.parquet")))
        if not files: continue
        ds = load_dataset("parquet", data_files=files, split="train")
        ds = ds.cast_column("audio", Audio(sampling_rate=SR, decode=True))
        key = f"indicsynth:{lang}"; stores[key] = ds
        gens = ds["Generative Model"]; spk = ds["Target Speaker ID"]
        n = len(ds) if not limit_per else min(limit_per, len(ds))
        for i in range(n):
            g = str(gens[i]).lower()
            sp = f"is_{lang}_{spk[i]}"
            rows.append(dict(store=key, idx=i, audiocol="audio", label=1, speaker=sp,
                             lang=lang, generator=g, dataset="indicsynth",
                             split=_split_of(sp, holdout_gen, g, "indicsynth")))
        print(f"  indicsynth/{lang}: {n} fakes")

    # IndicVoices (real)
    ivbase = os.path.join(root, "indicvoices_real")
    ivfiles = sorted(glob.glob(os.path.join(ivbase, "**", "*.parquet"), recursive=True))
    if ivfiles:
        ds = load_dataset("parquet", data_files=ivfiles, split="train")
        ds = ds.cast_column("audio_filepath", Audio(sampling_rate=SR, decode=True))
        stores["indicvoices"] = ds
        lg = ds["lang"]; spk = ds["speaker_id"]
        n = len(ds) if not limit_per else min(limit_per*5, len(ds))
        for i in range(n):
            l = str(lg[i]).lower()[:2]
            sp = f"iv_{spk[i]}"
            rows.append(dict(store="indicvoices", idx=i, audiocol="audio_filepath", label=0,
                             speaker=sp, lang=l, generator="real", dataset="indicvoices",
                             split=_split_of(sp, holdout_gen, "real", "indicvoices")))
        print(f"  indicvoices: {n} real")

    # DFADD (English fakes + some real)
    dfbase = os.path.join(root, "dfadd")
    dffiles = sorted(glob.glob(os.path.join(dfbase, "**", "*.parquet"), recursive=True))
    if dffiles:
        ds = load_dataset("parquet", data_files=dffiles, split="train")
        ds = ds.cast_column("audio", Audio(sampling_rate=SR, decode=True))
        stores["dfadd"] = ds
        names = ds["audio_name"]; labs = ds["label"]
        n = len(ds) if not limit_per else min(limit_per, len(ds))
        for i in range(n):
            nm = names[i] or ""
            sp = f"dfadd_{nm.split('_')[0]}"
            g = nm.rsplit('_',1)[-1].split('.')[0].lower() if '_' in nm else "dfadd"
            lab = 0 if str(labs[i]).lower().startswith("bona") else 1
            rows.append(dict(store="dfadd", idx=i, audiocol="audio", label=lab, speaker=sp,
                             lang="en", generator=g, dataset="dfadd",
                             split=_split_of(sp, holdout_gen, g, "dfadd")))
        print(f"  dfadd: {n}")
    return rows, stores

# ---------------- torch dataset ----------------
class CorpusDS(Dataset):
    def __init__(self, rows, stores, augment=False, force_codec=False):
        self.rows, self.stores = rows, stores
        self.augment, self.force_codec = augment, force_codec
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        r = self.rows[i]
        try:
            a = self.stores[r["store"]][r["idx"]][r["audiocol"]]
            y = np.asarray(a["array"], dtype=np.float32)
            sr = a["sampling_rate"]
            if sr != SR:
                import torchaudio.functional as F
                y = F.resample(torch.from_numpy(y), sr, SR).numpy()
        except Exception:
            y = np.zeros(CLIP_LEN, np.float32)
        if self.augment:
            y = telephony_augment(y, p=0.5, seed=i)
        elif self.force_codec:
            y = telephony_augment(y, p=1.0, seed=i, )
        if len(y) < CLIP_LEN: y = np.pad(y, (0, CLIP_LEN-len(y)))
        elif len(y) > CLIP_LEN:
            s = random.randint(0, len(y)-CLIP_LEN); y = y[s:s+CLIP_LEN]
        return torch.from_numpy(y.astype(np.float32)), int(r["label"])

def eer(yt, ys):
    fpr, tpr, _ = roc_curve(yt, ys); fnr = 1-tpr
    k = np.nanargmin(np.abs(fpr-fnr)); return float((fpr[k]+fnr[k])/2)

def evaluate(model, rows, stores, device, tag, force_codec=False, bs=16):
    if not rows: return
    dl = DataLoader(CorpusDS(rows, stores, force_codec=force_codec), batch_size=bs,
                    shuffle=False, num_workers=6, pin_memory=True)
    model.eval(); ys, yt = [], []
    with torch.no_grad():
        for x, y in dl:
            x = x.to(device, non_blocking=True)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                p = torch.softmax(model(input_values=x).logits, -1)[:,1].float().cpu().numpy()
            ys += p.tolist(); yt += y.numpy().tolist()
    if len(set(yt)) < 2:
        print(f"    [{tag}] only one class, skip"); return
    print(f"    [{tag:16s}] EER={eer(np.array(yt),np.array(ys))*100:.2f}%  "
          f"AUC={roc_auc_score(yt,ys)*100:.2f}%  n={len(yt)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=os.path.expanduser("~/data/voxdata/raw"))
    ap.add_argument("--langs", default="hindi,bengali,marathi,telugu,malayalam")
    ap.add_argument("--holdout-generator", default="xtts")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--limit-per", type=int, default=None, help="cap rows per source (smoke test)")
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--out", default=os.path.expanduser("~/checkpoints/voxshield/xlsr_corpus"))
    a = ap.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = a.gpu
    device = torch.device("cuda")
    os.makedirs(a.out, exist_ok=True)

    print("[load] building corpus index ...")
    rows, stores = load_corpus(a.data_root, a.holdout_generator, a.langs.split(","), a.limit_per)
    from collections import Counter
    print("  splits:", dict(Counter(r["split"] for r in rows)))
    print("  labels:", dict(Counter(r["label"] for r in rows)))

    train = [r for r in rows if r["split"]=="train"]
    val   = [r for r in rows if r["split"]=="val"]
    test  = [r for r in rows if r["split"]=="test"]
    testg = [r for r in rows if r["split"]=="test_gen"]
    if not train:
        print("no training rows — check data-root"); return

    labels = np.array([r["label"] for r in train])
    w = 1.0/np.bincount(labels)[labels]
    sampler = WeightedRandomSampler(w, num_samples=len(train), replacement=True)
    tl = DataLoader(CorpusDS(train, stores, augment=True), batch_size=a.bs, sampler=sampler,
                    num_workers=8, pin_memory=True)

    print(f"[model] loading XLSR-53  (train={len(train)} val={len(val)} test={len(test)} test_gen={len(testg)})")
    model = Wav2Vec2ForSequenceClassification.from_pretrained(
        "facebook/wav2vec2-large-xlsr-53", num_labels=2, ignore_mismatched_sizes=True)
    # torch>=2.6 fix: default (reentrant) gradient checkpointing silently drops grads
    # when the checkpointed segment's input doesn't require grad -> loss stays at 0.69,
    # model never learns. use_reentrant=False is the modern mode that handles this
    # correctly, so we can keep freezing the feature encoder (the proven recipe).
    model.freeze_feature_encoder()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs*max(1,len(tl)))

    best = 1.0
    for ep in range(a.epochs):
        model.train(); t0=time.time(); losses=[]
        for i,(x,y) in enumerate(tl):
            x=x.to(device,non_blocking=True); y=y.to(device,non_blocking=True)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = model(input_values=x, labels=y).loss
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); sch.step()
            losses.append(loss.item())
            if i%50==0: print(f"[e{ep} {i}/{len(tl)}] loss={loss.item():.4f} t={time.time()-t0:.0f}s")
        print(f"[e{ep}] eval (loss={np.mean(losses):.4f}):")
        evaluate(model, val,  stores, device, "val-clean", bs=a.bs)
        evaluate(model, test, stores, device, "test-clean", bs=a.bs)
        evaluate(model, test, stores, device, "test-G711", force_codec=True, bs=a.bs)
        evaluate(model, testg, stores, device, f"XGEN({a.holdout_generator})", bs=a.bs)
        # per-language on test
        for lang in a.langs.split(","):
            evaluate(model, [r for r in test if r["lang"]==lang[:2] or r["lang"]==lang],
                     stores, device, f"lang:{lang[:2]}", bs=a.bs)
        torch.save({"model":model.state_dict(),"epoch":ep}, f"{a.out}/last.pt")
    print(f"\n[done] checkpoint -> {a.out}/last.pt")

if __name__ == "__main__":
    main()
