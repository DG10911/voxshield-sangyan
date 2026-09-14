# VoxShield — Master Technical Dossier

**Single source of truth for the current state of the VoxShield project.**

Prepared as an evidence-based technical audit. Every number carries a source label:

| Label | Meaning |
|---|---|
| `[VERIFIED]` | Read directly from a training log, source file, or artifact during this audit |
| `[TEAM-VERIFIED]` | From `handbook/VOXSHIELD_FACTS.md` (team's own cited fact sheet); underlying results JSON was **not present** in the audited worktree |
| `[CALCULATED]` | Computed during this audit from manifest/metadata files |
| `[EXTERNAL]` | From third-party sources, cited (or via `VOXSHIELD_LANDSCAPE_2026.md`) |
| `[ESTIMATED]` | An estimate — explicitly flagged, never presented as fact |
| `[PROPOSED]` | A future target, not achieved |
| `NOT MEASURED` | No evidence exists |

**Audit date:** 2026-09-14
**Team:** DigiSeva (SRM IST), Problem Statement PS2
**Repository branch audited:** `analyze-voxshield-backend`
**Worktree HEAD:** `4849a03f` (snapshot before DGX migration); `origin` is 10 commits ahead (DGX work: through `d95d0b87`)

---

## ⚠️ THE SINGLE MOST IMPORTANT THING TO UNDERSTAND FIRST

VoxShield is **two different systems** that produce **non-comparable numbers**. Conflating them is the #1 risk in any pitch.

| | **System A — Deployed Fusion Pipeline** | **System B — DGX XLSR Fine-tune** |
|---|---|---|
| What it is | 5-detector ensemble + calibration + reason codes + speaker verification + scam-intent, **live in production** | A single wav2vec2-XLSR-53 model fine-tuned end-to-end as a binary classifier |
| Where it lives | Vultr VPS `https://64.177.121.208.sslip.io` `[TEAM-VERIFIED]` | HuggingFace `dg10911/voxshield-checkpoints`; not deployed `[VERIFIED]` |
| Headline EER | **5.9%** `[TEAM-VERIFIED]` | **0.16% / 0.31% / 0.99%** `[VERIFIED]` |
| **What the EER measures** | **CROSS-DATASET** — trained on mixed data, tested on held-out In-the-Wild it never saw | **WITHIN-ITW** — trained on ITW train split, tested on ITW test split (0.31% is speaker-disjoint, still same corpus) |
| Honesty | Harder task, real-world generalization | Easier task, in-domain; **not** cross-dataset |

**You cannot say "VoxShield improved from 5.9% to 0.31%."** They are different exams. System B's 0.31% is an in-corpus number; System A's 5.9% is a cross-corpus number. Section 10 and Section 27 elaborate. This distinction protects you from a reviewer dismantling your pitch.

---

## Table of Contents

1. Executive Project Snapshot
2. What Exactly Is VoxShield?
3. Complete System Architecture
4. All ML Models
5. Dataset Forensics
6. Current Attack Coverage
7. Indic Language Coverage
8. All Experimental Results (chronological)
9. Current Benchmark Numbers
10. Statistical Validity
11. Hardware / GPU Audit
12. Post-GPU Measurement Plan
13. Real-Time / Streaming Status
14. API + Dashboard + Product Status
15. Security / Fraud Product Features
16. Competitor Comparison
17. VoxShield Differentiation
18. Research & India Regulatory Context
19. Current Project Status Matrix
20. Everything Left To Do (backlog)
21. After-GPU Roadmap
22. 30 / 60 / 90 Day Roadmap
23. Investor / Judge Numbers
24. One-Slide Product Metrics
25. Technical Claim Audit
26. Reproducibility Audit
27. Final Scorecard
28. The Complete Truth

---

## 1. Executive Project Snapshot

| Metric | Current Value | Status | Source |
|---|---|---|---|
| Project purpose | Real-time AI-voice-clone / audio-spoof detection for Indic-language telephony fraud | Active | `[VERIFIED]` README |
| Target users | Banks, NBFCs, call-centres, telecom, government fraud teams | — | `[VERIFIED]` README |
| Target threat | Synthetic/cloned voice used in phone fraud (UPI, digital-arrest scams) | — | `[VERIFIED]` FACTS |
| **System A architecture** | 5-detector fusion + Platt calibration + channel-aware thresholds + SHAP reason codes | Live (TRL-5) | `[TEAM-VERIFIED]` |
| **System B architecture** | Single wav2vec2-XLSR-53, end-to-end binary classifier | Trained, not deployed | `[VERIFIED]` |
| Number of detectors (System A) | 5 (acoustic-DSP, Deepfake-V2, XLS-R, DistilHuBERT, LFCC+CQCC head) | Live | `[TEAM-VERIFIED]` FACTS |
| Datasets used | In-the-Wild, WaveFake, IndicVoices, garystafford, ElevenLabs, MMS-TTS Indic fakes | — | `[CALCULATED]` manifests |
| Total merged corpus (System A `combined.csv`) | 19,866 clips, 9,933 real / 9,933 fake (balanced) | Built | `[CALCULATED]` |
| In-the-Wild manifest | 31,779 clips | Built | `[CALCULATED]` |
| IndicVoices real (DGX) | 4,000 clips, 10 languages (400 each) | Downloaded | `[VERIFIED]` logs |
| Indic MMS-TTS fakes (DGX) | **0 generated** — script committed, blocked by DGX reboot | Blocked | `[VERIFIED]` |
| Total audio hours | NOT MEASURED (manifests list files, not durations) | — | — |
| Languages (System A Indic model) | 10 (Hi, Ta, Te, Bn, Mr, Gu, Kn, Ml, Pa, As) | Trained | `[TEAM-VERIFIED]` |
| Attack families in training | Real-world (ITW mix), WaveFake vocoders, ElevenLabs, MMS-TTS (VITS) | — | `[CALCULATED]` |
| Cloners explicitly represented | MMS-TTS, WaveFake vocoders, ElevenLabs; ITW = unspecified mix | — | `[CALCULATED]` |
| Codecs simulated | G.711 8 kHz μ-law, Opus, MP3 (System A aug); G.711 (System B aug) | — | `[VERIFIED]` |
| Sampling rate | 16 kHz mono (8 kHz = detected channel flag) | — | `[VERIFIED]` FACTS |
| Model params (System B XLSR) | 300M total, ~90-94M trainable head+encoder | — | `[VERIFIED]` log (`trainable=90.4M` base / XLSR-large) |
| **System B EER — random split ITW** | **0.16%**, AUC 99.99% | Verified | `[VERIFIED]` `xlsr_20260807_2235.log` |
| **System B EER — speaker-disjoint ITW** | **0.31%**, AUC 99.99% | Verified | `[VERIFIED]` `eval_speakerdisjoint_...log` |
| **System B EER — G.711 codec** | **0.99%** best / 1.23% final epoch, AUC 99.82% | Verified | `[VERIFIED]` `xlsr_aug_...log` |
| **System A meta-fusion EER** | **5.9%** (cross-dataset, held-out ITW) | Verified | `[TEAM-VERIFIED]` meta_eval.json |
| System A ROC-AUC | 0.983 | — | `[TEAM-VERIFIED]` |
| System A accuracy@0.70 | 93.4% | — | `[TEAM-VERIFIED]` |
| System A precision / recall / F1 | 93.5% / 92.9% / 0.93 | — | `[TEAM-VERIFIED]` |
| System A confusion @0.70 (n=320) | TP 144, TN 155, FP 10, FN 11 | — | `[TEAM-VERIFIED]` |
| System A min t-DCF | 0.252 | — | `[TEAM-VERIFIED]` |
| System A calibration ECE / Brier | 0.044 / 0.048 | — | `[TEAM-VERIFIED]` |
| Indic genuine clean FP (System A) | 11.7% → 6.3% (channel-aware) | — | `[TEAM-VERIFIED]` |
| Indic fake recall (System A) | 42% → 82% (language-ID routing) | — | `[TEAM-VERIFIED]` |
| Inference latency (System A, VPS CPU) | detection 1.7–2.1 s; speaker-verify 1.5 s | Measured | `[TEAM-VERIFIED]` |
| Inference latency (System B, A100) | ~19 ms warm | Measured | `[VERIFIED]` (this session) |
| Inference latency (System B, Mac MPS) | ~120 ms warm, 885–2337 ms cold | Measured | `[VERIFIED]` (this session, `say_fake.wav` → HIGH 93.3%) |
| Streaming time-to-flag (System A) | 3.0 s (within 10 s target) | — | `[TEAM-VERIFIED]` |
| API status | System A: ~30 FastAPI endpoints, live | Live | `[TEAM-VERIFIED]` |
| Dashboard status | Bank-grade dashboard (`frontend/index.html`), served locally + VPS | Live | `[VERIFIED]` (ran locally this session) |
| Deployment status | System A live on Vultr VPS + Docker; System B not deployed | — | `[TEAM-VERIFIED]` |
| Noisy-audio / cross-generator / streaming EER for System B | NOT MEASURED | — | — |
| VRAM (training, System B) | ~4.4 GB (base), ~25–30 GB (XLSR+aug) | Measured | `[VERIFIED]` (this session nvidia-smi) |

---

## 2. What Exactly Is VoxShield?

**Problem.** Voice-cloning tools now clone a target from 3–10 seconds of reference audio. Fraudsters use cloned voices in phone scams (fake bank officials, "digital arrest", relatives-in-distress). India is a prime target: telephony-scale, many languages, high UPI adoption.

**Threat model.** An attacker synthesizes speech in the victim's language (often Indic) and delivers it over a phone channel (G.711 8 kHz μ-law, or Opus/AMR over VoLTE). The audio is band-limited and codec-degraded, which destroys many of the high-frequency artifacts a naive detector relies on.

**Detection objective.** Given a call's audio, return a calibrated risk verdict (LOW / MEDIUM / HIGH) with explainable reason codes, ideally within the first ~10 seconds of the call, running on-premises (banks cannot send call audio to foreign clouds).

**Why conventional voice authentication fails.** Speaker-verification (biometrics) answers "is this the enrolled person's voice?" — but a good clone *matches* the enrolled voiceprint. You need a separate axis: "is this voice *synthetic*?" That is deepfake/spoof detection, and it is hard because modern vocoders leave only subtle artifacts (over-regular phase, over-smooth >6 kHz energy, missing micro-prosody: jitter/shimmer/breath).

**What makes VoxShield different (evidence-based):**
1. On-prem + open weights (banks' compliance requirement). `[VERIFIED]`
2. Indic-language coverage (10 languages in System A's Indic booster). `[TEAM-VERIFIED]`
3. Telephony codec-hardening (G.711/Opus/MP3 augmentation). `[VERIFIED]`
4. Explainable reason codes + SHAP over a logistic fusion head. `[TEAM-VERIFIED]`
5. Bundled speaker verification (ECAPA) + scam-intent ("Digital Arrest Shield"). `[TEAM-VERIFIED]`

**What VoxShield DOES today vs WILL do:**
- **Today (System A, live):** upload/stream a clip → fused verdict + reasons + spectrogram + speaker-verify + scam-intent, at ~1.7–2.1 s CPU latency on a $25/mo VPS.
- **Today (System B, trained not deployed):** a much stronger *single-model* ITW classifier (0.31% speaker-disjoint) that has **not** been integrated into the product or tested cross-dataset.
- **Later:** merge System B's stronger backbone into System A; complete Indic MMS-TTS fake generation + multi-cloner training; streaming for live calls; adversarial hardening.

---

## 3. Complete System Architecture

### System A — Deployed Fusion Pipeline (`backend/`)

```
Call audio (8/16 kHz, any codec)
  → load_audio()           resample→16 kHz mono, silence-trim (librosa top_db=30), cap first 6 s
  → feature bank           89-dim vector (features.py)
  → 5 detectors (ThreadPoolExecutor, concurrent)
        acoustic-dsp       pure DSP heuristic
        Deepfake-V2        MelodyMachine/wav2vec2-base   (HF pipeline, CPU)
        XLS-R              Gustking/wav2vec2-large-xlsr   (HF pipeline, CPU, ZERO-SHOT)
        DistilHuBERT       Om-Parab/distilhubert         (HF pipeline, CPU)
        LFCC+CQCC head     LogisticRegressionNP(89)
  → logistic meta-stacker  (standardized inputs, learned weights)
  → Platt calibration      {a: 5.893, b: -2.912}   [VERIFIED calibrator.json]
  → channel-aware threshold (wideband HIGH 0.70 / narrowband HIGH 0.85)
  → recall-floor gate      (if max(distilhubert,xlsr)≥0.90 & head≥0.5 → floor 0.70)
  → verdict + confidence + reason codes + SHAP + SHA-256 audit
  → Indic booster (env-gated)  language-ID (Whisper) → Indic-fake booster raises confident Indic fakes
```

**Fusion math** `[TEAM-VERIFIED VOXSHIELD_FACTS.md]`:
Meta-stacker is a standardized logistic regression over 5 detector scores:
`logit = b + Σ wᵢ·(xᵢ − μᵢ)/sdᵢ`, weights `acoustic-dsp −0.55, Deepfake-V2 −1.17, XLS-R +1.21, DistilHuBERT +2.22, LFCC+CQCC +2.10, bias +0.134`; then Platt `p = σ(a·logit + b)`, `{a:6.446, b:−3.151}`.
SHAP: closed-form exact for the logistic head, `φᵢ = (wᵢ/sdᵢ)(xᵢ − μᵢ)` in logit space (no `shap` dependency).

**89-dim feature vector** `[VERIFIED features.py + FACTS]`: LFCC 40 (n_lfcc=20, mean+std) + CQCC 40 (CQT 84 bins → DCT, mean+std) + 9 scalars (hf_energy_ratio, hf_regularity, spectral_flatness, phase_reg group-delay proxy, f0_jitter, shimmer, f0_voiced_ratio, silence_ratio, breath_score).

### System B — DGX XLSR Fine-tune

```
16 kHz wav → prep (mono, resample, pad/truncate to 3.0 s = 48,000 samples)
  → facebook/wav2vec2-large-xlsr-53 (feature encoder frozen, gradient checkpointing)
  → Wav2Vec2ForSequenceClassification head (2 classes)
  → softmax → fake probability
```
Training: bf16 autocast, AdamW, cosine LR, `WeightedRandomSampler` for class balance.
For the augmented variant (`train_wav2vec2_aug.py`): 50% of clips pass through `telephony_aug.py` (G.711 μ-law 8 kHz roundtrip + telephony band-pass 300–3400 Hz + noise SNR 15–30 dB). `[VERIFIED]`

**The `artifacts/` fusion head in this worktree** `[VERIFIED]`: `fusion_head.json` has keys `w[89], b=0.0786, mu[89], sd[89]`; `calibrator.json` `{a:5.893, b:-2.912}`. This is System A's trained head (89-dim), **not** System B.

---

## 4. All ML Models

| Model | Role | System | Arch | Params | Pretrained source | Fine-tuned? | Device | Status |
|---|---|---|---|---|---|---|---|---|
| acoustic-dsp | detector | A | DSP heuristic | 0 | — | n/a | CPU | Live `[TV]` |
| Deepfake-V2 | detector | A | wav2vec2-base | ~95M | MelodyMachine/Deepfake-audio-detection-V2 | zero-shot | CPU | Live `[TV]` |
| XLS-R (Gustking) | detector | A | wav2vec2-large-xlsr | ~300M | Gustking/...xlsr-deepfake | zero-shot | CPU | Live `[TV]` |
| DistilHuBERT | detector | A | DistilHuBERT | ~24M | Om-Parab/distilhubert-...itw | zero-shot | CPU | Live `[TV]` |
| LFCC+CQCC head | detector | A | LogisticRegressionNP(89) | 89 w | trained on merged corpus | yes | CPU | Live `[TV]` |
| ECAPA-TDNN | speaker verify | A | ECAPA | ~22M | speechbrain/spkrec-ecapa-voxceleb | no | CPU | Live `[TV]` |
| Whisper base/small | ASR + lang-ID | A | Whisper | 74M/244M | openai/faster-whisper | no | CPU | Live `[TV]` |
| Silero VAD | voice-activity gate | A | Silero | tiny | snakers4/silero-vad | no | CPU | Live `[TV]` |
| **Indic XLS-R booster** | Indic detector | A | wav2vec2-xls-r-300m | 300M | facebook/wav2vec2-xls-r-300m | **yes** (4k IndicVoices + 4k MMS-TTS) | GPU→CPU | Live, env-gated `[TV]` |
| **XLSR-ITW (V2)** | classifier | B | wav2vec2-large-xlsr-53 | 300M | facebook/wav2vec2-large-xlsr-53 | **yes** (ITW) | A100 | Trained, HF `[V]` |
| **XLSR-ITW-aug (V3)** | classifier | B | wav2vec2-large-xlsr-53 | 300M | same | **yes** (ITW + G.711 aug) | A100 | Trained, HF `[V]` |
| wav2vec2-base (V1) | classifier | B | wav2vec2-base | ~90M | facebook/wav2vec2-base | **yes** (ITW) | A100 | Trained, local `[V]` |

**System B training hyperparameters `[VERIFIED from logs]`:**
- V1 (base): 3 epochs, batch 32, lr 1e-4, cosine, bf16, 696 steps/epoch, ~55 s/epoch, trainable 90.4M.
- V2 (XLSR): 5 epochs, batch 16, lr 5e-5, cosine, bf16, 1391 steps/epoch, ~168 s/epoch.
- V3 (XLSR+aug): 3 epochs, batch 16, lr 5e-5, cosine, bf16, 1804 steps/epoch, ~205 s/epoch, speaker-disjoint train (28,858) / test (2,921).

---

## 5. Dataset Forensics

### 5.1 Inventory (System A merged corpus + DGX)

| Dataset | Source | Lang | Real/Fake | Generator | Files | Hours | SR | In train? | Status |
|---|---|---|---|---|---|---|---|---|---|
| In-the-Wild | HF mueller91/In-The-Wild | English | both | mixed/unspecified | 31,779 | NOT MEASURED | 16 kHz | yes (both systems) | `[V]` |
| WaveFake | Zenodo 4904579 | English | fake | vocoders (LJSpeech base) | 13,100 | NM | — | yes (A) | `[C]` |
| IndicVoices | AI4Bharat | 10 Indic | real | n/a (genuine) | 4,000 | NM | yes (A Indic) | `[V]` |
| garystafford | — | English | both | — | 1,866 | NM | yes (A) | `[C]` |
| ElevenLabs | — | English | fake | ElevenLabs | 1,388 | NM | yes (A) | `[C]` |
| MMS-TTS Indic fakes | facebook/mms-tts | 10 Indic | fake | MMS-TTS (VITS) | 4,000 (A) / **0 (B, blocked)** | NM | A yes / B no | `[V]` |

### 5.2 System A `combined.csv` (the merged super-dataset) `[CALCULATED]`

- **19,866 clips**, perfectly class-balanced: **9,933 real / 9,933 fake**
- Dataset mix: In-the-Wild 8,582 · WaveFake 3,000 · IndicVoices 3,000 · garystafford 2,684 · ElevenLabs 2,600

### 5.3 System B (DGX) splits `[VERIFIED from logs]`

- Random split: train 22,245 / test 9,534 (In-the-Wild only)
- Speaker-disjoint split: 44 train speakers / 10 test speakers; train 28,858 / test 2,921 (1,394 real / 1,527 fake)

### 5.4 Leakage analysis

| Leakage type | Finding | Source |
|---|---|---|
| **Speaker leakage** | System B's **random split (0.16%) has probable speaker leakage** — ITW clips split by file, so the same speaker appears in train+test. The team correctly re-ran a **speaker-disjoint** split → 0.31% (only +0.15 pts), which **rules out** heavy speaker memorization. Excellent practice. | `[VERIFIED]` |
| **Generator leakage** | **HIGH RISK, present.** System B trains and tests only on In-the-Wild → same generator distribution in train and test. Cross-generator EER is **NOT MEASURED**. This is the single biggest unmeasured risk for System B. | `[VERIFIED]` |
| **Dataset leakage** | System B: none beyond ITW (single-corpus). System A: cross-dataset by design (holds out ITW). | `[VERIFIED]` |
| **Duplicate/near-dup audio** | NOT CHECKED (no dedup audit run). | — |
| Indic real/fake speaker overlap | System A Indic: real = IndicVoices speakers, fake = MMS-TTS (synthetic, no human speaker) → no speaker overlap, but **content/generator is single-engine (MMS-TTS)** → in-distribution recall only. | `[TEAM-VERIFIED]` |

---

## 6. Current Attack Coverage

| Generator | Architecture | Zero-shot clone? | Indic? | In VoxShield **training**? | In VoxShield **test**? | Priority to add |
|---|---|---|---|---|---|---|
| MMS-TTS | VITS | no | **yes** | A: yes (Indic) | A: in-dist only | — |
| WaveFake vocoders | GAN vocoders | no | no | A: yes | A: yes | — |
| ElevenLabs | proprietary | yes | partial | A: yes (2.6k) | partial | Medium (refresh to v3) |
| In-the-Wild mix | unspecified | — | no | both | both | — |
| XTTS-v2 | GPT + diffusion decoder | **yes** | partial | **NO** | **NO** | **P0** `[EXTERNAL]` |
| F5-TTS | flow-matching DiT | **yes** | limited | **NO** | **NO** | **P0** `[EXTERNAL]` |
| Fish-Speech | codec-LM | **yes** | limited | **NO** | **NO** | **P1** `[EXTERNAL]` |
| GPT-SoVITS | codec-LM + VITS | **yes** (few-shot) | limited | **NO** | **NO** | **P1** `[EXTERNAL]` |
| MaskGCT | masked-codec-LM | **yes** | limited | **NO** | **NO** | **P1** `[EXTERNAL]` |
| VALL-E family | neural-codec-LM | **yes** | limited | **NO** | **NO** | **P1** `[EXTERNAL]` |
| Cartesia Sonic | SSM | **yes** | no (yet) | **NO** | **NO** | **P2** `[EXTERNAL]` |
| Sarvam Bulbul v2/v3 | proprietary (Indic-native) | yes | **yes (native)** | **NO** | **NO** | **P0** (Indic-critical) `[EXTERNAL]` |

**Bottom line:** VoxShield's Indic fake exposure is **MMS-TTS only** (a single VITS engine). The 2024–26 Indic threat wave (Bulbul, XTTS, F5, Fish, GPT-SoVITS) is entirely unrepresented. Section 20 P0 addresses this. `[EXTERNAL: VOXSHIELD_LANDSCAPE_2026.md]`

---

## 7. Indic Language Coverage

**System A Indic booster — per-language genuine clean FP (deployed)** `[TEAM-VERIFIED]`:

| Language | Genuine clean FP | Strength |
|---|---|---|
| Marathi | 0.0% | Strong |
| Tamil | 3.3% | Strong |
| Punjabi | 3.3% | Strong |
| Bengali | 3.3% | Strong |
| Kannada | 6.7% | OK |
| Gujarati | 6.7% | OK |
| Assamese | 6.7% | OK |
| Hindi | 10.0% | Weak |
| Malayalam | 10.0% | Weak |
| Telugu | 13.3% | **Weakest** |

- Aggregate Indic genuine FP: **11.7% → 6.3%** channel-aware `[TEAM-VERIFIED]`
- Indic fake recall: **42% → 82%** with language-ID routing `[TEAM-VERIFIED]`
- System A Indic model: **0% FP on real Indian speakers, 100% recall on the trained MMS-TTS engine** — but explicitly **in-distribution only** `[TEAM-VERIFIED]`
- Per-language **EER / FAR / FRR / F1 / AUC**: **NOT MEASURED** (only FP and aggregate recall are recorded)
- System B has **no Indic evaluation** (Indic fakes were never generated on the DGX)

**Proposed future languages / metrics:** full per-language EER + confidence intervals after the multi-cloner Indic corpus is built (Section 12).

---

## 8. All Experimental Results (chronological)

| Exp | Date | Goal | System | Data | Result | Best ckpt | Status | Source |
|---|---|---|---|---|---|---|---|---|
| A-fusion | ~Jul 2026 | 5-detector meta-fusion | A | merged, held-out ITW (n_test 320) | **EER 5.9%**, AUC 0.983, F1 0.93 | fusion_head.json | ✅ live | `[TV]` |
| A-perDet | ~Jul | single-detector EERs | A | 800-clip corpus | XLS-R 16.0% (best single), DistilHuBERT 24.9%, LFCC+CQCC 26.6%, DSP 47.4%, DeepfakeV2 62.0%, avg-fusion 19.1% | — | ✅ | `[TV]` |
| A-indic | ~Jul | Indic booster (RTX 5090) | A | 4k IndicVoices + 4k MMS-TTS, 10 lang, 3 ep, bs 8, lr 1e-5 | 0% FP real / 100% recall MMS-TTS (in-dist); routed 42→82% | dg10911/voxshield-indic-xlsr | ✅ live | `[TV]` |
| A-robust | ~Jul | codec/noise robustness self-test | A | n=80/cond | clean 7.5%; Opus 2.5% (improves); G.711 15.0%; MP3 20.0%; tempo0.9× 32.5%; noise@15dB 45.0%; pitch+2st 56.3% | — | ✅ | `[TV]` |
| B-smoke | 2026-08-07 | DSP fusion smoke on DGX | B(fusion) | ITW 22,245 tr / 200 te | in-domain 0.00%, **OOD ITW 2.94%**, min t-DCF 0.082 | artifacts | ✅ | `[V]` smoke log |
| **B-V1** | 2026-08-07 | wav2vec2-base fine-tune | B | ITW random 22,245/9,534 | **best EER 2.18%** (ep0), AUC 98.0%; ep1 collapsed 14.47%; ep2 3.86% | wav2vec2_itw/best.pt | ✅ | `[V]` wav2vec2 log |
| **B-V2** | 2026-08-07 | XLSR-53 fine-tune | B | ITW random | **best EER 0.16%** (ep4), AUC 99.99%, loss 0.0058 | wav2vec2_xlsr_itw/best.pt | ✅ | `[V]` xlsr log |
| **B-V2-sd** | 2026-08-08 | speaker-disjoint eval | B | ITW 10 unseen speakers (n=2,921) | **EER 0.31%**, AUC 99.99% (+0.15 vs random) | (same ckpt) | ✅ | `[V]` eval log |
| **B-V3** | 2026-08-08 | XLSR + G.711 aug | B | speaker-disjoint 28,858/2,921 | clean **0.31%** AUC 99.97%; **G.711 0.99%** best / 1.23% final AUC 99.82% | wav2vec2_xlsr_itw_aug/best.pt | ✅ | `[V]` xlsr_aug log |
| B-indic-fakes | 2026-08-10 | generate MMS-TTS Indic fakes | B | FLORES + MMS-TTS, 10 lang | **NOT RUN** — DGX driver mismatch → reboot pending | — | 🔴 blocked | `[V]` |

**Interpretation of the key experiments:**
- **B-V1 epoch collapse:** epoch 0 gave 2.18%, epoch 1 jumped to 14.47% then recovered to 3.86%. This is classic small-model over-fitting / LR-too-high oscillation on a tiny head. The "best" (epoch 0) was kept. Not a robust result — a 1-epoch best is fragile.
- **B-V2 (XLSR 0.16%):** loss drove to 0.0058, EER 0.16% — but this is **in-corpus ITW**. The near-zero loss is a warning sign of in-distribution saturation, not proof of real-world skill.
- **B-V2-sd (0.31%):** the honest one. Speaker-disjoint proves the model didn't just memorize voices. Still ITW-only (generator leakage remains).
- **B-V3 (G.711 0.99%):** codec-hardening worked — degradation from 0.31% clean to ~1% under G.711 is small and expected; on-par with the augmentation goal.

---

## 9. Current Benchmark Numbers (master table)

### System B (DGX XLSR) — WITHIN-ITW `[VERIFIED]`

| Condition | EER | AUC | n (test) | Source |
|---|---|---|---|---|
| Clean, random split | 0.16% | 99.99% | 9,534 | xlsr log |
| Clean, speaker-disjoint | 0.31% | 99.99% | 2,921 | eval log |
| Clean (V3 aug model) | 0.31% | 99.97% | 2,921 | xlsr_aug log |
| G.711 μ-law 8 kHz (V3) | 0.99% best / 1.23% final | 99.82% | 2,921 | xlsr_aug log |
| wav2vec2-base (V1) | 2.18% | 98.00% | 9,534 | wav2vec2 log |
| Opus / AMR-WB / MP3 / noise / reverb / cross-generator / per-language | **NOT MEASURED** | — | — | — |

### System A (Deployed Fusion) — CROSS-DATASET `[TEAM-VERIFIED]`

| Metric | Value |
|---|---|
| Meta-fusion EER (held-out ITW) | 5.9% |
| ROC-AUC | 0.983 |
| Accuracy@0.70 / Precision / Recall / F1 | 93.4% / 93.5% / 92.9% / 0.93 |
| min t-DCF | 0.252 |
| Confusion @0.70 (n=320) | TP 144, TN 155, FP 10, FN 11 |
| Robustness: clean / Opus12k / G.711 / MP3 / tempo0.9× / noise@15dB / pitch+2st | 7.5% / 2.5% / 15.0% / 20.0% / 32.5% / 45.0% / 56.3% |

**Verification of the "0.31% / 0.99%" headline:** confirmed against `eval_speakerdisjoint_20260808_0928.log` (0.31%) and `xlsr_aug_20260808_1017.log` ("best codec EER=0.99%"). These are **System B, In-the-Wild only, speaker-disjoint**. They are **not** the deployed product's numbers and **not** cross-dataset.

---

## 10. Statistical Validity

| Result | Sample | Speakers | CI computed? | Threshold method | Verdict |
|---|---|---|---|---|---|
| System B random 0.16% | 9,534 clips | overlapping (leak) | no | EER operating point | **PRELIMINARY** (speaker leak) |
| System B speaker-disjoint 0.31% | 2,921 clips | 10 unseen | no | EER | **MODERATELY SUPPORTED** (single corpus, no CI) |
| System B G.711 0.99% | 2,921 clips | 10 unseen | no | EER | **MODERATELY SUPPORTED** |
| System A 5.9% | 320 test | held-out ITW | no | fixed 0.70 | **MODERATELY SUPPORTED** (small n=320) |
| System A Indic 100% recall | in-dist MMS-TTS | synthetic | no | 0.85 | **PRELIMINARY** (in-distribution only) |
| System A per-language FP | 30/lang (`n=80/cond` robustness) | few | no | — | **PRELIMINARY** (tiny n per language) |

**No result has bootstrap confidence intervals.** Sample sizes for Indic per-language (~30) and System A test (320) are small. **Action:** compute 95% bootstrap CIs on every headline EER before any publication or investor claim (Section 12).

---

## 11. Hardware / GPU Audit

### Completed WITHOUT GPU (CPU/Mac)
- System A full pipeline (runs CPU on VPS). `[TEAM-VERIFIED]`
- System B **inference** on Mac MPS (~120 ms warm — demonstrated this session). `[VERIFIED]`
- All manifest building, dataset arrangement, fusion-head fit (numpy). `[VERIFIED]`

### Currently REQUIRES GPU
- System B training (XLSR fine-tune): needs ~4.4 GB (base) to ~25–30 GB (XLSR+aug) VRAM. Ran on 1× A100-40 GB. `[VERIFIED]`
- MMS-TTS Indic fake generation (10 languages): GPU strongly preferred (~25–30 min on A100). `[VERIFIED estimate from prior session]`

### Optional GPU acceleration
- System A neural detectors (currently CPU) could move to GPU for lower latency.

### Training-job hardware ledger `[VERIFIED]`
| Job | GPU | VRAM | Time | Batch | Precision |
|---|---|---|---|---|---|
| B-V1 base | A100-40GB | ~4.4 GB | ~3 min (3 ep) | 32 | bf16 |
| B-V2 XLSR | A100-40GB | ~25 GB | ~14 min (5 ep) | 16 | bf16 |
| B-V3 XLSR+aug | A100-40GB | ~25–30 GB | ~10 min (3 ep) | 16 | bf16 |
| **Total A100 compute burned** | | | **~35 min** | | |

Cost equivalent `[ESTIMATED]`: ~$0.75 (Vast.ai spot) to ~$12 (AWS on-demand).

### WHAT REMAINS AFTER GPU TRAINING → see Section 12.

---

## 12. Post-GPU Measurement Plan — "NUMBERS TO COLLECT AFTER GPU TRAINING"

1. Indic MMS-TTS fake generation (finish B-indic-fakes) → 4,000 fakes
2. Combined ITW+Indic manifest, speaker-disjoint
3. Continue-train XLSR on English+Indic → new checkpoint
4. **Per-language EER** (Hi/Ta/Bn/Te/Mr/Kn/Ml/Gu/Pa/As), clean + G.711
5. **Cross-generator EER** (train MMS-TTS, test XTTS/F5/Fish/GPT-SoVITS) ← the critical generalization number
6. Per-generator EER
7. Codec robustness matrix: clean / G.711 / G.729 / AMR-WB / Opus / MP3
8. Noise robustness (SNR 5/10/15/20 dB) + reverberation
9. Short-duration performance (1 s / 2 s / 3 s clips)
10. FAR @ operational thresholds; FRR @ operational thresholds
11. ROC-AUC + PR-AUC
12. Calibration (ECE, Brier, reliability diagram)
13. **95% bootstrap confidence intervals** on every headline EER
14. Inference latency (A100 / 4090 / CPU) — cold & warm
15. Streaming latency + time-to-flag distribution
16. Memory (RAM/VRAM) footprint
17. Throughput (req/s/GPU)
18. Model size on disk
19. Cold-start latency
20. Sustained-inference stability
21. FP rate on realistic Indian phone calls (real recordings)
22. FN rate on realistic cloned calls
23. Attack generalization (unseen cloners)
24. Speaker-verification EER (ECAPA) on Indian speakers
25. Fusion-of-System-A+B ablation (does XLSR fine-tune beat the zero-shot XLS-R detector inside the ensemble?)

---

## 13. Real-Time / Streaming Status

| Capability | System A | System B |
|---|---|---|
| Chunked audio | ✅ `stream_analyze` win 3.0 s / hop 1.0 s `[TV]` | ❌ batch only `[V]` |
| WebSocket | ⚠️ only WebRTC **signaling** relay (audio is P2P) `[TV]` | ❌ |
| Live microphone | ⚠️ via `/api/live-call` SSE (2.5 s window) `[TV]` | ❌ |
| Rolling windows / partial verdicts | ✅ running = mean(last 3) `[TV]` | ❌ |
| Fast-flag | ✅ single window ≥0.85 `[TV]` | ❌ |
| Detection within 10 s | ✅ time-to-flag 3.0 s `[TV]` | ❌ |

**System B needs a streaming wrapper** (sliding-window over the XLSR classifier + a WebSocket endpoint). Estimated ~1 day of CPU-only code (no GPU). This is the single biggest product gap for System B.

---

## 14. API + Dashboard + Product Status

| Feature | Completed | Partial | Planned | Missing |
|---|---|---|---|---|
| `/api/analyze` (clip) | ✅ A | | | |
| `/api/stream-analyze` | ✅ A | | | |
| `/api/live-call` SSE | ✅ A | | | |
| ECAPA enroll / verify-speaker | ✅ A | | | |
| Liveness challenge (Whisper+VAD) | ✅ A | | | |
| Digital Arrest Shield (scam-intent) | ✅ A | | | |
| Source attribution (3-class) | ✅ A | | | |
| Partial-fake localization | ✅ A | | | |
| SHA-256 audit | ✅ A (in-memory, 64-bit, not persisted) | | | |
| Bank-grade dashboard | ✅ A (ran locally this session) | | | |
| B `/predict` REST | ✅ B (`api_xlsr.py`, demonstrated 19 ms A100 / 93.3% on TTS) | | | |
| Auth / CORS / rate-limit / RBAC | | | | ❌ none (all endpoints open) `[TV]` |
| Database / persistence | | | | ❌ all in-memory `[TV]` |
| Multi-worker / horizontal scale | | | ✅ planned | ❌ single process `[TV]` |
| CI/CD, automated tests | | | ✅ planned | ❌ none `[TV]` |

---

## 15. Security / Fraud Product Features

**SHIPPED (in code, live):** 5-detector fusion + calibration + SHAP; channel-aware thresholds; liveness challenge-response; ECAPA enroll/verify; fraud-ring linkage; Digital Arrest Shield (English/Hindi/Hinglish scam-stage tracker); citizen warning (1930); source attribution; partial-fake localization; SHA-256 audit; Docker model-baking; systemd+Caddy VPS; load simulator. `[TEAM-VERIFIED]`

**IN DEVELOPMENT:** Indic multi-cloner training; System B integration; streaming for System B.

**PLANNED (deck marketing, NO code — do NOT claim):** JWT/OAuth/API-keys, rate-limiting, RBAC, CORS, AES-256-at-rest, TLS 1.3 pinning, HSM, SIEM, SOC2/ISO27001, immutable/persisted audit, any database, Redis/Kafka/queue, Kubernetes/autoscaling/load-balancer, multi-worker, CI/CD, air-gapped deployment. `[TEAM-VERIFIED — explicitly flagged as slideware]`

---

## 16. Competitor Comparison

`[EXTERNAL — VOXSHIELD_LANDSCAPE_2026.md + VOXSHIELD_FACTS.md; capabilities "Not publicly verified" where noted]`

| Capability | Pindrop | Reality Defender | Resemble Detect | Hiya | ElevenLabs | **VoxShield** |
|---|---|---|---|---|---|---|
| Deepfake detection | ✅ | ✅ | ✅ | ✅ | (cloner) | ✅ |
| Published EER | ~5% (w/ MFA "99%") | 98.5% claim | NPV | NPV | — | A: 5.9% cross-dataset / B: 0.31% in-ITW |
| Real-time / streaming | ✅ | ⚠️ | ✅ | ✅ | — | ✅ A (3 s flag) |
| Call-center / telecom | ✅ | ⚠️ | ⚠️ | ✅ | — | ✅ target |
| **Indic languages** | ❌ | ❌ | ❌ | ❌ | partial | ✅ 10 (A) |
| On-prem | ❌ cloud | ❌ cloud | ❌ cloud | ❌ carrier | ❌ | ✅ |
| Explainability | partial | ❌ | ❌ | ❌ | — | ✅ SHAP reasons |
| Speaker verification | ✅ | ❌ | watermark | ❌ | — | ✅ ECAPA |
| Public open weights | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ HF |
| Pricing | NPV | NPV | NPV | NPV | public tiers | free/OSS |

**VoxShield's honest position:** ~94% accuracy (5.9% EER cross-dataset) — behind Pindrop's marketed 99% (which includes multi-factor), but **uniquely owns Indic + on-prem + liveness + scam-intent + open weights**.

---

## 17. VoxShield Differentiation (ranked, evidence-gated)

| Rank | Differentiator | Proven? | Evidence |
|---|---|---|---|
| 1 | **Indic-language coverage** | ✅ partially (in-distribution) | 10-lang Indic booster, 0% FP real / 100% MMS-TTS recall `[TV]` |
| 2 | **On-prem + open weights** | ✅ proven | Live VPS + HF checkpoints `[TV/V]` |
| 3 | **Telephony codec robustness** | ✅ partially | System B G.711 0.99%; System A Opus improves, G.711 +7.5 pts `[V/TV]` |
| 4 | **Explainability (SHAP reasons)** | ✅ proven | closed-form SHAP over logistic head `[TV]` |
| 5 | **Bundled speaker-verify + scam-intent** | ✅ proven | ECAPA + Digital Arrest Shield live `[TV]` |
| 6 | **Low latency** | ✅ (System B 19 ms A100) | this session `[V]` |
| 7 | **Cross-generator generalization** | ❌ **UNPROVEN** | NOT MEASURED — biggest gap |
| 8 | **Research benchmark (first Indic deepfake benchmark)** | 🔵 opportunity | none exists publicly `[EXTERNAL]` |

Ranks 1–6 are **strategic strengths with at least partial evidence**. Rank 7 is a **strategic opportunity, not yet proven**. Rank 8 is a genuine publishable opening.

---

## 18. Research & India Regulatory Context

`[EXTERNAL — from VOXSHIELD_LANDSCAPE_2026.md; verify each before quoting publicly]`

- Voice-deepfake detection SOTA is dominated by SSL backbones (wav2vec2/XLS-R/WavLM) + AASIST-style graph heads; ASVspoof5 (2024) is the current benchmark.
- Codec robustness and cross-generator generalization are the field's two hardest open problems — exactly VoxShield's two biggest gaps.
- **Indic-language voice-deepfake datasets now exist (2025–2026 update):** IndicSynth (ACL 2025, 12 languages, ~4,000 hrs incl. Marathi; XTTS-v2 + VITS + FreeVC), Indic-CodecFake (ACL 2026, 12 langs, 8 neural codecs), HAV-DF (Hindi A/V, 2024), BanglaFake (Bengali, 2025). MLAAD carries thin Indic (Hindi 12.9h, Bangla 14.1h, Marathi 3h, Tamil 5h). **Do NOT claim "first Indic benchmark."** The still-open gap: cross-lingual generalization *tested on Indic* and **telephony-band (8 kHz) Indic** detection — both unpublished. `[EXTERNAL — VOXSHIELD_FRONTIER_RND.md]`
- India context (per landscape report, cited there): RBI banking-fraud figures, ~47% adult exposure to voice-clone scams, CERT-In deepfake advisory CIAD-2024-0060, DPDP Act compliance driving on-prem demand. **Treat all India numbers as `[EXTERNAL]` pending primary-source verification.**

---

## 19. Current Project Status Matrix

| Area | Status | Evidence | Remaining work | Priority |
|---|---|---|---|---|
| ML model (System A) | 🟢 COMPLETE | live fusion | maintain | — |
| ML model (System B) | 🟡 PARTIAL | trained, not integrated | merge into product | P1 |
| Training | 🟢 (both) | logs | multi-cloner retrain | P0 |
| Dataset (English) | 🟢 | manifests | — | — |
| Dataset (Indic fakes) | 🟡 | MMS-TTS only | add 5+ cloners | P0 |
| Evaluation (in-corpus) | 🟢 | logs | — | — |
| Evaluation (cross-generator) | 🔴 NOT STARTED | — | build test set | P0 |
| Indic coverage | 🟡 | in-dist only | broaden generators | P0 |
| Codec robustness | 🟡 | G.711 only (B) | Opus/AMR/G.729 | P1 |
| GPU experiments | 🟡 | blocked by reboot | resume | P0 |
| Streaming (System B) | 🔴 | — | add wrapper | P1 |
| API | 🟢 A / 🟡 B | live / /predict | merge | P2 |
| Frontend / dashboard | 🟢 | ran locally | — | — |
| Deployment | 🟢 A / 🔴 B | VPS / none | deploy B | P2 |
| Documentation | 🟡 | strong facts sheet | model card | P1 |
| Research benchmark | 🔵 FUTURE | — | publish Indic benchmark | P2 |
| Security hardening | 🔴 | no auth/DB | add before pilot | P1 |
| Productization | 🟡 | TRL-5 | pilot | P1 |

---

## 20. Everything Left To Do (backlog)

### P0 — Critical
| Task | Why | GPU? | CPU ok? | Est | Success metric |
|---|---|---|---|---|---|
| Finish MMS-TTS Indic fakes (B-indic-fakes) | unblock Indic training | yes | no | 30 min | 4,000 fakes |
| Multi-cloner Indic corpus (XTTS/F5/Fish/GPT-SoVITS/Bulbul + MMS) | fix generator leakage | yes | partial | 1–2 days | 6-cloner × 10-lang set |
| **Cross-generator EER measurement** | prove real-world generalization | yes | inference-CPU ok | 0.5 day | first honest cross-gen number |
| Merge System B backbone into System A ensemble | strongest model into product | opt | yes | 1 day | ensemble EER ↓ |

### P1 — High
| Task | Why | GPU? | Est |
|---|---|---|---|
| Streaming wrapper for System B | live-call defence | no | 1 day |
| Codec matrix (Opus/AMR-WB/G.729) | real telephony | yes(train)/CPU(eval) | 1 day |
| Bootstrap CIs on all EERs | statistical rigor | no | 0.5 day |
| Model card + reproducibility pack | shippable/publishable | no | 0.5 day |
| Security: auth + persistence (DB) | pre-pilot requirement | no | 2–3 days |

### P2 — Medium
| Task | Why | Est |
|---|---|---|
| Video-call audio integration (virtual audio device) | new surface | 2–4 days |
| Adversarial robustness (FGSM/PGD) | credibility | 0.5 day |
| Publish first Indic deepfake benchmark | research + distribution | 1 week |

### P3 — Future
Speaker-verify EER on Indian speakers; watermark-detection; multi-worker scale; SOC2 path.

---

## 21. After-GPU Roadmap

```
GPU back (driver reboot)
  → finish MMS-TTS Indic fakes
  → multi-cloner Indic corpus
  → continue-train XLSR (English+Indic)
  → FULL evaluation (per-language, per-generator, codec matrix, CIs)
  → CROSS-GENERATOR TEST  ← the make-or-break number
  → publish Indic benchmark
  → merge System B into System A ensemble
  → streaming wrapper + API
  → live demo (video-call / phone)
  → security hardening (auth + DB)
  → pilot on recorded IVR traffic (TRL-6)
  → research paper
```

---

## 22. 30 / 60 / 90 Day Roadmap

**Next 30 days** — Engineering: streaming wrapper, security (auth+DB). ML: finish Indic fakes, multi-cloner corpus, cross-generator EER. Research: bootstrap CIs. Product: merge B into A. Docs: model card. Demo: local video-call MVP.

**Next 60 days** — ML: codec matrix, adversarial hardening. Research: draft Indic benchmark paper. Product: pilot-ready packaging. Benchmark: publish Indic test set. Demo: live phone-call demo.

**Next 90 days** — Product: first pilot (bank/telco recorded traffic, TRL-6). Research: submit paper. Benchmark: leaderboard. Business: 1–3 LOIs.

---

## 23. Investor / Judge Numbers

### ✅ THE NUMBERS WE CAN SAFELY SAY TODAY
- System A (deployed): **5.9% EER, AUC 0.983, F1 0.93, 93.4% accuracy** on held-out In-the-Wild (cross-dataset). `[TEAM-VERIFIED]`
- System A Indic: **0% false positives on real Indian speakers, 100% recall on the MMS-TTS engine (in-distribution)**. `[TEAM-VERIFIED]` — always say "in-distribution".
- System B (research): **0.31% speaker-disjoint EER, 0.99% under G.711**, on In-the-Wild. `[VERIFIED]` — always say "In-the-Wild, in-corpus".
- Live latency 1.7–2.1 s CPU (System A); 19 ms A100 (System B). `[TV/V]`
- 10 Indic languages; on-prem; open weights. `[TV/V]`

### ❌ NUMBERS WE SHOULD NOT CLAIM YET
- "0.31% EER" as a headline product number (it's in-corpus, not cross-dataset — don't imply real-world).
- Any cross-generator / real-phone-call accuracy (NOT MEASURED).
- "99%", "production-ready", "SOC2", "enterprise-grade security" (slideware).
- "100% Indic recall" without the in-distribution caveat.

### 🎯 NUMBERS WE SHOULD TARGET
- Cross-generator EER < 5% on ≥5 unseen cloners.
- Per-language Indic EER < 3% clean, < 5% G.711, with 95% CIs.
- Real-Indian-phone-call EER < 5%.

---

## 24. One-Slide Product Metrics

| Metric | Current | Target | Status |
|---|---|---|---|
| Deployed EER (cross-dataset) | 5.9% | <4% | 🟢 |
| Research EER (ITW speaker-disjoint) | 0.31% | maintain | 🟢 |
| G.711 phone EER (System B) | 0.99% | <2% | 🟢 |
| Indic languages | 10 | 12 | 🟢 |
| Cross-generator EER | NOT MEASURED | <5% | 🔴 |
| Real-phone-call EER | NOT MEASURED | <5% | 🔴 |
| Latency (A100 / CPU) | 19 ms / 1.7 s | <50 ms / <1 s | 🟢/🟡 |
| Time-to-flag (streaming) | 3.0 s | <3 s | 🟢 |
| On-prem deploy | ✅ | ✅ | 🟢 |
| Speaker verification | ✅ ECAPA | + Indian EER | 🟡 |
| Explainability | ✅ SHAP | ✅ | 🟢 |
| Security (auth/DB) | ❌ | pre-pilot | 🔴 |

---

## 25. Technical Claim Audit

| Claim | Verdict | Note |
|---|---|---|
| "5.9% EER" | **SUPPORTED** | meta_eval.json, cross-dataset `[TV]` |
| "0.31% / 0.99% EER" | **SUPPORTED (scoped)** | ITW speaker-disjoint only `[V]` — must state scope |
| "real-time / within 10 seconds" | **SUPPORTED** | 3.0 s time-to-flag (System A) `[TV]` |
| "multilingual / Indic" | **PARTIALLY SUPPORTED** | 10 langs, but fakes = MMS-TTS only |
| "100% Indic recall" | **PARTIALLY SUPPORTED** | in-distribution only — caveat mandatory |
| "on-device / on-prem" | **SUPPORTED** | live VPS + open weights `[TV]` |
| "low latency" | **SUPPORTED** | 19 ms A100 / 1.7 s CPU `[V/TV]` |
| "state-of-the-art" | **NEEDS EXPERIMENT** | true in-ITW; unproven cross-generator |
| "enterprise security / SOC2 / AES-256" | **UNSUPPORTED** | slideware, no code `[TV]` |
| "production-ready" | **UNSUPPORTED** | TRL-5, no auth/DB/tests |
| "robust" | **PARTIALLY SUPPORTED** | codec yes; noise/pitch/tempo weak (45–56% EER) `[TV]` |

---

## 26. Reproducibility Audit — Score: **62 / 100**

| Dimension | Score | Note |
|---|---|---|
| Dependencies | 8/10 | `environment.yml` pinned (torch 2.5.1 cu124); System A `requirements.txt` present |
| Seeds | 7/10 | `random.seed(42)` in scripts; torch global seed not explicitly set |
| Dataset versions | 5/10 | HF repos named; exact ITW commit hash used but manifests reference local `/Volumes` paths |
| Preprocessing | 8/10 | fully in `features.py` / prep functions |
| Configuration | 6/10 | CLI args logged; no single config file |
| Checkpoints | 7/10 | on HF (2) + Mac backup; V1 base local-only |
| Commands | 7/10 | in logs + this dossier |
| Hardware | 8/10 | A100, VRAM, times all recorded |
| Eval scripts | 6/10 | `eval_speakerdisjoint.py` committed; cross-gen eval doesn't exist |
| Threshold selection | 5/10 | EER operating point clear; System A 0.70/0.85 documented but calibration JSONs not in worktree |
| **Missing for full repro** | — | results JSONs (meta_eval etc.) not in audited worktree; no fixed global seed; no automated test suite |

---

## 27. Final Scorecard (0–10)

| Dimension | Score | Justification |
|---|---|---|
| ML quality | 7 | Strong backbones, correct fine-tuning; V1 epoch-collapse shows fragility |
| Dataset quality | 6 | Balanced, multi-source; Indic fakes single-engine; no dedup audit |
| Attack coverage | 4 | MMS-TTS/WaveFake/ElevenLabs only; misses XTTS/F5/Fish/Bulbul |
| Indic coverage | 6 | 10 langs but in-distribution; per-language EER unmeasured |
| Evaluation rigor | 6 | Speaker-disjoint eval is excellent; no CIs, no cross-generator |
| Generalization | 4 | Proven within-corpus; cross-generator/cross-dataset (B) unproven |
| Codec robustness | 6 | G.711 hardening works; noise/pitch/tempo weak |
| Real-time capability | 6 | System A streaming solid; System B batch-only |
| Product readiness | 6 | Rich live product (TRL-5); no auth/DB |
| API maturity | 6 | ~30 endpoints live but open/in-memory |
| Deployment readiness | 5 | Live VPS single-process; not scalable/secured |
| Research novelty | 7 | Indic + codec framing is genuinely underexplored |
| Documentation | 8 | `VOXSHIELD_FACTS.md` is exceptional, honest, cited |
| Reproducibility | 6 | 62/100 (Section 26) |
| Commercial potential | 7 | Real India niche, on-prem moat; needs customers |
| **Overall** | **6.0** | **Strong, unusually honest prototype (TRL-5) with a real deployed product and a clear, cheap path to a defensible Indic benchmark. Main risks: attack coverage and cross-generator generalization are unproven.** |

---

## 28. The Complete Truth

**A. What VoxShield has genuinely achieved.** A live, deployed, explainable 5-detector fusion system (5.9% cross-dataset EER, AUC 0.983) with speaker verification and scam-intent detection, plus a research-grade single-model XLSR fine-tune (0.31% speaker-disjoint, 0.99% G.711 on In-the-Wild). Both are real, both are backed by logs/artifacts.

**B. What is impressive.** The honesty (the team's own `VOXSHIELD_FACTS.md` separates real from slideware); the speaker-disjoint re-evaluation (rare rigor for a student project); the codec-hardening study; the breadth of the live product; achieving all System B training in ~35 minutes of A100 time.

**C. What is weak.** Attack coverage (single Indic cloner), no cross-generator number, tiny per-language sample sizes, no confidence intervals, no security/persistence, System B not integrated or streamed.

**D. What is currently unproven.** Real-world (cross-generator, cross-dataset for B, real-phone-call) performance; Indic robustness beyond MMS-TTS; any security claim.

**E. Biggest technical risks.** (1) Generator leakage — System B may collapse on unseen cloners. (2) Indic in-distribution overfit — 100% MMS-TTS recall may not transfer. (3) Benign-transform fragility (noise/pitch/tempo 45–56% EER in System A).

**F. Biggest research opportunity.** ~~Publish the first public Indic voice-deepfake benchmark~~ **CORRECTED (2026-09-14):** IndicSynth (ACL 2025) and Indic-CodecFake (ACL 2026) already exist — do not claim "first." The genuinely open opportunity is narrower and stronger: the **first Indic *telephony-band* (8 kHz, G.711/AMR) cross-lingual benchmark + an on-prem federated continual-learning detector** — no prior work occupies that intersection. Use IndicSynth as ready-made multi-cloner training data to close the current MMS-TTS-only gap.

**G. Biggest commercial opportunity.** On-prem Indic voice-fraud detection for Indian BFSI/telco — a niche no incumbent (Pindrop/RealityDefender/Hiya) serves.

**H. Most important GPU experiment.** Multi-cloner Indic corpus + **cross-generator EER** — the number that proves or disproves real-world skill.

**I. Most important post-GPU experiment.** Cross-generator + real-Indian-phone-call evaluation with bootstrap CIs.

**J. Most important feature to build.** Streaming inference for the strong (System B) model — turns a batch classifier into a live-call defender.

**K. Most important dataset to add.** A multi-cloner Indic fake set (XTTS-v2, F5-TTS, Fish-Speech, GPT-SoVITS, Sarvam Bulbul) to kill the MMS-TTS monoculture.

**L. Most important benchmark to publish.** The Indic voice-deepfake benchmark (Section F).

**M. What must happen before calling VoxShield production-ready.** Cross-generator EER < 5% on ≥5 unseen cloners with CIs; real-phone-call FP/FN measured; auth + persistence + rate-limiting added; a pilot on real recorded traffic (TRL-6).

---

*End of dossier. All System B numbers verified against training logs in `~/voxshield_backup/logs/`; all System A numbers cited from `handbook/VOXSHIELD_FACTS.md` (team fact sheet — underlying results JSONs were not present in the audited worktree and should be re-attached for full reproducibility); external landscape numbers cited from `VOXSHIELD_LANDSCAPE_2026.md`.*
