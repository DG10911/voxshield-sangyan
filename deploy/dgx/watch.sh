#!/usr/bin/env bash
# Watch VoxShield DGX runs — status, tail, GPU, disk. Safe to run anytime.
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
echo "=== tmux sessions ==="; tmux ls 2>/dev/null || echo "(no tmux / no sessions)"
echo; echo "=== running python (train/gen) ==="; pgrep -af "train_corpus|run_round|gen_worst_ai" | head
echo; echo "=== latest round log ==="; LOG=$(ls -t "$ROOT"/logs/round_*.log 2>/dev/null | head -1)
[ -n "$LOG" ] && { echo "$LOG"; tail -n 15 "$LOG"; } || echo "(none yet)"
echo; echo "=== checkpoints ==="; ls -lh "$ROOT/checkpoints" 2>/dev/null
echo; echo "=== GPU ==="; nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv 2>/dev/null || echo "(nvidia-smi n/a)"
echo; echo "=== disk ==="; df -h "$ROOT" | tail -1
echo; echo "attach a running round:  tmux attach -t $(tmux ls 2>/dev/null | head -1 | cut -d: -f1)"
echo "live one-screen dashboard: bash dashboard.sh   (add --once for a single frame)"
