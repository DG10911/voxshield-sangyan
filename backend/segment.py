"""
VoxShield — Partial-Deepfake Segmentation + Generation-Boundary Detection
(roadmap §17, §18).

Instead of one FAKE/REAL label for a whole clip, produce a TIMELINE:
    00:00–00:06 HUMAN
    00:06–00:09 SYNTHETIC
    ...
plus the boundary points where the source appears to switch (Human→AI, AI→Human,
generator A→B). Consumes the per-window scores that fusion.stream_analyze already
produces (list of {t, score}). Boundaries = large, sustained jumps in the score
track. numpy-only; deterministic; non-breaking.
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict


def segment(windows: List[Dict], hi: float = 0.60, lo: float = 0.40,
            boundary_delta: float = 0.30) -> dict:
    """windows: [{'t': end_time_s, 'score': P_synthetic}, ...] in time order."""
    if not windows:
        return {"segments": [], "boundaries": []}
    ts = [float(w["t"]) for w in windows]
    ss = np.array([float(w["score"]) for w in windows])

    # hysteresis labelling: SYNTHETIC once >hi, stays until <lo (and vice-versa)
    labels = []
    state = "HUMAN"
    for s in ss:
        if state == "HUMAN" and s >= hi: state = "SYNTHETIC"
        elif state == "SYNTHETIC" and s <= lo: state = "HUMAN"
        labels.append(state)

    # collapse into contiguous segments
    segs = []
    start_i = 0
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[start_i]:
            seg_scores = ss[start_i:i]
            t0 = 0.0 if start_i == 0 else ts[start_i - 1]
            t1 = ts[i - 1]
            segs.append({"start_s": round(t0, 2), "end_s": round(t1, 2),
                         "label": labels[start_i],
                         "mean_score": round(float(seg_scores.mean()), 3),
                         "confidence": round(float(min(1.0, abs(seg_scores.mean() - 0.5) * 2)), 3)})
            start_i = i

    # explicit generation boundaries: large jumps between adjacent windows
    boundaries = []
    d = np.abs(np.diff(ss))
    for i in np.where(d >= boundary_delta)[0]:
        boundaries.append({"t_s": round(ts[i], 2),
                           "from": round(float(ss[i]), 3), "to": round(float(ss[i + 1]), 3),
                           "kind": "HUMAN→AI" if ss[i + 1] > ss[i] else "AI→HUMAN"})

    partial = len({s["label"] for s in segs}) > 1
    return {"segments": segs, "boundaries": boundaries, "is_partial_deepfake": partial,
            "n_segments": len(segs)}


def _selftest():
    # synthetic score track: human (low) → synthetic (high) → human (low)
    win = []
    for k in range(18):
        t = round((k + 1) * 1.0, 2)
        s = 0.85 if 6 <= k < 11 else 0.12
        win.append({"t": t, "score": s + 0.03 * np.sin(k)})
    r = segment(win)
    for s in r["segments"]:
        print(f"  {s['start_s']:>5}–{s['end_s']:<5}s  {s['label']:<9} mean={s['mean_score']} conf={s['confidence']}")
    print("  boundaries:", [(b["t_s"], b["kind"]) for b in r["boundaries"]])
    assert r["is_partial_deepfake"] and r["n_segments"] == 3 and len(r["boundaries"]) == 2, r
    print("\n[selftest] PASS — HUMAN→SYNTHETIC→HUMAN segmented with 2 generation boundaries.")


if __name__ == "__main__":
    _selftest()
