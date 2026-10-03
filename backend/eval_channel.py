"""
VoxShield — Channel-Matrix evaluation (roadmap §22, §23, §35).

Reports EER per channel/codec and the DEGRADATION each channel causes relative to
a clean baseline — so we can see, e.g., how much G.711 μ-law or packet-loss hurts.
Reuses eval_gengap's metric functions. Input CSV: label, score, channel[, generator].

Usage: python eval_channel.py --csv scores_by_channel.csv   |   --selftest
"""
from __future__ import annotations
import argparse, csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_gengap import eer, auc, _fmt, load_csv


def report(rows, baseline="clean"):
    chans = {}
    for r in rows:
        chans.setdefault(r.get("channel", "?") or "?", []).append(r)
    base_eer = None
    if baseline in chans:
        g = chans[baseline]; base_eer = eer([r["label"] for r in g], [r["score"] for r in g])
    print("=" * 58); print("VoxShield · Channel-Matrix EER"); print("=" * 58)
    print(f"  {'channel':<18} {'EER':>7} {'AUC':>7} {'Δ vs clean':>11} {'n':>7}")
    for c in sorted(chans):
        g = chans[c]; e = eer([r["label"] for r in g], [r["score"] for r in g])
        delta = "" if (base_eer is None or e is None) else f"{(e-base_eer)*100:+6.2f}pts"
        print(f"  {c:<18} {_fmt(e)} {_fmt(auc([r['label'] for r in g],[r['score'] for r in g]),0):>7} {delta:>11} {len(g):>7}")
    if base_eer is not None:
        print(f"\n  baseline '{baseline}' EER = {_fmt(base_eer)} — positive Δ = channel degrades detection.")


def _selftest():
    import numpy as np
    rng = np.random.default_rng(0); rows = []
    # clean: well separated; g711/narrowband: harder; packet_loss: hardest
    spread = {"clean": 0.06, "g711_ulaw": 0.16, "opus": 0.10, "packet_loss": 0.26}
    for ch, sd in spread.items():
        for _ in range(300):
            rows.append({"label": 0, "score": float(np.clip(rng.normal(0.15, sd), 0, 1)), "channel": ch})
            rows.append({"label": 1, "score": float(np.clip(rng.normal(0.85, sd), 0, 1)), "channel": ch})
    report(rows)
    print("\n[selftest] PASS — per-channel EER + degradation-vs-clean reported.")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv"); ap.add_argument("--baseline", default="clean")
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.csv: ap.error("--csv or --selftest")
    report(load_csv(a.csv), a.baseline)


if __name__ == "__main__":
    main()
