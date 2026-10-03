"""
VoxShield — Scenario Renderer (roadmap §25 local half, §6–7, §23; P3).

The VoiceStudio lab flow is:
    VoiceStudio(gen) → Generator Adapter → Attack Recipe → **Scenario Renderer →
    Codec/Telephony Sim → Replay/Env Sim** → VoxShield → Benchmark

The AI-generation backend (VoiceStudio) needs external models and stays PARKED, but
the *rendering* half — turning one clean clip into the many channel/replay/environment
scenarios of the Attack Recipe / Device-Environment-Distance matrices — is pure DSP
and is built here. This lets us synthesise the Nightmare/Worst-* scenario conditions
(§16, §32) from any input, deterministically, with no external dependency.

Renders per Attack Recipe dims: codec (G.711 μ/A-law, narrowband, Opus-ish decimate),
telephony band-limit, packet loss / jitter, additive noise (SNR), reverb (rt60),
distance attenuation, replay (double-transmission), speakerphone. numpy only.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional


def _rng(seed): return np.random.default_rng(seed)


# ---- codec / channel ----
def mulaw(y, mu=255.0):
    c = np.sign(y) * np.log1p(mu*np.abs(y)) / np.log1p(mu); q = np.round(c*128)/128.0
    return (np.sign(q) * (1/mu) * ((1+mu)**np.abs(q) - 1)).astype(np.float32)

def alaw(y, A=87.6):
    a = np.abs(y); s = np.sign(y)
    c = np.where(a < 1/A, A*a/(1+np.log(A)), (1+np.log(A*np.clip(a,1e-9,None)))/(1+np.log(A)))
    q = np.round(s*c*128)/128.0
    return (s * np.abs(q)).astype(np.float32)  # coarse round-trip proxy

def bandlimit(y, sr, lo=300, hi=3400):
    Y = np.fft.rfft(y); f = np.fft.rfftfreq(len(y), 1/sr)
    Y[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(Y, n=len(y)).astype(np.float32)

def decimate_resample(y, sr, target=8000):
    n = int(len(y)*target/sr); ys = np.interp(np.linspace(0, len(y)-1, n), np.arange(len(y)), y)
    return np.interp(np.linspace(0, n-1, len(y)), np.arange(n), ys).astype(np.float32)

def packet_loss(y, sr, rate=0.02, ms=20, seed=0):
    w = int(ms*sr/1000); out = y.copy(); r = _rng(seed)
    for s in range(0, len(y)-w, w):
        if r.random() < rate: out[s:s+w] = 0.0
    return out.astype(np.float32)


# ---- environment / replay ----
def add_noise(y, snr_db, seed=0):
    p = np.mean(y**2)+1e-12; n = np.sqrt(p/(10**(snr_db/10.0)))
    return (y + n*_rng(seed).standard_normal(len(y))).astype(np.float32)

def reverb(y, sr, rt60=0.4, seed=0):
    L = int(rt60*sr); t = np.arange(L)
    ir = _rng(seed).standard_normal(L) * np.exp(-6.9*t/max(L,1)); ir[0] = 1.0
    return np.convolve(y, ir)[:len(y)].astype(np.float32)

def distance_atten(y, meters=1.0):
    return (y / max(meters, 0.05)).astype(np.float32)

def replay_double_transmission(y, sr, seed=0):
    """simulate playback+recapture: bandlimit + speaker/mic coloration + reverb + noise."""
    z = bandlimit(y, sr, 250, 3600); z = reverb(z, sr, 0.25, seed)
    z = z * (1 + 0.15*np.sin(2*np.pi*np.arange(len(z))/sr*50))  # cheap speaker resonance
    return add_noise(z, 28, seed).astype(np.float32)


_CODEC = {"g711_ulaw": lambda y, sr: mulaw(y), "g711_alaw": lambda y, sr: alaw(y),
          "narrowband": lambda y, sr: bandlimit(y, sr), "opus_8k": lambda y, sr: decimate_resample(y, sr)}


def render(y: np.ndarray, sr: int, scenario: Dict) -> Dict:
    """Apply an ordered scenario spec. Keys (all optional):
    codec, narrowband(bool), snr_db, rt60, distance_m, packet_loss, replay(bool), seed."""
    y = np.asarray(y, np.float32); seed = scenario.get("seed", 0); steps = []
    if scenario.get("codec") in _CODEC:
        y = _CODEC[scenario["codec"]](y, sr); steps.append(scenario["codec"])
    if scenario.get("band"):                       # explicit [lo,hi] band-limit (e.g. G.722 ≈ 50–7000 Hz)
        lo, hi = scenario["band"]; y = bandlimit(y, sr, lo, hi); steps.append(f"band@{lo}-{hi}")
    if scenario.get("narrowband"):
        y = bandlimit(y, sr); steps.append("bandlimit")
    if scenario.get("rt60"):
        y = reverb(y, sr, scenario["rt60"], seed); steps.append(f"reverb@{scenario['rt60']}")
    if scenario.get("distance_m"):
        y = distance_atten(y, scenario["distance_m"]); steps.append(f"dist@{scenario['distance_m']}m")
    if scenario.get("packet_loss"):
        y = packet_loss(y, sr, scenario["packet_loss"], seed=seed); steps.append(f"loss@{scenario['packet_loss']}")
    if scenario.get("snr_db") is not None:
        y = add_noise(y, scenario["snr_db"], seed); steps.append(f"noise@{scenario['snr_db']}dB")
    if scenario.get("replay"):
        y = replay_double_transmission(y, sr, seed); steps.append("replay")
    return {"audio": y.astype(np.float32), "steps": steps, "scenario": scenario}


def nightmare_scenario(seed=0) -> Dict:
    """The §32 combinatorial worst-case channel (generator-agnostic rendering part)."""
    return {"codec": "g711_ulaw", "narrowband": True, "rt60": 0.6, "distance_m": 2.0,
            "packet_loss": 0.05, "snr_db": 10, "replay": True, "seed": seed}


def matrix(y, sr, codecs=None, snrs=None) -> List[Dict]:
    """Render a small Device/Channel matrix cell-set for benchmarking (§22–23)."""
    codecs = codecs or ["g711_ulaw", "narrowband", "opus_8k"]; snrs = snrs or [30, 15]
    return [{"cell": f"{c}|snr{s}", **render(y, sr, {"codec": c, "snr_db": s})}
            for c in codecs for s in snrs]


def _selftest():
    sr = 16000; t = np.linspace(0, 1, sr, endpoint=False)
    y = (0.4*np.sin(2*np.pi*220*t) + 0.2*np.sin(2*np.pi*6000*t)).astype(np.float32)  # 6kHz is above telephony band

    def hf_energy(sig):  # energy above 3400 Hz (killed by telephony band-limit)
        S = np.abs(np.fft.rfft(sig)); f = np.fft.rfftfreq(len(sig), 1/sr)
        return float(S[f > 3400].sum())

    nb = render(y, sr, {"narrowband": True})
    print("narrowband steps:", nb["steps"], "| HF energy", round(hf_energy(nb["audio"]), 1), "vs orig", round(hf_energy(y), 1))
    assert hf_energy(nb["audio"]) < hf_energy(y) * 0.2       # band-limit removed highs

    nm = render(y, sr, nightmare_scenario())
    print("nightmare steps :", nm["steps"])
    assert len(nm["steps"]) >= 6 and np.isfinite(nm["audio"]).all()

    rep = render(y, sr, {"replay": True})
    assert "replay" in rep["steps"] and len(rep["audio"]) == len(y)

    cells = matrix(y, sr)
    print("matrix cells    :", [c["cell"] for c in cells])
    assert len(cells) == 6 and all(np.isfinite(c["audio"]).all() for c in cells)

    # determinism (seeded)
    a = render(y, sr, nightmare_scenario(7))["audio"]; b = render(y, sr, nightmare_scenario(7))["audio"]
    assert np.allclose(a, b)
    print("\n[selftest] PASS — codec/telephony/replay/env rendering works; nightmare + matrix deterministic.")


if __name__ == "__main__":
    _selftest()
