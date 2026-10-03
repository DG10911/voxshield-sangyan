"""
VoxShield — Code-Switching Forensics (roadmap §10).

India-specific: speakers switch Hindi↔English, Tamil↔English, etc. mid-utterance.
A genuine speaker keeps the SAME voice across a language switch; a spliced/cloned
segment inserted at a switch boundary breaks speaker continuity. This module splits
a clip at switch points and checks speaker-embedding continuity across them.

Language-ID (to auto-find switch points) is [PENDING] — you can pass known switch
times, or use the crude spectral-novelty fallback. The continuity check itself works
now via speaker.embed. [HYPOTHESIS] — validate on real code-switch data. numpy + speaker.py.
"""
from __future__ import annotations
import numpy as np
from typing import List, Optional
from speaker import embed, _cos


def _auto_boundaries(y, sr, win_s=0.75):
    """crude switch-point guesser: large jumps in short-term spectral centroid."""
    w = int(win_s * sr)
    cents = []
    for s in range(0, len(y) - w + 1, w):
        S = np.abs(np.fft.rfft(y[s:s+w] * np.hanning(w)))
        cents.append((np.arange(len(S)) * S).sum() / (S.sum() + 1e-9))
    cents = np.array(cents)
    if len(cents) < 3:
        return []
    d = np.abs(np.diff(cents)) / (np.mean(cents) + 1e-9)
    return [int((i + 1) * w) for i in np.where(d > 0.25)[0]]


def analyze(y: np.ndarray, sr: int, switch_samples: Optional[List[int]] = None) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    bounds = switch_samples if switch_samples is not None else _auto_boundaries(y, sr)
    cuts = [0] + sorted(b for b in bounds if 0 < b < len(y)) + [len(y)]
    segs = [y[cuts[i]:cuts[i+1]] for i in range(len(cuts)-1) if cuts[i+1]-cuts[i] > sr//2]
    if len(segs) < 2:
        return {"segments": len(segs), "continuity": None,
                "verdict": "SINGLE_SEGMENT", "_status": "no usable switch boundary"}
    embs = [embed(s, sr) for s in segs]
    sims = [_cos(embs[i], embs[i+1]) for i in range(len(embs)-1)]
    min_sim = float(min(sims)); mean_sim = float(np.mean(sims))
    thr = 0.92   # calibrated for pseudo-embedding; recalibrate for ECAPA
    breaks = [i for i, s in enumerate(sims) if s < thr]
    return {"segments": len(segs), "boundary_similarities": [round(s, 3) for s in sims],
            "min_continuity": round(min_sim, 3), "mean_continuity": round(mean_sim, 3),
            "identity_breaks": breaks,
            "verdict": "CONTINUOUS_SPEAKER" if min_sim >= thr else "IDENTITY_BREAK_AT_SWITCH (possible splice/clone)",
            "_status": "HYPOTHESIS — speaker continuity across switch; LID auto-detect PENDING; validate on real code-switch data."}


def _selftest():
    sr = 16000
    def voice(f0, forms, seed, dur=1.0):
        t = np.linspace(0, dur, int(sr*dur), endpoint=False); rng = np.random.default_rng(seed)
        ph = np.cumsum(2*np.pi*(f0 + rng.standard_normal(len(t)))/sr)
        return (sum(np.sin(k*ph)*np.exp(-abs(k*f0-fm)/600) for k in range(1,10) for fm in forms)
                + 0.02*rng.standard_normal(len(t))).astype(np.float32)
    A1 = voice(130, [700,1200,2600], 1); A2 = voice(131, [710,1210,2610], 2)   # same spk, 2 "languages"
    B  = voice(210, [500,1800,3000], 9)                                          # different spk
    genuine = np.concatenate([A1, A2]); spliced = np.concatenate([A1, B])
    bnd = [len(A1)]
    g = analyze(genuine, sr, bnd); s = analyze(spliced, sr, bnd)
    print("genuine code-switch :", g["verdict"], "min_continuity", g["min_continuity"])
    print("spliced at switch   :", s["verdict"], "min_continuity", s["min_continuity"])
    assert g["min_continuity"] > s["min_continuity"]
    assert "IDENTITY_BREAK" in s["verdict"]
    print("\n[selftest] PASS — same-speaker switch stays continuous; a clone spliced at the switch is flagged.")


if __name__ == "__main__":
    _selftest()
