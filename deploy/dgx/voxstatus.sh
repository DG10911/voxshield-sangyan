#!/usr/bin/env bash
# VoxShield — one-shot status for everything on the DGX.
#   bash ~/voxshield/voxstatus.sh
cd ~/voxshield 2>/dev/null || exit 1

echo "================ VOXSHIELD STATUS $(date '+%Y-%m-%d %H:%M') ================"

echo; echo "---- tmux sessions (ours) ----"
tmux ls 2>/dev/null | grep -E "vox" || echo "none"

echo; echo "---- GPUs ----"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader

echo; echo "---- running workers (python) ----"
ps -eo etime,cmd 2>/dev/null | grep -E "run_round|train_backend|gen_fakes|adversarial|distill|orth_probe|ensemble_eval|download_resources|launch_" | grep -v grep | head -12 || echo "none"

echo; echo "---- per-language: trained? fakes? ----"
printf "%-11s %7s %8s %8s\n" LANG round fakes multi
for L in hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi urdu sanskrit \
         assamese maithili bodo dogri kashmiri konkani manipuri nepali santali sindhi english; do
  r=$([ -f "checkpoints/${L}.done" ] && echo OK || echo -)
  f=$(ls data_fakes/$L/*.wav 2>/dev/null | wc -l | tr -d ' ')
  m=$(ls data_fakes_multi/$L/*/*.wav 2>/dev/null | wc -l | tr -d ' ')
  printf "%-11s %7s %8s %8s\n" "$L" "$r" "$f" "$m"
done

echo; echo "---- checkpoints present ----"
ls -d checkpoints/*/ 2>/dev/null | wc -l | xargs echo "checkpoint dirs:"
ls checkpoints/*.done 2>/dev/null | wc -l | xargs echo "completed rounds:"

echo; echo "---- downloads ----"
echo -n "open(HF/OpenSLR/...): "; tail -1 logs/download_resources.log 2>/dev/null; grep -c "Fetching\|Downloading\|100%" logs/download_resources.log 2>/dev/null | xargs echo "  (~lines):"
echo -n "aikosh: "; tail -1 logs/aikosh_download.log 2>/dev/null
echo -n "kaggle: "; tail -1 logs/kaggle_download.log 2>/dev/null
echo -n "dataset size: "; du -sh data/indic 2>/dev/null | cut -f1

echo; echo "---- training logs (last line each) ----"
for f in logs/lowres_parler_*.log logs/multigen_*.log logs/improve_*.log logs/orth_*.log logs/ensemble.log; do
  [ -f "$f" ] && printf "%-34s %s\n" "$(basename $f)" "$(tail -1 "$f" 2>/dev/null | cut -c1-90)"
done 2>/dev/null | tail -15

echo; echo "---- latest results ----"
[ -f results/ensemble_report.txt ] && tail -20 results/ensemble_report.txt || echo "ensemble report pending"
[ -f results/report_all_norm.txt ] && echo "(report_all_norm.txt present)" || echo "(report_all_norm.txt pending)"

echo; echo "---- API keys present ----"
grep -oE "^export [A-Z_]+=" ~/.config/voxshield.env 2>/dev/null | sed 's/export //;s/=//' | tr '\n' ' '; echo

echo; echo "---- disk ----"
df -h ~ | tail -1

echo; echo "=========================================================="
