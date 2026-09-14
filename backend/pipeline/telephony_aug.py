"""
VoxShield on-the-fly telephony augmentation.

Applied in the dataloader — NO stored copies (raw stays one copy; channel variation
is generated per-sample). Deterministic per (clip_id, epoch) so eval is reproducible
while training stays varied.

Chain (each applied probabilistically): telephony band-pass (300-3400 Hz) →
G.711 mu-law 8 kHz roundtrip → additive noise (SNR 5-30 dB) → packet-loss dropouts →
mild clipping. All operate at 16 kHz mono float32 in/out.

Codec-holdout: pass `holdout_codec="amr"` to NEVER apply that codec during training,
so it can be used as a codec-generalization test.
"""
import numpy as np, torch
import torchaudio, torchaudio.functional as AF

SR, SR_PHONE = 16000, 8000

def _to_t(y): return torch.from_numpy(np.asarray(y, dtype=np.float32))

def g711_mulaw(y):
    t = _to_t(y)
    y8 = AF.resample(t, SR, SR_PHONE)
    q = torchaudio.functional.mu_law_encoding(y8, 256)
    d = torchaudio.functional.mu_law_decoding(q, 256)
    return AF.resample(d, SR_PHONE, SR).numpy().astype(np.float32)

def bandpass(y, low=300., high=3400.):
    t = _to_t(y)
    t = AF.highpass_biquad(t, SR, low)
    t = AF.lowpass_biquad(t, SR, high)
    return t.numpy().astype(np.float32)

def add_noise(y, snr_db):
    p = float(np.mean(y**2)) + 1e-9
    n = np.random.randn(len(y)).astype(np.float32) * np.sqrt(p / (10**(snr_db/10)))
    return (y + n).astype(np.float32)

def packet_loss(y, rate=0.02, frame=160):  # 10ms frames @16k
    y = y.copy()
    for s in range(0, len(y), frame):
        if np.random.random() < rate:
            y[s:s+frame] = 0.0
    return y

def clip_dist(y, thresh=0.95):
    return np.clip(y, -thresh, thresh).astype(np.float32)

def telephony_augment(y, p=0.6, seed=None, holdout_codec=None):
    """Return an augmented copy of y (16k mono float32). p = overall apply prob."""
    if seed is not None:
        np.random.seed(seed % (2**32))
    if np.random.random() >= p:
        return y.astype(np.float32)
    y = bandpass(y)
    if holdout_codec != "g711" and np.random.random() < 0.7:
        y = g711_mulaw(y)
    if np.random.random() < 0.7:
        y = add_noise(y, float(np.random.uniform(5, 30)))
    if np.random.random() < 0.3:
        y = packet_loss(y, rate=float(np.random.uniform(0.005, 0.03)))
    if np.random.random() < 0.2:
        y = clip_dist(y)
    m = float(np.max(np.abs(y))) + 1e-9
    if m > 1.0: y = y / m
    return y.astype(np.float32)

if __name__ == "__main__":
    x = (np.random.randn(48000).astype(np.float32) * 0.1)
    for seed in (1, 2, 3):
        z = telephony_augment(x, p=1.0, seed=seed)
        print(f"seed={seed} in={x.shape} out={z.shape} peak={np.max(np.abs(z)):.3f}")
    # determinism check
    a = telephony_augment(x, p=1.0, seed=7); b = telephony_augment(x, p=1.0, seed=7)
    print("deterministic:", np.allclose(a, b))
