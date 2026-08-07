# VoxShield — Ground-Truth Fact Sheet (single source of truth)
*Every number here is verified from a committed artifact or read from source (file:line). Use ONLY these numbers. Never invent. Distinguish "built today" from "design/roadmap".*

## Verified metrics
- Meta-fusion EER **5.9%** (0.0593), ROC-AUC **0.983**, accuracy@0.70 **93.4%**, precision **93.5%**, recall **92.9%**, F1 **0.93**, min t-DCF **0.252**. Held-out In-the-Wild, n_test=320, n_train=480. [meta_eval.json]
- Confusion @0.70: TP 144 · TN 155 · FP 10 · FN 11. [calibration.json]
- Calibration ECE **0.044**, Brier **0.048**, threshold 0.70. (Uncalibrated ECE 0.031 — calibration did NOT lower ECE; report honestly.) [calibration.json]
- Per-detector on full 800-clip corpus (reproduced from meta_scores.csv): XLS-R **16.0%** EER / 0.901 AUC (best single); DistilHuBERT 24.9% / 0.828 (deck shows 23.0%); LFCC+CQCC head 26.6% / 0.786; Acoustic-DSP 47.4% / 0.521; Deepfake-V2 (Wav2Vec2) 62.0% / 0.356; **simple-average fusion 19.1%** / 0.839.
- Indic genuine clean FP **11.7% → 6.3%** (channel-aware). [lang_report_pre_channel.json → lang_report.json]
- Per-language clean FP (deployed): Marathi 0.0, Tamil 3.3, Punjabi 3.3, Bengali 3.3, Kannada 6.7, Gujarati 6.7, Assamese 6.7, Hindi 10.0, Malayalam 10.0, Telugu 13.3 (weakest).
- Indic fake recall **42% → 82%** (language-ID routing), English EER unchanged **5.9%**. [exp_indicfull_result.json: live_indic_recall 0.417, indic_fake_recall 0.823, english_eer 0.059]
- Robustness self-test (n=80/cond, thr 0.70): clean EER 7.5%; Opus 12k **2.5%** (−5.0 pts, improves); G.711 8k 15.0% (+7.5); MP3 16k 20.0% (+12.5); tempo 0.9× 32.5% (+25.0); noise@15dB 45.0% (+37.5); pitch +2st 56.3% (+48.8). [robustness.json]
- Streaming time-to-flag **3.0 s** (5/5 clips ≥3s, all within 10s target); GPU sub-second, CPU 3–8s. [latency_trace.json]

## Architecture (real)
- Signal path: 8 kHz/16 kHz call → load_audio resamples to **16 kHz mono**, drops silence (librosa.effects.split top_db=30), caps first 6 s of speech → 89-dim feature bank → 5 detectors (run concurrently in a ThreadPoolExecutor) → logistic meta-stacker → Platt calibration → channel-aware threshold → verdict + reason codes + SHA-256 audit. (8 kHz is a DETECTED channel flag when hf_energy_ratio<0.02, not a resample target.)
- **89-dim feature vector** = LFCC 40 (n_lfcc=20, mean+std) + CQCC 40 (CQT 84 bins, DCT, mean+std) + 9 scalars: hf_energy_ratio, hf_regularity, spectral_flatness, phase_reg (group-delay proxy), f0_jitter, shimmer, f0_voiced_ratio, silence_ratio, breath_score.
- **5 detectors + learned stacker weights** (LogisticRegressionNP, standardized inputs, sigmoid): acoustic-dsp **w=−0.55** (pure DSP heuristic: fake_prob=0.34·hf+0.24·phase+0.24·prosody+0.18·breath); Deepfake-V2 (MelodyMachine, wav2vec2-base) **w=−1.17**; XLS-R (Gustking/wav2vec2-large-xlsr) **w=+1.21**; DistilHuBERT (Om-Parab) **w=+2.22**; LFCC+CQCC head (LogisticRegressionNP(89), b=−0.512, over the FULL 89-dim vector — name is a label) **w=+2.10**; bias b=+0.134. Stacker Platt cal {a:6.446,b:−3.151}. [meta_fusion.json]
- **Recall-floor gate**: if max(distilhubert, xlsr) ≥ 0.90 AND LFCC/CQCC head ≥ 0.5 → floor score to ≥ 0.70.
- **SHAP**: closed-form EXACT for the logistic head, φᵢ=(wᵢ/sdᵢ)(xᵢ−μᵢ) in logit space; contributions sum to final_logit−base_logit. No `shap` dependency.
- **Thresholds**: wideband HIGH 0.70 / MED 0.40; narrowband (phone) HIGH **0.85** / MED 0.55. Never auto-block — HIGH → human step-up.
- **Indic routing**: Whisper-base language-ID → if Indic, use Indic-aware stacker meta_fusion_indic.json (weights [0.617,−1.226,1.600,0.820,1.156]); fallback heuristic hf_energy_ratio<0.0015. narrowband flag only changes thresholds, not the stacker.
- **Source attribution**: multinomial softmax logistic over 89-dim, classes [ElevenLabs, Tacotron-TTS, In-the-Wild]; fires when score≥0.5. Real but simple 3-class linear.
- **Streaming**: stream_analyze win 3.0s / hop 1.0s / thr 0.70, running=mean(last 3 windows), fast-flag if a single window ≥0.85. /api/live-call SSE uses 2.5s window / 1.0s hop.

## Models (real) + devices
- 3 HF deepfake pipelines via transformers.pipeline("audio-classification", model=ID) — **no explicit device** (transformers default; effectively CPU). Lazy-load, serialized by _LOAD_LOCK to avoid MPS init race. IDs: MelodyMachine/Deepfake-audio-detection-V2, Gustking/wav2vec2-large-xlsr-deepfake-audio-classification, Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild.
- Liveness/digit ASR: transformers Whisper base.en → tiny.en fallback; Silero VAD gate before Whisper (prevents hallucinated digits on silence); decoding capped (max_new_tokens=32).
- Multilingual scam ASR: openai-whisper "small" (base mis-decodes Hindi→Urdu).
- ECAPA speaker verification: speechbrain/spkrec-ecapa-voxceleb, **192-D** embedding, CPU, cosine, verify threshold 0.18. Real. Decisions VERIFIED / REJECTED-CLONE / REJECTED-IDENTITY. Enrollment store in-memory only.
- Language-ID: openai-whisper "base".
- Fine-tuned xlsr_antispoof (1.18 GB) exists locally but is gitignored and NOT baked into Docker — roadmap asset, not deployed.

## Backend (real)
- Single FastAPI app (app.py), version 3.0.0. ~30 endpoints (analyze, stream-analyze, live-call SSE, enroll, verify-speaker, liveness/new+verify, analyze-call [Digital Arrest Shield], localize, why-fusion, audit, action, stress-test, health, /ws/call/{room} WebRTC signaling, page routes).
- Audio via multipart UploadFile; WebSocket only relays WebRTC signaling (audio is peer-to-peer, never through server).
- Concurrency: in-process only — ThreadPoolExecutor per request (detectors run concurrently), run_in_threadpool offloads blocking ML off the event loop. Model warmup on startup in a daemon thread.
- SHA-256 audit hash **truncated to 16 hex chars (64-bit)**; audit is an in-memory list capped 200, returns 50. NOT immutable, NOT persisted.
- **NO auth, NO CORS, NO rate-limiting, NO RBAC** — all endpoints open.
- **NO database** — all state in-memory (AUDIT, _ENROLLED, ACTIONS, BLACKLIST, CHALLENGES, ROOMS, _RING), lost on restart, not shared across workers.
- Launch: single-process uvicorn (run_voxshield.sh, NO --workers; auto-restart on OOM). run_https.sh = self-signed cert on LAN for two-phone demo.

## Deployment (real)
- Dockerfile: python:3.10-slim, **CPU torch** (no CUDA/MPS), bakes 4 models (3 classifiers + whisper-base.en) into HF_HOME at build time → no runtime download. EXPOSE 7860. Does NOT bake ECAPA/LID/xlsr_antispoof.
- deploy/vps/deploy_vps.sh: apt + venv + CPU torch, adds 4GB swap if RAM<6GB, **systemd** service (127.0.0.1:8000, Restart=always) + **Caddy** reverse proxy (:80 plain HTTP; HTTPS only if operator edits Caddyfile). Public Vultr box.
- DEPLOY.md paths: Mac+ngrok (demo), HuggingFace Spaces (Docker CPU free), Render/Railway/Fly (Docker CPU paid).
- Footprint: backend 2.2 GB; artifacts 1.2 GB (mostly xlsr_antispoof, local-only).
- Load test: simulate_load.py (concurrent multipart POST flood) — real.

## REAL vs SLIDEWARE (critical honesty table)
- REAL in code today: 5-detector fusion + calibration + SHAP; channel-aware thresholds; liveness challenge-response (Whisper + Silero VAD + timing); ECAPA enroll/verify; fraud-ring linkage; Digital Arrest Shield (scam-intent + stage tracker Authority→Threat→Isolation→Extraction, English/Hindi/Hinglish); citizen warning (call 1930); source attribution; partial-fake localization; SHA-256 audit; Docker model-baking; systemd+Caddy VPS; load simulator.
- SLIDEWARE / ABSENT (deck marketing only, NO code): JWT/OAuth/API-keys/auth, rate-limiting, RBAC, CORS, AES-256 at rest ("AES-256-ready"), TLS 1.3 pinning, HSM, SIEM, SOC/SOC2, Zero-Trust, immutable/persisted audit, ANY database, Redis/Kafka/RabbitMQ/Celery/queue, Kubernetes/nginx/autoscaling/GPU-cluster/load-balancer, multi-worker deployment, CI/CD (.github), automated test suite, air-gapped deployment (not actually documented/supported despite deck claim).
- TRL-5 (validated working system). The 12-sector expansion, managed-service SLAs (99.9%, <300ms), SOC2/ISO27001 are TARGETS not facts. The "100% Indic fine-tune recall" has NO committed artifact — cite 42→82% routed instead.

## Roadmap (honest)
- Close benign-DSP robustness gap (pitch/tempo/noise) via matched augmentation + deploy the fine-tuned XLS-R+AASIST Indic head (the 1.2GB local model).
- Real persistence (DB) + auth (API keys/JWT) + rate-limiting + CORS — none exist yet.
- Multi-worker / horizontal scale (currently single process), GPU batching (currently one clip at a time, no device/batch), containerized queue for concurrency.
- White-box adversarial (FGSM/PGD) hardening — stated roadmap, not covered.
- Pilot on recorded IVR traffic (TRL-6) → harden for India (TRL-7).

## ============ CURRENT LIVE SYSTEM (updated — use these) ============
- **Live & deployed:** public HTTPS at https://64.177.121.208.sslip.io (Vultr VPS, Ubuntu, AMD EPYC, 4 vCPU / 7.2 GB RAM + 8 GB swap, ~$25/mo). Caddy auto-HTTPS + coturn TURN relay. Single-process FastAPI/uvicorn, systemd auto-restart.
- **Live latency (measured on the VPS):** detection ~1.7–2.1s (genuine 1.67s, clone 2.08s), speaker verification ~1.5s, arrest-shield ~4–5s, localize ~4.5s, stress-test ~5.5s. RAM ~4–5 GB with all models loaded.
- **★ OUR CUSTOM INDIC MODEL (trained by the team, deployed live):** fine-tuned facebook/wav2vec2-xls-r-300m (300M params) on 4,000 IndicVoices genuine (AI4Bharat) + 4,000 MMS-TTS synthesized Indic fakes, 10 languages. 3 epochs, batch 8, lr 1e-5, RawBoost+codec aug. Trained on a rented RTX 5090 (~30 min, ~$2), saved to HuggingFace (dg10911/voxshield-indic-xlsr). Deployed as an env-gated Indic-routed BOOSTER (VOXSHIELD_INDIC_BOOST): only raises the score on confident Indic fakes (>=0.85), so it adds recall without adding false positives. Held-out Indic eval: **0% false positives on real Indian speakers, 100% recall on the trained (MMS-TTS) engine**. Verified live: genuine Tamil -> LOW 0.06; Tamil fake -> HIGH 1.0 with "+indic-boost". HONEST CAVEAT: the 100% is in-distribution (MMS-TTS); real-world coverage broadens as more TTS engines (ElevenLabs, NVIDIA) are added; pipeline is committed (INDIC_GPU_RUNBOOK.md).
- **faster-whisper** (CTranslate2 int8) now powers the scam/multilingual ASR (~4x faster than openai-whisper, same Hindi accuracy).
- **Feature bank:** 89-dim = LFCC 40 (n_lfcc=20 mean+std) + CQCC 40 + 9 scalars (hf_energy_ratio, hf_regularity, spectral_flatness, phase_reg, f0_jitter, shimmer, f0_voiced_ratio, silence_ratio, breath_score). SR=16kHz; 8kHz is a detected channel flag.
- **Model params:** XLS-R-300M ~300M; wav2vec2-base (Deepfake-V2) ~95M; DistilHuBERT ~24M; ECAPA-TDNN ~22M; Whisper base ~74M / small ~244M; MMS-TTS ~145M each; Silero VAD tiny.
- **Voice-cloning pipeline (for teaching):** reference audio (3-10s) -> speaker encoder (voiceprint embedding) -> acoustic model (TTS: VITS/Tacotron/VALL-E, or Voice Conversion) -> neural vocoder (HiFi-GAN/WaveNet/WaveGlow) -> waveform. The vocoder leaves artifacts (regular phase, oversmooth >6kHz energy, missing jitter/shimmer/breath) that detectors read.
- **Audio: G.711** µ-law = 8kHz telephony codec, band-limits to ~3.4kHz, destroys >4kHz vocoder artifacts. Studio = 48kHz (up to 24kHz). VoxShield trains with G.711/Opus/MP3 codec augmentation -> phone-hardened (Opus improves, G.711 only +7.5 pts EER).
- **Competitors:** Pindrop Pulse (99% w/ MFA, 2s, banks, English/cloud), Reality Defender (98.5%, multimodal, govt/cloud), aivoicedetector (99% clean, 0.48s GPU). None do Indic + on-prem + liveness + scam-intent. VoxShield ~94% honest (5.9% EER) but owns the Indian-telephony niche.
