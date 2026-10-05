#!/usr/bin/env bash
# VoxShield — PHASE 5 (Indic-Parler real TTS): two-class rounds for the low-res languages that
# Indic-Parler-TTS actually supports: kashmiri (ks), nepali (ne), sindhi (sd).
# (dogri/konkani/manipuri/santali have no available TTS; bodo only via community piper models.)
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_lowres_parler.sh
#   bash launch_lowres_parler.sh --only kashmiri 1
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN
HF=$(command -v hf || command -v huggingface-cli || echo "")

LANGS="kashmiri nepali sindhi"
N=${N:-300}

worker(){ local L=$1 DEV=${2:-0}
  { echo "==== lowres-parler $L (GPU $DEV) ===="
    local REAL="data/${L}/indicvoices_real/${L}"
    if ! ls "$REAL"/*.parquet >/dev/null 2>&1; then
      echo "  [data] downloading 1 IndicVoices shard for $L"
      mkdir -p "$REAL"
      "$HF" download ai4bharat/IndicVoices --repo-type dataset \
        --include "${L}/train-00000-of-*" --local-dir "data/${L}/indicvoices_real" \
        >/dev/null 2>&1 || { echo "!! data download failed $L"; exit 1; }
    else
      echo "  [data] real audio present"
    fi
    if [ ! -f "data_fakes/${L}/.parler_done" ]; then
      rm -f "data_fakes/${L}/.done_gen" "data_fakes/${L}/manifest.jsonl"
      CUDA_VISIBLE_DEVICES=$DEV python backend/gen_fakes_tts.py --lang "$L" \
        --data-root "data/${L}" --n "$N" --out "data_fakes/${L}" \
        && touch "data_fakes/${L}/.parler_done" || { echo "!! parler gen failed $L"; exit 1; }
    fi
    rm -f "checkpoints/${L}.done"
    FAKES_MANIFEST="$ROOT/data_fakes/${L}/manifest.jsonl" \
      CUDA_VISIBLE_DEVICES=$DEV bash run_round.sh "$L" --gpu "$DEV" --shards-end 0
    echo "==== lowres-parler $L done ===="
  } 2>&1 | tee -a "logs/lowres_parler_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

IFS=, read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  [ -z "$list" ] && continue
  dev=${VIS[$s]}
  tmux new-session -d -s "vox5p_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_lowres_parler.sh' --only \$L $dev; done; echo 'LOWRES-PARLER SLOT $s COMPLETE'"
  echo "  slot $s -> GPU $dev :$list"
done
echo "LOW-RES Indic-Parler launched. logs: tail -f logs/lowres_parler_*.log"
