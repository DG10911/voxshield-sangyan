# VoxShield — Prior-Art & Novelty Positioning for a Research Paper
**Purpose:** compare the 2025–2026 audio-deepfake-detection (ADD) literature and adjacent systems so we can state VoxShield's contributions honestly and defensibly. Compiled 2026-10-02 from live sources (venues/deadlines verified).

---

## 0 · The one-line situation
The field is **crowded and moving fast** on exactly the axes we touched — *generalization*, *codec/telephony robustness*, *abstention*, and *Indic datasets*. **None of those ideas alone is novel.** Our defensible space is the **combination**: a **channel-profiled, evidence-arbitrated, abstaining detector for multilingual Indic narrowband telephony, deployed on-prem**, validated on a reproducible codec/channel matrix.

---

## 1 · Master comparison table (systems)

| # | System / paper | Year · venue | Task | Approach | Data | Headline result | Limitation | Overlap w/ VoxShield |
|---|---|---|---|---|---|---|---|---|
| 1 | **ASVspoof 5** (Wang et al.) | 2024 · ASVspoof/Interspeech | CM + SASV, **Track 2 = telephony/VoIP** | SSL frontends + graph/ResNet backends, ensembles | crowdsourced, 16 attacks, codecs | Open T1 EER ~3–4%; **cross-DB EER 10–27%**; T2 min-aDCF 0.07 (open) | calibration poor (actDCF≈1); generalization still open | core benchmark we must report on |
| 2 | **IndicSynth** (Sharma, Ekbote, Gupta) | 2025 · **ACL Long** | **Indic synthetic speech dataset** | xtts-v2/vits/freevc over IndicSUPERB; mimicry+diversity | **12 Indic langs, 4,000 h, 989 spk** | SOTA ADD **fails** on Indic test sets | dataset only; **wideband**; CC-BY-NC (non-commercial) | our data source; proves the Indic gap |
| 3 | **"The Generalization Gap"** | 2026 · MDPI Electronics | vishing ADD | ResCNN + OC-Softmax one-class | ASVspoof19 → SONAR (9 modern generators) | **all models ≈ chance** on unseen modern TTS | no telephony/Indic; wideband | the "gap" is **already published** — cannot claim |
| 4 | **"Harder or Different?"** | 2024 · arXiv 2406.03512 | ADD generalization analysis | decompose gap into hardness vs difference | ASVspoof 19/21 | gap is **difference**, not hardness | analysis only | theoretical backing; cite, don't claim |
| 5 | **DOSS** | 2026 · **ACL Long** | data-centric generalization | diversity-optimized sampling | 12k h curated | **2.34% avg EER** unseen | data recipe, not telephony/Indic | data strategy prior art |
| 6 | **SLIM** (Reality Defender) | 2025 · patent US20250363996A1 | generalizable ADD | style↔linguistics mismatch, contrastive | bona fide speech | OOD gains | **patented**; English | mental model; freedom-to-operate risk |
| 7 | **ICLAD** | 2026 · **ACL Findings** | in-the-wild ADD | in-context learning + pairwise compare (ALM) | ITW/SpoofCeleb/DFEval | 2× macro-F1 on in-the-wild | LLM cost; no telephony | alternative backend |
| 8 | **Teffic-Audio** | 2026 · arXiv 2607.28351 | general ADD | Conformer + attentive pooling; <br>balance + **diverse augmentation** | open data | **pooled EER 1.454%** on Speech-DF-Arena (14 sets, #1) | no Indic/telephony | SOTA baseline to cite |
| 9 | **TWINSHIFT** | 2026 · arXiv 2510.23096 | OOD benchmark | unseen generator **and speaker** | benchmark | rigor for generalization claims | benchmark only | eval protocol reference |
| 10 | **SONAR** | 2025–26 | modern-TTS stress benchmark | 9 SOTA TTS vs human | 9,077 clips | detectors ≈ chance | wideband/English | eval set |
| 11 | **Audio deepfake @ first greeting (S-MGAA)** | 2026 · arXiv 2601.19573 | **ultra-short telephony** (0.5–2 s) under codec + packet loss | Multi-Granularity Adaptive TF attention, lightweight | Fake-or-Real/WaveFake/MLAAD/FoR | beats 9 SOTA, low RTF | no Indic; no abstention | **early-detection space taken** |
| 12 | **Telephony source tracing** (Klein et al.) | 2026 · **Odyssey** | source tracing under telephony | bandwidth vs codec ablation; **RawBoost + quantization aug** | telephony-transmitted | **codecs cause most degradation**; −20.1% rel EER | tracing, not detection; no Indic | strong support for our codec story |
| 13 | **Measuring robustness under corruption** (Li, Chen, Wei) | 2025 · arXiv | 10 detectors × 18 corruptions | AudioPerturber (noise/mod/compression/neural codecs) | multiple | models fragile to **compression/neural codecs** | analysis only | cite for channel stress |
| 14 | **CFE-ResNet** | 2023 · Interspeech | compressed-speech detection | compression-feature embedding, dual-branch ResNet | ASVspoof 19/21 + Mp3/AAC/OGG | robust to MP3/AAC | codecs, not telephony/Indic; no abstention | closest "codec-aware" prior art |
| 15 | **DK-CAST** | 2025 · Discover Computing | degraded ADD | codec-aware distillation (XLS-R teacher → student) | ASVspoof 19/21 | 0.38%/2.18% EER; 3.01% under MP3 | no telephony/Indic; no abstention | codec-aware competitor |
| 16 | **C-MCSS-Mamba** | 2026 · arXiv | **streaming/block-causal** SDD | XLS-R + Mamba, TTS/VC states, prefix decisions | ASVspoof19 + 4 cross-db | 0.47% EER; early prefix | no telephony/Indic; no abstention | streaming competitor |
| 17 | **Confidence estimation for CMs** (Hou et al.) | 2021 · arXiv 2110.04775 | **abstention** for spoofing CM | energy/NN confidence estimators | ASVspoof19 + VCC | abstain on unknown attacks; better EER on confident | wideband; single CM; no Indic | **abstention is NOT novel per se** |
| 18 | **CA-SOADD** | 2026 · **ICML** | strict one-class ADD | centroid-anchored boundary probes, no negatives | ASVspoof + MLAAD | best unseen-attack / domain-shift | one-class only; no telephony | one-class alternative to cite |
| 19 | **Fuzzy DPTFAN** | 2025 · Sensors | ADD | Pythagorean fuzzy sets + dual-path TF attention | ASVspoof | improved robustness/interpretability | not telephony/Indic | "uncertainty" prior art |
| 20 | **ASV on compressed audio** (Sokol et al.) | 2022 | speaker verification over codecs | GSM/AMR/G.711/G.722/AAC/Lyra/Opus + Discord | VoxCeleb etc. | codec → up to 2× EER; hard-mining helps | ASV not ADD | telephony-channel evidence |
| 21 | **DeepBlocker `xlsr-mamba-g711-v5`** (model card) | 2026 · commercial | **G.711 telephony ADD** | XLS-Mamba-LA fine-tuned, frozen SSL, G.711 aug | production telephony | ROC-AUC ≥0.92 G.711 | **closed**; English; no Indic; no abstention | **direct commercial competitor — must differentiate** |
| 22 | **Pindrop** (granted **US12562150B2**) | 2024–26 | call-center deepfake/liveness | spoofprints, response delay, NLP | call audio | granted patent | **patent**, not a paper | freedom-to-operate: broad claims taken |
| 23 | **Reality Defender** (granted US12462813B1) | 2025 | explainable ADD | real↔vocoded TF difference supervision | VocV4/LibriSeVoc | granted | patent | patent risk |

---

## 2 · The seven clusters (related-work skeleton)

1. **SSL front-ends** — Wav2Vec2, XLS-R, WavLM, HuBERT, Data2Vec; AASIST/AASIST3, RawNet2, RawGAT-ST, MFA-Conformer. *(foundation)*
2. **Generalization / data-centric** — DOSS (ACL'26), SLIM, "Harder or Different?", "The Generalization Gap", TWINSHIFT. **← idea taken.**
3. **Compression / telephony / codec robustness** — CFE-ResNet (IS'23), DK-CAST (2025), telephony source tracing (Odyssey'26), AudioPerturber study (2025), ASV-on-compressed (2022), DeepBlocker (2026). **← active, but *Indic telephony* under-served.**
4. **Streaming / early / short-utterance** — C-MCSS-Mamba (2026), S-MGAA (2026). **← taken for English.**
5. **Abstention / selective prediction / one-class** — Hou et al. (2021), CA-SOADD (ICML'26), fuzzy DPTFAN (Sensors'25). **← abstention exists for single CMs.**
6. **Multilingual / Indic / low-resource** — IndicSynth (ACL'25), IndicSUPERB, Task-Lens, GreenVoice. **← datasets exist; *methods* for Indic telephony ADD are open.**
7. **Datasets & benchmarks** — ASVspoof 2019/2021/5, MLAAD, SONAR, ITW, CodecFake, DFADD, Fake-or-Real, ADD 2022/23, Speech-DF-Arena. **← we must test on these.**

---

## 3 · Gap analysis — what is TAKEN vs OPEN

**Already claimed in the literature (do NOT present as novel):**
- "We identify a generalization gap on unseen generators." *(MDPI 2026, HarDer/Different 2024)*
- "SSL front-end + backend improves ADD." *(many)*
- "Codec compression degrades detectors; augmentation helps." *(CFE-ResNet, DK-CAST, Odyssey'26)*
- "Abstain when unconfident for spoofing CMs." *(Hou 2021)*
- "A dataset for Indic synthetic speech." *(IndicSynth ACL'25)*
- "Short/streaming detection for real-time." *(S-MGAA, C-MCSS-Mamba)*

**Still open (our room to claim):**
- **Indic *telephony* (narrowband G.711/narrowband) ADD with per-language results** — IndicSynth is wideband; ASVspoof T2 is not Indic; DeepBlocker is English/closed. *Open.*
- **Channel/codec-profiled *decision* layer** — most work augments/attends but does not **profile the channel and gate the decision** (route/abstain based on measured codec/bandwidth/SNR). *Largely open.*
- **Evidence arbitration across heterogeneous "brains" + calibrated abstention on Indic telephony** — Hou is a single CM; CA-SOADD is one-class. **Multi-source arbitration with channel-aware abstention** is our space.
- **Unknown-generator novelty scoring + an "unknown vault" for continuous operation** — not standard.
- **Reproducible Indic-telephony channel matrix benchmark** (G.711 A/µ-law, G.722, replay, codec round-trips × 20+ Indic languages). *Open benchmark contribution.*
- **Zero-cloud, on-prem, privacy-preserving Indic deployment** with Bhashini/AIKosh provenance. *Systems contribution.*

---

## 4 · VoxShield's defensible claims (write these as contributions)

**C1 · Multilingual Indic telephony benchmark.** We curate and release a **narrowband Indic ADD evaluation matrix**: 20+ languages × {clean, G.711 µ-law, G.711 A-law, G.722, replay, codec round-trip}, with a per-language scorecard. *(Extends IndicSynth from wideband/12 langs to telephony/23 langs.)*

**C2 · Channel-profiled detector with a codec-aware gate.** A **Universal Input Profiler** estimates codec/bandwidth/SNR and **routes** to a codec-appropriate branch (and can abstain). *Technical effect: bounded false-alarm rate and stable compute on real telephony.* Most prior work either augments blindly or attends; few **explicitly profile-and-gate the decision**.

**C3 · Evidence arbitration + calibrated abstention (VoxScore).** A decision layer fuses **heterogeneous evidence** (acoustic/physics, replay, environment, cross-codec, speaker, semantic↔prosody from ASR) and emits an **explicit abstain** when evidence disagrees, deferring to a deeper stage or a human. *We report the FP-rate reduction on genuine Indic callers and the abstention/accuracy trade-off* (risk–coverage curves). **Abstention exists for single CMs; multi-evidence arbitration on telephony Indic does not.**

**C4 · Unknown-generator novelty scoring + Unknown Vault.** A **novelty score** flags likely-unseen generators and stores them for offline enrolment without retraining — sustaining operation as generators evolve. *This is a continuous-operation contribution, not a restatement of the gap.*

**C5 · Deployable Indic stack.** An end-to-end, **on-premise** system (SSL detector + profiler + arbitration + speaker verification/diarization + Indic ALD/ASR), trained on public/AIKosh data, evaluated for **CPU/real-time** feasibility and **privacy** (no cloud egress). *Systems contribution.*

---

## 5 · Positioning statement & title options

> **Core claim:** *"We show that explicitly profiling the telephony channel and arbitrating heterogeneous evidence with calibrated abstention substantially reduces false alarms on genuine multilingual Indic callers while preserving unseen-generator detection — a regime the existing English/wideband literature does not address."*

**Title options**
1. *VoxShield: Codec-Profiled Evidence Arbitration with Calibrated Abstention for Multilingual Indic Telephony Deepfake Detection*
2. *Detecting Indic Telephony Deepfakes Behind the Codec: Channel Profiling, Evidence Arbitration, and Abstention*
3. *When to Say "I Don't Know": Selective, Channel-Aware Deepfake Detection for Indic Phone Calls*

**One-sentence contributions (for the abstract):** C1 benchmark · C2 profiler/gate · C3 arbitration+abstention · C4 novelty scoring · C5 deployable stack.

---

## 6 · Comparison table to put IN the manuscript

| System | Indic langs | Telephony/G.711 | Abstention | Unseen-gen handling | Speaker-ID fused | On-prem | Open |
|---|---|---|---|---|---|---|---|
| ASVspoof 5 T2 | ✗ | ✓ (VoIP) | ✗ | ✗ | ✓ (SASV) | ✗ | ✓ |
| IndicSynth | ✓ (12) | ✗ (wideband) | ✗ | ✗ (dataset) | ✗ | n/a | ✓ |
| "Gen. Gap" (MDPI'26) | ✗ | ✗ | ✗ | analyze only | ✗ | ✗ | ✓ |
| DOSS (ACL'26) | ✗ | ✗ | ✗ | data recipe | ✗ | ✗ | ✓ |
| S-MGAA (2026) | ✗ | ✓ (short) | ✗ | ✗ | ✗ | ✓ (light) | ✓ |
| DK-CAST (2025) | ✗ | codecs | ✗ | ✗ | ✗ | student | ? |
| Hou et al. (2021) | ✗ | ✗ | **✓** | ✓ (conf) | ✗ | ✗ | ✓ |
| DeepBlocker (2026) | ✗ | ✓ G.711 | ✗ | ✗ | ✗ | service | ✗ |
| **VoxShield (ours)** | **✓ (23)** | **✓ G.711 A/µ** | **✓** | **✓ novelty** | **✓** | **✓** | **✓** |

---

## 7 · Experiments required to *earn* the claims

| Claim | Experiment | Metric |
|---|---|---|
| C1 | Per-language EER/ROC-AUC over the codec × language matrix | per-lang EER, macro-avg |
| C2 | Ablation: with vs without channel-profiler gate; clean vs G.711 vs G.722 | EER, FP rate, RTF/CPU |
| C3 | **Risk–coverage curve** of abstention; FP-rate on genuine Indic calls before/after arbitration | AUC of selective prediction, FP@fixed recall |
| C4 | Held-out **unseen generator** slice; novelty-score ROC; Unknown-Vault enrolment gain | unseen-gen EER, novelty AUC |
| C5 | Real-time factor on CPU; end-to-end latency; privacy (no egress) | RTF, ms/clip |
| Baselines | XLS-R+RawBoost (our training recipe), AASIST/AASIST3, ResNet18, one-class (OC-Softmax) | EER/minDCF, Cllr |

**Report calibration too:** ASVspoof 5 showed top systems have *poor calibration* (actDCF≈1). Our abstention/arbitration story is stronger if we report **Cllr/ECE** and show better-calibrated, decision-useful scores.

---

## 8 · Citation kit (key references)

- **IndicSynth** — Sharma, Ekbote, Gupta. ACL 2025 Long, pp. 22037–22060. `2025.acl-long.1070`
- **ASVspoof 5** — Wang et al., *Crowdsourced Speech Data, Deepfakes, and Adversarial Attacks at Scale* (ASVspoof 2024) + challenge overview arXiv 2601.03944
- **The Generalization Gap** — MDPI Electronics 15(13):2846, 2026
- **Harder or Different?** — arXiv 2406.03512
- **DOSS** — ACL 2026 Long, `2026.acl-long.796`
- **ICLAD** — ACL Findings 2026, `2026.findings-acl.450`
- **Teffic-Audio** — arXiv 2607.28351
- **TWINSHIFT** — arXiv 2510.23096
- **S-MGAA (first greeting)** — arXiv 2601.19573
- **Telephony source tracing** — Klein et al., Odyssey 2026 (`klein26_odyssey`)
- **Audio robustness under corruption** — Li, Chen, Wei, arXiv 2025 (AudioPerturber)
- **CFE-ResNet** — Interspeech 2023
- **DK-CAST** — Discover Computing, 2025
- **C-MCSS-Mamba** — arXiv 2026
- **Confidence/abstention for CMs** — arXiv 2110.04775 (Hou et al.)
- **CA-SOADD** — ICML 2026
- **Fuzzy DPTFAN** — Sensors 25(24):7608, 2025
- **DeepBlocker** — `deepblocker.ai/model-card` (xlsr-mamba-g711-v5)
- Patents: **US12562150B2** (Pindrop), **US12462813B1** & **US20250363996A1** (Reality Defender)

---

## 8b · Zero-shot IndicSynth baselines vs our projected numbers (the money table)

IndicSynth (ACL'25) benchmarked **English-trained SOTA ADD, zero-shot, no fine-tuning** on IndicSynth-IndicSuperb. Their EERs are catastrophic — this is our strongest comparison.

| Language | Generator | AASIST | AASIST-L | RawNet-2 |
|---|---|---|---|---|
| Bengali | XTTS-v2 / FreeVC24 / VITS | 70.1 / 88.0 / **93.2** | 56.2 / 86.6 / 89.4 | 56.7 / 53.5 / 48.3 |
| Hindi | XTTS-v2 / FreeVC24 | 42.0 / 81.8 | 45.4 / 81.9 | **14.5** / 48.5 |
| Marathi | XTTS-v2 / FreeVC24 | 56.7 / 79.5 | 52.8 / 81.6 | 48.0 / 52.5 |
| Tamil | XTTS-v2 / FreeVC24 | 61.7 / 81.7 | 51.2 / 83.1 | 51.7 / 55.0 |
| Telugu | XTTS-v2 / FreeVC24 | 54.3 / 75.7 | 52.7 / 79.0 | 46.3 / 52.8 |
| Sanskrit | XTTS-v2 / FreeVC24 | 33.4 / 84.2 | 38.8 / 86.6 | **8.0** / 58.4 |
| *(range over all 12 langs)* | | **33–93%** | **39–89%** | **8–58%** |

*(On ASVspoof19-LA the same models score AASIST 0.83%, AASIST-L 0.99% — i.e. they collapse on Indic.)*

| Setting | Clean (seen) EER | Unseen-generator EER | Notes |
|---|---|---|---|
| **Zero-shot SOTA on Indic (IndicSynth'25)** | **33–93%** | — | English-trained, no fine-tune |
| Global SOTA, English wideband | AASIST 0.83 · C-MCSS-Mamba 0.47 · DK-CAST 0.38% | DOSS 2.34 · Teffic 1.45% (pooled) | different target |
| ASVspoof 5 open / cross-DB | ~3–4% | **10–27%** | telephony track; poor calibration |
| **VoxShield (projected, fine-tuned on Indic)** | **0.3–2%** | **5–20%** | + channel gate, abstention, 23 langs |

**Read:** fine-tuning on Indic is projected to cut EER from **33–93% → single digits** (≈30–90 absolute points) — that is the *baseline lift*, and it is why the method matters more than another architecture. We should **not** claim SOTA vs DOSS/Teffic (they are easier, English, more data); we claim the **regime** + the **abstention/profiling** contribution.

| Axis | Best existing | VoxShield projected | Verdict |
|---|---|---|---|
| Indic clean EER | 33–93% (zero-shot) | 0.3–2% | **large win (but fine-tuned)** |
| ≥G.711 telephony | DeepBlocker AUC≥0.92 (closed, EN) | EER 2–6% → AUC ~0.97–0.99 (open, 23 langs) | **win on scope** |
| Unseen generator | DOSS 2.34 / Teffic 1.45 (EN, pooled) | 5–20% | **we lose on raw EER — don't claim SOTA** |
| Abstention | Hou'21 (single CM) | FP −30–60% rel @90% cov | **first on Indic telephony evidence-fusion** |
| Calibration | ASVspoof5 actDCF≈1 (poor) | Cllr 0.3–1.0 bits | **competitive** |

---

## 9 · Overclaim warnings (reviewer-proofing)

1. **Don't** claim the generalization gap, abstention, codec augmentation, or Indic datasets as novel.
2. **Don't** claim SOTA on ASVspoof (we won't beat Teffic-Audio/DOSS); **claim the regime** we address.
3. **Do** frame abstention as *selective prediction over multi-source telephony evidence*, with risk–coverage curves and calibration.
4. **Do** position the **channel-profiled gate + arbitration + Indic telephony** as the novel *combination*, and back it with ablations.
5. **Licence note:** IndicSynth is **CC-BY-NC** → research only; state this explicitly in ethics/licence section.
