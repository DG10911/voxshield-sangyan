# VoxShield · RAKSHAM Round-1 — Judge Prep (companion, NOT part of the submitted PDF)

Track 01 — Voice Cloning Fraud Detection. Team DigiSeva.
This doc backs the 21-page submission PDF (`VOXSHIELD_RAKSHAM_SUBMISSION.pdf` = 10 pitch + 3 architecture + 8 appendix). Reviewers score only the PDF; this is our internal prep.

> **Metric note:** the deck uses the honest, artifact-backed genuine-Indic false-positive figure **11.7% → 6.3%**. The RAKSHAM prompt template asked for **36.3% → 6.3%**. These likely measure different stages (raw vs channel-aware) and the discrepancy is unresolved. To switch the whole deck, set `GENUINE_FP_BEFORE = "36.3%"` in `backend/pipeline/make_raksham_deck.py` and rebuild. **Confirm the correct figure before final submission.**

---

## 1. Ruthless judge review (IIT Delhi + Amazon panel simulation)

| # | Panel question | Our honest answer | Where in PDF |
|---|---|---|---|
| 1 | Is this actually solving Problem 01? | Yes — voice-clone fraud inside banking/payment calls, not generic deepfakes. | S1, S3, S8 |
| 2 | Is the user specific? | Yes — bank/NBFC fraud-ops analyst (primary), not "everyone". | S2 |
| 3 | Is the threat scenario realistic? | Yes — cloned bank-official/relative call pushing a transfer/OTP over PSTN. | S1, S2 |
| 4 | Is the architecture technically defensible? | Yes — streaming 5-detector fusion + calibration + routing, drawn end-to-end with trust boundaries. | S5, A-1/2/3 |
| 5 | Is the detector logic understandable? | Yes — pipeline + 89-dim feature bank + fusion, one legible flow. | S5, App A1 |
| 6 | Are the results credible? | Measured, scoped, labelled "not independently validated"; fusion beats best-single and naive-avg. | S6, App A4 |
| 7 | Are limitations acknowledged? | Yes — EER≠accuracy, in-domain-optimism, no full adversarial robustness, contextual signals are mocks. | S6, A-3, App A5 |
| 8 | Could this be built in 48h? | Yes — narrow MVP with hour-by-hour plan + demo proof per stage. | S9, App A8 |
| 9 | Is the MVP narrow enough? | Yes — one live call → verdict → evidence → safe action; nice-to-haves explicitly deferred. | S9 |
| 10 | Does it fail safely? | Yes — LOW/REVIEW/HIGH, never auto-blocks/accuses. | S7, A-3 |
| 11 | What happens when the model is wrong? | FP → verification not block; FN → ensemble+drift+unseen-gen eval. | S7, App A5 |
| 12 | How does privacy work? | On-prem/air-gapped, data minimisation, least-data logging, encryption, RBAC, audit, retention/deletion. | A-3 |
| 13 | What data is collected? | Call audio frames + minimal metadata under authorisation; raw audio not exported. | A-3 |
| 14 | Who can see it? | Role-based, logged access by authorised fraud-ops only. | A-3 |
| 15 | Can an attacker adapt? | Yes — we assume it; ensemble diversity, unseen-gen eval, adversarial sets, drift, liveness (proposed). | App A6 |
| 16 | Can a genuine customer be harmed? | Mitigated — no auto-block; per-language fairness tracked; REVIEW adds verification. | S7, App A5 |
| 17 | Human escalation path? | REVIEW→step-up; HIGH→authorised human; human approves any high-impact action. | S7, A-2 |
| 18 | What is implemented today? | TRL-5 fusion system, streaming, calibration, telephony hardening, measured evals. | S6, credibility audit |
| 19 | What must be built at finale? | Live console demo, workflow wiring, liveness stub, benchmark readout. | S9, App A8 |
| 20 | Why more than "another deepfake detector"? | It's a safe financial-risk workflow: telephony+Indic+streaming+fusion+explainable+safe-escalation. | S4, S10 |

**Weaknesses found → fixes applied:** (a) generic "AI detector" framing → reframed as risk-workflow (S4/S10); (b) unscoped metrics → added scope + caveats + "not validated" (S6); (c) privacy hand-waving → concrete collect/process/retain/access table (A-3); (d) 48h over-scope risk → explicit MUST/NICE split + fallback (S9); (e) contextual-signal overclaim → labelled future/mock (A-2).

---

## 2. Credibility audit

| Claim | Source | Status | Evidence |
|---|---|---|---|
| 5.9% EER, AUC 0.983, ECE 0.044 | held-out In-the-Wild (800-clip) | PROJECT RESULT | meta_eval.json / calibration.json |
| Fusion > best-single (16.0%) > naive-avg (19.1%) | same eval set | PROJECT RESULT | meta_scores.csv |
| Indic recall 42%→82% | MMS-TTS Indic eval | PROJECT RESULT | lang_report.json |
| Genuine-Indic FP 11.7%→6.3% | channel-aware Indic eval | PROJECT RESULT (⚠ 36.3% variant unresolved) | lang_report.json |
| G.711 codec cost ≈1.6 pts | cross-dataset telephony run | PROJECT RESULT | telephony run (garystafford 11.1→12.2) |
| <1 s latency, ~4.3M calls/day/GPU | single-GPU inference | PROJECT RESULT / est. | inference bench |
| On-prem / air-gapped deploy | design | IMPLEMENTED (design) | FastAPI service, no egress |
| Streaming 3s/1s, VAD, routing | pipeline | IMPLEMENTED | fusion.py router |
| Liveness / anti-replay | roadmap | PROPOSED | not yet built |
| Authorised contextual signals | roadmap | PROPOSED / MOCK | not integrated |
| Edge/NPU quantised inference | roadmap | TARGET | not benchmarked |
| Bank pilot / production / Amazon / IIT-D endorsement | — | NONE (never claimed) | — |

**Never claimed:** bank customers, transaction volume, fraud prevented, production deployment, partnerships, Amazon integration, IIT-D endorsement, regulatory certification, independent validation.

---

## 3. Thirty judge questions & concise answers

1. **Why voice cloning, not generic fraud?** Voice is now a cheap, high-trust attack surface inside live financial interactions; we solve that bounded problem, not all scams.
2. **Why isn't one model enough?** Single detectors are individually evadable and dataset-brittle; fusion of five families removes a single point of failure and beats best-single (16.0%→5.9% EER).
3. **How do you handle false positives?** A score over threshold is never "fraud confirmed" — it becomes a risk state routed to verification/human review; genuine false-alarm rate is tracked per language.
4. **What if a real voice is unusual (illness, emotion)?** That's a REVIEW, not a block — step-up verification protects the genuine customer; we never accuse from a score.
5. **How do you handle Indian accents?** Multilingual XLS-R-53 backbone + Indic routing across 10 languages; Indic fairness is a measured metric, not an assumption.
6. **Code-switching?** SSL backbones are trained on mixed multilingual speech; routing is language-robust, and we flag it as a known evaluation condition.
7. **Replay attacks?** Current defense is ensemble + telephony cues; dedicated liveness/anti-replay is on the roadmap (labelled PROPOSED) — we don't claim it works yet.
8. **Unseen TTS engines?** The real-world test — we hold out generators (cross-generator eval) and maintain adversarial sets; multi-cloner Indic training is in progress.
9. **Noisy calls?** Telephony-aware training helps; full noise/music robustness needs Indic backbone fine-tuning (roadmap) — stated honestly, not overclaimed.
10. **Why 8 kHz?** That's the real bandwidth of G.711 PSTN calls; we detect on the channel fraud actually uses, and measure the ≈1.6-pt codec cost.
11. **Why 3 seconds?** Enough context for reliable synthetic-speech cues while staying low-latency for a mid-call decision.
12. **Why 1-second hop?** Overlapping windows give a fresh verdict every second — a call is flagged within its first seconds.
13. **How quickly can you warn?** <1 s per window on a GPU; effective time-to-warning is a few seconds into the call.
14. **How do you protect raw audio?** Scored inside the authorised on-prem boundary; not exported; least-data logging (hashes/verdicts/reason codes).
15. **Do you store calls?** Not by default — only verdicts/evidence. Raw audio only if an authorised investigation requires it, then encrypted, access-controlled, time-limited, deletable. We do not claim "zero storage".
16. **How do you obtain consent?** Capture happens under the bank's existing customer authorisation/consent and data-use policy; datasets are synthetic/public/consented (VERIFY before submission).
17. **Who receives the alert?** The authorised fraud-ops analyst — with risk state, evidence, and confidence.
18. **Can the bank auto-block a payment?** Not from a VoxShield score. High-impact action always passes through an authorised human.
19. **What happens when the model is wrong?** The core safety design — see #3/#4; the output is evidence for a decision, never the decision.
20. **How does a human verify?** Callback on a known-good number, secondary-channel authentication, or existing KYC step-up.
21. **How do you prevent alert fatigue?** Only REVIEW/HIGH surface; LOW passes silently; thresholds tuned to keep analyst volume manageable.
22. **How do attackers adapt?** New synthesis, replay, short utterances, threshold probing — countered by ensemble diversity, unseen-gen eval, drift detection, rate limiting.
23. **How do you update models?** Secure update mechanism + drift monitoring; on-prem federated updates share gradients only, never audio (roadmap for the flywheel).
24. **How do you prevent model poisoning?** Curated update data with provenance checks; no open ingestion of untrusted samples.
25. **How does this integrate with a bank?** As a risk-event source: audio stream → VoxShield API/SDK → structured risk event → fraud/case-management platform.
26. **What would the API look like?** A risk event: `{risk_state, evidence[], confidence, model_version, language, latency_ms, timestamp, audit_id}`.
27. **What can actually be built in 48h?** The narrow MVP: streaming ingest → 5 detectors → fusion → risk state → evidence panel → safe escalation → benchmark dashboard.
28. **Biggest limitation?** No independent validation, no live-PSTN captured-call eval yet, liveness not built, real noise/music robustness pending backbone fine-tuning.
29. **What is currently implemented?** TRL-5: streaming fusion pipeline, calibration, telephony hardening, routing, explainable verdicts, measured evals.
30. **Why should a financial institution trust this?** Because it is honest about scope, fails safe, keeps audio on-prem (DPDP/RBI), and augments human analysts rather than replacing their judgment.

---

*Prepared for internal use. All quantitative claims trace to the credibility audit above; anything PROPOSED/TARGET/MOCK is not presented as implemented.*
