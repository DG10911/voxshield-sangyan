"""
VoxShield — Drift Monitoring (roadmap §24, §77).

Watches for the drifts that silently degrade a deployed detector:
    data drift      — score/feature distribution shift (PSI)
    error drift      — FPR / FNR moving vs baseline
    latency drift    — inference slowing down
    (generator/language/channel drift are data-drift on the respective slice)

Given a frozen BASELINE and a recent WINDOW of production observations, it flags
each drift with a severity. Pure measurement; stdlib + numpy.
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict, Optional


def psi(baseline: List[float], window: List[float], bins: int = 10) -> float:
    """Population Stability Index between two score distributions."""
    b = np.asarray(baseline); w = np.asarray(window)
    if len(b) == 0 or len(w) == 0:
        return 0.0
    edges = np.linspace(0, 1, bins + 1)
    pb = np.histogram(np.clip(b, 0, 1), edges)[0] / len(b) + 1e-6
    pw = np.histogram(np.clip(w, 0, 1), edges)[0] / len(w) + 1e-6
    return float(np.sum((pw - pb) * np.log(pw / pb)))


def _sev(x, lo, hi):
    return "OK" if x < lo else ("WARN" if x < hi else "ALERT")


def monitor(baseline: Dict, window: Dict) -> dict:
    """baseline/window dicts may carry: scores[list], fpr, fnr, latency_ms[list]."""
    out = {}
    if baseline.get("scores") and window.get("scores"):
        p = psi(baseline["scores"], window["scores"])
        out["data_drift"] = {"psi": round(p, 4), "severity": _sev(p, 0.1, 0.25)}
    if baseline.get("fpr") is not None and window.get("fpr") is not None:
        d = window["fpr"] - baseline["fpr"]
        out["fpr_drift"] = {"delta": round(d, 4), "severity": _sev(abs(d), 0.03, 0.08)}
    if baseline.get("fnr") is not None and window.get("fnr") is not None:
        d = window["fnr"] - baseline["fnr"]
        out["fnr_drift"] = {"delta": round(d, 4), "severity": _sev(abs(d), 0.03, 0.08)}
    if baseline.get("latency_ms") and window.get("latency_ms"):
        b = float(np.median(baseline["latency_ms"])); w = float(np.median(window["latency_ms"]))
        r = (w - b) / (b + 1e-9)
        out["latency_drift"] = {"baseline_ms": round(b, 1), "window_ms": round(w, 1),
                                "rel_change": round(r, 3), "severity": _sev(abs(r), 0.25, 0.75)}
    sev_order = {"OK": 0, "WARN": 1, "ALERT": 2}
    worst = max((v["severity"] for v in out.values()), key=lambda s: sev_order[s], default="OK")
    out["overall"] = worst
    return out


def _selftest():
    rng = np.random.default_rng(0)
    base = {"scores": list(rng.normal(0.2, 0.1, 2000).clip(0, 1)), "fpr": 0.06, "fnr": 0.05,
            "latency_ms": list(rng.normal(90, 10, 200))}
    stable = {"scores": list(rng.normal(0.21, 0.1, 2000).clip(0, 1)), "fpr": 0.065, "fnr": 0.05,
              "latency_ms": list(rng.normal(92, 10, 200))}
    drifted = {"scores": list(rng.normal(0.5, 0.2, 2000).clip(0, 1)), "fpr": 0.18, "fnr": 0.05,
               "latency_ms": list(rng.normal(200, 20, 200))}
    s = monitor(base, stable); d = monitor(base, drifted)
    print("STABLE :", s["overall"], {k: v.get("severity") for k, v in s.items() if isinstance(v, dict)})
    print("DRIFTED:", d["overall"], {k: v.get("severity") for k, v in d.items() if isinstance(v, dict)})
    assert s["overall"] == "OK" and d["overall"] == "ALERT"
    print("\n[selftest] PASS — stable window OK; shifted distribution + rising FPR + slow latency -> ALERT.")


if __name__ == "__main__":
    _selftest()
