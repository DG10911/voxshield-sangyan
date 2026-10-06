"""
VoxShield — VoxScore meta-uncertainty layer  (non-breaking add-on).

The existing fusion.analyze() returns ONE calibrated score. The VoxShield master
vision (§29 evidence diversity, §34 meta-uncertainty, §42 evidence arbitration,
§63 VoxScore) requires the system to NOT collapse everything into one number, and
above all to flag when an input is *unlike anything it knows* (open-set / zero-day)
instead of silently forcing "human".

This module wraps a set of per-detector fake-probabilities (e.g. the `per_model`
dict from fusion.analyze()) and produces a multi-dimensional VoxScore:

    authenticity            {human, synthetic}
    evidence_confidence     how much independent, agreeing evidence supports it
    distribution_confidence how "in-distribution" the pattern looks (calibration proxy)
    novelty                 open-set signal: detectors disagree / score is ambiguous
    risk                    LOW / REVIEW / MEDIUM / HIGH  (with an ABSTAIN band)

IMPORTANT — honest status:
  * `authenticity` is grounded in the trained detectors (VERIFIED path).
  * `evidence_confidence`, `distribution_confidence`, `novelty` here are
    AGREEMENT-BASED HEURISTICS — a research hypothesis (open-set via detector
    disagreement + score ambiguity), NOT a trained OOD/novelty detector. They must
    be validated against a real open-set / unseen-generator benchmark before any
    public claim. See eval plan in VOXSHIELD_MASTER_PLAN.md.

Nothing in fusion.py / features.py / app.py is modified; this only consumes their
output. Integrate by calling voxscore.from_analyze(fusion.analyze(y, sr)).
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional

# detector families we treat as (approximately) independent evidence streams.
# used to down-weight evidence_confidence when only correlated SSL models fired.
_FAMILY = {
    "acoustic-dsp": "dsp",
    "fusion-head(LFCC+CQCC)": "cepstral",
    # everything else (wav2vec2 / xls-r / distilhubert / neural:*) is SSL:
}
def _family(name: str) -> str:
    n = name.lower()
    if n in _FAMILY:
        return _FAMILY[n]
    if "lfcc" in n or "cqcc" in n or "cepstral" in n:
        return "cepstral"
    if "dsp" in n or "acoustic" in n:
        return "dsp"
    return "ssl"


def _stats(xs: List[float]):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / n
    return m, math.sqrt(var)


def voxscore(
    detector_probs: Dict[str, float],
    fused_score: Optional[float] = None,
    reasons: Optional[Dict[str, float]] = None,
    hi: float = 0.70,
    lo: float = 0.40,
) -> dict:
    """Compute a multi-dimensional VoxScore from per-detector fake-probabilities.

    detector_probs : {detector_name: P(synthetic)} in [0,1]
    fused_score    : optional final fused P(synthetic); if None, uses the
                     recall-aware blend (0.45*mean + 0.55*max) that fusion.py uses.
    reasons        : optional signal-derived reason codes (passed through).
    """
    names = list(detector_probs.keys())
    probs = [float(detector_probs[k]) for k in names]
    if not probs:
        return {"error": "no detector outputs"}

    mean_p, std_p = _stats(probs)
    mx = max(probs)
    if fused_score is None:                      # mirror fusion.py's blend
        fused_score = 0.45 * mean_p + 0.55 * mx
    fused_score = min(1.0, max(0.0, float(fused_score)))

    # --- evidence: agreement + polarity, scaled by family diversity -------------
    # agreement: 1 when detectors are unanimous, →0 when maximally split.
    agreement = 1.0 - min(1.0, std_p / 0.5)
    # polarity: how far from the 0.5 fence the detectors sit (confident vs hedging).
    polarity = sum(abs(p - 0.5) for p in probs) / len(probs) * 2.0
    # diversity: how many independent families actually fired (1..3 here).
    n_fam = len(set(_family(n) for n in names))
    diversity = min(1.0, n_fam / 3.0)            # 3 families = full credit
    evidence_confidence = max(0.0, min(1.0, (0.45 * agreement + 0.35 * polarity + 0.20 * diversity)))

    # --- novelty / open-set heuristic ------------------------------------------
    # High when detectors DISAGREE and the fused score sits in the ambiguous band.
    ambiguity = 1.0 - min(1.0, abs(fused_score - 0.5) * 2.0)   # 1 at 0.5, 0 at poles
    disagreement = 1.0 - agreement
    novelty = max(0.0, min(1.0, 0.55 * disagreement + 0.45 * ambiguity))
    # distribution_confidence: confident + agreeing + diverse => in-distribution.
    distribution_confidence = max(0.0, min(1.0, polarity * agreement * (0.6 + 0.4 * diversity)))

    # --- risk decision with an ABSTAIN band ------------------------------------
    # Never force a call when evidence is weak or the input looks novel: the
    # vision (and banking reality) require step-up verification, not auto-block.
    weak = evidence_confidence < 0.45 or novelty >= 0.45
    # A DECISIVE fused score wins even when evidence is weak: a genuine voice scored
    # near-0 must be HUMAN (not abstained). Abstention is reserved for the ambiguous
    # MIDDLE band, where forcing a call is what causes false alarms.
    if fused_score >= hi:
        risk = "HIGH"
    elif fused_score <= lo:
        risk = "LOW"
    elif weak:
        risk = "REVIEW"          # abstain band -> human / step-up verification
    else:
        risk = "MEDIUM"

    interp = _interpret(fused_score, evidence_confidence, distribution_confidence, novelty)
    verdict, abstain = _verdict2(risk)

    out = {
        # --- VoxScore 1.0 fields (kept for backward compatibility) ---
        "authenticity": {"human": round(1.0 - fused_score, 4),
                          "synthetic": round(fused_score, 4)},
        "evidence_confidence": round(evidence_confidence, 4),
        "distribution_confidence": round(distribution_confidence, 4),
        "novelty": round(novelty, 4),
        "risk": risk,
        "detectors": {"n": len(names), "families": n_fam,
                      "agreement": round(agreement, 4), "polarity": round(polarity, 4)},
        "interpretation": interp,
        # --- VoxScore 2.0 schema (roadmap §13) — superset; UNKNOWN & abstain first-class ---
        "verdict": verdict,                                   # HUMAN | AI | REPLAY | HYBRID | UNKNOWN
        "abstain": abstain,
        "detection_confidence": round(max(fused_score, 1.0 - fused_score), 4),
        "synthetic_score": round(fused_score, 4),
        # brains not yet built (roadmap §9–13, P2) -> null, never fabricated:
        "human_physics_score": None,
        "replay_score": None,
        "environment_consistency": None,
        "capture_chain_consistency": None,
        "speaker_consistency": None,
        "reason_codes": [f"{k}:{v}" for k, v in (reasons or {}).items()],
        "_status": "authenticity/synthetic=VERIFIED(detectors); "
                   "evidence/novelty/distribution=HEURISTIC(agreement-based, unvalidated); "
                   "physics/replay/environment/capture/speaker=PENDING(brains not built).",
    }
    if reasons is not None:
        out["reasons"] = reasons
    return out


def _verdict2(risk):
    """Map risk band -> VoxScore 2.0 verdict. Never force a class when unsure:
    MEDIUM/REVIEW -> UNKNOWN + abstain (roadmap: UNKNOWN is a valid result).
    REPLAY/HYBRID require the replay brain (§10, not built) -> not emitted yet."""
    if risk == "HIGH":
        return "AI", False
    if risk == "LOW":
        return "HUMAN", False
    return "UNKNOWN", True   # MEDIUM or REVIEW -> abstain, do not force HUMAN/AI


def _interpret(score, ev, dist, nov) -> str:
    if nov >= 0.45:
        return ("Anomalous / conflicting signals — the input looks OUTSIDE the system's known "
                "distribution (possible zero-day / unseen generator). Do not auto-decide; route to review.")
    if score >= 0.70 and ev >= 0.55:
        return "Strong, agreeing evidence of synthetic voice. Escalate to step-up verification."
    if score <= 0.40 and ev >= 0.55:
        return "Consistent evidence of genuine human speech. Continue standard checks."
    if ev < 0.45:
        return "Weak / conflicting evidence. Insufficient to decide — additional verification."
    return "Inconclusive. Apply additional verification before proceeding."


def from_analyze(result: dict, **kw) -> dict:
    """Consume a fusion.analyze() result dict without modifying fusion.py."""
    return voxscore(
        detector_probs=result.get("per_model", {}),
        fused_score=result.get("score"),
        reasons=result.get("reasons"),
        **kw,
    )


# ----------------------------------------------------------------------------
def _selftest():
    import json
    scenarios = {
        "confident_synthetic (agreeing detectors)": (
            {"acoustic-dsp": 0.88, "neural:xls-r": 0.93, "neural:distilhubert": 0.90,
             "fusion-head(LFCC+CQCC)": 0.91}, None),
        "confident_genuine (agreeing detectors)": (
            {"acoustic-dsp": 0.07, "neural:xls-r": 0.10, "neural:distilhubert": 0.09,
             "fusion-head(LFCC+CQCC)": 0.08}, None),
        "ZERO-DAY-like (detectors disagree, ambiguous)": (
            {"acoustic-dsp": 0.82, "neural:xls-r": 0.31, "neural:distilhubert": 0.66,
             "fusion-head(LFCC+CQCC)": 0.44}, None),
        "weak_evidence (few, hedging detectors)": (
            {"neural:xls-r": 0.55, "acoustic-dsp": 0.52}, None),
    }
    for name, (dp, fs) in scenarios.items():
        vs = voxscore(dp, fused_score=fs)
        print(f"\n### {name}")
        print(f"  authenticity synthetic={vs['authenticity']['synthetic']}  "
              f"risk={vs['risk']}  novelty={vs['novelty']}  "
              f"evidence={vs['evidence_confidence']}  dist_conf={vs['distribution_confidence']}")
        print(f"  → {vs['interpretation']}")
    # verify the key property: the zero-day case must NOT resolve to LOW/HIGH.
    zd = voxscore(scenarios["ZERO-DAY-like (detectors disagree, ambiguous)"][0])
    assert zd["risk"] == "REVIEW", "zero-day-like input should abstain to REVIEW"
    print("\n[selftest] PASS — ambiguous/disagreeing input correctly routed to REVIEW (not forced to a class).")


if __name__ == "__main__":
    _selftest()
