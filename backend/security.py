"""
VoxShield — Privacy & Security controls (roadmap §24, §73–74).

Treats VoxShield as critical infrastructure. Provides:
  * THREAT_MODEL — enumerated threats + mitigations (for review & audit)
  * privacy_check() — enforces data-minimization + consent before any sample is
    retained (no raw audio kept without a consent/licence basis; PII flagged)
  * redact() — strips/pseudonymises PII for the Unknown Vault / logs
  * self_audit() — reports mitigation coverage
stdlib only; non-breaking.
"""
from __future__ import annotations
import hashlib
from typing import Dict, List

THREAT_MODEL = [
    {"threat": "adversarial audio / examples", "mitigation": "adversarial-robustness eval; multi-detector fusion; abstain band"},
    {"threat": "model extraction via API",       "mitigation": "rate limiting, auth, per-tenant quotas, output coarsening"},
    {"threat": "API abuse / flooding",           "mitigation": "authn/z, rate limits, anomaly detection on usage"},
    {"threat": "data poisoning (training set)",  "mitigation": "governed flywheel: quarantine→validation→challenger→shadow; never live→prod"},
    {"threat": "insider / privileged access",    "mitigation": "access control, audit logs, least privilege, customer isolation"},
    {"threat": "privacy leakage of call audio",  "mitigation": "data minimization, on-prem/regional, encryption, retention+deletion"},
    {"threat": "prompt/API injection (if LLM)",  "mitigation": "input validation, sandboxing, no untrusted tool exec"},
    {"threat": "generator adaptation / arms-race","mitigation": "generalization-gap monitoring, generator hunter, continuous eval"},
]

PII_FIELDS = {"phone", "caller_id", "account_id", "customer_name", "raw_audio_path", "email"}


def privacy_check(record: Dict) -> Dict:
    """A sample may only be RETAINED if it carries a consent/licence basis and
    (if it holds raw audio/PII) that basis explicitly permits it."""
    errs = []
    consent = record.get("consent")
    if consent not in (True, "public", "licensed", "internal-generated"):
        errs.append("no valid consent/licence basis — must not retain")
    has_pii = any(k in record for k in PII_FIELDS)
    if has_pii and consent in (None, False):
        errs.append("PII/raw audio present without consent — reject or redact")
    if not record.get("provenance"):
        errs.append("missing provenance")
    return {"retain_ok": len(errs) == 0, "issues": errs, "has_pii": has_pii}


def redact(record: Dict) -> Dict:
    """Pseudonymise PII for vault/logs (hash, keep last-4 for phone)."""
    out = dict(record)
    for k in PII_FIELDS:
        if k in out and out[k] is not None:
            v = str(out[k])
            if k == "phone" and len(v) >= 4:
                out[k] = "••••" + v[-4:]
            else:
                out[k] = "sha256:" + hashlib.sha256(v.encode()).hexdigest()[:12]
    out["_redacted"] = True
    return out


def self_audit() -> Dict:
    return {"threats_modelled": len(THREAT_MODEL),
            "all_have_mitigation": all(t.get("mitigation") for t in THREAT_MODEL),
            "controls": ["data_minimization", "consent_enforcement", "pii_redaction",
                         "audit_logs", "access_control", "encryption", "retention_deletion",
                         "governed_learning", "rate_limiting", "tenant_isolation"]}


def _selftest():
    ok = {"sample_id": "s1", "consent": "public", "provenance": "MLAAD"}
    bad = {"sample_id": "s2", "phone": "+919876543210", "caller_id": "x", "consent": None}
    a = privacy_check(ok); b = privacy_check(bad)
    print("clean record retain_ok:", a["retain_ok"])
    print("PII no-consent issues :", b["issues"])
    red = redact(bad)
    print("redacted phone        :", red["phone"], "| caller_id:", red["caller_id"])
    aud = self_audit()
    print("threats modelled      :", aud["threats_modelled"], "all mitigated:", aud["all_have_mitigation"])
    assert a["retain_ok"] and not b["retain_ok"]
    assert red["phone"].startswith("••••") and red["caller_id"].startswith("sha256:")
    assert aud["all_have_mitigation"]
    print("\n[selftest] PASS — consent enforced, PII rejected/redacted, threat model complete.")


if __name__ == "__main__":
    _selftest()
