"""
VoxShield — Reverse-Time / Forward-Reverse Asymmetry brain (roadmap §9, P3).

Physical intuition: genuine human speech is produced by an irreversible physical
process (airflow, glottal closure, articulator inertia) — it has a time ARROW.
Attack transients, note onsets, and formant sweeps are asymmetric forward-vs-reversed.
Many vocoders/TTS synthesise frames more time-symmetrically (over-smoothed onsets,
symmetric energy envelopes), so their forward-reverse asymmetry is LOWER than a
real talker's. We quantify that asymmetry and flag suspiciously symmetric audio.

[HYPOTHESIS] — a physically-motivated open-set cue; must be validated + calibrated
on real vs synthetic before any weight in fusion. numpy only, non-breaking.
"""
from __future__ import annotations
import numpy as np


def _envelope(y, sr, hop=0.01):
    w = max(1, int(hop * sr))
    n = len(y) // w
    return np.array([np.sqrt(np.mean(y[i*w:(i+1)*w]**2) + 1e-12) for i in range(n)])


def _attack_decay_ratio(env):
    """humans: sharp attacks, slower decays (glottal). ratio of positive vs negative
    envelope slopes — a directional (time-arrow) statistic."""
    d = np.diff(env)
    up = d[d > 0].sum(); down = -d[d < 0].sum()
    return float(up / (down + 1e-9))


def forward_reverse(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    if len(y) < sr // 2:
        return {"asymmetry": None, "verdict": "TOO_SHORT", "_status": "need >=0.5s"}
    env = _envelope(y, sr); renv = env[::-1]

    # 1) attack/decay directionality differs forward vs reversed for real speech
    adr_f = _attack_decay_ratio(env); adr_r = _attack_decay_ratio(renv)
    adr_asym = abs(adr_f - adr_r) / (adr_f + adr_r + 1e-9)

    # 2) spectral-flux time-asymmetry: onset-heavy (human) vs symmetric (synthetic)
    S = np.abs(np.fft.rfft(np.reshape(y[:len(y)//512*512], (-1, 512)) * np.hanning(512), axis=1))
    flux = np.sqrt(np.maximum(np.diff(S, axis=0), 0).sum(1) + 1e-12)
    rflux = np.sqrt(np.maximum(np.diff(S[::-1], axis=0), 0).sum(1) + 1e-12)
    flux_asym = abs(flux.mean() - rflux.mean()) / (flux.mean() + rflux.mean() + 1e-9)

    asym = float(0.5 * adr_asym + 0.5 * flux_asym)
    # low asymmetry => suspiciously time-reversible => more synthetic-like
    synthetic_lean = float(np.clip(1.0 - asym * 6.0, 0.0, 1.0))
    return {"asymmetry": round(asym, 4), "attack_decay_asym": round(float(adr_asym), 4),
            "flux_asym": round(float(flux_asym), 4), "synthetic_lean": round(synthetic_lean, 3),
            "verdict": "TIME_SYMMETRIC (synthetic-leaning)" if asym < 0.08 else "TIME_ARROW_PRESENT (human-leaning)",
            "_status": "HYPOTHESIS — physical time-arrow cue; calibrate on real vs synthetic before weighting."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False); rng = np.random.default_rng(0)
    # human-like: sharp glottal attacks + slower decay (asymmetric transients)
    pulses = np.zeros_like(t)
    for on in np.arange(0.05, 2.0, 0.11):
        i = int(on*sr); dur = int(0.09*sr)
        seg = np.exp(-np.linspace(0, 5, dur)) * np.sin(2*np.pi*180*np.linspace(0, 0.09, dur))
        pulses[i:i+dur] += seg[:len(pulses[i:i+dur])]
    human = (pulses + 0.01*rng.standard_normal(len(t))).astype(np.float32)
    # synthetic-like: time-symmetric sustained tone (no attack arrow)
    synth = (0.3*np.sin(2*np.pi*180*t) + 0.15*np.sin(2*np.pi*360*t) + 0.005*rng.standard_normal(len(t))).astype(np.float32)
    h = forward_reverse(human, sr); s = forward_reverse(synth, sr)
    print("human :", h["verdict"], "asym", h["asymmetry"], "synth_lean", h["synthetic_lean"])
    print("synth :", s["verdict"], "asym", s["asymmetry"], "synth_lean", s["synthetic_lean"])
    assert h["asymmetry"] > s["asymmetry"]
    assert h["synthetic_lean"] < s["synthetic_lean"]
    print("\n[selftest] PASS — human transients carry a stronger time-arrow; symmetric tone leans synthetic.")


if __name__ == "__main__":
    _selftest()
