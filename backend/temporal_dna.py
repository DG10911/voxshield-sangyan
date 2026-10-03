"""
VoxShield — Temporal Voice DNA (roadmap §9, P3).

A clip's "DNA" = its trajectory of instability over time: how pitch, energy, and
spectral shape wander, where transitions/boundaries sit, and whether the STATISTICS
of that wander stay self-consistent. Two uses:
  1) micro-instability signature — real speakers drift/jitter continuously; many
     synths are locally too stable then jump at frame/chunk boundaries.
  2) generation-boundary hints — abrupt regime changes in the DNA track (a splice,
     a chunk seam, or a speaker/generator change) show up as boundary spikes.

Complements segment.py (which localises partial deepfakes). [HYPOTHESIS] — descriptive
trajectory features; validate + calibrate before weighting. numpy only, non-breaking.
"""
from __future__ import annotations
import numpy as np


def _frames(y, sr, win=0.025, hop=0.010):
    w = int(win*sr); h = int(hop*sr)
    if len(y) < w: return np.empty((0, w))
    idx = range(0, len(y)-w+1, h)
    return np.stack([y[i:i+w]*np.hanning(w) for i in idx])


def _track(y, sr):
    F = _frames(y, sr)
    if len(F) == 0: return None
    S = np.abs(np.fft.rfft(F, axis=1))
    energy = np.sqrt((F**2).mean(1) + 1e-12)
    centroid = (np.arange(S.shape[1]) * S).sum(1) / (S.sum(1) + 1e-9)
    # crude f0 proxy: peak in 80-400Hz band
    lo, hi = int(80*S.shape[1]*2/sr), int(400*S.shape[1]*2/sr)
    f0 = lo + np.argmax(S[:, lo:hi+1], axis=1)
    return {"energy": energy, "centroid": centroid, "f0": f0.astype(np.float32)}


def temporal_dna(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    tr = _track(y, sr)
    if tr is None or len(tr["energy"]) < 8:
        return {"verdict": "TOO_SHORT", "_status": "need >=~0.2s"}

    def micro(x):  # frame-to-frame relative wander (instability)
        x = np.asarray(x, np.float32); d = np.abs(np.diff(x))
        return float(d.mean() / (np.abs(x).mean() + 1e-9))
    inst = {k: micro(v) for k, v in tr.items()}
    instability = float(np.mean(list(inst.values())))

    # boundary track: combined z-scored jump magnitude across the three tracks
    def jumps(x):
        d = np.abs(np.diff(x.astype(np.float32)))
        return (d - d.mean()) / (d.std() + 1e-9)
    jz = jumps(tr["centroid"]) + jumps(tr["energy"]) + jumps(tr["f0"])
    boundaries = [int(i) for i in np.where(jz > 4.0)[0]]  # sharp multi-track seams

    # synthetic-lean: unusually LOW micro-instability but SHARP boundaries (chunk seams)
    low_inst = instability < 0.02
    seamy = len(boundaries) > 0 and instability < 0.04
    synthetic_lean = float(np.clip((0.02 - instability) * 25 + 0.4*seamy, 0, 1))
    return {"instability": round(instability, 4), "per_track": {k: round(v, 4) for k, v in inst.items()},
            "boundaries": boundaries, "n_boundaries": len(boundaries),
            "synthetic_lean": round(synthetic_lean, 3),
            "verdict": ("TOO_STABLE (synthetic-leaning)" if low_inst else
                        "SEAMED_TRAJECTORY (possible splice/chunk)" if seamy else
                        "NATURAL_DRIFT (human-leaning)"),
            "_status": "HYPOTHESIS — trajectory/boundary descriptors; calibrate before weighting; pairs with segment.py."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False); rng = np.random.default_rng(1)
    # human: continuously drifting f0 + energy (natural micro-instability)
    f0 = 150 + 12*np.sin(2*np.pi*0.7*t) + 3*rng.standard_normal(len(t)).cumsum()/np.sqrt(len(t))
    human = (np.sin(2*np.pi*np.cumsum(f0)/sr) * (0.5+0.3*np.abs(np.sin(2*np.pi*3*t)))
             + 0.01*rng.standard_normal(len(t))).astype(np.float32)
    # synthetic-with-seam: two too-stable tones spliced (a chunk boundary)
    a = 0.4*np.sin(2*np.pi*150*t[:sr]); b = 0.4*np.sin(2*np.pi*156*t[:sr])
    seam = np.concatenate([a, b]).astype(np.float32) + 0.002*rng.standard_normal(2*sr).astype(np.float32)
    h = temporal_dna(human, sr); s = temporal_dna(seam, sr)
    print("human :", h["verdict"], "instability", h["instability"], "bounds", h["n_boundaries"])
    print("seam  :", s["verdict"], "instability", s["instability"], "bounds", s["n_boundaries"])
    assert h["instability"] > s["instability"]
    assert h["synthetic_lean"] < s["synthetic_lean"]
    print("\n[selftest] PASS — human shows natural drift; the spliced too-stable tone is flagged.")


if __name__ == "__main__":
    _selftest()
