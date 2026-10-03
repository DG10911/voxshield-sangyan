"""
VoxShield — Master Evaluation Matrix (roadmap §22, §35).

"Never report only a single 98% number." This harness ingests a fully-tagged
scored CSV and produces the multi-axis performance matrix the vision demands:
    * EER per value on every available axis (generator, language, channel,
      device, environment, style, replay, ...)
    * 2-D cross-tabs (e.g. generator × channel) to expose interaction effects
    * the SEEN vs UNSEEN generalization gap (delegates to eval_gengap)
    * the WORST cells (highest-EER slices) — the priority attack surface

Pure measurement, no GPU. Input CSV needs at least: label, score (+ any tag columns).
Usage:  python eval_matrix.py --csv scores.csv
        python eval_matrix.py --csv scores.csv --cross generator channel
        python eval_matrix.py --selftest
"""
from __future__ import annotations
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_gengap import eer, auc, _fmt, load_csv, report as gengap_report

AXES = ["generator", "language", "channel", "device", "environment", "style", "replay", "codec"]


def _axis(rows, key):
    g = {}
    for r in rows:
        v = r.get(key)
        if v not in (None, ""):
            g.setdefault(v, []).append(r)
    out = []
    for v, gr in g.items():
        e = eer([r["label"] for r in gr], [r["score"] for r in gr])
        out.append((v, e, len(gr), sum(r["label"] for r in gr)))
    return out


def matrix(rows, cross=None):
    present = [a for a in AXES if any(r.get(a) for r in rows)]
    print("=" * 64); print("VoxShield · Master Evaluation Matrix"); print("=" * 64)
    y = [r["label"] for r in rows]; s = [r["score"] for r in rows]
    print(f"  overall  EER={_fmt(eer(y,s))}  AUC={_fmt(auc(y,s),0)}  n={len(rows)}  axes={present}")

    worst = []
    for ax in present:
        cells = _axis(rows, ax)
        print(f"\n  ── axis: {ax} ──")
        for v, e, n, pos in sorted(cells, key=lambda c: (-(c[1] or -1))):
            print(f"     {str(v):<26} EER={_fmt(e)}  n={n:>5} pos={pos:>5}")
            if e is not None:
                worst.append((ax, v, e, n))

    # 2-D cross-tab
    if cross and len(cross) == 2 and all(a in present for a in cross):
        a, b = cross
        va = sorted({r.get(a) for r in rows if r.get(a)})
        vb = sorted({r.get(b) for r in rows if r.get(b)})
        print(f"\n  ── cross-tab: {a} × {b} (EER) ──")
        print(f"     {a}\\{b}:   " + "  ".join(str(v) for v in vb))
        for x in va:
            cells = []
            for yv in vb:
                sub = [r for r in rows if r.get(a) == x and r.get(b) == yv]
                e = eer([r["label"] for r in sub], [r["score"] for r in sub]) if sub else None
                cells.append(_fmt(e))
            print(f"     {str(x):<18} " + " ".join(cells))

    # worst cells
    if worst:
        print("\n  ── WORST cells (priority attack surface) ──")
        for ax, v, e, n in sorted(worst, key=lambda w: -w[2])[:8]:
            print(f"     {ax}={v:<22} EER={e*100:5.2f}%  n={n}")

    if any(r.get("seen") for r in rows):
        print()
        gengap_report(rows)   # append the seen/unseen generalization gap + LOGO section


def _selftest():
    import numpy as np
    rng = np.random.default_rng(0); rows = []
    gens = {"freevc24": (1, 0.06), "bark": (0, 0.24), "elevenlabs": (0, 0.13)}
    chans = {"clean": 0.0, "g711_ulaw": 0.08}
    for g, (seen, base) in gens.items():
        for ch, cadd in chans.items():
            sd = base + cadd
            for _ in range(150):
                rows.append({"label": 1, "score": float(np.clip(rng.normal(0.85, sd), 0, 1)),
                             "generator": g, "channel": ch, "language": rng.choice(["hi", "bn"]), "seen": seen})
        for _ in range(150):
            rows.append({"label": 0, "score": float(np.clip(rng.normal(0.15, 0.08), 0, 1)),
                         "generator": "real", "channel": "clean", "language": "hi", "seen": 1})
    matrix(rows, cross=["generator", "channel"])
    print("\n[selftest] PASS — multi-axis matrix, cross-tab, worst cells, and generalization gap reported.")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv"); ap.add_argument("--cross", nargs=2)
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.csv: ap.error("--csv or --selftest")
    matrix(load_csv(a.csv), cross=a.cross)


if __name__ == "__main__":
    main()
