"""
VoxShield — Causal-Perturbation & Counterfactual Authenticity probing (roadmap §9, P3).

Two governed, model-agnostic diagnostics that operate on ANY scorer callable
`score(y, sr) -> synthetic_prob in [0,1]` (a mock locally; System-A `fusion.analyze`
on the server). They answer *why* a detector decided, and whether that decision is
CAUSAL or a shortcut:

  * Causal Perturbation — apply LABEL-PRESERVING transforms (codec, mild noise,
    gain, small time-shift) that a human/AI label should survive. A robust detector's
    synthetic-prob barely moves; a fragile/shortcut detector swings. High sensitivity
    to label-preserving perturbations ⇒ fragile decision ⇒ raise novelty/abstain.

  * Counterfactual Authenticity (CAD) — search the SMALLEST perturbation magnitude
    that flips the decision across the 0.5 boundary. A tiny flip distance ⇒ the
    decision sits on a knife-edge (low-confidence / adversarially fragile); a large
    flip distance ⇒ a stable, well-separated decision.

Evidence-only, never standalone; feeds VoxScore/arbitration as a CONFIDENCE modifier.
numpy only, non-breaking. [HYPOTHESIS] — calibrate perturbation budgets on real data.
"""
from __future__ import annotations
import numpy as np
from typing import Callable, Dict, List

Scorer = Callable[[np.ndarray, int], float]


# ---- label-preserving perturbations (a genuine label should survive all of these) ----
def _gain(y, db):          return (y * (10 ** (db / 20.0))).astype(np.float32)
def _noise(y, snr_db):
    p = np.mean(y**2) + 1e-12; n = np.sqrt(p / (10**(snr_db/10.0)))
    return (y + n * np.random.default_rng(0).standard_normal(len(y))).astype(np.float32)
def _shift(y, ms, sr):     s = int(ms*sr/1000); return np.roll(y, s).astype(np.float32)
def _mulaw(y, mu=255.0):   # G.711 μ-law round-trip (telephony)
    c = np.sign(y) * np.log1p(mu*np.abs(y)) / np.log1p(mu)
    q = np.round(c * 128) / 128.0
    return (np.sign(q) * (1/mu) * ((1+mu)**np.abs(q) - 1)).astype(np.float32)

_PERTURBATIONS = {
    "gain+6dB":   lambda y, sr: _gain(y, 6),
    "gain-6dB":   lambda y, sr: _gain(y, -6),
    "noise@30dB": lambda y, sr: _noise(y, 30),
    "shift+20ms": lambda y, sr: _shift(y, 20, sr),
    "g711_ulaw":  lambda y, sr: _mulaw(y),
}


def causal_perturbation(y: np.ndarray, sr: int, score: Scorer) -> Dict:
    y = np.asarray(y, np.float32)
    base = float(score(y, sr))
    deltas = {}
    for name, fn in _PERTURBATIONS.items():
        try:
            deltas[name] = round(float(score(fn(y, sr), sr)) - base, 4)
        except Exception as e:
            deltas[name] = None
    vals = [abs(d) for d in deltas.values() if d is not None]
    sensitivity = float(np.mean(vals)) if vals else 0.0
    max_swing = float(np.max(vals)) if vals else 0.0
    # label-preserving transforms shouldn't move the decision much; if they do → fragile
    fragile = sensitivity > 0.20 or max_swing > 0.35
    return {"base_prob": round(base, 4), "deltas": deltas,
            "mean_sensitivity": round(sensitivity, 4), "max_swing": round(max_swing, 4),
            "fragile": fragile,
            "confidence_penalty": round(float(min(0.4, sensitivity)), 3),
            "verdict": "FRAGILE/shortcut-leaning (raise abstain)" if fragile else "CAUSALLY_STABLE",
            "_status": "HYPOTHESIS — label-preserving perturbation robustness; calibrate budgets on real data."}


def counterfactual(y: np.ndarray, sr: int, score: Scorer,
                   grid: List[float] = None) -> Dict:
    """Smallest additive-noise magnitude (as SNR sweep) that flips the 0.5 decision."""
    y = np.asarray(y, np.float32); grid = grid or [40, 30, 20, 10, 5, 0]
    base = float(score(y, sr)); base_side = base >= 0.5
    flip_snr = None
    for snr in grid:
        p = float(score(_noise(y, snr), sr))
        if (p >= 0.5) != base_side:
            flip_snr = snr; break
    # higher flip_snr (flips even under gentle perturbation) ⇒ knife-edge decision
    knife_edge = flip_snr is not None and flip_snr >= 20
    margin = abs(base - 0.5)
    return {"base_prob": round(base, 4), "decision_margin": round(margin, 4),
            "flip_snr_db": flip_snr, "knife_edge": knife_edge,
            "confidence_penalty": round(0.3 if knife_edge else (0.15 if flip_snr is not None else 0.0), 3),
            "verdict": "KNIFE_EDGE (low-confidence, adversarially fragile)" if knife_edge
                       else ("FLIPPABLE_under_heavy_noise" if flip_snr is not None else "STABLE_decision"),
            "_status": "HYPOTHESIS — counterfactual flip distance; calibrate on adversarial + real data."}


def probe(y: np.ndarray, sr: int, score: Scorer) -> Dict:
    cp = causal_perturbation(y, sr, score); cf = counterfactual(y, sr, score)
    penalty = round(min(0.5, cp["confidence_penalty"] + cf["confidence_penalty"]), 3)
    return {"causal_perturbation": cp, "counterfactual": cf,
            "total_confidence_penalty": penalty,
            "_use": "subtract total_confidence_penalty from evidence_confidence; can trigger abstain. NEVER standalone."}


def _selftest():
    sr = 16000; t = np.linspace(0, 1, sr, endpoint=False)
    y = (0.4*np.sin(2*np.pi*180*t) + 0.02*np.random.default_rng(1).standard_normal(sr)).astype(np.float32)

    # robust scorer: depends on a stable spectral feature (survives label-preserving perturbations)
    def robust(sig, s):
        S = np.abs(np.fft.rfft(sig)); centroid = (np.arange(len(S))*S).sum()/(S.sum()+1e-9)
        return float(np.clip(centroid/ (len(S)*0.5), 0, 1))
    # fragile scorer: keys on absolute peak amplitude (a gain change flips it — shortcut)
    def fragile(sig, s):
        return float(np.clip(np.max(np.abs(sig))*1.4, 0, 1))

    pr = probe(y, sr, robust); pf = probe(y, sr, fragile)
    print("robust scorer :", pr["causal_perturbation"]["verdict"], "| sens", pr["causal_perturbation"]["mean_sensitivity"], "| penalty", pr["total_confidence_penalty"])
    print("fragile scorer:", pf["causal_perturbation"]["verdict"], "| sens", pf["causal_perturbation"]["mean_sensitivity"], "| penalty", pf["total_confidence_penalty"])
    assert pf["causal_perturbation"]["mean_sensitivity"] > pr["causal_perturbation"]["mean_sensitivity"]
    assert pf["total_confidence_penalty"] >= pr["total_confidence_penalty"]
    print("\n[selftest] PASS — fragile/shortcut scorer flagged as sensitive to label-preserving perturbations; robust one stable.")


if __name__ == "__main__":
    _selftest()
