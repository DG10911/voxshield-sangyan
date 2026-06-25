"""
VoxShield — data augmentation for robustness (used by training & eval).

Implements the augmentations shown in the literature to close the
lab -> real-world generalization gap:

  - RawBoost  : convolutive + impulsive + stationary noise (Tak et al. 2022).
  - Codec / telephony : 8 kHz narrowband downsample + mu-law (G.711-style)
                        round-trip, which strips high-freq artifacts.
  - Waveform  : additive Gaussian noise, pitch shift, time stretch.

All functions take/return float32 mono at the given sample rate.
"""
from __future__ import annotations
import numpy as np
import librosa

SR = 16000


def _norm(y):
    m = np.max(np.abs(y)) + 1e-9
    return (y / m).astype(np.float32)


# ---- RawBoost components ----------------------------------------------------
def convolutive_noise(y, sr=SR, n_taps=8, gain_db=(-6, 6)):
    """Random linear FIR filtering (channel/mic colouration)."""
    taps = np.random.uniform(-1, 1, n_taps)
    taps[0] = 1.0
    g = 10 ** (np.random.uniform(*gain_db) / 20.0)
    out = np.convolve(y, taps, mode="same") * g
    return _norm(out)


def impulsive_noise(y, p=0.0008, amp=0.5):
    """Signal-dependent impulsive clicks."""
    out = y.copy()
    idx = np.random.rand(len(y)) < p
    out[idx] += amp * np.sign(np.random.randn(idx.sum())) * (np.abs(out[idx]) + 0.05)
    return _norm(out)


def stationary_noise(y, snr_db=(10, 25)):
    """Additive white noise at a random SNR."""
    snr = np.random.uniform(*snr_db)
    p_sig = np.mean(y ** 2) + 1e-9
    p_noise = p_sig / (10 ** (snr / 10))
    return _norm(y + np.sqrt(p_noise) * np.random.randn(len(y)))


def rawboost(y, sr=SR):
    """RawBoost = chain of the three noise types (random subset)."""
    fns = [convolutive_noise, impulsive_noise, stationary_noise]
    np.random.shuffle(fns)
    out = y
    for fn in fns:
        if np.random.rand() < 0.7:
            out = fn(out) if fn is not convolutive_noise else fn(out, sr)
    return out.astype(np.float32)


# ---- Codec / telephony ------------------------------------------------------
def mu_law_roundtrip(y, mu=255):
    """G.711 mu-law companding round trip (8-bit quantisation)."""
    y = np.clip(y, -1, 1)
    comp = np.sign(y) * np.log1p(mu * np.abs(y)) / np.log1p(mu)
    q = np.round((comp + 1) / 2 * 255) / 255 * 2 - 1
    expd = np.sign(q) * (1 / mu) * ((1 + mu) ** np.abs(q) - 1)
    return expd.astype(np.float32)


def codec_8k(y, sr=SR):
    """Simulate a narrowband phone line: 16k -> 8k -> mu-law -> back to 16k."""
    y8 = librosa.resample(y, orig_sr=sr, target_sr=8000)
    y8 = mu_law_roundtrip(y8)
    y16 = librosa.resample(y8, orig_sr=8000, target_sr=sr)
    # match length
    if len(y16) < len(y): y16 = np.pad(y16, (0, len(y) - len(y16)))
    return _norm(y16[:len(y)])


# ---- Waveform ---------------------------------------------------------------
def pitch_shift(y, sr=SR, steps=(-2, 2)):
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=np.random.uniform(*steps)).astype(np.float32)


def time_stretch(y, rate=(0.9, 1.1)):
    try:
        return librosa.effects.time_stretch(y, rate=np.random.uniform(*rate)).astype(np.float32)
    except Exception:
        return y


AUGMENTERS = {
    "rawboost": rawboost,
    "codec_8k": codec_8k,
    "noise": stationary_noise,
    "pitch": pitch_shift,
    "stretch": time_stretch,
}


def augment(y, sr=SR, which=None, p=0.5):
    """Apply a random subset of augmentations (or a named list)."""
    out = y.astype(np.float32)
    names = which if which is not None else list(AUGMENTERS)
    for n in names:
        if which is not None or np.random.rand() < p:
            fn = AUGMENTERS[n]
            try:
                out = fn(out, sr) if n in ("rawboost", "codec_8k", "noise", "pitch") else fn(out)
            except Exception:
                pass
    return out.astype(np.float32)
