"""
VoxShield — train an alternative detector back-end (LCNN / Conformer / AASIST)
on the same corpus as `pipeline/train_corpus.py`, with optional ADVERSARIAL
training (FGSM / PGD). Produces `scores.csv` for `paper_report.py`.

Reuses `pipeline/train_corpus.load_corpus` (same splits/layout/metric as the XLS-R run),
so results are directly comparable to the main checkpoints.

Usage (DGX):
    python train_backend.py --arch aasist --data-root data/hindi --langs hindi \
        --holdout vits --epochs 3 --out checkpoints/aasist_hindi
    python train_backend.py --arch conformer --adv pgd --eps 0.005 ...
    python train_backend.py --selftest
"""
from __future__ import annotations
import argparse, csv, os, sys, time
import numpy as np, torch, torch.nn as nn
from torch.utils.data import DataLoader

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.join(_HERE, "pipeline"))
from backends import build, logmel                      # noqa
SR, CLIP_LEN = 16000, 16000 * 3


def pgd_attack(model, x, y, eps=0.005, alpha=0.001, steps=5, rand=True):
    """L-inf PGD (steps=1 & rand=False -> FGSM). x: waveform batch."""
    x_adv = x.detach() + (torch.empty_like(x).uniform_(-eps, eps) if rand else 0)
    for _ in range(max(1, steps)):
        x_adv.requires_grad_(True)
        loss = nn.functional.cross_entropy(model(x_adv), y)
        g = torch.autograd.grad(loss, x_adv)[0]
        x_adv = (x_adv + alpha * g.sign()).detach()
        x_adv = torch.clamp(x_adv, x - eps, x + eps).clamp(-1, 1)
    return x_adv.detach()


def _eer(y, s):
    from eval_gengap import eer
    return eer(list(y), list(s))


@torch.no_grad()
def _score(model, ds, device):
    model.eval(); ys, yt = [], []
    for x, y in DataLoader(ds, batch_size=16, shuffle=False, num_workers=4):
        p = torch.softmax(model(x.to(device)), -1)[:, 1].float().cpu().numpy()
        ys += p.tolist(); yt += y.numpy().tolist()
    return yt, ys


def train(arch, data_root, langs, holdout, epochs, out, adv="none", eps=0.005, alpha=0.001, steps=5,
          limit_per=None, lr=1e-3, bs=16):
    import train_corpus as TC
    os.makedirs(out, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rows, stores = TC.load_corpus(data_root, holdout, langs.split(","), limit_per)
    tr = [r for r in rows if r["split"] == "train"]
    va = [r for r in rows if r["split"] in ("val", "test")]
    if not tr:
        print("no training rows"); return
    ds_tr = TC.CorpusDS(tr, stores, augment=True)
    ds_va = TC.CorpusDS(va, stores, augment=False)
    model = build(arch).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    for ep in range(epochs):
        model.train(); t0 = time.time(); ls = []
        for i, (x, y) in enumerate(DataLoader(ds_tr, batch_size=bs, shuffle=True, num_workers=4)):
            x, y = x.to(device), y.to(device)
            opt.zero_grad(set_to_none=True)
            loss = nn.functional.cross_entropy(model(x), y)
            if adv in ("fgsm", "pgd") and (i % 2 == 0):
                xa = pgd_attack(model, x, y, eps, alpha, 1 if adv == "fgsm" else steps, rand=(adv == "pgd"))
                loss = loss + nn.functional.cross_entropy(model(xa), y)
            loss.backward(); opt.step(); ls.append(loss.item())
            if i % 50 == 0: print(f"[e{ep} {i}] loss={loss.item():.4f} t={time.time()-t0:.0f}s")
        print(f"[e{ep}] mean loss={np.mean(ls):.4f}")
        torch.save({"model": model.state_dict(), "arch": arch}, f"{out}/last.pt")

    yt, ys = _score(model, ds_va, device)
    if len(set(yt)) >= 2:
        print(f"[eval] EER={_eer(yt, ys)*100:.2f}%  n={len(yt)}")
    # scorecard for paper_report (clean + g711) over the whole set
    scored = _score_rows(model, rows, stores, device, False) + _score_rows(model, rows, stores, device, True)
    with open(f"{out}/scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "score", "generator", "language", "channel", "seen"])
        w.writeheader(); w.writerows(scored)
    print(f"[scores] {len(scored)} rows -> {out}/scores.csv")


@torch.no_grad()
def _score_rows(model, rows, stores, device, force_codec):
    import train_corpus as TC
    if not rows: return []
    ds = TC.CorpusDS(rows, stores, force_codec=force_codec)
    model.eval(); ys = []
    for x, _ in DataLoader(ds, batch_size=16, shuffle=False, num_workers=4):
        ys += torch.softmax(model(x.to(device)), -1)[:, 1].float().cpu().numpy().tolist()
    out = []
    for r, s in zip(rows, ys):
        out.append({"label": r["label"], "score": round(float(s), 6), "generator": r.get("generator", ""),
                    "language": r.get("lang", ""), "channel": "g711" if force_codec else "clean",
                    "seen": 0 if r["split"] in ("test_gen", "ood") else 1})
    return out


def _selftest():
    torch.manual_seed(0)
    model = build("aasist")
    x = (torch.rand(4, CLIP_LEN) - 0.5); y = torch.randint(0, 2, (4,))   # valid audio range
    xa = pgd_attack(model, x, y, steps=2)
    assert xa.shape == x.shape and (xa - x).abs().max() <= 0.005 + 1e-6
    loss = nn.functional.cross_entropy(model(xa), y); loss.backward()   # gradients flow
    print(f"  pgd ok: max|Δ|={ (xa-x).abs().max().item():.4f}  loss={loss.item():.3f}")
    print("\n[selftest] PASS — back-end + PGD/FGSM attack run end-to-end on random audio.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="aasist", choices=["lcnn", "conformer", "aasist"])
    ap.add_argument("--data-root"); ap.add_argument("--langs", default="hindi")
    ap.add_argument("--holdout", default="vits"); ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--out", default="checkpoints/backend"); ap.add_argument("--adv", default="none", choices=["none", "fgsm", "pgd"])
    ap.add_argument("--eps", type=float, default=0.005); ap.add_argument("--alpha", type=float, default=0.001)
    ap.add_argument("--steps", type=int, default=5); ap.add_argument("--limit-per", type=int, default=None)
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.data_root: ap.error("--data-root required")
    train(a.arch, a.data_root, a.langs, a.holdout, a.epochs, a.out, a.adv, a.eps, a.alpha, a.steps, a.limit_per)


if __name__ == "__main__":
    main()
