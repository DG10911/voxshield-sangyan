# VoxShield Edge — Snapdragon AI Lab Submission Kit
*Real-Time, Privacy-Preserving Voice-Clone Defense for Indian Telephony · Individual submission · Devansh Goenka*

**Evidence labels:** `[VERIFIED]` `[PROJECT RESULT]` `[IMPLEMENTED]` `[EXPERIMENTAL]` `[PROPOSED]` `[TARGET]` `[ILLUSTRATIVE]`

---

## 1 · One-Page Executive Summary

**The problem.** AI voice cloning is cheap and fast. In India, phone-based fraud — fake bank officials, "digital arrest" scams, relative-in-distress calls — increasingly uses synthetic voices in Indian languages over ordinary 8 kHz phone lines. A verdict after the call ends is forensics, not protection, and sensitive call audio should not be shipped to a foreign cloud.

**The solution.** VoxShield Edge is an on-device AI security layer that detects AI-generated / cloned voices during a call and explains *why* — running locally on a Snapdragon-powered HP PC. It is **telephony-first** (8 kHz G.711), **Indic-aware** (10 Indian languages, target), **multi-detector** (five complementary models + a learned fusion), **streaming** (a verdict within the first seconds), **explainable**, and **non-destructive** (recommends step-up verification; never auto-blocks). `[IMPLEMENTED]`

**Evidence `[PROJECT RESULT]`.** 5.9% EER on a held-out in-the-wild corpus · **6.8% EER / 0.98 AUC on out-of-distribution deepfakes from unseen generators** (the honest cross-generator result) · Indic fake recall 42% → 82% after Indic-aware retraining · genuine-Indic false positives 11.7% → 6.3%. Detector scoreboard: best single 16.0%, naive averaging 19.1%, **learned fusion 5.9%** — the fusion produces the gain.

**Snapdragon.** Targets the Hexagon NPU (45 TOPS on Snapdragon X Elite/Plus; 80 TOPS on X2 Elite `[VERIFIED]`) via PyTorch → ONNX (INT8) → ONNX Runtime QNN EP → NPU, compiled/profiled on real devices with Qualcomm AI Hub. **Honest status:** the detector runs today on CPU/GPU; the NPU port is a defined optimisation roadmap `[PROPOSED]` — no on-NPU latency is claimed until measured.

**Why on-device matters.** Privacy (no audio egress), offline operation, low latency, and power-efficient sustained inference — a Snapdragon AI PC per fraud-desk analyst, with no per-call cloud cost.

---

## 2 · Final Submission Copy (paste into the form)

**Project Title (≤500 chars):**
> VoxShield Edge — Real-Time, Privacy-Preserving Voice-Clone Detection for Indian Telephony, optimised for Snapdragon AI PCs

**Brief Project Description (short form field, if any):**
> VoxShield Edge is an on-device AI security layer that detects AI-cloned / synthetic voices during telephony calls and explains why, running locally on a Snapdragon-powered HP PC so sensitive audio never leaves the device. Telephony-first (8 kHz G.711), Indic-aware (10 Indian languages), it fuses five complementary detectors into a calibrated, explainable LOW/MEDIUM/HIGH risk verdict and recommends step-up verification — it never auto-blocks. Measured: 5.9% EER (held-out), 6.8% EER / 0.98 AUC on unseen-generator deepfakes, Indic recall 42%→82%. Snapdragon NPU optimisation (ONNX→QNN, Qualcomm AI Hub) is the defined next step.

**GitHub Repository Link:** `https://github.com/DG10911/voxshield`
**You have a Snapdragon laptop:** **Yes**
**Uploads:** Brief Description = `VOXSHIELD_SNAPDRAGON_BRIEF.pdf` · Pitch PDF = `VOXSHIELD_SNAPDRAGON_PITCH_PDFDECK.pdf` · Pitch PPT = `VOXSHIELD_SNAPDRAGON_PITCH.pptx` (Master doc = `VOXSHIELD_SNAPDRAGON_MASTER.pdf` if a longer doc is allowed).

---

## 3 · 120-Second Demo Script

| Time | On screen | Say |
|---|---|---|
| 0–10s | Title + a phone ringing | "When a cloned voice can sound like someone you trust, the device needs to know the difference. This is VoxShield Edge." |
| 10–25s | Live console, incoming Hindi call, waveform | "An 8 kHz telephony call comes in. Everything you see runs locally on this Snapdragon AI PC — no audio leaves the device." |
| 25–45s | Five detectors activating, streaming | "Five complementary detectors analyse 3-second windows every second — DSP, wav2vec2, XLS-R, DistilHuBERT, and cepstral. Notice they light up independently." |
| 45–60s | Fusion risk climbs to HIGH | "A learned fusion layer combines them into one calibrated risk score. This call scores HIGH — likely a synthetic voice." |
| 60–75s | Evidence panel | "And it tells us *why*: synthetic spectral characteristics, abnormal prosody, vocoder-like energy, and multiple detectors agreeing. It recommends step-up verification — it never auto-blocks a customer." |
| 75–90s | Toggle Wi-Fi OFF | "Now I disconnect the internet completely." |
| 90–105s | Run the same call again, offline | "Same call, same verdict — fully offline, on-device. Private by design." |
| 105–120s | Snapdragon optimisation slide | "Next, we compile the detector to the Snapdragon Hexagon NPU via Qualcomm AI Hub for power-efficient, all-day inference. **The voice never needed to leave the device to determine whether it could be trusted.**" |

*(The offline claim reflects the architecture: inference is local. If a specific model still calls out, adjust the wording before demoing.)*

---

## 4 · 25 Judge Q&A (honest, <80 words each)

1. **Why not one large model?** Single models are fragile to unseen generators (best single = 16.0% EER). Five complementary detectors fail differently; a learned fusion reaches 5.9% and 6.8% on unseen generators. Diversity, not size, drives robustness here. `[PROJECT RESULT]`
2. **Why does Snapdragon matter?** It enables private, offline, low-power, sustained inference on an endpoint. A fraud analyst's laptop can screen calls locally — no audio egress, no per-call cloud cost — which is exactly what regulated Indian banking needs.
3. **Which component runs on the NPU?** Today: none — it runs on CPU/GPU. The NPU port (ONNX → QNN EP → Hexagon) is the defined next step, validated via Qualcomm AI Hub profiling. We don't claim NPU latency we haven't measured. `[PROPOSED]`
4. **How did you validate?** Held-out in-the-wild (5.9% EER) and out-of-distribution generators (MLAAD, 6.8% EER / 0.98 AUC) — the models never saw those generators in training. In-corpus and OOD numbers are reported separately. `[PROJECT RESULT]`
5. **Unseen TTS systems?** The OOD result (6.8% EER on MLAAD, generators absent from training) is our evidence of cross-generator generalisation. It's not perfect; new generators are added to training as they appear. Cross-generator hardening is an ongoing target.
6. **Noisy calls?** The pipeline is telephony-hardened (G.711, band-limiting, noise). Heavy noise still reduces reliability — a stated limitation — and pushes borderline calls into an abstain band for analyst review rather than a forced decision.
7. **Genuine unusual voices?** Over-flagging real customers is costly, so we measure and minimise it: genuine-Indic false positives dropped 11.7% → 6.3% after Indic-aware retraining and channel-aware thresholding. `[PROJECT RESULT]`
8. **Why Indic languages?** Indian fraud happens in Indian languages, and English-tuned detectors both miss Indic fakes and over-flag genuine Indic speakers. An Indic-aware path with language-ID routing fixes both directions.
9. **Why 8 kHz?** It's the real telephony sampling rate. Studio-quality assumptions don't hold; we build and evaluate on 8 kHz G.711 narrowband from the start.
10. **Why 3 seconds?** Enough speech to judge a voice reliably while still forming an early verdict; combined with a 1-second hop the decision refines as the call continues.
11. **False-positive rate?** Genuine-Indic FP is 11.7% → 6.3% after Indic-aware retraining. `[PROJECT RESULT]` We treat FP as a first-class metric because banks can't afford to flag real customers.
12. **Preventing wrong auto-blocks?** By design VoxShield never auto-blocks. It outputs a risk + reasons and recommends step-up verification (OTP, biometric, fraud desk). A human stays in the loop.
13. **Can an attacker evade it?** Possibly — an adaptive attacker aware of the detector is a real threat. Multi-detector fusion raises the bar (evading one rarely evades all), and adversarial robustness is on the roadmap. We don't claim it's unbeatable.
14. **How does it generalise?** Measured cross-dataset / cross-generator: 6.8% EER on MLAAD generators unseen in training. In-corpus scores are much lower but reflect corpus separability, so we lead with the OOD number.
15. **Computational bottleneck?** The self-supervised transformer detectors (wav2vec2/XLS-R) dominate compute — precisely why NPU offload + INT8 quantisation via AI Hub is the optimisation target.
16. **Battery / power impact?** Not yet measured. Power-efficient sustained NPU inference is a target we'll quantify via AI Hub profiling on Snapdragon X/X2. We won't state a number until we have it. `[PROPOSED]`
17. **Why not cloud inference?** Regulated call audio shouldn't leave the institution; cloud adds latency, bandwidth cost, and privacy exposure. On-device is the differentiator, not a limitation.
18. **Commercial deployment model?** A Windows endpoint app per fraud-desk analyst on a Snapdragon AI PC, later an enterprise SDK/API and contact-centre/telecom integration.
19. **Next engineering milestone?** ONNX export + INT8 quantisation, then Qualcomm AI Hub compile/profile on Snapdragon X/X2 to obtain measured on-NPU latency and power.
20. **What's implemented today?** The full detection pipeline: VAD, streaming windows, 89-dim features, five detectors, learned fusion, Indic/telephony routing, calibrated risk, and reason codes — on CPU/GPU, TRL-5. `[IMPLEMENTED]`
21. **What's only proposed?** NPU execution, INT8 quantisation, measured on-device latency/power, and the packaged Windows endpoint app. All clearly labelled `[PROPOSED]`/`[TARGET]`.
22. **What did Snapdragon enable?** The architectural path to private, offline, power-efficient endpoint inference — the core product premise. The concrete NPU numbers come from the AI Hub step we've scoped.
23. **With another six months?** Measured NPU latency/power, real captured-PSTN evaluation, speaker- and generator-disjoint benchmarks, more Indic languages, challenge-response liveness, and a shippable Windows app.
24. **Biggest limitation?** Cross-generator generalisation and real-network validation are incomplete, and on-NPU performance is not yet measured. We state these plainly rather than hide them.
25. **Why should this be a real product?** It targets a real, growing Indian fraud vector that cloud, English-first detectors don't serve, with measured evidence, an on-device privacy story, and a credible Snapdragon path — a defensible niche, not a demo.

---

## 5 · Pre-Submission Checklist

- [ ] **Snapdragon laptop = Yes** answered truthfully on the form.
- [ ] Project Title pasted (≤500 chars).
- [ ] **Brief Project Description** uploaded: `VOXSHIELD_SNAPDRAGON_BRIEF.pdf` (accepted: pdf/doc/docx).
- [ ] **Pitch PDF** uploaded: `VOXSHIELD_SNAPDRAGON_PITCH_PDFDECK.pdf`.
- [ ] **Pitch PPT** uploaded: `VOXSHIELD_SNAPDRAGON_PITCH.pptx` — **open it once on your laptop to eyeball rendering**.
- [ ] GitHub repo `DG10911/voxshield` is **public**, has a clear README, and runs.
- [ ] All docs are in **English** (they are).
- [ ] No fabricated Qualcomm partnership / benchmark / user numbers (verified — none present).
- [ ] Numbers consistent across all files (5.9% / 6.8% / 0.98 / 42→82 / 11.7→6.3).
- [ ] One submission only (rule: first submission counts; can't edit after submitting).
- [ ] Deadline **30 Sep 2026, 23:59 IST** — submit with buffer.
- [ ] (Optional) Master doc `VOXSHIELD_SNAPDRAGON_MASTER.pdf` attached if a longer document is permitted.
- [ ] (Optional) Prototype console `voxshield_console.html` linked in the repo / demo video.

---

*Consistency note: this kit, the master document, the pitch deck, and the brief all use the same tagline, architecture, metrics, and Snapdragon positioning. The genuine-Indic false-positive figure is stated as 11.7% → 6.3% (the measured deployed-model value), not 36.3%.*
