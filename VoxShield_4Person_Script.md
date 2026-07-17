# VoxShield — Four-Person Presentation Script

**Team DigiSeva · SRM Institute of Science & Technology · PS2 — Audio Forensics for Voice Security**
Run this against `presentation.html` (15 chapters). Total target: **8–10 minutes** + demo + Q&A.
Fill in the four names below, then rehearse the handoffs until they are seamless.

---

## The lineup (who owns what)

| # | Presenter | Role on stage | Owns chapters | Time |
|---|---|---|---|---|
| **S1** | **[Name 1]** | Opener & Storyteller | Hero (team intro) · 01 Threat · 02 Why Banks Fail | ~2:00 |
| **S2** | **[Name 2]** | AI Architect | 03 Innovation · 04 Five Models · 05 Fairness | ~2:30 |
| **S3** | **[Name 3]** | Product Lead (drives the live demo) | 06 Liveness · 07 Beyond Detection · 08 Real Product **(LIVE)** · 09 Results | ~3:00 |
| **S4** | **[Name 4]** | Strategist & Closer | 10 Deployment · 11 Market · Enterprise · 12 Vision · Thank You | ~2:30 |

**Golden rule:** the person **not** speaking advances the slides and watches the room. One driver at a time. Never talk over the animation — let the reveal land, then speak.

---

## The 30-second spine (everyone memorises this)

> "Voice cloning turned the bank phone line into the easiest door into an account — a fake voice that knows your name, over an 8 kHz line that hides the evidence. VoxShield is a **defence-in-depth system, not a model**: five decorrelated detectors fused by a learned meta-stacker, a fairness layer measured across ten Indian languages, and a challenge-response liveness check that beats replay. It is **explainable, never auto-blocks, runs air-gapped on the bank's own hardware, and flags a fraud call in three seconds** — and it works today, TRL-5."

## Numbers everyone must know cold

| Metric | Value |
|---|---|
| Meta-fusion equal-error-rate (held-out In-the-Wild) | **5.9%** |
| ROC-AUC · Accuracy @0.70 | **0.983 · 94%** |
| Best single model alone (XLS-R) | 16.0% EER → fusion is **~3× better** |
| Fairness: false-positives on genuine Indic speech | **36.3% → single digits** after Indic-aware retraining |
| Streaming time-to-flag | **3.0 s** (well inside the 10 s target) |
| Maturity | **TRL-5**, working system |

*The honesty line (S2's mic-drop):* "The learned stacker gave **negative weight to two of its own five detectors** — it taught itself which models to distrust."

---

# SPEAKER 1 — Opener & Storyteller  ·  ~2:00

### ▸ HERO slide — the team introduction (make it warm, confident, 20s)
> "Good [morning/afternoon]. We are **Team DigiSeva** from SRM Institute of Science and Technology.
> I'm **[Name 1]**, I'll open with the problem. With me are **[Name 2]**, who built our detection AI; **[Name 3]**, who will show you the working product live; and **[Name 4]**, who'll cover deployment and where this goes next.
> What you're looking at is **VoxShield** — real-time AI voice-clone detection for India's voice-first banking. Let me tell you why it has to exist."

*(Stand center. Let the "VoxShield" title animation finish before the first word.)*

### ▸ Chapter 01 — The Threat  *("Your voice is no longer yours alone")*
> "A cloned voice can be built from seconds of public audio — a voicemail, a social clip. It sounds human, it knows the customer's name, and it calls the branch. Worse: a real bank call rides an 8 kHz telephone line, and that compression **smears the very artifacts** most detectors rely on. And it acts in minutes — voice-authorised transfers don't wait. Detection *after* the call is forensics, not protection."

### ▸ Chapter 02 — Why Banks Fail  *("One model. One language. One point of failure")*
> "So why doesn't off-the-shelf detection solve this? Three reasons. A **single model** is brittle — one unseen generator walks straight through. A **black box** can't freeze an account: no bank acts on 'the AI said so'. And **English-trained models are unfair** — they flag genuine Tamil or Bengali customers as synthetic. A detector that punishes honest customers is one a bank can't deploy."

**➡ HANDOFF to S2:** *"So we built the opposite of a single black box. [Name 2] will show you how."*

---

# SPEAKER 2 — AI Architect  ·  ~2:30

### ▸ Chapter 03 — Our Innovation  *("One layered, honest defence")*
> "Thanks, [Name 1]. VoxShield isn't a model — it's **defence-in-depth**: detection, fairness, liveness, and honesty, engineered together. Let me take them in turn."

### ▸ Chapter 04 — Five AI Models, One Brain  *("Weak alone. Strong together")*
> "Detection first. We run **five decorrelated detectors** — signal-processing, hand-crafted anti-spoofing features, and three neural models. Alone, the best of them sits at 16% error; some are near chance. But a **learned meta-stacker** combines them — and here's the honest part: it gave **negative weight to two of its own detectors**. It taught itself which to distrust. The result: **5.9% equal-error-rate on held-out data — about three times better than any single model** — with calibrated, probability-true scores and a plain-language reason code on every verdict."

*(Point to the scoreboard bars animating 62% → 5.9%.)*

### ▸ Chapter 05 — The Fairness Breakthrough  *("A detector that flags honest customers is a failed detector")*
> "Second layer: fairness. We measured false-positives on **genuine speech in ten Indian languages** — Hindi, Tamil, Bengali, Telugu, Marathi, and more. English-centric detectors fail here. After Indic-aware retraining we cut the false-positive rate on genuine Indian speech from **36.3% down to single digits** — and we publish the per-language numbers, including our weak spots. Measured fairness is the moat: it's what a public-sector bank can actually procure."

**➡ HANDOFF to S3:** *"Detection and fairness are the science. But detection alone loses to a replay attack — so [Name 3] will show you the layer that closes that door, live."*

---

# SPEAKER 3 — Product Lead (drives the demo)  ·  ~3:00

### ▸ Chapter 06 — Liveness  *("A recording can't answer a question from one second ago")*
> "Thanks, [Name 2]. Play a clone through a speaker and the acoustic path launders the digital artifacts — pure detection can miss it. So we add **challenge-response liveness**: the system speaks a random prompt — 'say four, seven, two' — and the caller must say it live. We verify **three things at once**: content — did they say the right digits; liveness — is it a live human, not a synthesis engine; and timing — inside the window. A recording can't answer a question generated one second ago."

### ▸ Chapter 07 — Beyond Detection  *("Catch the fraud, not just the fake")*
> "And we go past 'is it fake' to 'is it a scam.' Our **Digital Arrest Shield** fuses the clone score with **scam-intent read from the transcript** — in Hindi, Hinglish or English. A cloned 'CBI officer' running the digital-arrest playbook lands as **CRITICAL**, with the scam script transcribed and flagged. That's catching the fraud, not just the fake."

### ▸ Chapter 08 — Real Product **(LIVE DEMO)**  *("Not a deck. A working system")*
> "And this is not a mock-up — it's running right now. Let me show you."
>
> **[SWITCH to the live system / demo tab.]**
> 1. *Genuine clip →* reads **LOW**.
> 2. *AI-clone clip →* reads **HIGH** — even played through a phone.
> 3. *Live call / streaming →* watch it **flag the clone at 3 seconds**.
> 4. *(If time) Arrest Shield →* CRITICAL with the scam transcript.
>
> *(Keep it to 60–75s. If the network or mic misbehaves, say "here's the recorded run" and cut to a backup clip — never debug on stage.)*

### ▸ Chapter 09 — Measured Results  *("Numbers we can defend")*
> "Every number here is **held-out** — clips the system never trained on. 5.9% error, 0.98 AUC, 94% accuracy, flagged at 3 seconds, fairness cut from 36% to single digits. No cherry-picking, no 'up to'."

**➡ HANDOFF to S4:** *"A working system is only useful if a bank can actually run it. [Name 4] will take you there."*

---

# SPEAKER 4 — Strategist & Closer  ·  ~2:30

### ▸ Chapter 10 — Deployment & Trust  *("Built for a bank's basement, not our cloud")*
> "Thanks, [Name 3]. VoxShield runs **on-premise, air-gapped** — the Docker image bakes every model in, so it never phones home. Audio is **SHA-256 hashed**, never stored in the clear. And by design it **never auto-blocks** — high risk routes to step-up verification alongside the bank's existing caller-ID checks. A human stays in charge. It's built to GOV.UK / USWDS accessibility standards."

### ▸ Chapter 11 — The Market  *("India's banking future is voice-first")*
> "Why now? Phone banking, IVR and voice payments reach hundreds of millions that apps never will — across languages, literacy levels and feature phones. Every one of those calls is an attack surface. Voice security isn't a feature; it's table stakes for every bank running a call centre."

### ▸ Enterprise · Business Mode  *("One AI platform. Every voice. Every industry")*
> "And the same engine reaches beyond banking — government helplines, telecom anti-vishing, insurance claims, healthcare, legal forensics. One drop-in API, twelve sectors. That's the business: enterprise SaaS, usage-based API, on-prem licensing, and government and banking contracts."

### ▸ Chapter 12 — Vision  *("The generators will improve. So will the shield")*
> "The clones will get better — so does the shield: continual learning for new generators, deeper Indic fine-tuning, source attribution, adversarial-robust training. We're TRL-5 today, with an honest path to production."

### ▸ THANK YOU — the close (all four step forward)
> "**Detection. Fairness. Liveness.** One layered, honest defence for India's voice-first banking future. We're **Team DigiSeva** — thank you. We'd love your questions."

---

## Q&A — who fields what

| Question theme | Lead answer | Backup |
|---|---|---|
| Accuracy / EER / how it was measured | **S2** | S3 |
| Fairness / Indian languages / bias | **S2** | S1 |
| Live demo / product / latency | **S3** | S2 |
| Deployment / security / on-prem / compliance | **S4** | S3 |
| Business model / market / competition | **S4** | S1 |
| "Isn't this just a deepfake detector?" | **S1**: "No — real/fake is table stakes. We add fairness for India and liveness against replay, and we catch the *scam*, not just the fake." | S4 |

**If you don't know an answer:** "Great question — that's on our roadmap; here's how we'd approach it," then bridge to a strength. Never bluff a number.

---

## Rehearsal checklist
- [ ] Each speaker can deliver their block **without reading**, in time.
- [ ] Handoff lines are memorised — no awkward "um, over to you."
- [ ] The **demo has a recorded backup clip** ready in a second tab.
- [ ] Slides advance with **arrow keys**; the non-speaker drives.
- [ ] Numbers on your lips **match the numbers on the slide**.
- [ ] Timed a full run twice; you're under the limit with 30s to spare.
- [ ] One-line answers rehearsed for the six Q&A themes above.

## Timing at a glance
`S1 2:00 → S2 2:30 → S3 3:00 (incl. demo) → S4 2:30 → Q&A`  ≈ **10 minutes**.
To cut to **6 minutes**: S1 keeps only Hero + Threat; S2 drops the per-language detail; S3 does one demo (clone → HIGH at 3 s) and the results tile; S4 keeps Deployment + Close.
