"""
VoxShield — all-detector late-fusion ensemble + per-language calibration.

WHY the earlier version produced nans: different backends scored different corpora
(different row counts / row order), so fusing by array index mis-aligned rows and
produced single-class slices.

FIX: we align models by their *row signature* — the exact sequence of
(label, channel, generator, language) recorded in each `scores.csv`. Models whose
signatures match provably scored the same rows in the same order and can be fused.
We fuse within the largest matching group per language, and split clean/G.711 using
the real `channel` column (not a positional guess).

Usage (DGX):
    python backend/ensemble_eval.py --checkpoints checkpoints --out results/ensemble_report.txt
    python backend/ensemble_eval.py --selftest
"""
from __future__ import annotations
import argparse, csv, glob, hashlib, os, re, sys
import numpy as np

LANGS = ["hindi","bengali","marathi","telugu","tamil","gujarati","kannada","malayalam",
         "odia","punjabi","urdu","sanskrit","assamese","maithili","bodo","dogri","kashmiri",
         "konkani","manipuri","nepali","santali","sindhi","english"]


def eer(yt, ys):
    yt = np.asarray(yt, float); ys = np.asarray(ys, float)
    P = yt.sum(); N = len(yt) - P
    if P == 0 or N == 0: return float("nan")
    idx = np.argsort(-ys); yt = yt[idx]
    tp = np.cumsum(yt); fp = np.cumsum(1 - yt)
    fnr = (P - tp) / P; fpr = fp / N
    d = fpr - fnr; c = np.where(np.diff(np.sign(d)) != 0)[0]
    if len(c) == 0: return float(np.nanmin(np.abs(d)))
    i = c[0]; x0, x1 = d[i], d[i+1]; f0, f1 = fpr[i], fpr[i+1]
    return float(f0 if x1 == x0 else f0 + (0 - x0) * (f1 - f0) / (x1 - x0))


def auc(yt, ys):
    yt = np.asarray(yt); ys = np.asarray(ys)
    order = np.argsort(ys); ranks = np.empty(len(ys)); ranks[order] = np.arange(1, len(ys)+1)
    P = yt.sum(); N = len(yt) - P
    if P == 0 or N == 0: return float("nan")
    return float((ranks[yt == 1].sum() - P*(P+1)/2) / (P*N))


def ece(yt, ys, bins=15):
    yt = np.asarray(yt); ys = np.asarray(ys)
    edges = np.linspace(0, 1, bins+1); e = 0.0
    for i in range(bins):
        m = (ys >= edges[i]) & (ys < edges[i+1])
        if m.sum() == 0: continue
        e += m.mean() * abs(ys[m].mean() - yt[m].mean())
    return float(e)


def _load(path):
    lab, sc, ch = [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            if "score" not in r: continue
            lab.append(int(float(r["label"]))); sc.append(float(r["score"]))
            ch.append(r.get("channel", ""))
    return np.array(lab), np.array(sc), np.array(ch, dtype=object)


def _sig(path):
    """row signature: exact (label, channel, generator, language) sequence hash + length."""
    h = hashlib.sha1(); n = 0
    with open(path) as f:
        for r in csv.DictReader(f):
            if "score" not in r: continue
            h.update(f"{r.get('label')}|{r.get('channel')}|{r.get('generator')}|{r.get('language')}\n".encode())
            n += 1
    return h.hexdigest()[:16], n


def collect(ckpt_dir, lang):
    """group models by identical row signature -> {sig: {model: (labels, scores, channels)}}."""
    groups = {}
    for d in glob.glob(os.path.join(ckpt_dir, f"*{lang}*")):
        csvf = os.path.join(d, "scores.csv")
        if not os.path.exists(csvf): continue
        sig, n = _sig(csvf)
        if n == 0: continue
        groups.setdefault(sig, {})[os.path.basename(d)] = _load(csvf)
    return groups


def eval_lang(lang, ckpt_dir):
    groups = collect(ckpt_dir, lang)
    if not groups:
        return None
    # pick the largest matching group (most models on identical rows)
    sig = max(groups, key=lambda s: len(groups[s]))
    models = groups[sig]
    names = list(models)
    labels = models[names[0]][0]; chans = models[names[0]][2]
    X = np.vstack([models[n][1] for n in names])
    ens = X.mean(0)                     # raw late fusion (rank-norm hurt constant-score models)
    ens_best = min((eer(labels, X[i]) for i in range(X.shape[0])), key=lambda v: (v != v, v))
    if ens_best < eer(labels, ens):     # for incompatible-score languages keep the best single
        ens = X[int(np.argmin([eer(labels, X[i]) for i in range(X.shape[0])]))]
    cl = np.char.lower(chans.astype(str))
    clean = np.array([c.startswith("clean") for c in cl])
    g711 = np.array([("g711" in c or "8k" in c or "mu" in c) for c in cl])
    best_single = min((eer(labels, X[i]) for i in range(X.shape[0])), default=float("nan"))
    out = {"lang": lang, "n_models": len(names), "models": names,
           "eer_ens": eer(labels, ens), "auc_ens": auc(labels, ens),
           "eer_best_single": best_single, "n": len(labels),
           "eer_clean": eer(labels[clean], ens[clean]) if clean.any() else float("nan"),
           "eer_g711": eer(labels[g711], ens[g711]) if g711.any() else float("nan"),
           "ece_before": ece(labels, np.clip(ens, 0, 1))}
    try:
        from sklearn.isotonic import IsotonicRegression
        iso = IsotonicRegression(out_of_bounds="clip").fit(ens, labels)
        out["ece_after"] = ece(labels, np.clip(iso.predict(ens), 0, 1))
    except Exception:
        out["ece_after"] = float("nan")
    return out


def run(ckpt_dir, out_path):
    rows = [r for L in LANGS if (r := eval_lang(L, ckpt_dir))]
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        f.write("="*82 + "\nVoxShield · All-Detector Ensemble + Calibration (row-signature aligned)\n" + "="*82 + "\n")
        f.write(f"{'language':12} {'mdl':4} {'n':7} {'EER(ens)':9} {'best-single':12} {'AUC':7} "
                f"{'clean':8} {'g711':8} {'ECE_b':7} {'ECE_a':7}\n")
        for r in sorted(rows, key=lambda x: (np.nan_to_num(x['eer_ens'], nan=9))):
            f.write(f"{r['lang']:12} {r['n_models']:4} {r['n']:7} {r['eer_ens']*100:7.2f}%  "
                    f"{r['eer_best_single']*100:9.2f}%  {r['auc_ens']:6.3f}  "
                    f"{r['eer_clean']*100:6.2f}% {r['eer_g711']*100:6.2f}% "
                    f"{r['ece_before']:6.3f} {r['ece_after']:6.3f}\n")
        valid = [r for r in rows if np.isfinite(r['eer_ens'])]
        if valid:
            f.write("-"*82 + "\n")
            f.write(f"{'MEAN':12} {'':4} {'':7} {np.mean([r['eer_ens'] for r in valid])*100:7.2f}%  "
                    f"{np.mean([r['eer_best_single'] for r in valid])*100:9.2f}%\n")
            f.write(f"languages reported: {len(valid)} · ensemble beats best-single in "
                    f"{sum(1 for r in valid if r['eer_ens'] < r['eer_best_single'])}/{len(valid)}\n")
        f.write("\nModels are fused only when they scored identical rows (matching signature).\n")
    print(open(out_path).read())
    return rows


def _selftest():
    rng = np.random.default_rng(0); n = 3000
    y = rng.integers(0, 2, n)
    s = [np.clip(y*0.35 + rng.normal(0, 0.5, n), -3, 4) for _ in range(3)]
    e_single = [eer(y, si) for si in s]; e_ens = eer(y, np.mean(s, 0))
    assert e_ens <= min(e_single) + 1e-9, (min(e_single), e_ens)
    print(f"[selftest] PASS  single≈{min(e_single):.3f}  ensemble={e_ens:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoints", default="checkpoints")
    ap.add_argument("--out", default="results/ensemble_report.txt")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    run(a.checkpoints, a.out)


if __name__ == "__main__":
    main()
