#!/usr/bin/env bash
# VoxShield — multi-generator augmentation: dispatch every available generator per language,
# merge the fakes, and retrain. More generator diversity -> better unseen-generator EER.
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_multigen.sh
#   bash launch_multigen.sh --only hindi 1
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
export COQUI_TOS_AGREED=1
export SSL_CERT_FILE=${SSL_CERT_FILE:-$HOME/miniconda3/envs/voxshield/lib/python3.11/site-packages/certifi/cacert.pem}
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
export ENGINE_TIMEOUT=900
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

LANGS="${LANGS:-hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi urdu sanskrit bodo dogri kashmiri konkani manipuri nepali santali sindhi}"
N=${N:-200}
ENGINES=${ENGINES:-sarvam,cartesia,mms}

evaldir(){ for d in "data/$1_eval" "data/$1"; do [ -d "$d/indicsynth" ] && { echo "$d"; return; }; done; echo ""; }

worker(){ local L=$1 DEV=${2:-0}
  { echo "==== multigen $L (GPU $DEV) ===="
    local OUT="data_fakes_multi/${L}"
    python backend/gen_fakes_multi.py --lang "$L" --n "$N" --out "$OUT" --engines "$ENGINES"
    local D; D=$(evaldir "$L"); [ -z "$D" ] && { echo "!! no real data $L (skipping train)"; exit 0; }
    rm -f "checkpoints/${L}.done"
    FAKES_MANIFEST="$ROOT/${OUT}/manifest.jsonl" \
      CUDA_VISIBLE_DEVICES=$DEV bash run_round.sh "$L" --gpu "$DEV" --shards-end 0
    echo "==== multigen $L done ===="
  } 2>&1 | tee -a "logs/multigen_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

IFS=, read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  [ -z "${list// }" ] && continue
  dev=${VIS[$s]}
  tmux new-session -d -s "vox8_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_multigen.sh' --only \$L $dev; done; echo 'MULTIGEN SLOT $s COMPLETE'"
  echo "  slot $s -> GPU $dev :$list"
done
echo "MULTIGEN launched. logs: tail -f logs/multigen_*.log"
