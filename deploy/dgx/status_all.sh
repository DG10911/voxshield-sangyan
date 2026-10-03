#!/usr/bin/env bash
# VoxShield — DGX status at a glance. Read-only; run anytime.
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" 2>/dev/null || exit 1
c(){ printf "\n\033[1;36m== %s ==\033[0m\n" "$1"; }

c "tmux sessions (vox*)"
tmux ls 2>/dev/null | grep -E '^vox' || echo "  (none running)"

c "orchestrator (vox_all)"
tmux capture-pane -pt vox_all -S -6 2>/dev/null | grep -v '^$' | tail -6 || echo "  (no vox_all)"
echo "  log tail:"; tail -n 4 logs/orchestrator.log 2>/dev/null | sed 's/^/    /'

c "phase progress"
printf "  phase2 seen scores : %s / 12\n" "$(ls phase2/*_scores.csv 2>/dev/null | wc -l | tr -d ' ')"
printf "  gap reports        : %s\n" "$(ls phase2/*_gap.txt 2>/dev/null | wc -l | tr -d ' ')"
printf "  phase4 outputs     : %s\n" "$(ls -d checkpoints/aasist_* checkpoints/adv_* checkpoints/student_* 2>/dev/null | wc -l | tr -d ' ')"
printf "  checkpoints done   : %s\n" "$(ls checkpoints/*.done 2>/dev/null | wc -l | tr -d ' ')"
printf "  round dirs w/ ckpt : %s\n" "$(ls checkpoints/round_*/last.pt 2>/dev/null | wc -l | tr -d ' ')"
printf "  downloads finished : %s\n" "$(ls data_pull/.done_* 2>/dev/null | wc -l | tr -d ' ')"

c "active work"
pgrep -af "train_corpus|train_backend|adversarial_train|distill|eval_unseen|score_matrix|gen_fakes_mms|parquet_to_wav|hf download" 2>/dev/null | sed 's/^/  /' | head -20 || echo "  (idle)"

c "GPU"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null | sed 's/^/  /' || echo "  (nvidia-smi n/a)"

c "recent per-language logs (last line)"
for f in logs/phase2_*.log logs/gap_*.log logs/phase3_*.log; do
  [ -f "$f" ] || continue
  printf "  %-32s %s\n" "$(basename "$f")" "$(tail -n 1 "$f" | cut -c1-80)"
done 2>/dev/null | head -30

c "errors in logs (last 10)"
grep -rhiE "error|traceback|not a local folder|403|500" logs/*.log 2>/dev/null | tail -10 | cut -c1-120 | sed 's/^/  /' || echo "  (none)"

c "disk"
df -h "$ROOT" 2>/dev/null | tail -1 | sed 's/^/  /'
echo
