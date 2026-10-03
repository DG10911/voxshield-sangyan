"""
VoxShield — Paper-ready experiment report (one command).

Consumes ONE tagged scores CSV (label, score, generator, language, channel, seen)
and emits every table a manuscript needs, in order:

  1. overall + per-language EER/AUC
  2. per-channel EER + degradation vs clean            (claim C1/C2)
  3. per-axis + generator×channel cross-tab + worst cells + seen/unseen gap  (C1/C4)
  4. leave-one-generator-out unseen-generator EER       (C4)
  5. selective prediction / abstention: risk–coverage, FP reduction, Cllr   (C3)

CSV schema matches what pipeline/train_corpus.py writes (scores.csv).

Usage:
    python paper_report.py --csv checkpoints/round_*/scores.csv
    python paper_report.py --csv scores.csv --baseline clean --out report.txt
    python paper_report.py --selftest
"""
from __future__ import annotations
import argparse, sys, os, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eval_gengap as G
import eval_channel as C
import eval_matrix as M
import eval_selective as S


class _Tee:
    def __init__(self, *streams): self.streams = streams
    def write(self, s):
        for st in self.streams: st.write(s)
    def flush(self):
        for st in self.streams: st.flush()


def _per_language(rows):
    langs = {}
    for r in rows:
        v = r.get("language") or r.get("lang")
        if v: langs.setdefault(v, []).append(r)
    if not langs:
        return
    print("\n  ── per-language (paper Table C1) ──")
    print(f"    {'language':<12} {'EER':>8} {'AUC':>7} {'n':>7} {'n_fake':>7}")
    for lg in sorted(langs):
        gr = langs[lg]; y = [r["label"] for r in gr]; s = [r["score"] for r in gr]
        print(f"    {str(lg):<12} {G._fmt(G.eer(y,s)):>8} {G._fmt(G.auc(y,s),0):>7} "
              f"{len(gr):>7} {sum(y):>7}")


def run(rows, baseline="clean", cross=("language", "channel"), coverages=S.report.__defaults__[0]):
    print("#" * 66)
    print("# VoxShield — Paper Experiment Report")
    print("#" * 66)
    _per_language(rows)
    print()
    C.report(rows, baseline=baseline)                       # per-channel + Δ
    print()
    M.matrix(rows, cross=list(cross))                       # axes + cross-tab + worst + gap
    print()
    G.logo(rows)                                            # unseen-generator LOGO
    print()
    S.report(rows, coverages)                               # abstention / calibration
    print("\n[done] tables above correspond to paper claims C1–C4.")


def _selftest():
    import numpy as np
    rng = np.random.default_rng(0); rows = []
    langs = ["hi", "bn", "ta", "mr"]
    gens = {"xtts": (1, 0.10), "bark": (0, 0.22), "elevenlabs": (1, 0.12), "freevc24": (0, 0.28)}
    chans = {"clean": 0.0, "g711_ulaw": 0.10, "g711_alaw": 0.09, "g722": 0.05}
    for g, (seen, sd) in gens.items():
        for ch, cadd in chans.items():
            sd2 = sd + cadd
            for lg in langs:
                for _ in range(40):
                    rows.append({"label": 1, "score": float(np.clip(rng.normal(0.80, sd2), 0, 1)),
                                 "generator": g, "language": lg, "channel": ch, "seen": seen})
                for _ in range(40):
                    rows.append({"label": 0, "score": float(np.clip(rng.normal(0.20, 0.12), 0, 1)),
                                 "generator": "real", "language": lg, "channel": ch, "seen": 1})
    run(rows)
    print("\n[selftest] PASS — full paper report rendered from one tagged CSV.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--baseline", default="clean")
    ap.add_argument("--cross", nargs=2, default=["language", "channel"])
    ap.add_argument("--out"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest(); return
    if not a.csv:
        ap.error("--csv or --selftest")
    rows = G.load_csv(a.csv)
    if a.out:
        buf = io.StringIO(); old = sys.stdout; sys.stdout = _Tee(buf, old)
        try: run(rows, a.baseline, tuple(a.cross))
        finally:
            sys.stdout = old
            open(a.out, "w").write(buf.getvalue())
            print(f"[written] {a.out}")
    else:
        run(rows, a.baseline, tuple(a.cross))


if __name__ == "__main__":
    main()
