#!/usr/bin/env bash
# VoxShield — install everything needed to run all 28 generators as fake sources.
# Run on the DGX:  bash setup_generators.sh            (open engines + hints)
#                  KEYS=1 bash setup_generators.sh      (also print API-key setup)
set -uo pipefail
PIP="$HOME/miniconda3/envs/voxshield/bin/pip"; [ -x "$PIP" ] || PIP=pip

echo "== 1. python engines (pip) =="
for pkg in "TTS" "f5-tts" "kokoro" "soundfile" "librosa" "transformers" "accelerate"; do
  $PIP install -q -U "$pkg" && echo "  ok   $pkg" || echo "  FAIL $pkg"
done

echo "== 2. piper (binary + Indic voices) =="
if ! command -v piper >/dev/null; then
  mkdir -p "$HOME/tools"; cd "$HOME/tools"
  # pip wheel exists for many platforms; fall back to release binary if it fails
  $PIP install -q piper-tts && echo "  ok   piper-tts (pip)" || \
    echo "  note: grab a piper release binary + put on PATH, then set PIPER_VOICE=/path/voice.onnx"
fi
echo "  voices: https://huggingface.co/rhasspy/piper-voices  (hi, bn, ... ) → export PIPER_VOICE=..."

echo "== 3. API keys (Sarvam + others) — add to ~/.config/voxshield.env =="
cat > "$HOME/.config/voxshield.generators.example" <<'EOF'
SARVAM_API_KEY=
SARVAM_TTS_URL=https://api.sarvam.ai/text-to-speech
SARVAM_SPEAKER=meera
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE=21m00Tcm4TlvDq8ikWAM
CARTESIA_API_KEY=
HUME_API_KEY=
PLAYHT_API_KEY=
DASHSCOPE_API_KEY=
EOF
echo "  wrote ~/.config/voxshield.generators.example"

echo "== 4. repo-based engines (clone when you want them) =="
cat <<'EOF'
  cosyvoice       git clone https://github.com/FunAudioLLM/CosyVoice
  voxcpm2         git clone https://github.com/OpenBMB/VoxCPM2
  longcat_audio   git clone https://github.com/meituan-longcat/LongCat-Audio
  higgs_audio     git clone https://github.com/boson-ai/higgs-audio
  vibevoice       git clone https://github.com/microsoft/VibeVoice
  gpt_sovits      git clone https://github.com/RVC-Boss/GPT-SoVITS
  styletts2       git clone https://github.com/yl4579/StyleTTS2
  openvoice       git clone https://github.com/myshell-ai/OpenVoice
  rvc             git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
  seed_vc         git clone https://github.com/Plachtaa/seed-vc
EOF

echo "== 5. verify availability =="
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
python backend/generator_adapters.py || true
echo "done."
