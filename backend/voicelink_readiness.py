"""
VoxShield — VoiceLink Telephony Lab readiness gate (roadmap §26, external-telco drop-in).

The roadmap says: before wiring a real SIP/telephony provider (Twilio/Plivo/Exotel/
Knowlarity → Indian telecom → real device → VoxShield), answer 25 verification questions.
This module encodes those 25 questions as a machine-checkable checklist and returns a
GO / NO-GO with the exact blockers, so integration never starts on unverified assumptions
(and never touches customer audio without a consent/contract basis). stdlib only.
"""
from __future__ import annotations
from typing import Dict, List

# the 25 questions (roadmap §26), grouped
QUESTIONS: List[Dict] = [
    {"id": "sip",            "q": "SIP trunk supported?",                          "critical": True},
    {"id": "rtp",            "q": "RTP media access?",                             "critical": True},
    {"id": "websocket",      "q": "WebSocket media streaming?",                    "critical": True},
    {"id": "raw_audio",      "q": "Raw audio frames available?",                   "critical": True},
    {"id": "sr_8k",          "q": "8 kHz supported?",                              "critical": True},
    {"id": "sr_16k",         "q": "16 kHz supported?",                             "critical": False},
    {"id": "g711",           "q": "G.711 μ-law & A-law?",                          "critical": True},
    {"id": "bidi_stream",    "q": "Bidirectional streaming?",                      "critical": False},
    {"id": "timestamps",     "q": "Per-frame timestamps?",                         "critical": False},
    {"id": "events",         "q": "Call events (answer/hangup/DTMF)?",             "critical": False},
    {"id": "recordings",     "q": "Recording access (with consent)?",             "critical": False},
    {"id": "metadata",       "q": "Call metadata (CLI, direction)?",              "critical": False},
    {"id": "retention",      "q": "Retention/deletion controls?",                 "critical": True},
    {"id": "webhooks",       "q": "Webhooks/callbacks?",                          "critical": False},
    {"id": "concurrency",    "q": "Concurrent-call limits known?",                "critical": False},
    {"id": "sandbox",        "q": "Sandbox/test environment?",                    "critical": True},
    {"id": "test_numbers",   "q": "Test numbers available?",                      "critical": False},
    {"id": "inbound",        "q": "Inbound calls supported?",                     "critical": False},
    {"id": "outbound",       "q": "Outbound calls supported?",                    "critical": False},
    {"id": "custom_sip",     "q": "Custom SIP headers?",                          "critical": False},
    {"id": "api_limits",     "q": "API rate limits documented?",                  "critical": False},
    {"id": "research_partner","q": "Research/partnership terms clear?",           "critical": False},
    {"id": "consent_data",   "q": "Consent basis for all customer data?",         "critical": True},
    {"id": "dlt_compliance", "q": "India DLT/telecom compliance handled?",        "critical": True},
    {"id": "privacy",        "q": "Privacy/regional storage compliant?",          "critical": True},
]


def assess(answers: Dict[str, bool]) -> Dict:
    """answers: {question_id: True/False}. Missing = treated as not-yet-verified (False)."""
    verified, unverified, blockers = [], [], []
    for item in QUESTIONS:
        ok = bool(answers.get(item["id"], False))
        (verified if ok else unverified).append(item["id"])
        if not ok and item["critical"]:
            blockers.append(item["id"])
    go = len(blockers) == 0
    return {"total": len(QUESTIONS), "verified": len(verified), "unverified": len(unverified),
            "critical_blockers": blockers,
            "decision": "GO" if go else "NO-GO",
            "note": ("all critical items verified — safe to begin integration" if go else
                     f"{len(blockers)} critical item(s) unverified — do NOT start integration yet"),
            "unverified_items": [q["q"] for q in QUESTIONS if q["id"] in unverified],
            "_governance": "no customer audio may be processed without a consent/contract basis (consent_data + dlt_compliance)."}


def _selftest():
    none = assess({}); print("no answers :", none["decision"], "| blockers", len(none["critical_blockers"]))
    assert none["decision"] == "NO-GO" and len(none["critical_blockers"]) > 0
    # verify everything critical
    crit_ids = [q["id"] for q in QUESTIONS if q["critical"]]
    full = assess({cid: True for cid in crit_ids})
    print("critical ok:", full["decision"], "| verified", full["verified"], "/", full["total"])
    assert full["decision"] == "GO" and not full["critical_blockers"]
    # missing one critical (consent) → NO-GO
    minus = assess({cid: True for cid in crit_ids if cid != "consent_data"})
    print("no consent :", minus["decision"], "| blocker", minus["critical_blockers"])
    assert minus["decision"] == "NO-GO" and "consent_data" in minus["critical_blockers"]
    print("\n[selftest] PASS — 25-question gate: GO only when every critical item (incl. consent + DLT) is verified.")


if __name__ == "__main__":
    _selftest()
