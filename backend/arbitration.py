"""
VoxShield — Evidence Arbitration v1 + HEDS (roadmap §13, §21, §29, §37).

"Ten correlated neural models agreeing is not ten independent pieces of evidence."
This arbiter combines independent BRAINS by evidence FAMILY, so a stack of
correlated SSL detectors counts as ~one evidence stream, not many. It reports:
    * synthetic     — diversity-weighted fused P(synthetic)
    * heds          — Human Evidence Diversity Score (how many independent,
                      agreeing families support the call)
    * decision      — AI / HUMAN / UNKNOWN(abstain) with the same abstain discipline

Input: brains = [{name, family, score (P_synthetic 0-1), confidence 0-1}, ...].
numpy-only; deterministic; non-breaking. Complements voxscore (which works from raw
per-detector probs); this works from the higher-level brain outputs.
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict


def arbitrate(brains: List[Dict], hi: float = 0.60, lo: float = 0.40) -> dict:
    if not brains:
        return {"synthetic": None, "decision": "UNKNOWN", "abstain": True, "heds": 0.0}
    # 1) collapse within family (correlated detectors -> one confidence-weighted vote)
    fams: Dict[str, list] = {}
    for b in brains:
        fams.setdefault(b.get("family", b.get("name", "?")), []).append(b)
    fam_votes = {}
    for fam, bs in fams.items():
        w = np.array([b.get("confidence", 1.0) for b in bs]) + 1e-9
        s = np.array([float(b["score"]) for b in bs])
        fam_votes[fam] = {"score": float(np.average(s, weights=w)),
                          "confidence": float(np.mean([b.get("confidence", 1.0) for b in bs]))}
    n_fam = len(fam_votes)

    # 2) diversity-weighted fusion across families (each family weighted by its confidence)
    fs = np.array([v["score"] for v in fam_votes.values()])
    fc = np.array([v["confidence"] for v in fam_votes.values()]) + 1e-9
    synthetic = float(np.average(fs, weights=fc))

    # 3) HEDS: fraction of families that CONFIDENTLY agree with the majority side,
    #    scaled by how many independent families exist (more independent = stronger).
    side = synthetic >= 0.5
    agree = [f for f in fam_votes.values() if (f["score"] >= 0.5) == side and abs(f["score"] - 0.5) > 0.1]
    heds = float(min(1.0, (len(agree) / max(n_fam, 1)) * min(1.0, n_fam / 4.0)))

    # 4) decision with abstain: need diverse agreeing evidence to commit
    weak = heds < 0.4 or (lo < synthetic < hi)
    if synthetic >= hi and not weak:
        decision, abstain = "AI", False
    elif synthetic <= lo and not weak:
        decision, abstain = "HUMAN", False
    else:
        decision, abstain = "UNKNOWN", True
    return {"synthetic": round(synthetic, 4), "decision": decision, "abstain": abstain,
            "heds": round(heds, 4), "n_families": n_fam,
            "families": {k: round(v["score"], 3) for k, v in fam_votes.items()},
            "_status": "Evidence Arbitration v1 — family-collapsed diversity weighting; HEDS heuristic pending open-set validation."}


def _selftest():
    # Case A: 6 correlated SSL detectors all say fake -> should count as ~1 family (modest HEDS)
    ssl_only = [{"name": f"ssl{i}", "family": "ssl", "score": 0.9, "confidence": 0.9} for i in range(6)]
    a = arbitrate(ssl_only)
    # Case B: 4 INDEPENDENT families agree fake -> higher HEDS, confident AI
    diverse = [{"name": "ssl", "family": "ssl", "score": 0.88, "confidence": 0.9},
               {"name": "phase", "family": "phase", "score": 0.82, "confidence": 0.85},
               {"name": "physics", "family": "physics", "score": 0.79, "confidence": 0.8},
               {"name": "replay", "family": "replay", "score": 0.75, "confidence": 0.8}]
    b = arbitrate(diverse)
    print("6x correlated SSL :", {k: a[k] for k in ["synthetic", "decision", "heds", "n_families"]})
    print("4 diverse families:", {k: b[k] for k in ["synthetic", "decision", "heds", "n_families"]})
    assert b["heds"] > a["heds"], "diverse independent evidence must yield higher HEDS than correlated stack"
    assert a["n_families"] == 1 and b["n_families"] == 4
    print("\n[selftest] PASS — correlated SSL stack counts as 1 family; diverse evidence scores higher HEDS.")


if __name__ == "__main__":
    _selftest()
