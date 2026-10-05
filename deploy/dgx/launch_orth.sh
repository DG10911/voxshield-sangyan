#!/usr/bin/env bash
# VoxShield — C5: orthogonalized XLS-R probe for the hard languages (urdu, odia, malayalam).
# Extracts frozen XLS-R embeddings, removes the language subspace (language_orthogonalization),
# trains a linear probe, and reports EER with/without orthogonalization.
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_orth.sh
#   bash launch_orth.sh --only urdu 1
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

LANGS="urdu odia malayalam"
MODEL=${MODEL:-facebook/wav2vec2-large-xlsr-53}
LIMIT=${LIMIT:-3000}

evaldir(){ for d in "data/$1_eval" "data/$1"; do [ -d "$d/indicsynth" ] && { echo "$d"; return; }; done; echo ""; }

worker(){ local L=$1 DEV=${2:-0}
  { echo "==== orth $L (GPU $DEV) ===="
    local D; D=$(evaldir "$L"); [ -z "$D" ] && { echo "!! no data $L"; exit 1; }
    CUDA_VISIBLE_DEVICES=$DEV python backend/orth_probe.py --model "$MODEL" --data-root "$D" \
      --langs "$L" --holdout xtts --limit-per "$LIMIT" --out "checkpoints/orth_${L}"
    echo "==== orth $L done ===="
  } 2>&1 | tee -a "logs/orth_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

IFS=, read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  [ -z "${list// }" ] && continue
  dev=${VIS[$s]}
  tmux new-session -d -s "vox7_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_orth.sh' --only \$L $dev; done; echo 'ORTH SLOT $s COMPLETE'"
  echo "  slot $s -> GPU $dev :$list"
done
echo "ORTH probe launched. logs: tail -f logs/orth_*.log"
