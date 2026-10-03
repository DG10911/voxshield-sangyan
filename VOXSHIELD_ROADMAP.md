# VoxShield — Complete Master Roadmap
### THE single source of truth. All prior work + all merged requirements, integrated. Not a second roadmap.

**Status:** `[DONE]` in-repo & runs · `[PARTIAL]` partly built · `[HYP]` built but unvalidated hypothesis · `[TODO]` scoped, not started · `[FUTURE]` deferred by design
**Priority:** `P0` now · `P1` next · `P2` soon · `P3` later · `P4` long-term
**Standing rules (IMPLEMENTATION RULES §49):** inspect before adding · never duplicate · reuse interfaces · test every major component · isolate research from production · deterministic/auditable prod inference · never silently modify weights · **never train production from live traffic** · every model/dataset carries version+provenance+license/consent · every benchmark records exact scenario · always separate result/hypothesis/target · **never cite the contaminated in-corpus ~0%** · **never treat UNKNOWN as HUMAN** · **never auto-block on a score** (REVIEW/step-up only) · preserve explainability · optimise unseen-generator robustness · test unusual humans hard · privacy & security first-class.

---

## 1 · Vision
**Voice Trust Infrastructure.** North Star: *"VoxShield determines whether a voice interaction can be trusted."* Target: *any voice, language, device, environment, channel, generator, attack* — a long-term research/product **target, not a current claim**. It must reason about human/AI/TTS/cloning/VC/S2S/AI-agents/replay/hybrid/partial/unknown-generators/unknown-attacks/environment/telephony/capture-chain/cross-lingual/identity/conversation/network — well beyond a binary classifier.

## 2 · Current System (real today) — PRESERVED, do not overwrite
`[DONE]` 8 kHz G.711 μ-law ingest → Silero VAD → 3 s window / 1 s hop → normalize → 16 kHz mono → **89-dim feature bank** (LFCC, CQCC, group-delay phase, F0, jitter, shimmer, HF>6 kHz) → **5 detectors** (Acoustic DSP, wav2vec2, XLS-R-53, DistilHuBERT, LFCC+CQCC head) → **learned fusion + Platt calibration + reason codes + verdict** → Indic/telephony/general routing (`_meta`/`_meta_indic`/`_meta_narrowband`, partial) → telephony augmentation · System-B XLS-R leakage-fixed trainer (`backend/pipeline/train_corpus.py`).
`[HYP]` **VoxScore + abstain** (`backend/voxscore.py`).
**Measured `[PROJECT RESULT]` (keep separate from hypotheses/targets):** fusion **5.9% EER** held-out ITW · **6.8% EER / 0.98 AUC** OOD unseen-generator (MLAAD) · Indic recall **42→82%** · genuine-Indic FP **11.7→6.3%**. In-corpus ~0% = **leakage, NEVER a performance claim.**

## 3 · Architecture (unified target — build toward this)
```
AUDIO → Universal Input Profiler → { Fast Detector(L0) | Evidence Brains | Novelty }
      → Evidence Arbitration → VoxScore → { HUMAN | AI/FAKE | UNKNOWN }
UNKNOWN → Unknown Vault → Generator Hunter → Threat Registry → Generator Graph
      → Governed Learning Engine → Challenger → Golden/Zero-Day → Shadow → Production
```
Four explicit layers (never conflated): **Generators** (§4) → **Attack Modes** (§5) → **Attack Recipes** (§6) → **Scenario Graph** (§7).

## 4 · Generator Capability Registry `[DONE]` (`registries.py` + `registries/generators.json` — 20 versioned entries, ~30-field schema, cross-ref validation)
Versioned registry (same provider ships many models). **Schema per entry:** provider · model · version · release_date · api|local · tts · zero_shot_tts · few_shot_tts · voice_cloning · voice_conversion · speech_to_speech · voice_design · emotion_control · multilingual · cross_lingual_cloning · realtime · reference_audio_req · max_len · output_srs · output_codecs · watermark/provenance · license · commercial_availability · date_tested · detection_perf · unseen_behavior · telephony_robustness · replay_robustness · known_failure_modes.
**Seed set:** ElevenLabs · Fish Audio · Cartesia Sonic · Hume Octave · PlayHT · Qwen3-TTS · VoxCPM2 · LongCat-Audio · Higgs Audio · VibeVoice · XTTS · XTTS-v2 · GPT-SoVITS · F5-TTS · StyleTTS2 · CosyVoice · OpenVoice · VoiceStudio · +future. (Access legally; respect API terms/rate limits.)

## 5 · Attack Mode Registry `[DONE]` (`registries/attack_modes.json` — 22 modes)
Every experiment names its mode: TTS · zero-shot TTS · few-shot TTS · voice cloning · voice conversion · speech-to-speech · voice design · emotion-controlled TTS · cross-lingual cloning · long-form · real-time · AI-agent speech · conversational AI · replayed AI · replayed human · partial splice · human→AI · AI→human · genA→genB · AI→codec→replay · human→recording→replay · hybrid human/AI.

## 6 · Attack Recipe Registry `[DONE]` (`registries/attack_recipes.json` — 17-dim recipes, cross-ref validated)
Reproducible recipe = Generator × Version × Attack-Mode × Speaker × Language × Accent × Style × Emotion × Device × Microphone × Distance × Environment × Noise × Codec × Network × Replay × Manipulation. (e.g. *ElevenLabs × clone × Hindi × Bihar accent × emotional × Android × cheap mic × 50 cm × street × G.711 μ-law × packet-loss × speakerphone-replay*.) Foundation of the eval system.

## 7 · Generator × Scenario Graph `[DONE]` (`dataset_schema.py` scenario-graph schema + `scenario_render.py` edge transformations)
Not `real/ fake/`. Nodes = generator·version·voice·speaker·language·accent·device·mic·environment·codec·network·attack·replay·style·emotion; **edges = transformations** (e.g. `speaker→clone→Hindi TTS→emotional→G.711→noisy→replay`). Supports reproducible scenario generation (drives §33 Scenario Generator).

## 8 · Detection Science (the brains) — evidence sources, none standalone
- `[DONE]` Acoustic DSP · wav2vec2 · XLS-R-53 · DistilHuBERT · LFCC+CQCC · 89-dim bank · meta-stackers
- `[DONE]` **Universal Input Profiler** (`profiler.py`, §8→routes cascade) · **Fast Detector L0** (`fast_l0.py`, <300 ms target)
- `[DONE]` **AI-Agent / BotGuard Brain** (`botguard.py`) · **Novelty/Open-set Brain** (`voxscore.py` novelty/abstain) `[HYP]`
- `[DONE]` **Watermark-Agnostic** benchmark (`eval_watermark.py` — real±wm / fake±wm shortcut check)
- `[DONE]` **Partial Deepfake Segmentation** + **Generation Boundary Detector** (`segment.py`) `[HYP]`
- `[DONE]` **Speaker Identity Brain** (`speaker.py` embeddings/verify/cross-lingual) + **`speaker_engine.py`** (provider-agnostic: **SpeechBrain ECAPA** / **NeMo TitaNet** / **Phonexia** API / local fallback — auto-selected) · **`diarization.py`** (**pyannote 3.1** / **NeMo Sortformer** / built-in VAD+clustering fallback). *Replaces the broken Bhashini diarization path (see `VOXSHIELD_SPEAKER_PROVIDERS.md`); install pyannote/ECAPA on the DGX for SOTA.*
- `[DONE]` **All-Type Audio** (`alltype_audio.py` speech/singing/music/env/mixed router) `[HYP]` · `[FUTURE] P4` **Audio-Visual Consistency Brain** (needs video)

## 9 · Human Physics Engine `[DONE]` (`physics.py` → HPCS; `[HYP]` until validated on real data)
Question: *could a living human, in this environment, through this capture chain, produce this exact sequence?* Modules: **Glottal Dynamics** (open/closed quotient, pulse, excitation, periodicity, spectral tilt, trajectory) · **Breath/Physiology** (inhale/exhale, respiratory pauses, breath spectral sig, breath-prosody coupling, phrase-length) · **Micro-Articulation** (formant traj, phoneme transitions, onset/offset, timing, phase, energy) → **ATR** · **Human Microvariation** (F0/jitter/shimmer/energy/phase → entropy/recurrence/autocorr/temporal structure) → **HMS**. Metric: **HPCS**. No single feature proves AI.

## 10 · Replay / Environment / Capture + Phase/Temporal Forensics
- `[DONE]` **Replay Forensics** (`replay.py`) — live/recorded/AI/AI-replay/hybrid → **Double-Transmission Signature** `[HYP]`
- `[DONE]` **Environment Forensics** (`environment.py`) → **SVCS** + rt60 + **Capture-Chain Consistency** `[HYP]`
- `[DONE]` **Phase Trajectory** (`phase_traj.py` — group delay/curvature/cross-band/topology → PTS) · **Cross-Codec** (§11) · **Reverse-Time** (`reverse_time.py`) · **Temporal Voice DNA** (`temporal_dna.py`) — all `[HYP]`
- `[DONE]` **Cross-Language Speaker Physics** (`speaker.cross_lingual_continuity`) · **Code-Switching Forensics** (`codeswitch.py`) `[HYP]`
- `[DONE]` **Conversational Forensics** (`conversational.py` — Human Timing Complexity + Semantic↔Prosody + Voice Conservation) · **Counterfactual/CAD** (`causal_probe.py`) — evidence-only, never standalone `[HYP]`

### 11 · Cross-Codec Forensics `[DONE]` (`crosscodec.py` — μ-law/narrowband/decimate residual fingerprints) `[HYP]`
Run through G.711 μ/A, Opus, AMR, AAC, PCM, unknown; compare residuals/representation change; test whether codecs expose synthetic/generator-specific residual structure (esp. telephony).

## 12 · Open-Set / Zero-Day `[DONE]` (THE #1 PRIORITY — voxscore novelty/abstain + eval_gengap measured + unknown_vault; only the novelty-vs-fusion validation is GPU-parked)
Handle {known/unknown} × {human/AI} + unknown-attack + unknown-generator; **UNKNOWN must not become HUMAN**. Implement: novelty score · embedding distance · density estimation · open-set classifier · unknown vault (§16) · generator hypothesis · cluster discovery. Core benchmark = **Generalization Gap** (known−unseen) via `eval_gengap.py` `[DONE + REAL DATA: UNSEEN 9.95% EER, gap +9.95pts, mean-LOGO 6.58% on DGX]`; **validate voxscore novelty vs MLAAD-unseen `[GPU-PARKED]`** (needs 5-detector fusion scores).

## 13 · VoxScore 2.0 / Evidence Arbitration
- `[HYP]` current: {authenticity, evidence_confidence, distribution_confidence, novelty, risk, abstain} — `backend/voxscore.py`; **wired into `app.py` (additive field) + console VoxScore panel + ABSTAIN banner `[DONE]`**
- `[DONE]` **VoxScore 2.0 schema** (verdict HUMAN/AI/REPLAY/HYBRID/UNKNOWN + sub-scores + abstain; brains slots filled by `orchestrate.py`):
```json
{ "verdict":"HUMAN|AI|REPLAY|HYBRID|UNKNOWN",
  "detection_confidence":0,"evidence_confidence":0,"distribution_confidence":0,"novelty":0,
  "human_physics_score":0,"synthetic_score":0,"replay_score":0,
  "environment_consistency":0,"capture_chain_consistency":0,"speaker_consistency":0,
  "reason_codes":[],"abstain":false }
```
UNKNOWN + abstain are first-class valid results.
- `[DONE]` **Evidence Arbitration Brain** (`arbitration.py`) over independent brains; weights by **evidence diversity (HEDS)** — collapses correlated SSL to one family so they can't outvote independent physical evidence.
- `[DONE]` **Self-Critique** (`self_critique.py`) — asymmetric FP-guard: before a HIGH/AI verdict runs counter-tests (unusual human/accent/elderly/emotional/bad-mic/codec/replay/unknown-gen/noise/speakerphone/code-switch → lowers confidence or forces ABSTAIN) `[HYP]`.
- `[DONE]` reason codes · **Detector Cascade L0–L3** (`cascade.py` — L0 fast_l0 · L1 physics+phase · L2 fusion+voxscore · L3 full brains+arbitration+self-critique; targets <300 ms / ~1 s / ~3 s / <5 s, not claims).

## 14 · Dataset Engine `[DONE]` (`dataset_schema.py` — scenario-graph schema + validator; `scenario_render.py` renders channel/replay/env conditions)
Scenario-graph-first, metadata-first. **Schema (§34):** sample_id, speaker_id, language, accent, gender, age_group, generator, generator_version, voice_id, attack_mode, device, microphone, environment, distance, codec, sample_rate, network_condition, noise_condition, style, emotion, replay, splice, attack_type, label, label_confidence, provenance, license, consent, split, timestamp. **Labels:** HUMAN, AI_GENERATED, VOICE_CONVERSION, TTS, CLONED, REPLAY_HUMAN, REPLAY_AI, AI_AGENT, BOT, HYBRID, SPLICED, UNKNOWN. Active-learning + diversity (max info-gain/hour). Never blindly merge datasets.

## 15 · India-First Corpus `[PARK] P2` (real data collection — needs consented recordings; schema/manifests ready in §14/§16)
22 scheduled languages (Hindi/Tamil/Telugu/Bengali/Marathi/Gujarati/Kannada/Malayalam/Punjabi/Odia/Assamese/Urdu/…) + regional accents/dialects + code-switching + age/gender/style/pitch diversity. **Measure detection per language ≠ ASR/TTS coverage.** Do not treat unusual human speech as suspicious.

## 16 · Golden / Zero-Day / Nightmare / Worst-Human / Worst-AI
- `[DONE]` **Golden Set** + **Zero-Day Set** contract (`goldenset.py` — frozen, never_train enforced, full-slice coverage + provenance/consent). *Population with real clips = external data collection.*
- `[DONE]` **Worst-Human** manifest (`dataset_schema.worst_human_manifest` — rare accent/stutter/breathy/emotional/elderly/poor-mic/… → minimise FP).
- `[DONE]` **Worst-AI** manifest (`dataset_schema.worst_ai_manifest` — **seeded from measured hardest generators** griffin_lim/bark/lemas/rvc → maximise UGR).
- `[DONE]` **Nightmare** manifest + renderer (`dataset_schema.nightmare_manifest` + `scenario_render.nightmare_scenario` — the §32 combinatorial worst-case).

## 17 · Unknown Vault `[DONE]` (`unknown_vault.py` — consent-gated metadata + embedding clustering → research candidates)
Every interesting unknown stored as metadata (consent/privacy/license-gated): sample_id, embedding, language, accent, device, channel, environment, speaker, generator_hypothesis, detector_outputs, novelty, scenario, timestamp, provenance, license, consent. Cluster → research candidates.

## 18 · Generator Hunter `[DONE]` (`generator_hunter.py`)
Autonomous: unknown → novelty → cluster → representation analysis → compare known gens → hypothesize family → attack recipe → benchmark → registry → challenger training → validation. **Never auto-modify production models** (enforced: `auto_promote=False`, must pass flywheel gates). *Real challenger training = GPU.*

## 19 · Voice Threat Registry `[DONE]` (`threat_registry.py` — seeded from measured LOGO; upsert/query/hardest; persists registries/threats.json)
Living intel: generator, version, attack method, language, accent, codec, device, environment, replay, observed artifacts, detection perf, last/first tested, confidence, evidence, source, provenance.

## 20 · Generator Intelligence Graph `[DONE]` (`intel_graph.py` — queryable; served at `/api/intel`)
Graph: Generator→Version→Voice→Attack-Mode→Language→Codec→Device→Environment→Artifact→Detector→Failure-Mode. Queryable ("which gens are hard under Tamil+G.711+speakerphone?" / "which conditions cause highest FN?").

## 21 · Autonomous Learning Flywheel `[DONE]` (`flywheel.py` — governed state machine, ordered gates, live can't bypass to prod)
LIVE CALL → streaming detection → VoxScore → novelty → verdict → **verified feedback** → learning queue → data curator → QC → dedup → consent/license → label-confidence → adversarial validation → challenger → Golden → Zero-Day → bias/regression → shadow → promotion. **Hard rule: live traffic generates candidates only; NEVER rewrites production directly.**

## 22 · Evaluation / Master Matrix `[DONE]` (`eval_matrix.py` — multi-axis EER + cross-tabs + worst-cells + gap; never one aggregate number)
**Master Evaluation Matrix** = Generator × Version × Language × Accent × Device × Environment × Channel × Codec × Distance × Style × Replay × Manipulation. Nightmare Evaluation = automated worst-case (detection+latency+confidence+evidence-diversity+calibration+failure-reason). **Never one aggregate number.**

## 23 · Device / Environment / Distance / Channel Matrices
- `[DONE eval-code]` **Channel** matrix (`eval_channel.py` — per-channel EER + degradation; `scenario_render.py` synthesises codec/loss/jitter cells). *Real PSTN/SIP/device/room recordings = external data collection.*
- `[TODO external-data] P2` **Device** · **Environment** · `P3` **Distance** matrices — eval harness exists (§22); needs real captured recordings across the device/room/distance axes.

## 24 · MLOps / Security / Privacy `[DONE]`
- `[DONE]` **MLOps** (`mlops.py` — versioned registry, reproducibility fields, shadow-gate, rollback, no shadow-skip to prod) · **Drift monitoring** (`drift.py` — PSI + FPR/FNR/latency)
- `[DONE]` **Privacy** (`security.py` — `privacy_check()` consent-gate, `redact()` PII pseudonymization, retention/minimization controls)
- `[DONE]` **Security threat model** (`security.py` THREAT_MODEL + `self_audit()` — adversarial/extraction/abuse/poisoning/insider/leakage) — treats VoxShield as critical infra.

## 25 · VoiceStudio Generator/Attack Lab `[PARTIAL]` — rendering half `[DONE]` (`scenario_render.py`: Scenario Renderer + Codec/Telephony Sim + Replay/Env Sim); AI-generation backend `[PARK]` (needs external generators)
VoiceStudio = generation backend, **not** the detector. Flow: VoiceStudio → Generator Adapter → Attack Recipe → **Scenario Renderer → Codec/Telephony Sim → Replay/Env Sim `[DONE]`** → VoxShield → Benchmark. **AGPL — clean API/service boundary, legal review, no code copy, track model/license provenance.**

## 26 · VoiceLink Telephony Lab `[PLAN-READY] P3` (concrete cheap+legal path — see `VOXSHIELD_VOICELINK.md`; gate = `voicelink_readiness.py`)
**Provider:** Exotel AgentStream / Plivo Audio Streaming + **Pipecat** (8kHz G.711, WebSocket → `/api/ws-stream`, ~₹0.94/min, <300ms). **Legal path:** consented volunteers only → NO DLT (one-party consent + disclosure); POC 100 calls ≈ ₹500–2,000. **Scale:** FreeSWITCH `mod_ws_media`. **Highest-leverage resource: Indic-CodecFake + SATYAM (~98.32%, 12 Indic langs) + AI4Bharat partnership (ai4bharat@iitm.ac.in, Bhashini data) + govt Responsible-AI grants (IIT Kgp / Saakshya).**
Pipeline: AI Generator → Voice Agent → VoiceLink/SIP → Indian telecom → real device → mic/speakerphone → VoxShield. **Verify first (25 questions):** SIP/RTP/WebSocket/raw-audio/8k/16k/G.711 μ&A/bidi-stream/timestamps/events/recordings/metadata/retention/webhooks/concurrency/sandbox/test-numbers/inbound/outbound/custom-SIP/API-limits/research-partnership/consent-data. All customer data under explicit consent/contract/privacy.

## 27 · BHASHINI / ULCA Indic Lab `[LIVE · APPROVED]` (access granted 2026-09-14)
**Account:** Bhashini Udyat approved — **2,000 API calls**, manager Divya Goswami, CEO-approved 14-09-2026. Services: ASR · NMT · TTS · TLD · ALD · OCR · VAD · NER · GC.
**API model:** two-call ULCA flow — **Pipeline Config** (`POST https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline`, headers `userID`+`ulcaApiKey`) → returns `serviceId`/`modelId` + `pipelineInferenceAPIEndPoint.callbackUrl` + `inferenceApiKey` → **Pipeline Compute** (`POST https://dhruva-api.bhashini.gov.in/services/inference/pipeline`, header `Authorization: <key>`). Public pipeline IDs: IITM `660fa5bec7fb5b0328229016` · IITB `660f813c0413087224435d2c` · IIITH `660f866443e53d4133f65317` · Initial `64392f96daac500b55c543cd`.
**Code `[DONE]`:** `backend/bhashini.py` — real ULCA client: `config · asr · translate · synthesize · transliterate · ner · ocr · denoise · voice_clone · detect_audio_language · detect_text_language · diarize_speakers · diarize_languages · speaker_enroll · speaker_verify · stream_asr` + 15-group Service-ID catalogue + **call-budget tracker/retries/cache**. **Wired into `orchestrate.py`** (`use_bhashini` auto via `BHASHINI_ALWAYS=1`; transcript→`conversational.text_forensics`; optional diarization) and `/api/analyze?bhashini=true`; `/api/health` shows mode+quota; console has **"Run live on a clip"**. `backend/bhashini_livetest.py` — per-service live harness. Self-tests PASS.
**How Bhashini powers the detector (not a detection claim — routing + evidence):**
- **ALD → Universal Input Profiler (§8):** detect the spoken language of an incoming call → route to the right language scorecard / brain weights.
- **ASR → Conversational + Semantic↔Prosody brain (§10) and Causal probe:** transcript to test semantic↔prosody consistency and contradiction.
- **TLD → text-language routing** for any text channel; **NMT + Transliteration → cross-lingual clone pipeline (§37.3)** (EN→Indic before TTS).
- **Speaker enrollment/verification + Speaker/Language diarization → Speaker Identity Brain (§8)** (multi-speaker/replay detection).
- **TTS + Voice-Cloning (`bhashini/ai4b/indicf5-tts`) → Worst-AI generation (§16/§37.3)** — produce Indic attack clips to attack/train the detector.
**Cross-link:** Bhashini exposes the same underlying models that AIKosh (§38) distributes as downloadable assets (IndicConformer, IndicTrans2, IndicXlit, IndicF5, IITM/IISc/Coqui TTS) → **AIKosh = self-hosted weights/data; Bhashini = managed inference API (2,000-call budget).** Use AIKosh to train/own the model, Bhashini for fast generation/routing/enrichment without hosting.
**VERIFIED LIVE (2026-10-01):** app `suvidha` — Pipeline Config ✅ (returns asr `ai4bharat/conformer-multilingual-indo_aryan-gpu--t4`, translation `ai4bharat/indictrans-v2-all-gpu--t4`, tts) · **TLD** ✅ (`mai`, Deva, 0.999) · **ALD** ✅ (`hi`, Deva, 1.0) · **TTS** ✅ (48 kHz Hindi WAV) · **ASR** ✅ (correct transcript of the TTS audio). Credential mapping: `userID` = the account UUID, `ulcaApiKey` = the "Udyat Key", `BHASHINI_INFERENCE_KEY` = the "Inference" value (used directly against Dhruva).
**End-to-end `[DONE]`:** `backend/demo_telephony_bhashini.py` — Bhashini TTS → `scenario_render` G.711 μ-law + band-limit + noise @8 kHz → `orchestrate.run(..., use_bhashini=True)` → pipeline `profiler → fast_l0 → brains → **bhashini(ald+asr)** → detectors+voxscore → arbitration`; **language `hi` (ALD)** and the Hindi **transcript** surfaced.
**Surfaces `[DONE]`:** `/api/analyze?bhashini=true` now returns `language` + `transcript` + `bhashini` (opt-in) · **console panel** `BHASHINI · INDIC LANGUAGE & TRANSCRIPT` in `voxshield_console.html` (ALD language + confidence + ASR transcript, pipeline chip `bhashini(ald+asr)`) · `speaker.py` adds `enroll()` + `verify_against_enrolled()` + `verify_speaker()` · `backend/gen_worst_ai.py` (NMT→TTS/IndicF5→telephony **Worst-AI generator**).
**DGX A100 — VERIFIED END-TO-END (2026-10-01):** `orchestrate.run(use_bhashini=True, use_diarization=True)` ran `profiler → fast_l0 → brains → bhashini(ald+asr) → conversational(transcript) → diarization(nemo-sortformer)` on a real clip — **Bhashini ALD `hi`**, correct **ASR transcript**, **NeMo Sortformer 2-speaker** diarization, **ECAPA** verification (SAME 0.40/DIFF 0.22 @0.35). Providers: `diarization.py` (pyannote→nemo→**deepgram**→light) · `speaker_engine.py` (ecapa→nemo→phonexia→local) · `backend/dgx_e2e.py` · `VOXSHIELD_DGX_RUNBOOK.md`.
**Speaker services — status:** **enrollment ✅** (`speakerId` issued; "Speaker enrolled successfully"). **Verification ✅ on speech-like audio** — cross-clip same-speaker verified at **confidence 0.97**; **⛔ TTS-synthesized audio** yields an unverifiable profile (`HTTP 400 "Speaker not found"`) → use **real consented human clips** (see `backend/enroll_speaker.py`). **Root cause found: reusing a `speakerName` makes enrollment 400** → the code now always uses a **unique name** (`vx-<uuid>`). Payloads match the official `bhashini-client-sdk` v0.2.5. Local pseudo-embedding remains the fallback.
**Diarization — status:** `speaker-diarization` and `language-diarization` return **HTTP 500 on every service ID / length** (verified server-side) → report to Bhashini (digitalindiabhashinidivision@gmail.com).
**Rules:** ULCA APIs are **PoC-only** (production ⇒ Bhashini paid plan); never send real/consented recordings to a shared API — synthetic/public only; **Indic ASR/TTS coverage ≠ Indic deepfake-detection coverage** (separate eval axes).

## 28 · Product Family
- `[DONE]` Detect (`app.py`) · Live (`stream_analyze` + `/api/ws-stream`) · Investigator (`voxshield_console.html`) · Risk Engine/VoxScore (`voxscore.py`)
- `[DONE]` **Detect API** — REST+WebSocket + `/api/threats` · `/api/intel` · `/api/risk/score` · `/api/threat/search` · `/api/gateway/decide` · `/api/deployment/profile` · `/api/warroom` · `/api/consumer/check` · `/api/speaker/verify` · **BotGuard** (`botguard.py`). *Multi-language SDKs (Py/JS/Java/Go) = packaging `[TODO]`.*
- `[DONE]` **CallGuard** · **Voice Identity** · **Transaction Shield** · **Generator Intelligence** · **Cloud/Enterprise/Indic** surfaces (`deployment.py` — deploy-mode + product-profile config, fail-closed invariants).
- `[DONE]` **Red Team** (`redteam.py` — adversarial evasion harness) · **Telephony Gateway** (`telephony_gateway.py` — inline allow/warn/step-up/2FA/transfer, **auto_block always False**) · **Consumer** (`consumer.py` — "Is this voice real?" plain-language) · **War Room** (`warroom.py` — live ops rollup). *Audio-Visual stays `[FUTURE] P4` (needs video).*

## 29 · API / Deployment
`[DONE] P1` REST (`/api/analyze`, `/api/stream-analyze`) + WebSocket (`/api/ws-stream`). **Now also (additive, non-breaking):** every analyze response carries `voxscore` (P0) + `brains`/`arbitration`/`unified_verdict`/`abstain` (P2/P3 evidence-brain pipeline via `orchestrate.py`); new **`/api/threats`** (§19 hardest generators) + **`/api/intel`** (§20 graph queries: `?language=&codec=` hard-under, `?worst_by=` worst-condition). Console `voxshield_console.html` surfaces an **Evidence Brains** panel (physics/time-arrow/trajectory/replay/environment + arbiter verdict) and a **Generator Intelligence** panel (threat registry + graph Q&A). · `[DONE] P2` **deploy modes** cloud/private/on-prem/air-gapped/hybrid/edge (`deployment.py` — data-residency/model-location/telemetry/retention per mode; on-prem/air-gapped/edge fail-closed on external telemetry & model calls) · `[PARK] P3` distillation (teacher→student→edge; ONNX/TensorRT) + cascade for latency/power (GPU).

## 30 · Research Program (classify each: Established/Implementation/Hypothesis/Experimental/Future; verify literature before novelty)
1 Human Speech Physics · 2 Cross-Codec Causal Probing · 3 Voice-Environment Consistency · 4 Compositional Zero-Day Robustness · 5 Physio-Prosodic Consistency · 6 Evidence-Diverse Open-Set Voice Auth · 7 **Real-Time Indic Telephony Deepfake Detection Under Channel Shift** *(closest now)* · 8 Generation-Boundary Detection · 9 Temporal Voice DNA · 10 Replay Physics · 11 Human Microvariation Topology · 12 Generator Intelligence Graph · 13 Scenario-Graph-Based Voice Deepfake Benchmarking.

## 31 · Competitive Intelligence (track gaps, never copy architecture)
Pindrop (Pulse/BotStopper) · Resemble AI Detect · Telnyx Deepfake Detection · Reality Defender · Hiya · STIR/SHAKEN ecosystem · emerging vendors. Track: capabilities/latency/languages/channels/deployment/pricing/generator&deepfake coverage/AI-agent/telephony/identity/fraud-intel. Goal = differentiation.

## 32 · Three-Layer Moat
**L1 Science** (human physics, temporal forensics, open-set, causal probing, replay, environment, cross-codec, multilingual physics) · **L2 Data** (India corpus, generator registry, attack recipes, scenario graph, Golden/Zero-Day/Unknown-Vault/Nightmare) · **L3 Network** (telephony+enterprise integrations, threat intel, verified outcomes, generator intel, ecosystem feedback). Moat ≠ "better neural net."

## 33 · P0–P4 Implementation Plan (merged, dependency-ordered)
- **P0 (DONE ✅):** VoxScore + abstention `[HYP,DONE]` (`backend/voxscore.py`, self-test passes) · **wired into `app.py`** — additive `voxscore` field on `/api/analyze` + `/api/stream-analyze` (existing fields untouched) · **surfaced in console** — VoxScore meta-uncertainty panel (synthetic/evidence/distribution/novelty), REVIEW/ABSTAIN banner, new **ZERO-DAY** demo scenario + call-table row (`voxshield_console.html`, DOM verified) · basic end-to-end decision path intact.
- **P1 (in progress):**
  - ✅ `[DONE + REAL DATA]` **`eval_gengap.py`** — generalization-gap harness, **validated on the DGX over 37,493 scored clips**: SEEN (freevc24, in-corpus)=0.00% (leakage), **UNSEEN (26 MLAAD generators)=9.95% EER, GAP=+9.95 pts, mean-unseen (LOGO)=6.58%**. Hardest unseen: griffin_lim 29.9%, bark 23.5%, lemas-tts 21.2%, rvc 20.3% → priority set for Worst-AI (§16)/Generator Hunter (§18). Easiest: gradtts/supertonic/voxtral/resemble.ai <1.5%, elevenlabs-v3 6.3%. Scores at `~/logs/voxshield/scores.csv` on DGX.
  - ✅ `[DONE]` **Generator Capability Registry** (`registries/generators.json`, 20 versioned entries) · **Attack Mode Registry** (`attack_modes.json`, 22) · **Attack Recipe Registry** (`attack_recipes.json`, schema+recipes) · **`registries.py`** loader/validator (schema + cross-ref validation PASS)
  - ✅ `[DONE]` **VoxScore 2.0 schema** — `voxscore.py` now emits verdict HUMAN/AI/REPLAY/HYBRID/**UNKNOWN**+abstain + sub-score slots (unbuilt brains=null), backward-compatible; auto-flows through `app.py`
  - ✅ `[DONE]` **Universal Input Profiler** (`profiler.py`) — modality/narrowband/codec/SNR/quality/replay-prior (coarse), brains=null; self-test PASS
  - ✅ `[DONE]` **Golden/Zero-Day Set contract + validator** (`goldenset.py`) — frozen + full-slice coverage + provenance/consent enforced; self-test PASS
  - ✅ `[DONE]` **Fast L0** (`fast_l0.py`) — model-free cascade gate (fast-pass low-risk / escalate) · **Replay Forensics** (`replay.py`) — Double-Transmission Signature `[HYP]` · **BotGuard** (`botguard.py`) — behavioural human-vs-agent `[HYP]` · **Partial-deepfake + boundary** (`segment.py`) — timeline segmentation + generation boundaries · **Evidence Arbitration v1** (`arbitration.py`) — family-collapsed diversity weighting + HEDS · **Channel-Matrix eval** (`eval_channel.py`) · **watermark-agnostic** benchmark (`eval_watermark.py`) · **Detect API WebSocket** (`/api/ws-stream` in `app.py`, additive). All self-tests PASS; app.py syntax OK.
  - ✅ `[DONE]` **Master Evaluation Matrix** (`eval_matrix.py`) — multi-axis EER (generator/language/channel/device/env/style/replay/codec) + 2-D cross-tabs + worst-cells + generalization gap in one report.
  - ⏳ `[GPU-BLOCKED]` **validate voxscore novelty** — ONLY remaining P1 item; needs System-A 5-detector fusion scores (`dump_fusion_scores.py` + `validate_novelty.py`) which require the DGX (currently firewalled from user's network segment). Everything else in P1 is DONE.
- **P2 (in progress):**
  - ✅ `[DONE]` **14 modules, all self-tests PASS:**
    - *Science:* `physics.py` (HPCS) · `crosscodec.py` · `environment.py` (rt60/SVCS/capture) · `speaker.py` (verify + cross-lingual) · `codeswitch.py` (continuity-at-switch) — all `[HYP]`; ECAPA `[PENDING]`
    - *Product surfaces:* `callguard.py` (voice+device+network+account+txn) · `voice_identity.py` (enroll/verify; clone→REJECT_SPOOF) · `transaction_shield.py` (verification scales with call-risk × txn value)
    - *Data/governance/ops:* `dataset_schema.py` (scenario-graph + **Worst-AI/Worst-Human/Nightmare** manifests, seeded from measured hardest generators) · `flywheel.py` (ordered gates; live can't bypass to prod) · `mlops.py` (versioning + shadow-gate + rollback) · `drift.py` (PSI/FPR/latency drift) · `security.py` (threat model + consent/PII redaction)
    - *Integration:* **`orchestrate.py`** — the unified pipeline (profiler→L0→brains→voxscore→arbitration→callguard), runs end-to-end.
  - ⬜ `[TODO]` remaining P2 — **only external-resource items left:** India Corpus (data collection) · BHASHINI (API/network) · Voice Agent Lab (needs generators) · Cloud/Enterprise/Indic **deployment** surfaces (packaging/config over built modules) · Device/Env matrix **data** (eval side done via `eval_matrix`).
- **P3 (later):**
  - ✅ `[DONE]` **9 non-GPU modules, all self-tests PASS** (wired into `orchestrate.py`):
    - *Forensic science:* `reverse_time.py` (forward-reverse time-arrow asymmetry) · `temporal_dna.py` (micro-instability trajectory + generation-boundary hints) · `conversational.py` (Human Timing Complexity + Semantic↔Prosody + **Voice Conservation** across turns) · `causal_probe.py` (**Causal-Perturbation** robustness + **Counterfactual/CAD** flip-distance → confidence penalty / abstain, on any scorer callable) — all `[HYP]`, evidence-only, never standalone.
    - *Intelligence layer:* `unknown_vault.py` (§17 — consent-gated unknown metadata + clustering → research candidates) · `threat_registry.py` (§19 — living threat intel, seeded from measured LOGO) · `generator_hunter.py` (§18 — unknown→hypothesis→recipe→threat→**governed challenger**, never auto-promotes) · `intel_graph.py` (§20 — queryable Generator×condition graph: "hard under Tamil+G.711?", "worst codec by FN?").
    - *Scenario rendering:* `scenario_render.py` (§25 local half — codec/telephony/packet-loss/reverb/distance/**replay double-transmission** DSP; renders Nightmare §32 + Device/Channel matrix cells deterministically from any clip; the AI-generation VoiceStudio backend stays parked).
  - ⬜ `[PARK]` remaining P3 — **need GPU/external backends only:** VoiceStudio AI-generation backend (§25, needs generators) · VoiceLink Telephony Lab (§26, needs SIP/telco) · customer adapters · **distillation** (teacher→student→edge, GPU) · War Room / Red Team / Generator-Intel product surfaces (deployment packaging).
- **P4 (long-term):** Audio-Visual consistency (needs video) · Telephony Gateway (inline, never auto-block) · Consumer app · global expansion.

> **GPU-parked tasks (resume when DGX access returns):** validate voxscore novelty (System-A 5-detector fusion scores) · real ECAPA-TDNN speaker embedding (recalibrate 0.92 thresholds) · causal/counterfactual model-logit probing · challenger-model distillation. All scaffolding + governed proposal logic is already built and tested locally; these only need compute/data to execute.

## 34 · Definition of Done (roadmap is "merged" only when ALL are represented)
Every completed feature ✔ · every research direction ✔ · every generator ✔ (§4, versioned) · attack modes per generator ✔ (§5) · scenario conditions per attack ✔ (§6–7) · VoiceStudio lab ✔ (§25) · VoiceLink path ✔ (§26) · BHASHINI Indic path ✔ (§27) · Unknown Vault ✔ · Generator Hunter ✔ · Threat Registry ✔ · Generator Intelligence Graph ✔ · Golden ✔ · Zero-Day ✔ · Worst-Human ✔ · Worst-AI ✔ · Nightmare ✔ · Scenario Generator ✔ · governed autonomous learning ✔ · live isolated from direct training ✔ · open-set ✔ · abstention ✔ · replay ✔ · partial-deepfake ✔ · generation-boundary ✔ · environment/capture ✔ · cross-codec ✔ · cross-language ✔ · AI-agent ✔ · telephony/channel matrix ✔ · device/environment matrix ✔ · research-paper tracks ✔ · metrics defined ✔ · P0–P4 deps explicit ✔ · results vs targets separated ✔. **All present in this document.**

## 35 · Current Metrics (standard + custom, all broken down by language/generator/version/attack-mode/device/codec/environment/replay/style/channel)
Standard: EER · ROC-AUC · PR-AUC · FPR · FNR · precision · recall · F1 · min-tDCF. Custom: **UGR** (Unseen-Generator Robustness) · **HEDS** (Human Evidence Diversity) · **CZDR** (Compositional Zero-Day) · **HPCR** (Human Physical Consistency Rate) · **MTTD-G** (Mean Time To Detect a New Generator) · **Generalization Gap** (known−unseen). **Never one aggregate score.**

## 36 · Future Targets & Open Research Questions
**Targets:** cascade latency <300 ms/1 s/3 s/<5 s · closing the generalization gap · on-device NPU (see Snapdragon submission) · full India-corpus coverage.
**Open questions:** does agreement-based novelty track unseen generators (or need embedding-distance/density)? · are the 5 detectors independent evidence or correlated SSL (HEDS)? · do human-physics signals give *marginal* OOD gains over SSL? · do reverse-time / cross-codec residuals carry real signal? · best abstain thresholds for banking FP tolerance? · which forensic brain most lowers unseen-generator EER per compute?

## 37 · Research-Informed Upgrade Track (field scan 2026-09; 3-agent team 2026-09-30)
Sources: `VOXSHIELD_RESEARCH_2026-09.md` · `VOXSHIELD_VOICESTUDIO_GENERATORS.md` · `VOXSHIELD_THREAT_INTEL.md` · `VOXSHIELD_GPU_RENTAL.md`. ⚠️ Lead-sheets — verify arXiv links/product specs before citing.

### 37.1 Detector upgrades (all TRAINING-side → 🅿️ GPU)
- `[PARK-GPU] P1` **XLS-R-300M + SLS** front-end (~1.92% EER, codec-robust; +15–20% rel). `[PARK-GPU] P1` **RawBoost** augmentation (+27% on telephony/codec — highest Indic value) + test-time **LoRA** (8.84→5.30% unseen). `[PARK-GPU] P2` **AASIST3 / XLSR-AASIST** back-end (de-facto SOTA baseline). `[PARK-GPU] P3` **Gaussian-Process few-shot** adapter (21.67→10.42% from ~96 samples). `[PARK-GPU] P2` adversarial training (FGSM/PGD/C&W). **Serving/eval scaffolding already supports drop-in.**
- ✅ `[DONE]` **Cascade** (SOTA rec #4) — `cascade.py`; **SASV** (detect+verify) — `voice_identity.py`; **streaming/frame** detection — `/api/ws-stream`; **challenge-response** hook — gateway `step_up_verification`.

### 37.2 Datasets to pull (🌐 external, via `corpus_ingest.py`)
> **AIKosh (§38) is a primary distribution channel for the Indic sets below** — pull IndicVoices/IndicVoices-R, tribal-language corpora, and the 23-language pretraining corpus through its signed-URL API rather than scraping HF where an AIKosh copy exists.
- `[TODO-DATA] P1` **RTCFake** (600 hrs codec-compressed RTC — offline 95% → live <55%; **our real threat surface**, HF `JunXueTech/RTCFake`). `[TODO-DATA] P1` **IndicSynth** (4000 hr/12 langs) · **IndicFake** (7350 hr/17 langs) · **Indic-CodecFake** · **IndicVoices-R** (genuine, 22 langs → Worst-Human). `[TODO-DATA] P2` **ASVspoof 5** (2025). *Indic deepfake-detection data is <1yr old = our research opening.*

### 37.3 VoiceStudio generators to install (🌐 GPU; adapters ✅ ready in `generator_adapter.py`)
- `[TODO-INSTALL] P1` **IndicF5** (Apache, 11 Indic, 🥇) · **Indic-Parler-TTS** (Apache, 21 Indic) · **Fish-Speech-S2** (9 Indic, cross-lingual). `[TODO-INSTALL] P2` XTTS-v2 · CosyVoice2 · Qwen3-TTS. **Avoid:** MMS-TTS (non-commercial), VibeVoice (watermarked). Generate clean → degrade via `scenario_render.py` (G.711/band-limit/loss) → Worst-AI set. ✅ `[DONE]` **Registry entries added** to `registries/generators.json` (28 total: +IndicF5, Indic-Parler-TTS, Fish-Speech-S2, Sarvam, RVC, Seed-VC, Piper, Kokoro).

### 37.4 Threats to simulate → Attack Mode/Recipe registries
- ✅ `[DONE]` **attack modes added** to `registries/attack_modes.json` (26 total: +realtime_vc, agent_vishing, indic_cross_lingual_clone, codec_rtc). Track: Fraunhofer SIT, ASVspoof organizers; startups isVerified/Aurigin/Sumsub.
- ✅ `[DONE]` **Language coverage registry** `registries/languages.json` — all 22 Eighth-Schedule languages + Indian English, with script/family + per-language coverage (genuine_data / clone_generator / tts_generator / **detection_tested**). "Mastery" = detection_tested=True; currently 0/23 tested (data+generators ready, detection pending GPU). This is the India-First §15 tracker.

### 37.5 Compute plan
- ✅ `[DONE]` **Vast.ai runbook** (`VOXSHIELD_GPU_RENTAL.md`) — pick RTX 4090 interruptible (~$0.20/hr, ~$7–10/run); **never upload consented audio to rented host** (synthetic/public only; real Indic stays on DGX); hybrid: prototype on Vast, final train on DGX. `[TODO-USER]` rent instance + run the §37.1 training.

### 37.6 The one integrated run (when GPU is up)
IndicF5+Fish-Speech → cross-lingual Indic clones → `scenario_render` G.711 (Worst-AI) → + RTCFake + IndicSynth → train **XLS-R-300M + RawBoost + AASIST** → score with `eval_gengap` (watch the +9.95pt gap close). Target metric: **UGR ↑ / Generalization-Gap ↓** (§35).

---

## 38 · AIKosh (IndiaAI National AI Repository) Integration `[NEW · 2026-09-30]`
**What:** AIKosh = India's national AI dataset/model repository (MeitY / IndiaAI / NeGD). We use it as a **governed source of Indic speech data, Indic TTS/ASR/NMT models, and annotation tooling** — not as a detector. Three integration surfaces: **(a) MCP** for interactive discovery, **(b) the `aikosh` Python SDK** for automated ingest, **(c) the AIKosh Jupyter sandbox** for free light compute. Companion doc: `VOXSHIELD_AIKOSH.md`.

**MCP — CONNECTED `[DONE]`.** Endpoint `https://aikosh.indiaai.gov.in/aikoshmcp/mcp` (Streamable-HTTP). Auth = OAuth 2.1+PKCE **or** `Authorization: Bearer <AIKosh_API_KEY>` (verified: endpoint returns `401` + `WWW-Authenticate` without a token). Read-only tools: `get_dataset_filters` · `list_datasets_tool` · `get_dataset_metadata` · `get_dataset_file_structure` · `get_dataset_download_url_tool` · `get_file_download_url_tool` · `search_datasets_and_get_download_urls` · `search_datasets_with_signed_urls` · `ping` + model equivalents (`get_model_filters_tool` …). Wired into `~/.config/opencode/opencode.jsonc` → `mcp.aikosh` (`oauth:false`, header `Bearer {env:AIKOSH_API_KEY}`). Restart opencode after exporting `AIKOSH_API_KEY` to activate.
**SDK `[TODO]`.** `pip install aikosh` → `aikosh.set_api_key(...)`; base `https://aikosh-api.indiaai.gov.in/akp/idp/api/v1`, header `access-key`. (Host did not resolve from this network segment → use MCP or run the SDK where the API host is reachable.)
**Safety:** read-only; signed URLs expire fast; RESTRICTED assets may refuse download; REDIRECT/external assets return an HF URL. **Never upload consented audio back** — AIKosh is ingest-only. Every admitted sample records `provenance=AIKosh/<id>/<version>` + license + consent.

### 38.1 Verified catalogue (live MCP sweep, 2026-09-30)
**94 speech/audio models** (13 model-types) + **124 curated speech datasets** (from 3,929 keyword hits, de-duplicated). Licences/access read from the platform; re-checked per asset at ingest. Raw JSON + `AIKOSH_CATALOG.md`: `/Volumes/KIOXIA/voxshield/aikosh_research/`. Companion: `VOXSHIELD_AIKOSH.md`.

## Models

### A. Attack-generation models (32)
| Model | Licence | Access | id |
|---|---|---|---|
| A2TTS-Bengali Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `f0843b23-b6bd-41af-98f5-904376352a7f` |
| A2TTS-Gujarati Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `f565334a-89a5-4803-b116-5e9198704758` |
| A2TTS-Kannada Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `275b79db-df65-4707-bc52-7bff67ad4b03` |
| A2TTS-Malayalam Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `09cdfb55-5a02-4e7d-92da-149d424b2727` |
| A2TTS-Marathi Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `d9eff220-fbf7-433f-bffa-427921ae92fe` |
| A2TTS-Punjabi Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `589dee3c-166a-4762-8cb3-6de1a9e4df29` |
| A2TTS-Tamil Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `43cf4382-3bda-474a-8a3f-d77c1a3414f1` |
| A2TTS-Telugu Speaker Adaptive TTS (Text-to-Speech)-v0.5 | MIT | RESTRICTED | `393dadb3-e1dc-4740-aec0-7171d9241ea7` |
| AI4Bharat - Airavata: Large-Scale Multilingual Model for Indic Languages | MIT | REDIRECT | `8aec27c5-8c21-43c9-b541-a25e95276e0f` |
| AI4Bharat - Fastspeech2 Model using Hybrid Segmentation (HS): Text to Speech Model | MIT | REDIRECT | `7685d825-7944-4b46-adb4-25d103bf5420` |
| AI4Bharat-Indic-Parler-TTS-Pretrained: Text to Speech Model | MIT | REDIRECT | `e2e3f2a1-64f6-4068-a7c1-18958776538c` |
| AI4Bharat-Indic-Parler-TTS: Text to Speech Model | MIT | REDIRECT | `cd234a42-7ab9-44fe-afc3-eb58b675a9e3` |
| AI4Bharat-VITS-Rasa-13: Text to Speech Model | MIT | REDIRECT | `1cf3fe67-1264-4774-849f-3346a9cf1f7b` |
| AIBharat - IndicF5 | MIT | REDIRECT | `0be4d5ff-17cf-40ad-ac3c-43ec0b0a0724` |
| BHASHINI IISC Sourashtra Vits TTS Models | CC-BY-4.0 | REDIRECT | `d2ae7340-fdf5-4ce5-8929-a9f07ef4d568` |
| Bengali vb | MIT | RESTRICTED | `914e62cc-6df8-483c-8567-f19e227bd55d` |
| BharatGen - A2TTS-v0.5 : Speaker Adaptive TTS Model (Hindi) | MIT | HOSTED | `838baccc-0b09-4e31-aa54-6862b973b1fa` |
| Bhashini - Fastspeech2 Model using (HS) | MIT | HOSTED | `7677ccaf-c070-40b1-892d-1b564e2d824d` |
| Hindi vb | MIT | RESTRICTED | `7068707c-b221-4bf0-aa68-cde350905b47` |
| Indic-Speak | Other | HOSTED | `c0e5c4f2-3270-4bf2-94d3-6e5b43f6fe24` |
| Marathi vb | MIT | RESTRICTED | `6595067b-0e33-4f8a-aa8a-dcb948fe9c88` |
| SpeechT5 (voice conversion task) | MIT | REDIRECT | `92ae4761-46cc-4ca8-8809-0da7b412c0d9` |
| SpeechT5 HiFi-GAN Vocoder | MIT | REDIRECT | `0b66a816-150e-4a9c-9573-9f137b5dcc0d` |
| SpeechT5 Text to Speech model | MIT | REDIRECT | `007a38ad-34a7-4c53-a61c-eb9471a2e8f4` |
| SpeechT5: Unified-Modal Encoder-Decoder Pre-Training for Spoken Language Processing | MIT | REDIRECT | `02987fa5-db21-4eb4-88fe-f865d98c1754` |
| Tamil vb | MIT | RESTRICTED | `a9f706cf-9cec-4fef-a5c0-6bbeda1834b3` |
| Telugu vb | MIT | RESTRICTED | `975915bd-406a-4594-848c-ef8daf8151d7` |
| spk cond tts pflow Bengali | MIT | RESTRICTED | `25d79a17-596b-4f1a-ac26-c535d9793a8b` |
| spk cond tts pflow Hindi | MIT | RESTRICTED | `fd0773b1-4e33-4df7-bddf-bc0e32e299f1` |
| spk cond tts pflow Marathi | MIT | RESTRICTED | `2d8c50ea-e562-40df-a548-1db596c287e7` |
| spk cond tts pflow Tamil | MIT | RESTRICTED | `e2890257-8013-4744-9c67-75c718d42b7a` |
| spk cond tts pflow Telugu | MIT | RESTRICTED | `db1fd2b6-b694-4b09-8d16-bb9d382b2ea5` |

### B. Detection-support models (60)
| Model | Licence | Access | id |
|---|---|---|---|
| AI FRAUD DETECTION | Apache 2.0 | REDIRECT | `6445fbae-6b99-4165-a4e8-d1ebfdfbcffc` |
| AI4Bharat - Bengali IndicWav2Vec Speech Model | MIT | REDIRECT | `53693a49-9793-43b0-a5ac-8c1d426e0d9c` |
| AI4Bharat - Gujarati IndicWav2Vec Speech Model | MIT | REDIRECT | `3fae271b-7146-4803-bc42-4eeea8891b1a` |
| AI4Bharat - Hindi IndicWav2Vec Speech Model | MIT | REDIRECT | `490137c0-1bd6-4606-b95b-573c3848c955` |
| AI4Bharat - IndicBART-XXEN: Multilingual to English Text Generation Model | MIT | REDIRECT | `5f48c3e4-6987-4df7-8d64-e148ab435198` |
| AI4Bharat - IndicConformer Automatic Speech Recognition (ASR) Model for Nepali | MIT | REDIRECT | `5efac8bd-8636-4cfb-9862-d1e83f109acc` |
| AI4Bharat - IndicWav2Vec-Hindi: Hindi Speech Recognition Model | MIT | REDIRECT | `7ec092a5-d98f-41b1-bb49-3719e2cc425c` |
| AI4Bharat - IndicWav2Vec-Odia: Odia Speech Recognition Model | MIT | REDIRECT | `6794c718-ba8b-42bf-9e79-3f3e69055844` |
| AI4Bharat - Marathi IndicWav2Vec Speech Model | MIT | REDIRECT | `3643efc0-c6f3-495d-8e38-c3ecfb160020` |
| AI4Bharat - Odia IndicWav2Vec Speech Model | MIT | REDIRECT | `7e88527a-7a50-4b56-a636-64860b008f04` |
| AI4Bharat - Tamil IndicWav2Vec Speech Model | MIT | REDIRECT | `bf88ea99-dd23-4dcb-aad7-983fcc012a23` |
| AI4Bharat - Telugu IndicWav2Vec Speech Model | MIT | REDIRECT | `f475da27-f60e-4db6-81bc-b72af18c9065` |
| AI4Bharat Textual Language Detection | MIT | REDIRECT | `77d4d686-4c3c-47d0-a034-279f17711791` |
| AI4Bharat- Assamese - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `2f76d2e3-2d49-4e24-8aec-e34d512df939` |
| AI4Bharat- Bengali - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `cba49888-e5a4-4e9b-93f8-f86da38ef1c2` |
| AI4Bharat- Bodo - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `77bc7b04-ddce-4324-86b4-034e7cd1e17b` |
| AI4Bharat- Gujarati - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `7992c3e4-02e5-4298-be1d-d2fdff1111ac` |
| AI4Bharat- Hindi - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `2209b8a4-506e-44cf-877d-44017179ef6d` |
| AI4Bharat- IndicConformerAutomatic Speech Recognition (ASR) Model for Dogri | MIT | REDIRECT | `aa178a77-ecbf-48d2-9341-6e9c872aff0b` |
| AI4Bharat- IndicSeamless | CC-BY-NC-4.0 | REDIRECT | `cfa0ca56-f061-49f3-a883-05788d1bc5e8` |
| AI4Bharat- Kannada - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `1a95b822-5fdc-47bf-9821-7837ae5eec11` |
| AI4Bharat- Kashmiri - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `455001ae-677d-4d27-98c7-b90ec4e88fec` |
| AI4Bharat- Konkani - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `775c6bb9-4822-4e1c-903b-5176030cb53a` |
| AI4Bharat- Maithili - IndicConformer Automatic Speech Recognition (ASR) Model | MIT | REDIRECT | `6d73beb7-0234-471d-a333-ca56a91dddd9` |
| AI4Bharat-IndicConformer-STT-ML-Hybrid-CTC-RNNT-Large (Malayalam): Automatic Speech Recognition Model | MIT | REDIRECT | `1cd438b9-8437-4694-af08-5e09419b2568` |
| AI4Bharat-IndicConformer-STT-MNI-Hybrid-CTC-RNNT-Large (Manipuri): Automatic Speech Recognition Model | MIT | REDIRECT | `f7653b15-9c30-4353-b8f8-1b1d1ce43068` |
| AI4Bharat-IndicConformer-STT-MR-Hybrid-CTC-RNNT-Large (Marathi): Automatic Speech Recognition Model | MIT | REDIRECT | `e9136217-f02e-4da4-8506-3402c0bbf4e3` |
| AI4Bharat-IndicConformer-STT-OR-Hybrid-CTC-RNNT-Large (Oriya): Automatic Speech Recognition Model | MIT | REDIRECT | `e3ca361f-34e6-4414-87b1-174d781f164d` |
| AI4Bharat-IndicConformer-STT-PA-Hybrid-CTC-RNNT-Large (Punjabi): Automatic Speech Recognition Model | MIT | REDIRECT | `28bdddb9-5198-43f5-a96e-2e3885256c92` |
| AI4Bharat-IndicConformer-STT-SA-Hybrid-CTC-RNNT-Large (Sanskrit): Automatic Speech Recognition Model | MIT | REDIRECT | `73b4093e-773c-4643-a86a-a3a34e21b01b` |
| AI4Bharat-IndicConformer-STT-SAT-Hybrid-CTC-RNNT-Large (Santali): Automatic Speech Recognition Model | MIT | REDIRECT | `02a214bf-6de6-41d9-adec-724ed802404c` |
| AI4Bharat-IndicConformer-STT-SD-Hybrid-CTC-RNNT-Large (Sindhi): Automatic Speech Recognition Model | MIT | REDIRECT | `835c7e39-7b07-4244-809e-e0eb1122ad27` |
| AI4Bharat-IndicConformer-STT-TA-Hybrid-CTC-RNNT-Large (Tamil): Autmatic Speech Recognition Model | MIT | REDIRECT | `70835646-5c85-43f7-a0bc-e2dc5b44246a` |
| AI4Bharat-IndicConformer-STT-TE-Hybrid-CTC-RNNT-Large (Telugu): Automatic Speech Recognition Model | MIT | REDIRECT | `8ca45cbc-928e-4ec9-92d9-18eab95dd31c` |
| AI4Bharat-IndicConformer-STT-UR-Hybrid-CTC-RNNT-Large (Urdu): Automatic Speech Recognition Model | MIT | REDIRECT | `56cd30d4-ec42-4cbe-9fbb-173ed4301abe` |
| AIBharat - IndicConformer | MIT | REDIRECT | `82adc49a-e64c-4afe-8c42-da5e8be1993a` |
| AIBharat - IndicConformer-600M-Multi | MIT | REDIRECT | `8c4a77ae-cd9c-4d25-83bf-9a455ce73e98` |
| BharatGen - ASR: Hindi | MIT | RESTRICTED | `f03cc563-4af1-452e-a0e4-8b39fb34277a` |
| Dhwani - Multilingual Speech LLM | Krutrim Community License Agreement Version 1.0 | REDIRECT | `1fa1f0d5-5316-417f-9dca-a78077acb9c8` |
| Indic Trans2 | MIT | HOSTED | `6f174fcc-5470-42ff-aa38-fd0816731110` |
| Indic-Conformer model for ASR | MIT | HOSTED | `95ccc49e-8cb6-46b3-ba44-e8cfc9bd6333` |
| Indic-Transcribe-Core | Other | HOSTED | `0d317d58-00dc-4d6b-9d87-6cd4877d64d8` |
| Indic-Transcribe-Flex | Other | HOSTED | `d4ab7339-a5fd-43d0-8bd8-b37d7d8f3747` |
| Indic-Translate | Other | HOSTED | `b7a77674-9f38-4d4c-8943-ef4497a1b59c` |
| IndicXlit | MIT | HOSTED | `418f9c74-0e4a-4ba4-bb70-10faa1f4408f` |
| Krutrim Translate - Indic Language Translation Model | Krutrim Community License Agreement Version 1.0 | REDIRECT | `441d6913-e1a1-4cfe-9d2f-0aac19bed0e7` |
| Northeast STT Multilingual Speech to Text Model | CC-BY-4.0 | REDIRECT | `d1c60b96-dad9-454e-b25c-3484efebe908` |
| Parrotlet-A-2p5-Pro | Other | REDIRECT | `e4dc82ac-e307-4b1c-839c-951acda621f3` |
| SPRING LAB ASSAMESE-STREAMING | CC-BY-4.0 | HOSTED | `e8656888-4610-4d17-bb8f-a503b77bc3e9` |
| SPRING LAB BENGALI-STREAMING | CC-BY-4.0 | HOSTED | `03ed38b3-bd34-4268-8d78-d851455a6892` |
| SPRING LAB GUJARATI-STREAMING | CC-BY-4.0 | HOSTED | `004fa0f6-970a-459b-a2ea-48ea344e1f9e` |
| SPRING LAB HINDI-STREAMING | CC-BY-4.0 | HOSTED | `ca75d802-04e0-4afa-8c08-9ac59b1e3b71` |
| SPRING LAB KANNADA STREAMING | CC-BY-4.0 | HOSTED | `0026f8b8-b104-468b-90ec-ba7384435c5d` |
| SPRING LAB MARATHI-STREAMING | CC-BY-4.0 | HOSTED | `bcf6905f-c147-4b19-86d7-4b7805827f71` |
| SPRING LAB ODIA-STREAMING | CC-BY-4.0 | HOSTED | `b1fd112e-9443-44da-b062-ad3777feada2` |
| SPRING LAB PUNJABI-STREAMING | CC-BY-4.0 | HOSTED | `d74df3d9-7823-4091-9207-9a25d708d654` |
| SPRING LAB TAMIL-STREAMING | CC-BY-4.0 | HOSTED | `39fb5739-f609-4c34-9a21-53e7b7f12c8d` |
| Shrutam-2 | CC-BY-NC-4.0 | RESTRICTED | `10f8bfa3-5f2a-49de-a69a-d275d33239db` |
| Thore Bhasha-Setu | CC-BY-4.0 | HOSTED | `2f0e2bb4-0564-4409-ace8-de7cf98d2d33` |
| shuka-v1 | CC0-1.0 | REDIRECT | `33e17bd9-01d0-48f0-98d8-f5d5861ad981` |

## Datasets

### C. Attack / deepfake / anti-spoofing (1)
| Dataset | Licence | Access | id |
|---|---|---|---|
| IndicSynth | CC-BY-NC-4.0 | REDIRECT | `02269826-db98-43f2-bb51-c3644ea801ec` |
### D. Telephony / IVR (5)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Gram Vaani Hindi ASR Dataset | CC-BY-NC-4.0 | REDIRECT | `308f00aa-0e2e-4341-967c-40bf60ad63d2` |
| Month-wise Telephone Subscribers Rural vs Urban Wireless vs Wireline April 2014 to March 2023 | GODL license | HOSTED | `4315ec50-a8c1-48d0-9fef-5cf6f6655914` |
| Month-wise Telephones (Public Vs Private) from April 2009 to Feb 2015 | GODL license | HOSTED | `0392aa46-3188-402b-9a6b-7b2beacdbb52` |
| SARTHI AgriData | CC-BY-4.0 | REDIRECT | `f2e739e3-cebe-4021-a05d-26745c38acc8` |
| Service Area-wise Telephone from Mar 2002 to February 15 | GODL license | HOSTED | `ff0499f8-36ac-4cb5-8798-4c3099080fe3` |
### E. TTS / voice corpora (65)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Assamese Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b35af3d8-0a76-4ff0-8e19-4e26246ec919` |
| Assamese Male Mono (indicTTS phase3) | CC-BY-4.0 | HOSTED | `65633497-2803-4bfb-aa09-2f9be7f5ad69` |
| Bengali ASR Benchmark Dataset (IndicTTS Bengali) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `8bf87591-85e1-4b57-bdf2-03291281db7e` |
| Bengali Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5fc1c118-3306-46b0-9b71-c698dc895b21` |
| Bengali Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `eb64d933-a940-487b-8e9b-ae072980580e` |
| Bodo Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `08113a94-44c1-46b3-8cda-471b083e6137` |
| Bodo Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `95f7cd1f-87a6-4de1-b931-219e12c9afc8` |
| Dogri Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `fc697e74-00f8-412b-b9a3-db12569f39c4` |
| Dogri Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `bce58775-6245-492b-a6aa-0c3304e32061` |
| Gujarati ASR Benchmark Dataset for Diverse Domains (IndicTTS Gujarati) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `ee096546-2dc3-4bca-8849-0258aaed6eb7` |
| Gujarati Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `0df6148f-4cbd-4992-962e-fc65afb3a4e3` |
| Gujarati Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `8ffd893e-d269-4de5-b46c-9298edc6b4f4` |
| Hindi ASR Benchmark Dataset for Diverse Domains (IndicTTS Hindi) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `f9415f9c-483e-4632-b0e5-b8139eae383f` |
| Hindi Female Mono (IndicTTS Phase3) | CC-BY-4.0 | HOSTED | `086a5b17-39c0-407d-9def-bcf9a87faf15` |
| IISc SYSPIN_S1.0 Corpus | CC-BY-4.0 | REDIRECT | `a4446683-6d08-42af-966f-e1ecf2ea4825` |
| IndicSynth | CC-BY-NC-4.0 | REDIRECT | `02269826-db98-43f2-bb51-c3644ea801ec` |
| IndicVoices-R | CC-BY-ND-4.0 | REDIRECT | `bb368065-7ea7-422f-a7af-57666717ca44` |
| Kannada ASR Benchmark Dataset (IndicTTS Kannada) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `b8f113e1-880d-4529-9f92-60f9639cfa7a` |
| Kannada Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `0459e517-774b-4a30-81fe-e3cfcefeb145` |
| Kannada Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b24fc273-baea-4e92-aa81-bff3adf78832` |
| Kashmiri TTS Single Speaker Dataset | Attribution 3.0 Unported (CC BY 3.0) | HOSTED | `a940d4fe-0934-4e59-874f-edf5c8a876b1` |
| Konkani Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `244fc9d6-588b-4fe0-a5d7-0ffe7011e173` |
| Konkani Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `2da16d38-a452-4897-b306-26ba81b51336` |
| LJSpeech-1 | CC-BY-4.0 | REDIRECT | `14efee51-11a6-4bf3-9197-6469ecb02608` |
| MANGO TTS | CC-BY-4.0 | REDIRECT | `7f5c1b81-5a5f-4c67-a9d3-2cc0b58ef8ac` |
| MIZO Language TTS and ASR segmented | CC-BY-NC-4.0 | RESTRICTED | `5252fe39-915f-4348-bbb1-7d5a0a63e0cd` |
| Maithili Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `8f16af0f-9d3b-4c1f-9fe4-5dda3f55af92` |
| Maithili male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `04f14f98-33b5-4b3c-ad21-b593d2e70417` |
| Malayalam ASR Benchmark Dataset for Diverse Domains (IndicTTS Malayalam) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `8dbb3db5-e05f-48b4-a890-4af25b775700` |
| Malayalam female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `15a0a906-d0fa-4b52-9c8c-05eeabe6aba6` |
| Malayalam male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `c008702f-36c5-4285-859a-c91db9d00aee` |
| Manipuri Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `a6c81d1b-e02a-4d83-8105-397fd5b33d6e` |
| Manipuri male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `cef41a65-82ea-4fac-ab55-96c54d3d9d28` |
| Marathi ASR Benchmark Dataset for Diverse Domains (IndicTTS Marathi) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `c1549d79-2bae-4fa3-af76-1d2d3d9aba8d` |
| Marathi Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `7da27b19-d3d9-45a6-8f5b-ad2b9ab0c0f7` |
| Marathi male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `2dc49b90-d1fe-453d-b858-bcdd04b5c19e` |
| Mizo audio segmented ASR and TTS | CC-BY-NC-4.0 | RESTRICTED | `fa7c661f-3b6a-4962-82ca-510d2a90fd33` |
| Nepali Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `0e2484ab-f62b-4aa0-bf2f-4e390e8f75d4` |
| Nepali male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `718adff4-6506-457e-8d0d-fdf687cba809` |
| Odia (Oriya) Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `ea046f17-4a12-433a-97c8-20a340309dc7` |
| Odia (Oriya) male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5e66144e-9c10-43d3-aa39-cc834c0189e0` |
| Odia ASR Benchmark Dataset for Diverse Domains (IndicTTS Odia) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `2d250e35-c1d8-4034-8a61-dd4c4e8eb159` |
| Punjabi Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `36d9e328-f9bb-4897-bf2c-465af6a81872` |
| Punjabi male mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `1a546b97-13f0-41fb-9801-c1e35aa78e33` |
| Rajasthani Male mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5d7cd0bf-48fe-43e9-9a6a-a877865adc65` |
| Rajasthani female mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b6046517-0f82-4caa-8dd7-77d63a3634ee` |
| RasaTTS | CC-BY-ND-4.0 | REDIRECT | `cf8c6bb6-010b-46bf-9601-43a53bcc0701` |
| SPICOR TTS_1.0 Indian English Corpus | CC-BY-4.0 | REDIRECT | `20ec1d28-a1a5-4442-b0e7-7e1810a438df` |
| SPICOR TTS_2.0 Gujarati Corpus | CC-BY-4.0 | REDIRECT | `5cfebe30-7886-4c76-a637-ec453ccf2861` |
| SPICOR TTS_3.0 Sourashtra Corpus | CC-BY-4.0 | REDIRECT | `92868771-dfc5-48dc-a20b-81dcafb4b0cb` |
| Sanskrit Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `757f9ef9-eb44-4f06-983b-489d0d390d94` |
| Sanskrit Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `6d17f817-7035-4cb3-936d-1672acad5949` |
| Santali Female Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `f42e8fa1-62b2-436c-be2b-89516a92c9fa` |
| Santali Male Mono (IndicTTS Phase 3) | CC-BY-4.0 | HOSTED | `5c6b86ec-457e-48db-a5cf-ae04b976de3e` |
| Sindhi female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `3823c351-c42a-4ea5-97a0-8a54736bf44d` |
| Sindhi male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `a2f98961-f5f5-4878-8b7b-a09ae606070c` |
| Tamil ASR Benchmark Dataset for Diverse Domains (IndicTTS Tamil) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `458bf3d5-96b6-47cf-91f3-2ab4ace5fdaf` |
| Tamil Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `e9c6d414-cfab-42fa-8cc4-fadd9fbca9b4` |
| Tamil Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `c095b3e9-b3b0-45ba-bcc6-807907eb4c85` |
| Tawng Mizo Speech Dataset | CC-BY-NC-4.0 | RESTRICTED | `b57b0878-3b20-4824-a327-6d6cf639bcd6` |
| Tawng Mizo Speech Dataset 2 | CC-BY-NC-4.0 | RESTRICTED | `0ac02934-54aa-450f-a32f-8d4f1e1fca57` |
| Telugu ASR Benchmark Dataset (Indictts Telugu) | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `122a794f-b315-4e96-b0ee-acb5fc14368e` |
| Telugu Female Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `b2f84d9a-61dd-4e96-bd20-36c1ba0b532e` |
| Telugu Male Mono (indicTTS Phase 3) | CC-BY-4.0 | HOSTED | `80a75616-9b57-4279-95ec-1c547fcf807f` |
| VCTK Corpus - Accent and Voice Cloning | Other | REDIRECT | `b8fd001a-c12a-4365-b7f9-d1037150803f` |
### F. ASR / speech corpora (base, non-benchmark-slice) (37)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Bengali (Kathbath) Multilingual Speech Recognition Dataset | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `e474a2e1-e394-4aa3-8a68-2f1a96322171` |
| BhasaAnuvaad | CC-BY-4.0 | REDIRECT | `e378c256-9206-4108-ae7d-3e32de02dd1d` |
| Common Voice | CC0-1.0 | REDIRECT | `60bf61e1-84ea-4bd8-8f8f-4a289bb1e403` |
| Dehwali Bhili Conversational Dataset | CC-BY-4.0 | HOSTED | `9bcec89c-9e84-445b-81bf-ed81aaf350ab` |
| Dehwali Bhili Spontaneous Speech Dataset | CC-BY-4.0 | HOSTED | `69d3cd29-186a-4e8c-8a6a-1aebab01e56c` |
| Dehwali Bhili Studio Recording and Transcription Dataset | CC-BY-4.0 | HOSTED | `437eb57a-bab8-473f-b880-9b80bf379ae2` |
| Gram Vaani Hindi ASR Dataset | CC-BY-NC-4.0 | REDIRECT | `308f00aa-0e2e-4341-967c-40bf60ad63d2` |
| IISc IndicDLPRESPIN_S1.0 Corpus | CC-BY-4.0 | REDIRECT | `8b4fe62e-b5b6-4ded-953f-64bee875357d` |
| IndicST - Indian Multilingual Speech Translation Corpus | Krutrim Community License Agreement Version 1.0 | REDIRECT | `e25f556c-cc97-4586-9272-f78d476d699b` |
| IndicVoices | CC-BY-4.0 | REDIRECT | `c112ce47-770c-47f3-80be-09b5afec8bc5` |
| Lahaja | CC-BY-4.0 | REDIRECT | `4bca2bda-4ae7-4533-826b-30af6b8e2607` |
| LibriSpeech | Other | REDIRECT | `eec5ff28-3dd2-4bc2-a491-242c50cc88ca` |
| MIZO Language TTS and ASR segmented | CC-BY-NC-4.0 | RESTRICTED | `5252fe39-915f-4348-bbb1-7d5a0a63e0cd` |
| Mizo audio segmented ASR and TTS | CC-BY-NC-4.0 | RESTRICTED | `fa7c661f-3b6a-4962-82ca-510d2a90fd33` |
| Multidialectal Pradesh Odia Speech Repository MPOSR | Open Government License, India | HOSTED | `aa50055d-01af-4f06-95d3-926bc372860b` |
| Rural_Women_Bhojpuri | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | REDIRECT | `f195d578-acf3-44be-86df-cf625ac29238` |
| SPRING INX BENGALI | CC-BY-4.0 | HOSTED | `e2c487f9-1767-41f5-83bc-8889dd0b2956` |
| SPRING-INX-ASSAMESE | CC-BY-4.0 | HOSTED | `668836c9-6849-4531-8f23-2c0cd3108405` |
| SPRING-INX-GUJARATI | CC-BY-4.0 | HOSTED | `16394adf-ff0a-4a58-9875-e906af45e88a` |
| SPRING-INX-HINDI | CC-BY-4.0 | HOSTED | `92029f1b-67e9-4118-83fb-04c90271611e` |
| SPRING-INX-KANNADA | CC-BY-4.0 | HOSTED | `8c98c1f0-f9c0-4f38-94aa-2e2eabb1aad5` |
| SPRING-INX-MALAYALAM | CC-BY-4.0 | HOSTED | `2b630d5c-e363-4620-a0bd-73fb0b47f4f6` |
| SPRING-INX-MARATHI | CC-BY-4.0 | HOSTED | `26ddef40-9b24-451c-bbfb-5daeb0627ebe` |
| SPRING-INX-ODIA | CC-BY-4.0 | HOSTED | `4156308a-69d3-432c-84ee-967aca1ccc78` |
| SPRING-INX-TAMIL | CC-BY-4.0 | HOSTED | `d1426eea-9d43-455c-8351-5c66bf994f2d` |
| SPRING-LAB-PUNJABI | CC-BY-4.0 | HOSTED | `9d25de25-5b9d-48ef-bf2b-7d52dfde5bff` |
| Shrutilipi | CC-BY-4.0 | REDIRECT | `20d804c8-b8e5-44d8-b34e-7b3a1ec05394` |
| Shrutilipi (AI4Bharat) | CC-BY-4.0 | REDIRECT | `6fd05842-9454-4aed-b283-ff6842dc731f` |
| SpeeD-TB - Kokborok | CC-BY-4.0 | HOSTED | `3f46c900-66e1-4976-af48-2c51aa9721a3` |
| SpeeD-TB - Meitei | CC-BY-4.0 | HOSTED | `c8ceda14-d8d1-4477-9f8f-52297f44e5ac` |
| Speed-IA Speech Datasets and Models for Indo-Aryan languages | Attribution-Non-Commercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) | REDIRECT | `eeb022aa-b8f0-4737-a97e-d063bbc160cd` |
| Svarah | CC-BY-4.0 | REDIRECT | `5d2836b2-1020-4e86-a264-21a834dda906` |
| Tawng Mizo Speech Dataset | CC-BY-NC-4.0 | RESTRICTED | `b57b0878-3b20-4824-a327-6d6cf639bcd6` |
| Tawng Mizo Speech Dataset 2 | CC-BY-NC-4.0 | RESTRICTED | `0ac02934-54aa-450f-a32f-8d4f1e1fca57` |
| Vāksañcayaḥ - Sanskrit_ASR_Corpus | CC0-1.0 | HOSTED | `bc0bd104-f01c-41ea-8147-76adf1db32ba` |
| bhasha-sft_aya_dataset | CC-BY-4.0 | HOSTED | `18c2ecf8-ccc8-456a-8a06-e39369a8498a` |
| eka-medical-asr-evaluation-dataset | MIT | REDIRECT | `e3feb413-0dd4-4b4e-a30f-d4a4ace32b12` |
### G. Conversational / meeting (19)
| Dataset | Licence | Access | id |
|---|---|---|---|
| AMI Meeting Corpus - Dialogue and Multi-Speaker Conversations | Other | REDIRECT | `303b2d54-5656-4ef9-babe-6e152307ab7c` |
| AntEngage Empathy Conversation Dataset | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | HOSTED | `17c43348-e87b-47b4-b9f8-3fcf237dc1dd` |
| Chitchat Constitutional AI | CC-BY-4.0 | HOSTED | `4d745dd4-828c-4d0e-b315-57eadf3b0fb9` |
| Chitchat India Style | CC-BY-4.0 | HOSTED | `bac8d11f-f5da-4cf1-9600-7f8f426f4435` |
| Climate Resilient Agriculture - Instruction QA | CC-BY-NC-4.0 | REDIRECT | `02b7c311-f466-42cc-9017-2da79bc34253` |
| Climate Resilient Agriculture - Reasoning | CC-BY-NC-4.0 | REDIRECT | `214420fb-c1ac-486c-8bf5-c96e1d1ad703` |
| Dehwali Bhili Conversational Dataset | CC-BY-4.0 | HOSTED | `9bcec89c-9e84-445b-81bf-ed81aaf350ab` |
| Dehwali Bhili Spontaneous Speech Dataset | CC-BY-4.0 | HOSTED | `69d3cd29-186a-4e8c-8a6a-1aebab01e56c` |
| IEMOCAP - Interactive Emotional Dyadic Motion Capture Database | Other | REDIRECT | `e24acbac-414b-410c-a218-1bdbb15a3837` |
| Kirana Chain | CC-BY-4.0 | REDIRECT | `6c6db8c8-f2c7-4f4b-b622-d4930b00f492` |
| Llama Wildchat Lmsys | CC-BY-4.0 | HOSTED | `224cd126-7feb-42a5-9cdd-630c71975a2a` |
| NagaNLP Conversational Corpus | CC-BY-NC-4.0 | REDIRECT | `602764c1-3df1-4305-946f-d61b8cd11853` |
| OpenAssistant Conversations | Apache 2.0 | REDIRECT | `f03e27c8-2714-4498-a873-059aa5aad35b` |
| OpenSubtitles | Other | REDIRECT | `bb120955-b2f5-40c2-80df-ea645fa06cf2` |
| Reddit Comments Dataset | Other | REDIRECT | `5559dccb-d67a-413f-9c19-7c1f285c91a0` |
| ShareGPT Conversations | Apache 2.0 | REDIRECT | `20af627e-d527-4d0e-af12-2243a4735d0b` |
| TED-LIUM Release 3 - Transcribed TED Talks | CC-BY-4.0 | REDIRECT | `6bd7066f-5a94-45f6-9998-3f331bf58191` |
| UltraChat | MIT | REDIRECT | `c3ce7a15-704e-4f8a-a645-0d0ed2387ee2` |
| VAANI: Multi-modal, Multi-lingual Dataset | CC-BY-4.0 | REDIRECT | `40a87486-9632-4024-a665-c9938b39e355` |
### H. Language-ID / transliteration (5)
| Dataset | Licence | Access | id |
|---|---|---|---|
| Aksharantar | Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | REDIRECT | `c448d941-fbba-4607-bd33-ba489bd22bf5` |
| Indo-Aryan Language Identification Shared Task Dataset | Apache 2.0 | REDIRECT | `6ed22d44-f602-4764-9954-2326751dedfb` |
| ModeScript Synthetic Dataset | MIT | REDIRECT | `b2368fa3-1f9e-426e-a687-46e976ef09c6` |
| ModeTrans | MIT | REDIRECT | `3bc4aef3-7306-45ff-aaaf-f96a4892ab18` |
| PahariLI - Pahari Language Identification Corpus | Apache 2.0 | REDIRECT | `253ab174-7911-49fb-bc8e-62fe1e17bb04` |

### 38.2 Implementation
- ✅ `[DONE]` **MCP config** (opencode global) + **full catalogue enumerated & verified** — 15 tools · **94 models** · **124 curated datasets** (from 3,929 hits); ids/licenses/access read from the platform 2026-09-30. Raw JSON + sweep scripts on `/Volumes/KIOXIA/voxshield/aikosh_research/`.
- ✅ `[DONE]` **`backend/aikosh_ingest.py`** — verified asset catalogue + **fail-closed licence gate** (permissive → admitted; NC/ND/Other → held for research/eval) + offline-ingest wrapper onto `corpus_ingest`. Self-test PASS.
- ✅ `[DONE]` **`SOURCE_MAPS["aikosh"]`** in `corpus_ingest.py` — carries `provenance=AIKosh/<id>/<version>` + true licence; `corpus_ingest` self-test still PASS.
- ⬜ `[TODO]` **AIKosh provenance entries** in `registries/generators.json` (Fastspeech2, Indic-Parler-TTS, IndicF5, Sooktam2, A2TTS, SpeechT5-VC, spk-cond-tts-pflow, Indic-Speak) and dataset provenance in manifests.
- ⚠️ **Non-commercial/ND hold-list** (research/eval only, kept off the commercial corpus by the gate): IndicSynth, Gram Vaani, NagaNLP Conversational, Tawng Mizo/MIZO, Speed-IA (NC); IndicVoices-R, RasaTTS (**ND**); Shrutam-2 (NC); "Other"-licensed (VCTK, AMI, LibriSpeech, IEMOCAP, Indic-Speak, Indic-Transcribe, Parrotlet).
- 🔓 **RESTRICTED (request entitlement):** A2TTS (all but Hindi), spk-cond-tts-pflow (all), "vb" TTS (Hi/Bn/Mr/Ta/Te), BharatGen-ASR-Hindi.

### 38.3 Why it matters
- **India-hosted, govt platform** → data-residency-friendly, defensible provenance for a fraud-detection product.
- **Complements (does not duplicate) §27 BHASHINI** and §37 datasets: AIKosh is the *catalog+distribution* layer for many of the same AI4Bharat/Bhashini assets, with signed-URL delivery and free sandbox compute.
- **Highest-leverage use:** (1) IndicVoices genuine → drive the Worst-Human FP down; (2) Fastspeech2/Indic-Parler TTS → generate the Indic Worst-AI set that flips the **0/23 language scorecard** green on the next GPU run.

---
*Companions: `VOXSHIELD_MASTER_PLAN.md` (narrative) · research docs `VOXSHIELD_RESEARCH_2026-09.md` / `VOXSHIELD_VOICESTUDIO_GENERATORS.md` / `VOXSHIELD_THREAT_INTEL.md` / `VOXSHIELD_GPU_RENTAL.md` / `VOXSHIELD_AIKOSH.md` (§38) / `VOXSHIELD_AIKOSH_MASTER_LIST.md` / `VOXSHIELD_BHASHINI_SERVICE_IDS.md` (§27) / `VOXSHIELD_SPEAKER_PROVIDERS.md` · `backend/` modules, all self-test green · SDKs in `sdk/`. This file is the single source of truth. Tick `[TODO]→[DONE]` as items ship.*
