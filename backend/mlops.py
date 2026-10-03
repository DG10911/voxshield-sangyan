"""
VoxShield — MLOps registry (roadmap §24, §67).

Every production model must be REPRODUCIBLE and REVERSIBLE. This registry enforces
that each registered model carries: version · dataset_version · training_config ·
metrics · checkpoint_hash · provenance — and supports promote (to shadow/production)
and rollback. It refuses to register a model missing reproducibility fields, and
refuses to promote a model that hasn't passed shadow. stdlib only.
"""
from __future__ import annotations
import time
from typing import Dict, List, Optional

REQUIRED = ["model_id", "version", "dataset_version", "training_config",
            "metrics", "checkpoint_hash", "provenance"]
STATES = ["registered", "shadow", "production", "rolled_back"]


class ModelRegistry:
    def __init__(self):
        self.models: List[Dict] = []
        self._prod: Optional[str] = None       # "model_id@version" currently in production

    def register(self, **m) -> Dict:
        missing = [k for k in REQUIRED if k not in m or m[k] in (None, "")]
        if missing:
            return {"ok": False, "reason": f"missing reproducibility fields: {missing}"}
        rec = {**m, "key": f"{m['model_id']}@{m['version']}", "state": "registered",
               "registered_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        self.models.append(rec)
        return {"ok": True, "key": rec["key"], "state": rec["state"]}

    def _get(self, key): return next((r for r in self.models if r["key"] == key), None)

    def promote(self, key: str, to: str) -> Dict:
        r = self._get(key)
        if not r: return {"ok": False, "reason": "unknown model"}
        if to == "production" and r["state"] != "shadow":
            return {"ok": False, "reason": "must pass 'shadow' before 'production' (governance)"}
        if to not in STATES: return {"ok": False, "reason": f"bad state '{to}'"}
        r["state"] = to
        if to == "production":
            if self._prod: self._get(self._prod)["state"] = "rolled_back"   # demote previous
            self._prod = key
        return {"ok": True, "key": key, "state": to, "production": self._prod}

    def rollback(self) -> Dict:
        """Revert production to the most recent prior production model."""
        if not self._prod: return {"ok": False, "reason": "nothing in production"}
        self._get(self._prod)["state"] = "rolled_back"
        prev = [r for r in self.models if r["state"] == "rolled_back" and r["key"] != self._prod]
        target = prev[-1] if prev else None
        if target:
            target["state"] = "production"; self._prod = target["key"]
            return {"ok": True, "rolled_back_to": target["key"]}
        self._prod = None
        return {"ok": True, "rolled_back_to": None, "note": "no prior production; production now empty"}

    def reproducibility(self, key: str) -> Dict:
        r = self._get(key)
        return {k: r.get(k) for k in REQUIRED} if r else {}


def _selftest():
    reg = ModelRegistry()
    base = dict(model_id="xlsr-fusion", dataset_version="voxdata-2026.09",
                training_config={"bs": 20, "lr": 5e-5, "epochs": 3}, provenance="DGX srmist2")
    r1 = reg.register(version="1.0", metrics={"eer": 0.059, "ood_eer": 0.066},
                      checkpoint_hash="abc123", **base)
    bad = reg.register(version="bad", model_id="x", dataset_version="d",
                       training_config={}, provenance="p")   # missing metrics + checkpoint_hash
    print("register v1.0:", r1)
    print("register bad :", bad["ok"], "-", bad["reason"])
    assert r1["ok"] and not bad["ok"]
    # cannot jump straight to production
    direct = reg.promote("xlsr-fusion@1.0", "production")
    print("direct->prod :", direct["ok"], "-", direct["reason"])
    assert not direct["ok"]
    reg.promote("xlsr-fusion@1.0", "shadow"); ok = reg.promote("xlsr-fusion@1.0", "production")
    print("shadow->prod :", ok)
    assert ok["ok"] and reg._prod == "xlsr-fusion@1.0"
    # register + promote v2, then rollback
    reg.register(version="2.0", metrics={"eer": 0.071}, checkpoint_hash="def456", **base)
    reg.promote("xlsr-fusion@2.0", "shadow"); reg.promote("xlsr-fusion@2.0", "production")
    rb = reg.rollback()
    print("rollback     :", rb)
    assert rb["ok"] and rb["rolled_back_to"] == "xlsr-fusion@1.0"
    print("\n[selftest] PASS — reproducibility enforced; no shadow-skip to prod; rollback restores prior model.")


if __name__ == "__main__":
    _selftest()
