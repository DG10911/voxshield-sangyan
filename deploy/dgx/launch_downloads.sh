#!/usr/bin/env bash
# VoxShield — PHASE 0: pull ALL remaining models + datasets to the DGX, detached.
# Parallel, resume-safe (hf skips completed files), logs per target. Leave and return.
#
# Usage:  bash launch_downloads.sh            # models + a bounded dataset sample
#         FULL=1 bash launch_downloads.sh     # attempt full datasets (multi-TB, ~days)
#         MODELS_ONLY=1 bash launch_downloads.sh
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}
[ -f "$ENVF" ] && . "$ENVF"
HF=$(command -v hf || command -v huggingface-cli)
[ -n "$HF" ] || { echo "!! hf CLI missing"; exit 1; }
MODELS=${MODEL_ROOT:-$ROOT/models}; DATA=${DATA_ROOT:-$ROOT/data_pull}
mkdir -p "$MODELS" "$DATA" logs
FULL=${FULL:-0}; MODELS_ONLY=${MODELS_ONLY:-0}
JOBS=${JOBS:-4}                       # concurrent downloads
export HF_HUB_ENABLE_HF_TRANSFER=1

# ---- models (support + generators) ----
MODELS_LIST=(
  "bharatgenai/sooktam2"
  "ai4bharat/indic-conformer-600m-multilingual"
  "ai4bharat/indicwav2vec_v1_hindi" "ai4bharat/indicwav2vec_v1_bengali"
  "ai4bharat/indicwav2vec_v1_marathi" "ai4bharat/indicwav2vec_v1_gujarati"
  "ai4bharat/indicwav2vec_v1_tamil" "ai4bharat/indicwav2vec_v1_telugu"
  "ai4bharat/indicwav2vec_v1_odia"
)
dl(){ local kind=$1 repo=$2 extra=${3:-}; local name=${repo//\//__}
  local log="logs/dl_${kind}_${name}.log"
  [ -e "$DATA/.done_${kind}_${name}" ] && { echo "[skip] $name"; return 0; }
  echo "▶ $kind $repo"
  if [ "$kind" = model ]; then
    "$HF" download "$repo" --local-dir "$MODELS/$name" $extra >>"$log" 2>&1 && touch "$DATA/.done_${kind}_${name}" || echo "!! $repo failed (see $log)"
  else
    "$HF" download "$repo" --repo-type dataset --local-dir "$DATA/$name" $extra >>"$log" 2>&1 && touch "$DATA/.done_${kind}_${name}" || echo "!! $repo failed (see $log)"
  fi
}

# ---- datasets ----
DATASETS_LIST=(
  "ai4bharat/Shrutilipi" "ARTPARK-IISc/Vaani" "ai4bharat/Rasa"
  "ai4bharat/indicvoices_r" "ai4bharat/Lahaja" "ai4bharat/Svarah"
  "ai4bharat/MANGO" "ai4bharat/Aksharantar" "ai4bharat/Spoken-Tutorial"
  "mozilla-foundation/common_voice_17_0"
  "JunXueTech/RTCFake"                 # real-time-communication deepfakes (ACL 2026)
)
# huge / full-only sets (ASVspoof 5 ≈ 142 GB of tar files — not shard-samplable)
BIG_LIST=(
  "jungjee/asvspoof5"                  # HF mirror of the ASVspoof 5 database
)
# bounded sample for the multi-hundred-GB sets unless FULL=1
sample(){ [ "$FULL" = "1" ] && echo "" || echo "--include */train-0000*-of-*"; }

# launch downloads in the background (JOBS at a time)
n=0
for m in "${MODELS_LIST[@]}"; do dl model "$m" & n=$((n+1)); [ $((n%JOBS)) -eq 0 ] && wait; done
wait
if [ "$MODELS_ONLY" = "1" ]; then echo "models done -> $MODELS"; exit 0; fi
n=0
for d in "${DATASETS_LIST[@]}"; do dl dataset "$d" "$(sample)" & n=$((n+1)); [ $((n%JOBS)) -eq 0 ] && wait; done
wait
if [ "$FULL" = "1" ]; then
  for d in "${BIG_LIST[@]}"; do dl dataset "$d" "" & done; wait
fi

echo "── downloads finished ──"
du -sh "$MODELS" "$DATA" 2>/dev/null
echo "fills : ${MODELS_LIST[*]}"
echo "sets  : ${DATASETS_LIST[*]}"
echo "note  : RTCFake / Indic-CodecFake / ASVspoof 5 are not on HF — pull via AIKosh (pull.py) or their portals."
