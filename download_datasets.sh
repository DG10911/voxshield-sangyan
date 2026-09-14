#!/usr/bin/env bash
#
# VoxShield dataset downloader → KIOXIA SSD
# ------------------------------------------------------------------
# Verified 2026-09-14. HF repo IDs confirmed live (200 / gated) via API.
# SSD: /Volumes/KIOXIA  (802 GB free at time of writing).
# HF auth: logged in as dg10911. Gated sets need "Agree and access" clicked
#          once on the dataset's HF page while logged in.
#
# Usage:
#   bash download_datasets.sh            # runs the P0 + P1 active block
#   Edit INDIC_LANGS below to pick which IndicSynth languages to pull.
#
# Tooling: uses the venv hf CLI. No wget/aria2c on this Mac (curl only).
# ------------------------------------------------------------------
set -u

export VOXDATA=/Volumes/KIOXIA/voxdata
HF=/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/.venv_voxshield/bin/hf
export HF_HUB_ENABLE_HF_TRANSFER=0   # set 1 only if you `pip install hf_transfer`

mkdir -p "$VOXDATA"

hr(){ echo "------------------------------------------------------------------"; }
space(){ echo "[disk] $(df -h /Volumes/KIOXIA | tail -1 | awk '{print $4" free of "$2}')"; }

echo "VoxShield dataset download → $VOXDATA"
space
hr

# ==================================================================
# ⚠️  SIZE REALITY
#   IndicSynth FULL = 845 GB (bigger than your 802 GB free!). It is
#   organized per-language, so we pull ONLY the languages you pick.
#   Per-language sizes (GB): Sanskrit 167, Tamil 148, Punjabi 100,
#   Telugu 91, Kannada 68, Hindi 56, Gujarati 50, Marathi 42, Urdu 37,
#   Bengali 33, Malayalam 24, Odia 23.
# ==================================================================

# --- Pick your IndicSynth languages here (VoxShield core = Hi/Ta/Bn/Mr) ---
# Default below ≈ 279 GB (Hindi 56 + Tamil 148 + Bengali 33 + Marathi 42).
# Trim Tamil to save 148 GB if space is tight.
INDIC_LANGS=("Hindi" "Tamil" "Bengali" "Marathi")

# ============================ P0 — INDIC FAKES ====================
hr; echo "[P0] IndicSynth (ACL 2025) — synthetic Indic voices [open, gated=False]"
echo "     https://huggingface.co/datasets/vdivyasharma/IndicSynth"
INCLUDE_ARGS=()
for L in "${INDIC_LANGS[@]}"; do INCLUDE_ARGS+=(--include "${L}/*"); done
INCLUDE_ARGS+=(--include "README.md")
"$HF" download vdivyasharma/IndicSynth --repo-type dataset \
    "${INCLUDE_ARGS[@]}" \
    --local-dir "$VOXDATA/indicsynth"
space

# Indic-CodecFake — repo id NOT reliably verified from a live HF page.
# Project page: https://helixometry.github.io/IndicFake/  (ACL 2026)
# CONFIRM the exact HF/Zenodo id before uncommenting:
# "$HF" download <VERIFY_ID> --repo-type dataset --local-dir "$VOXDATA/indic_codecfake"

# BanglaFake (Bengali) — arXiv 2505.10885; confirm HF/GitHub host before use.
# HAV-DF (Hindi A/V) — arXiv 2411.15457; multimodal, lower priority for audio-only.

# ==================== P1 — MULTILINGUAL + CODEC ===================
hr; echo "[P1] CodecFake+ — 101 GB, 1.42M clips, 30+ codecs [MIT, open]"
echo "     https://huggingface.co/datasets/CodecFake/CodecFake_Plus_Dataset"
"$HF" download CodecFake/CodecFake_Plus_Dataset --repo-type dataset \
    --local-dir "$VOXDATA/codecfake_plus"
space

hr; echo "[P1] DFADD — 42.7 GB, diffusion/flow-matching TTS fakes [MIT, open]"
echo "     https://huggingface.co/datasets/isjwdu/DFADD"
"$HF" download isjwdu/DFADD --repo-type dataset \
    --local-dir "$VOXDATA/dfadd"
space

hr; echo "[P1] FLEURS — Indic real speech (small, for real class / eval) [CC-BY, open]"
echo "     https://huggingface.co/datasets/google/fleurs"
for cfg in hi_in ta_in bn_in mr_in te_in; do
  "$HF" download google/fleurs --repo-type dataset \
      --include "data/${cfg}/*" \
      --local-dir "$VOXDATA/fleurs"
done
space

hr; echo "P0 + P1 active block complete."
space
echo "Estimated pulled ≈ 279 (IndicSynth Hi/Ta/Bn/Mr) + 101 (CodecFake+) + 43 (DFADD) + ~15 (FLEURS) ≈ 438 GB"
hr

# ============================================================================
# P2 / P3 — OPT-IN. Uncomment what you want; re-check `df -h /Volumes/KIOXIA`.
# ============================================================================

# --- P2 English / general deepfake benchmarks (cross-dataset generalization) ---
# ASVspoof5 (2024) — 142 GB, English, 32 attacks + adversarial [open mirror]
# "$HF" download jungjee/asvspoof5 --repo-type dataset --local-dir "$VOXDATA/asvspoof5"
#
# SpoofCeleb — 134 GB [GATED: needs institutional (non-gmail) email approval; gmail likely rejected]
# "$HF" download jungjee/spoofceleb --repo-type dataset --local-dir "$VOXDATA/spoofceleb"
#
# ASVspoof 2021 DF + LA (Zenodo; get exact filenames from the record page first):
# curl -L -O https://zenodo.org/records/4835108/files/<FILE>   # DF
# curl -L -O https://zenodo.org/records/4837263/files/<FILE>   # LA
#
# ST-Codecfake (bilingual EN+ZH, 11 codecs) — Zenodo 14631091 (confirm filenames):
# curl -L -O https://zenodo.org/records/14631091/files/<FILE>
#
# LibriSeVoc (6 vocoders, English) — Zenodo 15127251 (HF stub is empty):
# curl -L -O https://zenodo.org/records/15127251/files/<FILE>
#
# FoR (Fake-or-Real), English — York U direct (verify links resolve):
# curl -L -o "$VOXDATA/for/for-norm.tar.gz" https://bil.eecs.yorku.ca/share/for-norm.tar.gz

# --- P3 extra Indic REAL speech (real class + TTS seed) ---
# Common Voice 17 Indic subsets [GATED: click accept on the HF page first]
# for lang in hi ta bn mr te; do
#   "$HF" download mozilla-foundation/common_voice_17_0 --repo-type dataset \
#       --include "audio/${lang}/*" --include "transcript/${lang}/*" \
#       --local-dir "$VOXDATA/common_voice_17"
# done
#
# AI4Bharat real speech (Kathbath auto-approves; IndicVoices-R & IndicSUPERB are gated):
# "$HF" download ai4bharat/Kathbath --repo-type dataset --local-dir "$VOXDATA/kathbath"
# "$HF" download ai4bharat/IndicVoices-R --repo-type dataset --local-dir "$VOXDATA/indicvoices_r"   # gated
# "$HF" download ai4bharat/indicsuperb --repo-type dataset --local-dir "$VOXDATA/indicsuperb"       # gated

# ============================================================================
# TTS / VOICE-CLONE MODELS — self-host to GENERATE new diverse fakes
# (models, not datasets → default --repo-type model). All verified live.
# ============================================================================
# mkdir -p "$VOXDATA/models"
# "$HF" download ai4bharat/IndicF5            --local-dir "$VOXDATA/models/indicf5"          # Indic flow-matching TTS
# "$HF" download ai4bharat/indic-parler-tts   --local-dir "$VOXDATA/models/indic-parler-tts" # Indic prompt TTS
# "$HF" download coqui/XTTS-v2                --local-dir "$VOXDATA/models/xtts-v2"          # multilingual clone (CPML non-commercial)
# "$HF" download SWivid/F5-TTS               --local-dir "$VOXDATA/models/f5-tts"           # flow-matching
# "$HF" download fishaudio/fish-speech-1.5   --local-dir "$VOXDATA/models/fish-speech"      # codec-LM clone
# "$HF" download amphion/MaskGCT             --local-dir "$VOXDATA/models/maskgct"          # masked-codec
# "$HF" download suno/bark                   --local-dir "$VOXDATA/models/bark"             # multilingual (incl Hindi)
# "$HF" download myshell-ai/OpenVoiceV2      --local-dir "$VOXDATA/models/openvoice-v2"     # tone-color clone

echo "Done. Re-run with P2/P3 lines uncommented to add more."
