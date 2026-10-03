# VoxShield — Paper Draft (working)
**Target:** ICASSP 2027 (paper deadline ~16–23 Sep 2026) or Interspeech 2027 (09 Feb 2027). Fallback: IEEE Access / MDPI Electronics.
**Companion docs:** `VOXSHIELD_PRIOR_ART.md` (comparison + novelty map), `VOXSHIELD_DGX_ROUNDS.md` (runs), `VOXSHIELD_ROADMAP.md`.

---

## Title
**VoxShield: Codec-Profiled Evidence Arbitration with Calibrated Abstention for Multilingual Indic Telephony Deepfake Detection**

*Alternates:* “When to Say ‘I Don’t Know’: Selective, Channel-Aware Deepfake Detection for Indic Phone Calls”; “Detecting Indic Telephony Deepfakes Behind the Codec.”

---

## Abstract (draft)
> Audio deepfake detection (ADD) has advanced rapidly on English, wideband benchmarks, yet real fraud happens on **narrowband telephony** and in **many Indic languages** — a regime where codec compression destroys the very artifacts detectors rely on, and where false alarms on genuine callers are as costly as misses. We present **VoxShield**, a detector that (i) **profiles the telephony channel** (codec, bandwidth, SNR) and gates the decision, (ii) **arbitrates heterogeneous evidence** (acoustic/physics, replay, environment, cross-codec, speaker, semantic↔prosody) and (iii) emits a **calibrated abstention** when evidence disagrees, deferring low-confidence trials. We introduce an **Indic telephony benchmark** spanning 23 languages × {clean, G.711 µ-law, G.711 A-law, G.722, replay, codec round-trip}, and report risk–coverage, false-alarm reduction on genuine callers, and unseen-generator generalization. On the benchmark, channel profiling + abstention cuts genuine-caller false alarms from X% to Y% while preserving unseen-generator EER, and the system runs in real time on CPU **on-premise** with no cloud egress. *(Numbers pending the DGX run.)*

---

## 1 · Introduction (outline)
- Fraud is increasingly **voice-based and Indic**; telephony is **narrowband + codec-degraded**.
- Existing ADD is strong on **wideband English** (ASVspoof 2019/2021/5, In-the-Wild) but **generalizes poorly** — the gap is already documented [MDPI’26, Harder-or-Different’24, DOSS’26].
- Codec compression is a **dominant** cause of degradation [Klein et al., Odyssey’26; Li et al., 2025]; codec-aware training helps [CFE-ResNet’23, DK-CAST’25].
- Several systems detect short/streaming/degraded speech [S-MGAA’26, C-MCSS-Mamba’26] and one commercial system targets **G.711 telephony** [DeepBlocker’26]; Indic **datasets** exist [IndicSynth, ACL’25] but **Indic telephony *detection methods*** remain largely unaddressed.
- Abstention is known for single countermeasures [Hou et al., 2021]; **multi-evidence arbitration with channel-aware abstention** is not.

**Contributions (state verbatim in the intro):**
- **C1 — Indic telephony benchmark.** 23 languages × 6 channel conditions, per-language scorecard. *Extends IndicSynth (12 langs, wideband) to telephony.*
- **C2 — Channel-profiled detector + codec-aware gate.** A profiler estimates codec/bandwidth/SNR and routes/gates the decision. *Technical effect: bounded false alarms + stable real-time compute.*
- **C3 — Evidence arbitration + calibrated abstention.** Fuses heterogeneous evidence and abstains on disagreement; reported with **risk–coverage**, **FP-reduction on genuine callers**, and **Cllr/ECE**.
- **C4 — Unknown-generator novelty scoring + Unknown Vault.** Flags unseen generators and enrols them without retraining.
- **C5 — Deployable on-prem Indic stack.** SSL detector + profiler + arbitration + speaker/diarization + Indic ALD/ASR; CPU real-time, privacy-preserving.

---

## 2 · Related Work (written)

### 2.1 Self-supervised front-ends and anti-spoofing back-ends
Modern ADD fine-tunes SSL encoders (Wav2Vec2, **XLS-R**, WavLM, HuBERT, Data2Vec) with classifier back-ends (**AASIST/AASIST3**, RawNet2, RawGAT-ST, MFA-Conformer). ASVspoof 5 [Wang et al., 2024] confirmed SSL front-ends dominate the **open** condition, while **closed**-condition winners rely on DSP augmentation (RawBoost, SpecAugment, codec perturbations). We adopt the SSL+RawBoost recipe as our reference detector and add channel profiling and arbitration on top.

### 2.2 Generalization to unseen generators
The central challenge is generalization, now well characterized: model capacity does not fix it, and the gap is largely **“difference,” not “hardness”** [Harder-or-Different’24]. Data composition is a lever: **DOSS** [Huang et al., ACL’26] shows diversity-optimized sampling reaches 2.34% avg EER on unseen attacks; **SLIM** [Reality Defender] uses style↔linguistics mismatch; **ICLAD** [ACL Findings’26] adapts training-free via in-context learning; **Teffic-Audio** [2026] tops Speech-DF-Arena (1.45% pooled EER) via balanced, augmented training; **“The Generalization Gap”** [MDPI Electronics’26] shows detectors collapse to chance on SONAR’s modern TTS. **TWINSHIFT** [2026] enforces unseen-generator-and-speaker evaluation. *We do not claim the gap; we target the **unaddressed regime** (Indic telephony) and measure it with a novelty score.*

### 2.3 Codec, compression, and telephony robustness
Compression is a first-order threat: a systematic study of 10 detectors × 18 corruptions finds **compression and neural codecs** most damaging [Li, Chen, Wei, 2025]; ASV on G.711/GSM/AMR/Opus degrades up to 2× [Sokol et al., 2022]. **CFE-ResNet** [Interspeech’23] embeds a compression branch; **DK-CAST** [Discover Computing’25] uses codec-aware distillation (0.38% / 2.18% EER; 3.01% under MP3). For telephony specifically, **Klein et al. (Odyssey’26)** show **codecs cause most of the degradation** and that RawBoost + random quantization **outperform training on real telephony data** (−20.1% relative EER). A commercial **G.711 detector** exists [DeepBlocker `xlsr-mamba-g711-v5`, 2026] but is **closed, English, and non-abstaining**. *Gap: no codec-profiled **decision** layer, and no Indic telephony detector.*

### 2.4 Streaming, early, and short-utterance detection
Detecting at the call opening is valuable: **S-MGAA** [2026] targets 0.5–2 s inputs under codec + packet loss with a lightweight TF-attention net; **C-MCSS-Mamba** [2026] is block-causal/streaming with TTS/VC mechanism states. *These are English-centric; we keep streaming as a deployment mode, not our novelty.*

### 2.5 Abstention, selective prediction, and one-class learning
Abstention for spoofing countermeasures was introduced by **Hou et al. [2021]** (energy/NN confidence; better EER on confident trials). **CA-SOADD** [ICML’26] tightens a one-class boundary without negatives; **fuzzy DPTFAN** [Sensors’25] injects uncertainty via Pythagorean fuzzy sets; selective prediction is standard in NLP/ML [Survey: Hendrickx et al., 2024]. *We extend abstention from a **single CM** to **multi-source evidence arbitration** on a **channel-profiled telephony** signal.*

### 2.6 Multilingual / Indic / low-resource speech
**IndicSynth** [Sharma, Ekbote, Gupta, ACL’25] provides 4,000 h, 12 Indic languages (CC-BY-NC) and shows SOTA ADD **fails** on Indic; IndicSUPERB, Task-Lens, GreenVoice map the resource landscape. *We use these datasets and extend to **telephony** across 23 languages with a per-language scorecard.*

### 2.7 Datasets and benchmarks
ASVspoof 2019/2021/**5**, In-the-Wild, **SONAR**, **CodecFake(+**), DFADD, Fake-or-Real, ADD 2022/23, **MLAAD**, Speech-DF-Arena. We report on ASVspoof-style slices **plus** our Indic telephony matrix.

---

## 3 · Method (skeleton — fill from code)
```
audio → Universal Input Profiler (codec/bandwidth/SNR)
      → Fast L0 gate            (cheap reject)
      → SSL detector (XLS-R + RawBoost)  +  codec-aware branch
      → evidence brains: physics · replay · environment · cross-codec · speaker · semantic↔prosody(ASR)
      → Evidence Arbitration (fuse + confidence)
            ├─ accept (high confidence)
            └─ ABSTAIN (disagreement / low confidence) → deeper stage / human
      → VoxScore + novelty score → verdict + reason codes
```
- **Profiler** (`backend/profiler.py`): maps to {clean, G.711 µ-law, G.711 A-law, G.722, packet-loss} and drives the gate.
- **Detector** (`pipeline/train_corpus.py`, `backend/fusion.py`): XLS-R-300M fine-tune + RawBoost + telephony augmentation (`telephony_aug.py`, `scenario_render.py`).
- **Arbitration/abstention** (`backend/arbitration.py`, `self_critique.py`, `orchestrate.py`).
- **Novelty** (`backend/unknown_vault.py`, `generator_hunter.py`).

## 4 · Experiments
- **Data:** IndicSynth (spoof) + IndicVoices/Shrutilipi/Vaani (genuine) + MLAAD/CodecFake/DFADD (OOD). IndicSynth is **CC-BY-NC → research only**.
- **Conditions:** clean, G.711 µ-law, G.711 A-law, G.722, replay, codec round-trip; per language.
- **Metrics:** EER, AUC, **minDCF/Cllr** (calibration), **risk–coverage/AURC & FP-reduction** (abstention), seen-vs-unseen EER (gap), LOGO.
- **Baselines:** XLS-R+RawBoost (ours, no gate/abstention), ResNet18/LFCC, AASIST/AASIST3, one-class (OC-Softmax).
- **Ablations:** ±channel-profiled gate; ±evidence arbitration; ±abstention; ±RawBoost.

## 5 · Results (fill from the harness)
Run on the DGX after training:
```bash
python backend/paper_report.py --csv checkpoints/round_*/scores.csv --baseline clean --out report.txt
```
This emits: per-language table (C1), per-channel EER + Δ (C2), language×channel cross-tab (C1), seen/unseen gap (C4), LOGO (C4), and risk–coverage + FP-reduction + Cllr (C3). Paste the tables into Tables 1–4.

## 6 · Limitations & ethics
- IndicSynth is **CC-BY-NC** (non-commercial); consented/real recordings never leave on-prem storage.
- No claim of SOTA on English wideband benchmarks.
- Abstention transfers risk to a second stage; we quantify the coverage–risk trade-off.

## 7 · References (seed list — expand)
- Sharma, Ekbote, Gupta. *IndicSynth.* **ACL 2025** Long, 22037–22060.
- Wang et al. *ASVspoof 5: Crowdsourced Speech Data, Deepfakes, and Adversarial Attacks at Scale.* **ASVspoof 2024**; overview arXiv:2601.03944.
- *The Generalization Gap…* **MDPI Electronics** 15(13):2846, 2026.
- *Harder or Different? Understanding Generalization of Audio Deepfake Detection.* arXiv:2406.03512.
- Huang et al. *DOSS.* **ACL 2026** Long.
- *ICLAD.* **ACL Findings 2026**.
- *Teffic-Audio.* arXiv:2607.28351.
- *TWINSHIFT.* arXiv:2510.23096.
- *Audio Deepfake Detection at the First Greeting (S-MGAA).* arXiv:2601.19573.
- Klein et al. *The Effect of Telephony Transmission on Source Tracing of Audio Deepfakes.* **Odyssey 2026.**
- Li, Chen, Wei. *Measuring Robustness of Audio Deepfake Detection under Real-World Corruption.* 2025.
- *CFE-ResNet.* **Interspeech 2023.**
- *DK-CAST.* **Discover Computing**, 2025.
- *C-MCSS-Mamba.* arXiv, 2026.
- Hou et al. *Estimating the Confidence of Speech Spoofing Countermeasure.* arXiv:2110.04775.
- *CA-SOADD.* **ICML 2026.**
- Sokol et al. *Automatic Speaker Verification on Compressed Audio.* 2022.
- DeepBlocker. *xlsr-mamba-g711-v5 model card.* 2026.
