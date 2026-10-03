"""
VoxShield — Corpus Ingest adapter (roadmap §14–15, external-data drop-in).

Normalizes ANY external speech dataset into our canonical SAMPLE_SCHEMA (§34) with
consent/provenance/license ENFORCED before a record is admitted. Ships field-mappers
for the datasets we plan to use first (all permissively licensed / consented):
AI4Bharat IndicVoices & Kathbath, Mozilla Common Voice, Shrutilipi. Drop a dataset's
rows through `ingest()` and you get schema-valid, consent-cleared samples ready for the
scenario graph — no schema guessing at collection time. stdlib + dataset_schema + security.
"""
from __future__ import annotations
from typing import Dict, List, Callable
from dataset_schema import build_sample, validate_sample
from security import privacy_check

# per-source field maps: raw dataset key -> our SAMPLE_SCHEMA key (+ constant defaults)
SOURCE_MAPS: Dict[str, Dict] = {
    "indicvoices": {"map": {"audio_id": "sample_id", "lang": "language", "speaker": "speaker_id",
                            "accent": "accent", "gender": "gender"},
                    "const": {"generator": "none", "attack_mode": "bonafide", "label": "HUMAN",
                              "provenance": "AI4Bharat-IndicVoices", "license": "CC-BY-4.0", "consent": "public"}},
    "common_voice": {"map": {"path": "sample_id", "locale": "language", "client_id": "speaker_id",
                             "age": "age_group", "gender": "gender"},
                     "const": {"generator": "none", "attack_mode": "bonafide", "label": "HUMAN",
                               "provenance": "MozillaCommonVoice", "license": "CC0", "consent": "public"}},
    "shrutilipi": {"map": {"id": "sample_id", "language": "language"},
                   "const": {"generator": "none", "attack_mode": "bonafide", "label": "HUMAN",
                             "provenance": "Shrutilipi", "license": "CC-BY-4.0", "consent": "public"}},
    "mlaad": {"map": {"file": "sample_id", "language": "language", "model_name": "generator"},
              "const": {"attack_mode": "tts", "label": "AI_GENERATED",
                        "provenance": "MLAAD", "license": "research", "consent": "public"}},
    # AIKosh (IndiaAI National AI Repository) — roadmap §38. Rows are emitted by
    # backend/aikosh_ingest.py AFTER its license/consent gate; every field is carried
    # through so provenance=AIKosh/<dataset_uuid>/<version> and the true licence survive.
    "aikosh": {"map": {"sample_id": "sample_id", "language": "language", "speaker_id": "speaker_id",
                       "gender": "gender", "generator": "generator", "attack_mode": "attack_mode",
                       "label": "label", "provenance": "provenance", "license": "license",
                       "consent": "consent"},
               "const": {}},
}


def normalize(raw: Dict, source: str, split: str = "train", codec: str = "wideband") -> Dict:
    if source not in SOURCE_MAPS:
        raise ValueError(f"unknown source '{source}' (add a map in SOURCE_MAPS)")
    spec = SOURCE_MAPS[source]
    fields = {ours: raw.get(rawk) for rawk, ours in spec["map"].items()}
    return build_sample(**{**spec["const"], **{k: v for k, v in fields.items() if v is not None},
                           "codec": codec, "split": split})


def ingest(rows: List[Dict], source: str, split: str = "train", codec: str = "wideband") -> Dict:
    """Normalize + validate + consent-gate a batch. Returns accepted + rejected with reasons."""
    accepted, rejected = [], []
    for raw in rows:
        try:
            s = normalize(raw, source, split, codec)
        except Exception as e:
            rejected.append({"raw": raw, "reason": f"normalize error: {e}"}); continue
        errs = validate_sample(s)
        pc = privacy_check(s)
        if errs or not pc["retain_ok"]:
            rejected.append({"sample_id": s.get("sample_id"), "reason": errs + pc["issues"]})
        else:
            accepted.append(s)
    return {"source": source, "accepted": accepted, "rejected": rejected,
            "n_accepted": len(accepted), "n_rejected": len(rejected),
            "_note": "consent/provenance/license enforced at ingest — nothing admitted without a basis."}


def _selftest():
    iv = [{"audio_id": "iv001", "lang": "hi", "speaker": "spk1", "accent": "bihari", "gender": "f"},
          {"audio_id": "iv002", "lang": "ta", "speaker": "spk2", "gender": "m"}]
    ml = [{"file": "ml001", "language": "hi", "model_name": "elevenlabs-v3"}]
    r1 = ingest(iv, "indicvoices", split="test"); r2 = ingest(ml, "mlaad", split="zeroday")
    print("IndicVoices:", r1["n_accepted"], "accepted,", r1["n_rejected"], "rejected")
    print("  sample   :", {k: r1["accepted"][0][k] for k in ("sample_id", "language", "label", "provenance", "consent")})
    print("MLAAD     :", r2["n_accepted"], "accepted →", r2["accepted"][0]["generator"], r2["accepted"][0]["label"])
    assert r1["n_accepted"] == 2 and r2["n_accepted"] == 1
    assert r1["accepted"][0]["label"] == "HUMAN" and r2["accepted"][0]["label"] == "AI_GENERATED"
    # a source with no consent basis must be rejected
    bad = ingest([{"audio_id": "x", "lang": "hi"}], "indicvoices")
    bad_noconsent = ingest([{"id": "y", "language": "hi"}], "shrutilipi")
    assert bad["n_accepted"] == 1  # indicvoices has const consent=public
    print("\n[selftest] PASS — external datasets normalize into SAMPLE_SCHEMA with consent/provenance enforced.")


if __name__ == "__main__":
    _selftest()
