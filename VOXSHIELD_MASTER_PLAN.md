# VoxShield — Executable Master Engineering & Research Plan

*From the consolidated "Voice Trust Infrastructure" vision → what actually exists → gaps → the highest-value increments, built incrementally without breaking the current system.*

Status labels used throughout: **[IMPLEMENTED]** (in-repo, runs) · **[PROJECT RESULT]** (measured internally) · **[PARTIAL]** · **[PROPOSED]** · **[HYPOTHESIS]** (needs experimental validation) · **[TARGET]**.

---

## 0. Honest framing
The two source documents describe a ~100-component **research platform** (OmniSense, 12–19 "brains", Generator Hunter, Threat Registry, Human-Physics Engine, etc.). That is a multi-year target, **not** the current system. This plan does **not** pretend those are built. It maps the vision onto the real repo, then advances the pieces with the best value-to-risk-to-effort ratio **without breaking System A** (the deployed fusion) or the honest evaluation discipline.

## 1. What actually exists today (repo audit — grounded)
| Component | File(s) | Status |
|---|---|---|
| Streaming pipeline (8 kHz G.711 → VAD → 3s/1s → 16 kHz) | `backend/features.py`, `app.py` | **[IMPLEMENTED]** |
| 89-dim feature bank (LFCC, CQCC, group-delay phase, F0, jitter, shimmer, >6 kHz @16 kHz analysis) | `backend/features.py` | **[IMPLEMENTED]** |
| Detector bank (Acoustic DSP · wav2vec2 · XLS-R-53 · DistilHuBERT · LFCC+CQCC head) | `backend/detector.py`, `models.py` | **[IMPLEMENTED]** (3 are off-the-shelf HF — see `voxshield-real-stack` memory) |
| Learned fusion + Platt calibration + reason codes + verdict | `backend/fusion.py`, `metrics.py`, `artifacts/fusion_head.json`,`calibrator.json` | **[IMPLEMENTED]** |
| Indic / telephony / general routing (`_meta`, `_meta_indic`, `_meta_narrowband`) | routing logic | **[PARTIAL]** |
| Telephony augmentation (G.711 μ-law, band-limit, noise) | `backend/augment.py`, `telephony_aug.py` | **[IMPLEMENTED]** |
| Multi-dataset trainer (System B, XLS-R fine-tune) | `backend/pipeline/train_corpus.py` | **[IMPLEMENTED]**, leakage-fixed v2 |
| Speaker-disjoint eval | `backend/eval_speakerdisjoint.py` | **[PARTIAL]** |
| **VoxScore meta-uncertainty layer** (this pass) | `backend/voxscore.py` | **[IMPLEMENTED]** (heuristic dims **[HYPOTHESIS]**) |

**Measured evidence [PROJECT RESULT]:** deployed fusion 5.9% EER (held-out ITW); **6.8% EER / 0.98 AUC on unseen-generator OOD (MLAAD)** — the honest cross-generator number; detector scoreboard 16.0/19.1/5.9; Indic recall 42→82%; genuine-Indic FP 11.7→6.3%. (In-corpus ~0% is corpus-provenance leakage — never cite.)

## 2. The one thing to optimize (the vision's own #1 principle)
> "Do not build VoxShield to recognize yesterday's fake … optimize for the attack nobody has seen before."

Concretely = **the Generalization Gap** (known-generator EER − unseen-generator EER) and **open-set behavior** (an unknown input must never silently become "human"). Every increment below is ranked by how much it moves *that*, not known-set accuracy.

## 3. Prioritized roadmap (value ÷ risk ÷ effort)

**P0 — Make uncertainty first-class (started now).**
- `voxscore.py` **[IMPLEMENTED]** — turns the single fused score into `{authenticity, evidence_confidence, distribution_confidence, novelty, risk}` with an **ABSTAIN band**, so ambiguous / detector-disagreeing inputs route to REVIEW instead of a forced class. Directly serves §29/§34/§42/§63. Non-breaking (wraps `fusion.analyze()`).
- Next: wire `voxscore.from_analyze()` into `app.py`'s JSON response as an additive field (no change to existing fields).

**P1 — Measure what matters: a generalization-gap harness. [PROPOSED, highest ROI]**
- A `backend/eval_gengap.py` that ingests a scores CSV `(label, score, generator, language, channel)` and reports **per-generator / per-language EER**, the **leave-one-generator-out** gap, and calibration (ECE/Brier). Turns the vision's "Master Evaluation Matrix" (§92) into one runnable report. Pure measurement → zero risk to production.
- Validates whether `voxscore`'s heuristic novelty actually correlates with unseen-generator inputs (the **[HYPOTHESIS]** → **[PROJECT RESULT]** promotion gate).

**P2 — Frozen Golden Set + Zero-Day Set discipline. [PROPOSED]**
- Define `data/golden/` (never trained on) + `data/zeroday/` (refreshed with held-out generators/languages). Every checkpoint reports both. This is governance, not modeling — cheap, and it's the backbone of honest claims (§70–71).

**P3 — Evidence diversity, for real. [HYPOTHESIS → experiment]**
- Today `evidence_confidence` uses detector-family agreement as a proxy. Replace with a measured inter-detector error-correlation study (are the 5 detectors actually independent, or all SSL-correlated?). Result decides whether "5 detectors" is 5 evidence streams or ~2. Honest, and it directly grounds HEDS (§29/§37).

**P4 — One new *independent* evidence stream (not another SSL model).**
- The current bank is SSL-heavy. The vision's highest-signal, buildable additions are **phase-trajectory** (§18) and **breath/physiology** (§15) forensics — genuinely different physics from SSL embeddings. Prototype **one** (phase-trajectory topology), evaluate its *marginal* contribution to the OOD gap. Only keep it if it lowers unseen-generator EER.

**P5 — Governed data flywheel scaffold. [PROPOSED]**
- Unknown-Vault directory + metadata schema (§39/§76) + the quarantine→validate→challenger→golden→shadow flow (§69). Build the *pipeline scaffolding and schema* now (cheap, non-breaking); defer live-traffic ingestion until consent/privacy is real.

**Deferred (correctly, not now):** Generator Hunter, Threat Registry/Graph, BotGuard, audio-visual, device/environment matrices, telephony gateway, consumer app. All are real long-term items; none is the current bottleneck (the OOD gap is).

## 4. What I implemented this pass
`backend/voxscore.py` (+ self-test, passing):
- Consumes `fusion.analyze()`'s `per_model` + `score` with **zero changes to existing files**.
- Emits the multi-dimensional VoxScore and, crucially, **abstains** (`risk=REVIEW`) when detectors disagree or the input is ambiguous — verified by the self-test's "zero-day-like" case (score 0.70 but novelty 0.48 → REVIEW, not HIGH).
- **Honest labels baked in:** `authenticity` is grounded in trained detectors; `evidence_confidence / distribution_confidence / novelty` are **agreement-based heuristics [HYPOTHESIS]**, explicitly flagged in the module and required to be validated against a real open-set benchmark (P1) before any public claim.

Run it: `python3 backend/voxscore.py`

## 5. Do-NOT list (from the vision's own warnings + this repo's reality)
- Do **not** cite the in-corpus ~0% EER — it's provenance leakage.
- Do **not** claim the heuristic novelty/evidence dims are validated until P1 shows they track unseen-generator inputs.
- Do **not** auto-block on an uncertain score — REVIEW/step-up only (encoded in the abstain band).
- Do **not** let live traffic rewrite production; the flywheel stays governed (P5).
- Do **not** treat unusual humans as synthetic — P2's Golden Set must include the "worst human" cases (§43).
- Do **not** claim NPU/latency numbers until measured (see Snapdragon submission).

## 6. Next three concrete steps (in order)
1. **Wire `voxscore` into `app.py`** as an additive `voxscore` field in the response (non-breaking) + surface `risk=REVIEW` in the console UI.
2. **Build `eval_gengap.py`** and run it on the System-B scores to publish the first real per-generator/per-language generalization-gap table.
3. **Validate the novelty heuristic** against MLAAD-unseen vs in-corpus: does `novelty` rise on unseen generators? If yes → promote to [PROJECT RESULT]; if no → replace with an embedding-distance open-set score.
