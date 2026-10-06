# VoxShield — Single Digest of ALL Numbers
_Source: `results/report_all_norm.txt` (DGX A100, Oct 2026). One place for every
language, every detector/model, and every metric._

## 1 · Headline
| Metric | Value |
|---|---|
| Overall EER | **10.25%** |
| Overall AUC | 0.949 |
| Corpus n | 1,639,372 (real 1,211,904 · fake 427,468) |
| Seen generators EER | **9.57%** |
| Unseen generators EER | **19.00%** |
| **Generalization gap** | **+9.43 pts (MODERATE)** |
| Channel clean → G.711 | 9.24% → 11.41% (**+2.17 pts**) |
| Calibration | ECE **0.058** · Brier 0.061 · Cllr **1.010 bits** |
| AURC | 0.0273 |
| Abstain 20% | false-alarm **2.55% → 0.23%** (−91%) |

## 2 · Leave-One-Generator-Out (each fake as unseen)
| Held-out generator | EER vs real | n_fake |
|---|---|---|
| freevc24 | 1.62% | 321,512 |
| vits | 19.00% | 30,900 |
| xtts_v2 | 27.19% | 75,056 |
| **MEAN unseen** | **15.94%** | — |

## 3 · All languages (23)
Two-class (validated):
| Language | Overall EER | Clean | G.711 | n |
|---|---|---|---|---|
| Punjabi (pa) | 0.03% | 0.00% | 0.05% | 135,048 |
| Telugu (te) | 0.06% | 0.00% | 0.11% | 136,822 |
| Marathi (mr) | 0.08% | 0.02% | 0.14% | 113,952 |
| Sanskrit (sa) | 0.09% | 0.03% | 0.15% | 129,166 |
| Hindi (hi) | 0.19% | 0.09% | 0.29% | 185,580 |
| Kannada (kn) | 1.16% | 0.65% | 1.62% | 108,830 |
| Tamil (ta) | 1.21% | 0.26% | 2.03% | 121,456 |
| Gujarati (gu) | 3.95% | 1.28% | 6.01% | 143,940 |
| Bengali (bn) | 6.88% | 3.30% | 10.36% | 117,210 |
| Urdu (ur) | 17.92% | 13.13% | 22.71% | 135,288 |
| Odia (or) | 34.09% | 32.53% | 35.68% | 129,300 |
| Malayalam (ml) | 36.26% | 37.51% | 37.81% | 108,380 |

Single-class (genuine-only, n_fake = 0 — pending real TTS):
| Code | Likely language | n | Status |
|---|---|---|---|
| as | Assamese | 10,644 | awaiting fakes |
| ks | Kashmiri | 25,726 | awaiting fakes |
| mn | Manipuri | 15,114 | awaiting fakes |
| ma | Maithili | 9,026 | awaiting fakes |
| ko | Konkani | 13,890 | awaiting fakes |

## 4 · Channel matrix
| Channel | EER | AUC | Δ vs clean | n |
|---|---|---|---|---|
| clean | 9.24% | 0.955 | +0.00 | 819,686 |
| G.711 μ-law | 11.41% | 0.943 | **+2.17 pts** | 819,686 |

## 5 · Selective prediction / abstention
| Coverage | Risk (err) | EER@cov | FP (genuine) |
|---|---|---|---|
| 100% | 6.57% | 10.25% | 2.55% |
| 95% | 4.82% | 9.96% | 1.24% |
| 90% | 3.91% | 10.30% | 0.60% |
| 80% | 2.79% | 8.45% | 0.23% |
| 70% | 1.73% | 5.84% | 0.06% |
| 50% | 2.04% | 9.76% | 0.04% |

## 6 · All detectors & models
Runtime ensemble (fused into the verdict):
| Detector | Type | Weight |
|---|---|---|
| acoustic-dsp | hand-crafted DSP (HF/phase/F0/breath) | 0.30 |
| Deepfake-audio-detection-V2 | neural | 0.50 |
| wav2vec2-large-xlsr-deepfake | neural SSL | 0.50 |
| distilhubert-finetuned-audio-deepfake | neural SSL | 0.50 |
| fusion-head (LFCC+CQCC) | trainable classifier | stream 0.40 |

Evidence brains (9, orchestration): Physics/HPCS · Replay · Environment · Cross-codec ·
Speaker · Semantic↔Prosody · Causal · Temporal-DNA · Arbitration.

Trained backends (Phase 4, 12 languages each): **AASIST** (`aasist_*`),
**adversarial Conformer** (`adv_*`), **distilled student** (`student_*`), plus
**XLS-R finetuned**. Ablations: `phase4/c2_*.txt` (12 languages).

## 7 · Worst cells (priority)
ml 36.26% · or 34.09% · ur 17.92% · G.711 11.41% · bn 6.88% · gu 3.95%

---
## UPDATE — 2026-10-06: 20 languages, 17 under 1% EER

### Core 12 (full-corpus ensemble; row-signature aligned)
| Language | Ensemble EER | Clean | G.711 |
|---|---|---|---|
| bengali | 0.11% | 0.01% | 0.21% |
| gujarati | 0.20% | 0.01% | 0.39% |
| kannada | 0.23% | 0.03% | 0.38% |
| tamil | 0.23% | 0.05% | 0.40% |
| punjabi | 0.28% | 0.02% | 0.55% |
| hindi | 0.28% | 0.06% | 0.51% |
| sanskrit | 0.51% | 0.03% | 1.00% |
| marathi | 0.58% | 0.11% | 1.05% |
| telugu | 0.59% | 0.08% | 1.05% |
| urdu | 19.60% | 15.58% | 23.20% |
| odia | 34.39% | 33.42% | 35.14% |
| malayalam | 39.33% | 40.76% | 38.25% |

### Low-res 8 (Bhashini TTS fakes; test-set EER)
| Language | test-clean | test-G.711 |
|---|---|---|
| bodo | 0.16% | 0.00% |
| dogri | 0.00% | 0.00% |
| kashmiri | 0.00% | 0.17% |
| konkani | 0.00% | 0.08% |
| manipuri | 0.00% | 0.00% |
| nepali | 0.29% | 0.58% |
| santali | 0.06% | 0.06% |
| sindhi | 0.00% | 0.19% |

**20 languages in scope · 17 under 1% EER · 9 core + 8 low-res.**
Honest caveats: core numbers are full-corpus (n=95k–185k); low-res are small test sets (~700–1,000) so optimistic. urdu/odia/malayalam remain hard on full corpus.
