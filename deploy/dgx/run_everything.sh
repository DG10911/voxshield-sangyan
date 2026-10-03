#!/usr/bin/env bash
# VoxShield — ONE command to run the ENTIRE remaining pipeline in dependency order.
# Launches each phase detached in its own tmux session, waiting between dependent
# stages. Safe to launch in a tmux session and leave.
#
#   tmux new -d -s vox_all "bash ~/voxshield/run_everything.sh"
#   # or foreground:  bash ~/voxshield/run_everything.sh
#
# Order: downloads -> redo failed two-class -> phase3(spoof) -> phase2(data+seen)
#        -> GAP(external unseen) -> phase4(AASIST/adversarial/distill/C2)
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
FULL=${FULL:-0}
mkdir -p logs phase2
LOG=logs/orchestrator.log
exec > >(tee -a "$LOG") 2>&1

say(){ echo "[$(date '+%H:%M:%S')] $*"; }
wait_for(){ # $1 glob, $2 need count, $3 timeout secs
  local pat=$1 need=$2 secs=${3:-10800}
  for i in $(seq 1 $((secs/30))); do
    local n; n=$(ls -d $pat 2>/dev/null | wc -l | tr -d ' ')
    [ "${n:-0}" -ge "$need" ] && { say "ready: $pat ($n>=$need)"; return 0; }
    sleep 30
  done
  say "!! timeout waiting for $pat ($need)"; return 1
}

say "=== VOXSHIELD RUN-EVERYTHING START (FULL=$FULL) ==="

say "[0] downloads"
tmux new-session -d -s vox_dl "cd $ROOT; export FULL=$FULL; bash '$ROOT/launch_downloads.sh'"

say "[A] redo failed two-class languages (BLOCKING — phase2 needs their checkpoints)"
for L in hindi gujarati malayalam odia; do
  rm -f "checkpoints/$L.done"
  CUDA_VISIBLE_DEVICES=0 bash "$ROOT/run_round.sh" "$L" --shards-end 9 || say "redo $L failed"
done
say "[A] redo complete"

say "[3] spoof + retrain genuine-only languages"
bash "$ROOT/launch_phase3.sh"

say "[2] pull eval data + SEEN numbers"
bash "$ROOT/launch_phase2.sh"

say "waiting for Phase 2 to produce scored results (8+ languages) ..."
wait_for "phase2/*_scores.csv" 8 21600

say "[GAP] external unseen-generator generalization gap"
bash "$ROOT/launch_gap.sh"

say "waiting a little for gap files ..."
wait_for "phase2/*_gap.txt" 4 21600

say "[4] AASIST / adversarial / distillation / C2"
bash "$ROOT/launch_phase4.sh"

say "=== ALL PHASES LAUNCHED. Monitor: tmux ls | grep vox ; tail -f logs/*.log ==="
say "=== outputs: phase2/report_all.txt, phase2/*_gap.txt, phase4/c2_*.txt ==="
