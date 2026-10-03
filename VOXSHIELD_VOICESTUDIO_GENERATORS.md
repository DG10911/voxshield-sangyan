# VoxShield — VoiceStudio Lab: locally-deployable generators (2026-09-30)

Open-source voice generators to run on the rented GPU to build our attack dataset,
ranked for **Indic support + telephony attack usefulness + permissive license**.
Plug each into `generator_adapter.py` (registry-linked). ⚠️ Verify licenses + Indic
claims at install time; some links may be stale.

## Install-first shortlist (Tier 1 — Indic-capable, permissive)
| # | Model | Type | VRAM | License | Indic | Note |
|---|---|---|---|---|---|---|
| 1 | **IndicF5** (AI4Bharat) | zero-shot clone | 6–8 GB | Apache-2.0 | **11 Indic langs** | 🥇 core Indic; near-human; `hf: ai4bharat/IndicF5` |
| 2 | **Indic Parler-TTS** | controllable TTS | 4–6 GB | Apache-2.0 | **21 Indic langs** | prosody/gender/style control; `hf: ai4bharat/indic-parler-tts` |
| 3 | **Fish-Speech / OpenAudio S2.1** | clone + TTS | 8–10 GB | Apache (open) | 9 Indic + 80 | ~90ms; cross-lingual; commercial tier is paid |
| 4 | **XTTS-v2** (Coqui) | zero-shot clone | 3–4 GB | CPML (research) | Hindi only | 6s clone, 17 langs; cross-lingual Hindi→Tamil |
| 5 | **CosyVoice2** | streaming clone | 6–8 GB | Apache-2.0 | limited (CJK) | streaming-first — good for realtime degradation tests |
| 6 | **Qwen3-TTS 0.6B** | clone + design | 0.6–1.7 GB | Apache-2.0 | no | tiny/fast, 49 timbres — voice diversity on constrained GPU |

**Recommended install stack for one 24 GB GPU:** IndicF5 (6) + Indic-Parler (4) + Fish-Speech (8) + Qwen3-TTS (0.6) ≈ fits a 4090/A100.
Quick install pattern: `git clone <repo> && pip install -r requirements.txt && huggingface-cli download <hf-id>`.

## Others worth knowing (diversity / edge)
F5-TTS (MIT, EN/ZH), StyleTTS2 (MIT, high quality, slow), GPT-SoVITS (MIT, few-shot), OpenVoice-v2 (MIT, VC), Higgs-Audio-v3 (Apache, SOTA Elo), Zonos (Apache), Chatterbox (MIT, optional watermark), Bark (MIT, slow), Piper (CPU-only, some Indic), MaskGCT (research, SOTA quality/slow).
**Avoid for our dataset:** MMS-TTS (CC-BY-**NC** — non-commercial), VibeVoice (watermarked + impersonation restrictions).

## Telephony degradation — we already own this half
**No open TTS embeds realistic telephony degradation.** Pipeline: synthesize clean →
degrade with our **`scenario_render.py`** (G.711 μ/A-law, 300–3400 Hz band-limit,
packet-loss/jitter, reverb, replay). That's exactly the local half of §25 we built.

## Registry mapping (feeds `registries/generators.json` via `generator_adapter.py`)
Each entry → provider · model · version · voice_cloning · cross_lingual · realtime ·
license · output_srs · watermark · vram_gb · indic_langs. IndicF5/Indic-Parler are the
priority additions (Indic + Apache + clean/no-watermark = ideal attack sources).

## Cross-lingual attack recipes to generate (our #1 hardness axis)
IndicF5: English voice → Hindi/Tamil clone · Fish-Speech: Hindi → Tamil/Bengali ·
XTTS-v2: Hindi → Tamil. These cross-lingual clones + G.711 render = our Worst-AI seed.
