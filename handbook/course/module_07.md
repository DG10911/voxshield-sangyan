# MODULE 7 — Inside VoxShield's Detection Pipeline

## Chapter 7.1 — The Journey of One Phone Call

Imagine a factory with a long assembly line.

A raw phone call goes in at one end. A clear verdict comes out the other end. In between, many small workers each do one job.

That is exactly how VoxShield works. Let us follow one phone call down the line, step by step.

LEARN:
- What happens to a call from the moment it arrives
- The five detectors and why they run at the same time
- Where the Indic booster joins in
- How fast the whole line runs

### Step 1 — The call arrives

A customer calls a bank. The audio comes in over a phone line.

Phone audio is often **8 kHz**. That means the phone captures only 8,000 tiny samples of sound every second. It is a low-quality, narrow pipe. Some calls come in wider, at **16 kHz**.

> In simple words: a phone line is like a small straw. Only part of the sound can squeeze through it.

### Step 2 — Load and clean the audio

Before anything else, we tidy the sound.

1. **Resample to 16 kHz mono.** Every clip is converted to one channel at 16,000 samples per second, so all later steps see the same shape.
2. **Drop the silence.** Long gaps where nobody speaks are removed. We only want the actual voice.
3. **Cap the first ~6 seconds of speech.** We do not need the whole call. The first few seconds of talking is plenty to judge the voice.

> In simple words: we wash the audio, throw away the quiet bits, and keep a short, clean sample of the person talking.

One small note. When the audio is very narrow (a true 8 kHz phone line), VoxShield does not stretch it back up. It simply raises a **channel flag** that says "this is a phone call." That flag matters later.

### Step 3 — Build the 89-dim feature bank

Now we measure the voice.

A computer cannot "hear" like you and me. So we turn the sound into **89 numbers**. Each number describes one property of the voice.

Think of a doctor's check-up. Height, weight, blood pressure, heartbeat — many small readings that together describe a patient. Our 89 numbers do the same for a voice.

These 89 numbers include:

- **40 LFCC numbers** — a classic way to describe the shape of speech sounds
- **40 CQCC numbers** — another spectral view, good at catching fine detail
- **9 special cues** — things like high-frequency energy, phase regularity, jitter, shimmer, breathiness, and silence

Real human voices are slightly messy. They have tiny wobbles, breaths, and imperfections. Cloned voices are often too smooth and too regular. Those 9 special cues are built to notice exactly that.

> In simple words: we describe the voice as 89 measurements. Fakes tend to look "too clean" in these numbers.

### Step 4 — Run the five detectors, all at once

Now the 89 numbers, and the cleaned audio, go to **five detectors**.

Each detector is its own expert with its own opinion. They are:

- **XLS-R** — a large speech model, our strongest single expert
- **DistilHuBERT** — a smaller, fast speech model
- **LFCC+CQCC head** — a detector built on the classic spectral numbers
- **Acoustic-DSP** — a hand-crafted rule-based checker
- **Deepfake-V2** — another deep speech model

Here is the key part. They do **not** work one after another. They run **in parallel**, at the same time, using a pool of worker threads.

Imagine five judges at a competition all watching the same performance together, instead of one after the other. It is much faster.

> In simple words: five different experts each score the voice — and they all score it at the same moment.

### Step 5 — The Indic booster votes

If the caller is speaking an Indian language, one more expert joins.

A small language-detector (Whisper) listens and asks: is this Hindi, Tamil, Telugu, and so on?

If yes, VoxShield brings in **our own custom Indic model**. We will tell its full story in Module 8. For now, know this: it is trained specially on Indian voices, and it only speaks up when it is very confident a clip is an Indian-language fake.

Because it only raises the alarm on confident fakes, it can add catching-power **without** wrongly flagging real Indian customers.

### Step 6 — Meta-fusion

Now VoxShield has many opinions. Five detectors, plus maybe the Indic booster.

A referee combines them into **one** number. This step is called **meta-fusion**. We explain it fully in Chapter 7.2.

### Step 7 — Calibration

That single number is then adjusted so it reads as a **true probability**. More on this in Chapter 7.2 as well.

### Step 8 — Channel-aware threshold and decision

Finally, VoxShield compares the probability to a cut-off line, and picks a verdict.

Remember the channel flag from Step 2? A phone call and a clean studio recording are judged with **different** cut-off lines, because a phone line naturally distorts a voice. We cover this in Chapter 7.3.

Out comes the verdict: is this voice likely genuine, uncertain, or likely cloned?

### How fast is all this?

Very fast. On the live server, a full detection takes about **1.7 to 2.1 seconds** — roughly **2 seconds** end to end. A genuine clip clears in about 1.67 s, a clone in about 2.08 s.

> In simple words: the whole assembly line — clean, measure, five experts, referee, verdict — finishes in about two seconds.

That is fast enough to help a bank employee **while the call is still happening**.

## Chapter 7.2 — The Referee and the Probability

We ended Chapter 7.1 with five detectors, each shouting a different score.

Someone has to combine them. That someone is the **referee**.

LEARN:
- What meta-fusion is and why we learn it, not guess it
- What "calibrated" really means
- Why a calibrated score can be trusted

### The referee: meta-fusion

The referee is a small, trained model called a **logistic model**. Its job is simple: take the five detector scores and blend them into one final score.

But it does not treat all five experts equally. Some experts are more reliable than others. So the referee gives each one a **weight** — how much its vote counts.

Here is the beautiful part. Those weights are **learned** from data, not chosen by hand. VoxShield studied many examples and worked out, on its own, which experts to trust.

It learned to **trust** the two strong speech models and the classic spectral head. It learned to **distrust** the two weakest detectors — it actually counts their votes negatively, as a sanity check.

> In simple words: the referee is a trained judge who has learned which experts are usually right, and listens to them more.

This is smarter than a simple average. If you just averaged all five, the weak experts would drag the good ones down. The learned referee avoids that trap.

### Calibration: turning a score into a real probability

The referee gives us a score. But a raw score can be misleading.

A model might output "0.9" and only be right 6 times out of 10. That is a liar's confidence. We do not want that.

So we add a step called **Platt calibration**. It gently reshapes the score so that the number means what it says.

Let us use a weather forecast.

A good weather forecaster is **calibrated** like this: on all the days she says "70% chance of rain," it actually rains on about 70% of them. Her numbers are honest. When she says 70, you can plan around 70.

A bad forecaster says "90%!" every day to sound confident, and is often wrong. You stop trusting her numbers.

VoxShield wants to be the good forecaster. After calibration, when it says a voice is 85% likely fake, that 85 should genuinely mean 85.

> In simple words: calibration makes the confidence number honest — so "80%" really means about 80%.

### How well calibrated is it?

We measure this with a score called **ECE** — Expected Calibration Error. Smaller is better. Zero would be perfect.

VoxShield's ECE is **0.044**. That is small. It means the confidence numbers are roughly trustworthy.

We will be honest here, exactly as our own records are. Calibration reshaped the reliability curve, but it did **not** dramatically shrink the error versus the raw scores. So we say plainly: "the confidence is roughly trustworthy," not "perfectly calibrated."

That honesty matters. A bank is making real decisions about real customers. We would rather tell you the truth than oversell a number.

## Chapter 7.3 — The Verdict a Human Can Read

A score is not enough. A bank employee needs a verdict they can **act on** and **explain**.

This chapter is about turning a probability into a clear, human-readable decision — and never, ever taking that decision away from the human.

LEARN:
- Why phone calls get a stricter cut-off than clean audio
- The three verdict bands and what each means
- The five reason codes and how VoxShield explains itself
- Why a human always makes the final call

### Channel-aware thresholds

A cut-off line — a **threshold** — is the score above which we say "this looks fake."

But one line does not fit every call. A phone line squeezes and distorts a voice, so genuine phone audio looks a little more suspicious by nature. If we used the same strict line for phone calls, we would wrongly flag too many real customers.

So VoxShield uses **two** cut-offs, chosen by the channel flag from Chapter 7.1:

- **Wideband (clean) audio:** the HIGH cut-off is **0.70**
- **Narrowband (phone) audio:** the HIGH cut-off is **0.85**

The phone line is stricter — it needs more evidence before crying "fake" — precisely so real customers on bad phone lines are not falsely accused.

> In simple words: a noisy phone call gets the benefit of the doubt, so we do not punish real people for a bad line.

### The three verdict bands

The final verdict comes in three simple bands:

- **HIGH** — likely a cloned voice → **step up**: verify the caller another way, warn the customer, involve a human agent
- **MED** — uncertain → **monitor**: keep watching, stay alert, do not relax
- **LOW** — likely genuine → **pass**: let the call continue normally

This is like a traffic light. Red means stop and check. Yellow means caution. Green means go.

### The five reason codes

VoxShield never just says "fake" and stops. It tells you **why**, using short reason codes:

| Code | What it flags |
|---|---|
| SSL | Deep speech models find the voice synthetic |
| PH | Phase looks too regular (a vocoder fingerprint) |
| HF | High-frequency energy is unnatural or oversmooth |
| PR | Prosody — the rhythm and melody — looks machine-like |
| BR | Breathing and micro-sounds are missing or wrong |

Each code points to a real property of the audio. Together they let a human understand the machine's thinking in plain terms.

### SHAP — showing the machine's homework

VoxShield goes one step further. It shows **how much each detector pushed the final score**, up or down.

This technique is called **SHAP**. Think of it as the machine showing its homework, not just the final answer.

Imagine five people voting on a decision, and afterwards each one tells you exactly how strongly they pushed, and in which direction. That is SHAP for our detectors.

> In simple words: VoxShield doesn't just give a verdict — it shows which expert pushed it, and by how much.

This turns a mysterious "AI said so" into an explanation a fraud analyst — or a regulator — can read and check.

### A human always decides

This is the most important rule in the whole system.

**VoxShield never auto-blocks a call.** The score is advice, not a sentence.

A HIGH verdict tells a human agent to step up and verify. It does not freeze the customer's account. It does not hang up the phone. A person always makes the final call.

Why so careful? Because the model is honest about its limits. It is roughly 94% accurate, not perfect. A simple trick like adding noise or shifting pitch can still fool it (we cover that gap honestly elsewhere). You do not hand life-changing decisions to a system that can be tricked. You keep a human in the loop.

> In simple words: the machine advises. The human decides. Always.

### The audit trail

Finally, every decision is stamped with a **SHA-256 audit hash** — a short digital fingerprint of that specific analysis.

It lets the bank look back later and confirm exactly what was decided, and on what audio. Think of it as a tamper-evident receipt for each verdict.

And with that receipt, one phone call's journey down the assembly line is complete: cleaned, measured, judged by five experts, refereed, calibrated, given an honest verdict with reasons — and handed to a human to act on.
