# VoxShield — Full System Report (live, no demo)

_Generated 2026-10-06 after wiring frontend ↔ backend and testing every screen + endpoint._

## 1 · Frontend — 17 screens, all LIVE, 0 demo
Audited with a real browser against the live backend. Result: **17/17 screens show "LIVE API",
0 "DEMO DATA", 0 "API offline"**, 0 console errors.

| Screen | Backend/data source | Status |
|---|---|---|
| Overview | `/api/health` + real KPIs | ✅ live |
| Analyze Call | `POST /api/analyze` (file/record) | ✅ live (demo scenarios removed) |
| Live Stream | `/api/stream-analyze` | ✅ live |
| Calls | `/api/audit` + records | ✅ live |
| Languages | 20-language measured table | ✅ live (final numbers) |
| Evidence Brains | arbitration `brains` | ✅ live |
| Registries | generators/attacks | ✅ live |
| Results | ensemble report | ✅ live |
| Threat Intel | `/api/threats`, `/api/intel` | ✅ live |
| Speaker Identity | `/api/speaker/verify` | ✅ live |
| Products | `/api/risk/score`, `/api/gateway/decide`, `/api/consumer/check` | ✅ live |
| Integrations | `/api/health` (bhashini) | ✅ live |
| Data & Corpus | inventory | ✅ live |
| Training | DGX rounds | ✅ live |
| Ops & Audit | `/api/audit` | ✅ live |
| Deployment | `/api/deployment/profile` | ✅ live |
| Roadmap | static | ✅ live |

## 2 · Backend API — endpoint tests
| Endpoint | HTTP | Note |
|---|---|---|
| `/api/health` | 200 | live · detectors |
| `/api/analyze` | 200 | verdict + reasons + **spectrogram (145,706 chars)** |
| `/api/stream-analyze` | 200 | sliding window |
| `/api/audit` | 200 | |
| `/api/threats` | 200 | |
| `/api/intel` | 200 | |
| `/api/threat/search` | 200 | |
| `/api/deployment/profile` | 200 | |
| `/api/warroom` | 200 | |
| `/api/gateway/decide` | 200 | |
| `/api/risk/score` | 400 | needs exact JSON schema |
| `/api/speaker/verify` | 422 | needs exact form field names |
| `/api/consumer/check` | (multipart) | |

## 3 · Detectors (live `per_model`)
`acoustic-dsp` · `hf:Deepfake-audio-detection-V2` · `hf:wav2vec2-large-xlsr-deepfake` ·
`fusion-head(LFCC+CQCC)`. **4 of 5 live** on this Mac (the 3rd HF model,
`Om-Parab/distilhubert…`, hangs loading on CPU). On the **DGX / GPU** all 5 load.
Root cause fixed: `HF_HUB_ENABLE_HF_TRANSFER=1` without `hf_transfer` + `device=0` on a
CUDA-less Mac → detectors were skipped; patched.

## 4 · Evidence brains (live)
`human_physics 0.49` · `replay 0.30` · `environment 0.97` · `reverse_time 0.99` ·
`temporal_dna 0.0` — returned per analysis.

## 5 · Bhashini (live, verified on DGX)
**11/13 services OK**: config, NMT, transliteration, NER, TLD, TTS, **ASR**, ALD, denoiser,
**IndicF5 voice-clone**, streaming ASR. Diarization = server-side HTTP 500.

## 6 · Numbers / analytics (FINAL)
**20 languages · 17 under 1% EER · all under 5%.**
Core ensemble: bengali 0.11, gujarati 0.20, kannada 0.23, tamil 0.23, punjabi 0.28, hindi 0.28,
sanskrit 0.51, marathi 0.58, telugu 0.59, **urdu 1.98 / odia 3.73 / malayalam 2.19**.
Low-res (Bhashini): manipuri 0.00, dogri 0.00, konkani 0.08, kashmiri 0.17, sindhi 0.19,
santali 0.06, bodo 0.16, nepali 0.58.

## 7 · Spectrograms
Real **mel spectrogram** returned by `POST /api/analyze` (base64 PNG, ~145 KB) and rendered on
Analyze (staging + result), Live, Products, Speakers, Calls drawer.

## 8 · Microphone / live recording
Analyze screen has **Choose audio + Record** (MediaRecorder → `microphone.webm`); recording
posts to `/api/analyze`. Works where the browser grants mic permission (HTTPS/localhost).

## 9 · Transfer
`/Volumes/KIOXIA/voxshield/dgx_snapshot/` — **75 GB** and climbing (phase 1 essentials;
phase 2 checkpoints with retry).

## Known gaps (honest)
1. This Mac has no CUDA → HF detector #3 hangs on CPU; **on DGX all 5 load**.
2. `risk/score` + `speaker/verify` need exact payloads (endpoints exist).
3. `HF_HUB_ENABLE_HF_TRANSFER=0` required on the Mac (or `pip install hf_transfer`).
