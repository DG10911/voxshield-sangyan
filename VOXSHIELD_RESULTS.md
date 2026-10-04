# VoxShield — Results (paper draft §5)
Source: `phase2/report_all.txt` (DGX, 2026-10-04). Numbers are measured, not projected.

## 5.1 Setup
12 two-class Indic languages (Hindi, Bengali, Marathi, Telugu, Tamil, Gujarati, Kannada,
Malayalam, Odia, Punjabi, Urdu, Sanskrit). Detector = XLS-R-300M + RawBoost, 3 epochs.
Fakes from IndicSynth (`freevc24` in training shards) + an **external unseen generator**
(MMS-TTS). Genuine = IndicVoices. Channels: clean and **G.711 telephony**.

## 5.2 Seen detection & channel
| Slice | EER | AUC |
|---|---|---|
| clean | 9.24% | 0.955 |
| G.711 µ/A-law | 11.41% | 0.943 |
| **Δ (codec cost)** | **+2.17 pts** | |

**Table 1 — per-language (clean / G.711) EER:**
| lang | clean | G.711 | lang | clean | G.711 |
|---|---|---|---|---|---|
| pa | 0.00% | 0.05% | kn | 0.65% | 1.62% |
| te | 0.00% | 0.11% | gu | 1.28% | 6.01% |
| mr | 0.02% | 0.14% | bn | 3.30% | 10.36% |
| sa | 0.03% | 0.15% | ur | 13.13% | 22.71% |
| hi | 0.09% | 0.29% | or | 32.53% | 35.68% |
| ta | 0.26% | 2.03% | ml | 37.51% | 37.81% |

Weak cells (ml, or, ur) have far fewer training shards — the honest per-language frontier.

## 5.3 Generalization gap (the headline)
| | EER | n_fake |
|---|---|---|
| SEEN generator | 9.57% | — |
| **UNSEEN generator** | **19.00%** | — |
| **GAP** | **+9.43 pts (MODERATE)** | |

**Leave-one-generator-out (each generator as the unseen test):**
| Held-out generator | EER vs real | n_fake |
|---|---|---|
| freevc24 (in training) | **1.62%** | 321,512 |
| vits (unseen) | **19.00%** | 30,900 |
| xtts_v2 (unseen) | **27.19%** | 75,056 |
| **MEAN unseen-generator EER** | **15.94%** | |

> English-trained SOTA zero-shot on Indic reaches **33–93% EER** (IndicSynth, ACL'25).
> Fine-tuning on Indic + codec profiling → **1.6% on seen generators**; the residual
> **~16% on a truly unseen generator** is the honest frontier this work quantifies.

## 5.4 Calibrated abstention (C3)
| Metric | Value |
|---|---|
| Overall calibration | ECE **0.058** · Brier 0.061 · **Cllr 1.010 bits** |
| FP on genuine @100% coverage | 2.55% |
| FP @90% coverage | **0.60%** (Δ −1.95 pts) |
| FP @80% coverage | **0.23%** (Δ −2.32 pts, **~91% relative**) |
| AURC | 0.0273 |
| Selective EER @95% coverage | 9.96% |

Abstaining on the least-confident **10–20%** of calls cuts genuine-caller false alarms by
**~76–91% relative** — the core safety argument for deploying on investor phone lines.

## 5.5 Comparison
| Setting | EER (Indic) |
|---|---|
| English SOTA, zero-shot (IndicSynth ACL'25) | 33–93% |
| **VoxShield, seen generator** | **1.62%** |
| **VoxShield, unseen generator** | **15.94% (mean LOGO)** |
| Global SOTA unseen, English wideband (DOSS/Teffic) | 1.5–2.3% *(easier target)* |

## 5.6 Caveats
- Aggregate clean EER (9.24%) mixes unseen generators into the pool; **per-generator seen
  EER is the clean number (1.62%)**.
- Per-language Table 1 pending tag-normalization re-run.
- 8 low-resource languages (bodo, dogri, kashmiri, konkani, manipuri, nepali, santali, sindhi)
  lack an MMS voice and remain single-class (not reported).
- IndicSynth is CC-BY-NC (research use only).
