# SANGYAN Investor Resilience Hackathon — VoxShield Submission Kit
**Track:** A — Digital Fraud & Scam Resilience (+ Open Track)
**Team:** Devansh Goenka (and team) · Deadline: **04 Oct 2026, 23:59 IST** (Unstop)
**One-line pitch:** *VoxShield — real-time, regional-language detection of AI-cloned voices in investment scam calls, before money changes hands.*

---

## 1 · Why this is a strong fit (criteria → our evidence)
| Criterion (weight) | What they want | VoxShield |
|---|---|---|
| **Resilience & Safety (30%)** | measurably avoid fraud/loss | Detects synthetic/cloned voice in vishing & fake-"finfluencer" voice notes **before** payment; abstains when unsure |
| **Tier-2/3 Usability (25%)** | regional language, low-bandwidth, voice, low cognitive load | **23 Indic languages**; telephony/G.711; Bhashini voice (ASR/ALD); runs **on-prem**, no cloud needed |
| **Guardrail Compliance & Trust (15%)** | non-commercial, no tips, privacy, honest uncertainty | No stock advice; **privacy-by-design** (on-device/local); **abstention** = honest uncertainty; open/provenance |
| **Technical Execution (15%)** | meaningful AI, not novelty | XLS-R + RawBoost detector, codec-profiled cascade, multi-evidence arbitration, speaker verification, adversarial-robust + distilled edge student |
| **Feasibility & Scalability (15%)** | beyond hackathon | REST/WS API + console + SDK; IVR/gateway-ready; trained on public + consented Indic telephony data |

**Problem → User → Solution → Technology → Real-world usefulness** is exactly VoxShield's arc.

---

## 2 · Submission text (paste-ready)

### Problem
India's retail investors (16 crore+ Demat, 70%+ from Tier-2/3) are increasingly targeted by **voice-based scams**: attackers use **AI voice cloning / TTS** to impersonate brokers, SEBI officials, family, or "finfluencers" over phone calls and voice notes. Existing scams are detected too late (when withdrawals are blocked). No accessible tool detects **synthetic speech in Indian languages over phone-quality audio**, and victims often can't read English-language warnings.

### Target user
A first-time investor in a Tier-2/3 city, comfortable in a regional language, receiving a suspicious call/voice note urging an urgent transfer, OTP, or a "guaranteed-return" scheme.

### Solution
**VoxShield Voice Scam Shield** analyzes a call/voice-note in the user's language and returns an explainable **risk verdict**: *human / synthetic / abstain*, with the **transcript**, detected **language**, and **reason codes** (codec/replay/speaker/physic evidence) — plus a plain-language warning and a "pause & verify" action. It runs **on-prem** (privacy), supports **23 Indic languages**, and works on **narrowband phone audio (G.711)**.

### Technology
- **Detector:** fine-tuned **XLS-R-300M + RawBoost**, telephony augmentation (G.711 µ/A-law, band-limit, packet-loss, replay).
- **Codec-profiled cascade + evidence arbitration** (physics/replay/environment/cross-codec/speaker/semantic) with **calibrated abstention**.
- **Indic language layer:** **Bhashini** ALD/ASR/TTS (approved) + **AIKosh** corpora/models.
- **Speaker verification/diarization:** ECAPA-TDNN + NeMo Sortformer (who is really calling).
- **Robustness:** PGD adversarial training + distilled **edge student** for low-end devices; IVR/Twilio-ready.
- Validation on a **12+ language Indic telephony benchmark**; generalization measured vs a **truly unseen generator**.

### Impact & scalability
Detects the fraud **before money moves**; works in the user's language and on cheap phones; deployable by banks, brokers, SEBI/NSDC helplines, IVR, and as an SDK in UPI/telecom gateways. Public-good, non-commercial, privacy-first.

---

## 3 · Demo video script (3–5 min)
| Time | Scene | On screen |
|---|---|---|
| 0:00–0:20 | **Hook** | A real-looking Hindi call: *"SEBI se bol raha hoon, aapke account mein problem hai, turant paise transfer karein."* |
| 0:20–0:45 | **Problem** | Stat card: 16 cr Demat, 70% Tier-2/3; voice-clone scams rising; victims realise too late. |
| 0:45–1:40 | **Live demo — real call** | Play a genuine human Hindi clip in the console → verdict **HUMAN**, language `hi`, transcript, confidence. |
| 1:40–2:30 | **Live demo — deepfake call** | Play an AI-cloned/Bhashini-TTS scam clip → verdict **SYNTHETIC**, reason codes, **"Pause & Verify"** warning in Hindi. |
| 2:30–3:10 | **Hard mode** | Same clip through **G.711 phone codec + replay** → still flags; show the abstraction **ABSTAIN** when evidence disagrees. |
| 3:10–3:45 | **Bharat-first** | Switch language (Tamil/Bengali); show low-bandwidth/on-prem (no cloud), edge student latency. |
| 3:45–4:20 | **Guardrails + scale** | "No tips, no data harvesting, on-device"; architecture diagram; deploy path (bank/IVR/SDK). |
| 4:20–4:45 | **Close** | "VoxShield — hear the human behind the call." Repo/live link. |

**Record with:** `voxshield_console.html` (browser) + `/api/analyze?bhashini=true`; generate the scam clip with **Bhashini TTS** (`backend/gen_worst_ai.py`), degrade through G.711 (`scenario_render.py`).

---

## 4 · PPT outline (10 slides)
1. **Title** — VoxShield: Voice Scam Shield for India's investors.
2. **Problem** — voice cloning in vishing/fintech scams; language + phone-quality gap.
3. **User & journey** — Tier-2/3 first-time investor; suspicious call → warning → verify.
4. **Solution** — analyze call → verdict + transcript + reason codes + pause/verify.
5. **Demo screenshots** — console panels (language, transcript, verdict, abstention).
6. **Architecture** — profiler → cascade → detector → evidence brains → arbitration → verdict.
7. **Technology** — XLS-R+RawBoost, Bhashini/AIKosh, ECAPA/NeMo, adversarial+distillation.
8. **Results** — per-language EER, G.711 degradation, unseen-generator gap, abstention FP cut.
9. **Bharat-first & guardrails** — 23 languages, on-prem privacy, no tips, honest uncertainty.
10. **Impact & roadmap** — bank/IVR/SDK deployment, public-good scaling.

---

## 5 · Guardrail compliance checklist (they check this — 15%)
- ✅ **No stock tips / no buy-sell-hold / no price prediction** — VoxShield only assesses authenticity of *audio*.
- ✅ **No monetisation funnels** — prototype, no commissions, no upsells.
- ✅ **Privacy by design** — on-prem/local inference; no SMS/OTP/financial-record harvesting; only the audio the user submits.
- ✅ **Public-good ethos** — framed as fraud-protection infrastructure.
- ✅ **Honest uncertainty** — explicit **ABSTAIN** class + confidence, never a false binary.

---

## 6 · To-do before 23:59 IST (today)
1. **Live demo link** — run the console + `backend/app.py` (or the DGX demo) and record/upload.
2. **Video** — follow §3 (3–5 min).
3. **PPT** — from §4.
4. **Write-up** — paste §2 (problem/user/solution/tech/impact).
5. Submit on **Unstop** → Sangyan → Submission round.

---

## 7 · Defense one-liners (if jury asks)
- *"Do you give investment advice?"* → No — we only tell you whether the **voice is human orAI**. No tips, ever.
- *"Does it work in my language / on a cheap phone?"* → 23 Indic languages; on-prem; distilled edge student; telephony-native (G.711).
- *"What if you're wrong?"* → We report **abstain** and a confidence; the user is told to **pause and verify** via official channels.
- *"How is this different from existing tools?"* → Existing detectors are English/wideband; we are **Indic + narrowband telephony + abstaining**.
