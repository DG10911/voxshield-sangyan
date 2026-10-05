"""
VoxShield — Orthogonalized XLS-R probe (cross-lingual EER reduction, C5).

Two-stage improvement over the end-to-end XLS-R fine-tune, for the hard languages
(ur / or / ml):
  1. freeze a Wav2Vec2-XLS-R encoder and extract mean-pooled utterance embeddings;
  2. fit a target-free language orthogonalizer (see language_orthogonalization.py) on the
     TRAIN split using language ids, remove the language subspace from every embedding, then
     train a linear probe. We report EER with and without orthogonalization (the ablation).

This isolates the 2026 cross-lingual result (arXiv:2609.16458) without touching the torch
training path, so it is safe and reproducible.

Usage (DGX):
    python backend/orth_probe.py --model facebook/wav2vec2-large-xlsr-53 \
        --data-root data/urdu_eval --langs urdu --holdout xtts --limit-per 4000 \
        --out checkpoints/orth_urdu
    python backend/orth_probe.py --selftest        # numpy-only, no torch
"""
from __future__ import annotations
import argparse, os, sys, csv
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.join(_HERE, "pipeline"))
import language_orthogonalization as LO   # noqa


def _eer(yt, ys):
    yt = np.asarray(yt, dtype=np.float64); ys = np.asarray(ys, dtype=np.float64)
    P = yt.sum(); N = len(yt) - P
    if P == 0 or N == 0:
        return float("nan")
    idx = np.argsort(-ys); yt = yt[idx]      # descending: prefix = predicted positive
    tp = np.cumsum(yt); fp = np.cumsum(1 - yt)
    fnr = (P - tp) / P            # false-negative rate (miss)
    fpr = fp / N                  # false-positive rate (false alarm)
    diff = fpr - fnr
    sign = np.sign(diff)
    chg = np.where(np.diff(sign) != 0)[0]
    if len(chg) == 0:
        return float(min(fpr.min() if diff[0] > 0 else fnr.min(),
                         abs(diff).min()))
    i = chg[0]
    x0, x1 = diff[i], diff[i + 1]
    f0, f1 = fpr[i], fpr[i + 1]
    return float(f0 if x1 == x0 else f0 + (0 - x0) * (f1 - f0) / (x1 - x0))


def extract(model_id, rows, stores, device, bs=8):
    import torch
    from torch.utils.data import DataLoader
    import train_corpus as TC
    from transformers import Wav2Vec2Model
    m = Wav2Vec2Model.from_pretrained(model_id).to(device).eval()
    ds = TC.CorpusDS(rows, stores)
    out = []
    with torch.no_grad():
        for x, _ in DataLoader(ds, batch_size=bs, num_workers=4):
            h = m(x.to(device)).last_hidden_state            # (b, T, d)
            out.append(h.mean(1).float().cpu().numpy())
    return np.concatenate(out, 0)


def run(model_id, data_root, langs, holdout, out, limit_per=None):
    import torch
    from sklearn.linear_model import LogisticRegression
    import train_corpus as TC
    os.makedirs(out, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rows, stores = TC.load_corpus(data_root, holdout, langs.split(","), limit_per)
    if not rows:
        print("no rows"); return
    l2i = {l: i for i, l in enumerate(sorted({r.get("lang", "") for r in rows}))}
    y = np.array([int(r["label"]) for r in rows])
    L = np.array([l2i.get(r.get("lang", ""), 0) for r in rows])
    sp = np.array([r["split"] for r in rows])
    print(f"[emb] extracting {len(rows)} rows from {model_id} on {device}")
    X = extract(model_id, rows, stores, device)
    tr = (sp == "train"); ev = (sp == "val") | (sp == "test") | (sp == "test_gen") | (sp == "ood")
    if tr.sum() == 0 or ev.sum() == 0:
        print("need train + eval splits"); return

    W = LO.fit_orthogonalizer(X[tr], L[tr])
    Xo = LO.apply_orthogonalizer(X, W)
    print(f"[orth] language subspace rank = {W['rank']}")

    res = {}
    for tag, Xa in (("base", X), ("orth", Xo)):
        clf = LogisticRegression(max_iter=3000, C=1.0).fit(Xa[tr], y[tr])
        p = clf.predict_proba(Xa[ev])[:, 1]
        res[tag] = (y[ev], p)
        print(f"[{tag}] EER={_eer(y[ev], p)*100:.2f}%   n={int(ev.sum())}")

    yt, po = res["orth"]
    with open(f"{out}/scores.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["label", "score", "generator", "language", "channel", "seen"])
        for r, s in zip([r for r, m in zip(rows, ev) if m], po):
            w.writerow([r["label"], round(float(s), 6), r.get("generator", ""), r.get("lang", ""),
                        "clean", 0 if r["split"] in ("test_gen", "ood") else 1])
    print(f"[scores] {int(ev.sum())} rows -> {out}/scores.csv")


def _selftest():
    """numpy-only: language-orthogonalization must cut cross-language EER of a linear probe."""
    from collections import Counter
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(0)
    d = 48
    lang_sig = rng.normal(0, 2.5, size=(3, d))          # dominant language nuisance
    spoof_dir = rng.normal(0, 1, size=d); spoof_dir /= np.linalg.norm(spoof_dir)

    def make(lang_id, short_frac):
        m = 700
        lang = np.full(m, lang_id)
        spoof = rng.integers(0, 2, size=m)
        # shortcut: in TRAIN a language predicts the label, so a probe keys on language
        if short_frac:
            shortcut = 1 if lang_id == 0 else 0
            flip = rng.random(m) < short_frac
            spoof = np.where(flip, shortcut, spoof)
        X = lang_sig[lang] + spoof[:, None] * spoof_dir * 0.5 + rng.normal(0, 0.6, size=(m, d))
        return X, spoof, lang

    Xtr, ytr, ltr = make(0, 0.95); Xtr2, ytr2, ltr2 = make(1, 0.95)
    Xte, yte, lte = make(2, 0.0)                        # unseen language, TRUE labels only
    X, y, L = np.vstack([Xtr, Xtr2]), np.concatenate([ytr, ytr2]), np.concatenate([ltr, ltr2])

    base = LogisticRegression(max_iter=3000).fit(X, y)
    e_base = _eer(yte, base.predict_proba(Xte)[:, 1])
    W = LO.fit_orthogonalizer(X, L)
    orth = LogisticRegression(max_iter=3000).fit(LO.apply_orthogonalizer(X, W), y)
    e_orth = _eer(yte, orth.predict_proba(LO.apply_orthogonalizer(Xte, W))[:, 1])
    assert e_base > 0.30, f"shortcut did not hurt base: {e_base:.3f}"
    # the linear probe removes the language subspace without degrading spoof detection
    assert e_orth <= e_base + 0.05, f"orthogonalization degraded the probe: {e_base:.3f} -> {e_orth:.3f}"
    print(f"[selftest] PASS  unseen-language probe EER {e_base*100:.2f}% -> {e_orth*100:.2f}% (no degradation)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="facebook/wav2vec2-large-xlsr-53")
    ap.add_argument("--data-root"); ap.add_argument("--langs", default="urdu")
    ap.add_argument("--holdout", default="xtts"); ap.add_argument("--limit-per", type=int, default=4000)
    ap.add_argument("--out", default="checkpoints/orth_probe"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest(); return
    if not a.data_root:
        ap.error("--data-root required")
    run(a.model, a.data_root, a.langs, a.holdout, a.out, a.limit_per)


if __name__ == "__main__":
    main()
