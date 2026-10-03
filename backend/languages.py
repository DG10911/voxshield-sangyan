"""
VoxShield — Language Mastery Scorecard (roadmap §15, §37.6).

Reads registries/languages.json and reports how close we are to being "master" of every
Indian language. Mastery is EARNED, not assumed: a language counts as mastered only when
`detection_tested=True` (VoxShield's detector validated on that language's deepfakes +
genuine speech) — having data/generators is necessary but NOT sufficient.

Use it to track progress each GPU training run:
    python3 languages.py                 # print the scorecard
    from languages import scorecard       # {tested, total, pending:[...], ...}
    mark_tested("hi", True)               # flip a language once its EER is validated
stdlib only, non-breaking.
"""
from __future__ import annotations
import json, os
from typing import Dict, List

_PATH = os.path.join(os.path.dirname(__file__), "registries", "languages.json")


def _load() -> Dict:
    with open(_PATH) as f:
        return json.load(f)


def scorecard() -> Dict:
    d = _load(); langs = d["languages"]; n = len(langs)
    def cnt(flag): return sum(1 for l in langs if l.get(flag))
    tested = [l for l in langs if l.get("detection_tested")]
    pending = [l for l in langs if not l.get("detection_tested")]
    # "ready to test" = has genuine data + at least one generator, just not validated yet
    ready = [l for l in pending if l.get("genuine_data") and (l.get("clone_generator") or l.get("tts_generator"))]
    by_family: Dict[str, Dict[str, int]] = {}
    for l in langs:
        f = by_family.setdefault(l["family"], {"total": 0, "tested": 0})
        f["total"] += 1; f["tested"] += 1 if l.get("detection_tested") else 0
    return {
        "total": n,
        "detection_tested": len(tested),
        "mastery_pct": round(100 * len(tested) / n, 1),
        "coverage": {"genuine_data": cnt("genuine_data"), "clone_generator": cnt("clone_generator"),
                     "tts_generator": cnt("tts_generator"), "detection_tested": len(tested)},
        "mastered": [l["code"] for l in tested],
        "ready_to_test": [l["code"] for l in ready],
        "pending": [l["code"] for l in pending],
        "by_family": by_family,
    }


def mark_tested(code: str, value: bool = True) -> Dict:
    """Flip a language's detection_tested flag (call after its EER is validated on real data)."""
    d = _load(); found = False
    for l in d["languages"]:
        if l["code"] == code:
            l["detection_tested"] = value
            l["mastery"] = "MASTERED (detection validated)" if value else "detection UNVERIFIED"
            found = True; break
    if not found:
        raise KeyError(f"language '{code}' not in registry")
    with open(_PATH, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    return scorecard()


def render(sc: Dict | None = None) -> str:
    sc = sc or scorecard()
    bar_n = 24; filled = round(bar_n * sc["mastery_pct"] / 100)
    bar = "█" * filled + "░" * (bar_n - filled)
    lines = [
        "╔═══ VoxShield · Indian-Language Mastery Scorecard ═══╗",
        f"  Mastery: {bar} {sc['mastery_pct']}%  ({sc['detection_tested']}/{sc['total']} detection-tested)",
        "  Pipeline readiness:",
        f"    genuine data     {sc['coverage']['genuine_data']}/{sc['total']}",
        f"    clone generator  {sc['coverage']['clone_generator']}/{sc['total']}",
        f"    tts generator    {sc['coverage']['tts_generator']}/{sc['total']}",
        f"    DETECTION TESTED {sc['coverage']['detection_tested']}/{sc['total']}   ← the one that = mastery",
        "  By family (tested/total): " + " · ".join(f"{k} {v['tested']}/{v['total']}" for k, v in sc["by_family"].items()),
        f"  ✅ mastered: {', '.join(sc['mastered']) or '(none yet)'}",
        f"  🟡 ready to test (need GPU run): {', '.join(sc['ready_to_test'])}",
        "╚" + "═" * 52 + "╝",
    ]
    return "\n".join(lines)


def _selftest():
    sc = scorecard()
    print(render(sc))
    assert sc["total"] >= 22 and 0 <= sc["mastery_pct"] <= 100
    assert set(sc["mastered"]) | set(sc["pending"]) == set(l["code"] for l in _load()["languages"])
    assert sc["coverage"]["genuine_data"] >= sc["detection_tested"]   # data is a prerequisite
    print("\n[selftest] PASS — scorecard reads registry; mastery = detection_tested; mark_tested() flips per language.")


if __name__ == "__main__":
    _selftest()
