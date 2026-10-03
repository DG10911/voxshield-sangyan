"""
VoxShield — CallGuard (roadmap §5/§28): voice + device + network + behaviour +
account + transaction fraud fusion.

The audio detector alone does NOT make the fraud decision. CallGuard combines the
VoxScore (voice authenticity) with contextual risk signals into a single, explained
CallRisk with a recommended workflow action. It is DECISION SUPPORT: it recommends
allow / step-up / fraud-desk — it NEVER auto-blocks a customer (roadmap rule).

Inputs:
    voxscore : dict from voxscore.py (uses synthetic_score, risk, novelty, abstain)
    context  : optional dict, any of:
        device_known (bool)         known/trusted device?
        new_caller (bool)           first time from this number/account?
        account_risk (0-1)          account's standing/history risk
        unusual_transaction (bool)  out-of-pattern request?
        known_fraud_pattern (bool)  matches a known fraud script/pattern?
        amount (float)              transaction amount (relative escalation only)
"""
from __future__ import annotations
from typing import Dict, Optional


_WEIGHTS = {"voice": 0.40, "device_known": 0.12, "new_caller": 0.10,
            "account_risk": 0.12, "unusual_transaction": 0.13, "known_fraud_pattern": 0.13}


def assess(voxscore: Dict, context: Optional[Dict] = None) -> dict:
    ctx = context or {}
    voice = float(voxscore.get("synthetic_score", voxscore.get("authenticity", {}).get("synthetic", 0.0)))
    novelty = float(voxscore.get("novelty", 0.0))
    abstain = bool(voxscore.get("abstain", False))

    contribs = {"voice": voice}
    contribs["device_known"] = 0.0 if ctx.get("device_known", True) else 1.0
    contribs["new_caller"] = 1.0 if ctx.get("new_caller") else 0.0
    contribs["account_risk"] = float(ctx.get("account_risk", 0.0))
    contribs["unusual_transaction"] = 1.0 if ctx.get("unusual_transaction") else 0.0
    contribs["known_fraud_pattern"] = 1.0 if ctx.get("known_fraud_pattern") else 0.0

    risk = sum(_WEIGHTS[k] * contribs[k] for k in _WEIGHTS)
    # a matched known fraud pattern is a hard escalator
    if ctx.get("known_fraud_pattern"):
        risk = max(risk, 0.75)
    risk = float(min(1.0, max(0.0, risk)))

    # tier + action (voice abstain/high-novelty => can't clear on voice alone)
    if risk >= 0.75 or (ctx.get("known_fraud_pattern") and voice >= 0.5):
        tier, action = "CRITICAL", "TRANSFER_TO_FRAUD_DESK"
    elif risk >= 0.5 or abstain or novelty >= 0.45:
        tier, action = "HIGH", "STEP_UP_VERIFICATION"    # OTP / biometric / knowledge
    elif risk >= 0.3:
        tier, action = "MEDIUM", "ADDITIONAL_VERIFICATION"
    else:
        tier, action = "LOW", "CONTINUE_NORMAL_FLOW"

    reasons = []
    if voice >= 0.6: reasons.append(f"high synthetic-voice probability ({voice:.2f})")
    if abstain or novelty >= 0.45: reasons.append("voice inconclusive / possible unseen attack — cannot clear on voice alone")
    if not ctx.get("device_known", True): reasons.append("unknown/untrusted device")
    if ctx.get("new_caller"): reasons.append("new caller")
    if ctx.get("account_risk", 0) >= 0.5: reasons.append("elevated account risk")
    if ctx.get("unusual_transaction"): reasons.append("out-of-pattern transaction")
    if ctx.get("known_fraud_pattern"): reasons.append("matches a known fraud pattern")

    return {"call_risk": round(risk, 3), "tier": tier, "recommended_action": action,
            "contributors": {k: round(v, 3) for k, v in contribs.items()},
            "reasons": reasons,
            "note": "Decision support only — VoxShield never auto-blocks; a human handles CRITICAL."}


def _selftest():
    from voxscore import voxscore
    # synthetic voice + hostile context -> CRITICAL
    vs_fake = voxscore({"acoustic-dsp": 0.9, "neural:xls-r": 0.93, "fusion-head(LFCC+CQCC)": 0.9})
    crit = assess(vs_fake, {"device_known": False, "new_caller": True, "account_risk": 0.7,
                            "unusual_transaction": True, "known_fraud_pattern": True, "amount": 250000})
    # genuine voice + normal context -> LOW
    vs_real = voxscore({"acoustic-dsp": 0.08, "neural:xls-r": 0.1, "fusion-head(LFCC+CQCC)": 0.09})
    low = assess(vs_real, {"device_known": True, "new_caller": False, "account_risk": 0.1})
    # zero-day voice (abstain) + normal context -> HIGH (can't clear on voice)
    vs_zd = voxscore({"acoustic-dsp": 0.82, "neural:xls-r": 0.31, "neural:distilhubert": 0.66})
    zd = assess(vs_zd, {"device_known": True})
    print("FAKE+hostile:", crit["tier"], crit["recommended_action"], "risk", crit["call_risk"])
    print("REAL+normal :", low["tier"], low["recommended_action"], "risk", low["call_risk"])
    print("ZERO-DAY    :", zd["tier"], zd["recommended_action"], "risk", zd["call_risk"])
    assert crit["tier"] == "CRITICAL" and low["tier"] == "LOW" and zd["tier"] == "HIGH"
    assert "auto-block" in crit["note"]
    print("\n[selftest] PASS — CallGuard fuses voice+context; abstain can't be cleared on voice; never auto-blocks.")


if __name__ == "__main__":
    _selftest()
