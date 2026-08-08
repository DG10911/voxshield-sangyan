# VoxShield XLSR — Speaker-disjoint honesty test
Date: 2026-08-08
Model: facebook/wav2vec2-large-xlsr-53 fine-tuned on In-the-Wild

## Split methodology
ITW meta.csv has a speaker column. 20% of speakers (10 of 54) were held out
entirely — every clip from those speakers is only in test, never in train.
This rules out speaker-identity memorization.

## Results
- Speaker-disjoint EER: 0.31%
- AUC: 99.99%
- Degradation vs random-split (0.16%): +0.15 pts
- Test set: 2921 clips (1394 real / 1527 fake) from 10 unseen speakers
- Eval time: 6s on 1x A100

## Interpretation
The model generalizes acoustically, not by memorizing voices.

## Repro
    python eval_speakerdisjoint.py
