# VoxShield — Generator Matrix (all 28) & Multi-Generator Plan

Training on **many generators** is the strongest lever on unseen-generator EER
(SAFE Challenge arXiv:2508.20983: dataset diversity → largest gains). This maps every entry in
`backend/registries/generators.json` to a concrete, runnable path.

## Tier 1 — runnable now (open/local, no key) — wire via `gen_fakes_multi.py`
| Engine | Registry | Deps | Notes |
|---|---|---|---|
| MMS-TTS | AI4Bharat | transformers | as, mai only voice coverage |
| Indic-Parler-TTS | AI4Bharat | transformers (installed) | **all 8 low-res**; our tokenizer fix |
| IndicF5 | AI4Bharat | transformers/indicf5 | 11 langs (as bn gu hi kn ml mr or pa ta te) |
| F5-TTS | SWivid | `pip install f5-tts` | zero-shot, needs ref clip |
| XTTS v1/v2 | Coqui | `pip install TTS` | multilingual multi-dataset |
| Kokoro-82M | hexgrad | `pip install kokoro` | English-centric |
| Piper | rhasspy | `piper` binary + onnx voice | many Indic voices |
| CosyVoice / Qwen3-TTS | Alibaba | large repos | zh-centric |
| VoxCPM2 / LongCat-Audio / Higgs / VibeVoice / OpenAudio | OpenBMB/Meituan/Boson/Microsoft/Fish | large repos | heavy |
| GPT-SoVITS / StyleTTS2 / OpenVoice / RVC / Seed-VC | community | various | cloning (need ref audio) |

## Tier 2 — API / proprietary (need keys)
| Engine | Provider | Env key |
|---|---|---|
| **Sarvam-TTS** | Sarvam AI | `SARVAM_API_KEY` (+ `SARVAM_TTS_URL`, `SARVAM_SPEAKER`) |
| ElevenLabs | ElevenLabs | `ELEVENLABS_API_KEY` |
| Cartesia (Sonic) | Cartesia | `CARTESIA_API_KEY` |
| Hume (Octave) | Hume | `HUME_API_KEY` |
| PlayHT | PlayHT | `PLAYHT_API_KEY` |

## Tier 3 — background / classical
- Griffin-Lim (baseline), Bark — low quality; already represented in the LOGO "hardest" set.

## What `gen_fakes_multi.py` does
For each language it runs every **available** engine (each in try/except → `[skip] reason`),
writes per-engine wavs under `data_fakes_multi/<lang>/<engine>/`, and merges them into one
`manifest.jsonl` that `run_round.sh` (via `FAKES_MANIFEST`) ingests. So the training corpus gains
generator diversity automatically as keys/deps are added — no code change.

## Expected effect
- More generators in **training** → higher **unseen-generator** generalization (the gap is the #1
  metric) → lower EER on the hard languages.
- API engines (Sarvam, ElevenLabs…) add *commercial-grade* fakes — the most valuable diversity,
  because our threat model is exactly high-quality commercial cloning.

## To unlock the API tier
Set the env keys on the DGX (`~/.config/voxshield.env`) then re-run `gen_fakes_multi.py`.
Sarvam is the priority (India-native, Indic coverage).
