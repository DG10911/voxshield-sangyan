# VoxShield — Deep-Research Findings & Improvement Plan (2026-10)

## A · TTS coverage for the 8 "low-resource" languages — SOLVED
Earlier I wrongly concluded no TTS existed (I had only checked MMS). Verified options that cover
**all 8**:

| Model | Languages | Notes |
|---|---|---|
| **Indic-Parler-TTS** (`ai4bharat/indic-parler-tts`) | officially: **Bodo, Dogri, Konkani, Manipuri, Santali, Sindhi, Nepali** (+18 more); **Kashmiri** unofficial | already installed; **our tokenizer fix makes it run**; used now |
| **DhVaani-0.5** (ARTPARK-IISc) | **27 Indian langs** incl. Dogri, Kashmiri, Konkani, Manipuri, Santali, Sindhi, Bodo | Apache-2.0, zero-shot, 24 kHz |
| **SPRING_F5** (SPRINGLab) | **23 langs** incl. Dogri, Kashmiri, Konkani, Manipuri, Santali, Sindhi | F5-TTS fine-tune |
| **Indic-Mio** (SPRINGLab) | all 22 scheduled | 44 kHz, LoRA-friendly |
| **AIKosh / IndicTTS Phase-3** | **hosted Bodo, Dogri, Konkani, Manipuri voices** (CC-BY-4.0) | provenance ids in `VOXSHIELD_AIKOSH.md` |
| MMS-TTS | only Assamese, Maithili | (the earlier dead end) |

**Action taken:** all 8 low-res languages queued through Indic-Parler on GPUs 1–3
(ks/ne/sd running; bodo/dogri/konkani/manipuri/santali chained in wave-2).

## B · Reducing EER to single digit — the 2026 levers
Ordered by expected impact on our weak languages (ur 17.9, or 34.1, ml 36.3):

1. **Language Orthogonalization** (arXiv:2609.16458) — remove language-dependent structure from
   SSL features with a target-free map; consistently lowers EER on unseen languages, larger gains
   for distant transfers. **Implemented:** `backend/language_orthogonalization.py` (self-test PASS).
2. **XLS-R-300M + AASIST + RawBoost** — de-facto SOTA recipe (we have RawBoost in `augment.py`).
3. **Layer-wise decision fusion** (arXiv:2607.20023) — ITW 6.90% EER; avoids feature collapse.
4. **SpAArSIST** (arXiv:2606.11674) — simplified AASIST backend, ITW EER 4.64% → **2.82%**.
5. **Longer segments** (4s → 12s) — +30% on processed-audio tasks (SAFE Challenge, arXiv:2508.20983).
6. **WavLM-Large + RawBoost** front-end (SAFE 2nd/3rd place) — strong complement to XLS-R.
7. **Test-time LoRA / GP few-shot** — already on our roadmap for low-res adaptation.

## C · What this means for "all languages, single-digit EER"
- **All languages:** achievable — Indic-Parler covers all 8 low-res; total → **~20–23 languages**.
- **Single-digit EER:** 9/12 done. ur/or/ml need items B1–B5. B1 is now implemented; B2/B3 are
  drop-in to the existing XLS-R/AASIST training path. Realistic, not guaranteed for ml.

## D · Roadmap deltas (from `VOXSHIELD_ROADMAP.md`)
- `[PARK-GPU]` XLS-R+SLS · RawBoost · AASIST3 — **unpark**: AASIST trained; add SLS + orthogonalization.
- `[TODO-DATA]` RTCFake, IndicFake — still pending external download.
- `[TODO]` AIKosh provenance entries (Fastspeech2, Indic-Parler, IndicF5, Sooktam2, …) — to add.
- `[PARK]` P2/P3 external-resource items unchanged (India corpus, telephony lab, deployment packaging).
