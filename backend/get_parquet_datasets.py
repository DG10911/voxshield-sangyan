"""
VoxShield — decode parquet-based HF audio datasets WITHOUT torchcodec/ffmpeg.
Reads the audio bytes straight from the parquet and decodes with soundfile
(libsndfile handles wav/flac/ogg). Writes into $SSD/voxdata/<name>/real|fake.

Run:  pip install pyarrow   then   python get_parquet_datasets.py
"""
import os, io, glob, numpy as np, soundfile as sf

SSD = os.environ.get("SSD", "/Volumes/KIOXIA")
OUT = os.path.join(SSD, "voxdata")

# (repo, folder, fixed_label, limit)
JOBS = [
    ("garystafford/deepfake-audio-detection", "garystafford", None, None),
]


def label_names(repo):
    try:
        from datasets import load_dataset_builder
        f = load_dataset_builder(repo).info.features
        for k in ("label", "labels", "class", "target"):
            if k in f and getattr(f[k], "names", None):
                return k, f[k].names
    except Exception as e:
        print("  (feature names unavailable:", e, ")")
    return None, None


def job(repo, name, fixed, limit):
    import pyarrow.parquet as pq
    from huggingface_hub import snapshot_download
    print(f"== {repo} ==")
    p = snapshot_download(repo, repo_type="dataset",
                          local_dir=os.path.join(OUT, name, "_pq"),
                          allow_patterns=["*.parquet"])
    files = sorted(glob.glob(os.path.join(p, "**", "*.parquet"), recursive=True))
    lk, names = label_names(repo)
    base = os.path.join(OUT, name)
    rd, fd = os.path.join(base, "real"), os.path.join(base, "fake")
    os.makedirs(rd, exist_ok=True); os.makedirs(fd, exist_ok=True)
    n0 = n1 = skip = 0
    for fp in files:
        rows = pq.read_table(fp).to_pylist()
        for row in rows:
            if limit and (n0 + n1) >= limit:
                break
            au = None
            for v in row.values():
                if isinstance(v, dict) and v.get("bytes"):
                    au = v; break
            if au is None:
                continue
            try:
                y, sr = sf.read(io.BytesIO(au["bytes"]), dtype="float32")
                if y.ndim > 1:
                    y = y.mean(1)
            except Exception:
                skip += 1; continue
            if fixed is not None:
                lab = fixed
            elif lk and lk in row:
                v = row[lk]
                s = str(names[v]).lower() if names and isinstance(v, int) else str(v).lower()
                lab = 1 if any(t in s for t in ("fake", "spoof", "synth", "ai", "gen", "clone")) else 0
            else:
                lab = 1
            sf.write(os.path.join(fd if lab == 1 else rd, f"{name}_{n0+n1}.wav"), y, sr)
            n1 += (lab == 1); n0 += (lab == 0)
    print(f"  ✓ {name}: real={n0} fake={n1}  (skipped {skip} undecodable)")


if __name__ == "__main__":
    for j in JOBS:
        try:
            job(*j)
        except Exception as e:
            print(f"  ! {j[0]} failed: {e}")
    print("\nNext: python make_manifests.py \"$SSD/voxdata\" --out manifests"
          " && python make_combined.py && python train_fusion.py --train manifests/combined.csv")
