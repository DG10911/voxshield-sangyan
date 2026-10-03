"""
VoxShield — Red Team harness (roadmap §28, P3).

Adversarial self-attack: takes a scorer callable `score(y, sr) -> synthetic_prob`
(a mock locally; System-A fusion on the server) and hammers a clean input through
the hardest conditions we know of — then reports where the detector is WEAK. It does
NOT modify any model; it produces a prioritized weakness report that feeds the
Worst-AI manifest (§16), the Threat Registry (§19), and the training curriculum.

Attacks (all local, via scenario_render + causal_probe):
  * channel/replay/env renders (G.711, narrowband, packet-loss, reverb, replay, nightmare)
  * label-preserving perturbations (should NOT flip a correct decision) via causal_probe
  * counterfactual flip-distance (how little noise flips the call)

numpy + local modules only, non-breaking.
"""
from __future__ import annotations
import numpy as np
from typing import Callable, Dict, List
from scenario_render import render, nightmare_scenario, matrix
from causal_probe import probe

Scorer = Callable[[np.ndarray, int], float]

# conditions a GENUINELY-AI clip should still be caught under (expect high synthetic prob)
_ATTACKS = [
    ("clean", {}), ("g711", {"codec": "g711_ulaw"}), ("narrowband", {"narrowband": True}),
    ("reverb", {"rt60": 0.6}), ("packet_loss", {"packet_loss": 0.05, "snr_db": 15}),
    ("replay", {"replay": True}), ("nightmare", None),
]


def attack(y: np.ndarray, sr: int, score: Scorer, expect_synthetic: bool = True) -> Dict:
    """Run the attack suite on one clip. If expect_synthetic, an attack 'succeeds'
    (evades) when the synthetic prob drops below 0.5 — a detection MISS we must fix."""
    y = np.asarray(y, np.float32)
    results: List[Dict] = []
    for name, spec in _ATTACKS:
        rendered = render(y, sr, nightmare_scenario() if spec is None else spec)["audio"]
        p = float(score(rendered, sr))
        evaded = (p < 0.5) if expect_synthetic else (p >= 0.5)
        results.append({"attack": name, "synthetic_prob": round(p, 3), "evaded": evaded})
    pr = probe(y, sr, score)
    evasions = [r for r in results if r["evaded"]]
    worst = sorted(results, key=lambda r: r["synthetic_prob"] if expect_synthetic else -r["synthetic_prob"])
    robustness = 1.0 - len(evasions)/len(results)
    return {"n_attacks": len(results), "evasions": [r["attack"] for r in evasions],
            "evasion_rate": round(len(evasions)/len(results), 3),
            "robustness_score": round(robustness, 3),
            "weakest_conditions": [r["attack"] for r in worst[:3]],
            "causal_fragility": pr["total_confidence_penalty"],
            "results": results,
            "feeds": ["worst_ai_manifest (§16)", "threat_registry (§19)", "training_curriculum"],
            "_governance": "reports weaknesses only — never modifies production models (§18/§21)."}


def campaign(clips: List[np.ndarray], sr: int, score: Scorer) -> Dict:
    """Aggregate a red-team campaign across several attack clips."""
    reps = [attack(c, sr, score) for c in clips]
    all_ev: Dict[str, int] = {}
    for r in reps:
        for e in r["evasions"]:
            all_ev[e] = all_ev.get(e, 0) + 1
    return {"clips": len(clips),
            "mean_robustness": round(float(np.mean([r["robustness_score"] for r in reps])), 3),
            "evasions_by_condition": dict(sorted(all_ev.items(), key=lambda x: -x[1])),
            "priority_fixes": sorted(all_ev, key=all_ev.get, reverse=True)[:3]}


def _selftest():
    sr = 16000; t = np.linspace(0, 1.5, int(sr*1.5), endpoint=False); rng = np.random.default_rng(0)
    y = (0.4*np.sin(2*np.pi*180*t) + 0.02*rng.standard_normal(len(t))).astype(np.float32)

    # a BRITTLE detector that keys on high-frequency energy → telephony band-limit evades it
    def brittle(sig, s):
        S = np.abs(np.fft.rfft(sig)); f = np.fft.rfftfreq(len(sig), 1/sr)
        return float(np.clip(S[f > 3400].sum()/ (S.sum()+1e-9) * 8, 0, 1))
    # a ROBUST detector: near-constant high synthetic prob regardless of channel
    def robust(sig, s): return 0.9

    rb = attack(y, sr, brittle); rr = attack(y, sr, robust)
    print("brittle: robustness", rb["robustness_score"], "evaded by", rb["evasions"])
    print("robust : robustness", rr["robustness_score"], "evaded by", rr["evasions"])
    assert rb["evasion_rate"] > rr["evasion_rate"]
    assert rr["robustness_score"] == 1.0
    camp = campaign([y, y*0.5], sr, brittle)
    print("campaign priority fixes:", camp["priority_fixes"], "| mean robustness", camp["mean_robustness"])
    assert "priority_fixes" in camp
    print("\n[selftest] PASS — red-team finds the brittle detector's telephony/narrowband evasions; robust one holds.")


if __name__ == "__main__":
    _selftest()
