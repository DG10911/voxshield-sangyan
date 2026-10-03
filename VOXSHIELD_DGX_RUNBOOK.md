# VoxShield — DGX A100 Runbook (end-to-end)
### Bhashini + NeMo/ECAPA + the fusion detector, on one call. Updated 2026-10-01.

## 0 · One-time env (add to `~/.bashrc`)
```bash
export HF_TOKEN=hf_<your real token>
export BHASHINI_USER_ID=<REDACTED>
export BHASHINI_API_KEY=<REDACTED>
export BHASHINI_INFERENCE_KEY=<REDACTED>
export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")   # fixes DGX TLS
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"
export DIARIZATION_BACKEND=nemo        # pyannote | nemo | deepgram | light
export HF_HOME=$HOME/hf_cache
```
Then `source ~/.bashrc`.

## 1 · Install (verified working on this DGX)
```bash
python -m pip install --upgrade pip
python -m pip install pyannote.audio speechbrain
python -m pip install nemo_toolkit[asr]        # NeMo Sortformer + TitaNet
conda install -n voxshield -y -c conda-forge ffmpeg
```

## 2 · Copy the code
```bash
# from your Mac
scp -r backend voxshield_console.html dgx:~/voxshield/
```

## 3 · Self-tests (all green on the DGX)
```bash
cd ~/voxshield
python backend/diarization.py        # -> nemo-sortformer (or pyannote)
python backend/speaker_engine.py     # available: {'ecapa': True, 'nemo': True, ...}
python backend/bhashini_smoketest.py # Bhashini connected
```

## 4 · End-to-end on a real call
```bash
# put a WAV on the DGX (16 kHz mono preferred)
scp your_call.wav dgx:~/voxshield/
python backend/dgx_e2e.py ~/voxshield/your_call.wav
# verify the caller's voice against an enrolled reference:
python backend/dgx_e2e.py ~/voxshield/your_call.wav --enroll ~/voxshield/known_voice.wav
```
Prints: **pipeline · language (Bhashini ALD) · transcript (Bhashini ASR) · diarization (NeMo/pyannote) · verdict (fusion) · speaker vs enrolled (ECAPA)**.

## 5 · Provider matrix (verified)
| Task | Working backend | Alternatives | Env key |
|---|---|---|---|
| Language (ALD) / ASR / TTS / NMT / TLD / streaming / voice-clone | **Bhashini** ✅ | — | `BHASHINI_*` |
| Speaker **diarization** | **NeMo Sortformer** ✅ | pyannote 3.1/community-1, **Deepgram** API, built-in `light` | `DIARIZATION_BACKEND`, `DEEPGRAM_API_KEY` |
| Speaker **verification** | **SpeechBrain ECAPA** ✅ | NeMo TitaNet, Phonexia API, local | `PHONEXIA_URL` |

## 6 · Known-good results on this DGX (2026-10-01)
- Language: ALD `hi`; ASR transcript correct; streaming ASR works; TTS/voice-clone/denoiser work.
- Diarization: `nemo-sortformer` → **2 speakers** on a male/female clip.
- Verification (ECAPA): SAME 0.40 ≥ 0.35 → `SAME_SPEAKER`; different 0.22 → `DIFFERENT_SPEAKER`.
- Bhashini `speaker-diarization`/`language-diarization` = 500 (server) → superseded by the above.

## 7 · Notes
- pyannote optional: accept `pyannote/speaker-diarization-community-1` (+ `segmentation-3.0`, `embedding`) terms to enable it.
- `speechmatics`/`phonexia` adapters are stubs until you add keys (add-ons in `diarization.py` / `speaker_engine.py`).
- Rotate the Bhashini + HF tokens (shared in chat).
