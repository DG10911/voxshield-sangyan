"""
VoxShield — Golden Set & Zero-Day Set contract + validator (roadmap §16, §21, §70–71).

The Golden Set is PERMANENTLY FROZEN and NEVER trained on; every model release is
scored against it. The Zero-Day Set is continuously refreshed with held-out
generators/languages/attacks and also never trained on. This module defines the
manifest contract and validates that a manifest:
  * carries `never_train: true`
  * covers every REQUIRED slice (so we don't accidentally ship a blind spot)
  * has provenance + license + consent on every entry (roadmap governance rule)

It does not move audio; it governs the metadata. Dependency-free (stdlib json).
"""
from __future__ import annotations
import json, os
from typing import List

# every Golden Set must exercise these slices (roadmap §16) so a release can never
# pass while blind to, e.g., unknown generators or difficult humans.
GOLDEN_REQUIRED_SLICES = [
    "human", "ai", "unknown", "replay", "multilingual", "telephony",
    "difficult_human", "difficult_ai", "edge_case",
]
ZERODAY_REQUIRED_SLICES = [
    "new_generator", "new_language", "new_codec", "new_device",
    "new_environment", "new_attack", "compositional",
]
ENTRY_REQUIRED = ["sample_id", "slice", "label", "provenance", "license", "consent"]
VALID_LABELS = {"HUMAN", "AI_GENERATED", "VOICE_CONVERSION", "TTS", "CLONED",
                "REPLAY_HUMAN", "REPLAY_AI", "AI_AGENT", "BOT", "HYBRID", "SPLICED", "UNKNOWN"}


def validate_manifest(doc: dict, kind: str = "golden") -> List[str]:
    required_slices = GOLDEN_REQUIRED_SLICES if kind == "golden" else ZERODAY_REQUIRED_SLICES
    errs: List[str] = []
    if doc.get("never_train") is not True:
        errs.append(f"{kind}: manifest must set never_train:true (frozen set)")
    entries = doc.get("entries", [])
    present = {e.get("slice") for e in entries}
    for s in required_slices:
        if s not in present:
            errs.append(f"{kind}: REQUIRED slice '{s}' not covered")
    for i, e in enumerate(entries):
        for k in ENTRY_REQUIRED:
            if k not in e or e[k] in (None, ""):
                errs.append(f"{kind} entry[{i}] missing '{k}'")
        if e.get("label") and e["label"] not in VALID_LABELS:
            errs.append(f"{kind} entry[{i}] invalid label '{e['label']}'")
        if e.get("consent") not in (True, "public", "licensed", "internal-generated"):
            errs.append(f"{kind} entry[{i}] consent must be one of true/public/licensed/internal-generated")
    return errs


def new_template(kind: str = "golden") -> dict:
    slices = GOLDEN_REQUIRED_SLICES if kind == "golden" else ZERODAY_REQUIRED_SLICES
    return {"name": f"voxshield-{kind}-set", "kind": kind, "never_train": True,
            "version": "0.1.0", "created": None, "note": "FROZEN — never used for training.",
            "entries": [{"sample_id": f"{kind}-{s}-000", "slice": s, "label": "UNKNOWN",
                         "provenance": "TODO", "license": "TODO", "consent": "internal-generated"}
                        for s in slices]}


def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _selftest():
    # a well-formed golden manifest (one entry per required slice)
    g = new_template("golden")
    for e in g["entries"]:
        e["label"] = {"human": "HUMAN", "ai": "AI_GENERATED", "unknown": "UNKNOWN",
                      "replay": "REPLAY_AI", "multilingual": "TTS", "telephony": "AI_GENERATED",
                      "difficult_human": "HUMAN", "difficult_ai": "CLONED", "edge_case": "HYBRID"}[e["slice"]]
        e["provenance"] = "internal-lab"; e["license"] = "internal"
    errs = validate_manifest(g, "golden")
    print("well-formed golden manifest errors:", errs)
    assert not errs, errs

    # a broken one: missing 'unknown' slice + not frozen
    bad = {"kind": "golden", "never_train": False,
           "entries": [{"sample_id": "x", "slice": "human", "label": "HUMAN",
                        "provenance": "p", "license": "l", "consent": True}]}
    berrs = validate_manifest(bad, "golden")
    print("broken manifest correctly flags:", len(berrs), "errors (never_train + missing slices)")
    assert any("never_train" in e for e in berrs) and any("REQUIRED slice" in e for e in berrs)

    z = new_template("zeroday")
    print("zero-day template slices:", [e["slice"] for e in z["entries"]])
    print("\n[selftest] PASS — Golden/Zero-Day contract enforces frozen + full-slice coverage + provenance/consent.")


if __name__ == "__main__":
    _selftest()
