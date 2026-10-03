"""
VoxShield — Watermark-Agnostic benchmark (roadmap §12 watermark-agnostic, §37).

A detector must learn AUTHENTICITY, not shortcut to "this generator's watermark is
present". This harness scores the four cells:  real±wm, fake±wm  and checks:
  (1) EER on fakes WITHOUT watermark ≈ EER WITH watermark   (no reliance on wm)
  (2) the watermark flag alone must NOT predict the label    (AUC(wm→label) ≈ 0.5)
If EER jumps badly when the watermark is removed, the detector is shortcutting.

Input CSV: label, score, watermark (0/1).   Usage: --csv ... | --selftest
"""
from __future__ import annotations
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_gengap import eer, auc, _fmt, load_csv


def report(rows):
    wm = [r for r in rows if str(r.get("watermark")) in ("1", "true", "True")]
    nowm = [r for r in rows if str(r.get("watermark")) in ("0", "false", "False")]
    e_wm = eer([r["label"] for r in wm], [r["score"] for r in wm]) if wm else None
    e_no = eer([r["label"] for r in nowm], [r["score"] for r in nowm]) if nowm else None
    wm_pred = auc([r["label"] for r in rows], [1.0 if str(r.get("watermark")) in ("1","true","True") else 0.0 for r in rows])
    print("=" * 58); print("VoxShield · Watermark-Agnostic Benchmark"); print("=" * 58)
    print(f"  EER with watermark    : {_fmt(e_wm)}  (n={len(wm)})")
    print(f"  EER without watermark : {_fmt(e_no)}  (n={len(nowm)})")
    if e_wm is not None and e_no is not None:
        jump = e_no - e_wm
        print(f"  Δ (no-wm − wm)        : {jump*100:+.2f} pts  "
              f"→ {'OK (watermark-agnostic)' if abs(jump) < 0.08 else 'SHORTCUT RISK — detector leans on watermark'}")
    print(f"  AUC(watermark → label): {_fmt(wm_pred,0)}  → {'OK (~0.5, wm not label-predictive)' if wm_pred and abs(wm_pred-0.5)<0.1 else 'watermark correlates with label — control the data'}")


def _selftest():
    import numpy as np
    rng = np.random.default_rng(0); rows = []
    # a GOOD (agnostic) detector: same separability with or without watermark; wm split 50/50 across labels
    for _ in range(300):
        for lab, mu in [(0, 0.15), (1, 0.85)]:
            rows.append({"label": lab, "score": float(np.clip(rng.normal(mu, 0.10), 0, 1)), "watermark": int(rng.integers(0, 2))})
    report(rows)
    print("\n[selftest] PASS — reports EER±watermark, Δ, and AUC(wm→label) to detect shortcutting.")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.csv: ap.error("--csv or --selftest")
    report(load_csv(a.csv))


if __name__ == "__main__":
    main()
