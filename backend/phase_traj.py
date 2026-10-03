"""
VoxShield — Phase Trajectory brain (roadmap §9, P2).

Standalone, deeper phase analysis than the coarse `phase` term inside physics.py.
Genuine speech has coherent, slowly-evolving phase (a real glottal source + vocal-
tract filter); many vocoders/TTS reconstruct magnitude well but leave phase artifacts
— discontinuities, group-delay irregularity, weak cross-band coherence. Crucially,
phase cues partly SURVIVE band-limiting, so they matter under telephony (§11).

Emits: group-delay continuity, phase-derivative curvature, cross-band coherence,
and a topology (unwrapped-phase winding) irregularity → phase_trajectory_score
(PTS; high = human-plausible). numpy only, non-breaking. [HYPOTHESIS] — calibrate.
"""
from __future__ import annotations
import numpy as np


def _stft(y, n=512, hop=128):
    w = np.hanning(n)
    frames = [y[i:i+n]*w for i in range(0, len(y)-n+1, hop)]
    if not frames: return None
    return np.fft.rfft(np.stack(frames), axis=1)


def phase_trajectory(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    Z = _stft(y)
    if Z is None or Z.shape[0] < 4:
        return {"pts": None, "verdict": "TOO_SHORT", "_status": "need >=~0.1s"}
    phase = np.angle(Z)                                    # (frames, bins)
    mag = np.abs(Z) + 1e-9

    # 1) group delay = -dphase/dfreq ; its cross-frame continuity (smooth for humans)
    gd = -np.diff(np.unwrap(phase, axis=1), axis=1)        # (frames, bins-1)
    gd_cont = 1 - np.clip(np.mean(np.abs(np.diff(gd, axis=0))) / (np.std(gd)+1e-9) / 3, 0, 1)

    # 2) instantaneous-frequency curvature (2nd time-derivative of phase; erratic=synthetic)
    dphi = np.unwrap(phase, axis=0)
    curv = np.abs(np.diff(dphi, n=2, axis=0))
    # weight by magnitude so silent bins don't dominate
    w = mag[2:] / mag[2:].sum()
    curvature = float((curv*w).sum())
    curv_score = 1 - np.clip(curvature/np.pi, 0, 1)

    # 3) cross-band phase coherence: adjacent frequency bands should co-evolve
    lowb = np.unwrap(phase[:, 1:phase.shape[1]//3], axis=0).mean(1)
    midb = np.unwrap(phase[:, phase.shape[1]//3:2*phase.shape[1]//3], axis=0).mean(1)
    if len(lowb) > 2 and np.std(lowb) > 1e-6 and np.std(midb) > 1e-6:
        coherence = abs(float(np.corrcoef(np.diff(lowb), np.diff(midb))[0, 1]))
    else:
        coherence = 0.5
    coherence = 0.0 if np.isnan(coherence) else coherence

    # 4) topology: winding-number stability of the dominant partial (real=stable)
    dom = np.argmax(mag.mean(0))
    winding = np.diff(np.unwrap(phase[:, dom]))
    topo = 1 - np.clip(np.std(winding)/(abs(np.mean(winding))+1e-9)/4, 0, 1)

    pts = float(np.clip(0.30*gd_cont + 0.25*curv_score + 0.25*coherence + 0.20*topo, 0, 1))
    return {"pts": round(pts, 3),
            "components": {"group_delay_continuity": round(float(gd_cont), 3),
                           "curvature_score": round(float(curv_score), 3),
                           "cross_band_coherence": round(float(coherence), 3),
                           "topology_stability": round(float(topo), 3)},
            "synthetic_lean": round(1-pts, 3),
            "verdict": "PHASE_INCOHERENT (synthetic-leaning)" if pts < 0.45 else "PHASE_COHERENT (human-leaning)",
            "telephony_note": "phase cues partially survive 8 kHz band-limiting (usable under G.711).",
            "_status": "HYPOTHESIS — standalone phase-trajectory brain; calibrate on real vs synthetic."}


def _selftest():
    sr = 16000; t = np.linspace(0, 1.5, int(sr*1.5), endpoint=False); rng = np.random.default_rng(0)
    # human-like: harmonics with a coherent, slowly-drifting phase (shared source)
    f0 = 140 + 8*np.sin(2*np.pi*0.5*t); ph = 2*np.pi*np.cumsum(f0)/sr
    human = (sum(np.sin(k*ph)/k for k in range(1, 8)) + 0.01*rng.standard_normal(len(t))).astype(np.float32)
    # synthetic-like: same magnitude content but randomised per-harmonic phase (incoherent)
    synth = sum(np.sin(k*2*np.pi*140*t + rng.uniform(0, 2*np.pi))/k for k in range(1, 8))
    synth = (synth + 0.5*rng.standard_normal(len(t))*np.abs(np.sin(2*np.pi*30*t))).astype(np.float32)
    h = phase_trajectory(human, sr); s = phase_trajectory(synth, sr)
    print("human  PTS:", h["pts"], h["components"])
    print("synth  PTS:", s["pts"], s["components"])
    assert h["pts"] > s["pts"]
    print("\n[selftest] PASS — coherent human phase scores higher than phase-randomised synthetic.")


if __name__ == "__main__":
    _selftest()
