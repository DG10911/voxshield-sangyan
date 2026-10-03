"""
VoxShield — Detector Cascade L0–L3 (roadmap §12, P2).

A latency/power-aware escalation ladder so cheap tiers handle easy cases and expensive
tiers only run when needed. Targets (TARGETS, not measured claims):

  L0  <300 ms  fast_l0 gate — silence/energy/band proxy; fast-pass obvious low-risk
  L1  ~1 s     cheap DSP signals (physics HPCS + phase PTS) — clear the very-human
  L2  ~3 s     detector-bank fusion + VoxScore (the main decision + abstain)
  L3  <5 s     full evidence brains + arbitration + self-critique (hard/borderline only)

Each tier can DECIDE (stop) or ESCALATE. Compute is spent proportional to difficulty.
Orchestration only — reuses fast_l0, physics, phase_traj, voxscore, self_critique;
the detector bank is injected (fusion.analyze on server). numpy + local modules.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Optional, Callable

from fast_l0 import screen
from physics import human_physics
from phase_traj import phase_trajectory
from voxscore import voxscore
from self_critique import critique

TARGETS_MS = {"L0": 300, "L1": 1000, "L2": 3000, "L3": 5000}


def run(y: np.ndarray, sr: int,
        detector_probs: Optional[Dict[str, float]] = None,
        context: Optional[Dict] = None,
        force_deep: bool = False) -> Dict:
    y = np.asarray(y, np.float32); ctx = dict(context or {}); trail = []

    # ---- L0: fast gate ----
    l0 = screen(y, sr)
    trail.append({"tier": "L0", "target_ms": TARGETS_MS["L0"], "decision": l0["decision"]})
    if not l0["escalate"] and not force_deep:
        return {"tier_reached": "L0", "verdict": "LOW_RISK", "abstain": False, "trail": trail,
                "note": "fast-passed; no detector compute spent."}

    # ---- L1: cheap DSP (very-human early-out) ----
    hp = human_physics(y, sr); pt = phase_trajectory(y, sr)
    ctx.setdefault("hpcs", hp["hpcs"])
    trail.append({"tier": "L1", "target_ms": TARGETS_MS["L1"], "hpcs": hp["hpcs"], "pts": pt["pts"]})
    very_human = hp["hpcs"] >= 0.7 and (pt["pts"] or 0) >= 0.7
    if very_human and not detector_probs and not force_deep:
        return {"tier_reached": "L1", "verdict": "LOW_RISK", "abstain": False, "trail": trail,
                "note": "strong human physics + coherent phase; cleared without the detector bank."}

    # ---- L2: detector bank fusion + VoxScore ----
    if not detector_probs:
        return {"tier_reached": "L1", "verdict": "NEEDS_DETECTOR_BANK", "abstain": None, "trail": trail,
                "note": "escalated past L1 but no detector_probs supplied (inject fusion.analyze)."}
    vs = voxscore(detector_probs)
    trail.append({"tier": "L2", "target_ms": TARGETS_MS["L2"], "risk": vs["risk"],
                  "synthetic": vs["synthetic_score"], "novelty": vs["novelty"]})
    ctx.setdefault("novelty", vs["novelty"])
    # confident, low-novelty, non-abstain → stop at L2
    if vs["risk"] in ("LOW", "HIGH") and not vs.get("abstain") and vs["novelty"] < 0.45 and not force_deep:
        # even a confident HIGH gets a self-critique pass (asymmetric FP-guard) at L2
        sc = critique(vs, ctx)
        final = sc["final_risk"] if sc["applied"] else vs["risk"]
        return {"tier_reached": "L2", "verdict": final, "abstain": sc.get("abstain", False),
                "voxscore": vs, "self_critique": sc if sc["applied"] else None, "trail": trail}

    # ---- L3: full brains + arbitration + self-critique (hard/borderline) ----
    from orchestrate import run as orchestrate_run
    o = orchestrate_run(y, sr, detector_probs=detector_probs, context=context, deep_on_lowrisk=True)
    sc = critique({"risk": o.get("verdict"), "abstain": o.get("abstain"),
                   "evidence_confidence": vs["evidence_confidence"]}, ctx)
    final = sc["final_risk"] if sc["applied"] else o.get("verdict")
    trail.append({"tier": "L3", "target_ms": TARGETS_MS["L3"], "arbiter": o.get("verdict"),
                  "self_critique": sc.get("final_risk")})
    return {"tier_reached": "L3", "verdict": final, "abstain": sc.get("abstain", o.get("abstain")),
            "voxscore": vs, "arbitration": o.get("arbitration"), "brains": o.get("brains"),
            "self_critique": sc if sc["applied"] else None, "trail": trail,
            "note": "hard/borderline case — full evidence spent."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False); rng = np.random.default_rng(0)
    y = (0.4*np.sin(2*np.pi*180*t) + 0.02*rng.standard_normal(len(t))).astype(np.float32)

    # a clip with no detector bank supplied → cascade escalates but can't decide past L1
    nat = sum(np.sin(2*np.pi*f*t) for f in [170, 340, 800, 2600, 5200])/5 + 0.02*rng.standard_normal(len(t))
    nat = (nat * 0.3/(np.max(np.abs(nat))+1e-9)).astype(np.float32)
    r0 = run(nat, sr)
    print("no-bank     :", r0["tier_reached"], r0["verdict"], "| trail starts", r0["trail"][0]["tier"])

    # confident synthetic, low novelty → decides early (L2), self-critique passes on clean ctx
    r2 = run(y, sr, detector_probs={"acoustic-dsp": 0.9, "neural:xls-r": 0.92, "neural:distilhubert": 0.9},
             context={"snr_db": 30})
    print("confident AI:", r2["tier_reached"], r2["verdict"], "abstain", r2["abstain"])

    # disagreeing detectors → escalate to L3 (full brains + arbitration)
    r3 = run(y, sr, detector_probs={"acoustic-dsp": 0.82, "neural:xls-r": 0.31, "neural:distilhubert": 0.66})
    print("zero-day    :", r3["tier_reached"], r3["verdict"], "abstain", r3["abstain"])

    assert r0["trail"][0]["tier"] == "L0"                       # ladder always starts at L0
    assert r2["tier_reached"] == "L2" and r2["verdict"] in ("HIGH", "AI")   # confident stops early
    assert r3["tier_reached"] == "L3"                           # disagreement spends full compute
    print("\n[selftest] PASS — ladder starts at L0; confident case decides at L2; disagreement escalates to L3.")


if __name__ == "__main__":
    _selftest()
