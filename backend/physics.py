"""
VoxShield — Human Physics Engine v1 (roadmap §9).

Asks: "could a living human, through this capture chain, have produced this exact
sequence?" Instead of "does it resemble known fakes?", it measures physical
plausibility from four evidence families and fuses them into HPCS (Human Physical
Consistency Score, high = physically human-plausible):

    glottal      — source periodicity / jitter-shimmer NATURALNESS (synthetic
                   speech is often *too* regular OR unnaturally irregular)
    breath       — presence of low-energy inter-phrase breath-like gaps
    microvar     — temporal ENTROPY of F0/energy micro-fluctuation (humans carry
                   rich, non-repeating micro-variation; some generators under-vary)
    phase        — group-delay trajectory smoothness/coherence

[HYPOTHESIS] — every score here is a research heuristic and MUST be validated on a
real human-vs-synthetic corpus (and against strong baselines) before any claim.
None is a standalone detector; they are evidence streams for the arbitration brain.
numpy-only.
"""
from __future__ import annotations
import numpy as np


def _frame(y, n=512, hop=256):
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    return np.stack([y[s:s+n] for s in range(0, len(y)-n+1, hop)])


def _f0_track(y, sr, n=1024, hop=256, fmin=70, fmax=400):
    """cheap autocorrelation F0 per frame (0 = unvoiced)."""
    f0 = []
    lo, hi = int(sr/fmax), int(sr/fmin)
    for s in range(0, max(1, len(y)-n+1), hop):
        seg = y[s:s+n] * np.hanning(n)
        ac = np.correlate(seg, seg, "full")[n-1:]
        if ac[0] <= 1e-8:
            f0.append(0.0); continue
        region = ac[lo:hi]
        if len(region) < 2:
            f0.append(0.0); continue
        k = int(np.argmax(region)) + lo
        f0.append(sr / k if ac[k] > 0.3 * ac[0] else 0.0)
    return np.array(f0)


def human_physics(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    y = y / (np.max(np.abs(y)) + 1e-9)
    F = _frame(y)
    energy = np.sqrt((F ** 2).mean(axis=1)) + 1e-9

    # --- breath: fraction of quiet inter-phrase gaps between voiced regions ---
    thr = 0.15 * energy.max()
    quiet = energy < thr
    # runs of quiet flanked by speech = breath-like pauses
    gaps = 0; inrun = False
    for q in quiet:
        if q and not inrun: gaps += 1; inrun = True
        if not q: inrun = False
    breath = float(np.clip(gaps / max(1, len(energy) / 40), 0, 1))

    # --- glottal naturalness: jitter/shimmer should be small but NONZERO ---
    f0 = _f0_track(y, sr); vf0 = f0[f0 > 0]
    if len(vf0) > 3:
        jit = np.mean(np.abs(np.diff(vf0))) / (np.mean(vf0) + 1e-9)     # rel jitter
        # natural window ~0.003..0.03; too small = synthetic-regular, too big = noise
        glottal = float(np.exp(-((np.log((jit + 1e-4) / 0.012)) ** 2) / 2.0))
    else:
        glottal = 0.3

    # --- microvariation entropy of energy micro-fluctuation ---
    de = np.diff(energy)
    hist, _ = np.histogram(de, bins=16, density=True); hist = hist + 1e-9
    ent = -np.sum(hist * np.log(hist)) / np.log(16)
    microvar = float(np.clip(ent, 0, 1))

    # --- phase-trajectory smoothness (group-delay coherence proxy) ---
    n = 512
    gd = []
    for s in range(0, max(1, len(y)-n+1), n):
        seg = y[s:s+n] * np.hanning(n)
        ph = np.unwrap(np.angle(np.fft.rfft(seg)))
        gd.append(np.mean(np.abs(np.diff(ph, 2))))     # curvature
    gd = np.array(gd) + 1e-9
    phase = float(np.clip(1 - min(1.0, np.std(gd) / (np.mean(gd) + 1e-9) / 3), 0, 1))

    hpcs = float(np.clip(0.30*glottal + 0.20*breath + 0.30*microvar + 0.20*phase, 0, 1))
    return {"hpcs": round(hpcs, 3),
            "components": {"glottal": round(glottal,3), "breath": round(breath,3),
                           "microvar": round(microvar,3), "phase": round(phase,3)},
            "plausibility": "HUMAN_PLAUSIBLE" if hpcs >= 0.55 else ("UNCERTAIN" if hpcs >= 0.4 else "PHYSICALLY_ANOMALOUS"),
            "_status": "HYPOTHESIS — 4 physical-consistency heuristics; validate on human-vs-synthetic corpus; never standalone."}


def _selftest():
    sr = 16000; t = np.linspace(0, 3, sr*3, endpoint=False)
    # NATURAL-ish: F0 with micro-jitter/vibrato, breath gaps, noise, harmonics
    f0 = 140 + 4*np.sin(2*np.pi*5*t) + np.random.randn(len(t))*1.5
    ph = np.cumsum(2*np.pi*f0/sr)
    nat = sum(np.sin(k*ph)/(k) for k in [1,2,3,4]) + 0.03*np.random.randn(len(t))
    env = np.ones_like(t)
    for c in [0.7, 1.6, 2.4]:                          # insert breath gaps
        env[(t > c) & (t < c+0.12)] = 0.05
    nat = (nat * env).astype(np.float32)
    # SYNTHETIC-ish: perfectly regular F0, no breath, low micro-variation, clean
    syn = np.sin(2*np.pi*140*t) + 0.5*np.sin(2*np.pi*280*t)
    syn = syn.astype(np.float32)
    a = human_physics(nat, sr); b = human_physics(syn, sr)
    print("NATURAL-ish :", a["hpcs"], a["plausibility"], a["components"])
    print("SYNTH-ish   :", b["hpcs"], b["plausibility"], b["components"])
    assert a["hpcs"] > b["hpcs"], "natural-ish should have higher HPCS than over-regular synthetic-ish"
    print("\n[selftest] PASS — HPCS higher for natural-ish (breath+micro-variation) than over-regular synthetic-ish.")


if __name__ == "__main__":
    _selftest()
