# VoxShield — Corpus Breakdown (the ~3 TB)

Real sizes (HF trees + AIKosh Content-Range). 2026-10-01.

**Datasets: 2357 GB (~2.36 TB)**  ·  **Models: 136 GB**  ·  **GRAND: 2.49 TB**

> ⚠️ **Dedupe note:** `Shrutilipi` appears **twice** in the catalogue (two AIKosh entries → the same 271 GB HF repo). De-duplicated: **datasets ≈ 2,086 GB**, **grand ≈ 2.22 TB**.

## Datasets — size tiers
| Tier | Sets | Total | Share |
|---|---|---|---|
| ≥100 GB | 6 | 2096.0 GB | 89% |
| 10–100 GB | 3 | 104.4 GB | 4% |
| 1–10 GB | 49 | 152.6 GB | 6% |
| <1 GB | 20 | 4.1 GB | 0% |

## The 6 big sets (84% of all data)
| Dataset | Size | Role | Keep after training? |
|---|---|---|---|
| IndicSynth | 540 GB | synthetic Indic ADD benchmark (12 langs) | ❌ re-downloadable |
| IndicVoices-R | 428 GB | re-synthesized IndicVoices (attack) | ❌ re-downloadable |
| VAANI: Multi-modal, Multi-lingual Dataset | 309 GB | pan-India genuine accents/dialects | ❌ re-downloadable |
| RasaTTS | 276 GB | Indic TTS corpus (12 langs) | ❌ re-downloadable |
| Shrutilipi (AI4Bharat) | 271 GB | 6,400 h genuine ASR (12 langs) | ❌ re-downloadable |
| Shrutilipi | 271 GB | 6,400 h genuine ASR (12 langs) | ❌ re-downloadable |

## Models — breakdown
| Tier | Sets | Total |
|---|---|---|
| ≥10 GB | 3 | 57.1 GB |
| 1–10 GB | 18 | 61.8 GB |
| 100 MB–1 GB | 35 | 16.5 GB |
| <100 MB | 4 | 0.1 GB |

**Largest models:**
- 27.5 GB — AI4Bharat - Airavata: Large-Scale Multilingual Model for
- 17.5 GB — shuka-v1
- 12.2 GB — Indic-Translate
- 9.9 GB — Parrotlet-A-2p5-Pro
- 6.0 GB — AI4Bharat- IndicSeamless
- 5.0 GB — Indic-Speak
- 4.9 GB — Hades-8B
- 4.5 GB — Indic-Transcribe-Flex
- 4.0 GB — BHASHINI IISC Sourashtra Vits TTS Models
- 3.8 GB — AI4Bharat-Indic-Parler-TTS-Pretrained: Text to Speech Mo
- 3.8 GB — AI4Bharat-Indic-Parler-TTS: Text to Speech Model
- 3.1 GB — Northeast STT Multilingual Speech to Text Model

## Keep vs delete (post-training)
**DELETE (re-downloadable / re-generatable):**
- the 6 big sets + IndicTTS/SPRING-INX corpora + all raw public corpora → **~2.3 TB**
- HF cache / feature cache / __pycache__ → regenerable
- generated Worst-AI clips (re-run `gen_worst_ai.py`)

**KEEP (the product / not reproducible):**
- **fine-tuned checkpoint + config + fusion head** (~1–3 GB) ← the detector
- inference-time base models actually used (XLS-R/wav2vec2 ~1.2 GB, ECAPA ~80 MB, NeMo Sortformer ~500 MB)
- manifests, registries, provenance, threat/intel graph (MBs)
- Golden / Zero-Day / Worst-Human curated sets (not re-downloadable)
- **consented/private recordings** (cannot re-download — keep on KIOXIA/DGX only)

**Typical result:** 2.5 TB → **~10–50 GB** after training.

## Minimal subset for ONE training run (~120–200 GB, not 2.5 TB)
| Need | Use | Size |
|---|---|---|
| Attack-side (synthetic) | IndicSynth (Hindi+Te+Mr+Bn+Ml) + your Bhashini/IndicF5 clips | ~150 GB (or subset) |
| Genuine genuine | IndicVoices (8 langs) + Shrutilipi (hi/ta) + Bhashini TTS-as-genuine | ~60 GB subset |
| Channel realism | `scenario_render` G.711 (renders on the fly, no storage) | 0 |
| OOD eval | MLAAD / CodecFake+ / DFADD (if not already local) | ~20 GB subset |

Re-pull anytime: `backend/aikosh_ingest.py`, `pull.py`, `pull_p1.sh`, `deploy/dgx/dgx_pull_voxshield.sh` + `AIKOSH_MASTER_LIST.md` (ids/licences).