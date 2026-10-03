# VoxShield — Real-Time Voice-Deepfake Detection for Indic-Language Telephony Fraud

**GBT BuildStorm 2026 — Round 1 Paper Submission**
**Track:** FinTech & Financial Inclusion (also fits Smart Cities / Open Innovation)
**Team Lead:** Devansh Goenka

---

## 1. Problem Statement

India is the world's largest telephony market and its fastest-growing digital-payments economy — and that makes it the world's biggest target for **voice-based fraud**. Two forces have collided:

1. **Voice cloning became trivially easy and cheap.** Modern text-to-speech and voice-conversion systems (XTTS, VITS, F5, neural-codec models, and India-native engines) can clone a person's voice from **3–10 seconds** of reference audio, in **Indian languages**, for near-zero cost.
2. **Fraud runs over the phone.** "Digital arrest" scams, fake bank-official calls, and relative-in-distress scams increasingly use **synthetic voices** in Hindi, Tamil, Bengali and other Indian languages, delivered over ordinary phone lines.

The gap: **every commercial voice-deepfake detector (Pindrop, Reality Defender, Hiya, Resemble) is English-first, cloud-only, and built for Western markets.** Indian banks and telcos legally **cannot** send customer call audio to a foreign cloud (DPDP Act, RBI data-localization). So the exact institutions being defrauded have **no deployable defense** for Indian-language, phone-quality audio.

**The problem we solve:** detect AI-cloned / synthetic voices in Indian-language telephone calls, in real time, running fully on-premises — the one solution the market lacks.

---

## 2. Proposed Solution — VoxShield

**VoxShield is an on-premises, Indic-language, telephony-hardened voice-deepfake detector.** Given a call's audio, it returns a calibrated risk verdict (LOW / MEDIUM / HIGH) with **explainable reason codes**, fast enough to flag a fraudulent call within its first seconds.

What makes it different — and defensible:

| Dimension | Commercial incumbents | **VoxShield** |
|---|---|---|
| Indian languages | ❌ English-first | ✅ 10 Indic languages |
| Deployment | ❌ cloud-only | ✅ **on-prem / air-gapped** (DPDP-compliant) |
| Telephony codecs | partial | ✅ hardened for G.711 8 kHz phone audio |
| Explainability | mostly black-box | ✅ per-signal reason codes |
| Model access | closed | ✅ open weights, reproducible |

**Why it's hard to copy:** the moat is not a single algorithm (the research is public) — it is (a) an **on-prem federated data flywheel** that improves from each bank's real fraud traffic *without any audio leaving their premises*, and (b) a **proprietary multi-engine Indic fake corpus** no competitor has. Both compound over time.

---

## 3. Technical Approach

**Detection model.** A self-supervised speech backbone (wav2vec2-XLS-R-53, pretrained on 56 languages including Hindi/Tamil/Bengali) fine-tuned as a binary real-vs-synthetic classifier. The multilingual pretraining gives free acoustic priors for Indian languages — a key advantage over English-only detectors.

**Telephony hardening.** Training applies on-the-fly channel augmentation — G.711 μ-law 8 kHz codec, telephony band-pass (300–3400 Hz), additive noise, packet-loss — so the model works on real phone audio, not just studio recordings. No stored copies: augmentation is generated per-sample at train time.

**Honest evaluation (the part most projects skip).** We evaluate under strict disjoint splits to avoid inflated numbers:
- **Speaker-disjoint** — test speakers never seen in training
- **Generator-holdout (cross-generator)** — train on some cloners, test on a *held-out* cloner (the true real-world test)
- **Cross-dataset OOD** — test on an entirely different dataset (MLAAD)
- **Per-language Indic** and **codec-degraded** breakdowns

**Explainability.** A calibrated fusion layer outputs per-signal reason codes (spectral/high-frequency artifacts, phase regularity, prosody, breath), so a fraud analyst sees *why* a call was flagged — essential for BFSI adoption.

**System.** A FastAPI inference service (sub-second on GPU) with a bank-grade dashboard and a sliding-window streaming mode for live-call decisions.

---

## 4. Tech Stack

| Layer | Technology |
|---|---|
| Backbone | wav2vec2-XLS-R-53 (300M), PyTorch 2.6 + CUDA |
| Training | HuggingFace Transformers, bf16 mixed precision, gradient checkpointing; NVIDIA A100 (DGX) |
| Data pipeline | HuggingFace Datasets, PyArrow, soundfile, torchaudio; on-the-fly telephony augmentation |
| Datasets | In-the-Wild, IndicSynth (12-lang synthetic, ACL 2025), IndicVoices (AI4Bharat real), DFADD (diffusion fakes), CodecFake+, MLAAD (multilingual OOD) |
| Fake generation (attack diversity) | Self-hosted TTS engines — AI4Bharat IndicF5, Indic-Parler-TTS, VITS, XTTS-v2, F5-TTS |
| Serving | FastAPI + Uvicorn, on-prem; ECAPA-TDNN speaker verification; Whisper/IndicConformer ASR for scam-intent |
| Deployment | Docker (CPU or single-GPU), on-prem / air-gapped; Bhashini/MeitY-aligned |

---

## 5. Results & Traction (measured, honest)

- **Deployed fusion system:** 5.9% EER, ROC-AUC 0.983, on held-out In-the-Wild — a live, explainable, on-prem product (TRL-5).
- **Indic fairness:** genuine-speaker false-alarm rate cut from 11.7% → 6.3% (channel-aware) across 10 Indian languages.
- **Research fine-tune (wav2vec2-XLS-R):** 0.31% EER speaker-disjoint on In-the-Wild (matching published state-of-the-art), 0.99% under G.711 phone codec.
- **Currently training** a multi-cloner Indic model on a purpose-built corpus (IndicSynth + IndicVoices + DFADD + more) to produce honest **cross-generator** and **per-language** numbers — the metric that proves real-world robustness.

*(All numbers are scoped precisely; in-corpus and cross-dataset figures are reported separately, never conflated.)*

---

## 6. Impact & Feasibility

- **Who benefits:** banks, NBFCs, telecom fraud teams, and ultimately every Indian phone user targeted by voice scams.
- **Why now:** RBI-reported banking fraud is rising sharply, ~47% of Indian adults report exposure to voice-clone scams, and CERT-In has issued deepfake advisories — regulators are actively pushing for defenses.
- **Feasibility:** already runs on a single A100 (or a consumer RTX GPU) at sub-second latency, ~4.3M calls/day per GPU — telco-scale, on-prem, today.
- **Go-to-market:** enterprise contact-center deployment first (banks legally need on-prem), then carrier-network integration.

---

## 7. Roadmap

- **Now:** multi-cloner Indic training + honest cross-generator benchmark.
- **3 months:** streaming live-call demo, challenge-response liveness, adversarial-robustness report.
- **12 months:** federated pilot with one bank (the data-flywheel moat), publish the first telephony-band Indic voice-deepfake benchmark.

---

## 8. Summary

VoxShield is the **only voice-deepfake detector built for how fraud actually happens in India** — Indian languages, phone-quality audio, on-premises, explainable. It combines a state-of-the-art self-supervised model, telephony-hardened training, rigorous honest evaluation, and a defensible data-flywheel moat, targeting a market the global incumbents legally cannot serve.

**No limits. We built it.**

---

*Team Lead: Devansh Goenka · Contact: devanshgoenka03@gmail.com · Public artifacts: GitHub (DG10911/voxshield), HuggingFace (dg10911/voxshield-checkpoints)*
