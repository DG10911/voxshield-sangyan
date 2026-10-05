# How to integrate ALL 28 generators into VoxShield

The framework is done: **`backend/generator_adapters.py`** registers all 28 with one interface
(`available()` / `synth(texts, out_dir)`), and the fake pipeline calls whichever are enabled.
Three steps: **(A) install**, **(B) keys**, **(C) run**.

## A · Install the open engines (one command, DGX)
```
bash deploy/dgx/setup_generators.sh
```
Installs: `TTS` (Coqui XTTS v1/v2), `f5-tts`, `kokoro`, `piper`, `transformers`, `librosa`, `accelerate`.

## B · Keys for the API engines
Copy `~/.config/voxshield.generators.example` → `~/.config/voxshield.env` and fill:
`SARVAM_API_KEY`, `ELEVENLABS_API_KEY`, `CARTESIA_API_KEY`, `HUME_API_KEY`, `PLAYHT_API_KEY`.

## C · Run multi-generator fakes + retrain
```
CUDA_VISIBLE_DEVICES=1,2,3 ENGINES=mms,parler,indicf5,bark,xtts_v2,f5,piper,kokoro,sarvam \
  bash deploy/dgx/launch_multigen.sh
```

## The 28 at a glance (what each needs)
| # | Generator | Kind | Enable with |
|---|---|---|---|
| 1 | ElevenLabs | api | `ELEVENLABS_API_KEY` |
| 2 | Fish Audio (OpenAudio-S2.1) | local | transformers |
| 3 | Cartesia Sonic | api | `CARTESIA_API_KEY` |
| 4 | Hume Octave | api | `HUME_API_KEY` |
| 5 | PlayHT | api | `PLAYHT_API_KEY` |
| 6 | Alibaba Qwen3-TTS | api/pkg | `DASHSCOPE_API_KEY` (dashscope) |
| 7 | OpenBMB VoxCPM2 | repo | clone repo |
| 8 | Meituan LongCat-Audio | repo | clone repo |
| 9 | Boson Higgs Audio | repo | clone repo |
| 10 | Microsoft VibeVoice | repo | clone repo |
| 11 | Coqui XTTS v1 | pkg | `pip install TTS` |
| 12 | Coqui XTTS v2 | pkg | `pip install TTS` |
| 13 | GPT-SoVITS | repo | clone repo |
| 14 | SWivid F5-TTS | pkg | `pip install f5-tts` |
| 15 | StyleTTS2 | repo | clone repo |
| 16 | Alibaba CosyVoice | repo | clone repo |
| 17 | MyShell OpenVoice | repo | clone repo |
| 18 | VoiceStudio (open-source) | repo | AGPL — clone |
| 19 | AI4Bharat MMS-TTS | pkg | transformers ✅ running |
| 20 | real (human) | n/a | label only |
| 21 | AI4Bharat IndicF5 | pkg | transformers |
| 22 | AI4Bharat Indic-Parler-TTS | pkg | ✅ running |
| 23 | Fish OpenAudio-S2.1 | pkg | transformers |
| 24 | **Sarvam-TTS** | **api** | **`SARVAM_API_KEY`** |
| 25 | RVC | repo | clone repo |
| 26 | Seed-VC | repo | clone repo |
| 27 | Piper | bin | `pip install piper-tts` + `PIPER_VOICE` |
| 28 | Kokoro-82M | pkg | `pip install kokoro` |

## Why this matters for EER
Training on **many generators** is the top lever on **unseen-generator** performance
(SAFE Challenge 2025). Adding commercial-grade fakes (**Sarvam, ElevenLabs**) is the highest-value
diversity because that *is* our threat model. Every engine you enable lands in the merged
manifest automatically — no code change.

## Verify availability anytime
```
python backend/generator_adapters.py      # prints OK/-- per generator with the reason
```
