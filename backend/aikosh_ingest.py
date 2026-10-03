"""
VoxShield — AIKosh (IndiaAI National AI Repository) ingest adapter (roadmap §38).

Two jobs:
  1. AIKOSH_ASSETS — a machine-readable, MCP-verified catalogue of the Indic datasets and
     models VoxShield pulls from AIKosh (ids/licences/access read from the platform
     2026-09-30). This is the single source of truth for §38 provenance.
  2. aikosh_ingest() — convert AIKosh records into canonical, consent/licence-gated
     samples via corpus_ingest.py, with a FAIL-CLOSED licence gate: permissive licences
     (CC-BY / CC0 / public-domain / MIT) are admitted; Non-Commercial / No-Derivatives /
     "Other" are held back for the research/eval track only.

Network calls (MCP JSON-RPC or the aikosh SDK) are optional and only used live; the
self-test is fully offline. stdlib only.
"""
from __future__ import annotations
from typing import Dict, List

import corpus_ingest
from corpus_ingest import ingest

AIKOSH_MCP_URL = "https://aikosh.indiaai.gov.in/aikoshmcp/mcp"

# ---------------------------------------------------------------------------
# MCP-verified catalogue (roadmap §38). access: HOSTED | REDIRECT | RESTRICTED
# ---------------------------------------------------------------
# helper ---------------------------------------------------------------
def _a(name, kind, aid, license, access, use, langs=""):
    return {"name": name, "kind": kind, "id": aid, "license": license,
            "access": access, "use": use, "languages": langs}


AIKOSH_ASSETS: List[Dict] = [
    # --- attack-generation models (VoiceStudio §4/§25) ---
    _a("Bhashini Fastspeech2 TTS", "model", "7677ccaf-c070-40b1-892d-1b564e2d824d", "MIT", "HOSTED", "attack_gen", "16 indic"),
    _a("AI4Bharat Indic-Parler-TTS", "model", "cd234a42-7ab9-44fe-afc3-eb58b675a9e3", "MIT", "REDIRECT", "attack_gen", "21 indic"),
    _a("AI4Bharat IndicF5", "model", "0be4d5ff-17cf-40ad-ac3c-43ec0b0a0724", "MIT", "REDIRECT", "attack_gen", "11 indic"),
    _a("BharatGen A2TTS (speaker-adaptive, Hindi)", "model", "838baccc-0b09-4e31-aa54-6862b973b1fa", "MIT", "HOSTED", "voice_clone", "hi"),
    _a("SpeechT5 voice conversion", "model", "92ae4761-46cc-4ca8-8809-0da7b412c0d9", "MIT", "REDIRECT", "voice_conversion", ""),
    _a("Sooktam2 (BharatGen)", "model", "b0af906c-7a7f-4e38-89fa-cd1d1b101556", "MIT", "REDIRECT", "attack_gen", "12 indic"),
    _a("Indic-Speak (Bodhan.AI)", "model", "c0e5c4f2-3270-4bf2-94d3-6e5b43f6fe24", "Other", "HOSTED", "attack_gen", "22 indic"),
    # --- detection-support models ---
    _a("IndicTrans2", "model", "6f174fcc-5470-42ff-aa38-fd0816731110", "MIT", "HOSTED", "nmt", "22 indic"),
    _a("IndicXlit", "model", "418f9c74-0e4a-4ba4-bb70-10faa1f4408f", "MIT", "HOSTED", "transliteration", "22 indic"),
    _a("IndicConformer-600M-Multi", "model", "8c4a77ae-cd9c-4d25-83bf-9a455ce73e98", "MIT", "REDIRECT", "asr", "22 indic"),
    _a("IndicWav2Vec (Hindi)", "model", "490137c0-1bd6-4606-b95b-573c3848c955", "MIT", "REDIRECT", "ssl_frontend", "hi"),
    _a("SPRING-INX data2vec AQC (Hindi)", "model", "f727e70c-8268-465a-a805-b80166674548", "MIT", "HOSTED", "asr", "hi"),
    _a("NE-LID", "model", "903578c4-2bd8-4e8a-b17c-036c10dea442", "Other", "REDIRECT", "lang_id", "northeast"),
    _a("COMI-LINGUA-LID", "model", "a3e7e3a9-cb31-468d-8bcd-b0c0ebb38fbc", "Other", "HOSTED", "lang_id", "hinglish"),
    # --- datasets ---
    _a("IndicSynth", "dataset", "02269826-db98-43f2-bb51-c3644ea801ec", "CC-BY-NC-4.0", "REDIRECT", "attack_eval", "12 indic"),
    _a("IndicVoices (AI4Bharat)", "dataset", "8853b359-5de0-4159-bee3-a03c94a71887", "CC-BY-4.0", "REDIRECT", "genuine", "22 indic"),
    _a("IndicVoices-R", "dataset", "bb368065-7ea7-422f-a7af-57666717ca44", "CC-BY-ND-4.0", "REDIRECT", "attack", "22 indic"),
    _a("Vaani (IISc/ARTPARK)", "dataset", "b6e2c424-6da5-4256-80be-6fc48147e7d5", "CC-BY-4.0", "REDIRECT", "genuine", "pan-india"),
    _a("Shrutilipi", "dataset", "6fd05842-9454-4aed-b283-ff6842dc731f", "CC-BY-4.0", "REDIRECT", "genuine", "12 indic"),
    _a("Gram Vaani Hindi ASR (telephony)", "dataset", "308f00aa-0e2e-4341-967c-40bf60ad63d2", "CC-BY-NC-4.0", "REDIRECT", "genuine_telephony", "hi"),
    _a("VCTK (accent + voice cloning)", "dataset", "b8fd001a-c12a-4365-b7f9-d1037150803f", "Other", "REDIRECT", "clone_source", "en"),
    _a("Common Voice", "dataset", "60bf61e1-84ea-4bd8-8f8f-4a289bb1e403", "CC0", "REDIRECT", "genuine", "multi"),
    _a("AMI Meeting Corpus", "dataset", "303b2d54-5656-4ef9-babe-6e152307ab7c", "Other", "REDIRECT", "conversational", "en"),
    _a("Dehwali Bhili Spontaneous Speech", "dataset", "69d3cd29-186a-4e8c-8a6a-1aebab01e56c", "CC-BY-4.0", "HOSTED", "genuine", "bhili"),
]

# licences that clear the commercial training corpus; everything else = research/eval only
PERMISSIVE = ("CC0", "CC-BY-4.0", "CC-BY-3.0", "PUBLIC-DOMAIN", "MIT")


def license_ok(license_str: str) -> bool:
    """Fail-closed: only clearly permissive licences are admitted to the corpus."""
    if not license_str:
        return False
    s = license_str.upper().replace(" ", "")
    if "NC" in s or "NON-COMMERCIAL" in s or "NONDERIV" in s or "NO-DERIV" in s or "ND-" in s:
        return False
    if s == "OTHER":
        return False
    return any(p in s for p in ("CC0", "CC-BY", "CCBY", "PUBLIC-DOMAIN", "PUBLICDOMAIN", "MIT"))


def classify_consent(license_str: str) -> str:
    return "public" if license_ok(license_str) else "research-only"


def asset(aid: str) -> Dict:
    for a in AIKOSH_ASSETS:
        if a["id"] == aid:
            return a
    raise KeyError(f"unknown AIKosh asset id: {aid}")


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------
def to_rows(records: List[Dict]) -> List[Dict]:
    """AIKosh sample record -> corpus_ingest 'aikosh' row (provenance/licence carried)."""
    rows = []
    for r in records:
        aid = r.get("dataset_id", "")
        lic = r.get("license", "")
        rows.append({
            "sample_id": r.get("sample_id"),
            "language": r.get("language"),
            "speaker_id": r.get("speaker_id"),
            "gender": r.get("gender"),
            "generator": r.get("generator", "none"),
            "attack_mode": r.get("attack_mode", "bonafide"),
            "label": r.get("label", "HUMAN"),
            "provenance": f"AIKosh/{aid}/{r.get('version', 'v1')}",
            "license": lic,
            "consent": classify_consent(lic),
        })
    return rows


def aikosh_ingest(records: List[Dict], split: str = "train", codec: str = "wideband") -> Dict:
    """Normalize + validate + consent-gate AIKosh samples via corpus_ingest.
    Non-permissive licences are recorded as 'held' (research/eval track), never admitted."""
    admitted, held, rejected = [], [], []
    for r in records:
        lic = r.get("license", "")
        if not license_ok(lic):
            held.append({"sample_id": r.get("sample_id"), "license": lic,
                         "reason": "non-permissive / unknown licence — research-only"})
            continue
        res = ingest([r], "aikosh", split=split, codec=codec)
        (admitted if res["n_accepted"] else rejected).extend(res["accepted"] or res["rejected"])
    return {"source": "aikosh", "admitted": admitted, "held_noncommercial": held,
            "rejected": rejected, "n_admitted": len(admitted),
            "n_held": len(held), "n_rejected": len(rejected)}


# ---------------------------------------------------------------------------
# live MCP client (optional; never used by self-test)
# ---------------------------------------------------------------------------
def mcp_call(method: str, params: Dict, api_key: str, _id: int = 1) -> Dict:
    import json, urllib.request
    body = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method, "params": params}).encode()
    req = urllib.request.Request(AIKOSH_MCP_URL, data=body, headers={
        "Authorization": "Bearer " + api_key, "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read().decode()
    for line in raw.splitlines():
        if line.startswith("data: "):
            ev = json.loads(line[6:])
            if ev.get("id") == _id:
                return ev
    return json.loads(raw)


def list_datasets(keyword: str, api_key: str, page: int = 1, page_size: int = 20) -> List[Dict]:
    r = mcp_call("tools/call", {"name": "list_datasets_tool",
                                "arguments": {"filters": {"keyword": keyword},
                                              "page": page, "page_size": page_size}}, api_key)
    return r.get("result", {}).get("structuredContent", {}).get("data", {}).get("data", []) \
        or _parse_text(r)


def _parse_text(r: Dict):
    import json
    for c in r.get("result", {}).get("content", []):
        if c.get("type") == "text":
            try:
                return json.loads(c["text"]).get("data", {}).get("data", [])
            except Exception:
                return []
    return []


# ---------------------------------------------------------------------------
def _selftest():
    import uuid
    # 1. catalogue integrity
    for a in AIKOSH_ASSETS:
        uuid.UUID(a["id"])                       # every id is a real uuid
        assert a["license"] and a["access"] and a["kind"] in ("model", "dataset")
    assert len(AIKOSH_ASSETS) == len({a["id"] for a in AIKOSH_ASSETS}), "duplicate asset id"
    print(f"catalogue: {len(AIKOSH_ASSETS)} verified assets "
          f"({sum(a['kind']=='model' for a in AIKOSH_ASSETS)} models, "
          f"{sum(a['kind']=='dataset' for a in AIKOSH_ASSETS)} datasets)")

    # 2. licence gate
    assert license_ok("CC-BY-4.0") and license_ok("CC0") and license_ok("MIT")
    assert not license_ok("CC-BY-NC-4.0") and not license_ok("CC-BY-ND-4.0") and not license_ok("Other")
    print("licence gate: permissive admitted, NC/ND/Other held ✓")

    # 3. end-to-end offline ingest through corpus_ingest
    recs = [
        {"sample_id": "aikosh-iv-1", "language": "hi", "speaker_id": "s1", "gender": "f",
         "dataset_id": asset("8853b359-5de0-4159-bee3-a03c94a71887")["id"], "license": "CC-BY-4.0"},
        {"sample_id": "aikosh-nc-1", "language": "hi", "dataset_id": "02269826-db98-43f2-bb51-c3644ea801ec",
         "license": "CC-BY-NC-4.0"},
    ]
    out = aikosh_ingest(to_rows(recs), split="test")
    assert out["n_admitted"] == 1 and out["n_held"] == 1, out
    s = out["admitted"][0]
    print("ingest:", out["n_admitted"], "admitted,", out["n_held"], "held (non-commercial),", out["n_rejected"], "rejected")
    print("  sample:", {k: s[k] for k in ("sample_id", "language", "label", "provenance", "license", "consent")})
    print("  held  :", out["held_noncommercial"][0]["reason"])


if __name__ == "__main__":
    _selftest()
