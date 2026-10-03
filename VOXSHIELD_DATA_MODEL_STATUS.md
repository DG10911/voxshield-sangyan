# VOXSHIELD — Data & Model Status (AIKosh × HuggingFace × KIOXIA)
### Verified 2026-10-01 · HF user `dg10911` · all catalogued HF repos now GRANTED/OPEN

Legend: ✅ downloaded · 🟢 ready to pull (access OK) · 🔒 RESTRICTED (AIKosh entitlement) · ⛔ gated (now granted) · 🟣 AIKosh HOSTED (pull via `pull.py`)

---

## 1 · Verification
- `HF_TOKEN` set; `hf auth whoami` → **dg10911**.
- Tested **all 27 HF repos** in the catalogue → **all GRANTED/OPEN**. No "Agree and access" clicks left.
- Corrected links: **RasaTTS → `ai4bharat/Rasa`**, **MANGO TTS → `ai4bharat/MANGO`**.

## 2 · KIOXIA inventory (whole SSD)

### 2.1 `/Volumes/KIOXIA/voxdata` — 535 GB (previous work)
| Path | Size | Content |
|---|---|---|
| `raw/indicsynth` | 231 GB | IndicSynth synthetic — Hindi 52 · Telugu 85 · Marathi 40 · Bengali 31 · Malayalam 23 |
| `raw/codecfake_plus` | 94 GB | CodecFake+ |
| `raw/dfadd` | 40 GB | DFADD |
| `raw/indicvoices_real/bengali` | 38 GB | IndicVoices genuine — **Bengali only** |
| `raw/rural_bhojpuri` | 32 GB | Rural Women Bhojpuri |
| `raw/mlaad` | 27 GB | MLAAD (unseen-generator OOD) |
| `in_the_wild` | 16 GB | In-the-Wild |
| `wavefake` | 6.8 GB | WaveFake |
| `raw/banglafake` | 5.3 GB | BanglaFake |
| `models/f5-tts` | 6.3 GB | F5-TTS |
| `models/indic-parler-tts` | 3.5 GB | Indic-Parler-TTS |
| `models/xtts-v2` | 1.9 GB | XTTS v2 |
| `models/indicf5` | 1.3 GB | IndicF5 |
| `raw/lahaja` | 1.3 GB | Lahaja |
| `raw/svarah` | 1.0 GB | Svarah |
| `asvspoof19_LA` | 1.1 GB | ASVspoof 2019 LA |
| `elevenlabs` | 1.0 GB | ElevenLabs fakes |
| `garystafford` | 1.0 GB | wav2vec deepfake-detector data |
| `indicvoices` | 820 MB | real/fake |
| `models/vits_rasa_13` | 153 MB | VITS-Rasa-13 |
| `raw/indicvoices_cleaned` | 426 MB | cleaned IndicVoices |

### 2.2 `/Volumes/KIOXIA/voxshield/data` — new AIKosh pulls
| File | Size |
|---|---|
| `Tamil_male_mono.zip` (IndicTTS Phase-3 Tamil male) | 2.7 GB |
| `IndicSynth/Hindi` (3 shards) | 1.5 GB |
| `Fastspeech2_HS-main.zip` | 227 MB |

### 2.3 Other caches
`hf_cache_active` 7.0 GB · `railcache` 1.9 GB · `hf_cache` 1.4 GB · `whisper_cache` 600 MB

> ⚠️ `voxshield/data/IndicSynth/Hindi` (1.5 GB) **duplicates** `voxdata/raw/indicsynth/Hindi` (52 GB) — safe to delete.

## 3 · Datasets — status (with links)

| Dataset | Coverage | Licence | Link | On KIOXIA |
|---|---|---|---|---|
| IndicSynth | 5 langs (hi/te/mr/bn/ml) | CC-BY-NC-4.0 | https://huggingface.co/datasets/vdivyasharma/IndicSynth | ✅ 231 GB |
| IndicVoices (genuine) | **Bengali only** | CC-BY-4.0 | https://huggingface.co/datasets/ai4bharat/IndicVoices | ✅ 38 GB (1/22) |
| IndicVoices-R | — | CC-BY-ND-4.0 | https://huggingface.co/datasets/ai4bharat/indicvoices_r | 🟢 |
| Shrutilipi | — | CC-BY-4.0 | https://huggingface.co/datasets/ai4bharat/Shrutilipi | 🟢 |
| Vaani (IISc/ARTPARK) | — | CC-BY-4.0 | https://huggingface.co/datasets/ARTPARK-IISc/Vaani | 🟢 |
| MANGO TTS | — | CC-BY-4.0 | https://huggingface.co/datasets/ai4bharat/MANGO | 🟢 |
| Rasa TTS | — | CC-BY-ND-4.0 | https://huggingface.co/datasets/ai4bharat/Rasa | 🟢 |
| Lahaja | — | CC-BY-4.0 | https://huggingface.co/datasets/ai4bharat/Lahaja | ✅ 1.3 GB |
| Svarah | — | CC-BY-4.0 | https://huggingface.co/datasets/ai4bharat/Svarah | ✅ 1.0 GB |
| Rural Women Bhojpuri | — | CC-BY-SA-4.0 | https://huggingface.co/datasets/ai4bharat/Rural_Women_Bhojpuri | ✅ 32 GB |
| Spoken-Tutorial | — | — | https://huggingface.co/datasets/ai4bharat/Spoken-Tutorial | 🟢 |
| Aksharantar | transliteration | CC-BY-SA-4.0 | https://huggingface.co/datasets/ai4bharat/Aksharantar | 🟢 |
| IndicST (Krutrim) | speech-translation | Krutrim | https://huggingface.co/datasets/krutrim-ai-labs/IndicST | 🟢 |
| eka-medical-asr | — | MIT | https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset | 🟢 |
| MoDeTrans / SynthMoDe | transliteration | MIT | https://huggingface.co/datasets/historyHulk/MoDeTrans | 🟢 |
| MLAAD | OOD unseen-gen | research | (local) | ✅ 27 GB |
| CodecFake+ | — | research | (local) | ✅ 94 GB |
| DFADD | — | research | (local) | ✅ 40 GB |
| WaveFake | — | research | (local) | ✅ 6.8 GB |
| In-the-Wild | — | research | (local) | ✅ 16 GB |
| BanglaFake | — | research | (local) | ✅ 5.3 GB |
| ASVspoof2019 LA | — | research | (local) | ✅ 1.1 GB |
| IndicTTS Phase-3 (per lang M/F) | 1 of ~22 | CC-BY-4.0 | AIKosh `c095b3e9…` (Tamil M) | ✅ Tamil M; rest 🟣 |
| SPICOR (Ind-Eng/Guj/SS) | — | CC-BY-4.0 | AIKosh `20ec1d28…/5cfebe30…/92868771…` | 🟣 |
| Kashmiri TTS single-speaker | — | CC-BY-3.0 | AIKosh `a940d4fe…` | 🟣 |
| SPRING-INX (16 langs) | — | CC-BY-4.0 | AIKosh `92029f1b…` (Hindi) | 🟣 |
| SpeeD-TB (Kokborok/Meitei/Toto) | — | CC-BY-4.0 | AIKosh `3f46c900…/c8ceda14…/694b488b…` | 🟣 |
| Dehwali Bhili suite | — | CC-BY-4.0 | AIKosh `69d3cd29…` | 🟣 |
| Gram Vaani Hindi (telephony) | — | CC-BY-NC-4.0 | https://www.openslr.org/118/ | 🟢 research-only |
| Common Voice | multi | CC0-1.0 | https://commonvoice.mozilla.org/ | 🟢 |
| VCTK | en | Other | https://datashare.ed.ac.uk/handle/10283/3443 | 🟢 |
| Mizo / Akashvani broadcasts | — | NC/various | AIKosh (RESTRICTED) | 🔒 |

## 4 · Models — status (with links)

### 4.1 Attack-generation (TTS / VC / clone)
| Model | Licence | Link | On KIOXIA |
|---|---|---|---|
| Bhashini Fastspeech2 (16 Indic) | MIT | AIKosh `7677ccaf…` | ✅ 227 MB |
| IndicF5 | MIT | https://huggingface.co/ai4bharat/IndicF5 | ✅ 1.3 GB |
| Indic-Parler-TTS | MIT | https://huggingface.co/ai4bharat/indic-parler-tts | ✅ 3.5 GB |
| F5-TTS | MIT | https://huggingface.co/SWivid/F5-TTS | ✅ 6.3 GB |
| XTTS v2 | Coqui CPML | https://huggingface.co/coqui/XTTS-v2 | ✅ 1.9 GB |
| VITS-Rasa-13 | MIT | https://huggingface.co/ai4bharat/vits_rasa_13 | ✅ 153 MB |
| Sooktam2 | MIT | https://huggingface.co/bharatgenai/sooktam2 | 🟢 |
| A2TTS speaker-adaptive (Hindi) | MIT | AIKosh `838baccc…` | 🟣/🔒 |
| spk-cond-tts-pflow (5 langs) | MIT | AIKosh | 🔒 |
| SpeechT5 voice-conversion / TTS / vocoder | MIT | https://huggingface.co/microsoft/speecht5_vc | 🟢 |
| Indic-Speak | Other | AIKosh `c0e5c4f2…` | 🟣 |

### 4.2 Detection-support (ASR / SSL / LID / NMT)
| Model | Licence | Link | Status |
|---|---|---|---|
| IndicConformer-600M-Multi | MIT | https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual | 🟢 |
| IndicConformer per-language | MIT | https://huggingface.co/ai4bharat/indicconformer_stt_hi_hybrid_ctc_rnnt_large | 🟢 |
| IndicWav2Vec (per-lang) | MIT | https://huggingface.co/ai4bharat/indicwav2vec_v1_hindi | 🟢 |
| SPRING-INX data2vec (16 langs) | MIT | AIKosh HOSTED | 🟣 |
| SPRING LAB streaming ASR (9) | CC-BY | AIKosh HOSTED | 🟣 |
| AI4Bharat Textual LID | MIT | https://huggingface.co/ai4bharat/indiclid ¹ | 🟢 |
| Bhashini Textual LID v1.0 | — | AIKosh `2531aeb7…` | 🟣 |
| IndicTrans2 | MIT | AIKosh `6f174fcc…` / HF | 🟣 |
| IndicXlit | MIT | AIKosh `418f9c74…` | 🟣 |
| Airavata | MIT | https://huggingface.co/ai4bharat/Airavata | 🟢 |

¹ verify exact repo id at pull time.

## 5 · Detectors — status
| Detector | Status |
|---|---|
| **VoxShield 5-model ensemble** (Acoustic DSP · wav2vec2 · XLS-R-53 · DistilHuBERT · LFCC/CQCC + meta-fusion) | ✅ in repo, measured |
| **VoxShield evidence brains** (physics/replay/environment/cross-codec/phase/temporal/conversational/causal/arbitration/self-critique) | ✅ in repo |
| AIKosh **AI FRAUD DETECTION** (Apache-2.0, `6445fbae…`) | 🔎 found, not pulled |
| AIKosh **DistilBERT-AI-Text-Detector** (`998dc858…`) | 🔎 text-only |
| Audio deepfake **detector model on AIKosh** | ❌ none — AIKosh has data, not ADD models |

## 6 · What's LEFT (gaps)
1. **IndicVoices**: have Bengali only → pull Hindi/Tamil/Telugu/Marathi/Kannada/Gujarati/Odia (all granted).
2. **IndicSynth**: missing Tamil, Kannada, Gujarati, Odia, Punjabi, Sanskrit, Urdu.
3. Not yet pulled: Shrutilipi, Vaani, MANGO, Rasa, Aksharantar, Spoken-Tutorial, IndicST.
4. AIKosh HOSTED to pull via `pull.py`: remaining IndicTTS langs, SPICOR, Kashmiri TTS, SPRING-INX, SpeeD-TB, Dehwali Bhili.
5. Install detection-support models: IndicConformer-600M, IndicWav2Vec, Sooktam2, LID, IndicTrans2, IndicXlit.
6. RESTRICTED entitlements: A2TTS (non-Hindi), spk-cond-pflow, vb TTS, BharatGen-ASR-Hindi, Mizo, Akashvani.
7. Housekeeping: delete the duplicate `voxshield/data/IndicSynth`; extract `Tamil_male_mono.zip`.
8. Downstream (GPU): `scenario_render` → train XLS-R+RawBoost → `eval_gengap` → 0/23 scorecard.
