# Bhashini support report — draft email
**To:** digitalindiabhashinidivision@gmail.com
**Subject:** API issue: diarization endpoints return HTTP 500; speaker-verification "Speaker not found" (app `suvidha`)

Dear Bhashini Team,

We are integrating the Bhashini (ULCA/Dhruva) inference APIs for a speech-forensics project. Our account/app is **`suvidha`** (ULCA user `<redacted>`), approved 14-09-2026 (2,000 calls). Working services: **ASR, TTS, NMT, Transliteration, NER, TLD, ALD, Denoiser, Voice-Cloning (IndicF5), and streaming ASR** — thank you.

Two problems remain — both reproduce consistently via the raw REST API (`POST https://dhruva-api.bhashini.gov.in/services/inference/pipeline`, `Authorization: <inference key>`):

**1. Speaker / Language Diarization → HTTP 500 (server-side)**
- Request: `taskType="speaker-diarization"`, `config.serviceId` tried **both** `bhashini/iisc/speaker-diarization` and `bhashini/speaker-diarization`; `inputData.audio=[{audioContent:<base64 16 kHz WAV, speech>}]`.
- Also tried 2.5 s and 10 s clips → **HTTP 500 "Internal Server Error"** every time.
- `taskType="language-diarization"` (`bhashini/nitk/language-diarization`) → same HTTP 500.
- Payload matches the official `bhashini-client-sdk` v0.2.5 exactly.
- **Request:** confirm whether these endpoints are enabled for our key, and the correct serviceId/usage.

**2. Speaker Verification: "Speaker not found" for a different clip**
- Enrollment `taskType="speaker-enrollment"`, `config.speakerName=<unique>`, `inputData.audio` → returns a valid `speakerId` ("Speaker enrolled successfully").
- Verifying the **same** clip → `confidence 1.0` ✅.
- Verifying a **different** clip of the same synthetic-voice speaker → `HTTP 400 {"detail":{"message":"Speaker not found."}}`.
- We also found: **re-enrolling the same `speakerName` returns HTTP 400** (so names must be unique) — please confirm this is expected.
- **Request:** (a) Is the enrolled profile persisted per account/app, or only per request? (b) Does verification require real human speech (vs TTS-synthesized audio)? (c) Any required audio duration / min-speech for a reusable profile?

Our integration code + exact payloads are available and we can share a Postman collection or logs.

Thank you,
<Your Name> · SRM Institute of Science and Technology
Project: VoxShield (Real-Time Voice Deepfake & Audio-Spoofing Detection for Indic-Language Telephony Fraud)
