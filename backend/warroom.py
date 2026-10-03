"""
VoxShield — War Room / live operations rollup (roadmap §28, P3).

Aggregates the stream of per-call results (the app.py AUDIT log, or any list of
verdict events) into the operational picture an analyst desk watches: volume,
flag-rate, abstain-rate, per-language/region breakdown, top active threats, and a
drift signal vs a baseline window. Read-only situational awareness — it decides
nothing (decisions live in the gateway/callguard). stdlib + drift.py + threat_registry.
"""
from __future__ import annotations
from typing import Dict, List, Optional
from collections import Counter
import threat_registry


def _rate(events, pred):
    return round(sum(1 for e in events if pred(e))/len(events), 3) if events else 0.0


def rollup(events: List[Dict], baseline: Optional[Dict] = None) -> Dict:
    """events: [{verdict|label, abstain?, language?, region?, score?, latency_s?}]"""
    n = len(events)
    if n == 0:
        return {"volume": 0, "note": "no events"}
    def verdict(e): return (e.get("verdict") or e.get("label") or "").upper()
    flagged = _rate(events, lambda e: verdict(e) in ("AI", "SYNTHETIC", "HIGH", "FLAGGED"))
    abstained = _rate(events, lambda e: e.get("abstain") or verdict(e) in ("UNKNOWN", "REVIEW"))
    langs = Counter(e.get("language") for e in events if e.get("language"))
    regions = Counter(e.get("region") for e in events if e.get("region"))
    lat = [e["latency_s"] for e in events if e.get("latency_s") is not None]

    out = {"volume": n, "flag_rate": flagged, "abstain_rate": abstained,
           "top_languages": langs.most_common(5), "top_regions": regions.most_common(5),
           "p50_latency_s": round(sorted(lat)[len(lat)//2], 3) if lat else None,
           "active_threats": [{"generator": t["generator"],
                               "unseen_eer_pct": (t.get("detection_perf") or {}).get("unseen_eer_pct")}
                              for t in threat_registry.hardest(5)]}

    # drift vs a baseline window (flag/abstain rate + volume), if provided
    if baseline:
        from drift import monitor
        window = {"fpr": flagged, "fnr": abstained,
                  "data": [e.get("score", 0.5) for e in events]}
        try:
            out["drift"] = monitor(baseline, window)
        except Exception as e:
            out["drift"] = {"error": str(e)[:80]}
    # cheap alerting thresholds (advisory only)
    alerts = []
    if flagged > 0.5: alerts.append("HIGH flag-rate — possible coordinated attack or model regression")
    if abstained > 0.4: alerts.append("HIGH abstain-rate — many unknowns, likely unseen generator surge")
    out["alerts"] = alerts
    out["_status"] = "read-only situational awareness; decides nothing."
    return out


def _selftest():
    events = ([{"verdict": "AI", "language": "Hindi", "region": "Delhi", "score": 0.9, "latency_s": 0.4}]*4 +
              [{"verdict": "UNKNOWN", "abstain": True, "language": "Tamil", "region": "Chennai", "score": 0.6}]*3 +
              [{"verdict": "HUMAN", "language": "Hindi", "region": "Mumbai", "score": 0.1, "latency_s": 0.3}]*3)
    r = rollup(events, baseline={"fpr": 0.1, "fnr": 0.1, "data": [0.1]*10})
    print("volume", r["volume"], "| flag_rate", r["flag_rate"], "| abstain_rate", r["abstain_rate"])
    print("top languages:", r["top_languages"])
    print("active threats:", [t["generator"] for t in r["active_threats"]][:3])
    print("alerts:", r["alerts"])
    assert r["volume"] == 10 and r["flag_rate"] == 0.4 and r["abstain_rate"] == 0.3
    assert r["top_languages"][0][0] == "Hindi"
    assert len(r["active_threats"]) == 5
    print("\n[selftest] PASS — rollup computes flag/abstain rates, language/region mix, active threats + alerts.")


if __name__ == "__main__":
    _selftest()
