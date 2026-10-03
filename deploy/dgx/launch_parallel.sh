#!/usr/bin/env bash
# VoxShield — PARALLEL 23-language build across the DGX's 8× A100.
# Each GPU slot processes a share of the languages sequentially; all detached in tmux.
# Wall-clock ≈ ceil(23/GPUS) languages per slot  (8 GPUs -> 3 languages each -> ~1 day).
#
# Usage:  bash launch_parallel.sh                  # 8 GPUs, all 23 languages, bounded data
#         bash launch_parallel.sh --gpus 4         # use 4 slots
#         bash launch_parallel.sh --gpu-ids 0,1,2,3   # use ONLY these physical GPUs (shared box!)
#         bash launch_parallel.sh --shards-end 15  # more data per language
#         bash launch_parallel.sh --smoke          # 1 language, tiny data, ~20 min validation
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }

GPUS=${GPUS:-8}; SHARDS_END=${SHARDS_END:-9}; SMOKE=0; GPU_IDS=${GPU_IDS:-}
LANGSTR="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi assamese urdu sanskrit nepali maithili bodo dogri kashmiri manipuri konkani santali sindhi english"
while [ $# -gt 0 ]; do
  case "$1" in
    --gpus) GPUS=$2; shift;;
    --gpu-ids) GPU_IDS=$2; shift;;
    --shards-end) SHARDS_END=$2; shift;;
    --smoke) SMOKE=1; GPUS=1; SHARDS_END=0;;
  esac; shift
done

# physical GPU per slot: explicit --gpu-ids wins; else 0..GPUS-1
GIDS=()
if [ -n "$GPU_IDS" ]; then
  IFS=',' read -ra GIDS <<< "$GPU_IDS"; GPUS=${#GIDS[@]}
fi
gpuid(){ local s=$1; if [ "${#GIDS[@]}" -gt 0 ]; then echo "${GIDS[$((s % ${#GIDS[@]}))]}"; else echo "$s"; fi; }

mkdir -p logs
run(){ # $1 = slot index, $2 = space-separated languages
  local slot=$1; shift
  local gpu; gpu=$(gpuid "$slot")
  # pin each slot to its own physical GPU (run_round.sh sets CUDA_VISIBLE_DEVICES=$gpu)
  tmux new-session -d -s "vox_slot$slot" \
    "cd $ROOT; for L in $*; do echo \"########## \$L (gpu $gpu) ##########\"; bash run_round.sh \"\$L\" --gpu $gpu --shards-end $SHARDS_END; done; echo 'SLOT $slot COMPLETE'"
}

# ---- distribute languages round-robin across GPU slots ----
read -ra A <<< "$LANGSTR"
if [ "$SMOKE" = "1" ]; then
  run 0 "hindi"
  echo "▶ SMOKE launched in tmux 'vox_slot0' (1 language, tiny data)"
else
  for ((s=0; s<GPUS; s++)); do
    list=""
    for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
    run "$s" "$list"
  done
  echo "▶ PARALLEL launched: $GPUS slots (tmux vox_slot0..$((GPUS-1))) on GPUs: $(for ((s=0;s<GPUS;s++)); do printf '%s ' "$(gpuid $s)"; done)"
  echo "  each slot runs its languages sequentially on its own A100."
fi

cat <<EOF

  sessions : $(tmux ls 2>/dev/null | wc -l | tr -d ' ')   (tmux ls)
  watch    : bash watch.sh
  resume   : bash resume.sh --go
  detach   : Ctrl-b d    reattach: tmux attach -t vox_slot0
  logs     : tail -f $ROOT/logs/round_*.log
  ETA      : ~ceil(23/$GPUS) languages/slot × ~6 h ≈ ~$(python -c "import math;print(math.ceil(23/max(1,$GPUS))*6)") h
EOF
