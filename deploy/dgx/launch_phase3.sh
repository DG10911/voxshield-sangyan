#!/usr/bin/env bash
# VoxShield — PHASE 3: fix the "genuine-only" languages (no spoof set).
# For each: generate MMS-TTS fakes -> inject into the round -> retrain -> eval.
# Detached, GPU-pinned, parallel, resume-safe. Leave and return.
#
# Usage:  bash launch_phase3.sh                 # 10 languages across GPUs
#         N=500 GPUS=4 bash launch_phase3.sh     # more fakes, 4 GPUs
#         bash launch_phase3.sh --only manipuri
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}
[ -f "$ENVF" ] && . "$ENVF"

GPUS=${GPUS:-8}; N=${N:-300}
LANGS="assamese bodo dogri kashmiri konkani maithili manipuri nepali santali sindhi"
mkdir -p logs data_fakes
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

worker(){ # $1 lang
  local L=$1
  exec > >(tee -a "logs/phase3_${L}.log") 2>&1
  echo "==== phase3 $L ===="
  if [ ! -f "data_fakes/${L}/.done_gen" ]; then
    python backend/gen_fakes_mms.py --lang "$L" --n "$N" --out "data_fakes/${L}" \
      && touch "data_fakes/${L}/.done_gen" || { echo "!! gen failed for $L"; return 1; }
  fi
  rm -f "checkpoints/${L}.done"                 # allow retrain
  FAKES_MANIFEST="$ROOT/data_fakes/${L}/manifest.jsonl" \
    bash run_round.sh "$L" --gpu "${CUDA_VISIBLE_DEVICES:-0}" --shards-end 0
  echo "==== phase3 $L done ===="
}

case "${1:-}" in
  --only) worker "${2:?lang}"; exit $?;;
esac

read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  tmux new-session -d -s "vox3_slot$s" \
    "cd $ROOT; export N=$N; for L in $list; do CUDA_VISIBLE_DEVICES=$s bash '$ROOT/launch_phase3.sh' --only \$L; done; echo 'PHASE3 SLOT $s COMPLETE'"
done
cat <<EOF
▶ PHASE 3 launched ($GPUS slots), detached.
  langs  : $LANGS
  fakes  : $N/language via facebook/mms-tts-*  -> data_fakes/<lang>/
  status : tmux ls | grep vox3 ; tail -f logs/phase3_*.log
  note   : some MMS-TTS codes (sat/snd/kas…) may be missing -> that language logs 'gen failed' and is skipped.
EOF
