# MODULE 2 — How AI Actually Clones a Voice

In Module 1 we saw the problem from the outside: a father, a phone call, a stolen ₹50,000.

Now we step inside. We are going to walk into the attacker's workshop and watch, calmly and slowly, how a machine turns a few seconds of your voice into a convincing fake.

Do not worry if you have never touched AI before. We will build every idea from zero.

LEARN:
- What makes each human voice unique in the first place
- The three different ways AI can produce speech, and when a scammer uses each
- The full voice-cloning pipeline, one block at a time
- Where the fake secretly gives itself away — the thread we pick up in Module 3

## Chapter 2.1 — What Makes Every Human Voice Unique

Before we can understand how a voice is copied, we should understand what is being copied.

No two people sound exactly alike. Why not?

### Your voice is built by your body

When you speak, air pushes up from your lungs, passes over your **vocal cords** (two small flaps in your throat that vibrate), and is then shaped by your mouth, tongue, teeth, and nose before it reaches the air.

Every one of those parts is a slightly different size and shape in every person. So the sound that comes out is slightly different in every person too.

Think of a musical instrument. A flute and a trumpet play the same note, but you can tell them apart instantly. The note is the same; the body making it is not. Your throat and mouth are your personal instrument.

The result is a bundle of features that, together, make you sound like you:

- **Pitch** — how high or low your voice sits
- **Timbre** — the "colour" or texture of the sound, the thing that makes your voice yours even at the same pitch as someone else
- **Accent and pronunciation** — how you shape words, shaped by your language and where you grew up
- **Rhythm and speed** — how fast you talk, where you pause
- **Breathing** — when and how you take breath between phrases
- **Micro-variations** — tiny, constant wobbles. Your pitch trembles a little (called **jitter**), your loudness trembles a little (called **shimmer**). No human holds a note perfectly steady.

All of that together is your **voice identity**. Think of it as a fingerprint made of sound.

> In simple words: your voice is unique because it is made by your body, and no two bodies are shaped exactly the same. Pitch, texture, accent, breathing, and a thousand tiny wobbles all mix into one signature.

### Why it feels un-fakeable — but isn't

Because your voice feels so personal, it also feels impossible to copy. Surely a machine cannot reproduce all of that at once?

Here is the uncomfortable truth. Everything we just listed — pitch, timbre, accent, rhythm — is, to a computer, just a **pattern in a sound wave**. And patterns are exactly what modern AI is good at learning.

The machine does not need to understand you. It just needs enough examples of the pattern to reproduce it.

Hold on to one small detail, though, because it will matter enormously later: the micro-variations. The jitter, the shimmer, the natural breathing. These are so subtle and so messy that AI often gets them slightly wrong. Remember that. It is the crack in the fake.

## Chapter 2.2 — The Three Ways AI Makes Speech

Not every fake voice is made the same way. There are three main approaches, and a scammer chooses between them depending on what they are trying to do.

### Way 1 — Text-to-Speech and zero-shot voice cloning

This is the most common method.

Plain **Text-to-Speech (TTS)** is what you already know from Google Maps or a railway announcement. You give it text, it reads the text aloud — but in a generic, factory voice. It does not sound like anyone in particular.

**Voice cloning** takes TTS one dangerous step further. You give it text *and* a short sample of a specific person's voice. Now it reads your text aloud in *that person's* voice.

The frightening version is called **zero-shot** cloning. "Zero-shot" means the AI has never been specially trained on the target person. It hears just a few seconds of them, once, and can immediately imitate them. No weeks of training. No big dataset. A short clip is enough.

You may hear these model and product names: **VITS**, **Tacotron**, **VALL-E**, **ElevenLabs**, and **MMS-TTS**. Each is a system that can turn typed text into spoken audio, some of them in a chosen person's voice.

**When a scammer uses it:** the relative-in-distress and digital-arrest scams. The attacker types out exactly what they want said — "Papa, I've had an accident" — and the machine speaks it in a cloned voice. Full control over the words, delivered in a voice you trust.

### Way 2 — Voice Conversion

Voice Conversion is different, and cleverer in its own way.

Here the attacker **speaks the words themselves**, live, into a microphone. The AI listens and, on the fly, changes the sound of their voice into the target's voice. The words stay exactly as spoken; only the speaker's identity is swapped.

Think of it like a real-time filter. The attacker says "transfer the money" in their own voice, and out the other end comes "transfer the money" in your voice.

> In simple words: with Text-to-Speech the attacker types and the machine talks. With Voice Conversion the attacker talks and the machine disguises their voice as someone else's, in real time.

**When a scammer uses it:** live, back-and-forth conversations. Because a real human is speaking, the reply is instant and natural. If the victim asks an unexpected question, the attacker can answer it on the spot — while still sounding like the person being impersonated. This makes it powerful for a two-way phone call where a pre-typed script would fall apart.

### Way 3 — Replay

The third way uses no fancy generation at all.

**Replay** simply means playing a real recording of the victim's actual voice back down the line. No cloning. No AI voice at all. Just a genuine clip, captured earlier, pressed into service at the wrong moment.

It sounds crude, but it can work against a system that asks a customer to say a fixed phrase, such as "my voice is my password." If an attacker recorded the victim saying that phrase once, they can play it back to get in.

**When a scammer uses it:** attacking voice-password systems, where the same phrase is expected every time. The defence against replay is to ask for something *new* each time — a random digit sequence the attacker could not have recorded in advance. VoxShield includes exactly this kind of **liveness challenge**, but we are getting ahead of ourselves.

Here is a table to keep the three straight.

| Method | Who actually speaks | Best for the scammer when |
| Text-to-Speech / cloning | Nobody — the machine generates it from text | The attacker wants full control of the exact words |
| Voice Conversion | The attacker, in real time | The call is a live back-and-forth conversation |
| Replay | The victim, in an old recording | The system expects a fixed, repeated pass-phrase |

## Chapter 2.3 — The Complete Voice-Cloning Pipeline

Now let us follow a Text-to-Speech clone all the way through, block by block. Most modern systems look roughly like this. We will treat it like an assembly line in a factory.

The line runs like this:

1. **Reference audio** (3 to 10 seconds of the target's voice)
2. **Speaker Encoder**
3. **Speaker Embedding** — the voiceprint
4. **Text input** — the words the attacker wants said
5. **Acoustic model / TTS**
6. **Neural Vocoder**
7. **Final fake waveform**

Let us walk each station.

### Station 1 — Reference audio

Everything starts with a recording of the person you want to imitate. As we saw in Module 1, this comes from an Instagram reel, a WhatsApp note, a podcast, a leaked call — anywhere your voice was saved.

Modern systems need surprisingly little. **Three to ten seconds** is often enough. The cleaner and clearer the sample, the better the clone — but the bar is low.

### Station 2 — Speaker Encoder

The speaker encoder is a listener. Its only job is to study that short reference clip and figure out *what makes this voice sound the way it does*.

It is not interested in the words. It is interested in the identity — the pitch range, the texture, the accent, the personal flavour.

Think of a skilled impressionist listening to a politician for a few seconds, working out the essence of how they talk before attempting the impression.

### Station 3 — Speaker Embedding (the voiceprint)

The encoder's conclusion comes out as a **speaker embedding**. This is just a list of numbers that captures the identity of the voice.

That may sound strange, so here is the idea. To a computer, "this voice is deep, slightly nasal, fast, with a Tamil accent" can be written down as a row of numbers. That row is the voiceprint.

> In simple words: the speaker embedding is your voice turned into a string of numbers — a compact recipe of what makes you sound like you. To give a sense of scale, one voiceprint system VoxShield uses on the defence side boils a whole voice down to just 192 numbers.

Once the machine holds this recipe, it no longer needs the original recording. It has the essence.

### Station 4 — Text input

This station is simple. The attacker types the words they want the fake voice to say.

"Papa, I've had an accident, send fifty thousand rupees."

That is it. Plain text, typed by the criminal.

### Station 5 — Acoustic model (the TTS model)

Now two streams meet. The **acoustic model** takes the *voiceprint* (who should speak) and the *text* (what should be said) and combines them.

Its output is not yet sound you can hear. It produces a kind of detailed sketch of the sound — a blueprint that says, moment by moment, which frequencies should be loud and which soft to speak these words in this voice. Engineers often call this sketch a **spectrogram**, but you can just think of it as a plan for the sound.

This is the station where VITS, Tacotron, or VALL-E do their work.

Think of it as a composer writing detailed sheet music: every note is decided, but nobody has played it out loud yet.

### Station 6 — Neural Vocoder

The **vocoder** is the musician who finally plays the sheet music out loud.

It takes that detailed sound-plan from the previous station and turns it into an actual audio waveform — real sound you can play through a speaker. Common vocoders are named **HiFi-GAN**, **WaveNet**, and **WaveGlow**.

This is the last station on the line. Whatever the vocoder produces is what the victim hears.

### Station 7 — Final fake waveform

Out comes the finished clip: a sound file that plays your voice saying words you never said. It is emailed, sent as a WhatsApp note, or played down a live call.

The assembly line is complete.

### The crack in the fake

We could stop here. But there is one more thing, and it is the whole reason a system like VoxShield can exist.

That last station, the vocoder, is very good — but it is not perfect. When it manufactures the waveform from scratch, it leaves behind faint, unnatural marks. Little tells.

Remember those micro-variations from Chapter 2.1 — the natural jitter, the shimmer, the messy breathing? A real human body produces them without trying. A vocoder tends to make its output slightly *too* clean, slightly *too* regular, and it often mishandles the very highest frequencies of the sound.

These traces are far too subtle for a human ear. Your father on the phone will never hear them.

But a machine that knows exactly where to look can.

> In simple words: the vocoder is the last step in making a fake voice, and it always leaves behind tiny hidden fingerprints that no human can hear. Learning to read those fingerprints is exactly how VoxShield catches a clone — and that is where Module 3 begins.
