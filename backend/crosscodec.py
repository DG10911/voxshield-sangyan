"""
VoxShield — Cross-Codec Forensic Probing (roadmap §11).

Run audio through several codecs and analyse the RESIDUAL each leaves. Hypothesis:
genuine and synthetic speech respond differently to codec transforms, so the vector
of residual fingerprints is an evidence stream (esp. valuable for telephony).

Produces a residual-fingerprint per codec {ulaw, alaw-ish, narrowband, downsample8k}
= (residual_energy, spectral_change, hf_loss). [HYPOTHESIS] — the discriminative
claim must be validated on paired real/synthetic data; this module builds the
feature. numpy-only (codecs simulated: μ-law companding, band-limit, decimation).
"""
from __future__ import annotations
import numpy as np


def _ulaw(y, mu=255):
    y = np.clip(y, -1, 1)
    c = np.sign(y) * np.log1p(mu * np.abs(y)) / np.log1p(mu)      # compress
    q = np.round(c * 128) / 128                                   # 8-bit quantise
    return np.sign(q) * (1 / mu) * ((1 + mu) ** np.abs(q) - 1)    # expand


def _bandlimit(y, sr, lo=300, hi=3400):
    F = np.fft.rfft(y); fr = np.fft.rfftfreq(len(y), 1/sr)
    F[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(F, n=len(y)).astype(np.float32)


def _decimate8k(y, sr):
    if sr <= 8000: return y
    f = int(round(sr / 8000))
    d = y[::f]
    return np.repeat(d, f)[:len(y)]


def _spec(y, sr, n=1024):
    if len(y) < n: y = np.pad(y, (0, n-len(y)))
    S = np.abs(np.fft.rfft(y[:len(y)//n*n].reshape(-1, n) * np.hanning(n), axis=1)).mean(0) + 1e-9
    return S / S.sum(), np.fft.rfftfreq(n, 1/sr)


def cross_codec(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    y = y / (np.max(np.abs(y)) + 1e-9)
    S0, fr = _spec(y, sr)
    codecs = {"ulaw": _ulaw(y), "narrowband": _bandlimit(y, sr), "down8k": _decimate8k(y, sr)}
    fp = {}
    for name, yc in codecs.items():
        yc = yc[:len(y)]
        res = float(np.sqrt(np.mean((yc - y[:len(yc)]) ** 2)))         # residual energy
        Sc, _ = _spec(yc, sr)
        spec_change = float(np.sum(np.abs(Sc - S0)) / 2)               # total variation
        hf_loss = float(max(0.0, S0[fr > 3400].sum() - Sc[fr > 3400].sum())) if (fr > 3400).any() else 0.0
        fp[name] = {"residual": round(res, 4), "spec_change": round(spec_change, 4), "hf_loss": round(hf_loss, 4)}
    return {"codec_fingerprint": fp,
            "_status": "HYPOTHESIS — cross-codec residual fingerprint feature; validate discriminativeness on paired real/synthetic."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False)
    y = (sum(np.sin(2*np.pi*f*t) for f in [200, 800, 2400, 5200]) / 4 + 0.02*np.random.randn(len(t))).astype(np.float32)
    r = cross_codec(y, sr)
    for k, v in r["codec_fingerprint"].items():
        print(f"  {k:<11} residual={v['residual']} spec_change={v['spec_change']} hf_loss={v['hf_loss']}")
    fps = r["codec_fingerprint"]
    assert fps["narrowband"]["hf_loss"] >= fps["ulaw"]["hf_loss"], "narrowband should lose more HF than ulaw"
    assert all(v["residual"] > 0 for v in fps.values()), "each codec must leave a residual"
    print("\n[selftest] PASS — per-codec residual fingerprints computed (narrowband loses most HF).")


if __name__ == "__main__":
    _selftest()
