#!/usr/bin/env bash
# VoxShield — PHASE 4: the remaining GPU work, parallel + detached.
#   * AASIST-style back-end training            (train_backend.py --arch aasist)
#   * Conformer back-end + ADVERSARIAL (PGD)     (adversarial_train.py)
#   * Distillation  XLS-R teacher -> LCNN student (distill.py)
#   * C2 ablation (channel-profiled gate vs global) on each round's scores.csv
# Uses the eval data pulled by Phase 2 (data/<lang>_eval) so no re-download.
# Resume-safe. Launch and leave.
#
# Usage: HOLDOUT=xtts bash launch_phase4.sh
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
GPUS=${GPUS:-8}; HOLDOUT=${HOLDOUT:-xtts}
LANGS="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi urdu sanskrit"
mkdir -p logs phase4
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

worker(){ # $1 lang
  local L=$1 D="data/${L}_eval"
  exec > >(tee -a "logs/phase4_${L}.log") 2>&1
  echo "==== phase4 $L ===="
  [ -d "$D" ] || { echo "!! no $D (Phase 2 did not pull $L) — skip"; return 1; }
  local CK; CK=$(ls -d checkpoints/round_*_"${L}"*/last.pt 2>/dev/null | head -1)

  # AASIST-style back-end (clean)
  [ -f "checkpoints/aasist_${L}/scores.csv" ] || \
    python backend/train_backend.py --arch aasist --data-root "$D" --langs "$L" \
      --holdout "$HOLDOUT" --epochs 3 --out "checkpoints/aasist_${L}"

  # Conformer + ADVERSARIAL (PGD)
  [ -f "checkpoints/adv_${L}/scores.csv" ] || \
    python backend/adversarial_train.py --arch conformer --attack pgd --eps 0.005 --steps 5 \
      --data-root "$D" --langs "$L" --holdout "$HOLDOUT" --epochs 3 --out "checkpoints/adv_${L}"

  # Distillation (needs the XLS-R teacher ckpt)
  if [ -n "$CK" ] && [ ! -f "checkpoints/student_${L}/scores.csv" ]; then
    python backend/distill.py --teacher "$CK" --arch lcnn --data-root "$D" --langs "$L" \
      --holdout "$HOLDOUT" --epochs 3 --out "checkpoints/student_${L}"
  fi

  # C2 ablation on the round's own scores.csv (clean vs g711)
  local SC; SC=$(ls -d checkpoints/round_*_"${L}"*/scores.csv 2>/dev/null | head -1)
  [ -n "$SC" ] && python backend/eval_c2_ablation.py --csv "$SC" --tpr 0.95 > "phase4/c2_${L}.txt"
  echo "==== phase4 $L done ===="
}

case "${1:-}" in --only) worker "${2:?lang}"; exit $?;; esac

read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  tmux new-session -d -s "vox4_slot$s" \
    "cd $ROOT; export HOLDOUT=$HOLDOUT; for L in $list; do CUDA_VISIBLE_DEVICES=$s bash '$ROOT/launch_phase4.sh' --only \$L; done; echo 'PHASE4 SLOT $s COMPLETE'"
done
cat <<EOF
▶ PHASE 4 launched ($GPUS slots), detached.
  outputs : checkpoints/{aasist_,adv_,student_}<lang>/scores.csv ; phase4/c2_<lang>.txt
  status  : tmux ls | grep vox4 ; tail -f logs/phase4_*.log
  novelty : after this, build a wav manifest and run:
            python backend/dump_fusion_scores.py --manifest eval.jsonl --out fusion_scores.csv
            python backend/validate_novelty.py --csv fusion_scores.csv
EOF
