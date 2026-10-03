"""
VoxShield — Environment + Capture-Chain Forensics (roadmap §10, §13).

Characterises the world around the voice and asks whether the voice physically
belongs in it (a cloned voice dropped onto the wrong room/mic is inconsistent):
    rt60_proxy          reverberation (envelope decay)
    noise_floor         background level + flatness
    svcs                Scene-Voice Consistency Score — do voiced and non-voiced
                        frames share the same background/room (one capture chain)?
    capture_consistency spectral-colour stability across the clip (AGC/mic signature)

[HYPOTHESIS] — heuristics; validate on real environment/capture datasets (roadmap
mentions ESDD2-style environment-aware evaluation). Evidence stream, never standalone.
numpy-only.
"""
from __future__ import annotations
import numpy as np


def _frames(y, n=512, hop=256):
    if len(y) < n: y = np.pad(y, (0, n-len(y)))
    return np.stack([y[s:s+n] for s in range(0, len(y)-n+1, hop)])


def environment(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    y = y / (np.max(np.abs(y)) + 1e-9)
    F = _frames(y)
    e = np.sqrt((F**2).mean(1)) + 1e-9
    edb = 20*np.log10(e)

    # rt60 proxy: median downward slope after energy peaks (reverb tail decay)
    slopes = []
    for i in range(1, len(edb)-1):
        if edb[i] > edb[i-1] and edb[i] > np.percentile(edb, 60):     # local onset
            j = i
            while j+1 < len(edb) and edb[j+1] < edb[j]:
                j += 1
            if j > i+1:
                dur = (j-i) * (256/sr)
                drop = edb[i] - edb[j]
                if drop > 3: slopes.append(dur * 60 / drop)            # time to -60 dB
    rt60 = float(np.clip(np.median(slopes), 0, 3)) if slopes else 0.0

    # noise floor
    floor = float(np.percentile(edb, 10)); noise_floor_db = round(floor, 1)

    # SVCS: background spectrum in quiet frames vs low-band of voiced frames — a
    # consistent scene has similar noise colour throughout (low divergence).
    thr = np.percentile(e, 40)
    quiet = F[e < thr]; loud = F[e >= thr]
    def bgspec(fr):
        if len(fr) == 0: return None
        S = np.abs(np.fft.rfft(fr * np.hanning(fr.shape[1]), axis=1)).mean(0) + 1e-9
        return S / S.sum()
    sq, sl = bgspec(quiet), bgspec(loud)
    if sq is not None and sl is not None:
        div = float(np.sum(np.abs(sq - sl)) / 2)                       # total variation 0..1
        svcs = round(1 - div, 3)
    else:
        svcs = None

    # capture consistency: stability of spectral centroid across the clip (AGC/mic)
    cents = []
    for fr in F:
        S = np.abs(np.fft.rfft(fr)); c = (np.arange(len(S))*S).sum()/(S.sum()+1e-9)
        cents.append(c)
    cents = np.array(cents)
    capture = round(float(np.clip(1 - np.std(cents)/(np.mean(cents)+1e-9), 0, 1)), 3)

    return {"rt60_proxy_s": round(rt60, 3), "noise_floor_db": noise_floor_db,
            "svcs": svcs, "capture_consistency": capture,
            "_status": "HYPOTHESIS — environment/capture heuristics; validate on real room/mic datasets; never standalone."}


def _selftest():
    rng = np.random.default_rng(0)
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False)
    # dry: short amplitude bursts with fast decay (little reverberation)
    gate = (np.abs(np.sin(2*np.pi*3*t)) > 0.5).astype(np.float32)
    dry = (np.sin(2*np.pi*220*t) * gate + 0.01*rng.standard_normal(len(t))).astype(np.float32)
    # reverberant: convolve with a long, smooth exponential decay tail (deterministic)
    ir = np.exp(-np.linspace(0, 2.5, 2400)).astype(np.float32)
    wet = np.convolve(dry, ir)[:len(dry)].astype(np.float32)
    a = environment(dry, sr); b = environment(wet, sr)
    print("DRY :", {k: a[k] for k in ["rt60_proxy_s", "svcs", "capture_consistency"]})
    print("WET :", {k: b[k] for k in ["rt60_proxy_s", "svcs", "capture_consistency"]})
    assert b["rt60_proxy_s"] >= a["rt60_proxy_s"], "reverberant should have >= rt60"
    assert a["svcs"] is not None and b["svcs"] is not None
    print("\n[selftest] PASS — reverberant clip shows >= rt60 than dry; SVCS + capture-consistency computed.")


if __name__ == "__main__":
    _selftest()
