#!/usr/bin/env bash
# Launch a VoxShield round DETACHED so it runs for hours after your laptop disconnects.
# Servers don't sleep; tmux keeps the process alive across SSH drops.
#
# Usage:  bash launch_round.sh "hindi,marathi"
#         bash launch_round.sh "tamil" --epochs 4
#         bash launch_round.sh "all"            # runs the 23-language sweep sequentially
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }
LANGS=${1:?"usage: launch_round.sh <langs|all> [run_round args...]"}
shift || true
SESSION=vox_"$(echo "$LANGS" | tr ',' '_' | cut -c1-20)"
mkdir -p logs

if command -v tmux >/dev/null 2>&1; then
  tmux has-session -t "$SESSION" 2>/dev/null && { echo "session $SESSION already running"; tmux attach -t "$SESSION"; exit 0; }
  if [ "$LANGS" = "all" ]; then
    # sequential sweep over all 23 languages
    SWEEP="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi assamese urdu sanskrit nepali maithili bodo dogri kashmiri manipuri konkani santali sindhi english"
    CMD="for L in $SWEEP; do echo \"##### LANGUAGE \$L #####\"; bash run_round.sh \"\$L\" $*; done"
  else
    CMD="bash run_round.sh \"$LANGS\" $*"
  fi
  tmux new-session -d -s "$SESSION" "$CMD"
  echo "▶ launched in tmux session '$SESSION' (running detached)"
  echo "  attach : tmux attach -t $SESSION"
  echo "  detach : Ctrl-b then d"
  echo "  log    : tail -f $ROOT/logs/round_*.log"
  echo "  status : bash watch.sh"
else
  # fallback: nohup + disown (still survives disconnect)
  nohup bash run_round.sh "$LANGS" "$@" >> "logs/nohup_$(date +%Y%m%d_%H%M).log" 2>&1 &
  disown
  echo "▶ launched with nohup (pid $!). tail -f $ROOT/logs/nohup_*.log"
fi
