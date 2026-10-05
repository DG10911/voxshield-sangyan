# VoxShield — Master Status: what's DONE, what's LEFT
_Updated 2026-10-05. Single ledger across science, data, backend, frontend, docs, GPU._

## ✅ DONE

### Science & evaluation
- **12 Indic languages two-class validated** (pa te mr sa hi kn ta gu bn ur or ml).
- Ensemble + fusion + calibration + selective abstention implemented and measured.
- Full eval suite: **C1 per-language · C2 ablation · C3 abstention · C4 generalization-gap** →
  `results/report_all_norm.txt`, `phase2/report_all.txt`, `scores_all.csv` (224,716 rows).
- Headline: overall EER **10.25%** · seen **9.57%** · unseen **19.00%** · gap **+9.43** ·
  clean→G.711 9.24→11.41 (**+2.17**) · ECE **0.058** · Cllr **1.010** · AURC **0.0273** ·
  abstain-20% false-alarm **2.55% → 0.23% (−91%)**.

### Phase 4 (GPU, done)
- **12 languages × 3 backends trained**: `aasist_*`, `adv_*` (PGD), `student_*` (distilled).
- **C2 ablations written**: `phase4/c2_*.txt` (12 files).
- (4 GPUs were still busy at last check — verify the tail: `tmux ls | grep vox`.)

### Data & corpus
- IndicVoices real audio for 12 eval langs (+ konkani, kashmiri, bodo, dogri).
- Spoof corpora for the 12 (IndicSynth freevc24 + MMS/vits/xtts unseen).
- AIKosh/HF catalogue mapped (124 datasets / 94 models).

### Backend / API
- **15 FastAPI routes** (health, analyze+**mel-spectrogram**, stream, ws, audit, threats, intel,
  risk/score, threat/search, gateway/decide, consumer/check, deployment/profile, warroom,
  speaker/verify).
- **Bhashini/ULCA adapter implemented** (MOCK + LIVE) — ASR/TTS/NMT/translit/ALD/TLD; keys present
  in `~/.config/voxshield.env` (user/api/inference). Live smoke scripts exist.
- 9 evidence brains; LCNN/Conformer/AASIST backends; distillation; adversarial training.

### Frontend
- **17-screen React console** (Codex-generated) — integrated, served at `/voxshield/`.
- **Mel-spectrogram on all 6 audio surfaces** (Analyze staging + result, Live, Products, Speakers,
  Calls drawer); QA: **17/17 screens, 0 errors, nav 17/17, ⌘K works, tests 8/8**.
- **Single all-numbers digest** dashboard → `voxshield_numbers.html`.

### Docs & assets
- `VOXSHIELD_PRIOR_ART.md`, `VOXSHIELD_PAPER_DRAFT.md`, `VOXSHIELD_RESULTS.md`,
  `VOXSHIELD_ALL_NUMBERS.md`, `VOXSHIELD_SYSTEM_OVERVIEW.md`, `VOXSHIELD_STATUS.md`,
  `VOXSHIELD_UI_SPEC.md`, `VOXSHIELD_UI_PROMPT.md`, Bhashini integration + service-IDs + support email.
- `SANGYAN_VoxShield.pptx` (10 slides), `SANGYAN_VoxShield_demo.mp4` (3:22),
  `VOXSHIELD_film.mp4` (4:30), `VOXSHIELD_film_v2.mp4` (2:30), launch site.
- Public repo: `github.com/DG10911/voxshield-sangyan`.

## ⛔ LEFT / BLOCKED

### 1. Low-resource languages (8) — BLOCKED on TTS
Target: give `bodo dogri kashmiri konkani manipuri nepali santali sindhi` a real spoof set so they
become two-class (23/23).

**Blocker:** **MMS-TTS has no voices for them.** Verified `facebook/mms-tts-<code>`:
- exists: `asm` (Assamese), `mai` (Maithili)
- missing (401): `brx doi kas kok mni npi sat snd`

Consequences:
- Only **Assamese + Maithili** can use MMS.
- **Nepali (300)** and **Maithili (300)** fakes already exist (from an earlier engine).
- Codec-fake (`gen_codecfake.py`) measured **≈chance EER (~50%)** → not usable as detection.
- GPUs 1–3 are **free** (0 MiB); disk has **6.4 TB** free.

**Unblock paths (need a decision):**
- **C1 — Indic-TTS / IndicF5 (AI4Bharat, open weights, local)** for the missing 7 — best licensed,
  offline, no API terms. Highest effort.
- **C2 — Indic-Parler-TTS** — previously blocked by CUDA device-side assert on this stack.
- **C3 — accept 12 (or 14) languages**, mark the rest as genuine-only / future work (honest).

### 2. Paper write-up
- Results + Discussion sections not yet written from `report_all_norm.txt`.
- **C2 ablation numbers** (`phase4/c2_*.txt`) not yet folded into the paper.

### 3. Bhashini live verification
- Adapter + keys exist; **end-to-end live smoke not yet confirmed** (`bhashini_livetest.py`).

### 4. Submission
- Upload video demo + pptx on the SANGYAN form (assets ready).
- Fix UI label: **"Seen EER 1.62%"** → clarify *seen (freevc24) 1.62% vs seen aggregate 9.57%*.

## Next actions (suggested order)
1. Decide low-res path (C1/C2/C3).
2. Write paper Results/Discussion + fold in `c2_*.txt`.
3. Run Bhashini live smoke → record pass/fail.
4. Submit (video + deck) and apply the EER-label fix.
