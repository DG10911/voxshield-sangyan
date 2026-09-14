# VoxShield Dataset Catalog

Definitive, download-ready catalog of voice/speech datasets for **VoxShield** — a
voice-deepfake detector for **Indic-language telephony fraud**.

- **Target SSD:** `/Volumes/KIOXIA/voxdata/` — **802 GB free** (931 GB volume).
- **Tooling:** venv `hf` CLI at
  `/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/.venv_voxshield/bin/hf`
  (`huggingface_hub` 0.36.2). `curl` available. **No `wget` / `aria2c`.**
- **HF auth:** already logged in as **`dg10911`** — gated repos work *after* you click
  "Agree and access" on each dataset's HF page.
- **Companion script:** `download_datasets.sh` (P0+P1 active, P2/P3 commented out).

## ✅ VERIFICATION UPDATE (2026-09-14) — read this first

The rows below were later **verified live** via the HF API. Confirmed facts that OVERRIDE
the `[unverified]` tags in the older table:

| Dataset | Repo ID (verified) | Size (verified) | Gated | License |
|---|---|---|---|---|
| **IndicSynth** | `vdivyasharma/IndicSynth` | **845 GB total** (1,414 files) | **open** | CC (see repo) |
| **CodecFake+** | `CodecFake/CodecFake_Plus_Dataset` | **101 GB** (1.42M clips) | open | MIT |
| **DFADD** | `isjwdu/DFADD` | **42.7 GB** (~208k clips) | open | MIT |
| **ASVspoof5** | `jungjee/asvspoof5` | **142 GB** | open (mirror) | see repo |
| **SpoofCeleb** | `jungjee/spoofceleb` | **134 GB** | **GATED — institutional email** | CC-BY-4.0 |
| **Kathbath** | `ai4bharat/Kathbath` | large | auto-approve | CC-BY-4.0 |
| **IndicVoices-R** | `ai4bharat/IndicVoices-R` | large | **gated** | CC-BY-4.0 |
| **IndicSUPERB** | `ai4bharat/indicsuperb` | large | **gated** | CC-BY-4.0 |
| **FLEURS** | `google/fleurs` | ~2–3 GB/lang | open | CC-BY-4.0 |
| **Common Voice 17** | `mozilla-foundation/common_voice_17_0` | ~GB/lang | **gated** | CC0 |
| TTS models (all verified live) | `ai4bharat/IndicF5`, `ai4bharat/indic-parler-tts`, `coqui/XTTS-v2`, `SWivid/F5-TTS`, `fishaudio/fish-speech-1.5`, `amphion/MaskGCT`, `suno/bark`, `myshell-ai/OpenVoiceV2` | 1–4 GB each | open | mixed (see below) |

**🚨 IndicSynth is 845 GB — LARGER than your 802 GB free space.** It is organized
per-language, so you MUST download a subset. Per-language sizes (GB): Sanskrit 167,
Tamil 148, Punjabi 100, Telugu 91, Kannada 68, Hindi 56, Gujarati 50, Marathi 42,
Urdu 37, Bengali 33, Malayalam 24, Odia 23. The `download_datasets.sh` script pulls only
the languages in its `INDIC_LANGS` array (default Hi/Ta/Bn/Mr ≈ 279 GB).

Still unverified (confirm the exact host/id before downloading): Indic-CodecFake repo id,
BanglaFake host, HAV-DF host, ST-Codecfake / LibriSeVoc / CVoiceFake / FoR exact sizes
(Zenodo pages timed out during verification).

---

## Older auto-compiled note (superseded by the table above)

Four research sub-agents verified IDs against live pages; their findings did not reach the
compiler before it first wrote this file, so tags below may say `[unverified]` even where the
update table above confirms them. **Trust the verification table above over inline tags.**

Already on the SSD (do **not** re-download; upgrade notes only): `asvspoof19_LA`,
`codecfake`, `elevenlabs`, `garystafford`, `in_the_wild`, `indicvoices`, `speechfake`,
`wavefake`.

---

## A) Master table (sorted by priority)

Priority key: **P0** = Indic fakes (fixes the MMS-TTS monoculture — top need) · **P1** =
multilingual + codec benchmarks · **P2** = English/general benchmarks (cross-dataset
generalization) · **P3** = extra real speech (real class + TTS seed).

| Pri | Dataset | Repo ID / URL | ~Size | Clips/Hours | Langs | Real/Fake | License | Gated |
|-----|---------|---------------|-------|-------------|-------|-----------|---------|-------|
| P0 | **IndicSynth** | `vdivyasharma/IndicSynth` **[unverified id]** | ~200 GB **[unverified]** | ~4000 h | 12 Indic | Fake (synthetic) | research/CC **[unverified]** | likely gated **[unverified]** |
| P0 | **Indic-CodecFake** | `helixometry/IndicFake` **[unverified id]** | **[unverified]** | **[unverified]** | Indic | Fake (codec) | **[unverified]** | **[unverified]** |
| P0 | **HAV-DF** (Hindi A/V) | GitHub **[unverified]** | **[unverified]** | **[unverified]** | Hindi | Fake | **[unverified]** | n/a |
| P0 | **BanglaFake** | HF/GitHub **[unverified]** | **[unverified]** | **[unverified]** | Bengali | Fake | **[unverified]** | **[unverified]** |
| P1 | **MLAAD** (v5) | `mueller91/MLAAD` | ~160 GB **[unverified]** | 38 langs incl. some Indic | multi | Fake | CC-BY-NC-SA-4.0 **[unverified]** | open **[unverified]** |
| P1 | **M-AILABS** (real pair for MLAAD) | caito.de / OpenSLR mirror **[unverified]** | ~40 GB **[unverified]** | ~1000 h | multi (EU) | Real | free/BSD-like **[unverified]** | no |
| P1 | **XMAD-Bench** | HF **[unverified]** | **[unverified]** | multi | Fake bench | **[unverified]** | **[unverified]** | **[unverified]** |
| P1 | **MLADDC** | HF **[unverified]** | **[unverified]** | multi | Fake bench | **[unverified]** | **[unverified]** | **[unverified]** |
| P1 | **CodecFake+ / ST-Codecfake** | HF/Zenodo **[unverified]** | **[unverified]** | English+ | Fake (codec) | **[unverified]** | **[unverified]** | **[unverified]** |
| P2 | **ASVspoof5** (2024) | asvspoof.org / Zenodo **[unverified]** | ~300+ GB **[unverified]** | very large | English | Real+Fake | ODC-By / research **[unverified]** | registration **[unverified]** |
| P2 | **ASVspoof2021 LA** | Zenodo **[unverified record]** | ~8 GB **[unverified]** | English | Real+Fake | research | no |
| P2 | **ASVspoof2021 DF** | Zenodo **[unverified record]** | ~25 GB **[unverified]** | English | Real+Fake | research | no |
| P2 | **SpoofCeleb** | HF **[unverified id]** | ~40 GB **[unverified]** | English | Real+Fake | **[unverified]** | **[unverified]** |
| P2 | **DFADD** | HF **[unverified id]** | ~30 GB **[unverified]** | English | Fake (diffusion/FM TTS) | **[unverified]** | **[unverified]** |
| P2 | **CVoiceFake** | HF/Zenodo **[unverified]** | **[unverified]** | multi | Fake (codec) | **[unverified]** | **[unverified]** |
| P2 | **LibriSeVoc** | GitHub/Zenodo **[unverified]** | ~7 GB **[unverified]** | English | Real+Fake (vocoder) | research | no |
| P2 | **FoR (Fake-or-Real)** | bil.eecs.yorku.ca **[unverified]** | ~35 GB **[unverified]** | English | Real+Fake | research | no |
| P2 | **ADD2023** | official (may be closed) **[unverified]** | **[unverified]** | Mandarin | Fake | restricted **[unverified]** | yes **[unverified]** |
| P3 | **Common Voice 17** (Indic subsets) | `mozilla-foundation/common_voice_17_0` | ~5-30 GB/lang | many h | hi/ta/bn/mr/te/… | Real | CC0 | **gated** |
| P3 | **FLEURS** (Indic configs) | `google/fleurs` | ~2-3 GB/lang | ~10 h/lang | hi/ta/bn/mr/te/… | Real | CC-BY-4.0 | open |
| P3 | **IndicVoices-R** | `ai4bharat/IndicVoices-R` **[unverified id]** | ~large | ~1700 h | 22 Indic | Real (TTS-grade) | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **Kathbath** | `ai4bharat/Kathbath` **[unverified id]** | ~large | ~1684 h | 12 Indic | Real | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **Shrutilipi** | `ai4bharat/Shrutilipi` **[unverified id]** | ~large | ~6400 h | 12 Indic | Real | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **IndicTTS** | `ai4bharat/indictts` **[unverified id]** | ~moderate | multi h | Indic | Real (studio) | research | **[unverified]** |
| P3 | **Rasa** | `ai4bharat/Rasa` **[unverified id]** | ~moderate | expressive | Indic | Real | **[unverified]** | **[unverified]** |
| P3 | **IndicSUPERB** | `ai4bharat/IndicSUPERB` **[unverified id]** | ~large | ~1684 h | 12 Indic | Real | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **Lahaja** | `ai4bharat/Lahaja` **[unverified id]** | ~moderate | accented Hindi | Hindi | Real | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **Vaani** (IISc-Google) | `ARTPARK-IISc/Vaani` **[unverified id]** | very large | 1000s h | many Indic | Real | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **SPRING-INX** | IIT-M / OpenSLR **[unverified]** | large | multi h | Indic | Real | **[unverified]** | **[unverified]** |
| P3 | **SYSPIN** | HF/official **[unverified]** | large | multi h | 9 Indic | Real (TTS) | CC-BY-4.0 **[unverified]** | **[unverified]** |
| P3 | **OpenSLR SLR63** | openslr.org/63 (Malayalam) | ~5 GB **[unverified]** | ~1.8k utt | Malayalam | Real | CC-BY-SA-4.0 | no |
| P3 | **OpenSLR SLR64** | openslr.org/64 (Marathi) | ~3 GB **[unverified]** | Marathi | Real | CC-BY-SA-4.0 | no |
| P3 | **OpenSLR SLR65** | openslr.org/65 (Tamil) | ~4 GB **[unverified]** | Tamil | Real | CC-BY-SA-4.0 | no |
| P3 | **OpenSLR SLR66** | openslr.org/66 (Telugu) | ~4 GB **[unverified]** | Telugu | Real | CC-BY-SA-4.0 | no |
| P3 | **OpenSLR SLR103 (MUCS)** | openslr.org/103 | ~20 GB **[unverified]** | multi | 6+ Indic | Real | CC-BY-4.0 | no |

> Sizes marked **[unverified]** are estimates — confirm on the repo page's "Files and
> versions" tab before relying on the download plan totals.

---

## B) Size-aware download plan (fits ~700 GB, leaves headroom on 802 GB)

Grab in this order; stop when you approach ~700 GB. Because several P0 sizes are
**[unverified]**, run `hf download ... --dry-run` **[unverified flag support]** or check the
repo's file listing first and re-check `df -h /Volumes/KIOXIA` between big pulls.

**REVISED with verified sizes (this is what `download_datasets.sh` does):**

| Step | Dataset | Verified size | Running total | In script? |
|------|---------|---------------|---------------|-----------|
| 1 | **IndicSynth subset** — Hindi 56 + Tamil 148 + Bengali 33 + Marathi 42 | **279 GB** | 279 GB | ✅ active |
| 2 | **CodecFake+** (telephony-relevant, MIT) | **101 GB** | 380 GB | ✅ active |
| 3 | **DFADD** (diffusion/FM fakes, MIT) | **43 GB** | 423 GB | ✅ active |
| 4 | **FLEURS** Indic (real class / eval) | ~15 GB | 438 GB | ✅ active |
| 5 | ASVspoof5 (English cross-dataset) | 142 GB | 580 GB | 🔲 opt-in |
| 6 | Common Voice Indic (real seed, gated) | ~40 GB | 620 GB | 🔲 opt-in |
| 7 | Kathbath (Indic real, auto-approve) | large | — | 🔲 opt-in |

**Recommendation:** run the active block first (**~438 GB** — comfortable on 802 GB free).
Drop Tamil from `INDIC_LANGS` to save 148 GB if you want lots of headroom (→ ~290 GB).
Add ASVspoof5 (142 GB) only if you want the English cross-dataset number; it fits alongside
the active block (580 GB total). **SpoofCeleb (134 GB) is gated to institutional email — a
gmail account will likely be rejected, so treat it as unavailable for now.** Skip the full
845 GB IndicSynth — you physically cannot fit it.

---

## C) TTS / voice-clone models to self-host (generate NEW fakes)

Download to `$VOXDATA/models/<name>` (model repos default to `--repo-type model`).

| Model | Repo | ~Size | License | Indic? | Generate a fake clip |
|-------|------|-------|---------|--------|----------------------|
| **IndicF5** | `ai4bharat/IndicF5` **[unverified id]** | ~1-3 GB | research **[unverified]** | Yes (Indic) | F5-TTS-style flow-matching infer with a ref clip + target text |
| **Indic Parler-TTS** | `ai4bharat/indic-parler-tts` **[unverified id]** | ~2-4 GB | Apache/CC **[unverified]** | Yes (many Indic) | `ParlerTTSForConditionalGeneration` + text description prompt |
| **Parler-TTS mini** | `parler-tts/parler-tts-mini-v1` | ~1.5 GB | Apache-2.0 | English (base) | prompt-conditioned TTS via `parler_tts` |
| **MMS-TTS** | `facebook/mms-tts-hin`, `-tam`, `-ben`, `-mar`, `-tel` | ~0.5 GB each | CC-BY-NC-4.0 | Yes (per-lang) | `VitsModel` + `AutoTokenizer` forward pass (what SSD already leans on — diversify away) |
| **XTTS-v2** | `coqui/XTTS-v2` | ~1.8 GB | Coqui CPML (non-commercial) | multilingual, no native Indic | `TTS` lib: `tts.tts_to_file(text, speaker_wav, language)` |
| **F5-TTS** | `SWivid/F5-TTS` | ~1.4 GB | CC-BY-NC / MIT code | via fine-tune (IndicF5) | `f5-tts_infer-cli --ref_audio --gen_text` |
| **Fish-Speech** | `fishaudio/fish-speech-1.5` **[unverified version]** | ~1 GB | CC-BY-NC-SA (weights) | multilingual | `fish-speech` CLI, ref-audio clone |
| **GPT-SoVITS** | GitHub `RVC-Boss/GPT-SoVITS` | ~2 GB | MIT (code) | some (fine-tunable) | few-shot clone via WebUI/infer script |
| **StyleTTS2** | GitHub `yl4579/StyleTTS2` | ~0.8 GB | MIT | English (base) | `inference` with ref style + text |
| **Bark** | `suno/bark` | ~4 GB | MIT | multilingual (incl. Hindi) | `bark.generate_audio(text)` |
| **MaskGCT** | `amphion/MaskGCT` | ~4 GB **[unverified]** | CC-BY-NC / Amphion | multilingual | Amphion MaskGCT zero-shot infer w/ prompt wav |
| **OpenVoice v2** | `myshell-ai/OpenVoiceV2` | ~1 GB | MIT | tone-color clone atop base TTS | extract tone color + apply to base TTS output |

**Attack-family diversification note:** the deployed detector was trained heavily on
MMS-TTS-style fakes. Prioritize generating with **architecturally distinct** families —
flow-matching (IndicF5/F5-TTS), diffusion/masked-codec (MaskGCT, Bark), and GAN/vocoder
paths — to break the monoculture.

---

## Download command reference

Datasets: `hf download <repo_id> --repo-type dataset --local-dir $VOXDATA/<name>`
Models:   `hf download <repo_id> --local-dir $VOXDATA/models/<name>`
Zenodo/OpenSLR/direct: `curl -L -o $VOXDATA/<name>/<file> "<url>"`

**Gated sets** (need "Agree and access" clicked once on the HF page while logged in as
`dg10911`): Common Voice (`mozilla-foundation/common_voice_17_0`), and likely IndicSynth
and several AI4Bharat repos **[unverified]**. FLEURS and MLAAD are open **[unverified for
MLAAD]**.
