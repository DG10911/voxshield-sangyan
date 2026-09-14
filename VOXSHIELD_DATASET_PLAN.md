# VoxShield — 800 GB Dataset Allocation Plan (Research & Architecture Review)

*Senior-ML-scientist review of the dataset strategy. All sizes/IDs verified live via HuggingFace API 2026-09-14. Verification tags: **VERIFIED** / **REPORTED** / **UNCERTAIN** / **NOT FOUND**. No data has been downloaded or modified.*

---

## 0. Verification results (what changed vs your candidate list)

| Dataset | Your claim | Verified reality | Tag |
|---|---|---|---|
| IndicSynth | ~845 GB, HF `vdivyasharma/IndicSynth` | **845.2 GB**, 1,412 parquet files, per-language dirs, **open**, CC BY-NC 4.0 | **VERIFIED** |
| IndicVoices | ~744 GB | **744.7 GB**, 1,499 parquet, gated-auto, CC-BY | **VERIFIED** |
| IndicVoices-R | ~1,047 GB | **1,047 GB**, gated-auto | **VERIFIED** |
| Indic-CodecFake | ~80 GB (est) | **NOT ON HUGGINGFACE.** Only project page helixometry.github.io/IndicFake. No downloadable repo found via HF search. | **NOT FOUND** — cannot allocate |
| Rural_Women_ASR_v2 | ~127 GB | **127 GB**, open | **VERIFIED** |
| Lahaja | ~1.4 GB | **1.4 GB**, gated-auto | **VERIFIED** |
| indicvoices-cleaned | ~0.4 GB | **0.4 GB**, open | **VERIFIED** |
| BanglaFake | ~25.5k clips | HF `sifat1221/banglaFake` exists (size UNCERTAIN); arXiv 2505.10885 | **REPORTED** |
| CodecFake+ | ~100.5 GB | **100.5 GB** split `.xz` archive (NOT parquet → must extract), 1.42M clips, MIT, open | **VERIFIED** |
| MLAAD | ~34.7 GB | **34.7 GB**, 99,306 wav files, gated-auto | **VERIFIED** |
| ST-Codecfake | uncertain | Zenodo 14631091 only (not on HF), EN+ZH, size UNCERTAIN | **REPORTED** |
| CVoiceFake | ~1.25M clips | Only `SpeechAntiSpoofingBenchmarks/CVoiceFake_small` on HF; full = Zenodo 11229569 | **REPORTED** |

**Also verified & available (not in your list but higher-value than some that are):**
- **DFADD** `isjwdu/DFADD` — 42.7 GB, **diffusion + flow-matching** English fakes, MIT, open. **VERIFIED.** (The modern attack class you're missing.)
- **ASVspoof5** `jungjee/asvspoof5` — 142 GB, 32 attacks + adversarial, open. **VERIFIED.**
- **AI4Bharat TTS models** (IndicF5, indic-parler-tts, vits_rasa_13, vits-*) — 1–4 GB each, open. **VERIFIED.** Generate your *own* fakes.

**Already on your SSD (~129 GB, keep):** asvspoof19_LA, codecfake, elevenlabs, garystafford, in_the_wild, indicvoices (4k), speechfake, wavefake.

---

## 1. What actually matters most for VoxShield (ranked, with reasoning)

For a **cross-generator, cross-lingual, telephony-robust Indic detector**, the ranking is NOT "more audio." It is:

| Rank | Factor | Why | Data implication |
|---|---|---|---|
| 1 | **Fake-generator diversity** | Your #1 measured gap. A detector overfits to the vocoders it saw. Cross-generator EER is the make-or-break number. | Maximize distinct TTS/VC/codec engines, not clip count |
| 2 | **Codec/telephony relevance** | Your target domain is 8 kHz phone audio; artifacts >4 kHz are destroyed. | CodecFake+ + on-the-fly G.711/Opus aug |
| 3 | **Indic language diversity** | Your differentiator + fairness. | IndicSynth multi-language |
| 4 | **Speaker independence (real∩fake)** | Prevents the model learning *speakers* instead of *synthesis*. | Speaker-disjoint splits |
| 5 | **Accent / rural diversity** | Fairness (your Telugu/Hindi FP weakness). | Rural_Women subset, Lahaja, Svarah |
| 6 | **Real-speaker diversity** | Needed for a solid "real" class, but you already have plenty. | *Diminishing returns — don't over-invest* |
| 7 | **Cross-dataset OOD** | Honest generalization number. | Hold out whole datasets |
| 8 | **Raw quantity** | Lowest priority. 200 GB of redundant read-speech ≈ useless. | Cap real speech |

**Core principle: value = Indic × generator-diversity × codec-diversity × speaker-diversity × telephony-relevance PER GB.** A 43 GB diffusion-fake set (DFADD) beats 200 GB of extra clean read-speech.

---

## 2. Is 800 GB enough? (storage reality)

**Yes — comfortably, and you should NOT use all of it.** Realistic budget:

| Bucket | Need |
|---|---|
| Raw datasets (new) | ~550 GB |
| Existing SSD datasets | ~129 GB (already there) |
| HF cache (`~/.cache/huggingface`) during download | up to ~1× the biggest single file; **set `HF_HUB_ENABLE_HF_TRANSFER` off, use `--local-dir` to avoid double-storing** |
| CodecFake+ extraction overhead (.xz → wav) | ~1.5–2× its 100 GB during unpack = transient +100–150 GB |
| Manifests + metadata | < 2 GB |
| Cached features (optional, only if you precompute) | 20–50 GB |
| Checkpoints / experiments | 20–40 GB |
| **Safety buffer** | **≥ 150 GB** |

**Verdict: target ~550 GB of raw datasets, leaving ~250 GB free.** The CodecFake+ extraction transient is the tightest moment — extract it *first* while the disk is emptiest, or extract to a location you clean up after converting to manifests.

---

## 3. Challenge of your proposed allocation

Your draft (≈779 GB) — my verdict on each line:

| Your line | Verdict | Reason |
|---|---|---|
| IndicSynth ~220 GB | **↑ INCREASE to ~300 GB** | Highest value/GB (multi-cloner Indic fakes). This IS the moat. |
| IndicVoices ~170 GB | **↓ REDUCE to ~80 GB** | You need *enough* real, not 170 GB. Redundant with existing + IndicVoices-R. |
| IndicVoices-R ~120 GB | **✂ CUT to 0 (or ~40 GB)** | It's TTS-grade real — overlaps IndicVoices. 120 GB of a 1 TB set = arbitrary 12% slice with unclear speaker coverage. Low marginal value. |
| Rural_Women ~127 GB | **↓ REDUCE to ~20 GB subset** | It's a **fairness TEST set**, not bulk training. 127 GB is wildly oversized for that role. |
| Indic-CodecFake ~80 GB | **✂ REMOVE** | **NOT FOUND on HF** — cannot download. Reallocate its 80 GB. |
| CodecFake+ ~60 GB | **↑ take FULL 100 GB** | Unique codec diversity — the single best telephony-relevance/GB. Don't truncate it. |
| Lahaja 1.4, indicvoices-cleaned 0.4 | **✓ KEEP** | Cheap, high-value fairness/quick-start. |
| MLAAD (you asked) | **✓ ADD (35 GB)** | Cross-lingual fake eval incl. Indic — great OOD test. |
| BanglaFake (you asked) | **✓ ADD if verified (~5 GB)** | Real Bengali fakes — rare, cheap. |
| — | **✚ ADD DFADD (43 GB)** | Diffusion/flow-matching fakes — the modern class you lack. |

---

## 4. The recommended ≤800 GB corpus

| Dataset | Local GB | Role | Real/Fake | Languages | Main contribution | Why this amount | Priority |
|---|---|---|---|---|---|---|---|
| **IndicSynth** (Hi+Bn+Mr+Te+Ml) | **246** | TRAIN | Fake | 5 Indic | Multi-cloner (XTTS+VITS+FreeVC) Indic fakes — the moat | Language breadth over the giant Tamil/Sanskrit; avoids 148 GB Tamil | P0 |
| **CodecFake+** (full) | **100** | TRAIN | Both | English+ | 30+ neural codecs — telephony/codec diversity | Unique per-GB; don't truncate | P0 |
| **DFADD** | **43** | TRAIN | Fake | English | Diffusion + flow-matching fakes | Modern attack class you lack | P0 |
| **IndicVoices** (5 langs subset) | **80** | TRAIN | Real | 5 Indic | Real Indic class, natural speech | Enough for balance, not bulk | P1 |
| **MLAAD** (Indic + sample) | **35** | OOD-TEST | Fake | 40+ | Cross-lingual fake generalization | Held out from training | P1 |
| **Rural_Women** (subset) | **20** | TEST/fairness | Real | Indic rural | Accent/fairness eval | Test-only, small slice | P1 |
| **BanglaFake** [verify] | **~5** | TRAIN/test | Both | Bengali | Real Bengali fakes | Cheap, rare | P2 |
| **Lahaja + Svarah + indicvoices-cleaned** | **~3** | TEST | Real | Hi/IndEng | Accent + quick-start | Cheap fairness | P2 |
| **AI4Bharat + general TTS models** | **~25** | TOOLING | — | Indic+multi | Generate NEW fakes (IndicF5, parler, vits, XTTS, F5, Fish, MaskGCT) | The moat corpus generator | P0 |
| **(existing SSD sets)** | (129) | mixed | — | EN+Indic | ITW/ASVspoof19/WaveFake/etc. | already present | keep |
| **NEW TOTAL** | **~557 GB** | | | | | leaves ~245 GB free | |

Optional add if you want the English cross-dataset number: **ASVspoof5 (142 GB)** → ~699 GB new, still <800.

### CORE TRAINING DATA
IndicSynth (5 langs) + CodecFake+ + DFADD + IndicVoices (subset) + BanglaFake + your existing WaveFake/ASVspoof19/ITW. Plus **fakes you generate** from the TTS models.

### VALIDATION DATA
A **held-out slice of IndicSynth languages' speakers** (speaker-disjoint) + a held-out generator (see §5).

### INTERNAL TEST (never touched in training)
ITW (your current benchmark), a speaker-disjoint Indic slice, Rural_Women/Lahaja/Svarah (fairness).

### OOD DATA (stream / external, generalization only)
MLAAD, ASVspoof5, CVoiceFake (stream `_small`), IndicVoices-R (stream) — never trained on.

---

## 5. Data-leakage & split strategy (the most important section)

VoxShield must be evaluated under **four simultaneous disjointness constraints**:

1. **Speaker-disjoint** — no speaker in both train and test. *Critical:* IndicSynth fakes are cloned from IndicVoices speakers → if a speaker's real clip is in train and their cloned fake is in test, that's leakage. **Rule: partition by speaker ID first, then assign both their real and fake clips to the same split.**
2. **Generator-disjoint** — hold out ≥1 entire TTS/VC engine from training and test on it. E.g., **train on IndicSynth-VITS + IndicSynth-FreeVC, test on IndicSynth-XTTS** (and vice-versa). This is your cross-generator EER — the number that proves real-world skill.
3. **Source-dataset-disjoint** — train on IndicSynth+CodecFake+, test on MLAAD (different pipeline entirely). Cross-dataset generalization.
4. **Codec-disjoint** — hold out ≥1 codec (e.g., train on G.711+Opus, test on AMR-WB) to measure codec generalization.

**Concrete recommended split:**
- Train: 70% speakers × {VITS, FreeVC fakes} × {clean, G.711, Opus} + CodecFake+ + DFADD.
- Val: 15% speakers (disjoint) × same generators.
- Internal test: 15% speakers (disjoint) × **XTTS fakes held out** (generator-disjoint) × **AMR-WB held out** (codec-disjoint).
- OOD test: MLAAD + ASVspoof5 (source-disjoint), never seen.

**Yes — a model trained on IndicSynth-XTTS SHOULD be tested on a different generator entirely.** And yes, speakers shared between real and fake sets create leakage — enforce speaker-level partitioning before anything else.

---

## 6. Telephony layer — generate on-the-fly, do NOT store copies

**Decision: on-the-fly augmentation at dataloader time. Store only RAW + manifests + deterministic seeds.**

Reasoning: storing `RAW → 8kHz → noisy → codec → augmented` as 5 copies of a 550 GB corpus = **2.7 TB** — impossible on 1 TB. Instead:
- One raw copy on disk.
- `telephony_aug.py`-style transforms applied in the `Dataset.__getitem__` (you already have this pattern from the DGX work): G.711 μ-law 8 kHz roundtrip, telephony band-pass 300–3400 Hz, additive noise (SNR 5–30 dB), Opus/AMR simulation, mild reverb, packet-loss dropouts, clipping.
- **Deterministic seed per (clip_id, epoch)** so augmentations are reproducible for eval but varied for training.
- Cache **features** (not augmented audio) only if a specific experiment reuses them heavily — and cap the feature cache at ~30–50 GB.

Storage implication: **~0 GB extra** for telephony (vs +2 TB if stored). This is the single biggest storage win.

---

## 7. Filesystem / data architecture (no redundant copies)

```
/Volumes/KIOXIA/voxdata/
  raw/            # one immutable copy per dataset (parquet or wav)
  manifests/      # CSV: path,label,speaker,lang,generator,codec,split  ← the source of truth
  models/         # TTS engines for generating new fakes
  generated/      # fakes YOU synthesize (multi-engine Indic corpus)
  features_cache/ # optional, capped, gitignored
  # NO noisy/ 8khz/ augmented/ dirs — those are runtime-only
```
Manifests carry every attribute (speaker, lang, generator, codec) so splits are just manifest filters. Augmentation is lazy. This keeps the whole thing under ~600 GB on disk.

---

## 8. Download vs stream (per dataset)

| Dataset | Decision | Why |
|---|---|---|
| IndicSynth (5 langs) | 🟡 **DOWNLOAD CURATED SUBSET** | Parquet, per-language dirs — subset with `--include "Hindi/*"` etc. Full 845 GB won't fit. |
| CodecFake+ | 🟢 **DOWNLOAD FULL** | Split `.xz` archive — not streamable, must extract. Unique value. |
| DFADD | 🟢 **DOWNLOAD FULL** | 43 GB, parquet+zip, small enough. |
| IndicVoices (train) | 🟡 **DOWNLOAD SUBSET** (5 langs) | 744 GB full is overkill; subset for real class. |
| MLAAD | 🟡 **DOWNLOAD SUBSET** (Indic + sample) | 99k loose wavs; grab Indic language folders only. |
| Rural_Women | 🟡 **DOWNLOAD SUBSET** | Fairness test only — small slice. |
| BanglaFake | 🟢 DOWNLOAD (if verified) | Small. |
| Lahaja/Svarah/cleaned | 🟢 DOWNLOAD FULL | Tiny. |
| IndicVoices-R | 🔵 **STREAM** | 1 TB — stream via `load_dataset(..., streaming=True)` for occasional OOD eval; never store. |
| ASVspoof5 | 🔵 STREAM or 🟡 subset | 142 GB — optional; stream for OOD or download if you want the English number. |
| CVoiceFake / ST-Codecfake | 🔵 STREAM small / Zenodo | Only `_small` on HF; full on Zenodo. |
| Indic-CodecFake | 🔴 **DO NOT USE (yet)** | NOT FOUND on HF — monitor for release. |

**HF streaming reality:** works well for the **parquet** datasets (IndicSynth, IndicVoices, IndicVoices-R, DFADD) via `datasets.load_dataset(id, streaming=True)`. Does NOT work for CodecFake+ (split archive) or cleanly for MLAAD's 99k loose files. So: download the parquet subsets you train on; stream the parquet giants you only eval on.

---

## 9. Alternatives found (better per-GB than some candidates)

- **DFADD (43 GB)** — add; fills the diffusion/flow-matching gap. Higher value than another 43 GB of real speech.
- **ASVspoof5 (142 GB)** — best English cross-dataset OOD; optional.
- **AI4Bharat TTS models (~25 GB total)** — highest strategic value: let you *generate unlimited multi-engine Indic fakes*, which no downloadable dataset gives you. **This replaces the need for Indic-CodecFake** (which isn't downloadable): generate codec fakes yourself by running IndicF5/parler/vits outputs through neural codecs.
- **Skip:** IndicVoices-R as a download (stream instead), most of Rural_Women (subset only), full IndicVoices (subset only).

---

## 10. Final decision

**A. RECOMMENDED ~557 GB PLAN** — table in §4. Leaves ~245 GB free (extraction buffer + processing + checkpoints).

**B. DOWNLOAD:** IndicSynth (Hi+Bn+Mr+Te+Ml, ~246 GB) · CodecFake+ (100) · DFADD (43) · IndicVoices (5-lang subset, ~80) · MLAAD (Indic subset, ~35) · Rural_Women (subset ~20) · BanglaFake (~5) · Lahaja+Svarah+cleaned (~3) · TTS models (~25).

**C. STREAM:** IndicVoices-R · ASVspoof5 (or subset-download) · CVoiceFake_small · (IndicVoices full for extra langs).

**D. IGNORE:** Indic-CodecFake (NOT FOUND) · full IndicVoices-R download · full Rural_Women · SpoofCeleb (institutional-gated) · ST-Codecfake (unless you want the Zenodo pull).

**E. EXPECTED STORAGE:** raw new ~557 GB + existing 129 GB = 686 GB used; +transient extraction ~100 GB (CodecFake+, cleaned after) ; manifests <2 GB; feature cache ≤50 GB (optional); checkpoints ~30 GB; **safety buffer ~150 GB.** Peak during CodecFake+ extraction is the tight point — do it first.

**F. WHY THIS BEATS "download all 2–3 TB":** it maximizes *generator + codec + language diversity per GB* instead of piling up redundant real read-speech. Cross-generator generalization (your weakest, most important axis) is driven by attack diversity, not clip count. The on-the-fly telephony layer adds infinite channel variation at zero storage. Generating your own multi-engine fakes gives coverage no fixed dataset has.

**G. RISKS:**
- **Generator leakage** — IndicSynth is 3 engines; without generator-holdout you'll overfit to them. *Mitigate:* §5 generator-disjoint split + self-generated engines.
- **Speaker leakage** — real (IndicVoices) speakers cloned into IndicSynth fakes. *Mitigate:* speaker-level partition first.
- **Language imbalance** — Sanskrit/Tamil dominate IndicSynth by size; your target Hi/Ta/Bn may be under-weighted. *Mitigate:* balance by clip count, not GB; weighted sampler.
- **Domain/telephony mismatch** — IndicSynth is studio-quality; real fraud is phone. *Mitigate:* on-the-fly G.711/Opus aug (mandatory).
- **License** — IndicSynth is **CC BY-NC 4.0 (non-commercial)**; fine for research/benchmark, but a commercial product cannot ship a model trained on it without clearing rights. *Flag for the business plan.*
- **Synthetic-artifact overfit** — training only on TTS fakes may miss real replay/VC attacks. *Mitigate:* include VC (FreeVC in IndicSynth) + real-world ITW.
- **Overfitting to IndicSynth** — it's one lab's pipeline. *Mitigate:* MLAAD/ASVspoof5 as source-disjoint OOD tests.

**H. NEXT ACTIONS (implementation, in order):**
1. **Verify** BanglaFake (`sifat1221/banglaFake`) size/license; confirm IndicSynth per-language speaker metadata exists for speaker-disjoint splitting.
2. **Storage prep** — create the `raw/ manifests/ models/ generated/` tree; confirm ≥250 GB stays free.
3. **Download** in order: CodecFake+ first (extract while disk emptiest) → DFADD → IndicSynth 5-lang subset → IndicVoices 5-lang subset → MLAAD Indic → small sets → TTS models.
4. **Subset selection** — per-language `--include` for IndicSynth/IndicVoices; Indic folders for MLAAD.
5. **Manifests** — build unified CSV (path,label,speaker,lang,generator,codec) across all sets.
6. **Deduplication** — hash-based dedup within/across sets; check IndicSynth-vs-IndicVoices speaker overlap.
7. **Splitting** — speaker-disjoint + generator-holdout (XTTS) + codec-holdout (AMR-WB) + dataset-holdout (MLAAD/ASVspoof5).
8. **Telephony aug** — wire on-the-fly G.711/Opus/noise/packet-loss into the dataloader (extend existing `telephony_aug.py`).
9. **Baseline training** — XLSR fine-tune on the multi-engine Indic corpus (needs DGX GPU).
10. **Evaluation** — cross-generator, per-language, codec-matrix, OOD, with bootstrap CIs.

---

*Storage figures verified via HF API 2026-09-14. IndicSynth per-language GB and the split archive nature of CodecFake+ were confirmed from file listings. Indic-CodecFake absence confirmed via HF dataset search returning no match.*

Research and allocation plan complete. I have NOT downloaded or modified anything. Do you give me permission to execute the recommended VoxShield 800-GB dataset setup?
