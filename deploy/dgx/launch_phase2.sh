#!/usr/bin/env bash
# VoxShield — PHASE 2: post-training tasks, detached + parallel across the GPUs.
# Recovers the GENERALIZATION GAP for every two-class language and aggregates the
# paper report. Safe to launch and leave; resume-safe (finished languages skipped).
#
# Per language:
#   1. pull IndicSynth HIGHER shards (>=10 → generators not in training 0..9) + genuine
#   2. list the generators actually present (so we pick a TRUE unseen one)
#   3. score the saved checkpoint with the held-out generator -> phase2/<lang>_scores.csv
#   4. render the paper report                                -> phase2/<lang>_report.txt
# Last job: concatenate everything -> phase2/scores_phase2_all.csv + phase2/report_all.txt
#
# Usage (on the DGX):
#   HOLDOUT=vits bash launch_phase2.sh            # after choosing the holdout generator
#   HOLDOUT=vits GPUS=4 bash launch_phase2.sh     # 4 GPUs
#   HOLDOUT=vits bash launch_phase2.sh --only hindi   # one language, foreground (smoke)
#   bash launch_phase2.sh --agg                   # just the aggregate job
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}
[ -f "$ENVF" ] && . "$ENVF"

GPUS=${GPUS:-8}; HOLDOUT=${HOLDOUT:-vits}; SHARD_HI=${SHARD_HI:-"1* 2*"}
LANGS="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi urdu sanskrit"
mkdir -p logs phase2
HF=$(command -v hf || command -v huggingface-cli)

worker(){ # $1 = lang  (runs in this process)
  local L=$1
  local ll; ll=$(echo "$L" | tr 'A-Z' 'a-z')
  local Cap; Cap=$(echo "$ll" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')
  local ev="data/${L}_eval"
  exec > >(tee -a "logs/phase2_${L}.log") 2>&1
  echo "==== phase2 $L (holdout=$HOLDOUT) ===="
  [ -f "phase2/${L}_scores.csv" ] && { echo "[resume] $L already done — skip"; return 0; }

  local inc=()
  for b in $SHARD_HI; do inc+=(--include "$Cap/train-000${b}-of-*"); done
  "$HF" download vdivyasharma/IndicSynth --repo-type dataset "${inc[@]}" \
      --local-dir "$ev/indicsynth" 2>&1 | tail -2
  "$HF" download ai4bharat/IndicVoices --repo-type dataset --include "$ll/train-0000*-of-*" \
      --local-dir "$ev/indicvoices_real" 2>&1 | tail -2

  echo "--- generators present ---"
  python backend/eval_unseen.py --list-generators --data-root "$ev" --lang "$L" || true

  local CKPT; CKPT=$(ls -d checkpoints/round_*_"${L}"*/last.pt 2>/dev/null | head -1)
  [ -z "$CKPT" ] && CKPT=$(ls -d checkpoints/round_*"${ll}"*/last.pt 2>/dev/null | head -1)
  if [ -z "$CKPT" ]; then
    echo "!! no checkpoint for $L — check:  ls -d checkpoints/round_*${ll}*"; return 1
  fi
  echo "ckpt: $CKPT"
  python backend/eval_unseen.py --ckpt "$CKPT" --data-root "$ev" --lang "$L" \
      --holdout "$HOLDOUT" --out "phase2/${L}_scores.csv"
  [ -f "phase2/${L}_scores.csv" ] && python backend/paper_report.py \
      --csv "phase2/${L}_scores.csv" --out "phase2/${L}_report.txt"
  echo "==== phase2 $L done ===="
}

aggregate(){
  exec > >(tee -a logs/phase2_aggregate.log) 2>&1
  local want; want=$(echo $LANGS | wc -w | tr -d ' ')
  echo "waiting for $want languages…"
  for i in $(seq 1 720); do
    n=$(ls phase2/*_scores.csv 2>/dev/null | wc -l | tr -d ' ')
    [ "${n:-0}" -ge "$want" ] && break
    sleep 30
  done
  python - <<'PY'
import glob, csv
rows = []
for f in ["scores_all.csv"] + sorted(glob.glob("phase2/*_scores.csv")):
    try:
        for r in csv.DictReader(open(f)): rows.append(r)
    except FileNotFoundError: pass
w = csv.DictWriter(open("phase2/scores_phase2_all.csv", "w", newline=""),
                   fieldnames=["label","score","generator","language","channel","seen"])
w.writeheader(); w.writerows(rows); print(len(rows), "rows aggregated")
PY
  python backend/paper_report.py --csv phase2/scores_phase2_all.csv --out phase2/report_all.txt
  echo "==== PHASE 2 COMPLETE -> phase2/report_all.txt ===="
}

case "${1:-}" in
  --only) worker "${2:?lang}"; exit $?;;
  --agg)  aggregate; exit $?;;
esac

read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  tmux new-session -d -s "vox2_slot$s" \
    "cd $ROOT; export HOLDOUT=$HOLDOUT; for L in $list; do CUDA_VISIBLE_DEVICES=$s bash '$ROOT/launch_phase2.sh' --only \$L; done; echo 'SLOT $s COMPLETE'"
done
tmux new-session -d -s vox2_agg "cd $ROOT; bash '$ROOT/launch_phase2.sh' --agg"

cat <<EOF
▶ PHASE 2 launched ($GPUS slots + aggregator), detached.
  holdout : $HOLDOUT
  status  : tmux ls | grep vox2      ;   bash watch.sh
  logs    : tail -f $ROOT/logs/phase2_*.log
  resume  : re-run the same command (finished languages are skipped)
  done    : phase2/report_all.txt
EOF
