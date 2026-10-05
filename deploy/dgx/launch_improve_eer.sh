#!/usr/bin/env bash
# VoxShield — EER-improvement pass for the hardest languages (urdu, odia, malayalam).
# Stronger AASIST + adversarial Conformer with more epochs, on the free GPUs, queued behind
# the low-res Indic-Parler jobs. Language orthogonalization (backend/language_orthogonalization.py)
# is the next hook; this run establishes the stronger-backbone baseline it will build on.
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_improve_eer.sh
#   bash launch_improve_eer.sh --only urdu 1
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

LANGS="urdu odia malayalam"
EPOCHS=${EPOCHS:-8}

evaldir(){ for d in "data/$1_eval" "data/$1"; do [ -d "$d/indicsynth" ] && { echo "$d"; return; }; done; echo ""; }

worker(){ local L=$1 DEV=${2:-0}
  { echo "==== improve $L (GPU $DEV, ${EPOCHS}ep) ===="
    local D; D=$(evaldir "$L")
    [ -z "$D" ] && { echo "!! no data for $L"; exit 1; }
    [ -f "checkpoints/aasist2_${L}/scores.csv" ] && echo "[skip] aasist2 $L" || \
      CUDA_VISIBLE_DEVICES=$DEV python backend/train_backend.py --arch aasist --data-root "$D" \
        --langs "$L" --holdout xtts --epochs "$EPOCHS" --out "checkpoints/aasist2_${L}"
    [ -f "checkpoints/adv2_${L}/scores.csv" ] && echo "[skip] adv2 $L" || \
      CUDA_VISIBLE_DEVICES=$DEV python backend/adversarial_train.py --arch conformer --attack pgd \
        --eps 0.005 --steps 5 --data-root "$D" --langs "$L" --holdout xtts --epochs "$EPOCHS" \
        --out "checkpoints/adv2_${L}"
    [ -f "checkpoints/aasist2_${L}/scores.csv" ] && \
      python backend/eval_c2_ablation.py --csv "checkpoints/aasist2_${L}/scores.csv" --tpr 0.95 \
        > "phase4/improve_c2_${L}.txt" 2>&1
    echo "==== improve $L done ===="
  } 2>&1 | tee -a "logs/improve_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

IFS=, read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  [ -z "${list// }" ] && continue
  dev=${VIS[$s]}
  tmux new-session -d -s "vox6_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_improve_eer.sh' --only \$L $dev; done; echo 'IMPROVE SLOT $s COMPLETE'"
  echo "  slot $s -> GPU $dev :$list"
done
echo "EER-improvement launched. logs: tail -f logs/improve_*.log"
