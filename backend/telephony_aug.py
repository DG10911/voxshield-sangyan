import numpy as np
import torch
import torchaudio
import torchaudio.functional as AF

SR_IN = 16000
SR_PHONE = 8000

def g711_mulaw_roundtrip(y):
    y_t = torch.from_numpy(y.astype(np.float32))
    y8 = AF.resample(y_t, SR_IN, SR_PHONE)
    q = torchaudio.functional.mu_law_encoding(y8, quantization_channels=256)
    y8_hat = torchaudio.functional.mu_law_decoding(q, quantization_channels=256)
    y_up = AF.resample(y8_hat, SR_PHONE, SR_IN)
    return y_up.numpy().astype(np.float32)

def telephony_bandpass(y_np, sr=SR_IN, low=300.0, high=3400.0):
    y_t = torch.from_numpy(y_np.astype(np.float32))
    y_t = AF.highpass_biquad(y_t, sr, cutoff_freq=low)
    y_t = AF.lowpass_biquad(y_t, sr, cutoff_freq=high)
    return y_t.numpy().astype(np.float32)

def add_noise(y, snr_db):
    p = np.mean(y ** 2) + 1e-9
    n_p = p / (10 ** (snr_db / 10.0))
    n = np.random.randn(len(y)).astype(np.float32) * np.sqrt(n_p)
    return (y + n).astype(np.float32)

def telephony_augment(y, p=0.5, snr_db_range=(15, 30)):
    if np.random.random() >= p:
        return y
    y = telephony_bandpass(y)
    y = g711_mulaw_roundtrip(y)
    snr = float(np.random.uniform(*snr_db_range))
    y = add_noise(y, snr)
    m = np.max(np.abs(y)) + 1e-9
    if m > 1.0:
        y = y / m
    return y.astype(np.float32)

if __name__ == "__main__":
    x = np.random.randn(48000).astype(np.float32) * 0.1
    y = telephony_augment(x, p=1.0)
    print("in:", x.shape, x.dtype, "out:", y.shape, y.dtype,
          "peak_in:", np.max(np.abs(x)), "peak_out:", np.max(np.abs(y)))
