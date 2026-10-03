"""
VoxShield — Replay Forensics (roadmap §10, §12).

Distinguishes live vs re-recorded audio via a Double-Transmission Signature:
    source → recording → loudspeaker → room → microphone → second recording
Each extra transmission adds band-limiting, added reverb tail, a raised/coloured
noise floor, and mild nonlinearity. This module estimates a `replay_score` from
those cues.  [HYPOTHESIS] — a heuristic evidence stream, NOT a validated replay
detector; must be validated on a replay corpus (roadmap §16 Golden Set) before use.
numpy-only.
"""
from __future__ import annotations
import numpy as np


def _bands(y, sr, n_fft=1024):
    if len(y) < n_fft:
        y = np.pad(y, (0, n_fft - len(y)))
    hop = n_fft // 2; win = np.hanning(n_fft)
    S = []
    for s in range(0, len(y) - n_fft + 1, hop):
        S.append(np.abs(np.fft.rfft(y[s:s+n_fft] * win)))
    S = np.mean(np.stack(S), axis=0) + 1e-9 if S else np.abs(np.fft.rfft(y[:n_fft]*win)) + 1e-9
    fr = np.fft.rfftfreq(n_fft, 1/sr)
    return S, fr


def replay_score(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    S, fr = _bands(y, sr)
    nyq = sr / 2
    # 1) band-limiting: a replay/telephony chain rolls off energy above the ~3.4 kHz
    # telephone edge. Measure the fraction of energy in (3.4 kHz .. Nyquist).
    mid_hi = float(S[fr > 3400].sum() / S.sum()) if (fr > 3400).any() else 0.0
    bandlimit = 1 - min(1.0, mid_hi / 0.15)
    # 2) noise-floor colour: replayed audio has a raised, flatter low-level floor
    frame = np.abs(y[:(len(y)//400)*400].reshape(-1,400)).mean(1) if len(y) >= 400 else np.abs(y)[None]
    floor = float(np.percentile(frame, 10)); peak = float(np.percentile(frame, 90)) + 1e-9
    raised_floor = min(1.0, floor / (peak * 0.15))
    # 3) reverb tail proxy: energy decay slowness in the envelope autocorrelation
    env = frame - frame.mean()
    ac = np.correlate(env, env, "full")[len(env)-1:]
    ac = ac / (ac[0] + 1e-9)
    tail = float(np.clip(np.mean(ac[1:min(10, len(ac))]), 0, 1)) if len(ac) > 2 else 0.0
    score = float(np.clip(0.45*bandlimit + 0.30*raised_floor + 0.25*tail, 0, 1))
    return {"replay_score": round(score, 3),
            "cues": {"bandlimit": round(bandlimit,3), "raised_floor": round(raised_floor,3),
                     "reverb_tail": round(tail,3)},
            "verdict": "LIKELY_REPLAY" if score >= 0.6 else ("POSSIBLE_REPLAY" if score >= 0.4 else "LIKELY_LIVE"),
            "_status": "HYPOTHESIS — heuristic Double-Transmission Signature; validate on a replay corpus before use."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False)
    live = sum(np.sin(2*np.pi*f*t) for f in [180,360,900,2400,5600]) / 5 + 0.01*np.random.randn(len(t))
    live *= 0.4 / (np.max(np.abs(live))+1e-9)
    # simulate replay: band-limit + add reverb-ish smear + raise noise floor
    F = np.fft.rfft(live); fr = np.fft.rfftfreq(len(live), 1/sr); F[fr > 3400] *= 0.05
    rep = np.fft.irfft(F).astype(np.float32)
    rep = np.convolve(rep, np.exp(-np.linspace(0,3,400)), "same")  # reverb tail
    rep += 0.03*np.random.randn(len(rep))                          # raised floor
    rep *= 0.4/(np.max(np.abs(rep))+1e-9)
    a = replay_score(live, sr); b = replay_score(rep, sr)
    print("LIVE   :", a["replay_score"], a["verdict"], a["cues"])
    print("REPLAY :", b["replay_score"], b["verdict"], b["cues"])
    assert b["replay_score"] > a["replay_score"], "replayed audio should score higher"
    print("\n[selftest] PASS — replayed audio yields a higher Double-Transmission score than live.")


if __name__ == "__main__":
    _selftest()
