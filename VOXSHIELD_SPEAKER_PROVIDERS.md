# VoxShield — Speaker Diarization & Verification Providers (Bhashini-independent)
### Roadmap §8/§10 · added 2026-10-01 — replaces the broken Bhashini diarization path

Bhashini's `speaker-diarization` / `language-diarization` return HTTP 500 on every service ID
and clip length, and `speaker-verification` only self-matches synthetic audio. So VoxShield now
uses **provider-agnostic engines** with best-in-class alternatives + a dependency-free fallback.

## Code
- **`backend/diarization.py`** — `diarize(y, sr, backend="auto")` → `{backend, n_speakers, segments}`
- **`backend/speaker_engine.py`** — `embed / verify / enroll / verify_against / available`
- Wired: `orchestrate.run(..., use_diarization=True)`; `/api/analyze?diarization=true`; `/api/health` → `speaker_backends`.

## Diarization providers
| Backend | Quality | Licence | Install | Notes |
|---|---|---|---|---|
| **pyannote.audio 3.1 / community-1** ⭐ | SOTA (VoxConverse ~8–11% DER) | MIT | `pip install pyannote.audio` + accept HF terms + `HF_TOKEN` | no speaker-count ceiling; GPU |
| **NVIDIA NeMo Sortformer** | strong, streaming | NVIDIA | `pip install nemo_toolkit[asr]` | DGX-native; ≤4 speakers; offline+streaming |
| **NeMo clustering** (MarbleNet+TitaNet) | strong | NVIDIA | same | flexible count |
| **VibeVoice** | best 6–14 spk (2026 bench) | research | `pip install` (repo) | meeting-scale |
| **3D-Speaker** (Alibaba) | SOTA toolkit | Apache | `pip install 3d-speaker`/repo | diarization + verification + CAM++ |
| **Deepgram / Speechmatics / Gladia** (API) | commercial | paid | REST | zero-setup; telephony channels |
| **built-in `light`** ✅ works now | approx (VAD + cosine clustering) | in-repo | none | numpy-only fallback, always available |

## Verification / enrollment providers
| Backend | Quality | Licence | Install | Notes |
|---|---|---|---|---|
| **SpeechBrain ECAPA-TDNN** ⭐ | VoxCeleb EER ~0.8–1% | Apache-2.0 | `pip install speechbrain` | easiest strong default |
| **NVIDIA NeMo TitaNet-L** ⭐ | SOTA | NVIDIA | `pip install nemo_toolkit[asr]` | DGX-native |
| **WeSpeaker** (ResNet-293) | SOTA | Apache | `pip install wespeaker` | production toolkit |
| **Kiwano** (fwSE-ResNet-200) | best EER (0.46% VoxCeleb1-O, 2026) | open | repo | research grade |
| **3D-Speaker ERes2Net** | strong | Apache | repo | Indic/Chinese tested |
| **Phonexia Speech Platform** (API, on-prem) | forensic-grade, **channel-independent (GSM/VoLTE/VoIP), language-independent, 3 s min speech** | commercial | REST/gRPC | **best fit for telephony fraud**; `PHONEXIA_URL` |
| **ID R&D / Veridas / Auraya** (API) | commercial | paid | REST | alternative biometrics vendors |
| **built-in `local`** ✅ works now | weak (spectral+pitch) | in-repo | none | always-available fallback |

## Recommended for VoxShield (Indic telephony, on-prem DGX)
1. **Diarization → pyannote.audio 3.1** (primary) + **NeMo Sortformer** (streaming/telephony ≤4 spk).
2. **Verification → SpeechBrain ECAPA-TDNN** (default) or **NeMo TitaNet** (DGX); **Phonexia** for forensic/telephony deployments.
3. **Fallback → built-in** `light` diarizer + `local` embeddings (works offline, no keys).

## Install on the DGX
```bash
pip install pyannote.audio                  # accept pyannote/segmentation-3.0 + speaker-diarization-3.1 terms
pip install speechbrain                     # ECAPA-TDNN
pip install nemo_toolkit[asr]               # TitaNet + Sortformer (DGX-native)
# then: python backend/diarization.py && python backend/speaker_engine.py
```
Auto-selection is best-first (`pyannote → nemo → light`, `ecapa → nemo → phonexia → local`); if a
backend isn't installed it silently falls back, so the pipeline never breaks.

## Language note
Speaker identity + diarization are **language-independent** (voice traits, not words) — pyannote/ECAPA
train on multilingual data and work on Indic audio without Indic-specific training.
