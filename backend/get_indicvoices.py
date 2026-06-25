"""
VoxShield — AI4Bharat IndicVoices loader (real Indian speech, all accents).
Downloads a balanced slice of REAL human Indian voices across major languages,
decoding audio WITHOUT torchcodec (uses soundfile on raw bytes).

Needs: huggingface-cli login + access granted on the dataset page.
Run:   python get_indicvoices.py
Output: $SSD/voxdata/indicvoices/real/*.wav   (all label = real / bonafide)
"""
import os, io, numpy as np, soundfile as sf

SSD = os.environ.get("SSD", "/Volumes/KIOXIA")
OUT = os.path.join(SSD, "voxdata", "indicvoices", "real")
os.makedirs(OUT, exist_ok=True)

LANGS = ["hindi", "tamil", "bengali", "telugu", "marathi", "kannada",
         "malayalam", "gujarati", "punjabi", "assamese"]
PER_LANG = 400          # ~400 clips/language → ~4000 real Indian voices
AUDIO_COL_CANDIDATES = ["audio_filepath", "audio", "audio_path"]


def main():
    from datasets import load_dataset, Audio
    total = 0
    for lang in LANGS:
        got = 0
        for split in ("valid", "train"):
            try:
                ds = load_dataset("ai4bharat/IndicVoices", lang, split=split, streaming=True)
            except Exception as e:
                continue
            # find the audio column and turn OFF decoding (avoids torchcodec)
            feats = getattr(ds, "features", {}) or {}
            acol = next((c for c in AUDIO_COL_CANDIDATES if c in feats), None)
            if acol is None:
                acol = next((c for c in AUDIO_COL_CANDIDATES if True), "audio_filepath")
            try:
                ds = ds.cast_column(acol, Audio(decode=False))
            except Exception:
                pass
            try:
                for ex in ds:
                    if got >= PER_LANG:
                        break
                    a = ex.get(acol)
                    if not isinstance(a, dict):
                        continue
                    b = a.get("bytes")
                    if not b:
                        continue
                    try:
                        y, sr = sf.read(io.BytesIO(b), dtype="float32")
                        if y.ndim > 1:
                            y = y.mean(1)
                    except Exception:
                        continue
                    if y.size < 800:
                        continue
                    sf.write(os.path.join(OUT, f"{lang}_{got}.wav"), y, sr)
                    got += 1
            except Exception as e:
                print(f"  {lang}/{split} stream issue: {str(e)[:80]}")
            if got >= PER_LANG:
                break
        total += got
        print(f"  {lang:12s} -> {got} real clips")
    print(f"\n✓ IndicVoices: {total} real Indian voices -> {OUT}")
    print('Next: python make_manifests.py "$SSD/voxdata" --out manifests'
          ' && python make_combined.py && python train_fusion.py --train manifests/combined.csv --augment')


if __name__ == "__main__":
    main()
