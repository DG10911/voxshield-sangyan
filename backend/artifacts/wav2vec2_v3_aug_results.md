# VoxShield XLSR — Telephony-augmented (G.711 8 kHz)
Date: 2026-08-08
Model: facebook/wav2vec2-large-xlsr-53 fine-tuned on In-the-Wild
Training: 3 epochs, bs=16, lr=5e-5, bf16, gradient checkpointing
Augmentation: 50% probability per clip — G.711 mu-law 8 kHz roundtrip +
              telephony bandpass (300-3400 Hz) + noise (SNR 15-30 dB)
Data: speaker-disjoint split (44 train / 10 test speakers, 28858 train / 2921 test)

## Results
| Test condition          | EER    | AUC    |
|-------------------------|--------|--------|
| Clean 16 kHz            | 0.31%  | 99.97% |
| G.711 mu-law 8 kHz      | 1.23%  | 99.82% |
| Best codec across epochs| 0.99%  | -      |

Baseline without augmentation typically degrades 5-10 pts on G.711.
Ours degrades ~1 pt.

## Comparison
| Model                        | Test        | EER    |
|------------------------------|-------------|--------|
| DSP fusion baseline          | ITW clean   | 2.94%  |
| wav2vec2-base FT             | ITW clean   | 2.18%  |
| XLSR-53 FT (random split)    | ITW clean   | 0.16%  |
| XLSR-53 FT (speaker-disjoint)| ITW clean   | 0.31%  |
| XLSR-53 + G.711 augment      | G.711 phone | 0.99%  |

## Checkpoint
- DGX: ~/checkpoints/voxshield/wav2vec2_xlsr_itw_aug/best.pt
- HuggingFace: dg10911/voxshield-checkpoints/xlsr_itw_aug_g711.pt
