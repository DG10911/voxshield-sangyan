"""
VoxShield — Master Dataset scenario-graph schema + Worst-AI manifest (roadmap §14,§16,§34).

The dataset is a SCENARIO GRAPH, not real/ + fake/ folders. This module defines the
canonical per-sample metadata schema, validates records, references the registries
(§4–6), and builds the Worst-AI challenge manifest seeded from measured hardest
generators (the eval_gengap LOGO result). stdlib only.
"""
from __future__ import annotations
from typing import Dict, List

SAMPLE_SCHEMA = [
    "sample_id", "speaker_id", "language", "accent", "gender", "age_group",
    "generator", "generator_version", "voice_id", "attack_mode",
    "device", "microphone", "environment", "distance", "codec", "sample_rate",
    "network_condition", "noise_condition", "style", "emotion", "replay", "splice",
    "attack_type", "label", "label_confidence", "provenance", "license", "consent",
    "split", "timestamp",
]
REQUIRED = ["sample_id", "language", "generator", "attack_mode", "codec", "label",
            "provenance", "license", "consent", "split"]
VALID_LABELS = {"HUMAN", "AI_GENERATED", "VOICE_CONVERSION", "TTS", "CLONED",
                "REPLAY_HUMAN", "REPLAY_AI", "AI_AGENT", "BOT", "HYBRID", "SPLICED", "UNKNOWN"}
VALID_SPLITS = {"train", "val", "test", "golden", "zeroday"}


def validate_sample(s: Dict) -> List[str]:
    errs = []
    for k in REQUIRED:
        if k not in s or s[k] in (None, ""):
            errs.append(f"missing required '{k}'")
    for k in s:
        if k not in SAMPLE_SCHEMA:
            errs.append(f"unknown field '{k}'")
    if s.get("label") and s["label"] not in VALID_LABELS:
        errs.append(f"invalid label '{s['label']}'")
    if s.get("split") and s["split"] not in VALID_SPLITS:
        errs.append(f"invalid split '{s['split']}'")
    return errs


def build_sample(**kw) -> Dict:
    s = {k: kw.get(k) for k in SAMPLE_SCHEMA}
    s.setdefault("label_confidence", 1.0)
    return s


# measured hardest UNSEEN generators (eval_gengap LOGO on DGX, 2026-09-29): EER%
HARDEST_UNSEEN = {"griffin_lim": 29.9, "bark": 23.5, "lemas-tts": 21.2, "rvc": 20.3,
                  "kartoffelbox": 8.7, "outetts": 6.3, "zonos2": 6.3, "elevenlabs-v3": 6.3}


def worst_ai_manifest() -> Dict:
    """Seed the Worst-AI challenge suite from the measured hardest generators —
    these are where the model is weakest and must be attacked/trained first."""
    entries = []
    for gen, eer in sorted(HARDEST_UNSEEN.items(), key=lambda x: -x[1]):
        entries.append({"sample_id": f"worstai-{gen}", "generator": gen, "attack_mode": "tts",
                        "measured_eer_pct": eer, "priority": "high" if eer >= 15 else "medium",
                        "label": "AI_GENERATED", "split": "zeroday",
                        "language": "multi", "codec": "g711_ulaw",
                        "provenance": "MLAAD", "license": "research", "consent": "public"})
    return {"name": "voxshield-worst-ai", "never_train": True,
            "note": "Hardest UNSEEN generators from measured LOGO — priority targets for Generator Hunter (§18) & training curriculum.",
            "entries": entries}


WORST_HUMAN_SLICES = ["strong_accent", "rare_pronunciation", "stutter", "breathy",
                      "hoarse", "emotional", "elderly", "young", "poor_microphone",
                      "heavy_noise", "speakerphone", "code_switch", "whisper", "shout"]


def worst_human_manifest() -> Dict:
    """The difficult GENUINE-human suite — the point is to MINIMISE false positives.
    Unusual humans must never be classified as synthetic (roadmap §16/§43)."""
    return {"name": "voxshield-worst-human", "never_train": True,
            "note": "Hardest genuine humans — measure & minimise FALSE POSITIVES. Unusual human != AI.",
            "entries": [{"sample_id": f"worsthuman-{s}", "slice": s, "label": "HUMAN",
                         "language": "multi", "codec": "g711_ulaw",
                         "provenance": "collection-TODO", "license": "consented", "consent": True,
                         "split": "golden"} for s in WORST_HUMAN_SLICES]}


def nightmare_manifest() -> Dict:
    """The combinatorial worst-case suite (roadmap §32) — unknown generator + Indian
    accent + low-resource language + G.711 + noise + replay + speakerphone + emotion
    + code-switch + partial splice + unknown device."""
    dims = {"generator": "unknown", "accent": "rural-indian", "language": "low-resource-indic",
            "codec": "g711_ulaw", "noise": "heavy", "replay": "speakerphone", "emotion": "distressed",
            "manipulation": "code_switch+partial_splice", "device": "unknown-feature-phone"}
    return {"name": "voxshield-nightmare", "never_train": True,
            "note": "Hardest combinatorial scenario — the ultimate stress test (roadmap §32).",
            "dimensions": dims,
            "entries": [{"sample_id": f"nightmare-{i:03d}", "slice": "compositional",
                         "label": "UNKNOWN", "attack_mode": "cross_lingual", "split": "zeroday",
                         "provenance": "scenario-generator", "license": "research", "consent": "internal-generated",
                         **{k: v for k, v in dims.items()}} for i in range(3)]}


def _selftest():
    good = build_sample(sample_id="s1", language="hi", generator="freevc24", attack_mode="tts",
                        codec="g711_ulaw", label="TTS", provenance="IndicSynth", license="research",
                        consent="public", split="test")
    e = validate_sample(good); print("valid sample errors:", e); assert not e

    bad = {"sample_id": "s2", "label": "MAGIC", "split": "prod", "weird": 1}
    be = validate_sample(bad)
    print("bad sample flags:", len(be), "errors (missing required + bad label/split + unknown field)")
    assert any("invalid label" in x for x in be) and any("unknown field" in x for x in be)

    wa = worst_ai_manifest()
    print("Worst-AI top targets:", [(x["generator"], x["measured_eer_pct"]) for x in wa["entries"][:4]])
    assert wa["never_train"] and wa["entries"][0]["generator"] == "griffin_lim"
    wh = worst_human_manifest(); nm = nightmare_manifest()
    print("Worst-Human slices  :", len(wh["entries"]), "· Nightmare dims:", len(nm["dimensions"]))
    assert wh["never_train"] and all(e["label"] == "HUMAN" for e in wh["entries"])
    assert nm["never_train"] and nm["entries"][0]["label"] == "UNKNOWN"
    print("\n[selftest] PASS — schema validates; Worst-AI/Worst-Human/Nightmare manifests built.")


if __name__ == "__main__":
    _selftest()
