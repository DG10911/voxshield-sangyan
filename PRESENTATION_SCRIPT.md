# VoxShield — Presentation Script & Judge Playbook
*Team DigiSeva · PS2 — AI voice-clone detection for Indian banking. Every number here is traceable to a committed artifact.*

---

## 0. The 30-second elevator (memorise this)

> "Voice cloning has made the bank phone line the easiest door into an account — a fake voice that knows your name, over an 8 kHz line that hides the evidence. VoxShield is a **defence-in-depth** system, not a model: **five decorrelated detectors fused by a learned meta-stacker** (5.9% held-out error), a **fairness layer measured across 10 Indian languages**, and a **challenge-response liveness check** that beats replay. It's **explainable, never auto-blocks, runs air-gapped on the bank's own hardware, and flags a fraud call in 3 seconds** — and it's a working system today, TRL-5."

**One-line hook:** *"Real/fake is table stakes. We catch the fraud, not just the fake — fairly, in the languages the scam is actually run in."*

---

## 1. The numbers cheat-sheet (know these cold)

| Metric | Value | Source artifact |
|---|---|---|
| Meta-fusion EER (held-out In-the-Wild, n=320) | **5.9%** | `meta_eval.json` |
| ROC-AUC | **0.983** | `meta_eval.json` |
| Accuracy @0.70 · Precision · Recall · F1 | 93.4% · 93.5% · 92.9% · 0.93 | `meta_eval.json` |
| Confusion @0.70 | TP 144 · TN 155 · FP 10 · FN 11 | `calibration.json` |
| Calibration ECE · Brier | 0.044 · 0.048 | `calibration.json` |
| Best single model (XLS-R 300M) EER | 16.0% | `meta_scores.csv` (800-clip) |
| Naive average fusion EER | 19.1% | `meta_scores.csv` |
| Indic genuine FP (clean), channel-aware | **6.3%** (from 11.7%) | `lang_report.json` |
| Indic fake recall, language-routed | **82%** (from 42%) | `exp_indicfull_result.json` |
| Streaming time-to-flag | **3.0 s** (5/5 clips ≥3 s, within 10 s) | `latency_trace.json` |
| Training / test split | 480 train / 320 test, In-the-Wild held out | `meta_eval.json` |

**The learned stacker weights** (the honesty story): DistilHuBERT **+2.22**, LFCC+CQCC head **+2.10**, XLS-R **+1.21**, Acoustic-DSP **−0.55**, Deepfake-V2 **−1.17**, bias +0.13. *The model learned to distrust two of its own five detectors.*

---

## 2. Slide-by-slide talk track

### Prologue · One Call. One Approval. One Invisible Fraud.

*(This is the cold open. Deliver it slowly, let the balance drop land, then move into the problem. The deck's Prologue section mirrors this beat for beat.)*

> Good morning, respected judges. We are Team DigiSeva from SRM Institute of Science and Technology.
>
> For the next twelve minutes, we would like to tell you a story. Because the problem we are solving does not begin with AI models or algorithms. It begins with a phone call.
>
> Our project is VoxShield, a real-time AI voice-clone detection platform designed for Indian banking. By combining six complementary detectors, a learned fusion model, language-aware fairness, and challenge-response liveness, VoxShield helps identify high-risk voice impersonation attempts within the first ten seconds of a call.
>
> Let us show you why that matters.
>
> It is 10 a.m. A customer service representative at a bank receives an incoming call. The caller sounds calm, confident, and familiar. They know the customer's name, account information, and recent transaction history. They correctly answer the identity verification questions asked by the agent.
>
> For the particular request they are making, the bank follows its normal verification process. If additional verification such as an OTP is required, the attacker has already obtained it through social engineering or another compromise. From the agent's perspective, every required check has been satisfied. The request is approved.
>
> A few minutes later, the real customer opens the banking app. Their balance has dropped from ₹8,47,000 to ₹97,000. They immediately call the bank and say: "I never made that call."
>
> What happened? No banking server was hacked. No malware broke into the bank. No insider transferred the money. Instead, the attacker combined stolen personal information, social engineering, and an AI-generated clone of the customer's voice to convincingly impersonate the customer throughout the verification process.
>
> This is the key point: voice cloning does not replace existing banking security. It strengthens an impersonation attack by making the fraudster sound exactly like the genuine customer. As AI voice synthesis becomes increasingly realistic, a familiar voice is no longer sufficient evidence that the caller is genuine.
>
> That is exactly the gap VoxShield is designed to help close. Instead of relying only on what the caller knows or how convincing they sound, VoxShield provides the bank with an independent, AI-powered assessment of whether the voice itself appears genuine or synthetically generated, enabling high-risk calls to be routed for additional verification before money moves.

**Judge-proofing this open (if pressed):**
- *"But OTP would stop this."* Correct in isolation, which is why we say the voice does not replace 2FA, it strengthens social engineering. If the attacker has already phished the OTP, the voice is what makes the whole call believable to the agent. VoxShield adds a check the attacker cannot phish: the acoustic authenticity of the voice itself.
- *"So you are not claiming to bypass all security?"* No. We are honest: we add an independent, explainable signal on the one thing that used to be trusted automatically, the voice, and we route high-risk calls to step-up. We never auto-block.

---

### Ch 1 · The Threat — *"Your voice is no longer yours alone."*
- Consumer tools clone a speaker from **seconds** of audio — a voicemail, a social post. Cheap, public, multilingual.
- Three forces make it a bank problem: (1) clones sound human and *know the customer's name*; (2) **telephony hides the evidence** — 8 kHz G.711 smears the exact high-frequency artifacts most detectors rely on; (3) **the damage is fast** — voice-authorised transfers act in minutes. *A verdict after the call ends is forensics, not protection.*
- **Land this line:** "Detection has to happen inside the first seconds — or it's an autopsy, not a defence."

### Ch 2 · Why Banks Fail — *"One model. One language. One point of failure."*
- We **measured the standard approaches first.** Single detectors we tested ranged **16.0%–62.4% EER** on held-out data — a generator the model never saw walks straight through.
- Black boxes can't face a customer: *"the AI said fraud"* won't survive an auditor or a regulator.
- English-centric models **punish India** — genuine Tamil/Bengali speech read as synthetic.
- And even a perfect detector **loses to replay** — play the clone through a speaker and the acoustic path launders the artifacts. **Detection alone is not a defence.**

### Ch 3 · Our Innovation — *"One layered, honest defence."*
Four pillars: **① Detection** (5 decorrelated families, learned stacker, calibrated) · **② Fairness** (10 Indian languages, Indic-retrained, telephony-tested) · **③ Liveness** (random challenge a recording can't answer) · **④ Honesty engineered** (reason codes, SHA-256 audit, never auto-block).

### Ch 4 · Five AI Models, One Brain — *"Weak alone. Strong together."* (the technical heart)
Walk the pipeline left→right:
1. **Incoming call** 8 kHz G.711 → **sliding window** 3 s / 1 s hop, verdict every second.
2. **Feature bank → 89-dim vector:** LFCC, CQCC, group-delay **phase**, **prosody** (F0, jitter, shimmer), **HF vocoder energy >6 kHz**.
3. **The five detectors** (say the weight out loud — it's the wow):
   - Acoustic DSP — signal artifacts, always-on — EER 46.9% — **w = −0.55**
   - Wav2Vec2 (Deepfake-audio-detection-V2) — EER 62.4% — **w = −1.17**
   - **XLS-R 300M** — multilingual wav2vec2, deepfake-FT — EER 16.0% — **w = +1.21**
   - **DistilHuBERT** — fine-tuned on In-the-Wild — EER 23.0% — **w = +2.22**
   - **LFCC+CQCC fusion head** — RawBoost + codec aug — EER 26.8% — **w = +2.10**
4. **Meta-fusion** (logistic, bias +0.13) → **Platt calibration** → **true probability**.
5. **Risk verdict:** HIGH ≥ 0.70 → step-up · MEDIUM → monitor · LOW → pass. **+ reason codes + SHA-256 audit. Never auto-block.**
- **The scoreboard:** best single 16.0% EER, naive average *worse* at 19.1%, **only the learned stacker hits 5.9%.** Point at the negative weights: *"the model learned which of its own detectors to distrust — that honesty is the architecture."*
- **Reason codes:** **SSL** (neural synthesis likelihood), **PH** (unnatural phase regularity), **HF** (vocoder fingerprint >6 kHz), **PR** (missing prosody), **BR** (TTS inserts silence, not breath).

### Ch 5 · The Fairness Breakthrough
- Per-language **false-positive** rate on genuine speech, threshold 0.70, measured not projected. Overall genuine-Indic FP **11.7% → 6.3%** with channel-aware thresholding.
- **Fairness cuts both ways** — we also had to catch *Indian-language fakes*. Synthesized an Indic deepfake set (MMS-TTS), trained an Indic-aware path, route with on-device language-ID: **Indic fake recall 42% → 82%, English EER unchanged at 5.9%.**
- **Own the weak spot:** "Telugu is still our weakest language, and under 8 kHz telephony rates rise further — which is exactly why we built channel-aware thresholds and why we gate action on liveness, not detection alone."

### Ch 6 · Liveness — *"A recording can't answer a question from one second ago."*
- System speaks a **random digit challenge**; the caller must say it live. Three checks, **all three required**:
  1. **Content** — Whisper ASR transcribes the reply; do the digits match (incl. "four seven two")?
  2. **Liveness** — the full ensemble scores the *reply itself* — is it a live human, not a real-time TTS?
  3. **Timing** — did it arrive inside the window?
- **Each escape route closed by a different check:** replay fails content, real-time TTS fails liveness, human-relay fails timing.

### Ch 7 · Beyond Detection (the intelligence layer — *"catch the fraud, not just the fake"*)
- **Digital Arrest Shield:** fuses clone-score with **scam-intent** on the transcript and tracks the live script stage **Authority → Threat → Isolation → Extraction**; full playbook + cloned voice → **CRITICAL**. Covers English, Hindi & Hinglish — the languages the ₹19,000 cr scam is run in.
- **Citizen-protection warning:** on a digital-arrest verdict it **speaks a warning in the victim's language** — *"no real agency arrests over a call — hang up and call 1930."* Stops the payment, not just logs it.
- **ECAPA speaker verification:** identity **×** liveness in one embedding. A clone of the customer **passes identity but fails liveness → REJECTED-CLONE** — the case biometric-alone systems miss.
- **Fraud-ring linkage:** rolling speaker-print links the same cloned voice across victims — **even across the 8 kHz codec** (it runs on a speaker-identity embedding, not detection features).
- **Explainable, live:** streams each detector's score, strongest evidence, fusion logic, rising confidence, **generator attribution**, and **partial-fake localization** (which seconds are AI).

### Ch 8 · Real Product, Running Today — *"Not a deck. A working system." (TRL-5)*
Five live surfaces: **Operator Console** (verdict + fusion breakdown + spectrogram + reason codes) · **Live Call** (scored every 2 s, flag at 3.0 s) · **Liveness Challenge** · **Bank Integration View** (feeds existing fraud flow, step-up not freeze) · **Beyond the fraud desk** (IVR, payments, agent-assist, KYC, forensics — one REST API).

### Ch 9 · Measured Results — *"Numbers we can defend."*
5.9% EER · 0.983 AUC · 93.4% acc · 3.0 s flag · 6.3% Indic FP · 5+1 detectors. **Every figure held-out.** Show the 7-system scoreboard; land the honesty note: *naive averaging (19%) is worse than the best single model (16%) — only the learned stacker beats both.*

### Ch 10 · Deployment & Trust + India/DPDP
- Stateless FastAPI a bank runs **on-prem / air-gapped**; audio **hashed, never stored in clear**; **never auto-block**; explainable; WCAG 2.1 AA.
- Full architecture (5 layers) — every component in the repo today.
- **DPDP one-pager:** 6 principles → 6 design facts (minimisation, purpose limitation, localisation, no-solely-automated-decision, transparency, accountability). *"Data it never keeps is data neither it nor the bank must protect."*

### Ch 11–12 · Market & Vision
- India's banking future is **voice-first** — reaches customers apps never will. **Fairness across 10 languages is the moat** a PSU bank can actually procure.
- Beachhead **banking (live, TRL-5)**; the 12-sector map is **addressable expansion, not current deployments** (say this plainly). SLAs/certs (99.9%, SOC 2, ISO 27001) are **targets**, not held today; WCAG AA + audit trail **are** implemented today.
- Honest TRL path: TRL-5 now → sandbox pilot (TRL-6) → harden for India (TRL-7).

---

## 3. Live demo flow (if you screen-share)
1. **Operator Console** → drop `02_ai_clone_1.wav` → HIGH ~0.96, show reason codes + spectrogram.
2. **Live Call / streaming** → show the timeline crossing 0.70 at **3.0 s**.
3. **Liveness** → issue challenge, answer live → 3-check PASS; then play a recording → content FAIL.
4. **Fairness page** → per-language FP bars; name Telugu as the honest weak spot.
5. **`/docs`** → show it's a real OpenAPI service. Mention `/api/why-fusion` for explainability.

*Run locally:* `cd /Volumes/KIOXIA/voxshield/backend && ./run_voxshield.sh` → `http://localhost:8000/hub`.

---

## 4. JUDGE Q&A — the hard questions, honest answers

### A. Accuracy & method
**Q: Is 5.9% EER just overfitting / leakage?**
No. The **In-the-Wild corpus is held out entirely**; the neural models are **frozen**; the meta-stacker trains on 480 clips and is evaluated on a **disjoint 320-clip split it never saw**. These are cross-dataset numbers, and the per-detector scoreboard is reproducible from the committed `meta_scores.csv`.

**Q: Why five models? Isn't one good model enough?**
Because each detector **fails differently**, and a generator that fools one often doesn't fool another. Best single model is 16% EER; **fusion gets 5.9%.** Critically, **naive averaging is *worse* (19%)** than the best single — only a *learned* stacker that knows how much to trust each detector wins.

**Q: Then why keep two detectors with *negative* weights — why not delete them?**
A negative weight isn't a useless detector; it's a **contrarian feature.** When those two fire in a particular pattern, that pattern is itself informative to the stacker. Removing them measurably hurt fusion. Keeping them — and showing the negative weights — is the honest, better-performing choice.

**Q: Why does calibration matter?**
Because a bank acts on a **probability**, not a raw score. We Platt-calibrate so 0.7 means ~70%; **ECE 0.044, Brier 0.048.** We also expose an **abstain band** for the uncertain middle instead of forcing a call.

**Q: How is this different from a commercial deepfake-detection API?**
Four things a single-model cloud API can't give a bank: **learned multi-model fusion + calibration**, **explainable reason codes**, **measured Indian-language fairness**, and **on-prem/air-gapped + liveness**. It's a defence system, not a classifier.

### B. Fairness
**Q: How do you *know* it's fair to Indian languages?**
We **measured** it — genuine speech in **10 languages**, per-language FP **published** (including the bad ones). Channel-aware thresholding cut overall Indic clean FP **11.7% → 6.3%**, and language-routing lifted Indic fake recall **42% → 82%** with **English EER unchanged (5.9%).**

**Q: Telugu FP is still high — isn't that a problem?**
Yes, and we **show it rather than hide it** — Telugu is our weakest at 13.3% clean. Two mitigations already in the system: channel-aware thresholds, and **we never auto-block** — high risk routes to step-up, so a false positive costs a verification step, not a frozen account. Full fix is on the roadmap (Indic fine-tune).

### C. Robustness & security (we red-teamed ourselves)
**Q: Can an attacker evade you?**
We tested exactly this and **publish the results.** We're **robust to the channels we hardened for** — real VoIP/phone codecs: **Opus actually improves (EER 2.5%), G.711 +7.5 pts, MP3 +12.5 pts.** But **benign DSP manipulations degrade us**: pitch-shift +48.8 pts, noise +37.5, tempo +25. That's our top robustness gap, and we're honest about it — the fix is matched augmentation + the SSL fine-tune, plus liveness gating action regardless.

**Q: What about replay attacks?**
That's what **liveness** is for. A recording can't answer a challenge with digits that didn't exist when it was recorded. Replay fails content; real-time TTS fails the liveness score; a human relay fails timing.

**Q: White-box adversarial attacks (FGSM/PGD)?**
**Stated roadmap, not claimed as covered.** Our self-test covers signal-level + channel robustness, which is the reproducible part on our hardware. We don't overclaim.

**Q: What's your false-positive story for a real customer?**
~6% on English held-out, 6.3% on clean Indic. And structurally: **no customer is ever locked out by a model score** — HIGH routes to human step-up verification. The score is a fraud *signal*, not a *judge*.

### D. Data & training
**Q: What did you train on, and where's the leakage control?**
Frozen public anti-spoof models + a stacker trained on a mixed corpus with **In-the-Wild held out for test**. Training uses **RawBoost + G.711 codec augmentation** (so telephony is home turf). Indic fakes were **synthesized (MMS-TTS)**; genuine Indic from **IndicVoices**. Test split is disjoint.

**Q: Your eval sets are small (n=320, 30 clips/language).**
Fair — they're honest sample sizes and we label them everywhere (no "up to", no projections). They're big enough to be directional and reproducible; scaling the eval is part of the pilot phase. We'd rather show a real 320-clip number than a projected one.

### E. Deployment, privacy, scale
**Q: Latency in production?**
GPU **sub-second**; commodity CPU **3–8 s**. Streaming **time-to-flag 3.0 s** (measured, `latency_trace.json`), inside the 10 s design target.

**Q: DPDP / data privacy?**
On-prem/air-gapped → **data never leaves the bank**; raw audio **never stored in clear** (SHA-256 hash only); **no training on customer calls**; **no solely-automated decision**; full audit trail. Six DPDP principles mapped to six design facts in the deck.

**Q: Does it scale?**
**Stateless** — no sessions, no shared state. Add replicas behind a load balancer, capacity grows linearly. Models baked into a ~2 GB Docker image → **zero runtime downloads**, real air-gap.

**Q: What's the footprint / can a bank run it offline?**
One Docker image, all five detectors + Whisper (~2 GB), no external calls at runtime. Edge/quantised path (AASIST-L, ONNX) is the near-term streaming-on-CPU plan.

### F. Business & differentiation
**Q: Why can't a bank just buy an existing vendor?**
Existing vendors are English-centric single models behind a cloud endpoint. A PSU bank needs **measured Indian-language fairness, on-prem residency, explainability, and liveness** — that's our moat, and it's procurable.

**Q: What's live vs. roadmap?**
**Live today (TRL-5):** the five-detector fusion, fairness eval, liveness, live two-party call demo, on-prem Docker, audit trail. **Roadmap:** the 12-sector expansion, managed-service SLAs, SOC 2 / ISO 27001, and the Indic SSL fine-tune. We separate the two on the slides deliberately.

**Q: Revenue model?**
Enterprise SaaS (per-line), metered API usage, on-prem licensing (banking/defense), and government citizen-helpline contracts. Banking fraud-desk is the beachhead.

### G. The curveballs
**Q: What happens when generators get better?**
Two structural defences that don't depend on today's artifacts: **fusion** (a new generator has to beat five decorrelated detectors *and* the stacker), and **liveness** (challenge-response is generator-agnostic — it attacks the *replay/real-time* constraint, not the audio fingerprint). Plus a retraining pipeline.

**Q: What's the single biggest weakness you'd fix first?**
Benign-DSP robustness (pitch/noise/tempo). It's measured, it's published, and the fix is concrete: matched augmentation in training + the XLS-R+AASIST Indic fine-tune. We'd rather you hear it from us than find it.

**Q: If I pitch-shift a clone, you miss it — so is this even useful?**
Detection is **one layer**. That attacker still has to pass **liveness** to move money, and the **intelligence layer** (scam-stage + intent) fires on the transcript regardless of acoustic evasion. Defence-in-depth means no single evasion wins.

---

## 5. Honesty guardrails (do NOT overclaim)
- Say **"TRL-5, validated working system"** — not "production-deployed in a bank."
- The **12 sectors** are *addressable*, banking is the only live one.
- **99.9% / <300 ms / SOC 2 / ISO 27001** are **targets**, not current facts.
- The **XLS-R Indic fine-tune "100%"** figure has **no committed artifact** — call it roadmap, cite **42→82% routed** as the real number.
- Integration logos (Azure/Twilio/Salesforce…) are **channels it *can* integrate with**, not existing customers.
- Pitch/tempo/noise **do** degrade us — never claim full robustness; claim **codec**-robustness (that's the measured, true one).
