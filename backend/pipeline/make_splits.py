"""
VoxShield split generator — enforces the four disjointness constraints from the
dataset plan so cross-generator EER is honest.

Constraints:
  1. SPEAKER-disjoint  — a speaker's rows never span train/val/test
  2. GENERATOR-holdout — one cloner family held out entirely for the test set
  3. DATASET-holdout   — MLAAD kept as OOD (never trained on)
  4. (codec-holdout is applied at augmentation time, not here — see telephony_aug)

Strategy:
  - MLAAD  -> split = "ood"        (source-disjoint generalization test)
  - held-out generator (default 'xtts') -> any clip from it goes to "test_gen"
  - remaining rows: partition by SPEAKER into train/val/test (70/15/15)

Usage:
  python make_splits.py --manifest manifests_v2/manifest.csv \
      --out manifests_v2/manifest_split.csv --holdout-generator xtts
"""
import csv, argparse, hashlib

def bucket(speaker, seed):
    h = int(hashlib.md5(f"{seed}:{speaker}".encode()).hexdigest(), 16) % 100
    return "train" if h < 70 else ("val" if h < 85 else "test")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="manifests_v2/manifest.csv")
    ap.add_argument("--out", default="manifests_v2/manifest_split.csv")
    ap.add_argument("--holdout-generator", default="xtts",
                    help="substring; any generator containing it goes to test_gen (cross-generator eval)")
    ap.add_argument("--ood-datasets", default="mlaad")
    ap.add_argument("--seed", default="voxshield42")
    a = ap.parse_args()
    ood = set(a.ood_datasets.split(","))
    rows = list(csv.DictReader(open(a.manifest)))
    for r in rows:
        if r["dataset"] in ood:
            r["split"] = "ood"
        elif a.holdout_generator and a.holdout_generator in r["generator"]:
            r["split"] = "test_gen"          # unseen-generator test
        else:
            r["split"] = bucket(r["speaker"], a.seed)
    fields = list(rows[0].keys())
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(f"[splits] {len(rows)} rows -> {a.out}")
    print("  by split:", dict(Counter(r["split"] for r in rows)))
    # leakage self-check: no speaker in >1 of {train,val,test}
    from collections import defaultdict
    sp = defaultdict(set)
    for r in rows:
        if r["split"] in ("train", "val", "test"):
            sp[r["speaker"]].add(r["split"])
    leaks = [s for s, v in sp.items() if len(v) > 1]
    print(f"  speaker-leak check: {len(leaks)} speakers span multiple splits "
          f"({'OK' if not leaks else 'LEAK!'})")
    print(f"  held-out generator '{a.holdout_generator}': "
          f"{sum(1 for r in rows if r['split']=='test_gen')} clips in test_gen")

if __name__ == "__main__":
    main()
