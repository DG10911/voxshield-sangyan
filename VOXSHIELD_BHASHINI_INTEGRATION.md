# Bhashini × VoxShield — Integration Research & Plan

*Prepared 2026-09-14. Sources are official (bhashini.gov.in, ULCA GitBook docs, github.com/AI4Bharat, MeitY/PIB) wherever possible. Anything not verifiable against a primary source is marked **[unverified]**. No endpoints, pricing, or language lists are invented — where a number could not be confirmed, it is flagged.*

---

## 1. What Bhashini actually is and offers (2024–2026)

**Bhashini** is the Government of India's National Language Translation Mission, run by the **Digital India Bhashini Division (DIBD)**, a unit under MeitY. Its goal is to let citizens access digital services in their own language. The mission has three interlocking pieces:

- **ULCA (Universal Language Contribution API)** — the open-source data platform and model-registry layer. It hosts datasets and *models*, and exposes them behind a uniform API contract. Repo: [github.com/bhashini-dibd/ulca](https://github.com/bhashini-dibd/ulca).
- **Dhruva** — the inference-serving platform. Live model inference actually executes at `https://dhruva-api.bhashini.gov.in/services/inference/pipeline` (confirmed as the `callbackURL` in the Pipeline Config response — [ULCA docs](https://bhashini.gitbook.io/bhashini-apis/pipeline-config-call/response-payload)).
- **Bhashini Udyat / Udaan / Sahyogi programs** — the outreach + ecosystem/startup arm ([bhashini.gov.in/sahyogi/startup](https://bhashini.gov.in/sahyogi/startup/winners)). "Udyat" broadly refers to integrating Bhashini's multilingual APIs into government platforms.

Behind the API, the models are overwhelmingly from **AI4Bharat (IIT Madras)** — the same lab that publishes IndicConformer (ASR), IndicTrans2 (NMT), and Indic-TTS/IndicF5 (TTS). Bhashini funds AI4Bharat's data collection (e.g. the IndicVoices corpus, 15,000 hrs across 400+ districts).

### Services exposed

| Service | Task type | Model provider (typical) | Languages | Notes |
|---|---|---|---|---|
| **ASR** (speech→text) | `asr` | AI4Bharat IndicConformer (e.g. `ai4bharat/conformer-multilingual-indo_aryan-gpu--t4`) | ~12 confirmed live (as, bn, en, gu, hi, kn, ml, mr, or, pa, ta, te); 22 in the underlying model | Input audio base64 (`audioContent`), **16 kHz**, FLAC/WAV. Domain flag: general/agri/medical. |
| **TTS** (text→speech) | `tts` | AI4Bharat Indic-TTS (FastPitch/HiFi-GAN family), IndicF5 | ~13 Indic | `supportedVoices`: male/female. Output base64, sample rate seen at **8 kHz** in TTS examples [unverified whether higher rates offered]. |
| **NMT** (translation) | `translation` | AI4Bharat IndicTrans2 | All 22 scheduled languages | Text-to-text. |
| **Transliteration** | `transliteration` | AI4Bharat Xlit/IndicXlit | Many Indic | Native↔romanized. |
| **Language ID (audio)** | audio-lang-detection | `bhashini/iitmandi/audio-lang-detection/gpu` (IIT Mandi) | as, bn, en, gu, hi, kn, ml, mr, or, pa, ta, te | Detects spoken language from audio. Directly relevant to VoxShield routing. |
| **Language ID (text)** | textual language detection | AI4Bharat IndicLID | 22 | |
| **OCR** | ocr | Various | Several | Less relevant to VoxShield. |

Exact per-service language availability drifts as models are swapped; the authoritative list is the **Pipeline Config response** for your pipeline ID and the ULCA model catalog ([available-models docs](https://dibd-bhashini.gitbook.io/bhashini-apis/available-models-for-usage)). Treat the table above as indicative, not contractual.

### How you actually call it — the ULCA "pipeline" concept

Bhashini uses a **two-call pattern**, not a single REST endpoint:

1. **Pipeline Config call** — POST to `https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline` with headers `userID` and `ulcaApiKey` (both from your ULCA "My Profile"). Body includes a `pipelineId` (a well-known default pipeline ID is used in most examples) and the task sequence you want, e.g. `[asr]`, `[asr, translation]`, `[asr, translation, tts]`. The response returns, per task, a **`serviceId`** and **`modelId`**, the supported `languages`, and a **`pipelineInferenceAPIEndPoint`** block containing the `callbackURL` (`https://dhruva-api.bhashini.gov.in/services/inference/pipeline`) and an **`inferenceApiKey`** (a `name`/`value` pair — the value is the `Authorization` header for the next call).
2. **Pipeline Compute call** — POST to that `callbackURL` with the `Authorization` header, echoing the chosen `serviceId`s plus the actual input (base64 `audioContent` for ASR, text for NMT/TTS, `sourceLanguage`/`targetLanguage`). Response returns the transcript / translation / synthesized audio.

Config is a prerequisite you can cache; Compute is the hot path. Sources: [Pipeline Compute Call](https://bhashini.gitbook.io/bhashini-apis/pipeline-compute-call), [Overall Understanding](https://bhashini.gitbook.io/bhashini-apis), and a working reference implementation at [AdityaKukreti/bhashini-api](https://github.com/AdityaKukreti/bhashini-api).

### Auth, limits, pricing

- **Auth:** register at [bhashini.gov.in/ulca/user/register](https://bhashini.gov.in/ulca/user/register#), verify email, generate keys under "My Profile". You get a **`userID` + `ulcaApiKey`**; limit **5 keys per integrator** ([onboarding docs](https://bhashini.gitbook.io/bhashini-apis/pre-requisites-and-onboarding)).
- **Free tier / rate limits:** the free developer keys are intended for prototyping; the docs state that production/commercial use requires contacting the Bhashini team for a **paid plan** — exact RPS/QPS and free-tier ceilings are **not published** [unverified]. Note: `bhashini.ai` / `bhashiniservices.com` (credit-based, GST-inclusive pricing) appears to be a **third-party commercial reseller**, *not* the government DIBD service — do not conflate them.
- **Apps/tools:** the **Bhashini** consumer app, **Anuvaad** (document translation), and **Chitralekha** (video subtitling/voiceover) are reference applications. No official heavyweight SDK; community wrappers (Python) exist.

---

## 2. How Bhashini helps VoxShield specifically

VoxShield's core is a fine-tuned wav2vec2-XLSR anti-spoof detector across 10 Indic languages, sold on-prem to Indian BFSI/gov. Bhashini touches four distinct places — and they are *not* equally valuable.

### 2a. ASR for scam-intent transcription (augmenting Whisper)
Bhashini ASR (IndicConformer) is arguably the strongest **open, India-specific** ASR available and covers the 22 scheduled languages — better native coverage than Whisper on low-resource Indic. It could transcribe call audio to feed a scam-intent/NLP layer. **Caveat:** published Indic ASR research is candid that **telephony + noisy + spontaneous speech remains hard** even for IndicConformer (see arXiv work on region-specific and noisy Indic ASR). Do not assume clean-speech WER transfers to 8 kHz G.711 phone audio — VoxShield's own telephony findings (codec cost ~1.6 pts) show how much narrowband degrades models. **Recommendation:** treat Bhashini ASR as a *transcription/intent* aid, not as a replacement for the acoustic anti-spoof path.

### 2b. Language-ID to route to the correct detector head
This is the **cleanest technical fit**. The `audio-lang-detection` service (IIT Mandi) covers ~12 Indic languages and maps almost 1:1 onto VoxShield's 10-language detector heads. A single Bhashini LID call could route incoming audio to the right head instead of running a home-grown classifier. Low integration cost, bounded latency, non-safety-critical.

### 2c. TTS as an additional fake-voice generator (attack augmentation)
VoxShield currently augments with MMS-TTS. Bhashini exposes **AI4Bharat Indic-TTS (FastPitch/HiFi-GAN) and IndicF5** — architecturally **distinct** from Meta's MMS-TTS (different vocoder, different training data, near-human polyglot IndicF5). Adding these as *new spoof classes* diversifies the attack distribution and should improve generalization to unseen synthesis engines — exactly the failure mode anti-spoof models suffer from. This is a **high-value, low-risk, training-time** use. IndicF5 in particular is a modern voice-cloning-capable model that better matches real adversary tooling than older MMS-TTS.

### 2d. Government credibility / procurement
Building on Bhashini is a **genuine GTM asset** in India. It signals MeitY alignment, supports the "Made-in-India, Indic-first, sovereign" narrative, and eases empanelment conversations with government/PSU-bank buyers. It does **not** by itself confer DPDP compliance or CERT-In empanelment — those are separate. But "our language stack is built on the Government's own Bhashini models" is a strong slide.

### 2e. Grants / programs
Real, active funding exists via the **BHASHINI Challenge / Samanvay / LEAP hackathons** ([innovateindia.mygov.in/bhashini-challenge](https://innovateindia.mygov.in/bhashini-challenge/), [PIB PRID 2132385](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2132385)). Reported structure: ₹1 L to top-10 Stage-1 prototypes, ₹2 L each to top-3 Stage-2, and a **₹50 L** winner prize for deploying in 10 Indian languages. VoxShield (10 Indic languages, fraud/social-impact angle) is a strong fit — worth applying.

---

## 3. Limitations & risks (honest)

1. **Cloud vs on-prem — the central conflict.** Bhashini's Dhruva inference is a **cloud API**. VoxShield's entire BFSI pitch is **on-prem, air-gapped, no audio leaves the bank**. Routing live call audio to `dhruva-api.bhashini.gov.in` at runtime **directly contradicts** that value proposition. This is the single most important finding: **do not put Bhashini in the real-time on-prem inference path.**
2. **Data privacy / DPDP.** Sending customer call audio (voice = personal/biometric-adjacent data) to a government cloud raises consent, purpose-limitation, and data-residency questions under the **DPDP Act**. Even though it is a government endpoint, a BFSI customer's DPO will treat it as a third-party processor. Avoid for production PII.
3. **Latency & uptime.** Two-hop (config cached + compute) network round-trips add tens–hundreds of ms and depend on Bhashini uptime; **not** suitable for the low-latency real-time detection budget. No published SLA [unverified].
4. **Rate limits.** Free keys throttle; production requires a paid plan whose limits aren't public [unverified]. A dependency you don't control.
5. **Licensing for TTS-as-training-data.** The underlying AI4Bharat TTS models are generally **Apache-2.0 / CC-BY-4.0** ([Indic-TTS repo](https://github.com/AI4Bharat/Indic-TTS)), which is permissive for generating synthetic training audio. **However**, Bhashini's *API terms of use* for the served endpoints are a separate contract and are **not clearly published for commercial redistribution** [unverified]. **Safer path:** for training-set augmentation, run **AI4Bharat's open-source model weights locally** (offline, no API terms, no per-call limits) rather than pulling audio through the Bhashini API. You get the same distinct engines with clean licensing and reproducibility.

---

## 4. Concrete 5-step integration plan

**Opinionated verdict on where Bhashini fits:**
- ✅ **Training-time attack augmentation** — YES, high value. Use AI4Bharat TTS (IndicF5 + Indic-TTS) as new spoof classes. Do it via **local open weights**, not the cloud API.
- ⚠️ **Runtime language-ID routing** — MAYBE, only in cloud/SaaS deployments, never in air-gapped on-prem. Prefer the open LID weights on-prem.
- ❌ **Runtime ASR / scam-intent in the on-prem detection path** — NO via cloud API; contradicts the on-prem selling point and creates DPDP exposure. If ASR is wanted, self-host IndicConformer weights.
- ✅ **Go-to-market credibility + grants** — YES, immediately, near-zero cost.

| # | Step | What | Effort / time |
|---|---|---|---|
| 1 | **Onboard + validate** | Register at ULCA, generate `userID`/`ulcaApiKey`, run a Config→Compute round-trip for ASR + LID + TTS on VoxShield sample telephony clips. Measure real WER/LID accuracy on 8 kHz audio. | ~2–3 days, 1 eng |
| 2 | **TTS augmentation (the real win)** | Pull **AI4Bharat Indic-TTS + IndicF5 open weights** locally; generate spoof clips across the 10 languages; add as new attack classes; retrain; measure EER/FP delta vs current MMS-TTS-only set. | ~1.5–2 weeks, 1 eng + GPU |
| 3 | **LID routing prototype** | Benchmark open IndicLID/audio-lang-detection weights as the front-door router to the correct detector head; A/B vs current routing. Keep on-prem. | ~3–5 days |
| 4 | **GTM + grant packaging** | Add "built on India's Bhashini/AI4Bharat stack" to deck; apply to the BHASHINI Challenge / LEAP hackathon (10-language fraud-shield angle). | ~2–3 days, non-eng |
| 5 | **Optional cloud-SaaS tier** | *Only* for a future non-air-gapped SaaS offering: expose Bhashini ASR-driven scam-intent as an add-on, with explicit customer consent + DPDP data-flow docs. Guard behind a deployment flag. | ~1 week if pursued |

**Bottom line:** Bhashini's biggest, safest payoff for VoxShield is **offline: distinct TTS engines for attack augmentation + AI4Bharat weights for LID/ASR you self-host**, plus **free go-to-market and grant leverage**. Keep the Government *cloud* API out of the on-prem real-time path — that's where it conflicts with your core promise.

---

### Sources
- [Bhashini ULCA APIs — GitBook](https://bhashini.gitbook.io/bhashini-apis) · [Pipeline Compute](https://bhashini.gitbook.io/bhashini-apis/pipeline-compute-call) · [Config Response Payload](https://bhashini.gitbook.io/bhashini-apis/pipeline-config-call/response-payload) · [Onboarding](https://bhashini.gitbook.io/bhashini-apis/pre-requisites-and-onboarding)
- [github.com/bhashini-dibd/ulca](https://github.com/bhashini-dibd/ulca) · [AdityaKukreti/bhashini-api reference client](https://github.com/AdityaKukreti/bhashini-api)
- [AI4Bharat IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) · [Indic-TTS](https://github.com/AI4Bharat/Indic-TTS) · [IndicLID](https://github.com/AI4Bharat/IndicLID) · [indic-conformer-600m-multilingual](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- [Bhashini portal](https://bhashini.gov.in/) · [BHASHINI Challenge (MyGov)](https://innovateindia.mygov.in/bhashini-challenge/) · [PIB hackathon release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2132385) · [Sahyogi/Startup winners](https://bhashini.gov.in/sahyogi/startup/winners)
