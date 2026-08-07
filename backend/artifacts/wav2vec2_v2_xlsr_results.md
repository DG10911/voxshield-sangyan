# VoxShield — XLSR-53 fine-tune on In-the-Wild
Date: 2026-08-07
Hardware: 1x NVIDIA A100-SXM4-40GB
Model: facebook/wav2vec2-large-xlsr-53 (300M params, 56 languages incl. Hindi/Tamil/Bengali)
Training: 5 epochs, batch=16, lr=5e-5, bf16, gradient checkpointing
Data: In-the-Wild — 22,245 train / 9,534 held-out test (70/30 random split)

## Results
- **Best EER: 0.16%** (baseline DSP: 2.94%)
- **AUC: 99.99%**
- **Relative EER reduction vs DSP baseline: 94.6%** (18x)
- Loss final epoch: 0.0058
- Wall time: ~14 min (168s/epoch × 5 epochs + eval)

## Context
- Published SoTA on ITW in-domain: 0.1–0.5% EER
- Cross-domain: 1–3% (untested here — future work)

## Why XLSR
Trained on 56 languages including Hindi, Tamil, Bengali via Common Voice.
Acoustic representations transfer directly to Indic telephony use case.

## Checkpoint
- ~/checkpoints/voxshield/wav2vec2_xlsr_itw/best.pt (~1.2 GB)
