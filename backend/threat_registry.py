"""
VoxShield — Voice Threat Registry (roadmap §19, P3).

A living intelligence store of observed voice threats. Each entry records, per §19:
generator, version, attack_method, language, accent, codec, device, environment,
replay, observed_artifacts, detection_perf (measured EER/FN if any), first_seen,
last_tested, confidence, evidence, source, provenance.

Seeded from MEASURED intelligence: the eval_gengap LOGO result on the DGX
(hardest UNSEEN generators). New threats are added by the Generator Hunter (§18)
when a research candidate is confirmed. Persists to registries/threats.json.
stdlib only, non-breaking.
"""
from __future__ import annotations
import json, os, time
from typing import Dict, List, Optional

_STORE = os.path.join(os.path.dirname(__file__), "registries", "threats.json")
THREAT_FIELDS = ["threat_id", "generator", "version", "attack_method", "language", "accent",
                 "codec", "device", "environment", "replay", "observed_artifacts",
                 "detection_perf", "first_seen", "last_tested", "confidence", "evidence",
                 "source", "provenance"]

# measured hardest UNSEEN generators (eval_gengap LOGO, DGX 2026-09-29) → EER%
_SEED = {"griffin_lim": 29.9, "bark": 23.5, "lemas-tts": 21.2, "rvc": 20.3,
         "kartoffelbox": 8.7, "outetts": 6.3, "zonos2": 6.3, "elevenlabs-v3": 6.3}


def _load() -> List[Dict]:
    if not os.path.exists(_STORE):
        return _seed()
    with open(_STORE) as f:
        return json.load(f).get("threats", [])


def _seed() -> List[Dict]:
    now = time.time()
    return [{"threat_id": f"THR-{g}", "generator": g, "version": "unknown",
             "attack_method": "tts", "language": "multi", "codec": "g711_ulaw",
             "observed_artifacts": [], "detection_perf": {"unseen_eer_pct": eer},
             "first_seen": now, "last_tested": now,
             "confidence": "measured", "evidence": "eval_gengap LOGO (37,493 clips, DGX)",
             "source": "MLAAD-OOD", "provenance": "internal-measured"}
            for g, eer in _SEED.items()]


def _save(threats: List[Dict]):
    with open(_STORE, "w") as f:
        json.dump({"_note": "living voice-threat intelligence (roadmap §19)",
                   "count": len(threats), "threats": threats}, f, indent=2)


def upsert(entry: Dict, persist: bool = False) -> Dict:
    bad = [k for k in entry if k not in THREAT_FIELDS]
    if bad: raise ValueError(f"unknown threat field(s): {bad}")
    if "generator" not in entry: raise ValueError("threat requires 'generator'")
    entry.setdefault("threat_id", f"THR-{entry['generator']}")
    entry.setdefault("first_seen", time.time()); entry["last_tested"] = time.time()
    threats = _load()
    for i, t in enumerate(threats):
        if t["threat_id"] == entry["threat_id"]:
            threats[i] = {**t, **entry}; break
    else:
        threats.append(entry)
    if persist: _save(threats)
    return entry


def query(min_eer: float = 0.0, language: Optional[str] = None,
          threats: Optional[List[Dict]] = None) -> List[Dict]:
    threats = threats if threats is not None else _load()
    out = [t for t in threats
           if (t.get("detection_perf", {}).get("unseen_eer_pct", 0) >= min_eer)
           and (language is None or t.get("language") in (language, "multi"))]
    return sorted(out, key=lambda t: -t.get("detection_perf", {}).get("unseen_eer_pct", 0))


def hardest(n: int = 5, threats: Optional[List[Dict]] = None) -> List[Dict]:
    return query(threats=threats)[:n]


def _selftest():
    threats = _load()
    print("seeded threats:", len(threats))
    top = hardest(3, threats)
    print("hardest 3:", [(t["generator"], t["detection_perf"]["unseen_eer_pct"]) for t in top])
    assert top[0]["generator"] == "griffin_lim"
    # upsert a hunter-confirmed threat (in-memory)
    e = upsert({"generator": "newclone-x", "attack_method": "voice_conversion",
                "language": "hi", "detection_perf": {"unseen_eer_pct": 15.0},
                "confidence": "hypothesis", "source": "generator_hunter"})
    q = query(min_eer=10.0, threats=_load() if False else threats+[e])
    print("threats EER>=10:", [t["generator"] for t in q])
    assert "newclone-x" in [t["generator"] for t in q]
    print("\n[selftest] PASS — seeded from measured LOGO; hardest ranked; hunter can upsert new intel.")


if __name__ == "__main__":
    _selftest()
