"""
VoxShield — balanced combined training set across ALL datasets.

Caps each dataset/class so no single set dominates (so ElevenLabs & modern
fakes are well represented), then balances real vs fake by oversampling.
Output: manifests/combined.csv  ->  python train_fusion.py --train manifests/combined.csv
"""
import csv, glob, os, random
random.seed(0)
mdir = "manifests"
import os as _os
CAP = int(_os.environ.get("VOXSHIELD_CAP", "3000"))   # per dataset/class; raise via env for more accuracy
SKIP = {"combined.csv", "demo.csv", "itw_small.csv", "super_train.csv", "itw_test.csv"}

buckets = {}
for c in glob.glob(os.path.join(mdir, "*.csv")):
    if os.path.basename(c) in SKIP:
        continue
    for r in csv.DictReader(open(c)):
        ds = r.get("dataset", "x")
        buckets.setdefault(ds, {"0": [], "1": []})
        buckets[ds][r["label"]].append((r["path"], r["label"], ds))

real, fake = [], []
for ds, b in buckets.items():
    for lab, lst in b.items():
        random.shuffle(lst)
        sel = lst[:CAP]
        (real if lab == "0" else fake).extend(sel)
        if sel:
            print(f"  {ds:16s} {'real' if lab=='0' else 'fake'}: {len(sel)}")

random.shuffle(real); random.shuffle(fake)
# balance classes by oversampling the smaller one
if real and fake:
    if len(fake) < len(real):
        fake = (fake * (len(real) // len(fake) + 1))[:len(real)]
    elif len(real) < len(fake):
        real = (real * (len(fake) // len(real) + 1))[:len(fake)]

rows = real + fake
random.shuffle(rows)
with open(os.path.join(mdir, "combined.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["path", "label", "dataset"])
    for p, l, d in rows: w.writerow([p, l, d])
print(f"combined.csv: {len(rows)} rows (real {len(real)} / fake {len(fake)})")
