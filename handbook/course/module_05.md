# MODULE 5 — Why Phone Calls Are Harder Than Studio Audio

Imagine you build a brilliant AI detector.

In the lab, it almost never makes a mistake.

Then you plug it into a real bank's phone line.

Suddenly it starts missing fakes.

Nothing broke. The AI did not get worse overnight.

The **audio itself** changed. A real bank call is a very different kind of sound from a studio recording. This module explains why, and how VoxShield is built for the phone, not the lab.

LEARN:
- What "sample rate" means, and why 48 kHz and 8 kHz are so different
- Why a phone codec like G.711 throws away the exact clues detectors need
- How VoxShield trains for phone audio so a real call is home turf, not a surprise

## Chapter 5.1 — Studio 48 kHz vs Telephone 8 kHz

Let us start with one simple idea: **sampling**.

Sound in the real world is smooth and continuous. A computer cannot store something continuous. So it measures the sound many, many times every second. Each measurement is one **sample**.

The number of samples taken per second is the **sample rate**.

> In simple words: sample rate is how many tiny snapshots of the sound we take every second. More snapshots means more detail.

Think of filming a moving car. Take 5 photos a second and the motion looks jumpy and rough. Take 100 photos a second and it looks smooth and clear. Audio is exactly the same. More samples, more detail.

### Studio quality

A professional microphone usually records at **48,000 samples per second**. We write this as **48 kHz** (kHz means "thousands per second").

That is 48,000 snapshots of the voice, every single second.

At that rate, almost every tiny detail survives: breath, texture, faint vibrations, the little imperfections that make a real voice real.

### Telephone quality

Traditional phone systems usually run at **8,000 samples per second**, or **8 kHz**.

Instead of 48,000 snapshots, the phone keeps only 8,000. That is six times fewer. Most of the fine detail is simply never recorded.

A human on the call can still understand the words perfectly. But for an AI hunting for tiny clues, most of the evidence is already gone before analysis even begins.

### Nyquist: the rule that decides what survives

Here is the key piece of science, kept simple.

There is a rule in signal processing called the **Nyquist limit**. It says: the highest frequency you can capture is **half** of your sample rate.

> In simple words: whatever your sample rate is, cut it in half. That is the highest pitch the recording can hold. Anything higher than that is lost forever.

So let us apply the rule.

- Studio at 48 kHz keeps frequencies up to **24 kHz** (half of 48).
- Phone at 8 kHz keeps frequencies up to only **4 kHz** (half of 8).

The human voice has energy well above 4 kHz. The crisp, high, hissy parts of speech live up there. On a phone, all of that is chopped off. Only the lower, muffled part of the voice makes it through.

This is why a phone call sounds "smaller" and more muffled than someone speaking to you in person. It is not your imagination. Everything above 4 kHz has been thrown away.

Here is the comparison side by side.

| Property | Studio recording | Telephone call |
| Sample rate | 48 kHz (48,000/sec) | 8 kHz (8,000/sec) |
| Highest frequency kept (Nyquist) | up to 24 kHz | up to 4 kHz only |
| Typical codec | none, or lossless | G.711, band-limited to ~3.4 kHz |
| Detail captured | breath, texture, high harmonics | words only, most detail gone |
| Do clone artifacts survive? | yes, fully | mostly destroyed |

That last row is the whole problem. Remember it. We will now explain why it hurts so much.

## Chapter 5.2 — G.711 and What Codecs Throw Away

Sample rate is only half the story. Phone systems also **compress** the audio. That is the job of a **codec**.

A codec is a piece of software that squeezes audio down to a smaller size for transmission, then unpacks it at the other end.

> In simple words: a codec is like a JPEG for sound. It makes the file small enough to send cheaply, but some detail is lost forever in the squeezing.

The classic telephone codec is called **G.711**, in a form known as **µ-law** (pronounced "mew-law"). When you make an ordinary phone call, your voice is very likely processed by G.711 before it reaches the other person.

G.711 does two things. It compresses the audio to save bandwidth. And it **band-limits** the voice to roughly **3.4 kHz** — meaning it deliberately keeps only the frequencies below that line and discards the rest.

### Why do banks not just use studio quality?

Judges and managers often ask this. It is a fair question.

The answer is scale and cost. Millions of calls happen every day. Sending every one in full studio quality would demand far more bandwidth, more storage, and more network cost. Phone networks were designed decades ago, when bandwidth was very expensive, to carry clear speech as cheaply as possible.

So they were tuned for one job: make the words understandable. Not: preserve every acoustic detail. And they do that job very well. The trouble is only for us, the detector.

### The cruel irony

Now here is the part that really stings.

Recall from earlier modules how a voice clone is built. A **vocoder** (the final stage of a cloning pipeline, the part that turns the machine's plan into an actual waveform) leaves behind faint fingerprints. These are the tell-tale signs of a fake:

- unnaturally regular phase
- over-smooth energy in the high frequencies
- missing natural jitter, shimmer, and breath

Where do most of these vocoder fingerprints live? **Above 4 to 6 kHz.** Up in the high band.

And what does the phone codec delete? **Everything above about 3.4 to 4 kHz.**

> In simple words: the exact place where a fake voice leaves its fingerprints is the exact place the phone codec wipes clean.

The codec, without meaning to, destroys the evidence. It is as if a burglar left fingerprints on a window, and then a cleaner came by and polished that window spotless before the police arrived.

### Why a studio-only detector goes blind

Now picture a detector trained only on clean studio audio. It has learned to look for those high-frequency artifacts. That is its whole strategy.

Send it a real bank call. The high band is gone. Its favourite clues do not exist anymore. It cannot find the evidence it was taught to rely on.

So it hesitates, or it guesses. Its lab-perfect accuracy collapses on the very calls that matter most. This is the gap between a research demo and a working bank system. Many published models never cross it.

## Chapter 5.3 — How VoxShield Fights Back

VoxShield was built knowing all of this from day one. It does not pretend calls are clean. It expects the phone.

Here are the specific defences.

### 1. Train with codec augmentation

The single most important idea is **codec augmentation**.

During training, VoxShield takes clean audio and deliberately runs it through phone-style codecs — **G.711, Opus, and MP3** — before showing it to the model. So the AI sees the degraded, compressed, band-limited version, again and again.

> In simple words: instead of only studying perfect audio, VoxShield practises on beaten-up phone audio on purpose. So a real call is not a shock. It is home turf.

Think of teaching a driver. You do not train only on sunny, empty roads. You train in rain, fog, night, and traffic, so nothing on a real trip is a surprise. Codec augmentation does the same for the detector.

Our custom Indic model reinforces this. It was fine-tuned with **RawBoost and codec augmentation** baked into training, so its phone-hardening is not an afterthought — it is part of how the model learned.

### 2. The robustness self-test numbers

We test this honestly, and we report the numbers honestly. VoxShield runs a robustness self-test: it takes a clean set of clips, applies one real-world distortion at a time, and measures the error rate. The core measure is **EER** (Equal Error Rate) — lower is better.

| Condition | EER | Change vs clean |
| Clean baseline | 7.5% | — |
| Opus at 12 kbps | 2.5% | improves by 5.0 points |
| G.711 at 8 kHz | 15.0% | +7.5 points |
| MP3 at 16 kHz | 20.0% | +12.5 points |

Look at the Opus row. The error actually **goes down** — to **2.5%**. The model is so comfortable with codec audio that a compressed clip is easier for it than a raw one. That is codec augmentation paying off.

G.711, the hardest classic telephone codec, only pushes error up by **7.5 points**. That is a modest, survivable dent — not the collapse a studio-only detector would suffer. Phone audio is genuinely home turf here.

### 3. Always resample to 16 kHz internally

When a call arrives, VoxShield does not analyse it at 8 kHz. It **resamples the audio to 16 kHz mono** internally before doing anything else.

Why 16 kHz and not just leave it at 8? Because 16 kHz keeps everything up to 8 kHz (Nyquist again). Some real vocoder traces survive in that **6 to 8 kHz** band even after a phone call. Working at 16 kHz makes sure the pipeline can still see whatever survived, rather than throwing away the last remaining clues.

### 4. The 8 kHz channel flag raises the bar

VoxShield also notices when a call is narrowband — that is, genuine phone audio with the high frequencies missing. It detects this from how little energy sits in the high band (technically, when the high-frequency energy ratio drops very low).

When that phone flag is raised, VoxShield **raises its decision bar**. For a wideband studio call, the "HIGH concern" threshold is **0.70**. For a narrowband phone call, that threshold climbs to **0.85**.

> In simple words: on a muffled phone call the detector has less evidence to work with, so it demands a stronger case before it raises an alarm. This protects real customers from being wrongly flagged just because the line was low quality.

Note carefully: the 8 kHz flag only changes the **threshold**. It does not change the detector models themselves. It simply tells the referee, "be more careful, this is a hard channel."

### 5. Measured on real telephony, on a rented GPU

We did not want to just *argue* that VoxShield survives the phone. We measured it.

We took the same held-out benchmark our headline 5.9% is built on, and pushed every clip through the real **8 kHz G.711 phone codec** — the exact thing a real call does to the sound. Then we scored it all again on a rented GPU (an RTX 5090, for a few dollars).

Here is what came back, honestly:

- On real phone-quality audio, VoxShield still holds a **single-digit 6.3% equal-error-rate**. The phone does not blind it.
- The codec is not free: on a clean cross-dataset test it costs about **1.6 points** of accuracy (the studio error rises from roughly 11% to 12%). That is the honest price of a compressed line, and it is small.
- The most important number for a bank: once we tune a stacker for the phone channel, **genuine callers wrongly flagged drop from 23% to 3.3%**. That is the difference between a system a bank can deploy and one it cannot — a real customer on a bad line is no longer treated like a fraudster.
- Speed on that GPU was about **1 second per verdict** (fastest 0.9 seconds), with all five detectors fused. On a plain CPU box it is a few seconds. The bank picks the hardware tier.

> In simple words: we ran the whole test again on real phone-quality sound. The system still catches fakes (6.3% error), and once tuned for the phone it almost stops bothering honest callers (false alarms fall from 23% to about 3%), all in about a second per call on a GPU.

One honest note we always add: this phone number is measured on In-the-Wild data, where one of our detectors has seen similar audio, so it is a best case. On a fully unseen dataset the phone error is a little higher. We report both, and we never relabel the phone number as the studio number.

### 6. The honest gap

We promised, throughout this course, never to overclaim. So here is the truth.

Codec distortion is a problem VoxShield handles well. But **benign, non-codec distortions are still an open gap**. When we test with a gentle pitch shift, a small tempo change, or added background noise, the error rate climbs steeply — noise and pitch changes hurt the most.

These are not attacks. They are ordinary things that happen on real calls: a person speaking faster, a fan in the room, a slightly warped line. Right now they can degrade our accuracy.

We know this. It is on the roadmap, to be closed with matched augmentation — training on those exact distortions the same way we already trained on codecs. Until then, we state it plainly rather than hide it.

And crucially, VoxShield **never auto-blocks** a call. A HIGH result routes to a human step-up check, never an automatic rejection. So even where the model is uncertain, a real person makes the final call.

That is the honest picture: strong on the phone codecs that used to defeat everyone else, still growing on benign noise, and careful never to punish a customer for a bad line.
