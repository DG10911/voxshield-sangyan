"""
VoxShield — Self-Critique brain (roadmap §12, P2).

Before VoxShield commits to a HIGH-RISK verdict (about to call a human "AI"), it must
argue against itself. This module runs COUNTER-TESTS: is there an innocent explanation
for the synthetic-looking evidence? Each counter-test that fires lowers confidence or
forces ABSTAIN — protecting unusual-but-genuine humans (the FP the roadmap cares most
about: rare accent, elderly, emotional, bad mic, heavy codec, replay, code-switch,
noise, speakerphone, unknown-generator).

Applied ONLY to would-be AI verdicts (asymmetric — we never talk ourselves *into*
calling a human AI). Consumes a voxscore result + the input profile + brain outputs.
stdlib only, non-breaking. [HYPOTHESIS] — calibrate penalties on Worst-Human set.
"""
from __future__ import annotations
from typing import Dict, List


# each counter-test: (name, condition(ctx)->bool, confidence_penalty, rationale)
COUNTER_TESTS = [
    ("unusual_human_physics", lambda c: c.get("hpcs") is not None and 0.35 <= c["hpcs"] < 0.55, 0.15,
     "borderline physiology — could be an unusual but genuine human, not synthesis"),
    ("heavy_codec",           lambda c: c.get("narrowband") or c.get("codec") in ("g711_ulaw", "g711_alaw", "amr"), 0.12,
     "aggressive codec can mimic synthetic smoothing — don't over-trust HF absence"),
    ("replay_present",        lambda c: (c.get("replay_score") or 0) >= 0.5, 0.10,
     "recorded-genuine (replay) can look synthetic — verify live-vs-recorded before AI"),
    ("high_novelty",          lambda c: (c.get("novelty") or 0) >= 0.45, 0.20,
     "outside known distribution — could be unknown human condition, not a known fake"),
    ("low_quality_input",     lambda c: (c.get("snr_db") is not None and c["snr_db"] < 12) or c.get("quality") == "poor", 0.12,
     "noisy/low-quality capture inflates artifacts — insufficient evidence for a hard call"),
    ("fragile_decision",      lambda c: c.get("fragile") is True or (c.get("flip_snr_db") or 0) >= 20, 0.18,
     "causal-probe says the decision is a knife-edge / label-preserving-fragile"),
    ("code_switch",           lambda c: c.get("code_switch") is True, 0.08,
     "Indic code-switching stresses detectors — genuine speakers switch languages mid-call"),
    ("emotional_or_atypical", lambda c: c.get("style") in ("emotional", "shout", "whisper", "elderly", "child"), 0.10,
     "atypical genuine delivery (emotional/elderly/child) raises false-positive risk"),
]


def critique(voxscore: Dict, context: Dict) -> Dict:
    """context merges profile + brains: hpcs, narrowband, codec, replay_score, novelty,
    snr_db, quality, fragile, flip_snr_db, code_switch, style."""
    risk = voxscore.get("risk") or voxscore.get("verdict")
    high_risk = risk in ("HIGH", "AI") and not voxscore.get("abstain")
    if not high_risk:
        return {"applied": False, "reason": f"not a high-risk verdict (risk={risk})",
                "final_risk": risk, "abstain": voxscore.get("abstain", False)}

    fired: List[Dict] = []
    total = 0.0
    for name, cond, pen, why in COUNTER_TESTS:
        try:
            if cond(context):
                fired.append({"test": name, "penalty": pen, "rationale": why}); total += pen
        except Exception:
            pass
    total = min(0.6, total)
    base_conf = voxscore.get("evidence_confidence", voxscore.get("evidence", 0.7)) or 0.7
    new_conf = max(0.0, base_conf - total)
    # if enough doubt accumulates, DOWNGRADE the hard AI call to ABSTAIN/REVIEW
    downgrade = total >= 0.30 or new_conf < 0.45
    return {"applied": True, "counter_tests_fired": fired, "total_penalty": round(total, 3),
            "evidence_confidence_before": round(float(base_conf), 3),
            "evidence_confidence_after": round(float(new_conf), 3),
            "final_risk": "REVIEW" if downgrade else risk, "abstain": downgrade,
            "note": ("Self-critique found innocent explanations → downgraded to REVIEW/ABSTAIN (protect genuine humans)."
                     if downgrade else "Counter-tests did not overturn the high-risk verdict."),
            "_status": "HYPOTHESIS — asymmetric FP-guard; calibrate penalties on Worst-Human set (§16)."}


def _selftest():
    ai = {"risk": "HIGH", "evidence_confidence": 0.7, "abstain": False}
    # clean confident AI on good input → verdict stands
    r1 = critique(ai, {"hpcs": 0.15, "snr_db": 30, "novelty": 0.1})
    print("clean AI      :", r1["final_risk"], "abstain", r1["abstain"], "penalty", r1["total_penalty"])
    # same AI score but unusual-human context (elderly + narrowband + high novelty + fragile) → downgrade
    r2 = critique(ai, {"hpcs": 0.45, "narrowband": True, "novelty": 0.5, "fragile": True, "style": "elderly"})
    print("atypical human:", r2["final_risk"], "abstain", r2["abstain"], "penalty", r2["total_penalty"],
          "| fired", [f["test"] for f in r2["counter_tests_fired"]])
    # a LOW verdict is never touched (asymmetric)
    r3 = critique({"risk": "LOW", "evidence_confidence": 0.8, "abstain": False}, {})
    assert r1["final_risk"] == "HIGH" and not r1["abstain"]
    assert r2["final_risk"] == "REVIEW" and r2["abstain"]
    assert r3["applied"] is False
    print("\n[selftest] PASS — confident AI on clean input stands; unusual-human context forces ABSTAIN; LOW untouched.")


if __name__ == "__main__":
    _selftest()
