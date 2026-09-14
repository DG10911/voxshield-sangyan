# VoxShield — Master Ranked Dataset List

*The definitive, ranked reference of every voice/speech dataset relevant to VoxShield (voice-deepfake detection for Indic-language telephony fraud). Sizes/IDs/gating **verified live via HuggingFace API on 2026-09-14** unless tagged `[verify]`.*

**Legend:** 🟢 open · 🔑 gated-auto (click "Agree", instant) · 🔒 gated-manual (institutional email) · ✅ already on your KIOXIA SSD
**Ranking = usefulness to VoxShield's mission** (Indic + fake + telephony), not raw size.

---

## TIER S — Highest value (Indic fakes + Indic real). Build the moat here.

| # | Dataset | Provider | Size | Real/Fake | Langs | What it does / best feature | License | Access |
|---|---|---|---|---|---|---|---|---|
| 1 | **IndicSynth** | Divya Sharma et al. (ACL 2025) | **845 GB** (subset by lang) | Fake | 12 Indic | The one that fixes your MMS-TTS monoculture: XTTS-v2 + VITS + FreeVC fakes, mimicry+diversity subsets. Per-lang GB: Sanskrit167 Tamil148 Punjabi100 Telugu91 Kannada68 Hindi56 Gujarati50 Marathi42 Urdu37 Bengali33 Malayalam24 Odia23 | CC BY-NC 4.0 | 🟢 `vdivyasharma/IndicSynth` |
| 2 | **IndicVoices** | AI4Bharat | **744 GB** | Real | 22 Indic | Natural conversational real Indian speech — the gold real-class + TTS seed | CC-BY-4.0 | 🔑 `ai4bharat/IndicVoices` |
| 3 | **IndicVoices-R** | AI4Bharat | **1,047 GB** | Real | 22 Indic | TTS-grade studio real speech (1,700h). Huge — stream/subset on DGX | CC-BY-4.0 | 🔑 `ai4bharat/IndicVoices-R` |
| 4 | **Indic-CodecFake** | IIIT-Delhi (ACL 2026) | `[verify]` | Fake | 12 Indic | Neural-codec (8 families) Indic fakes — matches your codec-hardening story exactly | `[verify]` | 🔒 `[verify id]` project: helixometry.github.io/IndicFake |
| 5 | **Rural_Women_ASR_v2** | AI4Bharat | **127 GB** | Real | Indic | Rural-accent real speech → your **fairness test** (weak Telugu/Hindi) | CC-BY | 🟢 `ai4bharat/Rural_Women_ASR_v2` |
| 6 | **Lahaja** | AI4Bharat | **1.4 GB** | Real | Accented Hindi | Small, targeted **accent-robustness test set** | CC-BY-4.0 | 🔑 `ai4bharat/Lahaja` |
| 7 | **indicvoices-cleaned** | AI4Bharat | **0.4 GB** | Real | Indic | Tiny clean subset — instant quick-start real class | CC-BY | 🟢 `ai4bharat/indicvoices-cleaned` |
| 8 | **BanglaFake** | Fahad et al. (2025) | `[verify ~GB]` | Both | Bengali | 12.3k real + 13.3k fake Bengali, SOTA TTS | `[verify]` | `[verify]` arXiv 2505.10885 |

---

## TIER A — Multilingual + codec deepfake benchmarks (cross-generator generalization)

| # | Dataset | Provider | Size | Real/Fake | Langs | What it does / best feature | License | Access |
|---|---|---|---|---|---|---|---|---|
| 9 | **CodecFake+** | CodecFake team (2025) | **100.5 GB** | Both | English+ | 1.42M clips, **30+ neural codecs** — the codec-robustness workhorse | MIT | 🟢 `CodecFake/CodecFake_Plus_Dataset` |
| 10 | **MLAAD** | Fraunhofer/Müller | **34.7 GB** | Fake | 40+ (incl Hi/Bn/Mr/Ta) | Multi-language anti-spoofing; 200+ TTS models. Thin per-Indic but great cross-lingual eval | CC-BY-NC-SA | 🔑 `mueller91/MLAAD` |
| 11 | **ST-Codecfake** | Xie et al. (2025) | `[verify]` | Fake | EN+ZH | 11 neural-codec methods + audio-LM OOD test — source-tracing frontier | CC BY-NC-ND | Zenodo 14631091 |
| 12 | **CVoiceFake** | SafeEar (CCS 2024) | `[verify ~large]` | Both | 5 (EN/ZH/DE/FR/IT) | 1.25M clips, 6 vocoders, from Common Voice | `[verify]` | Zenodo 11229569 |

---

## TIER B — English/general deepfake benchmarks (honest cross-dataset numbers)

| # | Dataset | Provider | Size | Real/Fake | Langs | What it does / best feature | License | Access |
|---|---|---|---|---|---|---|---|---|
| 13 | **ASVspoof5** | ASVspoof (2024) | **142 GB** | Both | English | The current standard: 32 attacks + adversarial, 2k speakers | see repo | 🟢 `jungjee/asvspoof5` |
| 14 | **In-the-Wild** ✅ | Müller (2022) | **8.2 GB** | Both | English | Real-world celeb deepfakes — your current headline benchmark | research | 🟢 `mueller91/In-The-Wild` |
| 15 | **DFADD** | Du et al. (2024) | **42.7 GB** | Fake | English | **Diffusion + flow-matching** TTS fakes (the modern attack class) | MIT | 🟢 `isjwdu/DFADD` |
| 16 | **SpoofCeleb** | Jung et al. | **134 GB** | Both | English | SASV/ASV + deepfake at scale | CC-BY-4.0 | 🔒 institutional email (gmail rejected) |
| 17 | **ASVspoof 2021 LA+DF** | ASVspoof | ~8+25 GB `[verify]` | Both | English | Classic LA/DF eval — comparability with literature | research | Zenodo 4837263 / 4835108 |
| 18 | **LibriSeVoc** | Sun et al. | ~7 GB `[verify]` | Both | English | 6 vocoders self-vocoded from LibriTTS — vocoder-artifact study | CC-BY-SA | Zenodo 15127251 |
| 19 | **FoR (Fake-or-Real)** | York U | ~35 GB `[verify]` | Both | English | 195k utts, 4 versions (norm/2sec/rerec) | research | bil.eecs.yorku.ca |
| 20 | **ASVspoof19 LA** ✅ | ASVspoof | on SSD | Both | English | Standard training protocol | research | ✅ SSD |
| 21 | **WaveFake** ✅ | Frank & Schönherr | on SSD | Fake | English | GAN-vocoder fakes (LJSpeech base) | research | ✅ SSD |
| 22 | **codecfake / speechfake** ✅ | — | on SSD | Fake | — | Codec + general fakes | — | ✅ SSD |
| 23 | **elevenlabs / garystafford** ✅ | — | on SSD | Both | English | Commercial-cloner + curated fakes | — | ✅ SSD |

---

## TIER C — Real Indic speech (real class + TTS seed). Big; subset or grab small ones.

| # | Dataset | Provider | Size | Langs | What it does / best feature | Access |
|---|---|---|---|---|---|---|
| 24 | **Rasa** | AI4Bharat | 387 GB | Indic | Expressive/emotional real speech (hardest for TTS to match) | 🔑 `ai4bharat/Rasa` |
| 25 | **Shrutilipi** | AI4Bharat | 271 GB | 12 Indic | 6,400h mined real — largest real corpus | 🔑 `ai4bharat/Shrutilipi` |
| 26 | **SpeechArenaBench** | AI4Bharat | 259 GB | Indic | Speech eval benchmark | 🔑 `ai4bharat/SpeechArenaBench` |
| 27 | **Kathbath** | AI4Bharat | 174 GB | 12 Indic | Read speech, clean, per-language | 🔑 `ai4bharat/Kathbath` |
| 28 | **Rural_Women_Bhojpuri** | AI4Bharat | 34 GB | Bhojpuri | Ultra-low-resource rural real | 🟢 `ai4bharat/Rural_Women_Bhojpuri` |
| 29 | **IndicVoices-ST** | AI4Bharat | 31 GB | Indic | Speech-translation paired | 🔑 `ai4bharat/IndicVoices-ST` |
| 30 | **Svarah** | AI4Bharat | 1.1 GB | Indian English | Indian-accented English (Svarah) — accent robustness | 🔑 `ai4bharat/Svarah` |
| 31 | **FLEURS** | Google | 878 GB all / ~2-3 GB per Indic config | 102 (incl Indic) | Clean read speech, easy per-language subset for eval | 🟢 `google/fleurs` |
| 32 | **Common Voice 17** | Mozilla | per-lang (config download) | many Indic | Crowd real speech, CC0 — TTS seed | 🔑 `mozilla-foundation/common_voice_17_0` |
| 33 | **indicvoices (yours)** ✅ | AI4Bharat | on SSD (4k clips) | 10 Indic | Your existing Indic real set | ✅ SSD |
| 34 | **OpenSLR SLR63-66, 103** | OpenSLR/Google | 3–20 GB each | Ml/Mr/Ta/Te/multi | Small clean per-language real | 🟢 openslr.org |

---

## TIER D — TTS / voice-clone MODELS (not datasets) — self-host to GENERATE fakes

*Each is a distinct architecture → distinct artifacts → broader detector coverage. Download to `$VOXDATA/models/`.*

| # | Model | Provider | Arch | Indic? | Best feature | Access |
|---|---|---|---|---|---|---|
| M1 | **IndicF5** | AI4Bharat | flow-matching | ✅ native | Newest, most natural Indic clone | 🟢 `ai4bharat/IndicF5` |
| M2 | **indic-parler-tts** | AI4Bharat | prompt TTS | ✅ many | Controllable Indic voices via text prompt | 🟢 `ai4bharat/indic-parler-tts` |
| M3 | **vits_rasa_13** | AI4Bharat | VITS expressive | ✅ | Emotional Indic fakes | 🟢 `ai4bharat/vits_rasa_13` |
| M4 | **vits-multilingual-all / vits-hi-synthetic** | AI4Bharat | VITS variants | ✅ | Multiple distinct VITS fingerprints | 🟢 `ai4bharat/vits-*` |
| M5 | **MMS-TTS** ✅ | Meta | VITS | ✅ per-lang | (your current fakes — diversify AWAY from this) | 🟢 `facebook/mms-tts-<lang>` |
| M6 | **XTTS-v2** | Coqui | GPT+diffusion | multilingual | Strong zero-shot clone from ref audio | 🟢 `coqui/XTTS-v2` (CPML non-commercial) |
| M7 | **F5-TTS** | SWivid | flow-matching | via IndicF5 | Fast high-quality clone | 🟢 `SWivid/F5-TTS` |
| M8 | **Fish-Speech 1.5** | Fish Audio | codec-LM | multilingual | Codec-LM family (matches CodecFake threat) | 🟢 `fishaudio/fish-speech-1.5` |
| M9 | **MaskGCT** | Amphion | masked-codec | multilingual | Masked generative codec transformer | 🟢 `amphion/MaskGCT` |
| M10 | **Bark** | Suno | codec-LM | incl Hindi | Multilingual incl Hindi | 🟢 `suno/bark` |
| M11 | **OpenVoice v2** | MyShell | tone-color clone | atop base TTS | Fast tone-color transfer | 🟢 `myshell-ai/OpenVoiceV2` |
| M12 | **"Phir Hera Fairy"** | AI4Bharat (Sept 2026) | English-faker | ✅ Indic | NEW: English model that clones Indic well — add when weights public | `[verify]` |

---

## Size-aware pull plan (802 GB SSD free)

**Grab first (~438 GB, comfortable):**
1. IndicSynth Hi+Ta+Bn+Mr → 279 GB
2. CodecFake+ → 100 GB
3. DFADD → 43 GB
4. FLEURS Indic configs + small AI4Bharat real (indicvoices-cleaned, Lahaja, Svarah) → ~16 GB

**Then optionally (fits alongside):** ASVspoof5 142 GB → 580 GB total.
**Then TTS models** (~20 GB for all 11) → generate your own multi-engine Indic fakes.

**Do NOT try to fully download:** IndicSynth (845), IndicVoices-R (1 TB), IndicVoices (744), FLEURS-all (878) — subset by language/config.
**Unavailable:** SpoofCeleb (institutional email only).

---

## The 5 that matter most for VoxShield right now

1. **IndicSynth** (subset) — multi-cloner Indic fakes, fixes your #1 gap.
2. **CodecFake+** — telephony/codec robustness at scale.
3. **DFADD** — diffusion/flow-matching fakes (the modern attack class).
4. **AI4Bharat TTS models** (IndicF5 + parler + vits) — generate *your own* diverse fakes = the moat corpus.
5. **Rural_Women + Lahaja + Svarah** — fairness/accent test sets to fix weak Telugu/Hindi.

*All IDs verified live 2026-09-14. Items tagged `[verify]` (Indic-CodecFake, BanglaFake exact host/size, ST-Codecfake/CVoiceFake/LibriSeVoc/FoR sizes) returned 401/timeout during verification — confirm on the source page before downloading.*
