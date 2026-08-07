# MODULE 8 — Datasets and Our Own Fine-Tuned Indic Model

## Chapter 8.1 — The Data VoxShield Learned From

A detector is only as good as what it learned from.

If you only ever showed a child pictures of cats, they would call every animal a cat. To teach VoxShield well, we had to show it many real voices and many fake voices — and be very careful about how we tested it.

LEARN:
- The four kinds of data VoxShield learned from
- Why one dataset was deliberately kept "hidden"
- What "no leakage" means and why it makes our numbers believable

### The four datasets

Here is what VoxShield learned from, and how each was used.

| Dataset | What it is | How we used it |
|---|---|---|
| In-the-Wild | Public English data, real and fake voices | **Held out** for honest testing → 5.9% EER |
| ASVspoof / WaveFake | Public English spoofing data | English training |
| IndicVoices | 4,000 real Indic voices, 10 languages, from AI4Bharat / IIT-Madras and Bhashini | Real Indian speech for training |
| MMS-TTS fakes | 4,000 Indic fakes we synthesized ourselves | Fake Indian speech for training |

The first two are English. The last two are Indian. That mix matters, because voice fraud in India happens in Hindi, Tamil, Telugu, Bengali, and more — not just English.

> In simple words: we taught VoxShield with both English and Indian voices, real and fake.

### The most important idea: no leakage

Now here is the part that makes our results trustworthy. Please read it slowly.

Imagine a student who steals the exam paper the night before. He scores 100%. But that score is a lie — he did not really learn anything. He just memorized the answers.

Machine learning models can cheat in exactly this way. If a model is **tested on the same data it trained on**, its score looks amazing but means nothing. This cheating is called **data leakage**.

We refused to let VoxShield cheat.

The **In-the-Wild** dataset was **never** used for training. Not once. We locked it away and only used it for the final exam. The split was clean and disjoint: **480 clips for training, 320 completely separate clips for testing**, with a fixed seed so anyone can reproduce it.

> In simple words: VoxShield's final test was on voices it had never seen — like a real exam with no leaked answers.

This is **why** the headline number survives scrutiny. When we say **5.9% EER** (roughly 94% accuracy on this honest test), it is a real grade on unseen data — not a memorized one.

Many flashy demos quietly skip this step. We put it front and center, because a bank should trust a number that was earned honestly.

## Chapter 8.2 — The Models We Started From

VoxShield did not build every brain from scratch. That would take years and enormous computing power.

Instead, like most modern AI, it stands on the shoulders of **open-source models** — powerful, freely available starting points trained by the wider research community.

LEARN:
- What a "pretrained model" is
- Which open models VoxShield builds on
- Roughly how big each one is

### What "pretrained" means

A **pretrained model** is a brain someone else already trained on huge amounts of audio. It already understands the general shape of speech.

We take that brain and adapt it to our specific job. It is like hiring an experienced musician instead of teaching someone music from birth. They already know the basics; you just teach them your song.

The size of a model is measured in **parameters** — the little adjustable knobs inside it. More parameters usually means more capacity, but also more computing cost.

### The starting points

| Model | What it does | Rough size |
|---|---|---|
| Deepfake-V2 (wav2vec2-base) | Deepfake speech detection | ~95M params |
| XLS-R-300M | Multilingual speech understanding | ~300M params |
| DistilHuBERT | Fast, compact speech model | ~24M params |
| ECAPA-TDNN | Speaker verification (voiceprints) | ~22M params |
| Whisper base / small | Speech recognition, language-ID | ~74M / ~244M params |
| MMS-TTS | Text-to-speech (to make Indic fakes) | ~145M each |

> In simple words: these are strong, free brains built by the community. We adapted them instead of starting from zero.

Notice MMS-TTS at the bottom. That one is a **fake-voice generator**. We used it as a tool — to create the Indian fake voices we needed to teach our detector. More on that next.

## Chapter 8.3 — How We Built Our Own Indic Detector Overnight

This is the story we are most proud of. We will tell it plainly and honestly, including the parts that are not perfect.

LEARN:
- Why the base system struggled with Indian fakes
- How the team trained a custom Indic detector overnight
- What the results were — and the honest limit on them

### The problem

VoxShield's original five detectors were mostly trained on English. When Indian-language fakes arrived, they struggled.

The frozen base ensemble caught only about **42%** of Indic fakes. That means more than half slipped through. Not good enough for a bank.

We added a **language router** — detect the Indian language, then use tuning meant for Indic audio. That lifted catching-power to **82%**.

Better. But still not good enough. One in five fakes was still getting past.

> In simple words: our first system was trained on English, so it missed too many Indian fakes.

### The overnight build

So the team did something bold. Instead of just talking about a fix, they **built** one.

Here is exactly what happened:

1. **Rented a GPU.** A single RTX 5090, for about **30 minutes**, costing about **$2**.
2. **Gathered the data.** 4,000 real Indian voices from IndicVoices, plus 4,000 Indian fakes we synthesized with MMS-TTS — across **10 languages**.
3. **Fine-tuned XLS-R-300M.** We took that 300-million-parameter multilingual brain and trained it on our Indian real-vs-fake data. Settings: **3 epochs, batch size 8, learning rate 1e-5, with codec augmentation** (so it learns to survive phone-line distortion).
4. **Deployed it live.** The finished model went straight into the running system.

Two dollars. Thirty minutes. A brand-new custom detector for Indian voices.

> In simple words: for about the price of a cup of coffee, the team trained and shipped a detector made just for Indian speech.

### How it plugs in safely

The custom model is deployed as an **env-gated Indic booster** — a switch the system can turn on.

Here is the clever, careful design. The booster **only raises the score on confident Indic fakes**. It never lowers a score, and it never speaks up unless it is very sure.

Why design it this way? Because of the golden rule from Module 7: do not wrongly accuse real customers. A booster that can only add evidence of a fake — and only when confident — **cannot** create new false alarms on genuine Indian speakers.

> In simple words: the booster can only catch more fakes. By design, it cannot start blocking real people.

### The results

On a held-out Indic evaluation, the custom model scored:

- **0% false positives** on real Indian speakers
- **100% recall** on the fake engine it was trained against (MMS-TTS)

And it was **verified live**, not just on paper:

- A genuine Tamil voice → **LOW**, score 0.06 (correctly seen as real)
- A Tamil fake → **HIGH**, with a **+indic-boost** tag (correctly caught)

Meanwhile, the English performance stayed exactly where it was: **5.9% EER, unchanged**. The new Indian skill did not cost us any English skill.

### The honest caveat

Now the honest part, because honesty is the whole point of this course.

That **100% recall is in-distribution**. It means 100% against the specific fake engine we trained on — **MMS-TTS**.

The real world has many other voice-cloning engines: ElevenLabs, NVIDIA, and more. Against a brand-new engine the model has never seen, we should expect lower than 100%. Real-world coverage **broadens as more TTS engines are added** to the training fakes.

> In simple words: 100% means 100% against the fakes we trained on — not a promise against every future faker.

We say this openly. A number without its context is a half-truth, and a bank deserves the full truth.

### Why this story matters

Here is the real lesson, beyond the numbers.

The whole pipeline is **committed and repeatable**. It is written down in a runbook. Anyone on the team can rent a GPU, run it again, add new fake engines, and ship an updated detector.

That is the point. Many teams talk about what they *could* build. This team took a real gap — weak Indic coverage — rented a GPU for two dollars, trained a real model overnight, deployed it live, and verified it on a real phone.

> In simple words: this proves the team can execute, not just talk.

And that is the strongest thing a young system can show a bank: not a perfect score, but a proven, repeatable way to keep getting better.
