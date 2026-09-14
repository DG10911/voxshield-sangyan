# VoxShield Landscape Report 2026

**Scope.** Gap analysis between VoxShield's current attack coverage (wav2vec2-large-XLSR-53 fine-tuned on In-the-Wild + MMS-TTS Indic fakes, 0.31% clean EER / 0.99% G.711 EER) and the 2026 real-world Indic-language voice-fraud threat landscape. All URLs are inline; anything unverifiable is marked `[unverified]`.

---

## 1. Voice-Cloning Technology Landscape 2024–2026

### 1a. Open-source cloners

VoxShield trained *only* on **MMS-TTS** Indic fakes plus generic In-the-Wild English. That is a narrow attack basis: MMS-TTS is a VITS-family multilingual model and looks nothing like modern flow-matching / neural-codec / autoregressive-LM cloners. Anything trained *only* against MMS-TTS is unlikely to generalise to XTTS-v2, F5-TTS, MaskGCT, GPT-SoVITS, or codec-LM systems.

| Model | Arch family | Zero-shot ref | Indic support | Weights | Covered by VoxShield? |
|---|---|---|---|---|---|
| **XTTS-v2** ([Coqui/HF](https://huggingface.co/coqui/XTTS-v2)) | GPT-style + HiFi-GAN | 6–10s | Hindi (list of 17 langs); no Tamil/Bengali natively | Public (CPML non-commercial) | Likely-no |
| **XTTS-v3** [unverified public release] | – | – | – | – | Likely-no |
| **F5-TTS** ([arXiv 2410.06885](https://arxiv.org/abs/2410.06885), [HF](https://huggingface.co/SWivid/F5-TTS)) | Flow-matching DiT | 3–10s | Chinese/English base; cross-lingual F5 adds more ([arXiv 2509.14579](https://arxiv.org/pdf/2509.14579)) | Public (CC-BY-NC) | Likely-no |
| **MaskGCT** ([arXiv 2409.00750](https://arxiv.org/abs/2409.00750)) | Masked GCT non-AR | 3s | EN/ZH primarily | Public | Likely-no |
| **GPT-SoVITS** ([GitHub](https://github.com/RVC-Boss/GPT-SoVITS)) | GPT + VITS decoder | 3–10s | Community forks for Hindi | Public (MIT) | Likely-no |
| **StyleTTS 2** ([arXiv 2306.07691](https://arxiv.org/abs/2306.07691)) | Diffusion + adversarial | 3s | English | Public | Likely-no |
| **VALL-E / VALL-E 2** (Microsoft) | Neural-codec LM | 3s | English demo only | Not released | Likely-no (via reimpl.) |
| **YourTTS** ([arXiv 2112.02418](https://arxiv.org/abs/2112.02418)) | VITS+SE | few-shot | Community | Public | Partial (VITS-family, close to MMS-TTS) |
| **MetaVoice-1B** ([GitHub](https://github.com/metavoiceio/metavoice-src)) | GPT audio-token LM | ~30s | English | Public (Apache-2.0) | Likely-no |
| **Fish-Speech v1.5 / S2** ([fish.audio](https://fish.audio)) | Codec-LM + flow decoder | 10–30s | 8 langs incl. Hindi/Japanese | Public (Apache-2.0) | Likely-no |
| **Bark** ([suno/bark](https://huggingface.co/suno/bark)) | Codec-LM (Encodec) | prompt-based | Multilingual, English strongest | Public (MIT) | Likely-no |
| **Tortoise-TTS** ([GitHub](https://github.com/neonbjb/tortoise-tts)) | Autoregressive+diff. | few-shot | English | Public | Likely-no |
| **ChatTTS** ([GitHub](https://github.com/2noise/ChatTTS)) | Conv-LM | prompt | EN/ZH | Public (CC-BY-NC) | Likely-no |
| **Parler-TTS** ([HF](https://huggingface.co/parler-tts)) | Prompt-conditioned LM | style prompt | English | Public (Apache-2.0) | Likely-no |
| **OpenVoice V2** ([HF](https://huggingface.co/myshell-ai/OpenVoiceV2)) | Base TTS + tone-color extractor | 3s | EN/ES/FR/ZH/JP/KR + cross-lingual | Public (MIT) | Likely-no |
| **Mars5** (CAMB.AI) | Codec + refinement | 5s | ~140 langs claimed | Public (partial) | Likely-no |
| **CSM-1B (Sesame)** ([HF](https://huggingface.co/sesame/csm-1b)) | LLaMA-audio interleaved | streaming | English | Public (Apache-2.0) | Likely-no |
| **MMS-TTS** ([Meta](https://huggingface.co/facebook/mms-tts)) | VITS | – | 1100+ langs incl. all 10 Indic | Public | **Yes** (VoxShield's training source) |
| **VoxCPM** ([arXiv 2509.24650](https://arxiv.org/abs/2509.24650)) | Tokenizer-free | 3s | – | [unverified] | Likely-no |

Overview refs: [Inferless open-TTS comparison](https://www.inferless.com/learn/comparing-different-text-to-speech---tts--models-part-2), [CodeSOTA best-for-cloning 2026](https://www.codesota.com/speech/best-for-voice-cloning), [ClonEval benchmark](https://arxiv.org/pdf/2504.20581).

**Gap.** Of ~20 mainstream open cloners, VoxShield has only in-family exposure to one (MMS-TTS/VITS). The 2024–2026 wave is dominated by **flow-matching (F5, E2), neural-codec LMs (VALL-E, Fish, MaskGCT, Bark, XTTS)**, and **conversational streaming models (CSM)** — none of which VoxShield has seen.

### 1b. Commercial cloners with API

| Vendor | Latest model | Indic langs | Zero-shot | Notes |
|---|---|---|---|---|
| **ElevenLabs** | v3 / Turbo v2.5 / Flash | 70+ langs incl. **Hindi, Tamil, Bengali, Telugu, Malayalam, Gujarati** | 30–60s IVC; 30 min PVC | v3 is the market leader; $0.10/1k chars ([pricing](https://elevenlabs.io/pricing)) |
| **Cartesia Sonic 3.5** | streaming | Hindi (top-tier), Tamil/Bengali less depth | 3s | Sub-100ms streaming; $5–$299/mo ([Cartesia](https://cartesia.ai/)) |
| **PlayHT / Play.ai** | Play 3.0 mini + Dialog | Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Punjabi, Kannada | few-sec | 200ms streaming |
| **Resemble AI** | Rapid + Localize | 149 langs incl. Indic | 10s | Also sells "Resemble Detect" — competitor |
| **Speechify Voice Cloning** | – | Hindi/Tamil/Bengali | ~30s | Consumer-facing |
| **LOVO** | Genny | Hindi + regional | ~30s | – |
| **WellSaid Labs** | – | English focus | 4-hr training | Enterprise |
| **Descript Overdub** | – | English | ~10 min | – |
| **Murf.ai** | Gen 2 | Hindi, Tamil, Bengali | few-min | India-founded |
| **Rime** | Mist / Arcana | English focus | 10s | Low-latency telephony |
| **HeyGen** | Voice Clone | Hindi + | 30s | Video-driven |
| **Podcastle** | Revoice | English focus | 70s | – |
| **Replica Studios** | – | English focus | 15–30 min | – |
| **Uberduck** | – | English + community | few-sec | Community voices |
| **Sarvam AI Bulbul-v3** | – | **11 Indian languages, native accents** | consent-based | India-native, on-prem SLA ([sarvam.ai](https://www.sarvam.ai/blogs/bulbul-v3)) |
| **Krutrim / Kruti** | – | 13 Indian languages | text+voice agent | Ola-backed ([YourStory](https://yourstory.com/ai-story/ola-krutrim-launches-agentic-ai-assistant-kruti)) |

Refs: [Dupple 2026](https://dupple.com/learn/best-ai-voice-cloning-tools), [Deepgram TTS API roundup](https://deepgram.com/learn/best-text-to-speech-apis-2026), [MediaNama on Sarvam Bulbul-v2](https://www.medianama.com/2025/05/223-sarvam-ai-bulbul-v2-tts-launch-privacy-challenges/).

### 1c. Zero-shot vs few-shot

- **3-second zero-shot (adversary-viable from a WhatsApp voice note):** VALL-E, F5-TTS, MaskGCT, StyleTTS2, OpenVoice, Cartesia Sonic, VoxCPM.
- **6–30-second reference:** XTTS-v2/v3, Fish-Speech, GPT-SoVITS, MetaVoice, ElevenLabs IVC, PlayHT, Resemble, Bulbul-v3.
- **Minutes to hours (Professional Voice Cloning):** ElevenLabs PVC, WellSaid, Replica, Descript Overdub, Tortoise fine-tune.

**Fraud implication for India.** The Indic scam surface starts at 3–10s samples — trivially harvestable from ringback recordings, WhatsApp status voice notes, or Reels. Any detector that doesn't cover 3s-zero-shot codec-LM cloners has a real coverage hole.

---

## 2. AI Voice Agents Ecosystem 2025–2026 (Real-time Conversational)

These platforms give fraudsters a *live, interactive* deepfake, not just a rendered clip. Detection must run on **streaming audio** with sub-second decisions.

| Platform | Voice-to-voice latency | TTS backend | Notes |
|---|---|---|---|
| **Retell AI** | ~580–800ms ([Retell](https://www.retellai.com/blog/retell-vs-bland-vs-vapi-vs-elevenlabs)) | pluggable | Own turn-taking model |
| **Vapi** | ~500–700ms | pluggable (Cartesia/11L/Deepgram) | Highest control |
| **Bland AI** | ~700–900ms | proprietary | Outbound-scale focus |
| **Deepgram Voice Agent** | ~500ms | Aura-2 | Full-stack |
| **Cartesia Sonic** | <100ms TTFT | Sonic 3.5 | Sub-second streaming |
| **ElevenLabs Conversational** | ~800ms | Flash | Multi-lingual incl. Hindi |
| **Sesame CSM / Maya / Miles** | 200–300ms ([Sesame](https://www.sesame.com/)) | CSM-1B | Emotional prosody |
| **Rime Arcana / Mist** | ~200ms | in-house | Telephony-tuned |
| **PlayAI** | ~300ms | Play 3.0 Dialog | – |
| **Poly.ai** | – | – | Contact-center focus |

**Fraud usage.** Public press has documented deepfake voice-agent misuse for CEO fraud (Arup, Hong Kong, 2024), "digital arrest" scams in India ([ORF](https://www.orfonline.org/expert-speak/deepfakes-and-financial-cybercrime-india-s-multi-layered-response)), and grandparent scams (US/Australia). Vapi and Bland specifically have been flagged by researchers as low-friction to abuse (any credit card, no KYC). `[unverified]` for specific vendor breach counts.

**Gap for VoxShield.** VoxShield today is a batch classifier on a WAV file, ~20ms/inference. It has not been evaluated on **streaming chunked inference**, **turn-taking dynamics**, or **live PSTN codec + jitter + packet-loss** — which is where the agents actually live.

---

## 3. Indic / Indian-Focused Voice Models

| Player | Product | Cloning? | Notes |
|---|---|---|---|
| **Sarvam AI** | Sarvam-1 LLM, Sarvam-M, **Bulbul-v2/v3 TTS** ([Bulbul-v3](https://www.sarvam.ai/blogs/bulbul-v3)) | Yes, consent-based, 35+ voices, 11→22 langs | India's default TTS candidate for Aadhaar/DPI |
| **Krutrim (Ola)** | Krutrim LLM, **Kruti** agentic assistant | Voice in 13 Indian langs (June 2025) | Layoffs in linguistics team 2025 ([BT](https://www.businesstoday.in/technology/story/what-a-miss-olas-krutrim-fails-to-hail-a-ride-on-indias-biggest-ai-summit-517900-2026-02-25)) |
| **AI4Bharat** (IIT-M) | IndicTrans2, Bhashini, **IndicSUPERB**, **IndicVoices** (12k hrs / 22 langs / 22.5k speakers), **IndicVoices-R** (1704 hrs TTS) ([AI4Bharat](https://ai4bharat.iitm.ac.in/)) | Research | Public datasets, gold source |
| **Bhashini** (MeitY) | National language mission | – | Government aggregation layer |
| **gnani.ai** | 14B voice-first Indic LM | Voice agents | On-prem / sovereign |
| **Yellow.ai** | Voice+chatbot | Cloning [unverified] | Bangalore |
| **Kore.ai** (bought Vernacular.ai) | Voice contact center | – | – |
| **Skit.ai** | Voice bots | – | Bengaluru |
| **Uniphore** | Emotion AI | – | $2.5B valuation |
| **Neysa** | GPU cloud | – | Infra, not TTS |
| **BharatGen** (IIT-B consortium) | Sovereign LLM/voice | – | Announced 2025 |
| **CDAC** | – | – | Government R&D |

**Indic cloning attack surface = wide.** Bulbul-v3 and Kruti expose native Hindi/Tamil/Bengali/Telugu voices via API today; open-source XTTS/F5/GPT-SoVITS forks for Hindi exist on HF. VoxShield's Indic training is MMS-TTS only — a *single, low-quality* family — so on Bulbul/Kruti/finetuned-XTTS outputs, EER is likely to be far worse than the reported In-the-Wild 0.31%.

---

## 4. Voice-Deepfake Datasets Beyond ASVspoof2019 + In-the-Wild

| Dataset | Size | Languages | Attacks | Link |
|---|---|---|---|---|
| **ASVspoof 5 (2024)** | ~150k utts eval | English | Codec-LM, diffusion, adversarial, spoofing-in-the-wild | [asvspoof.org](https://www.asvspoof.org/) |
| **MLAAD v9** | 163.9h across **23 languages**, 54 TTS systems, 21 architectures | multi | Modern TTS incl. Hindi/Bengali/Tamil ([resemble.ai](https://www.resemble.ai/resources/mlaad-the-multi-language-audio-anti-spoofing-dataset)) | [deepfake-total.com/mlaad](https://deepfake-total.com/mlaad) |
| **WaveFake** | 117k | English/JP | 6 vocoders | [arXiv 2111.02813](https://arxiv.org/abs/2111.02813) |
| **FoR (Fake or Real)** | 195k | EN | commercial+OSS TTS | [Zenodo](https://bil.eecs.yorku.ca/datasets/) |
| **ADD 2022 / ADD 2023** | ~500k | Mandarin | LF, PF, partial fake | [arXiv 2305.13774](https://arxiv.org/abs/2305.13774) |
| **CFAD** | ~350k | Mandarin | noisy/partial | [arXiv](https://arxiv.org/abs/2207.12308) |
| **FMFCC-A** | 40k | Mandarin | – | – |
| **LibriSeVoc** | 79k real / 13k fake | English | 6 vocoders | 2023 |
| **CVoiceFake** | Common-Voice-derived | multilingual | LJS/VITS TTS | [unverified full stats] |
| **DFADD** | – | – | **Diffusion + flow-matching TTS** ([ResearchGate](https://www.researchgate.net/publication/388097733_DFADD)) | 2024 |
| **Indic-CodecFake / SATYAM** | Indic langs | Hindi/Tamil/Bengali/etc. | **Neural audio codec synthesized** ([arXiv 2604.19949](https://arxiv.org/pdf/2604.19949)) | 2026 |
| **PhonemeDF** | – | – | naturalness eval | [arXiv 2603.15037](https://arxiv.org/pdf/2603.15037) |
| **RTCFake** | streaming/RTC | – | codec + jitter | [arXiv 2604.23742](https://arxiv.org/pdf/2604.23742) |
| **SAFE Challenge** | 2025 | multi | attribution | [arXiv 2510.03387](https://arxiv.org/pdf/2510.03387) |
| **HABLA** | Spanish | – | – | (not Hindi despite the acronym confusion) |

**Real bonafide Indic (for negatives):** **IndicVoices** (12k hrs / 22 langs, [AI4Bharat](https://ai4bharat.iitm.ac.in/datasets/indicvoices/)), **IndicVoices-R** (1704 hrs, [HF](https://huggingface.co/datasets/ai4bharat/indicvoices_r)), **Kathbath** (AI4Bharat, [GitHub](https://github.com/AI4Bharat/kathbath)), **Shrutilipi** ([HF](https://huggingface.co/datasets/ai4bharat/shrutilipi)), **Vaani** (IISc–Google, ~150k hrs), **Common Voice Hindi/Tamil/Bengali** ([commonvoice.mozilla.org](https://commonvoice.mozilla.org/)).

**Public fraud-call recordings.** No comprehensive public Indian scam-call corpus exists (verified via search). Closest: TRAI/DoT Chakshu portal reports, media anecdotes; the "digital arrest" audio artifacts circulated on X/Reddit `[unverified for training use]`.

**Biggest missing training piece for VoxShield:** MLAAD v9 (Indic subset) + Indic-CodecFake + DFADD + RTCFake.

---

## 5. Detection Landscape

### 5a. Open-source SOTA

- **AASIST / AASIST3** — ASVspoof reference; SSL-frontend variants (WavLM, Wav2Vec2, HuBERT, UniSpeech-SAT) dominate ASVspoof5 open track. See [ASVspoof 2024 archive](https://www.isca-archive.org/asvspoof_2024/index.html) and SZU-AFS system ([arXiv 2408.09933](https://arxiv.org/pdf/2408.09933)).
- **RawNet2 / RawBoost augmentation.**
- **XLS-R + AASIST fusion** — most winning systems.
- **SHIELD** — adversarial-robust ensemble ([arXiv 2507.13170](https://arxiv.org/pdf/2507.13170)).
- **MSC-Adapter** — parameter-efficient adapter for synthetic-speech detection ([arXiv 2510.24852](https://arxiv.org/pdf/2510.24852)).
- **HF public detectors:** `MelodyMachine/Deepfake-audio-detection-V2`, `motheecreator/Deepfake-audio-detection`, `Nie-Y/spoof-detection`, `hemg/spoofing-detection-2` (English-heavy, no published EER on Indic).

### 5b. Commercial

| Vendor | Focus | Notable |
|---|---|---|
| **Pindrop Pulse** | Call-center, meetings | 99% acc / <1% FPR on internal benchmark; won ACM-MM DDC 2025 ([pindrop.com](https://www.pindrop.com/product/pindrop-pulse/)) |
| **Reality Defender** | Multi-modal | Learn-from-Real ASVspoof5 submission ([arXiv 2410.07379](https://arxiv.org/pdf/2410.07379)) |
| **Hiya** | Call screen + deepfake | Consumer + carrier |
| **Aurigin.ai** | Voice-bio anti-spoof | 98%+ acc, <50ms, 80+ langs ([aurigin.ai](https://aurigin.ai/)) |
| **Resemble Detect** | – | Same-vendor conflict |
| **Voxmind** [unverified] | – | – |
| **HyperVerge** | India KYC | CNN+MFCC audio detection |
| **Bachao.AI** | India consumer | Voice+video deepfake ([bachao.ai](https://www.bachao.ai/deepfake-detection)) |
| **ScamShieldAI** | India | Consumer app |

### 5c. Watermarking

- **AudioSeal (Meta)** — 1/16000s-localized watermark, robust to compression/reencode, MIT license, streaming as of Dec-2025 ([GitHub](https://github.com/facebookresearch/audioseal), [MIT Tech Review](https://www.technologyreview.com/2024/06/18/1094009/meta-has-created-a-way-to-watermark-ai-generated-speech/)).
- **XAttnMark** — cross-attention robust watermark ([arXiv 2502.04230](https://arxiv.org/pdf/2502.04230)).
- **StreamMark** — semi-fragile proactive detection ([arXiv 2604.11917](https://arxiv.org/pdf/2604.11917)).
- **Perth / SilentCipher / WavMark** — earlier baselines.

**Reality check.** Watermarks help only when the generator cooperates. Fraudsters use OSS cloners without a watermark, or strip it via re-vocode. Watermarking is a *complement*, not a *replacement* — a VoxShield detector should **check AudioSeal presence as a positive signal** but never rely on it.

---

## 6. India Context

- **Financial impact:** RBI reports Rs 48,021 crore of banking fraud in FY26, +46.4% YoY over Rs 32,803 crore in FY25 ([DQIndia](https://www.dqindia.com/data-and-ai/ai-scams-india-2025-deepfake-identity-fraud-rs-22495-crore-12108304)). I4C/NCRP report Rs 19,813–22,495 crore lost to cyber-fraud in 2025.
- **Prevalence:** 47% of Indian adults have been hit by, or know a victim of, an AI voice-clone/deepfake scam (vs. 25% global) — McAfee/BusinessLine 2025. 83% of Indian voice-scam victims suffer monetary loss; ~half >Rs 50,000.
- **Pi-Labs prediction:** Deepfake financial fraud in India could top **Rs 70,000 crore by 2025** ([Deccan Herald](https://www.deccanherald.com/opinion/deepfake-the-new-face-of-financial-fraud-3674748)).
- **Regulatory & response:**
  - **CERT-In advisory CIAD-2024-0060** on deepfakes (27 Nov 2024) — High severity, covers voice ([Khaitan summary](https://www.khaitanco.com/thought-leadership/Growing-Concern-over-Deepfakes-CERT-In-Issues-Advisory)).
  - **TRAI** telecom-consent framework + AI-caller-ID rules (2025/26) — see [Deccan Herald TRAI reforms](https://www.deccanherald.com/amp/story/opinion%2Ftrai-s-reforms-and-the-illusion-of-safety-3821497).
  - **DoT/Chakshu** portal for reporting spam/scam calls; 1.2M SIMs deactivated, 1.33M mule accounts frozen in 2025.
  - **MeitY / IT Rules 2021 amendments** — synthetic-media labelling obligations.
  - **RBI** MFA + video-KYC liveness circulars.
- **Buyer requirements:** Banks/NBFCs demand **on-prem** or **VPC** deployment, RBI data-localization, ISO-27001, SOC-2 Type-II, and increasingly CERT-In empanelment for security vendors. VoxShield's on-prem HF-weights model already matches this — it's the correct wedge.
- **Indian competitors:**
  - **Bachao.AI** — consumer deepfake detection (voice+video).
  - **ScamShield AI** — consumer / SMB.
  - **HyperVerge** — KYC + deepfake audio.
  - **Effectiv** — fraud platform with voice module.
  - **IDfy** — video-KYC vendor with liveness.
  - **gnani.ai / Skit.ai** — could pivot detection-side (currently generators).
  - No pure-play Indic **audio-deepfake-detection** startup with a strong published EER on Indic languages — VoxShield's positioning gap is real.

---

## 7. Concrete Integration Recommendations (Ranked by Impact / Effort)

Effort scale: **S** = <1 wk, **M** = 1–4 wk, **L** = 1–3 mo.

### R1. Train against MLAAD v9 Indic subset + Indic-CodecFake immediately
- **Why:** Directly plugs the largest known gap — 23-language, 54-TTS-system coverage including Hindi/Bengali/Tamil samples from modern architectures (XTTS, VITS, Tortoise, Bark, Fish, F5). Indic-CodecFake covers neural-codec attacks specifically.
- **Cost:** ~free (download); GPU-hours only.
- **Timeline:** **M** (1–2 weeks). Prep + fine-tune LoRA head on wav2vec2-XLSR.

### R2. Generate a VoxShield-Indic-Fakes-2026 corpus from XTTS-v2, F5-TTS, GPT-SoVITS, Fish-Speech, Bulbul-v3 (API), ElevenLabs v3 (API)
- **Why:** MMS-TTS-only training is the single biggest coverage hole. Generate ~50k fakes across 10 languages × 6 cloners using IndicVoices reference speakers (with consent flag).
- **Cost:** ElevenLabs $99–$330/mo × 2mo; Bulbul-v3 credits ~₹20–50k; OSS free but ~$500 A100 hrs.
- **Timeline:** **L** (4–8 weeks) — generation pipeline is the bulk.

### R3. Add streaming/chunked inference mode for live-call defence
- **Why:** All the fraud action lives on live PSTN + WebRTC (Retell/Vapi/Bland/Cartesia). A batch WAV classifier can't gate a live call.
- **Cost:** engineering only; VoxShield already ~20ms/inference on A100 so latency budget exists.
- **Timeline:** **M** (2–3 weeks) — sliding-window buffer + hysteresis + PLC/jitter robustness eval.

### R4. Codec + telephony augmentation stack expansion (Opus/AMR-WB in addition to G.711)
- **Why:** Indian telcos increasingly use Opus (VoLTE/VoWiFi) and AMR-WB, not just G.711. Your 0.99% G.711 result is great but partial.
- **Cost:** engineering only; retrain existing model with expanded augmentation.
- **Timeline:** **S** (3–5 days).

### R5. Integrate AudioSeal detector as an auxiliary positive-evidence channel
- **Why:** Free upside — if incoming audio contains a Meta-family watermark, log it and up-weight the fake decision. Never rely, but never ignore.
- **Cost:** pip install audioseal; 1-day integration.
- **Timeline:** **S** (2 days).

### R6. Publish an **IndicSpoof benchmark** (VoxShield-branded)
- **Why:** ~~No public Indic ADSC leaderboard exists.~~ **CORRECTED (2026-09-14):** Indic deepfake *datasets* now exist — IndicSynth (ACL 2025, 12 langs, ~4,000h), Indic-CodecFake (ACL 2026), HAV-DF (Hindi), BanglaFake (Bengali). So don't claim "first Indic dataset." The still-open leaderboard gap is a **telephony-band (8 kHz) cross-lingual Indic evaluation** — nobody occupies it. Owning *that* benchmark (not a generic Indic one) is the category-defining move. Use IndicSynth/Indic-CodecFake as ready-made multi-cloner training data. Attracts buyers + citations, generates dataset flywheel.
- **Cost:** compute + curation, small.
- **Timeline:** **L** (6–10 weeks including a workshop submission).

### R7. Partner or bilaterally test with Sarvam AI (Bulbul-v3) and AI4Bharat
- **Why:** Sarvam is the most-likely-to-be-abused Indic TTS (native accents, easy API). A public "Bulbul-v3-safe" claim gives VoxShield distribution; also a hedge — Sarvam themselves may want a detection partner for compliance.
- **Cost:** BD, zero infra.
- **Timeline:** **M** (relationship-building, 1 mo).

### R8. Product surface: WhatsApp Voice-Note verifier + IVR SDK
- **Why:** WhatsApp voice notes are the #1 Indic-fraud vector (grandparent/CEO scams). An IVR SDK plugs into bank contact-centre stacks (SBI, HDFC, ICICI, Kotak) that already procure fraud-analytics.
- **Cost:** two thin wrappers (WhatsApp Business API + FreeSWITCH/Asterisk module) over the same FastAPI core.
- **Timeline:** **M** (3–4 weeks per surface).

### R9. Compliance packaging: CERT-In empanelment + RBI Data-Localization + DPDP Act 2023 alignment
- **Why:** Turns "we're a student project" into "we're a procurable vendor for BFSI." CERT-In empanelment (via a partner if needed), ISO-27001, SOC-2 Type-II gap-audit, DPDP Act consent-model documentation.
- **Cost:** ₹8–20 L for audit+empanelment paperwork.
- **Timeline:** **L** (3–6 months, largely paperwork).

### R10. Adversarial + robustness eval suite (SHIELD-style)
- **Why:** Attackers will re-vocode, add music, add reverb, or run adversarial perturbations. Publish robustness numbers *before* someone else publishes a break.
- **Cost:** compute + engineering.
- **Timeline:** **M** (2–3 weeks) using published SHIELD/RTCFake benchmarks.

---

## Appendix — Priority acquisition list (datasets and APIs)

1. MLAAD v9 (deepfake-total.com/mlaad)
2. Indic-CodecFake / SATYAM ([arXiv 2604.19949](https://arxiv.org/pdf/2604.19949))
3. DFADD (diffusion/flow-matching)
4. RTCFake (streaming)
5. ASVspoof 5 (train + eval)
6. IndicVoices + IndicVoices-R (bonafide)
7. Vaani (bonafide, apply via IISc)
8. Common Voice Hindi/Tamil/Bengali/Telugu/Marathi (bonafide)
9. Bulbul-v3, ElevenLabs v3, PlayHT, Cartesia, XTTS-v2, F5-TTS, GPT-SoVITS, Fish-Speech, MaskGCT, OpenVoice V2 (fake-generation APIs / weights)
10. AudioSeal (detector for cooperative-watermark channel)

*End of report.*
