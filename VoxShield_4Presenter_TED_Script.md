# VoxShield — The 12–15 Minute Pitch
### Team DigiSeva · UCO Bank × Punjab & Sind Bank × IIT Kharagpur Hackathon (PS2 — Audio Forensics)
**Four presenters · TED-style · follows `presentation.html` chapter by chapter · every number is from the real, live system.**

> **How to use this script:** `[SLIDE]` cues map to the deck. Bold lines are the words to say. *Italic notes* are delivery/coaching. Never read the slide — the slide is the visual, you are the voice. Target ~2 minutes buffer for the live demo and questions.

**Presenter map (equal split, ~3–3.5 min each):**
- **P1 — Opening & the Problem** (Hook → Threat → Why Banks Fail)
- **P2 — The Architecture & the AI** (Innovation → Pipeline → Six Models → Meta-Fusion)
- **P3 — Fairness, Liveness & Beyond Detection** (Fairness + 6th detector → Liveness → the extra shields → live product)
- **P4 — Results, Deployment, Business & the Close**

---

## PRESENTER 1 — THE PROBLEM  *(≈ 3 min)*

### [SLIDE: "Your voice is no longer yours alone."]  — Opening Story

*(Walk to centre. Pause. Let the room settle before the first word.)*

**"9:30 in the morning. A father is having his tea. His phone rings — and it's his son. The voice is shaking: 'Papa, I've had an accident, I need fifty thousand rupees, right now, please.' He doesn't stop to wonder *is this really my son* — he knows that voice. He's known it for twenty years. So he sends the money.**

**That evening his son walks in the door. Safe. Cheerful. Hungry. He never made that call.**

**Nobody hacked a bank that morning. Nobody stole a password or broke any encryption. The attacker defeated the one security system a bank can never patch — a father's trust in his own son's voice.**

**We are Team DigiSeva. And VoxShield exists because voice — the oldest password humanity has — has just been broken."**

### [SLIDE: "Seconds of audio to clone" / "Telephony hides the evidence" / "The damage happens fast"] — The Threat

**"Three facts make this urgent.**

**One — it is cheap. A few seconds of anyone's voice, from a reel, a voice note, a YouTube clip, is now enough for free software to clone them convincingly. Your voice is already out in the open.**

**Two — the phone line helps the attacker. A real call is squeezed through a codec called G.711 — 8 kilohertz telephony.** *(Explain simply:)* **think of it as a narrow letterbox that throws away all the high-frequency detail to save bandwidth. The problem is: the tiny giveaways a clone leaves behind live in exactly that high-frequency detail. So the phone line quietly erases the very evidence we need. This is why a detector trained on clean studio audio falls apart on a real call.**

**Three — it's fast. By the time a human feels something is 'off', the money has already moved. Fraud like this happens in the length of one phone call."**

### [SLIDE: "One model. One language. One point of failure."] — Why Banks Fail Today

**"So why don't the tools we already have stop this?**

**Because most deepfake detectors fail in three ways at once. They're *brittle* — one AI model, one blind spot; a new voice-generator it hasn't seen slips right past. They're *black boxes* — they output 'fake: 87%' with no reason, and no bank officer can freeze a customer's payment on a number they can't explain. And they're *English-centric* — trained on American English, so on Tamil, Bengali, Punjabi, they wrongly flag *genuine* Indian customers as fakes.**

**A detector that insults honest Indian customers is not a security system — it's a liability. To hand off: what a bank actually needs isn't a better single model. It's a layered, honest defence. Priya will show you how we built one."**

*(Handoff — step back, gesture to P2.)*

---

## PRESENTER 2 — THE ARCHITECTURE & THE AI  *(≈ 3.5 min)*

### [SLIDE: "One layered, honest defence." — 01 Detection / 02 Fairness / 03 Liveness / 04 Honesty]

**"Thank you, Aarav. VoxShield is built on four pillars, and I'll be honest about each: **Detection** — catch the fake. **Fairness** — never punish a real Indian customer. **Liveness** — make sure there's a living person on the line, not a recording. And **Honesty, engineered** — every verdict comes with a reason a human can read. Let me start with detection — the core AI."**

### [SLIDE: "Weak alone. Strong together." — the Six AI Models scoreboard]

**"Here is our first honest admission. Look at our six detectors *individually* — most of them are mediocre. Our best single model gets a 16% error rate. Our weakest is basically a coin toss.**

*(Explain EER once, clearly:)* **When I say 'error rate' I mean EER — Equal Error Rate. It's the single fairest score for a detector: the point where the mistakes it makes calling fakes 'real' equal the mistakes calling real voices 'fake'. Lower is better. Zero would be perfect.**

**So how do six weak detectors become one strong system? Two ideas.**

**First — they're deliberately *different*.** *(Explain SSL + LFCC/CQCC simply:)* **Some are big self-supervised models — 'SSL' just means they taught themselves the shape of human speech by listening to enormous amounts of audio, like a child learning sound before learning words. Others are hand-built signal detectors that measure classic fingerprints — LFCC and CQCC are just two mathematical ways of turning sound into a fingerprint the machine can compare, one tuned to even frequencies, one tuned musically across octaves. Different detectors get fooled by different fakes — so a generator that beats one runs into the next."**

### [SLIDE: Meta-fusion detail — weights, bias, Platt calibration]

**"Second — and this is the clever part — we don't just average their votes. We *learn* who to trust. This is meta-learning.** *(Explain:)* **a small 'referee' model that has watched all six detectors on real data and learned each one's track record — who's reliable, who lies, and by how much.**

**Now, the part judges love. Two of our detectors have *negative* weights.** *(Beat.)* **That sounds like a bug. It's our favourite feature. We found two detectors that are *reliably wrong* on our data. And a detector that's consistently wrong is just as useful as one that's consistently right — you flip its vote. So when it screams 'real!', the referee hears 'probably fake'. We turned our worst models into informants.**

**One more honest term — Platt calibration.** *(Explain:)* **it makes the final score mean what it says. When VoxShield outputs 0.9, it should be genuinely nine-times-in-ten fake — so an officer can trust the number, not just the label.**

**The result of the fusion: simple averaging of these detectors gives 19% error. Our learned referee cuts that to 5.9% — with an AUC of 0.983.** *(Explain AUC in one line:)* **AUC is 'how well can it separate real from fake across every setting' — 1.0 is perfect, 0.5 is guessing; 0.983 is excellent. That's roughly 94% honest accuracy on a held-out test. Not the 99% some vendors advertise — a real, measured, defensible number. Rohan will show you the pillar that makes this fair for India."**

*(Handoff to P3.)*

---

## PRESENTER 3 — FAIRNESS, LIVENESS & BEYOND  *(≈ 3.5 min)*

### [SLIDE: "A detector that flags honest customers is a failed detector." — Fairness 36.3% → 6.3%]

**"Thanks, Priya. This slide is our conscience. We took English-trained detectors and measured them on *genuine* speech in ten Indian languages. They wrongly flagged 36% of real Indian customers as fake. One in three honest people — insulted by the security system meant to protect them.**

*(Explain fairness + Indic routing simply:)* **Fairness here isn't a slogan — it's a measured number we publish, including our weak spots. We fixed it two ways. First, Indic routing: a fast language detector listens for a second, and if the call is an Indian language, it sends it to an Indian-aware version of the referee. Second, channel-aware thresholds — a phone line and a studio line get judged by different bars, because they distort sound differently.**

**Result: false alarms on genuine Indian speech dropped from 36.3% to 6.3%. And crucially — English accuracy did not move; still 5.9%. We added an Indian skill without losing an English one."**

### [SLIDE: "The 6th detector — an Indic specialist that can only escalate"]

**"Then we built our own. This is the model we're proudest of — a sixth detector, trained by our team, on a rented GPU, in about thirty minutes, for around two dollars. We fine-tuned a 300-million-parameter multilingual speech model on 4,000 real Indian voices and 4,000 Indian fakes we synthesised ourselves.**

**But here's the safety design. This specialist has one rule: it can only ever *raise* the alarm, never lower it — and only when it's very confident on Indian audio. So it can rescue a fake the other five missed, but it can *never* turn a real customer into a false alarm. On held-out Indian audio: zero false positives on real speakers. It lifted Indian-language clone-catching from 42% to 82% — nearly double — without costing us a single genuine customer."**

### [SLIDE: "A recording can't answer a question from one second ago." — Liveness]

**"Now — detection alone has a loophole. What if the attacker doesn't clone at all, and just *replays* a real recording of your voice? That's a replay attack, and it defeats a pure detector, because the audio *is* genuinely you.**

**So VoxShield adds liveness — challenge-response.** *(Explain:)* **the system asks the caller to say four random digits, right now. A recording from ten minutes ago can't answer a question from one second ago. We check the digits are correct, spoken by a live voice, within a tight time window. Living person passes; playback fails."**

### [SLIDE: "Catch the fraud, not just the fake." — Digital Arrest Shield, warning, enrolment, fraud-ring, identity × liveness]

**"And detection is only half the fraud. Sometimes the *voice is real* but the *situation is a scam* — the 'digital arrest' calls where a fake 'officer' terrifies a victim into paying. Our Digital Arrest Shield listens to the *intent*, tracking the classic scam arc — authority, threat, isolation, extraction — in Hindi, English and Hinglish, and warns the citizen: 'No real agency arrests you over a call. Hang up and dial 1930.' It stops the payment, not just logs the fraud.**

**Around this sit voice enrolment and verification — a voiceprint check for 'is this the real account-holder' — and fraud-ring linkage, connecting one fake voice across many victims. To close my part — this isn't a slide deck. It's live. Meera will show you."**

*(Handoff to P4.)*

---

## PRESENTER 4 — RESULTS, DEPLOYMENT, BUSINESS & CLOSE  *(≈ 3.5 min)*

### [SLIDE: "Not a deck. A working system." — live demo]

**"Thank you, Rohan. Everything you've heard runs today. *(Gesture to demo screen.)* We drop in a call, and in about two seconds the verdict comes back — a score, a HIGH/MEDIUM/LOW label, and five plain-English reason codes an operator can read aloud: low jitter, too-regular high band, no breath. And it scores you *while you're still speaking* — flagging a fake around three seconds in, well inside a ten-second target."**

### [SLIDE: "Numbers we can defend." — scoreboard, fusion value, red-team]

**"Now the honest scoreboard. Held-out test: 5.9% equal-error-rate, AUC 0.983, 93.4% accuracy at our deployed threshold, precision 93.5%, recall 92.9%.**

**What does fusion buy that a single-model API can't? Our best *single* detector was 16% error — the fusion is 5.9%. Nearly three times better, and it degrades gracefully when a new generator appears, because six different models don't share one blind spot.**

**And we red-teamed *ourselves* — this is the honesty pillar. We're transparent about where we're weaker: we handle phone codecs and compression well — Opus actually *improves* us — but aggressive pitch-shifting and heavy background noise still push our error up. We publish that, because a bank should buy a system that knows its own limits, not one that hides them."**

### [SLIDE: "Built for a bank's basement, not our cloud." — architecture, scalability, DPDP]

**"Deployment. This matters enormously to a public-sector bank: VoxShield runs *on-premise*, on CPU, inside the bank's own walls. Customer voice never leaves the building — which is exactly what the DPDP Act, India's data-protection law, demands. Our live system today runs on a single modest cloud box — 4 cores, 8 gigs of memory, about twenty-five dollars a month — and it scales like an ordinary web service, because that's all it is: an API. No exotic hardware. A bank can run this in the basement."**

### [SLIDE: "India's banking future is voice-first." + "One AI platform. Every voice. Every industry."] — Business & Vision

**"Why does this win? Because voice is the channel Indian banking *cannot* abandon — IVR, phone banking, voice assistants, hundreds of millions of callers, many who can't type but can speak. Global players — Pindrop, Reality Defender — are excellent, but English-first and cloud-first. None of them do Indian languages *and* on-premise *and* liveness *and* scam-intent together. That combination is our moat, and fairness is the part a public-sector bank can actually procure.**

**And the same engine — voice authentication with an explanation — extends beyond banking to insurance, telecom, healthcare, government. One API, many sectors."**

### [SLIDE: "The generators will improve. So will the shield."] — Closing Story

*(Slow down. Come back to the father.)*

**"Let's go back to that father, and that morning call. In a world with VoxShield, before the money moves, the system has already listened. It hears the too-perfect breath, the high band that's a shade too clean, and it says — gently, with its reasons — 'this voice was not born from a human throat.' The transfer pauses. The father calls his son. His son picks up, safe, and confused why Papa sounds so shaken.**

**The people building these fakes will keep getting better. We know that. So the honest promise we make isn't 'we've won.' It's this: the generators will improve — and so will the shield. VoxShield is how we make sure that when your family calls, the person on the line is really them.**

**We are Team DigiSeva. Thank you."**

*(All four presenters step forward together for questions.)*

---

## APPENDIX — Fast answers to expected judge questions
- **"Why 94% and not 99%?"** — Because ours is a *held-out, honest* number on real-world In-the-Wild data at a fixed threshold. Vendor 99%s are usually clean-audio, in-distribution, best-case. We'd rather defend a real number.
- **"Negative weights — isn't that overfitting?"** — They're learned on training folds and validated on a held-out set; two detectors are *systematically* anti-correlated with truth on our data, so flipping them is principled, not a fluke.
- **"36.3% vs the 11.7% in your handbook?"** — Two baselines: **36.3%** = English-only detectors on Indic speech (the deck's before-any-Indic-work number); **11.7%** = after Indic routing, before channel-aware thresholds. Both land at **6.3%** deployed. *(Pick one baseline and state it consistently on stage.)*
- **"100% Indic recall?"** — In-distribution, against the specific engine we trained on (MMS-TTS). Real-world coverage broadens as we add more generators; we say this plainly.
- **"Security features on the slides (auth, encryption)?"** — Several are roadmap ("AES-256-ready"), not shipped. On-prem + DPDP-by-design is real today; enterprise auth/RBAC is next. Be honest if asked.
- **Term one-liners:** EER = error rate where false-real and false-fake mistakes are equal (lower better). AUC = separability, 1.0 perfect / 0.5 guessing. SSL = model that self-taught speech from raw audio. LFCC/CQCC = two ways to fingerprint sound. Platt calibration = makes the score's probability honest. G.711 = 8 kHz phone codec that erases high-frequency clone artifacts.
