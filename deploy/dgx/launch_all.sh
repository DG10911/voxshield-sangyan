#!/usr/bin/env bash
# VoxShield — MASTER launcher: run ALL remaining work on the DGX, detached.
#   Phase 0  downloads  (models + datasets)
#   Phase 2  generalization gap for the 12 two-class languages + aggregate report
#   Phase 3  spoof (MMS-TTS) + retrain for the 10 genuine-only languages
# Everything runs in tmux; you can close the laptop and leave.
#
# Usage:  HOLDOUT=xtts bash launch_all.sh
#         FULL=1 HOLDOUT=xtts bash launch_all.sh      # full multi-TB dataset pull
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}
[ -f "$ENVF" ] && . "$ENVF"
HOLDOUT=${HOLDOUT:-xtts}

echo "▶ [0] downloads (detached tmux vox_all_dl)"
tmux new-session -d -s vox_all_dl "cd $ROOT; export FULL=${FULL:-0}; bash '$ROOT/launch_downloads.sh'"

echo "▶ [2] generalization-gap sweep (holdout=$HOLDOUT)"
HOLDOUT="$HOLDOUT" bash "$ROOT/launch_phase2.sh"

echo "▶ [3] spoof-gen + retrain for genuine-only languages"
bash "$ROOT/launch_phase3.sh"

cat <<EOF

════════════════════════════════════════════════════════════════════
 ALL PHASES LAUNCHED — nothing depends on your laptop now.
   tmux ls | grep vox          sessions running
   tail -f logs/phase2_*.log   gap sweep
   tail -f logs/phase3_*.log   spoof + retrain
   tail -f logs/dl_*.log       downloads
   cat phase2/report_all.txt    paper tables (when done)
 Resume anytime by re-running the same command (finished work is skipped).
════════════════════════════════════════════════════════════════════
EOF
