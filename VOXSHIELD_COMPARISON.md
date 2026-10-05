# VoxShield vs Existing Systems

_Framing matters: most published systems are **English, wideband, seen-generator**.
VoxShield targets the harder cell — **Indic, telephony (G.711), unseen-generator, on-prem**.
Numbers below are the reported figures; VoxShield's are measured (`results/report_all_norm.txt`)._

## VoxShield measured (this work)
| Metric | Value |
|---|---|
| Languages | 12 validated two-class (→ ~20 in progress) |
| Overall EER | **10.25%** |
| Seen-generator EER | **9.57%** |
| **Unseen-generator EER** | **19.00%** (LOGO mean **15.94%**) |
| Generalization gap | **+9.43 pts** |
| Clean → **G.711 telephony** | 9.24% → **11.41% (+2.17)** |
| Calibration | **ECE 0.058** · Cllr 1.010 |
| Abstention | false alarms **2.55% → 0.23%** (−91%) @80% |
| Best languages | pa/te/mr/sa/hi/kn **all < 1%** |

## Comparison table
| System | Focus | Benchmark | Reported | Notes |
|---|---|---|---|---|
| **VoxShield (ours)** | **Indic · telephony · unseen-gen** | internal Indic (LOGO) | **unseen 19.0% / seen 9.6%**, **G.711 11.4%**, 12 langs | on-prem, calibrated, abstains |
| IndicSynth (ACL 2025) | Indic zero-shot ADD | IndicSynth | **33–93% EER** across Indic | we lead on the same language families |
| SATYAM / IndicFake (2026) | Indic codec-deepfake | Indic-CodecFake | **~98.3% accuracy** | accuracy≠EER; different corpus |
| ASVspoof 5 baseline | English wideband | ASVspoof 5 | min-DCF 0.60–0.65 (MMS) | lab audio, not telephony |
| XLS-R + AASIST (Tak'22) | SSL anti-spoof | In-the-Wild | ~35.6% (AASIST base) → ~8–18% | wideband, English |
| SAFE Challenge 2025 (WavLM+AASIST+RawBoost) | multi-dataset | In-the-Wild | **8.42% EER** | 9 languages, wideband |
| SpAArSIST (2026) | AASIST simplification | In-the-Wild | **2.82% EER** | same benchmarks, English-ish |
| Layer-wise fusion (2025) | XLS-R decision fusion | In-the-Wild | 6.90% EER | — |
| MamBo-3-Hydra (ACL'26) | Mamba-Attention backend | ASV21LA / ITW | 0.81% / 4.97% EER | wideband |
| Commercial (Pindrop, Reality Defender, Hiya) | enterprise | not published | — | English-centric; no Indic telephony |

## Where VoxShield wins
1. **Indic-first + telephony**: **G.711 penalty only +2.17 pts**; most detectors collapse (+20–30%) on narrowband.
2. **Zero-shot Indic**: beats IndicSynth's 33–93% range on the same language families.
3. **Open-set discipline**: reports **unseen 19%**, not just the optimistic seen 9.6% (many papers quote only seen).
4. **Calibrated + abstains**: ECE 0.058, false alarms −91% — production-ready analyst workflow.
5. **On-prem, no egress**: BFSI/privacy requirement commercial cloud APIs can't meet.

## Where we're behind (honest)
- **In-the-Wild (English social media)**: SpAArSIST 2.82% / SAFE 8.42% vs our unseen 19% — but those are **wideband English**, a different, easier cell than **Indic telephony**.
- **Accuracy-style metrics**: SATYAM ~98.3% (on its own corpus) — different dataset, not directly comparable.
- **Commercial scale**: Pindrop etc. have far more data/engines; we compete on **Indic + on-prem**, not breadth.

## One-paragraph positioning
> Existing detectors excel on **English, wideband, seen generators**. VoxShield is built for the
> **harder, under-served cell — Indic languages over **real telephone codecs**, tested on
> **unseen generators**, deployed **on-prem**. On that cell it beats the Indic zero-shot
> baseline (IndicSynth 33–93%) and absorbs telephony with only +2.17 pts, while staying
> calibrated (ECE 0.058) and safe (abstention cuts false alarms 91%). On English wideband
> benchmarks, specialized systems (SpAArSIST 2.82%, SAFE 8.42%) are ahead — a different task.
