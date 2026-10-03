# Bhashini × VoxShield — Live Service-ID Catalogue & Integration Map
### Approved 2026-09-14 · 2,000 API calls · Udyat account · code: `backend/bhashini.py`

## 1 · Auth & flow
1. **Pipeline Config** — `POST https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline`
   headers `userID` + `ulcaApiKey` (ULCA → My Profile). Body: `pipelineTasks[]` + `pipelineRequestConfig.pipelineId`.
   Returns per task: `serviceId`, `modelId`, `languages`; plus `pipelineInferenceAPIEndPoint` = `{ callbackUrl, inferenceApiKey{name,value} }`.
2. **Pipeline Compute** — `POST <callbackUrl>` (default `https://dhruva-api.bhashini.gov.in/services/inference/pipeline`)
   header `<inferenceApiKey.name>: <inferenceApiKey.value>`, body `pipelineTasks[].config.serviceId` + `inputData`.

Public pipeline IDs: IITM `660fa5bec7fb5b0328229016` · IITB `660f813c0413087224435d2c` · IIITH `660f866443e53d4133f65317` · **Initial `64392f96daac500b55c543cd`**.

Env: `BHASHINI_USER_ID`, `BHASHINI_API_KEY`, optional `BHASHINI_INFERENCE_KEY` (skips config), `BHASHINI_PIPELINE_ID`.

**Credential mapping (Udyat portal, app `suvidha`):**
- `userID` = the account UUID (the unlabeled value with the **Revoke** button)
- `ulcaApiKey` = the **"Udyat Key"** value
- `BHASHINI_INFERENCE_KEY` = the **"Inference"** value → used **directly** against Dhruva (`Authorization`)
- Config-able tasks = `asr / translation / transliteration / tts`; **TLD / ALD / diarization / OCR are direct compute calls** (not config-able → they carry their own `serviceId`).

**✅ Verified live 2026-10-01 (app `suvidha`):** Config ✅ · TLD ✅ (`mai`, Deva, 0.999) · ALD ✅ (`hi`, Deva, 1.0) · TTS ✅ (48 kHz Hindi WAV) · ASR ✅ (correct transcript). Note: ASR needs **16 kHz** audio and rejects `source: null` (use `""`).

## 2 · Service IDs (by task) → VoxShield use

### ASR
| Service ID | Languages | VoxShield use |
|---|---|---|
| `bhashini/ai4bharat/conformer-multilingual-asr` | all 22 | default transcription (§10) |
| `bhashini/bodhan/asr-transcribe-flex` | 27 (incl. Bhili, Chhattisgarhi, Haryanvi) | widest coverage |
| `bhashini/bodhan/asr-transcribe-core` | 25 | |
| `ai4bharat/conformer-hi-gpu--t4` | Hindi | |
| `ai4bharat/conformer-multilingual-dravidian-gpu--t4` | Kn/Ml/Ta/Te | |
| `ai4bharat/conformer-multilingual-indo_aryan-gpu--t4` | Hi/Bn/Mr/Ur/Od/Pa/Gu/Sa | |
| `bhashini/iitm/asr-dravidian--gpu--t4` | Te/Kn/Ml/Ta | |
| `bhashini/iisc/asr-mai-t4` · `bhashini/iisc/asr-bho-t4` | Maithili · Bhojpuri | low-resource |

### Translation (NMT)
`bhashini/iiith/nmt-all` (36 langs incl. Hinglish) · `ai4bharat/indictrans-v2-all-gpu--t4` (22) · `bhashini/bodhan/Indic-trans-v4` · `iitb/trilingual-en_hi_mr-v1-gpu--t4` — **cross-lingual clone text (§37.3)**.

### Transliteration
`ai4bharat/indicxlit--cpu-fsv2` (24 langs) — code-switch/script normalization.

### TTS
`Bhashini/IITM/TTS` (25) · `Bhashini/IISC/TTS` (SYSPIN) · `ai4bharat/indic-tts-coqui-{dravidian,indo_aryan,misc}` · `bhashini/bodhan/indic-tts` — **Worst-AI generation (§16)**.

### Language detection
- **ALD:** `bhashini/iitmandi/audio-lang-detection/gpu` (12) · `bhashini/ald` (18) — **profiler routing (§8)**.
- **TLD:** `bhashini/indic-lang-detection-all` · `bhashini/iiiith/indic-lang-detection-all` · `bhashini/indic/tld`.

### Speaker / diarization / NER / other
- **Speaker enrollment** `bhashini/iitdharwad/speaker-enrollment` · **verification** `bhashini/iitdharwad/speaker-verification` — **Speaker Identity Brain (§8)**.
- **Speaker diarization** `bhashini/iisc/speaker-diarization` · `bhashini/speaker-diarization`.
- **Language diarization** `bhashini/nitk/language-diarization`.
- **Voice cloning** `bhashini/ai4b/indicf5-tts` (11 langs) — **clone attacks**.
- **NER** `bhashini/iiith/ner` · `bhashini/ai4bharat/indic-ner` · `bhashini/aukbc/ner`.
- **OCR** `bhashini/iiith-bhasha-ocr`, `bhashini/iiith-ocr-sceneText-all`, `bhashini/iiith/ocr-hw-bhaasha`, `bhashini/bodhan/indic-doc/ocr`.
- **Lip sync** `bhashini/iitm/lip-sync` (future AV). **KWS** `bhashini/iitg/kws`.

## 3 · Where it plugs into VoxShield
```
call audio ─► ALD (bhashini) ──► language route (scorecard §23)
            └► ASR (bhashini) ─► transcript ─► Conversational / Semantic↔Prosody / Causal brain (§10)
text channel ─► TLD (bhashini) ─► route
Worst-AI gen: NMT/Translit ─► TTS/Voice-Clone (bhashini) ─► scenario_render (G.711) ─► train/eval
identity:    Speaker enroll/verify + diarization (bhashini) ─► Speaker Identity Brain (§8)
```

## 4 · Rules
- ULCA = **PoC only**; production needs a Bhashini paid plan.
- **Never** send real/consented recordings to the shared API — synthetic/public only.
- Indic ASR/TTS **coverage ≠ deepfake-detection coverage** (separate eval axes).
- AIKosh (§38) = self-hosted weights/data · Bhashini = managed inference (2,000 calls).

---

## 6 · Implementation status (2026-10-01)
**Client functions (all in `backend/bhashini.py`):** `config · asr · translate · synthesize ·
transliterate · ner · ocr · denoise · voice_clone · detect_audio_language · detect_text_language ·
diarize_speakers · diarize_languages · speaker_enroll · speaker_verify · stream_asr` (+ `enrolled_id`,
`verification_result`, `quota_status`).

**Live test (`backend/bhashini_livetest.py`):**
| Service | Result |
|---|---|
| config · nmt · transliteration · ner · tld · tts · asr · ald | ✅ OK |
| denoiser · voice_clone(indicf5) · **stream_asr (WebSocket)** | ✅ OK |
| speaker_diarization · language_diarization | ⛔ HTTP 500 (server-side) |
| ocr | ⏭ needs an image (`--image`) |

**Ops:** call-budget tracker (`~/.config/bhashini_quota.json`, `BHASHINI_CALL_BUDGET`, default 2000) + retries with backoff (3× on 5xx/timeout) + config caching.
**Wiring:** ALD+ASR in `orchestrate` (auto-on via `BHASHINI_ALWAYS=1`); ASR transcript → `conversational.text_forensics`; optional `use_bhashini_diarization`; `/api/analyze?bhashini=true`; `/api/health` exposes mode + quota; console panel has **"Run live on a clip"**; `gen_worst_ai.py` uses **voice-clone + transliteration**; `enroll_speaker.py` enrolls a **real** voice.
**Known limits:** verification/diarization need **real human speech** (TTS-synthetic enroll → "Speaker not found"); diarization endpoints 500; ULCA is PoC-only (production ⇒ paid plan); streaming expects 16 kHz and the server wants **float32** chunk bytes (handled).
