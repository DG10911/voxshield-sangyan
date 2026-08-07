# MODULE 4 — How Sound Becomes Numbers

A computer cannot hear.

It has no ears. It only understands numbers.

So before VoxShield can catch a fake, it must turn a voice into numbers it can reason about. That journey — from a vibration in the air to a neat list of numbers — is the story of this module.

LEARN:
- What sound really is, and how a computer records it
- How a wave becomes a picture called a spectrogram
- Why VoxShield turns each call into exactly 89 numbers, and what they mean

## Chapter 4.1 — What Sound Really Is

Clap your hands.

You just squeezed the air. That squeeze pushed the air next to it, which pushed the air next to that, and so on — a ripple racing outward until it reaches an ear.

That is all sound is. Moving air. A pressure wave.

> In simple words: sound is nothing but air being pushed back and forth very fast.

### From a wave to a waveform

If we track how the air pressure rises and falls over time and draw it on a graph, we get a wiggly line.

That line is called a **waveform**. It goes up when the air is pushed together and down when it is pulled apart.

The height of the wiggle is the **amplitude** — how strong the push is. A big amplitude is a loud sound. A small amplitude is a quiet one.

### How a computer captures the wave

A wave is smooth and never-ending. A computer needs numbers. So it takes rapid snapshots of the wave's height, thousands of times a second.

Each snapshot is a **sample**. How often it takes them is the **sample rate**.

> In simple words: recording sound is like a movie camera for air. Sample rate is how many frames per second it shoots.

More frames mean a more faithful recording. VoxShield does all its analysis at a sample rate of **16,000 samples per second** (written 16 kHz). Every incoming call, whether it arrives at 8 kHz or 16 kHz, is first resampled to 16 kHz mono so everything is measured on the same ruler.

There is a nice detail here. If the very high frequencies are missing, that itself is a clue — it usually means the audio came down a narrow phone line (8 kHz telephony). VoxShield notices that and adjusts, rather than being fooled by it.

So now we have a wave, turned into a long list of sample numbers. But a raw list of numbers is hard to read. We need a better picture.

## Chapter 4.2 — The Spectrogram: A Picture of Sound

Here is a hard truth. A waveform, on its own, is almost useless to the eye.

Look at one and try to answer simple questions. Is this speech or music? Where did the person breathe? Is it a cloned voice? You cannot tell. The waveform only shows loudness over time. It hides *which frequencies* are inside the sound.

So we use something far more powerful. A **spectrogram**.

> In simple words: a spectrogram is a picture of sound — an X-ray that lets you see inside a voice.

### The three parts of the picture

A spectrogram shows three things at once.

- **Time** runs left to right. When did it happen?
- **Frequency** runs bottom to top. Low pitches at the bottom, high pitches at the top.
- **Brightness (color)** shows energy. Bright means strong sound at that frequency; dark means weak.

Think of a song. Your ear hears drums, guitar, and a singer all mixed together. A waveform blends them into one blur. A spectrogram pulls them apart and shows exactly which frequencies are active at each moment.

Just as a doctor uses an X-ray to see inside a body, VoxShield uses a spectrogram to see inside speech.

### How a fake looks different

Remember the fingerprints from Module 3? Many of them become *visible* here.

Look at the high frequencies, near the top of the picture. In a real voice, that region is rough and lively and a little uneven.

In a fake, the top of the picture often looks too clean. Too smooth. Too tidy. The vocoder's shortcut shows up as bands that are suspiciously regular where a real voice would be messy.

> In simple words: in a real voice the high bands look like a natural forest. In a fake they can look like a printed pattern.

VoxShield actually draws this. In its console it renders a spectrogram in "magma" colors — deep purples for quiet, bright oranges and yellows for strong energy — so a human reviewer can *see* the evidence, not just trust a score.

That matters. A number alone asks you to have faith. A picture lets a bank officer look with their own eyes.

But a picture is for humans. The detectors themselves need something tighter and more precise. That is where features come in.

## Chapter 4.3 — Feature Extraction: The 89 Numbers

Why not just feed the raw sound wave into the detectors and be done?

Because raw audio is enormous and mostly noise. Six seconds at 16 kHz is nearly a hundred thousand samples, and almost all of it is irrelevant to the one question we care about: real or fake?

So VoxShield does what every good forensic lab does. It extracts **features** — a small set of carefully chosen measurements that concentrate the useful evidence and throw away the rest.

> In simple words: we do not hand the detector the whole haystack. We hand it the needles.

VoxShield boils every call down to a **89-dimensional feature bank** — 89 numbers that together describe the voice. Let us see where they come from.

### LFCC — the even-ruler fingerprint

The first 40 numbers come from **LFCC**, which stands for **Linear-Frequency Cepstral Coefficients**.

Do not let the name scare you. It is a compact summary of the *shape* of the sound's spectrum — a fingerprint of which frequencies are strong and which are weak.

The word **linear** is the key. LFCC treats every frequency band as equally important, like a ruler with evenly spaced marks.

Why does that help? Because AI voices leave tiny artifacts spread across the *whole* frequency range, including the high parts that human hearing tends to ignore. By looking everywhere equally, LFCC keeps that forensic evidence instead of discarding it. This is why LFCC is a favorite in anti-spoofing research.

### CQCC — the zoom-lens fingerprint

The next 40 numbers come from **CQCC**, or **Constant-Q Cepstral Coefficients**.

CQCC also fingerprints the spectral shape, but it looks in a different way. It uses fine detail at low frequencies and broader detail at high ones — the way a piano keyboard spaces its notes.

> In simple words: LFCC is a camera with evenly spaced measurements. CQCC is a camera that automatically zooms in where more detail is needed.

Because the two cameras see differently, they catch different clues. LFCC might flag unusual spectral distortion; CQCC is especially good at vocoder and compression artifacts. Using both gives VoxShield a richer, more robust view than either alone.

### The 9 interpretable scalars

LFCC (40) plus CQCC (40) gives 80 numbers. The final **9** are the plain-language clues from Module 3 — the ones a human can actually understand and explain in a fraud report.

Here is what each one means.

| Scalar | What it measures |
| hf_energy_ratio | How much energy sits in the high band above ~6 kHz |
| hf_regularity | How machine-like and repetitive that high-band energy is |
| spectral_flatness | Whether the sound is tonal like a voice, or flat like noise |
| phase_reg | How unnaturally tidy the ripple timing (phase) is |
| f0_jitter | Tiny wobbles in pitch — present in real voices, missing in TTS |
| shimmer | Tiny wobbles in loudness — the voice's natural tremble |
| f0_voiced_ratio | How much of the clip is actual voiced speech |
| silence_ratio | How much of the clip is flat, dead silence |
| breath_score | How much natural breathing texture is present |

40 plus 40 plus 9 equals **89**. That is the feature bank — the same 89 numbers for every call.

> In simple words: LFCC and CQCC are the deep, expert fingerprints. The 9 scalars are the clues you can explain to your manager in one sentence.

### Why this design is honest

Notice what these 89 numbers give us. They are not a black box.

The five detectors read these features and vote, but because 9 of the numbers are human-readable, VoxShield can always point to *why* it flagged a call — "low jitter, too-regular high band, no breath." That is the explanation a bank needs before it acts on a customer.

And it acts fairly. VoxShield never auto-blocks a call. A high-risk score raises a human step-up, not an automatic rejection. The numbers inform a person; they do not replace one.

That is the whole pipeline in miniature. A vibration in the air becomes a wave, the wave becomes a picture, and the picture becomes 89 honest numbers.

From here, in the next module, those 89 numbers meet the five detectors that decide: real voice, or a shortcut wearing its disguise.
