# VoxShield — How To Actually Win

*An honest strategy doc. No hype. Grounded in verified AI4Bharat assets (HF API, 2026-09-14), the frontier R&D findings, and VoxShield's real measured state.*

---

## 0. The uncomfortable truth first

**You will NOT beat the world on model architecture.** The detection recipe (SSL front-end + graph/attention head + augmentation + ensemble) is openly published and moves monthly. MIT, Stanford, EURECOM, NII, IIIT-Delhi all publish their best methods with code. A better `.pt` file is not a moat — anyone can retrain it in an afternoon on an A100.

**So "beat the world" cannot mean "highest EER on a leaderboard."** It has to mean owning something the world structurally cannot copy fast. There are exactly three such things, and you're positioned for all three:

1. **A proprietary data flywheel** (real Indian fraud-call traffic → on-prem federated learning).
2. **A regulatory + distribution wedge** (on-prem + DPDP + Bhashini/MeitY alignment → banks that legally cannot use Pindrop).
3. **An unclaimed research corner** (telephony-band, cross-lingual **Indic** deepfake detection + attribution — nobody occupies it).

Everything below serves those three.

---

## 1. The AI4Bharat arsenal you now have access to (VERIFIED)

AI4Bharat (IIT-Madras, the lab behind Bhashini's models) has published everything open. This is your unfair advantage as an Indian team — world-class Indic speech resources, free.

### 1.1 Real Indic speech datasets (the "real" class + TTS seed) — `[VERIFIED via HF API]`

| Dataset | Size | Gated | Use |
|---|---|---|---|
| `ai4bharat/indicvoices_r` | **1,047 GB** | auto-approve | TTS-grade real speech, 22 langs |
| `ai4bharat/IndicVoices` | **744 GB** | auto-approve | Natural real speech, 22 langs |
| `ai4bharat/Rasa` | **387 GB** | auto-approve | Expressive/emotional real |
| `ai4bharat/Shrutilipi` | **271 GB** | auto-approve | 6,400h mined real |
| `ai4bharat/Kathbath` | **174 GB** | auto-approve | Read speech, 12 langs |
| `ai4bharat/Rural_Women_ASR_v2` | **127 GB** | **open** | Rural accents (fairness!) |
| `ai4bharat/Rural_Women_Bhojpuri` | **34 GB** | **open** | Bhojpuri rural |
| `ai4bharat/IndicVoices-ST` | 31 GB | auto | Speech-translation |
| `ai4bharat/Lahaja` | 1.4 GB | auto | **Accented Hindi (fairness test)** |
| `ai4bharat/Svarah` | 1.1 GB | auto | Indian-English accents |
| `ai4bharat/indicvoices-cleaned` | 0.4 GB | **open** | Clean subset, quick start |
| `ai4bharat/MANGO` | 1.0 GB | **open** | — |

**These are huge — do NOT download in full** (indicvoices_r alone is 1 TB > your SSD). Grab the **small open ones** (`indicvoices-cleaned`, `Lahaja`, `Svarah`, `Rural_Women_Bhojpuri`) as your real class + fairness test sets, and stream/subset the big ones later on the DGX.

### 1.2 TTS "faker" models to self-host (generate DIVERSE Indic fakes) — `[VERIFIED]`

This is the key to killing your MMS-TTS monoculture. Each is a **different architecture** → different artifacts → broader detector coverage:

| Model | Architecture | Why it matters |
|---|---|---|
| `ai4bharat/IndicF5` | **flow-matching** | Newest, most natural Indic clone |
| `ai4bharat/indic-parler-tts` (+ `-pretrained`) | prompt-conditioned | Controllable Indic voices |
| `ai4bharat/vits_rasa_13` | **VITS expressive** | Emotional fakes |
| `ai4bharat/vits-multilingual-all`, `vits-hi-synthetic`, `vits-hi-base`, `vits-hi-asr-enhanced`, `vits-hi-proximal-chha` | VITS variants | Multiple distinct VITS fingerprints |
| `ai4bharat/bhili-tts` | tribal-language TTS | Ultra-low-resource coverage |

**Combined with the general cloners** (XTTS-v2, F5-TTS, Fish-Speech, MaskGCT, Bark) from the dataset catalog, you can build a **6–10 engine × 12-language** Indic fake corpus. That corpus is itself a moat — it doesn't exist anywhere else.

### 1.3 ASR / language-ID models (routing + scam transcription) — `[VERIFIED]`

- `ai4bharat/indic-conformer-600m-multilingual` — one model, 22 languages, for on-prem transcription (replaces Whisper, no cloud).
- `ai4bharat/indicconformer_stt_<lang>` — 22 per-language ASR models.
- `ai4bharat/indicwav2vec_v1_<lang>` — per-language wav2vec2 (could even be a detector backbone).

Use these **self-hosted** for language-routing and scam-intent transcription → keeps you on-prem, no Bhashini cloud call.

---

## 2. The new-threat radar (defend against the newest fakers)

`[EXTERNAL — AI4Bharat HF activity + landscape research]`

- **"Phir Hera Fairy"** (AI4Bharat, Sept 2026): an English TTS model shown to be a **strong faker of fluent low-resource Indian-language speech**. This is a *brand-new attack family* — an English model cloning Indic voices. **Add its outputs to your training set** the moment weights/samples are public. It also validates your thesis: Indic voice-cloning is now easy and getting easier.
- **Sarvam Bulbul v2/v3** — proprietary Indic-native TTS, another engine to cover.
- **XTTS-v2 / F5-TTS / Fish-Speech / MaskGCT** — general cloners with growing Indic support.

**Winning move:** your detector must be tested against every one of these. The team that has the broadest, freshest Indic attack corpus wins — and that's an operations advantage (keep generating fakes from new engines), not a one-time algorithm.

---

## 3. "What AI hasn't built yet" — the corners you can own

From the frontier R&D report (verified prior-art), these are genuinely thin or unclaimed. Ranked by how winnable they are for a small Indian team:

| # | White-space | Prior art | Your shot |
|---|---|---|---|
| 1 | **On-prem federated continual learning for anti-spoofing on Indic telephony** | No paper unites federated + continual + anti-spoofing. Components exist separately. | **★ The wedge.** Patent the system; the data compounds. |
| 2 | **Telephony-band (8 kHz) Indic vocoder attribution** — identify *which* engine cloned a call, on phone audio | Attribution exists; 8 kHz + Indic = unclaimed | Publishable + patentable niche |
| 3 | **Challenge-response liveness vs real-time clones** | Sparse (mostly preprints/vendor) | High-value, kills the "clone passes voiceprint" attack |
| 4 | **Micro-prosody / vocal-tract-length physiological cues** on telephony | Breathing is taken; micro-prosody + VTL are thin | Supporting signal, publishable |
| 5 | **Cross-lingual transfer tested ON Indic** (train high-resource → test Indic telephony) | Transfer literature is English/Chinese only | First-mover paper |

**You do NOT invent a new physics.** You occupy the intersection nobody bothered with because they're not Indian, not telephony-focused, and not on-prem. That intersection is real, defensible, and yours.

---

## 4. The honest "beat the world" formula

> **World-class Indic attack coverage (operations) + on-prem federated data flywheel (moat) + telephony-band Indic benchmark & attribution (research credibility) + liveness (product completeness) — sold to Indian BFSI/telco that legally cannot use foreign cloud detectors (distribution).**

No single piece is unbeatable. The *combination*, compounding on proprietary Indian fraud data, is.

**What you can truthfully say to a judge/investor/bank:**
- "We cover more Indic cloners than anyone — and we add every new one within days."
- "Our detector improves from each bank's real fraud traffic without any audio leaving their premises." (DPDP-native)
- "We're building the first telephony-band Indic deepfake benchmark + engine-attribution."
- "We run fully on-prem — the one thing Pindrop, Reality Defender, and Hiya structurally cannot offer Indian banks."

**What you must NOT say:** "we invented a detection method no one can replicate," "first Indic dataset" (IndicSynth got there), "99%", or quote the 0.31% without saying "in-corpus ITW."

---

## 5. The 90-day plan to get there

**Days 1–30 (mostly no-GPU, data + prototype):**
- Download the active dataset block (IndicSynth Hi/Ta/Bn/Mr + CodecFake+ + DFADD + FLEURS) → SSD.
- Grab small AI4Bharat real sets (indicvoices-cleaned, Lahaja, Svarah, Rural_Women) as real class + fairness test.
- Download the TTS faker models (IndicF5, indic-parler-tts, vits_rasa_13, XTTS-v2, F5-TTS).
- Prototype the challenge-response liveness endpoint (CPU-only).
- Fix the Telugu/Hindi fairness weakness (per-language recalibration).

**Days 31–60 (GPU, the corpus + the model):**
- Generate the **multi-engine × multi-language Indic fake corpus** (6–10 TTS engines × 12 langs) — this artifact is your moat.
- Retrain XLSR on English + multi-engine Indic + telephony augmentation.
- Measure the numbers that matter: **cross-generator EER, per-language EER, G.711 Indic EER, with bootstrap CIs.**
- Stand up the vocoder-attribution head (which engine made this call).

**Days 61–90 (research + pilot):**
- Publish the **telephony-band Indic benchmark** (leaderboard + paper draft, cite IndicSynth/Indic-CodecFake honestly).
- File a **provisional patent** on the federated-liveness on-prem architecture.
- Get **1 bank/telco LOI** for a pilot on recorded IVR traffic (this is what actually moves valuation, per the earlier analysis).
- Ship the federated-learning MVP: detector that updates on-prem per client.

---

## 6. The one sentence that wins

> **"VoxShield is the on-prem voice-deepfake detector built for India: it covers every Indic cloner, hardens for phone codecs, decides live within seconds, improves from each bank's own fraud traffic without the audio ever leaving their building — and it's the only one an Indian bank can legally deploy."**

That's not "we beat the world at ML." It's "we own the one market the world's best can't legally serve, on a data moat that compounds." **That is how a small team actually wins.**

---

*Sources: AI4Bharat dataset/model sizes and IDs verified via HuggingFace API 2026-09-14; frontier white-spaces from `VOXSHIELD_FRONTIER_RND.md` (7 verified prior-art threads); competitive/regulatory context from `VOXSHIELD_LANDSCAPE_2026.md`; VoxShield measured state from `VOXSHIELD_MASTER_DOSSIER.md`. New-threat items (`Phir Hera Fairy`, Bulbul) are `[EXTERNAL]` — verify weights/samples availability before training on them.*
