"""
VoxShield — demo training set that INCLUDES your own AI clips (ElevenLabs etc).

Combines:
  - real voices from In-the-Wild (plenty),
  - In-the-Wild fakes,
  - YOUR custom AI clips in  $SSD/voxdata/custom/fake/  (oversampled so the
    fusion head actually learns them — this is what makes the live demo catch
    ElevenLabs).

Output: manifests/demo.csv   ->   train with:
    python train_fusion.py --train manifests/demo.csv --augment
"""
import csv, glob, os, random
random.seed(0)
SSD = os.environ.get("SSD", "/Volumes/KIOXIA")
N = 1500   # In-the-Wild real / fake each

itw = list(csv.DictReader(open("manifests/in_the_wild.csv")))
real = [r["path"] for r in itw if r["label"] == "0"]
fake = [r["path"] for r in itw if r["label"] == "1"]
random.shuffle(real); random.shuffle(fake)

exts = (".mp3", ".wav", ".flac", ".m4a", ".ogg")
custom = [c for c in glob.glob(os.path.join(SSD, "voxdata/custom/fake", "*"))
          if c.lower().endswith(exts)]
print(f"custom AI clips found: {len(custom)}")

rows = [(p, "0", "itw") for p in real[:N]]
rows += [(p, "1", "itw") for p in fake[:N]]

# Oversample custom AI fakes so they're ~1/3 of the fake class (learnable, not lost)
if custom:
    target = max(len(custom), N // 2)
    k = max(1, target // len(custom))
    for c in custom:
        for _ in range(k):
            rows.append((c, "1", "custom"))
    print(f"oversampled {len(custom)} custom clips x{k} = {len(custom)*k} fake instances")
else:
    print("WARNING: no custom clips in custom/fake — add ElevenLabs/TTS mp3s there!")

random.shuffle(rows)
with open("manifests/demo.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["path", "label", "dataset"])
    for p, l, d in rows: w.writerow([p, l, d])
print(f"wrote manifests/demo.csv with {len(rows)} rows")
