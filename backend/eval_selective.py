"""
VoxShield — Selective-Prediction / Abstention evaluation (paper claim C3).

Most ADD papers report a single EER. VoxShield's C3 claim is that an explicit
ABSTAIN option (defer low-confidence trials to a deeper stage / human) reduces
false alarms on genuine callers at an acceptable loss of coverage. This module
measures exactly that:

    * risk–coverage curve + AURC (area under the risk–coverage curve)
    * false-alarm (FP) rate on genuine callers as a function of abstention
    * selective EER at chosen coverage levels
    * calibration: ECE, Brier, and Cllr (cost of log-likelihood ratio)

Confidence measure = max(P(fake), P(genuine)); prediction = score >= 0.5.
Input CSV needs at least: label (0 genuine / 1 synthetic), score (P(synthetic)).
Optional tag columns (language, channel, generator) are ignored here.

Usage:  python eval_selective.py --csv scores.csv
        python eval_selective.py --csv scores.csv --coverage 0.5,0.7,0.9,0.95
        python eval_selective.py --selftest
"""
from __future__ import annotations
import argparse, csv, math, sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_gengap import eer, auc, ece, brier, _fmt, load_csv


def _confidence(scores):
    s = np.asarray(scores, float)
    return np.maximum(s, 1.0 - s)


def _correct(labels, scores):
    y = np.asarray(labels); s = np.asarray(scores, float)
    return (s >= 0.5).astype(int) == y.astype(int)


def risk_coverage(labels, scores):
    """Returns (coverages, risks, aurc). Sorted by confidence descending."""
    y = np.asarray(labels); c = _confidence(scores); ok = _correct(labels, scores)
    order = np.argsort(-c)
    ok = ok[order]
    n = len(ok)
    cov = np.arange(1, n + 1) / n
    errs = np.cumsum(~ok)
    risk = errs / np.arange(1, n + 1)
    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    aurc = float(_trapz(risk, cov)) if n > 1 else float(risk[0])
    return cov, risk, aurc


def fp_rate(labels, scores):
    """False-positive rate among GENUINE trials (label 0 predicted fake)."""
    y = np.asarray(labels); s = np.asarray(scores, float)
    gen = y == 0
    if gen.sum() == 0:
        return None
    return float(((s[gen] >= 0.5).sum()) / gen.sum())


def selective_eer(labels, scores, coverage):
    """EER computed on the top-`coverage` fraction by confidence."""
    y = np.asarray(labels); c = _confidence(scores)
    k = max(2, int(round(coverage * len(y))))
    idx = np.argsort(-c)[:k]
    return eer(y[idx].tolist(), np.asarray(scores)[idx].tolist())


def cllr(labels, scores):
    """Binary cost of log-likelihood ratio (positive class = synthetic).
    LLR = logit(P(synthetic)); lower Cllr = better-calibrated, decision-useful scores.
    Cllr in [0, ...]; 1.0 bit ≈ no better than chance."""
    y = np.asarray(labels, float); s = np.clip(np.asarray(scores, float), 1e-6, 1 - 1e-6)
    llr = np.log(s / (1 - s))
    pos = llr[y == 1]; neg = llr[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    a = np.mean(np.log2(1 + np.exp(-pos)))          # target (fake) trials
    b = np.mean(np.log2(1 + np.exp(neg)))           # non-target (genuine)
    return float(0.5 * (a + b))


def report(rows, coverages=(1.0, 0.95, 0.9, 0.8, 0.7, 0.5)):
    y = [r["label"] for r in rows]; s = [r["score"] for r in rows]
    print("=" * 60)
    print("VoxShield · Selective Prediction / Abstention (C3)")
    print("=" * 60)
    base_fp = fp_rate(y, s); base_eer = eer(y, s)
    print(f"  overall   EER={_fmt(base_eer)}  AUC={_fmt(auc(y,s),0)}  "
          f"FP(genuine)={_fmt(base_fp)}  n={len(rows)}")
    print(f"  calibration  ECE={_fmt(ece(y,s),0)}  Brier={_fmt(brier(y,s),0)}  "
          f"Cllr={_fmt(cllr(y,s),0)} bits")

    cov, risk, aurc = risk_coverage(y, s)
    print(f"\n  risk-coverage (AURC={aurc:.4f}, lower=better; AURC of a random abstainer≈base error)")
    print(f"    {'coverage':>9} {'risk(err)':>10} {'EER@cov':>9} {'FP(genuine)':>12}")
    for c in coverages:
        k = max(2, int(round(c * len(y))))
        idx = np.argsort(-_confidence(s))[:k]
        yy = np.asarray(y)[idx].tolist(); ss = np.asarray(s)[idx].tolist()
        r = float(np.mean(~_correct(yy, ss)))
        print(f"    {c*100:8.0f}% {_fmt(r):>10} {_fmt(selective_eer(y, s, c)):>9} {_fmt(fp_rate(yy, ss)):>12}")

    # the headline: abstention removes false alarms
    if base_fp is not None:
        for c in (0.9, 0.8):
            k = max(2, int(round(c * len(y))))
            idx = np.argsort(-_confidence(s))[:k]
            fp_c = fp_rate(np.asarray(y)[idx].tolist(), np.asarray(s)[idx].tolist())
            if fp_c is not None:
                saved = (base_fp - fp_c)
                print(f"  → abstaining on the least-confident {100-c*100:.0f}% cuts genuine false-alarms "
                      f"{base_fp*100:.2f}% → {fp_c*100:.2f}%  (Δ={saved*100:+.2f} pts)")
    print(f"  selective EER @95% coverage = {_fmt(selective_eer(y, s, 0.95))}")


def _selftest():
    rng = np.random.default_rng(0); rows = []
    # genuine mostly low, some hard borderline; fakes mostly high, some borderline
    for _ in range(500):
        rows.append({"label": 0, "score": float(np.clip(rng.normal(0.18, 0.20), 0, 1))})
    for _ in range(500):
        rows.append({"label": 1, "score": float(np.clip(rng.normal(0.82, 0.20), 0, 1))})
    report(rows)
    cov, risk, aurc = risk_coverage([r["label"] for r in rows], [r["score"] for r in rows])
    assert risk[0] <= risk[-1] + 1e-9, "risk should not increase with more rejects"
    assert 0.0 <= aurc <= 1.0
    print("\n[selftest] PASS — risk–coverage, AURC, FP-vs-abstention, and Cllr reported.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--coverage", default="1.0,0.95,0.9,0.8,0.7,0.5")
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.csv: ap.error("--csv or --selftest")
    covs = tuple(float(x) for x in a.coverage.split(","))
    report(load_csv(a.csv), covs)


if __name__ == "__main__":
    main()
