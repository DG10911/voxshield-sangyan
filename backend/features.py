"""
VoxShield — acoustic feature extraction (research-backed set).

Produces:
  1) a mel-spectrogram PNG (base64) for the dashboard,
  2) interpretable artifact features (reason codes), and
  3) a fixed-length numeric FEATURE VECTOR (LFCC + CQCC + group-delay +
     prosody + spectral stats) for the trainable fusion head.

Feature families chosen from the anti-spoofing literature:
  - LFCC   : linear-freq cepstral — preserves high-freq vocoder artifacts.
  - CQCC   : constant-Q cepstral — top hand-crafted feature in ASVspoof.
  - Group-delay (phase) : synthesis has unnaturally regular phase.
  - Prosody (F0 jitter/shimmer, voiced ratio) : pitch micro-variation.
  - HF energy / regularity, spectral flatness, silence/breath cues.
"""
from __future__ import annotations
import io, base64
import numpy as np
import librosa

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import librosa.display  # noqa

SR = 16000
N_FFT = 512
HOP = 160          # 10 ms
N_MELS = 128


# ----------------------------------------------------------------------------
def load_audio(raw_bytes: bytes, sr: int = SR) -> tuple[np.ndarray, int]:
    """Decode audio bytes to mono float32 @ sr.
    Tries soundfile/librosa first; falls back to pydub+ffmpeg for compressed
    containers (mp3/m4a/webm). The web UI already sends 16 kHz WAV, so this
    fallback is only for direct API/CLI callers."""
    try:
        y, _ = librosa.load(io.BytesIO(raw_bytes), sr=sr, mono=True)
    except Exception:
        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(io.BytesIO(raw_bytes))
            seg = seg.set_channels(1).set_frame_rate(sr)
            y = np.array(seg.get_array_of_samples(), dtype=np.float32)
            y /= float(1 << (8 * seg.sample_width - 1))
        except Exception as e:
            raise ValueError(
                "Unsupported audio format. Send WAV/FLAC, or install ffmpeg "
                f"for mp3/m4a/webm. ({e})")
    if y.size == 0:
        raise ValueError("Empty or unreadable audio.")
    y, _ = librosa.effects.trim(y, top_db=35)
    if y.size < sr // 2:
        y = np.pad(y, (0, sr // 2 - y.size))
    return y.astype(np.float32), sr


def mel_spectrogram_png(y: np.ndarray, sr: int = SR) -> str:
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=N_FFT, hop_length=HOP,
                                       n_mels=N_MELS, fmax=sr // 2)
    S_db = librosa.power_to_db(S, ref=np.max)
    fig, ax = plt.subplots(figsize=(7.6, 2.0), dpi=110)
    librosa.display.specshow(S_db, sr=sr, hop_length=HOP, x_axis="time",
                             y_axis="mel", fmax=sr // 2, cmap="magma", ax=ax)
    ax.set_facecolor("#06101f"); fig.patch.set_facecolor("#06101f")
    ax.tick_params(colors="#9fc6ff", labelsize=7)
    for sp in ax.spines.values(): sp.set_color("#0d2138")
    ax.set_xlabel(""); ax.set_ylabel("")
    fig.tight_layout(pad=0.4)
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _safe(x, lo=0.0, hi=1.0): return float(max(lo, min(hi, x)))


# ---- cepstral helpers -------------------------------------------------------
def lfcc(y, sr=SR, n_lfcc=20):
    """Linear-frequency cepstral coefficients."""
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP)) ** 2
    n_filt = 40
    fb = np.linspace(0, sr / 2, n_filt + 2)
    bins = np.floor((N_FFT + 1) * fb / sr).astype(int)
    fbank = np.zeros((n_filt, S.shape[0]))
    for m in range(1, n_filt + 1):
        l, c, r = bins[m - 1], bins[m], bins[m + 1]
        for k in range(l, c): fbank[m - 1, k] = (k - l) / max(c - l, 1)
        for k in range(c, r): fbank[m - 1, k] = (r - k) / max(r - c, 1)
    feat = np.log(fbank @ S + 1e-9)
    from scipy.fftpack import dct
    return dct(feat, type=2, axis=0, norm="ortho")[:n_lfcc]


def cqcc(y, sr=SR, n_cqcc=20):
    """Constant-Q cepstral coefficients (CQT magnitude -> log -> DCT)."""
    try:
        C = np.abs(librosa.cqt(y, sr=sr, hop_length=HOP, n_bins=84, bins_per_octave=12))
        from scipy.fftpack import dct
        return dct(np.log(C + 1e-9), type=2, axis=0, norm="ortho")[:n_cqcc]
    except Exception:
        return np.zeros((n_cqcc, 1))


def group_delay_var(y, sr=SR):
    """Variance of the modified group-delay-ish phase derivative.
    Lower variance => more regular phase => more synthetic."""
    D = librosa.stft(y, n_fft=N_FFT, hop_length=HOP)
    phase = np.angle(D)
    gd = np.diff(np.unwrap(phase, axis=0), axis=0)   # group-delay proxy
    return float(np.var(gd))


# ----------------------------------------------------------------------------
def extract_features(y: np.ndarray, sr: int = SR) -> dict:
    """Interpretable reason-code features in [0,1]-ish ranges."""
    stft = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP)) + 1e-9
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)

    hi = freqs >= 6000
    hf_energy_ratio = _safe(stft[hi].sum() / stft.sum())
    hf_band = stft[hi].mean(axis=0); hf_band /= (hf_band.mean() + 1e-9)
    hf_cv = hf_band.std() / (hf_band.mean() + 1e-9)
    hf_regularity = _safe(1.0 - hf_cv / 1.5)

    flatness = float(np.mean(librosa.feature.spectral_flatness(S=stft)))
    spectral_flatness = _safe(flatness * 6.0)

    # phase regularity from group delay (normalise: low var => synthetic)
    gd_var = group_delay_var(y, sr)
    phase_reg = _safe(1.0 - gd_var / 3.0)

    try:
        f0, voiced, _ = librosa.pyin(y, fmin=70, fmax=400, sr=sr,
                                     frame_length=1024, hop_length=HOP)
        f0v = f0[~np.isnan(f0)]
        f0_voiced_ratio = _safe(np.mean(voiced.astype(float))) if voiced is not None else .5
        if f0v.size > 4:
            periods = 1.0 / f0v
            jitter = float(np.mean(np.abs(np.diff(periods))) / (np.mean(periods) + 1e-9))
            amps = np.abs(y); shimmer = float(np.std(amps) / (np.mean(amps) + 1e-9))
        else:
            jitter, shimmer = 0.02, 1.0
    except Exception:
        f0_voiced_ratio, jitter, shimmer = 0.5, 0.02, 1.0

    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=HOP)[0]
    thr = 0.15 * (rms.mean() + 1e-9)
    silence_ratio = _safe(np.mean(rms < thr))
    quiet = rms < thr
    bb = (freqs >= 200) & (freqs <= 2000)
    if quiet.any() and stft.shape[1]:
        be = stft[bb][:, quiet[:stft.shape[1]]].mean() / (stft.mean() + 1e-9)
    else:
        be = 0.0
    breath_score = _safe(silence_ratio * (1.0 - _safe(be * 3.0)))

    return {
        "duration": round(len(y) / sr, 2),
        "sr": sr,
        "narrowband": bool(hf_energy_ratio < 0.02),   # likely 8 kHz / telephony
        "hf_energy_ratio": round(hf_energy_ratio, 4),
        "hf_regularity": round(hf_regularity, 4),
        "spectral_flatness": round(spectral_flatness, 4),
        "phase_reg": round(phase_reg, 4),
        "f0_jitter": round(jitter, 5),
        "shimmer": round(shimmer, 4),
        "f0_voiced_ratio": round(f0_voiced_ratio, 4),
        "silence_ratio": round(silence_ratio, 4),
        "breath_score": round(breath_score, 4),
    }


def feature_vector(y: np.ndarray, sr: int = SR) -> np.ndarray:
    """Fixed-length numeric vector for the trainable fusion head.
    = mean+std of LFCC & CQCC  +  scalar interpretable features."""
    L = lfcc(y, sr); C = cqcc(y, sr)
    stats = np.concatenate([L.mean(1), L.std(1), C.mean(1), C.std(1)])
    f = extract_features(y, sr)
    scal = np.array([f["hf_energy_ratio"], f["hf_regularity"], f["spectral_flatness"],
                     f["phase_reg"], f["f0_jitter"], f["shimmer"], f["f0_voiced_ratio"],
                     f["silence_ratio"], f["breath_score"]], dtype=np.float32)
    v = np.concatenate([stats, scal]).astype(np.float32)
    return np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
