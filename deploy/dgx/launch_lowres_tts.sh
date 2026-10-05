#!/usr/bin/env bash
# VoxShield — PHASE 5 (real TTS): give the single-class languages a genuine spoof set
# using MMS-TTS (facebook/mms-tts-<code>), then retrain a two-class round.
#   bash launch_lowres_tts.sh                # 8 languages across selected GPUs, detached
#   bash launch_lowres_tts.sh --only nepali  # smoke-test one (foreground)
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_lowres_tts.sh
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

LANGS="bodo dogri kashmiri konkani manipuri nepali santali sindhi"
N=${N:-300}

worker(){ local L=$1 local DEV=${2:-0}
  { echo "==== lowres-tts $L (GPU $DEV) ===="
    if [ ! -f "data_fakes/${L}/.done_gen" ]; then
      python backend/gen_fakes_mms.py --lang "$L" --n "$N" --out "data_fakes/${L}" \
        && touch "data_fakes/${L}/.done_gen" || { echo "!! TTS gen failed $L"; exit 1; }
    fi
    local DATA="data/${L}"
    [ -d "$DATA" ] || { echo "!! real data dir missing: $DATA"; exit 1; }
    rm -f "checkpoints/${L}.done"
    FAKES_MANIFEST="$ROOT/data_fakes/${L}/manifest.jsonl" \
      CUDA_VISIBLE_DEVICES=$DEV bash run_round.sh "$L" --gpu "$DEV" --shards-end 0
    echo "==== lowres-tts $L done ===="
  } 2>&1 | tee -a "logs/lowres_tts_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  dev=${VIS[$s]}
  tmux new-session -d -s "vox5t_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_lowres_tts.sh' --only \$L $dev; done; echo 'LOWRES-TTS SLOT $s COMPLETE'"
  echo "  slot $s → GPUs[$dev] :$list"
done
echo "▶ LOW-RES real-TTS launched ($GPUS slots). logs: tail -f logs/lowres_tts_*.log"
