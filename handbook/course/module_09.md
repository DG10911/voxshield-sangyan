# MODULE 9 — The Other Layers of Defence

So far this course has been about one thing: catching a fake voice.

But catching fakes is only one door. A determined attacker will try other doors.

VoxShield is built like a castle, not a single gate. If one wall is climbed, another stands behind it. Engineers call this **defence-in-depth**.

This module is about the walls behind the first wall.

LEARN:
- Why a voiceprint answers two questions at once — is it you, and are you human
- Why a replayed recording of your real voice can slip past a fake-voice detector
- How a random-number challenge stops replays, live TTS, and human relays
- How VoxShield reads scam intent and still protects real customers from being wrongly blocked

## Chapter 9.1 — Speaker Verification: Is It Really You?

Detecting a fake voice tells you the audio is synthetic. It does not tell you *who* the caller claims to be.

Imagine a caller with a perfectly genuine, human voice. No AI. But it is not the customer — it is a stranger who happens to know the account number.

A fake-voice detector would wave them through. The audio is real, after all.

So we need a second, different check. We need to ask: **is this the same person who opened the account?**

> In simple words: one check asks "is this voice real?" A different check asks "is this voice *you*?"

### The voiceprint

When a customer enrols, VoxShield listens to their voice and turns it into a **voiceprint**.

The voiceprint is made by a real model called **ECAPA-TDNN** (about 22 million parameters). You do not need the name. You need the idea.

The model boils a voice down to exactly **192 numbers**.

Those 192 numbers are like a fingerprint for a voice. Your pitch, your throat shape, your speaking rhythm — all squeezed into a small list of numbers that is uniquely, recognisably you.

> In simple words: your voiceprint is 192 numbers that describe your voice the way a fingerprint describes your thumb.

### Comparing two voiceprints

When you call in, VoxShield makes a fresh voiceprint from the live audio.

Then it compares the fresh 192 numbers to the 192 numbers stored at enrolment.

The comparison uses **cosine similarity** — a simple measure of how closely two lists of numbers point in the same direction. It runs from 0 (nothing alike) to 1 (identical).

VoxShield uses a threshold of **0.18**. Above it, the two voiceprints are close enough to be the same person. Below it, they are not.

### Two questions, one check

Here is the clever part. This single comparison quietly answers **two** questions at once.

1. Is this the **same customer** as the enrolled voice? (identity)
2. Is this a **live human** and not a clone of that customer? (authenticity — because the fake-voice detector from earlier modules runs alongside it)

Put those together and there are exactly three possible outcomes.

| Outcome | What it means | What the bank does |
| VERIFIED | Same customer, and a genuine human voice | Let the call proceed |
| REJECTED-CLONE | It matches the customer's voice, but the audio is synthetic | Stop — this is a clone of the real customer |
| REJECTED-IDENTITY | A genuine human voice, but not this customer | Stop — wrong person |

### The insight ordinary biometrics miss

This is the part worth slowing down for.

A plain voice-biometric system only asks question one: does the voiceprint match?

A perfect clone of the customer *will* match. The voiceprint of a good clone looks almost exactly like the real one. That is the whole point of cloning.

So plain biometrics happily say "VERIFIED" to a perfect clone. This is the case they miss.

> In simple words: ordinary voice login can be fooled by a good clone, because a clone is *built* to match the voiceprint.

VoxShield catches exactly that case. When the voiceprint matches but the fake-voice detector says "synthetic," the answer is **REJECTED-CLONE** — the one an ordinary system would have waved through.

One honest note: today the enrolled voiceprints are held **in memory only**. Restart the server and they are gone. A real database is on the roadmap, not built yet.

## Chapter 9.2 — Liveness and Why Replay Attacks Break Normal Detectors

Now for the door that surprises people.

A fake-voice detector asks one question: **is this audio synthetic?**

But an attacker can win without generating any synthetic audio at all.

### The replay attack

Suppose yesterday a scammer recorded the real customer. Maybe a genuine WhatsApp voice note. Maybe a cloned line they already made and saved.

Today they call the bank. They do not speak. They press **Play**.

The bank hears a real, human, genuine-sounding recording. Because it *is* genuine audio — it was recorded from a real voice.

> In simple words: a recording of a real voice is not synthetic. So a "is this fake?" detector has nothing to catch.

This is a **replay attack**. The caller is not speaking live. They are replaying old audio. And it slips straight past a detector that only hunts for synthesis artifacts.

### The fix: ask a question they could not have pre-recorded

You cannot beat a recording by analysing the sound alone. You beat it by making the caller do something *right now* that a recording cannot do.

So VoxShield adds a **challenge**.

The system speaks a **random number** out loud — say, "please repeat four-seven-two-nine." The caller must say it back.

A recording made yesterday cannot possibly contain today's random number. That is the trap.

### Three checks on the answer

When the caller replies, VoxShield runs three separate checks. All three must pass.

1. **Content** — did they say the *right* number? A speech-to-text model (**Whisper**) reads the reply. A voice-activity gate (**Silero VAD**) runs first, so the system does not hallucinate digits out of silence.
2. **Liveness** — is the audio a genuine human voice? The fake-voice ensemble from the earlier modules checks this.
3. **Timing** — did the answer arrive *within the time window*? Not too slow.

> In simple words: say the right number, in a real human voice, fast enough. Miss any one, and you fail.

### Why every kind of attacker trips

Look at how neatly each attack falls down.

| Attacker | How they fail |
| Replay of an old recording | Fails **Content** — the recording cannot know today's random number |
| Real-time text-to-speech clone | Fails **Liveness** — the ensemble flags the synthetic audio |
| Human relay (a person listening and repeating) | Fails **Timing** — relaying the number takes too long |

Each attacker beats *one* check. None beats all three.

That is defence-in-depth in miniature. No single wall stops everyone. Three walls together leave nowhere to stand.

## Chapter 9.3 — Digital Arrest Shield and Fairness

The last layer is not about the voice at all. It is about the **words**.

### The digital arrest scam

A cruel scam is sweeping India. A caller claims to be from the police, or CBI, or "customs." They tell the victim they are under **digital arrest**. They frighten them, isolate them, and drain their savings.

Detecting whether that caller's voice is cloned is useful. But there is a second signal sitting right there: *what the caller is saying.*

So VoxShield fuses the clone score with a **scam-intent read of the transcript**.

The audio is transcribed by **faster-whisper** — a fast speech-to-text engine that handles **Hindi and Hinglish** (the Hindi-English mix people actually speak). It is roughly four times faster than the older engine, at the same accuracy.

> In simple words: VoxShield does not only ask "is this voice fake?" It also reads the words and asks "is this a scam script?"

### Tracking the stages of a scam

Scam calls follow a pattern. VoxShield tracks the stage the call has reached.

1. **Authority** — "I am calling from the CBI."
2. **Threat** — "There is a case against you. You could be arrested."
3. **Isolation** — "Do not tell anyone. Stay on this call."
4. **Extraction** — "Transfer the money now to clear your name."

Watching this ladder is powerful. A caller who climbs from authority to threat to isolation to extraction is following the scammer's script almost word for word.

### Protecting the victim in real time

When the signs line up, VoxShield can speak a plain warning to the customer:

*No real agency arrests you over a phone call. Hang up and call 1930.*

(1930 is India's national cybercrime helpline.)

That is the whole point. The system is not only defending the bank. It is defending the person on the other end of the line.

### Fairness: the promise not to punish the innocent

Now the honest, hard part.

A bank must catch fraud. But a bank must **not** wrongly block its real customers. Imagine a genuine grandmother in Chennai, calling about her own pension, and the system flags her as a fake.

That is a **false positive** — calling something fake when it is real. Every false positive is a real, upset human being.

> In simple words: it is not enough to catch bad calls. You must also let the good calls through — for everyone, in every language.

### Why fairness is hard across India's languages

VoxShield's detectors learned mostly from certain kinds of audio. On some Indian languages, genuine speakers were more likely to be wrongly flagged.

Across the Indic languages, the genuine-clean false-positive rate started at **11.7%**. More than one real customer in ten wrongly flagged. Not good enough.

The fix was **channel-aware thresholds** — adjusting how strict the system is based on the audio channel (a crisp studio line and a compressed phone line need different bars). That single change cut the Indic clean false-positive rate from **11.7% to 6.3%**.

### The honest per-language table

We do not hide the uneven parts. Here is the deployed false-positive rate, language by language.

| Language | Genuine-clean false-positive rate |
| Marathi | 0.0% |
| Tamil | 3.3% |
| Punjabi | 3.3% |
| Bengali | 3.3% |
| Kannada | 6.7% |
| Gujarati | 6.7% |
| Assamese | 6.7% |
| Hindi | 10.0% |
| Malayalam | 10.0% |
| Telugu | 13.3% |

Marathi is excellent — no real speakers wrongly flagged. **Telugu is the weakest at 13.3%**, and we say so plainly. Closing that gap is ongoing work, not a solved problem.

> In simple words: our fairness is good but not perfect, and we tell you exactly where it is weakest instead of hiding it.

That honesty is itself a defence. A bank can trust a system that shows its own soft spots far more than one that claims to be flawless.

And that is Module 9. Detection is the front gate. Behind it stand speaker verification, liveness, scam-intent reading, and a hard promise of fairness. Together they are what "defence-in-depth" really means.
