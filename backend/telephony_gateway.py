"""
VoxShield — Telephony Gateway (roadmap §28, P4).

The inline, in-call decision layer for a live telephony deployment. It maps the
VoxShield verdict + CallGuard fraud tier + call context to a graded ACTION:

    allow · warn · step_up_verification · require_2fa · transfer_to_human · investigate

HARD RULE (roadmap-wide): **never auto-block / auto-drop a call on uncertainty.**
An UNKNOWN/abstain or a zero-day never terminates a call by itself — it escalates to
a human or a step-up challenge. Blocking is only ever a human decision downstream.
This is decision-support, not enforcement. Consumes callguard.assess() output +
voxscore + context. stdlib only, non-breaking.
"""
from __future__ import annotations
from typing import Dict, Optional

# ordered least→most friction; we never emit a terminal "block"
ACTIONS = ["allow", "warn", "step_up_verification", "require_2fa", "transfer_to_human", "investigate"]


def decide(voxscore: Dict, callguard: Dict, context: Optional[Dict] = None) -> Dict:
    ctx = context or {}
    verdict = voxscore.get("verdict") or voxscore.get("risk")
    abstain = bool(voxscore.get("abstain"))
    tier = (callguard or {}).get("tier", "LOW")            # LOW/HIGH/CRITICAL
    high_value = bool(ctx.get("high_value_action"))         # e.g. transfer, password reset

    # base action from fraud tier
    action = {"LOW": "allow", "HIGH": "step_up_verification", "CRITICAL": "transfer_to_human"}.get(tier, "warn")

    reasons = [f"callguard_tier={tier}"]
    # uncertainty NEVER blocks — it escalates to a human / challenge
    if abstain or verdict in ("UNKNOWN", "REVIEW"):
        action = _max(action, "transfer_to_human")
        reasons.append("uncertain/zero-day → human review (never auto-block on uncertainty)")
    elif verdict in ("AI", "HIGH"):
        action = _max(action, "require_2fa")
        reasons.append("synthetic-leaning verdict → strong verification")
    # sensitive action in-flight raises the floor
    if high_value and action == "allow":
        action = "warn"; reasons.append("high-value action → minimum warn")
    if high_value and tier != "LOW":
        action = _max(action, "require_2fa"); reasons.append("high-value + elevated risk")

    return {"action": action, "auto_block": False,          # invariant: always False
            "tier": tier, "verdict": verdict, "abstain": abstain,
            "reasons": reasons,
            "note": "decision-support only — VoxShield never terminates a call automatically; blocking is a downstream human decision.",
            "customer_message": _msg(action)}


def _max(a, b):
    return a if ACTIONS.index(a) >= ACTIONS.index(b) else b


def _msg(action):
    return {
        "allow": "Call proceeds normally.",
        "warn": "Proceed with awareness — mild anomaly noted.",
        "step_up_verification": "Please answer a security question to continue.",
        "require_2fa": "A one-time code has been sent — please confirm it.",
        "transfer_to_human": "Connecting you to a specialist for verification.",
        "investigate": "Flagged for review; the interaction continues under monitoring.",
    }[action]


def _selftest():
    lo = {"tier": "LOW"}; hi = {"tier": "HIGH"}; crit = {"tier": "CRITICAL"}
    r_ok   = decide({"verdict": "HUMAN", "abstain": False}, lo)
    r_ai   = decide({"verdict": "AI", "abstain": False}, hi, {"high_value_action": True})
    r_zero = decide({"verdict": "UNKNOWN", "abstain": True}, hi)
    r_crit = decide({"verdict": "AI", "abstain": False}, crit)
    print("genuine+low  :", r_ok["action"])
    print("AI+high+txn  :", r_ai["action"])
    print("zero-day     :", r_zero["action"], "| auto_block", r_zero["auto_block"])
    print("critical     :", r_crit["action"])
    assert r_ok["action"] == "allow"
    assert r_ai["action"] == "require_2fa"
    assert r_zero["action"] == "transfer_to_human" and r_zero["auto_block"] is False
    assert all(decide(v, c)["auto_block"] is False for v in
               [{"verdict": "AI"}, {"verdict": "UNKNOWN", "abstain": True}] for c in [lo, hi, crit])
    print("\n[selftest] PASS — actions scale with risk; uncertainty escalates to a human; auto_block is ALWAYS False.")


if __name__ == "__main__":
    _selftest()
