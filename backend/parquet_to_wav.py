"""
VoxShield — extract wavs + manifest rows from parquet shards (IndicSynth / IndicVoices).
Feeds `score_matrix.py`, `dump_fusion_scores.py`, `paper_report.py` — i.e. lets us
build the external-unseen-generator GAP from parquet corpora.

IndicSynth  : audio column "audio"           (dict: bytes/path/array, sampling_rate)
IndicVoices : audio column "audio_filepath"  (dict)

Usage:
    python parquet_to_wav.py --glob "data/hindi_eval/indicsynth/Hindi/*.parquet" \
        --label 1 --generator freevc24 --language hindi --seen 1 --limit 1500 \
        --out-dir data_gap/hindi/seen --manifest data_gap/hindi/manifest.jsonl
    python parquet_to_wav.py --glob ".../indicvoices_real/hindi/*.parquet" --audio-col audio_filepath \
        --label 0 --generator real --language hindi --seen 1 --limit 1500 \
        --out-dir data_gap/hindi/real --manifest data_gap/hindi/manifest.jsonl --append
    python parquet_to_wav.py --selftest
"""
from __future__ import annotations
import argparse, glob, io, json, os, sys
import numpy as np


def _audio_bytes(cell):
    """Return (bytes_or_None, path_or_None) from an HF audio cell."""
    if isinstance(cell, dict):
        b = cell.get("bytes") or cell.get("path")
        if isinstance(b, (bytes, bytearray)):
            return bytes(b), None
        if isinstance(b, str):
            return None, b
    elif isinstance(cell, (bytes, bytearray)):
        return bytes(cell), None
    return None, None


def extract(pattern, audio_col, label, generator, language, seen, limit, out_dir, manifest, append=False):
    import pandas as pd, soundfile as sf
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"!! no parquet matched {pattern}"); return 0
    os.makedirs(out_dir, exist_ok=True)
    f = open(manifest, "a" if append else "w")
    made = 0
    for pf in files:
        if made >= limit:
            break
        try:
            df = pd.read_parquet(pf, columns=[audio_col])
        except Exception as e:
            print("  skip", pf, repr(e)[:80]); continue
        for cell in df[audio_col].tolist():
            if made >= limit:
                break
            b, p = _audio_bytes(cell)
            try:
                if b is not None:
                    y, sr = sf.read(io.BytesIO(b), dtype="float32")
                elif p is not None and os.path.isfile(p):
                    y, sr = sf.read(p, dtype="float32")
                else:
                    continue
            except Exception:
                continue
            if np.ndim(y) > 1:
                y = np.mean(y, 1)
            out = os.path.abspath(os.path.join(out_dir, f"{language}_{label}_{made:05d}.wav"))
            sf.write(out, np.clip(y, -1, 1), sr)
            f.write(json.dumps({"path": out, "label": int(label), "language": language,
                                "generator": generator, "seen": int(seen)}) + "\n")
            made += 1
    f.close()
    print(f"[extract] {made} wavs -> {out_dir}  (manifest={manifest}, append={append})")
    return made


def _selftest():
    import soundfile as sf, pandas as pd, tempfile
    d = tempfile.mkdtemp()
    # synthesize a tiny parquet with an HF-style audio cell
    buf = io.BytesIO(); sf.write(buf, np.zeros(1600, "float32"), 16000, format="WAV")
    df = pd.DataFrame({"audio": [{"bytes": buf.getvalue(), "path": None, "sampling_rate": 16000}]})
    pq = os.path.join(d, "x.parquet"); df.to_parquet(pq)
    man = os.path.join(d, "m.jsonl")
    n = extract(pq, "audio", 1, "freevc24", "hi", 1, 5, os.path.join(d, "wavs"), man)
    assert n == 1 and json.loads(open(man).read().strip())["label"] == 1
    print("[selftest] PASS — parquet audio extracted to wav + manifest row.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob"); ap.add_argument("--audio-col", default="audio")
    ap.add_argument("--label", type=int, default=1); ap.add_argument("--generator", default="freevc24")
    ap.add_argument("--language", default="hi"); ap.add_argument("--seen", type=int, default=1)
    ap.add_argument("--limit", type=int, default=1500); ap.add_argument("--out-dir")
    ap.add_argument("--manifest", default="manifest.jsonl"); ap.add_argument("--append", action="store_true")
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not (a.glob and a.out_dir): ap.error("--glob and --out-dir required")
    extract(a.glob, a.audio_col, a.label, a.generator, a.language, a.seen, a.limit, a.out_dir, a.manifest, a.append)


if __name__ == "__main__":
    main()
