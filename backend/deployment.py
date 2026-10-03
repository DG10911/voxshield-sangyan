"""
VoxShield — Deployment profiles & product surfaces (roadmap §28–29, P2).

Turns the built engine into shippable products WITHOUT new science — just governed
configuration. Two axes:

  * DEPLOY MODE — cloud · private-cloud · on-prem · air-gapped · hybrid · edge.
    Each fixes data-residency, model location, telemetry, retention, external calls.
  * PRODUCT SURFACE — Cloud (multi-tenant SaaS) · Enterprise (single-tenant/on-prem)
    · Indic (India data-residency, Indic-language routing). Each maps to a default
    deploy mode + policy, which callers can tighten but never loosen past the mode.

Invariants enforced here (fail-closed): air-gapped/on-prem ⇒ NO external telemetry,
NO external model/API calls; edge ⇒ on-device model, minimal retention. stdlib only.
"""
from __future__ import annotations
from typing import Dict, List

DEPLOY_MODES = {
    "cloud":       {"data_residency": "provider-region", "model_location": "cloud",   "external_telemetry": True,  "external_model_calls": True,  "default_retention_days": 30},
    "private":     {"data_residency": "tenant-vpc",      "model_location": "cloud",   "external_telemetry": False, "external_model_calls": False, "default_retention_days": 30},
    "on-prem":     {"data_residency": "customer-dc",     "model_location": "on-prem", "external_telemetry": False, "external_model_calls": False, "default_retention_days": 14},
    "air-gapped":  {"data_residency": "customer-dc",     "model_location": "on-prem", "external_telemetry": False, "external_model_calls": False, "default_retention_days": 7},
    "hybrid":      {"data_residency": "split",           "model_location": "cloud+edge","external_telemetry": True, "external_model_calls": False, "default_retention_days": 30},
    "edge":        {"data_residency": "on-device",       "model_location": "edge",    "external_telemetry": False, "external_model_calls": False, "default_retention_days": 1},
}

PRODUCT_SURFACES = {
    "cloud":      {"mode": "cloud",     "multi_tenant": True,  "indic_routing": False, "note": "multi-tenant SaaS"},
    "enterprise": {"mode": "on-prem",   "multi_tenant": False, "indic_routing": False, "note": "single-tenant / on-prem or private"},
    "indic":      {"mode": "private",   "multi_tenant": True,  "indic_routing": True,  "residency": "India", "note": "India data-residency + Indic-language routing"},
}


def profile(surface: str, overrides: Dict | None = None) -> Dict:
    if surface not in PRODUCT_SURFACES:
        raise ValueError(f"unknown surface '{surface}' (choose {list(PRODUCT_SURFACES)})")
    prod = dict(PRODUCT_SURFACES[surface])
    mode = prod["mode"]; base = dict(DEPLOY_MODES[mode])
    cfg = {**base, **prod, "deploy_mode": mode}
    for k, v in (overrides or {}).items():
        # tightening only: a caller may DISABLE telemetry/external calls or SHORTEN
        # retention, never enable/lengthen beyond the mode's ceiling (fail-closed).
        if k == "external_telemetry" and v and not base["external_telemetry"]:
            continue
        if k == "external_model_calls" and v and not base["external_model_calls"]:
            continue
        if k == "retention_days" and v > base["default_retention_days"]:
            v = base["default_retention_days"]
        cfg[k] = v
    cfg.setdefault("retention_days", base["default_retention_days"])
    cfg["_invariants_ok"] = _check(cfg)
    return cfg


def _check(cfg: Dict) -> bool:
    if cfg["deploy_mode"] in ("air-gapped", "on-prem", "edge"):
        if cfg.get("external_telemetry") or cfg.get("external_model_calls"):
            return False
    if cfg["deploy_mode"] == "edge" and cfg.get("model_location") not in ("edge", "cloud+edge"):
        return False
    return True


def validate(cfg: Dict) -> List[str]:
    errs = []
    if not _check(cfg):
        errs.append(f"invariant violation for {cfg['deploy_mode']}: external telemetry/model-calls must be off")
    if cfg.get("retention_days", 0) > DEPLOY_MODES[cfg["deploy_mode"]]["default_retention_days"]:
        errs.append("retention exceeds mode ceiling")
    return errs


def _selftest():
    cloud = profile("cloud"); ent = profile("enterprise"); indic = profile("indic")
    print("cloud     :", cloud["deploy_mode"], "telemetry", cloud["external_telemetry"], "retention", cloud["retention_days"])
    print("enterprise:", ent["deploy_mode"], "telemetry", ent["external_telemetry"], "multi_tenant", ent["multi_tenant"])
    print("indic     :", indic["deploy_mode"], "residency", indic.get("residency"), "indic_routing", indic["indic_routing"])
    # attempt to ILLEGALLY enable telemetry on enterprise (on-prem) → must be refused
    hardened = profile("enterprise", {"external_telemetry": True, "retention_days": 999})
    print("hardened  :", "telemetry", hardened["external_telemetry"], "retention", hardened["retention_days"], "ok", hardened["_invariants_ok"])
    assert cloud["_invariants_ok"] and ent["_invariants_ok"] and indic["_invariants_ok"]
    assert hardened["external_telemetry"] is False and hardened["retention_days"] <= 14
    assert indic.get("residency") == "India" and indic["indic_routing"] is True
    assert not validate(cloud) and not validate(ent)
    print("\n[selftest] PASS — product surfaces map to safe deploy modes; on-prem/air-gapped fail-closed on external telemetry.")


if __name__ == "__main__":
    _selftest()
