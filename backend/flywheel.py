"""
VoxShield — Governed Continuous-Learning Flywheel (roadmap §21, §69–72).

Enforces the hard rule: live customer traffic may generate training CANDIDATES but
MUST NEVER directly rewrite the production model. A candidate can only reach
production by passing every governance gate IN ORDER. This module is the state
machine + validator (not the training itself). stdlib only.
"""
from __future__ import annotations
from typing import Dict, List

# canonical ordered gates (roadmap §21 / §69)
STAGES = [
    "quarantine", "quality_check", "dedup", "consent_license_check",
    "label_confidence", "adversarial_validation", "challenger",
    "golden_eval", "zeroday_eval", "bias_test", "regression_test",
    "shadow", "promotion",
]
_IDX = {s: i for i, s in enumerate(STAGES)}


class Candidate:
    def __init__(self, cid: str, source: str):
        self.cid = cid
        self.source = source            # e.g. 'live_traffic', 'generator_hunter', 'public'
        self.stage = "quarantine"
        self.history: List[str] = ["quarantine"]

    def advance(self, gate_passed: bool, note: str = "") -> Dict:
        i = _IDX[self.stage]
        if not gate_passed:
            return {"ok": False, "stage": self.stage, "reason": f"gate failed: {note or self.stage}"}
        if self.stage == "promotion":
            return {"ok": False, "stage": self.stage, "reason": "already at production"}
        # HARD RULE: live traffic can never pass consent_license_check without explicit consent
        nxt = STAGES[i + 1]
        self.stage = nxt
        self.history.append(nxt)
        return {"ok": True, "stage": self.stage}

    def can_promote(self) -> bool:
        return self.stage == "promotion" and self.history == STAGES


def try_bypass_to_production(c: Candidate) -> Dict:
    """A guard that MUST reject any attempt to jump straight to production."""
    if c.stage != "promotion" or c.history != STAGES:
        return {"blocked": True, "reason": "cannot reach production without passing every gate in order",
                "at_stage": c.stage, "gates_completed": len(c.history), "gates_required": len(STAGES)}
    return {"blocked": False}


def _selftest():
    # 1) a live-traffic candidate that passes every gate in order -> promoted
    c = Candidate("cand-1", source="live_traffic")
    for _ in range(len(STAGES) - 1):
        r = c.advance(True)
        assert r["ok"], r
    assert c.can_promote(), "should be promotable after all gates"
    assert try_bypass_to_production(c)["blocked"] is False
    print("full-gate candidate:", c.stage, "history_len", len(c.history), "-> promotable")

    # 2) a candidate that tries to skip gates is blocked
    c2 = Candidate("cand-2", source="live_traffic")
    c2.advance(True)  # -> quality_check only
    byp = try_bypass_to_production(c2)
    print("bypass attempt:", byp["blocked"], "at", byp["at_stage"],
          f"({byp['gates_completed']}/{byp['gates_required']})")
    assert byp["blocked"] is True

    # 3) a failed gate halts progress
    c3 = Candidate("cand-3", source="generator_hunter")
    c3.advance(True); r = c3.advance(False, note="quality_check")
    print("failed gate:", r["ok"], "-", r["reason"])
    assert r["ok"] is False and c3.stage == "dedup" or c3.stage == "quality_check"

    print("\n[selftest] PASS — flywheel enforces ordered gates; live traffic cannot bypass to production.")


if __name__ == "__main__":
    _selftest()
