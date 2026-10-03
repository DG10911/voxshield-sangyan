# VoxShield — SOTA Research & Upgrade Plan (2026-09-29)

Field scan of 2024–2026 voice-deepfake / anti-spoofing research, mapped to our stack
(5-detector ensemble: Acoustic DSP + wav2vec2 + XLS-R-53 + DistilHuBERT + LFCC/CQCC +
learned meta-fusion; Indic telephony; unseen-generator robustness = #1 priority).

> ⚠️ **Verify every arXiv link before citing in a submission.** This is a research
> lead-sheet, not a citation list. Numbers are as-reported by the sources — reproduce
> before claiming any of them as ours.

## The hard truth (consistent across sources)
- SSL front-ends (XLS-R / WavLM / wav2vec2) now dominate: **~1.5–3.5% EER in-distribution**.
- **But 30–50% relative degradation on UNSEEN generators** — "domain amnesia" (99% in-lab → ~50% error in the wild). This is exactly the gap our `eval_gengap` measured (+9.95 pts). Our focus is the right one.

## SOTA detectors worth adopting
| Approach | Reported | For us |
|---|---|---|
| **XLS-R-300M + SLS** (selective layer summarization) | ~1.92% EER ASVspoof21-DF | Strongest single front-end; codec-robust. **GPU-train.** |
| **WavLM ensemble / +wav2vec2 fusion** | ~2.56–2.69% EER | Alt front-end; fusion gains diminish vs single XLS-R+SLS |
| **RawBoost augmentation** | **+27% rel.** on telephony/codec | **Highest-value for G.711.** Training-time only, no inference cost |
| **Meta-LoRA / MLDG** | 8.84%→5.30% EER unseen | Few-shot adapt to new generators |
| **Gaussian-Process few-shot (ADD-GP)** | 21.67%→10.42% w/ ~96 samples | Adapt to a new Indic TTS from ~50–100 calls, no full retrain |
| AASIST2 / XLSR-Mamba | short-utt / low-latency | Backend options |
| Whisper-based / diffusion-restore | — | ⚠️ latency/compute heavy — **skip for real-time** |

## Datasets — the Indic gap is real (and it's our opening)
- **IndicSynth** (~4,000 hrs, 12 Indic langs, TTS+VC) — first large-scale Indic deepfake set
- **IndicFake** (~7,350 hrs, 17 Indian langs + En, 4.2M samples)
- **Indic-CodecFake** (neural-codec deepfakes, 12 Indic langs) — directly on our G.711/codec theme
- **IndicVoices-R** (AI4Bharat, all 22 langs, genuine) — our HUMAN / Worst-Human side
- Standard: ASVspoof 2019/2021/**5(2024)**, In-the-Wild, MLAAD, CodecFake, WaveFake
- Verdict: **Indic deepfake-detection data is <1yr old and sparse — a genuine research contribution is available here.**

## Indic models/platforms
- **AI4Bharat**: IndicWav2Vec (SSL backbone, 22 langs), IndicTTS (baseline generator), IndicVoices-R
- **BHASHINI/ULCA**: LID/ASR/TTS — our `bhashini.py` adapter is ready for keys
- Generators to add to the registry: IndicTTS, MMS, Sarvam AI, DonaLabTTS

## Top 5 recommendations (ranked, honest)
1. **XLS-R-300M + SLS front-end** — +15–20% rel. EER, codec-robust. *Low complexity, GPU-train.* 🅿️
2. **RawBoost + test-time LoRA** — +10–15% on telephony/unseen. *Highest Indic-telephony value.* 🅿️
3. **Curate IndicSynth + IndicFake training set** — +8–12% on Indic speakers. *Fills the gap.* 🅿️ (data + GPU)
4. **Cascade detection (LFCC→SSL)** — RTF ×4 faster, ~1–2% EER cost. ✅ **already built** as `cascade.py` (L0→L3); validate the LFCC L1 gate on real data.
5. **Gaussian-Process few-shot adapter** — +10% unseen TTS from ~96 samples. *Research differentiator.* 🅿️

## Status mapping
- ✅ **Already have:** cascade (#4, `cascade.py`), open-set/abstain (`voxscore`), generalization-gap harness (`eval_gengap`, measured), scenario/codec rendering (`scenario_render`), BHASHINI + generator + corpus adapters (ready for keys/data).
- 🅿️ **GPU-parked (do when access returns):** #1 XLS-R+SLS, #2 RawBoost+LoRA, #3 Indic-dataset training, #5 GP few-shot. All are *training* upgrades — our serving/eval scaffolding already supports dropping them in.
- 🌐 **Data:** pull IndicSynth / IndicFake / Indic-CodecFake / IndicVoices-R via `corpus_ingest.py`.

## Honest hype filter
- ✅ Proven: SSL front-ends, RawBoost, few-shot meta-learning.
- ⚠️ Diminishing: heavy ensemble meta-fusion (single XLS-R+SLS often matches it).
- ❌ Skip for real-time: Whisper-based detectors, diffusion reconstruction (latency/compute).
