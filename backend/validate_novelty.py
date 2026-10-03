"""
VoxShield — validate the voxscore NOVELTY heuristic (roadmap §12, §13).

Question: does voxscore.novelty (detector-disagreement + score-ambiguity) actually
RISE on UNSEEN-generator fakes vs SEEN-generator fakes? If yes, the heuristic tracks
open-set inputs and can be promoted [HYP]->[PROJECT RESULT]; if not, it should be
replaced by an embedding-distance / density open-set score.

Reads fusion_scores.csv (label, seen, generator, per_model JSON) produced by
dump_fusion_scores.py, runs voxscore() per row, and compares novelty / REVIEW-rate
across SEEN vs UNSEEN fakes. Honest: it reports whatever the data shows.
"""
from __future__ import annotations
import csv, json, sys, os, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxscore import voxscore
from eval_gengap import auc


def run(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                pm = json.loads(r["per_model"])
            except Exception:
                continue
            if not pm or "_error" in pm:
                continue
            vs = voxscore(pm)
            rows.append({"label": int(r["label"]), "seen": int(r["seen"]),
                         "generator": r.get("generator"),
                         "novelty": vs["novelty"], "risk": vs["risk"],
                         "synthetic": vs["synthetic_score"]})
    if not rows:
        print("no usable rows (per_model empty / errored)"); return

    def agg(sub, name):
        if not sub:
            print(f"  {name:<24} (none)"); return None
        nov = np.mean([r["novelty"] for r in sub])
        rev = np.mean([r["risk"] == "REVIEW" for r in sub])
        syn = np.mean([r["synthetic"] for r in sub])
        print(f"  {name:<24} n={len(sub):<4} mean_novelty={nov:.3f}  REVIEW_rate={rev:.2%}  mean_synth={syn:.3f}")
        return nov

    print("=" * 62); print("VoxScore novelty validation — SEEN vs UNSEEN generators"); print("=" * 62)
    seen_fake = [r for r in rows if r["label"] == 1 and r["seen"] == 1]
    unseen_fake = [r for r in rows if r["label"] == 1 and r["seen"] == 0]
    real = [r for r in rows if r["label"] == 0]
    n_seen = agg(seen_fake, "SEEN fakes")
    n_unseen = agg(unseen_fake, "UNSEEN fakes")
    agg(real, "genuine (real)")

    # does novelty predict 'unseen' among fakes?
    fakes = seen_fake + unseen_fake
    if seen_fake and unseen_fake:
        y = [1 if r["seen"] == 0 else 0 for r in fakes]      # 1 = unseen
        a = auc(y, [r["novelty"] for r in fakes])
        print(f"\n  AUC(novelty → is-UNSEEN, among fakes) = {a:.3f}")
        verdict = ("VALIDATED — novelty rises on unseen generators" if (n_unseen and n_seen and n_unseen > n_seen + 0.03 and (a or 0) > 0.55)
                   else "NOT VALIDATED — novelty does not clearly track unseen; use embedding-distance open-set instead")
        print(f"  → {verdict}")
    print("\n  (Heuristic status stays [HYP] unless VALIDATED above.)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--csv", required=True); a = ap.parse_args()
    run(a.csv)
