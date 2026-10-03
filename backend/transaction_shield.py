"""
VoxShield — Transaction Shield (roadmap §8, §28).

The banking policy layer on top of CallGuard: it takes the CallGuard risk (which
already fused voice + device + network + account) and applies TRANSACTION context
— type and amount — to decide the required verification step. Higher-value / higher-
sensitivity transactions demand stronger verification for the same call risk.

Decision support only — it recommends the verification requirement; it NEVER blocks.
Pure policy; stdlib. Builds on callguard.assess() output.
"""
from __future__ import annotations
from typing import Dict, Optional

# sensitivity weight per transaction type (higher = needs more verification)
_TXN_SENSITIVITY = {
    "balance_inquiry": 0.1, "statement": 0.2, "bill_pay": 0.5, "transfer": 0.8,
    "add_payee": 0.85, "profile_change": 0.9, "large_transfer": 1.0, "loan": 0.9,
}
# amount escalation bands (INR) -> additional multiplier
def _amount_factor(amount: Optional[float]) -> float:
    if not amount:
        return 0.0
    if amount >= 500000: return 1.0
    if amount >= 100000: return 0.7
    if amount >= 25000:  return 0.4
    if amount >= 5000:   return 0.2
    return 0.05


def assess(callguard_result: Dict, txn_type: str = "transfer",
           amount: Optional[float] = None) -> dict:
    call_risk = float(callguard_result.get("call_risk", 0.0))
    sensitivity = _TXN_SENSITIVITY.get(txn_type, 0.6)
    amt = _amount_factor(amount)

    # combined exposure: how much is at stake × how risky the call is
    exposure = min(1.0, 0.5 * sensitivity + 0.5 * amt)
    combined = min(1.0, 0.6 * call_risk + 0.4 * exposure)

    # required verification tier for THIS transaction
    if combined >= 0.75 or (call_risk >= 0.6 and sensitivity >= 0.8):
        req, action = "MANUAL_FRAUD_REVIEW", "HOLD_FOR_ANALYST"
    elif combined >= 0.5:
        req, action = "STRONG_2FA", "REQUIRE_OTP_AND_BIOMETRIC"
    elif combined >= 0.3:
        req, action = "STEP_UP", "REQUIRE_OTP"
    else:
        req, action = "STANDARD", "PROCEED_NORMAL"

    return {"transaction": txn_type, "amount": amount,
            "call_risk": round(call_risk, 3), "sensitivity": sensitivity,
            "combined_exposure": round(combined, 3),
            "required_verification": req, "recommended_action": action,
            "rationale": f"call_risk={call_risk:.2f} · txn_sensitivity={sensitivity:.2f} · amount_factor={amt:.2f}",
            "note": "Decision support — never auto-blocks; high-value + risky calls escalate verification, not denial."}


def _selftest():
    from voxscore import voxscore
    from callguard import assess as cg_assess
    # low-risk genuine call, small bill pay -> STANDARD
    cg_low = cg_assess(voxscore({"acoustic-dsp": 0.08, "neural:xls-r": 0.1}), {"device_known": True})
    low = assess(cg_low, "bill_pay", 800)
    # high-risk synthetic call, large transfer -> MANUAL_FRAUD_REVIEW
    cg_hi = cg_assess(voxscore({"acoustic-dsp": 0.9, "neural:xls-r": 0.93}),
                      {"device_known": False, "new_caller": True, "unusual_transaction": True, "known_fraud_pattern": True})
    hi = assess(cg_hi, "large_transfer", 600000)
    # genuine but large transfer -> at least STEP_UP (value raises the bar)
    mid = assess(cg_low, "large_transfer", 300000)
    print("low  :", low["required_verification"], "exposure", low["combined_exposure"])
    print("high :", hi["required_verification"], "exposure", hi["combined_exposure"])
    print("mid  :", mid["required_verification"], "exposure", mid["combined_exposure"])
    assert low["required_verification"] == "STANDARD"
    assert hi["required_verification"] == "MANUAL_FRAUD_REVIEW"
    assert mid["required_verification"] in ("STEP_UP", "STRONG_2FA")
    print("\n[selftest] PASS — verification requirement scales with call risk × transaction value/sensitivity.")


if __name__ == "__main__":
    _selftest()
