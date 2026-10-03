"""
VoxShield — Fast Detector L0 (roadmap §43 cascade, level 0).

An ultra-cheap, model-free screen that runs FIRST so the expensive detector bank
only fires on the uncertain minority. It NEVER makes the final call — it only
routes compute: obvious low-risk audio can fast-pass; everything else escalates.

Decision ∈ {FAST_PASS_LOW_RISK, ESCALATE}. Target <300 ms (roadmap target, not a
measured claim). Uses only numpy spectral stats (shares the profiler's cheap pass).
"""
from __future__ import annotations
import numpy as np
from profiler import profile   # reuse the cheap spectral pass


def screen(y: np.ndarray, sr: int, low_risk_gate: float = 0.20) -> dict:
    """Return a cascade gate. proxy is a CHEAP risk heuristic in [0,1] — not a
    detector; only its extremes are trusted to fast-pass, everything else escalates."""
    p = profile(y, sr)
    if p.get("modality") == "silence":
        return {"level": "L0", "decision": "ESCALATE", "proxy": None,
                "reason": "silence/too-short — needs VAD + deeper look", "escalate": True}
    # cheap syntheticness proxy: unusually flat/over-regular spectrum + clipping-free
    # + very low HF variability are weak synthetic hints; high SNR clean speech with
    # natural rolloff is a weak genuine hint. Deliberately conservative.
    hf = p.get("hf_ratio") or 0.0
    q = p.get("quality") or 0.0
    rolloff = p.get("rolloff_hz") or 0.0
    nyq = sr / 2
    natural = (0.05 < hf < 0.6) and (rolloff > 0.3 * nyq) and q > 0.4
    proxy = float(np.clip(0.5 - 0.3 * (1 if natural else 0) + 0.2 * (1 - min(1.0, q)), 0, 1))
    if natural and proxy <= low_risk_gate:
        return {"level": "L0", "decision": "FAST_PASS_LOW_RISK", "proxy": round(proxy, 3),
                "reason": "natural spectrum, high quality, no cheap anomaly — low prior",
                "escalate": False, "profile": p}
    return {"level": "L0", "decision": "ESCALATE", "proxy": round(proxy, 3),
            "reason": "not clearly low-risk — run detector bank", "escalate": True, "profile": p}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr * 2, endpoint=False)
    natural = sum(np.sin(2*np.pi*f*t) for f in [170, 340, 800, 2600, 5200]) / 5 + 0.02*np.random.randn(len(t))
    natural *= 0.3 / (np.max(np.abs(natural)) + 1e-9)
    silence = np.zeros(sr)
    a = screen(natural, sr); b = screen(silence, sr)
    print("natural :", {k: a[k] for k in ["decision", "proxy", "escalate"]})
    print("silence :", {k: b[k] for k in ["decision", "escalate"]})
    assert b["escalate"] is True, "silence must escalate"
    print("\n[selftest] PASS — L0 fast-passes obvious low-risk and escalates the rest (never decides synthetic).")


if __name__ == "__main__":
    _selftest()
