"""
VoxShield — BHASHINI / ULCA live adapter (roadmap §27, upgraded).

Real ULCA flow: Pipeline Config (userID + ulcaApiKey) -> serviceId/modelId + inference
endpoint + inferenceApiKey -> Pipeline Compute (Authorization: <inferenceApiKey>).

Used by VoxShield for: audio/text language routing (ALD/TLD), transcription evidence
(ASR -> Conversational/Semantic-Prosody brain), speaker verify/diarization, cross-lingual
attack text (NMT/transliteration), and Worst-AI generation (TTS/voice-cloning).

Modes:
  * MOCK (default, no keys) — deterministic placeholders so tests/pipeline run offline.
  * LIVE — set BHASHINI_USER_ID + BHASHINI_API_KEY (ULCA "My Profile"). Optional:
    BHASHINI_PIPELINE_ID (default = public "Initial Pipeline" id).

Credential note: ULCA API usage is PoC-only; production needs a Bhashini paid plan.
Detector caveat: Indic ASR/TTS coverage != Indic deepfake-detection coverage. stdlib only.
"""
from __future__ import annotations
import os, json, base64, hashlib, time
from typing import Dict, List, Optional

CONFIG_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
INFER_URL_DEFAULT = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
PIPELINE_ID = os.environ.get("BHASHINI_PIPELINE_ID", "64392f96daac500b55c543cd")
# If you already have the app's inference key, you can skip the config call entirely:
DIRECT_INFER_KEY = os.environ.get("BHASHINI_INFERENCE_KEY")          # Udyat "Inference" key
DIRECT_INFER_URL = os.environ.get("BHASHINI_INFER_URL", INFER_URL_DEFAULT)

# --- Service-ID catalogue (from AIKosh-independent Bhashini docs, 2026-10) ---
SERVICE_IDS: Dict[str, Dict[str, str]] = {
    "asr": {
        "dravidian_iitm": "bhashini/iitm/asr-dravidian--gpu--t4",
        "hindi_ai4b": "ai4bharat/conformer-hi-gpu--t4",
        "multilingual_ai4b": "bhashini/ai4bharat/conformer-multilingual-asr",   # all 22
        "indoaryan_iitm": "bhashini/iitm/asr-indoaryan--gpu--t4",
        "misc_iitm": "bhashini/iitm/asr-misc--gpu--t4",
        "mai_iisc": "bhashini/iisc/asr-mai-t4",
        "bho_iisc": "bhashini/iisc/asr-bho-t4",
        "transcribe_flex": "bhashini/bodhan/asr-transcribe-flex",               # 27 langs
        "transcribe_core": "bhashini/bodhan/asr-transcribe-core",
    },
    "translation": {
        "nmt_all_iiith": "bhashini/iiith/nmt-all",
        "indictrans_v2": "ai4bharat/indictrans-v2-all-gpu--t4",
        "indictrans_v4": "bhashini/bodhan/Indic-trans-v4",
        "iitb_trilingual": "iitb/trilingual-en_hi_mr-v1-gpu--t4",
    },
    "transliteration": {"indicxlit": "ai4bharat/indicxlit--cpu-fsv2"},
    "tts": {
        "iitm": "Bhashini/IITM/TTS",                                            # 25 langs
        "coqui_dravidian": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4",
        "coqui_indoaryan": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
        "coqui_misc": "ai4bharat/indic-tts-coqui-misc-gpu--t4",
        "iisc_syspin": "Bhashini/IISC/TTS",
        "bodhan": "bhashini/bodhan/indic-tts",
    },
    "ald": {  # audio language detection
        "iitmandi": "bhashini/iitmandi/audio-lang-detection/gpu",
        "ald": "bhashini/ald",
    },
    "tld": {  # text language detection
        "ai4b_all": "bhashini/indic-lang-detection-all",
        "iiith_all": "bhashini/iiiith/indic-lang-detection-all",
        "indic_tld": "bhashini/indic/tld",
    },
    "ner": {
        "iiith": "bhashini/iiith/ner",
        "ai4b": "bhashini/ai4bharat/indic-ner",
        "aukbc": "bhashini/aukbc/ner",
    },
    "speaker_enrollment": {"iitdharwad": "bhashini/iitdharwad/speaker-enrollment"},
    "speaker_verification": {"iitdharwad": "bhashini/iitdharwad/speaker-verification"},
    "speaker_diarization": {
        "iisc": "bhashini/iisc/speaker-diarization",
        "oss": "bhashini/speaker-diarization",
    },
    "language_diarization": {"nitk": "bhashini/nitk/language-diarization"},
    "voice_cloning": {"indicf5": "bhashini/ai4b/indicf5-tts"},
    "ocr": {
        "printed": "bhashini/iiith-bhasha-ocr",
        "scene": "bhashini/iiith-ocr-sceneText-all",
        "handwritten": "bhashini/iiith/ocr-hw-bhaasha",
        "bodhan": "bhashini/bodhan/indic-doc/ocr",
    },
    "denoiser": {"fb": "bhashini/facebook/denoiser--gpu-t4"},
    "kws": {"iitg": "bhashini/iitg/kws"},
    "lip_sync": {"iitm": "bhashini/iitm/lip-sync"},
}

VOICE_CLONE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/tts/voice-cloning"
DENOISE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/denoiser"
ASR_STREAM_URL = os.environ.get("BHASHINI_ASR_WS", "wss://dhruva-api.bhashini.gov.in/ws/v1/asr/stream")
ASR_STREAM_SERVICE = "bhashini/ai4b/indic-conformer/grpc"

TASK_TYPE = {"ald": "audio-lang-detection", "tld": "txt-lang-detection",
             "speaker_diarization": "speaker-diarization", "language_diarization": "language-diarization",
             "transliteration": "transliteration", "voice_cloning": "tts", "asr": "asr",
             "translation": "translation", "tts": "tts", "ner": "ner", "ocr": "ocr"}

TASK_TYPE = {"ald": "audio-lang-detection", "tld": "txt-lang-detection",
             "speaker_diarization": "speaker-diarization", "transliteration": "transliteration",
             "voice_cloning": "tts", "asr": "asr", "translation": "translation", "tts": "tts",
             "ner": "ner"}


def _live() -> bool:
    return bool((os.environ.get("BHASHINI_USER_ID") and os.environ.get("BHASHINI_API_KEY"))
                or os.environ.get("BHASHINI_INFERENCE_KEY"))


def _b64(path_or_b64: str) -> str:
    """Accept a file path or an already-base64 string."""
    if os.path.exists(path_or_b64):
        with open(path_or_b64, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return path_or_b64


# ------------------------------------------------------------------ config
_CONFIG_CACHE: Dict[str, Dict] = {}


def config(pipeline_tasks: List[Dict], pipeline_id: str = PIPELINE_ID) -> Dict:
    """Pipeline Config call. Returns service/model ids + inference endpoint + key."""
    key = json.dumps([t.get("taskType") for t in pipeline_tasks]) + "|" + pipeline_id
    if key in _CONFIG_CACHE:
        return _CONFIG_CACHE[key]
    hdr = {"userID": os.environ["BHASHINI_USER_ID"], "ulcaApiKey": os.environ["BHASHINI_API_KEY"],
           "Content-Type": "application/json"}
    body = json.dumps({"pipelineTasks": pipeline_tasks,
                       "pipelineRequestConfig": {"pipelineId": pipeline_id}}).encode()
    out = _post(CONFIG_URL, body, hdr)
    _CONFIG_CACHE[key] = out
    return out


def _endpoint(cfg: Dict):
    ep = (cfg.get("pipelineInferenceAPIEndPoint") or {})
    url = ep.get("callbackUrl") or INFER_URL_DEFAULT
    k = ep.get("inferenceApiKey") or {}
    return url, k.get("name", "Authorization"), k.get("value")


def _creds(pipeline_id: str = PIPELINE_ID):
    """Inference creds: use BHASHINI_INFERENCE_KEY directly, else fetch one via a config call."""
    if DIRECT_INFER_KEY:
        return DIRECT_INFER_URL, "Authorization", DIRECT_INFER_KEY
    cfg = config([{"taskType": "asr"}], pipeline_id)
    return _endpoint(cfg)


_QUOTA_FILE = os.path.expanduser(os.environ.get("BHASHINI_QUOTA_FILE", "~/.config/bhashini_quota.json"))
BUDGET = int(os.environ.get("BHASHINI_CALL_BUDGET", "2000"))


def quota_status() -> Dict:
    """Local call-budget tracker (the ULCA account has 2,000 calls)."""
    q = {}
    try:
        if os.path.exists(_QUOTA_FILE):
            q = json.load(open(_QUOTA_FILE))
    except Exception:
        q = {}
    used = int(q.get("used", 0))
    return {"used": used, "budget": BUDGET, "remaining": max(0, BUDGET - used),
            "updated": q.get("updated")}


def _quota_bump(n: int = 1):
    q = quota_status()
    if q["used"] + n > BUDGET:
        raise RuntimeError(f"Bhashini call budget exceeded ({q['used']}/{BUDGET}) — raise BHASHINI_CALL_BUDGET")
    q["used"] += n; q["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        os.makedirs(os.path.dirname(_QUOTA_FILE), exist_ok=True)
        json.dump({"used": q["used"], "updated": q["updated"]}, open(_QUOTA_FILE, "w"))
    except Exception:
        pass


def _post(url: str, body: bytes, headers: Dict, retries: int = 3) -> Dict:  # pragma: no cover (network)
    import urllib.request, urllib.error
    ctx = None
    if os.environ.get("BHASHINI_INSECURE") == "1":      # behind a firewall with an untrusted CA
        import ssl
        ctx = ssl._create_unverified_context()
    last = None
    for attempt in range(retries):
        _quota_bump(1)
        req = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < retries - 1:
                last = e; time.sleep(1.5 * (attempt + 1)); continue
            raise
        except Exception as e:
            if attempt < retries - 1:
                last = e; time.sleep(1.5 * (attempt + 1)); continue
            raise
    raise last


def _svc(cfg: Dict, task_type: str, lang: Optional[str] = None) -> Optional[str]:
    for block in cfg.get("pipelineResponseConfig", []):
        if block.get("taskType") == task_type:
            for c in block.get("config", []):
                if not lang or (c.get("language", {}) or {}).get("sourceLanguage") == lang:
                    return c.get("serviceId")
    return None


# ------------------------------------------------------------------ compute
def _resolve_service(task_type: str, lang: Optional[str] = None) -> Optional[str]:
    """Ask the live pipeline config which serviceId to use for this task (needs user creds)."""
    if not (os.environ.get("BHASHINI_USER_ID") and os.environ.get("BHASHINI_API_KEY")):
        return None
    try:
        cfg = config([{"taskType": task_type}], PIPELINE_ID)
        return _svc(cfg, task_type, lang)
    except Exception:
        return None


def _compute(task: Dict, input_data: Dict, pipeline_id: str = PIPELINE_ID) -> Dict:
    """Config-able tasks (asr/translation/tts) resolve serviceId via config; direct tasks
    (tld/ald/diarization/ocr) carry their own serviceId and just need inference creds."""
    if (task.get("config") or {}).get("serviceId"):
        url, hname, hval = _creds(pipeline_id)
    else:
        cfg = config([task], pipeline_id)
        url, hname, hval = _endpoint(cfg)
        task.setdefault("config", {})["serviceId"] = _svc(
            cfg, task["taskType"], (task.get("config", {}).get("language") or {}).get("sourceLanguage"))
    body = json.dumps({"pipelineTasks": [task], "inputData": input_data}).encode()
    resp = _post(url, body, {hname: hval, "Content-Type": "application/json"})
    # surface API errors instead of letting callers hit a cryptic KeyError on pipelineResponse
    if isinstance(resp, dict):
        bad = (resp.get("status") == "error" or "error" in resp
               or ("pipelineResponse" not in resp and "audio" not in resp and "output" not in resp))
        if bad:
            raise RuntimeError(f"Bhashini {task.get('taskType')} failed: {json.dumps(resp)[:400]}")
    return resp


def asr(audio: str, source_language: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("asr", source_language)
    task = {"taskType": "asr", "config": {
        "language": {"sourceLanguage": source_language},
        "serviceId": service_id or SERVICE_IDS["asr"]["multilingual_ai4b"],
        "audioFormat": "wav", "samplingRate": 16000, "postProcessors": ["itn"]}}
    return _compute(task, {"input": [{"source": ""}], "audio": [{"audioContent": _b64(audio)}]})


def translate(text: str, source_language: str, target_language: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("translation", target_language, text)
    task = {"taskType": "translation", "config": {
        "language": {"sourceLanguage": source_language, "targetLanguage": target_language},
        "serviceId": service_id or SERVICE_IDS["translation"]["indictrans_v2"]}}
    return _compute(task, {"input": [{"source": text}], "audio": [{"audioContent": None}]})


def synthesize(text: str, target_language: str, gender: str = "female", service_id: Optional[str] = None) -> Dict:
    """TTS — generates Indic test audio for the Worst-AI / generator set.
    Resolves the serviceId from the live pipeline config (the hardcoded ids can be
    rejected by the server); falls back to the catalogue id only if config is unavailable."""
    if not _live():
        return _mock("tts", target_language, text)
    sid = service_id or _resolve_service("tts", target_language) or SERVICE_IDS["tts"]["iitm"]
    task = {"taskType": "tts", "config": {
        "language": {"sourceLanguage": target_language},
        "serviceId": sid,
        "gender": gender, "speed": 1.0, "samplingRate": 22050}}
    return _compute(task, {"input": [{"source": text}], "audio": [{"audioContent": None}]})


def detect_audio_language(audio: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("ald", _mock_lang(audio))
    task = {"taskType": "audio-lang-detection",
            "config": {"serviceId": service_id or SERVICE_IDS["ald"]["iitmandi"]}}
    return _compute(task, {"audio": [{"audioContent": _b64(audio)}]})


def detect_text_language(text: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("tld", _mock_lang(text))
    task = {"taskType": "txt-lang-detection",
            "config": {"serviceId": service_id or SERVICE_IDS["tld"]["ai4b_all"]}}
    return _compute(task, {"input": [{"source": text}]})


def diarize_speakers(audio: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return {"_mode": "MOCK", "output": [{"speaker_labels": [{"speaker1": [{"start_time": 0.0, "duration": 1.5}]}]}]}
    task = {"taskType": "speaker-diarization",
            "config": {"serviceId": service_id or SERVICE_IDS["speaker_diarization"]["iisc"]}}
    return _compute(task, {"audio": [{"audioContent": _b64(audio)}]})


def speaker_enroll(audio: str, speaker_name: str = "spk1", service_id: Optional[str] = None) -> Dict:
    """Bhashini speaker enrollment (IIT Dharwad). Payload: config.speakerName + inputData.audio.
    Returns the API response; `enrolled_id(resp)` extracts the reusable speakerId."""
    if not _live():
        return {"_mode": "MOCK", "pipelineResponse": [{"output": [{"speakerId": f"mock-{speaker_name}"}]}]}
    task = {"taskType": "speaker-enrollment",
            "config": {"serviceId": service_id or SERVICE_IDS["speaker_enrollment"]["iitdharwad"],
                       "speakerName": speaker_name}}
    return _compute(task, {"audio": [{"audioContent": _b64(audio)}]})


def speaker_verify(audio: str, speaker_id: str, service_id: Optional[str] = None) -> Dict:
    """Bhashini speaker verification (IIT Dharwad): does this audio match the enrolled speakerId?
    Payload: config.speakerId + inputData.audio (single audio)."""
    if not _live():
        return {"_mode": "MOCK", "pipelineResponse": [{"output": [{"match": True, "score": 0.5}]}]}
    task = {"taskType": "speaker-verification",
            "config": {"serviceId": service_id or SERVICE_IDS["speaker_verification"]["iitdharwad"],
                       "speakerId": speaker_id}}
    return _compute(task, {"audio": [{"audioContent": _b64(audio)}]})


def enrolled_id(resp: Dict) -> Optional[str]:
    try:
        o = resp["pipelineResponse"][0]["output"][0]
        return o.get("speakerId") or o.get("speaker_id") or o.get("source")
    except Exception:
        return None


def verification_result(resp: Dict):
    """Pull the verification decision/score out of the (varied) response shapes."""
    def dig(v):
        if isinstance(v, dict):
            for k in ("verified", "verificationResult", "isVerified", "match", "matched", "success", "score", "confidence", "similarity"):
                if k in v and isinstance(v[k], (bool, int, float)):
                    return {k: v[k]}
            for nv in v.values():
                r = dig(nv)
                if r: return r
        elif isinstance(v, list):
            for it in v:
                r = dig(it)
                if r: return r
        return None
    return dig(resp)


# ------------------------------------------------------------------ mock/status
def _mock_lang(seed: str) -> str:
    langs = ["hi", "ta", "te", "bn", "mr", "kn", "ml", "gu", "pa", "en"]
    return langs[int(hashlib.sha256(str(seed).encode()).hexdigest(), 16) % len(langs)]


def _mock(task: str, lang: str, text: str = "") -> Dict:
    return {"_mode": "MOCK", "taskType": task, "output": [{"source": text or f"[mock-{task}]",
            "langCode": lang}], "_note": "set BHASHINI_USER_ID/BHASHINI_API_KEY for real ULCA."}


def transliterate(text: str, source_language: str, target_language: str,
                  is_sentence: bool = True, num_suggestions: int = 1,
                  service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("transliteration", target_language, text)
    task = {"taskType": "transliteration", "config": {
        "language": {"sourceLanguage": source_language, "targetLanguage": target_language},
        "serviceId": service_id or SERVICE_IDS["transliteration"]["indicxlit"],
        "isSentence": is_sentence, "numSuggestions": num_suggestions}}
    return _compute(task, {"input": [{"source": text}]})


def ner(text: str, source_language: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("ner", source_language, text)
    task = {"taskType": "ner", "config": {
        "language": {"sourceLanguage": source_language},
        "serviceId": service_id or SERVICE_IDS["ner"]["ai4b"]}}
    return _compute(task, {"input": [{"source": text}]})


def ocr(image: str, source_language: str, text_detection: bool = False,
        service_id: Optional[str] = None) -> Dict:
    if not _live():
        return _mock("ocr", source_language)
    task = {"taskType": "ocr", "config": {
        "language": {"sourceLanguage": source_language},
        "serviceId": service_id or SERVICE_IDS["ocr"]["printed"],
        "textDetection": "True" if text_detection else "False"}}
    return _compute(task, {"image": [{"imageContent": _b64(image)}]})


def denoise(audio: str, service_id: Optional[str] = None) -> Dict:
    """Denoiser uses a dedicated flat endpoint (not the pipeline one)."""
    if not _live():
        return {"_mode": "MOCK", "audio": [{"audioContent": None}], "_note": "set keys for real denoise."}
    payload = {"config": {"serviceId": service_id or SERVICE_IDS["denoiser"]["fb"]},
               "audio": [{"audioContent": _b64(audio)}]}
    return _post_json(DENOISE_URL, payload)


def voice_clone(text: str, ref_text: str, ref_audio: str, source_language: str = "hi",
                service_id: Optional[str] = None) -> Dict:
    """IndicF5 voice cloning — dedicated endpoint; returns synthesized audio (base64)."""
    if not _live():
        return {"_mode": "MOCK", "audio": [{"audioContent": None}], "_note": "set keys + real ref audio."}
    payload = {"config": {"language": {"sourceLanguage": source_language},
                          "serviceId": service_id or SERVICE_IDS["voice_cloning"]["indicf5"]},
               "input": [{"source": text, "refText": ref_text, "refAudioContent": _b64(ref_audio)}]}
    return _post_json(VOICE_CLONE_URL, payload, extra_headers={"x-auth-source": "API_KEY"})


def diarize_languages(audio: str, service_id: Optional[str] = None) -> Dict:
    if not _live():
        return {"_mode": "MOCK", "output": [{"language_labels": [{"lang1": [{"start_time": 0.0, "duration": 1.5}]}]}]}
    task = {"taskType": "language-diarization",
            "config": {"serviceId": service_id or SERVICE_IDS["language_diarization"]["nitk"]}}
    return _compute(task, {"audio": [{"audioContent": _b64(audio)}]})


def _post_json(url: str, payload: Dict, extra_headers: Optional[Dict] = None) -> Dict:
    """POST a flat (non-pipeline) payload to a dedicated inference endpoint."""
    _, _, key = _creds()
    headers = {"Authorization": key, "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    return _post(url, json.dumps(payload).encode(), headers)


def stream_asr(audio_pcm16, sample_rate: int = 16000, language: str = "hi",
               service_id: str = ASR_STREAM_SERVICE, timeout: float = 15.0,
               interim: bool = False) -> str:
    """Streaming ASR over WebSocket (protocol per official SDK).
    `audio_pcm16` = raw int16 PCM bytes (or iterable of chunks). Requires `websockets`.
    Auth: `?api_key=<inference key>`. Returns the concatenated transcript."""
    try:
        import asyncio, websockets
    except Exception as e:
        raise RuntimeError("streaming ASR needs `pip install websockets`") from e
    if sample_rate != 16000:
        raise ValueError("ASR streaming supports only 16000 Hz PCM.")
    if not _live():
        return "[mock-stream-asr]"
    from urllib.parse import quote
    key = DIRECT_INFER_KEY or (lambda: _creds()[2])()
    url = f"{ASR_STREAM_URL}?api_key={quote(key)}"
    if isinstance(audio_pcm16, (bytes, bytearray)):
        step = 16000 * 2 // 5  # 200 ms
        chunks = [audio_pcm16[i:i + step] for i in range(0, len(audio_pcm16), step)]
    else:
        chunks = list(audio_pcm16)

    def _i16_to_f32(b: bytes) -> bytes:  # server expects float32 'raw' audio
        import array
        s = array.array("h"); s.frombytes(b)
        return array.array("f", (max(-1.0, min(1.0, x / 32768.0)) for x in s)).tobytes()

    chunks = [_i16_to_f32(c) for c in chunks if c]

    start = {"type": "start", "controlConfig": {"dataTracking": False},
             "config": {"serviceId": service_id, "language": {"sourceLanguage": language},
                        "audioFormat": "pcm", "encoding": "raw", "samplingRate": 16000,
                        "transcriptionFormat": {"value": "transcript"}, "profanityFilter": True,
                        "postProcessors": ["itn", "punctuation"]},
             "streamingConfig": {"chunkDurationMs": 200, "interimResults": interim,
                                 "endOfStreamPolicy": "client_signal"}}

    async def _run():
        texts = []
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps(start))
            # wait for ready
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout))
                if m.get("type") == "ready": break
                if m.get("type") == "error": raise RuntimeError(m.get("message", "stream error"))
            for c in chunks:
                await ws.send(c)
            await ws.send(json.dumps({"type": "end"}))
            try:
                while True:
                    m = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout))
                    if m.get("type") == "transcript":
                        t = (m.get("output") or [{}])[0].get("source")
                        if t: texts.append(t)
                        if m.get("isFinal"): break
                    elif m.get("type") == "error":
                        raise RuntimeError(m.get("message", "stream error"))
                    elif m.get("type") in ("end", "close"):
                        break
            except asyncio.TimeoutError:
                pass
        return " ".join(texts).strip()

    return asyncio.run(_run())


def status() -> Dict:
    return {"mode": "LIVE" if _live() else "MOCK", "have_keys": _live(),
            "pipeline_id": PIPELINE_ID, "services_known": sorted(SERVICE_IDS),
            "enable": "export BHASHINI_USER_ID / BHASHINI_API_KEY (ULCA My Profile)",
            "caveat": "ULCA APIs are PoC-only; production = Bhashini paid plan. ASR/TTS coverage != detection coverage."}


def _selftest():
    st = status()
    print("mode:", st["mode"], "| services:", len(st["services_known"]))
    assert "asr" in SERVICE_IDS and "translation" in SERVICE_IDS and "tts" in SERVICE_IDS
    assert SERVICE_IDS["voice_cloning"]["indicf5"].endswith("indicf5-tts")
    print("ALD(mock):", _mock("ald", _mock_lang("clip"))["output"][0]["langCode"])
    print("TLD(mock):", _mock("tld", _mock_lang("text"))["output"][0]["langCode"])
    print(f"[selftest] PASS — adapter ready ({'LIVE' if st['have_keys'] else 'MOCK, no keys'}).")


if __name__ == "__main__":
    _selftest()
