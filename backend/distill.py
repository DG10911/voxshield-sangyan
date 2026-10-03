"""
VoxShield — distillation: XLS-R teacher -> compact student (LCNN/Conformer/AASIST).

Teacher = a trained `Wav2Vec2ForSequenceClassification` checkpoint (from the sweeps).
Student = a small back-end from `backends.py` (edge-friendly). Trains on the same
corpus, distilling teacher logits (KD) + hard labels. Produces `scores.csv`.

Usage (DGX):
    python distill.py --teacher checkpoints/round_*_hindi/last.pt --arch lcnn \
        --data-root data/hindi --langs hindi --holdout vits --out checkpoints/student_hindi
    python distill.py --selftest
"""
from __future__ import annotations
import argparse, csv, os, sys, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import DataLoader

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.join(_HERE, "pipeline"))
from backends import build                                  # noqa
MODEL_ID = "facebook/wav2vec2-large-xlsr-53"


def load_teacher(ckpt, device, model_id=MODEL_ID):
    from transformers import Wav2Vec2ForSequenceClassification
    t = Wav2Vec2ForSequenceClassification.from_pretrained(model_id, num_labels=2, ignore_mismatched_sizes=True)
    ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    t.load_state_dict(ck.get("model", ck) if isinstance(ck, dict) else ck)
    t.to(device).eval()
    for p in t.parameters(): p.requires_grad_(False)
    return t


def kd_loss(s_logits, t_logits, y, T=3.0, alpha=0.7):
    kl = F.kl_div(F.log_softmax(s_logits / T, -1), F.softmax(t_logits / T, -1),
                  reduction="batchmean") * (T * T)
    ce = F.cross_entropy(s_logits, y)
    return alpha * kl + (1 - alpha) * ce


def train(teacher_ckpt, arch, data_root, langs, holdout, epochs, out, T=3.0, alpha=0.7, limit_per=None, bs=16, lr=1e-3):
    import train_corpus as TC
    os.makedirs(out, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    teacher = load_teacher(teacher_ckpt, device)
    rows, stores = TC.load_corpus(data_root, holdout, langs.split(","), limit_per)
    tr = [r for r in rows if r["split"] == "train"]
    if not tr: print("no training rows"); return
    ds = TC.CorpusDS(tr, stores, augment=True)
    student = build(arch).to(device)
    opt = torch.optim.AdamW(student.parameters(), lr=lr, weight_decay=0.01)
    for ep in range(epochs):
        student.train(); t0 = time.time(); ls = []
        for i, (x, y) in enumerate(DataLoader(ds, batch_size=bs, shuffle=True, num_workers=4)):
            x, y = x.to(device), y.to(device)
            with torch.no_grad():
                tl = teacher(input_values=x).logits
            sl = student(x)
            loss = kd_loss(sl, tl, y, T, alpha)
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); ls.append(loss.item())
            if i % 50 == 0: print(f"[e{ep} {i}] loss={loss.item():.4f} t={time.time()-t0:.0f}s")
        print(f"[e{ep}] mean={np.mean(ls):.4f}")
        torch.save({"model": student.state_dict(), "arch": arch, "distilled_from": teacher_ckpt}, f"{out}/last.pt")

    scored = _score_rows(student, rows, stores, device, False) + _score_rows(student, rows, stores, device, True)
    with open(f"{out}/scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "score", "generator", "language", "channel", "seen"])
        w.writeheader(); w.writerows(scored)
    from eval_gengap import report
    print(f"[scores] {len(scored)} rows -> {out}/scores.csv"); report(scored)


@torch.no_grad()
def _score_rows(model, rows, stores, device, force_codec):
    import train_corpus as TC
    if not rows: return []
    ds = TC.CorpusDS(rows, stores, force_codec=force_codec)
    model.eval(); ys = []
    for x, _ in DataLoader(ds, batch_size=16, shuffle=False, num_workers=4):
        ys += torch.softmax(model(x.to(device)), -1)[:, 1].float().cpu().numpy().tolist()
    return [{"label": r["label"], "score": round(float(s), 6), "generator": r.get("generator", ""),
             "language": r.get("lang", ""), "channel": "g711" if force_codec else "clean",
             "seen": 0 if r["split"] in ("test_gen", "ood") else 1} for r, s in zip(rows, ys)]


def _selftest():
    torch.manual_seed(0)
    t_logits = torch.randn(4, 2); y = torch.randint(0, 2, (4,))
    s2 = torch.randn(4, 2, requires_grad=True)
    loss = kd_loss(s2, t_logits, y)
    assert torch.isfinite(loss)
    loss.backward()                          # gradient must flow to the student logits
    assert s2.grad is not None and s2.grad.abs().sum() > 0
    print(f"  kd loss ok: {loss.item():.3f}; student grad norm={s2.grad.abs().sum().item():.3f}")
    print("\n[selftest] PASS — KD loss (logit + hard) differentiable to the student.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher"); ap.add_argument("--arch", default="lcnn", choices=["lcnn", "conformer", "aasist"])
    ap.add_argument("--data-root"); ap.add_argument("--langs", default="hindi"); ap.add_argument("--holdout", default="vits")
    ap.add_argument("--epochs", type=int, default=3); ap.add_argument("--out", default="checkpoints/student")
    ap.add_argument("--temp", type=float, default=3.0); ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--limit-per", type=int, default=None); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not (a.teacher and a.data_root): ap.error("--teacher and --data-root required")
    train(a.teacher, a.arch, a.data_root, a.langs, a.holdout, a.epochs, a.out, a.temp, a.alpha, a.limit_per)


if __name__ == "__main__":
    main()
