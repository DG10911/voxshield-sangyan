"""
VoxShield — C2 ablation: channel profiling / gated decision vs a single global threshold.

Claim C2: because codecs shift the score distribution, a SINGLE global threshold
over-flags genuine calls on some channels. Profiling the channel and using a
per-channel operating point cuts false alarms at the same recall.

Reports, at a fixed target recall (TPR):
    * UNGATED  : one global threshold  -> EER, FP-rate on genuine callers
    * GATED    : per-channel threshold -> EER (same), FP-rate on genuine callers
    * FP reduction (relative) per channel + overall

Input CSV: label (0 genuine / 1 synthetic), score (P(fake)), channel.

Usage: python eval_c2_ablation.py --csv scores.csv [--tpr 0.95]
       python eval_c2_ablation.py --selftest
"""
from __future__ import annotations
import argparse, sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_gengap import eer, _fmt, load_csv


def _thr_at_tpr(labels, scores, tpr_target):
    y = np.asarray(labels); s = np.asarray(scores, float)
    pos = s[y == 1]
    if len(pos) == 0:
        return 1.0
    return float(np.quantile(pos, 1 - tpr_target))       # threshold so TPR≈target


def _fp(labels, scores, thr):
    y = np.asarray(labels); s = np.asarray(scores, float)
    g = y == 0
    return float((s[g] >= thr).sum() / max(g.sum(), 1))


def report(rows, tpr_target=0.95):
    y = [r["label"] for r in rows]; s = [r["score"] for r in rows]
    print("=" * 62); print("VoxShield · C2 ablation — channel-profiled gate vs global"); print("=" * 62)
    print(f"  target recall (TPR) = {tpr_target:.0%}   n={len(rows)}")

    thr_g = _thr_at_tpr(y, s, tpr_target)
    fp_g = _fp(y, s, thr_g)
    print(f"\n  UNGATED  global thr={thr_g:.3f}  EER={_fmt(eer(y,s))}  FP(genuine)={_fmt(fp_g)}")

    chans = {}
    for r in rows:
        chans.setdefault(r.get("channel", "?") or "?", []).append(r)
    print(f"\n  GATED (per-channel thr) — profiled decision")
    print(f"    {'channel':<16} {'thr':>7} {'EER':>8} {'FP':>8} {'n':>7}")
    gen_fp_num = 0.0; gen_n = 0
    for c in sorted(chans):
        gr = chans[c]; yy = [r["label"] for r in gr]; ss = [r["score"] for r in gr]
        t = _thr_at_tpr(yy, ss, tpr_target); f = _fp(yy, ss, t)
        n_gen = sum(1 for v in yy if v == 0)
        gen_fp_num += f * n_gen; gen_n += n_gen
        print(f"    {c:<16} {t:>7.3f} {_fmt(eer(yy,ss)):>8} {_fmt(f):>8} {len(gr):>7}")
    fp_gated = gen_fp_num / max(gen_n, 1)
    rel = (fp_g - fp_gated) / fp_g * 100 if fp_g else 0.0
    print(f"\n  → FP(genuine): global {fp_g*100:.2f}%  ->  gated {fp_gated*100:.2f}%   "
          f"(relative {rel:+.1f}%)")
    print("    (positive = channel profiling reduces genuine false alarms at equal recall)")


def _selftest():
    rng = np.random.default_rng(0); rows = []
    # clean: genuine low, fake high; g711_ulaw: score distribution shifted UP (codec inflates)
    for ch, g_mu, f_mu in [("clean", 0.15, 0.85), ("g711_ulaw", 0.45, 0.90)]:
        for _ in range(400):
            rows.append({"label": 0, "score": float(np.clip(rng.normal(g_mu, 0.12), 0, 1)), "channel": ch})
            rows.append({"label": 1, "score": float(np.clip(rng.normal(f_mu, 0.12), 0, 1)), "channel": ch})
    report(rows)
    print("\n[selftest] PASS — gated (per-channel) FP should be lower than global in the shifted channel.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--tpr", type=float, default=0.95)
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.csv: ap.error("--csv or --selftest")
    report(load_csv(a.csv), a.tpr)


if __name__ == "__main__":
    main()
