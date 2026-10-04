# VoxShield — Full System Overview
_End-state description after all GPU (DGX A100) tasks complete._

## 1 · What it is
VoxShield is a real-time **voice-fraud intelligence system** that detects AI-cloned voices in
investment scam calls across Indic languages, on narrowband telephone audio (G.711), on-prem,
returning **HUMAN / SYNTHETIC / ABSTAIN** with transcript, language and reason codes. It is a
decision-support tool — it never gives investment advice.

## 2 · What completes when the GPU queue finishes
| Task | Output | Effect on system |
|---|---|---|
| Phase 4 backends (`aasist_*`, Conformer) | trained checkpoints + `checkpoints/aasist_*/scores.csv` | 3 neural backends trained & benchmarked |
| Adversarial training (PGD) | robust Conformer | robustness to evasion |
| Distillation | compact student | deployable edge model |
| C2 ablation (`phase4/c2_*.txt`) | component-contribution tables | paper's ablation section |
| Low-res round (8 langs) | per-language scores | coverage 15/23 → **23/23** (environment-dependent) |
| Downloads | AIKosh/HF corpus on disk | reproducibility |

## 3 · Architecture — 7 layers
1. **Ingest** — call/upload/stream → 16 kHz mono, G.711/8 kHz phone path emulation.
2. **Representation** — log-mel + **LFCC** + **CQCC** (+ RawBoost augmentation).
3. **Detector ensemble (5)** — Acoustic-DSP (0.30) + 3 neural SSL (0.50 each) + trainable
   fusion-head(LFCC+CQCC).
4. **Evidence "brains" (9)** — physics(HPCS), replay, environment, cross-codec, speaker,
   semantic↔prosody, causal, temporal-DNA, arbitration.
5. **Fusion & calibre** — recall-aware blend (models 0.5 · reasons 0.3 · head 0.4) → calibrated
   score → threshold + **selective abstention**.
6. **Intelligence** — threat registry (28 generators, 26 attacks), intel graph, unknown vault.
7. **Surfaces** — API + 17-screen console + product integrations.

## 4 · Data & languages
- **23 Indian languages**; **12** validated two-class (pa, te, mr, sa, hi, ta, kn, gu, bn, ur, or, ml),
  **15/23** trained pre-GPU, **8 low-res** (bodo, dogri, kashmiri, konkani, manipuri, nepali,
  santali, sindhi) finishing in the GPU round.
- Corpus: AIKosh **124 datasets / 94 models**, IndicSUPERB/IndicSynth, HF deepfake sets,
  self-generated fakes (TTS + codec).

## 5 · Results (measured, DGX 2026-10)
| Metric | Value |
|---|---|
| Seen EER | **1.62%** (freevc24) |
| Unseen (LOGO mean) | **15.94%** (vits 19.00 · xtts_v2 27.19) |
| Generalization gap | **+9.43 pts** |
| Clean → G.711 | 9.24% → 11.41% (**+2.17 pts**) |
| False-alarm (abstention) | 2.55% → 0.23% @80% coverage (**−91%**) |
| Calibration | **ECE 0.058**, Cllr 1.01, AURC 0.0273 |
| Zero-shot SOTA (IndicSynth ACL'25) | 33–93% → we lead |
Per-language clean/G.711 EER: pa 0.00/0.05 · te 0.00/0.11 · mr 0.02/0.14 · sa 0.03/0.15 ·
hi 0.09/0.29 · ta 0.26/2.03 · kn 0.65/1.62 · gu 1.28/6.01 · bn 3.30/10.36 · ur 13.13/22.71 ·
or 32.53/35.68 · ml 37.51/37.81.

## 6 · API (real, `backend/app.py`)
`GET /api/health` · `POST /api/analyze` (+spectrogram) · `POST /api/stream-analyze` ·
`WS /api/ws-stream` · `GET /api/audit` · `GET /api/threats` · `GET /api/intel` ·
`POST /api/risk/score` · `GET /api/threat/search` · `POST /api/gateway/decide` ·
`POST /api/consumer/check` · `GET /api/deployment/profile` · `GET /api/warroom` ·
`POST /api/speaker/verify`.

## 7 · Frontend
17-screen console (Overview · Analyze · Live · History · Languages · Brains · Registries ·
Results · Threat intel · Speaker · Product surfaces · Integrations · Data · Training rounds ·
Ops · Deployment · Roadmap) — self-contained, dark premium design, live API + offline mock.

## 8 · Product surfaces
CallGuard (risk score) · Voice Identity · Transaction Shield · Telephony Gateway ·
War Room (read-only) · Consumer one-tap check.

## 9 · Deployment
Profiles: Cloud · Enterprise on-prem · **Indic on-prem** · Edge. Privacy-by-design, data
residency, no external egress, append-only audit.

## 10 · Compliance / guardrails
No tips/price prediction/broker promotion · explicit ABSTAIN · read-only War Room ·
third-party attribution (Bhashini/AIKosh/HF) · IndicSynth CC-BY-NC (research).

## 11 · Repo & assets
`github.com/DG10911/voxshield-sangyan` (public): backend, training, DGX orchestration,
eval/reporting, 17-screen UI, deck, films, docs (spec, prompt, prior art, paper draft, results).

## 12 · Roadmap
P0 ensemble+calibre ✅ · P1 Indic + G.711 ✅ · P2 generalization (XLS-R+RawBoost) ✅ ·
P3 selective abstention ✅ · P4 AASIST/Conformer/distill/adversarial (GPU) ⏳ ·
P5 open-set low-res, streaming, edge quantisation.
