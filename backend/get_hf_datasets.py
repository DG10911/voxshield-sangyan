"""
VoxShield — auto-download + arrange MODERN HuggingFace deepfake datasets.

Fully automatic. Streams + caps big datasets so you get strong diversity of
modern AI generators without terabytes. Writes audio into
  $SSD/voxdata/<name>/real/ and /fake/   so make_manifests.py picks them up.

JOBS = (repo_id, folder, fixed_label, limit, streaming)
  fixed_label: 1=all fake, 0=all real, None=read label column
  limit:       max samples to pull (None = all)
  streaming:   True = pull on-demand (for huge datasets, no full download)

Run:  pip install datasets soundfile   then   python get_hf_datasets.py
"""
import os, numpy as np, soundfile as sf

SSD = os.environ.get("SSD", "/Volumes/KIOXIA")
OUT = os.path.join(SSD, "voxdata")

JOBS = [
    # repo,                                    folder,         fixed, limit, stream
    ("skypro1111/elevenlabs_dataset",          "elevenlabs",   1,     None,  False),  # ElevenLabs clones ⭐
    ("garystafford/deepfake-audio-detection",  "garystafford", None,  None,  False),  # balanced real+fake
    ("ajaykarthick/codecfake-audio",           "codecfake",    1,     2000,  True),   # neural-codec fakes
    ("DeepFense/SpeechFake",                   "speechfake",   None,  3000,  True),   # 40 modern TTS tools
    # ---- India: real human speech (all accents) + multilingual fakes ----
    ("ai4bharat/IndicVoices",                  "indicvoices",  0,     2500,  True),   # REAL · 22 Indian languages, 400+ districts
    ("mueller91/MLAAD",                        "mlaad",        1,     2500,  True),   # FAKE · 50+ langs incl. Indic TTS
]

EXTS_OK = True


def find_audio_key(ex):
    for k, v in ex.items():
        if isinstance(v, dict) and "array" in v and "sampling_rate" in v:
            return k
    return None


def label_from_example(ex, fixed, names):
    if fixed is not None:
        return fixed
    for k in ("label", "labels", "class", "target", "type", "is_fake", "spoof"):
        if k in ex:
            v = ex[k]
            if isinstance(v, bool):
                return int(v)
            if isinstance(v, (int, np.integer)):
                if names and 0 <= v < len(names):
                    s = str(names[v]).lower()
                    return 1 if any(t in s for t in ("fake", "spoof", "synth", "ai", "clone", "gen")) else 0
                return int(v)   # assume 1=fake
            if isinstance(v, str):
                s = v.lower()
                return 1 if any(t in s for t in ("fake", "spoof", "synth", "ai", "clone", "gen")) else 0
    return 1   # default: treat as fake if no label found


def run_job(repo, name, fixed, limit, streaming):
    from datasets import load_dataset
    print(f"== {repo}  (limit={limit}, stream={streaming}) ==")
    ds = load_dataset(repo, split="train", streaming=streaming)
    # try to get ClassLabel names for proper label mapping
    names = None
    try:
        feat = ds.features
        for k in ("label", "labels", "class", "target", "type"):
            if k in feat and getattr(feat[k], "names", None):
                names = feat[k].names
    except Exception:
        pass
    base = os.path.join(OUT, name)
    rdir, fdir = os.path.join(base, "real"), os.path.join(base, "fake")
    os.makedirs(rdir, exist_ok=True); os.makedirs(fdir, exist_ok=True)
    n0 = n1 = 0
    ak = None
    for i, ex in enumerate(ds):
        if limit and (n0 + n1) >= limit:
            break
        try:
            if ak is None:
                ak = find_audio_key(ex)
                if ak is None:
                    print("  ! no audio column found; skipping dataset"); return
            a = ex[ak]
            y = np.asarray(a["array"], dtype="float32"); sr = int(a["sampling_rate"])
            if y.size < 800:
                continue
            lab = label_from_example(ex, fixed, names)
            d = fdir if lab == 1 else rdir
            sf.write(os.path.join(d, f"{name}_{i}.wav"), y, sr)
            n1 += (lab == 1); n0 += (lab == 0)
            if (n0 + n1) % 500 == 0:
                print(f"   …{n0+n1} written")
        except Exception as e:
            if i < 3:
                print("  skip sample:", e)
    print(f"   ✓ {name}: real={n0} fake={n1} -> {base}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for job in JOBS:
        try:
            run_job(*job)
        except Exception as e:
            print(f"  ! {job[0]} failed ({e.__class__.__name__}): {e}")
    print("\nDONE. Next:")
    print('  python make_manifests.py "$SSD/voxdata" --out manifests')
    print("  python make_combined.py")
    print("  python train_fusion.py --train manifests/combined.csv")
