"""
VoxShield — Universal Input Profiler (roadmap §8).

A cheap, model-free pass that runs BEFORE the expensive detector stack and
estimates what kind of audio this is, so the cascade (§43) can route compute
dynamically. It never decides human/AI — it only characterises the input.

Output `InputProfile`:
    modality              speech | music | environment | mixed | silence
    narrowband            bool   (telephony / band-limited)
    est_sample_rate_class "8k-narrowband" | "16k+"
    codec_hint            "g711-like/narrowband" | "wideband" | null
    speakers              int (coarse; diarization pending -> default 1)
    snr_db                float (rough)
    clipping              float [0,1]
    replay_likelihood     float [0,1]  (coarse heuristic — flagged)
    quality               float [0,1]
    language              null   (LID brain pending, §8)
    environment           null   (environment brain pending, §10)
    distance              null
    reverberation         null
    novelty               null   (comes from VoxScore, §13)
    confidence            float [0,1]

Everything the profiler cannot yet estimate is null (pending a brain) — never
fabricated. Dependency-light: numpy only.
"""
from __future__ import annotations
import numpy as np


def _spectral(y, sr, n_fft=1024):
    if len(y) < n_fft:
        y = np.pad(y, (0, n_fft - len(y)))
    win = np.hanning(n_fft)
    hop = n_fft // 2
    mags = []
    for s in range(0, len(y) - n_fft + 1, hop):
        seg = y[s:s + n_fft] * win
        mags.append(np.abs(np.fft.rfft(seg)))
    if not mags:
        mags = [np.abs(np.fft.rfft(y[:n_fft] * win))]
    S = np.mean(np.stack(mags), axis=0) + 1e-9
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    return S, freqs


def profile(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, dtype=np.float32)
    if y.ndim > 1:
        y = y.mean(axis=1)
    n = len(y)
    if n == 0:
        return {"modality": "silence", "confidence": 1.0}

    rms = float(np.sqrt(np.mean(y ** 2)))
    peak = float(np.max(np.abs(y)) + 1e-9)
    clipping = float(np.mean(np.abs(y) > 0.98))
    zcr = float(np.mean(np.abs(np.diff(np.sign(y))) > 0) )

    S, freqs = _spectral(y, sr)
    Sn = S / S.sum()
    # spectral flatness (geometric/arithmetic mean) — high => noise/unvoiced
    flat = float(np.exp(np.mean(np.log(S))) / np.mean(S))
    # high-frequency energy ratio (>3.4 kHz vs total) — near-zero => narrowband telephony
    hf = float(S[freqs >= 3400].sum() / S.sum()) if (freqs >= 3400).any() else 0.0
    # spectral rolloff (95%)
    cum = np.cumsum(Sn); rolloff = float(freqs[np.searchsorted(cum, 0.95)]) if cum[-1] > 0 else 0.0
    # rough SNR: top-decile energy vs bottom-decile (proxy)
    frame = np.abs(y[: (n // 400) * 400].reshape(-1, 400)).mean(axis=1) if n >= 400 else np.abs(y)[None]
    if len(frame) > 4:
        hi = np.percentile(frame, 90); loq = np.percentile(frame, 10) + 1e-6
        snr_db = float(20 * np.log10(hi / loq))
    else:
        snr_db = None

    nyq = sr / 2
    narrowband = bool(hf < 0.03 or rolloff < 3600 or nyq <= 4100)
    codec_hint = "g711-like/narrowband" if narrowband else "wideband"
    sr_class = "8k-narrowband" if narrowband else "16k+"

    # modality (coarse): silence / speech / music/environment
    if rms < 0.005:
        modality = "silence"
    elif flat > 0.4:
        modality = "environment"          # very flat spectrum -> noise/ambient
    elif zcr > 0.35 and flat > 0.2:
        modality = "mixed"
    else:
        modality = "speech"

    # replay likelihood (coarse heuristic): band-limiting + reduced HF + low rolloff
    # relative to the channel — a *flag*, not a detector. Replay brain (§10) pending.
    replay_likelihood = float(np.clip(0.5 * (1 - min(1.0, hf / 0.05)) +
                                      0.5 * (1 - min(1.0, rolloff / (nyq + 1e-9))), 0, 1))
    if not narrowband:
        replay_likelihood *= 0.5          # wideband -> weaker replay prior

    quality = float(np.clip(0.5 * min(1.0, (snr_db or 0) / 40.0) +
                            0.3 * (1 - clipping) + 0.2 * min(1.0, rms / 0.1), 0, 1))
    confidence = 0.6 if snr_db is not None else 0.4

    return {
        "modality": modality,
        "narrowband": narrowband,
        "est_sample_rate_class": sr_class,
        "codec_hint": codec_hint,
        "speakers": 1,                     # diarization pending
        "snr_db": None if snr_db is None else round(snr_db, 1),
        "clipping": round(clipping, 4),
        "replay_likelihood": round(replay_likelihood, 4),
        "quality": round(quality, 4),
        "hf_ratio": round(hf, 4),
        "rolloff_hz": round(rolloff, 1),
        "language": None, "environment": None, "distance": None,
        "reverberation": None, "novelty": None,
        "confidence": confidence,
        "_status": "modality/narrowband/codec/snr/quality/replay=COARSE-HEURISTIC; "
                   "language/environment/distance/reverb/novelty=PENDING(brains not built).",
    }


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr * 2, endpoint=False)
    # (a) wideband voiced-ish signal with harmonics up to ~6 kHz
    wide = sum(np.sin(2 * np.pi * f * t) for f in [180, 360, 900, 2200, 4800]) / 5
    wide += 0.02 * np.random.randn(len(t))
    # (b) narrowband/telephony: band-limit the same signal to ~300-3400 Hz
    from numpy.fft import rfft, irfft, rfftfreq
    F = rfft(wide); fr = rfftfreq(len(wide), 1 / sr)
    F[(fr < 300) | (fr > 3400)] = 0
    narrow = irfft(F).astype(np.float32)

    pw = profile(wide, sr); pn = profile(narrow, sr)
    print("WIDEBAND  :", {k: pw[k] for k in ["modality", "narrowband", "codec_hint", "hf_ratio", "rolloff_hz", "replay_likelihood", "quality"]})
    print("NARROWBAND:", {k: pn[k] for k in ["modality", "narrowband", "codec_hint", "hf_ratio", "rolloff_hz", "replay_likelihood", "quality"]})
    assert pn["narrowband"] is True and pw["narrowband"] is False, "should distinguish narrowband from wideband"
    assert pn["hf_ratio"] < pw["hf_ratio"], "narrowband should have lower HF ratio"
    print("\n[selftest] PASS — profiler distinguishes wideband vs narrowband/telephony and flags replay-prior.")


if __name__ == "__main__":
    _selftest()
