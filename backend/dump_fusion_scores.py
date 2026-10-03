"""
VoxShield — dump per-model fusion scores for a manifest -> fusion_scores.csv.
Unblocks `validate_novelty.py` (voxscore novelty) which needs the per_model JSON
plus label/seen/generator for each clip.

Manifest JSONL (same shape as score_matrix / gen_worst_ai):
    {"path": "/abs/clip.wav", "label": 1, "language": "hi", "generator": "xtts", "seen": 0}

Usage:
    python dump_fusion_scores.py --manifest eval.jsonl --out fusion_scores.csv
    python dump_fusion_scores.py --selftest
"""
from __future__ import annotations
import argparse, csv, json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from score_matrix import read_wav, clip_prep, write_wav   # noqa
import fusion                                             # noqa

FIELDS = ["label", "seen", "generator", "language", "score", "label_str", "per_model"]


def run(manifest, out, limit=None):
    rows = []
    with open(manifest) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = json.loads(line)
            p = m.get("path")
            if not p or not os.path.isfile(p):
                continue
            try:
                y, sr = read_wav(p)
            except Exception as e:
                print("  skip", p, repr(e)[:80]); continue
            y = clip_prep(y, sr)
            res = fusion.analyze(y, 16000)
            rows.append({"label": int(m.get("label", 0)), "seen": int(m.get("seen", 1)),
                         "generator": m.get("generator", ""), "language": m.get("language", ""),
                         "score": round(float(res.get("score", 0.0)), 6),
                         "label_str": res.get("label", ""),
                         "per_model": json.dumps(res.get("per_model", {}))})
            if limit and len(rows) >= limit:
                break
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"[fusion] {len(rows)} rows -> {out}")
    return rows


def _selftest():
    import tempfile
    d = tempfile.mkdtemp(); p = os.path.join(d, "x.wav")
    import numpy as np
    write_wav(p, (0.1 * np.sin(2 * np.pi * 300 * np.arange(16000 * 3) / 16000)).astype("float32"))
    man = os.path.join(d, "m.jsonl")
    open(man, "w").write(json.dumps({"path": p, "label": 1, "generator": "x", "language": "hi", "seen": 0}) + "\n")
    # stub fusion.analyze so we don't load the model bank
    orig = fusion.analyze
    fusion.analyze = lambda y, sr: {"score": 0.7, "label": "MEDIUM", "per_model": {"acoustic-dsp": 0.6, "xlsr": 0.8}}
    try:
        rows = run(man, os.path.join(d, "out.csv"))
    finally:
        fusion.analyze = orig
    assert rows and json.loads(rows[0]["per_model"])["xlsr"] == 0.8
    print("[selftest] PASS — fusion_scores.csv written with per_model JSON (validate_novelty can consume it).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest"); ap.add_argument("--out", default="fusion_scores.csv")
    ap.add_argument("--limit", type=int, default=None); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not a.manifest: ap.error("--manifest or --selftest")
    run(a.manifest, a.out, a.limit)


if __name__ == "__main__":
    main()
