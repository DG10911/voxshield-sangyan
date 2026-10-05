#!/usr/bin/env bash
# VoxShield — PHASE 5 (real TTS): give the single-class languages a genuine spoof set
# with MMS-TTS (facebook/mms-tts-<code>), pull ONE IndicVoices shard for real audio,
# then retrain a two-class round.
#   bash launch_lowres_tts.sh                 # 8 languages across free GPUs, detached
#   bash launch_lowres_tts.sh --only nepali 1 # smoke-test one (foreground, GPU 1)
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_lowres_tts.sh
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN
HF=$(command -v hf || command -v huggingface-cli || echo "")

LANGS="bodo dogri kashmiri konkani manipuri nepali santali sindhi"
N=${N:-300}

worker(){ local L=$1 DEV=${2:-0}
  { echo "==== lowres-tts $L (GPU $DEV) ===="
    # 1) real audio (ONE shard; full set is ~30 GB/lang, we only need a slice)
    local REAL="data/${L}/indicvoices_real/${L}"
    if ! ls "$REAL"/*.parquet >/dev/null 2>&1; then
      echo "  [data] downloading 1 IndicVoices shard for $L"
      mkdir -p "$REAL"
      "$HF" download ai4bharat/IndicVoices --repo-type dataset \
        --include "${L}/train-00000-of-*" --local-dir "data/${L}/indicvoices_real" \
        >/dev/null 2>&1 || { echo "!! data download failed $L"; exit 1; }
    else
      echo "  [data] real audio present ($(ls "$REAL"/*.parquet | wc -l) shard)"
    fi
    # 2) synthetic fakes (real MMS-TTS voices)
    if [ ! -f "data_fakes/${L}/.done_gen" ]; then
      python backend/gen_fakes_mms.py --lang "$L" --n "$N" --out "data_fakes/${L}" \
        && touch "data_fakes/${L}/.done_gen" || { echo "!! TTS gen failed $L"; exit 1; }
    fi
    # 3) train the two-class round
    rm -f "checkpoints/${L}.done"
    FAKES_MANIFEST="$ROOT/data_fakes/${L}/manifest.jsonl" \
      CUDA_VISIBLE_DEVICES=$DEV bash run_round.sh "$L" --gpu "$DEV" --shards-end 0
    echo "==== lowres-tts $L done ===="
  } 2>&1 | tee -a "logs/lowres_tts_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

IFS=, read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  dev=${VIS[$s]}
  tmux new-session -d -s "vox5t_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_lowres_tts.sh' --only \$L $dev; done; echo 'LOWRES-TTS SLOT $s COMPLETE'"
  echo "  slot $s -> GPU $dev :$list"
done
echo "LOW-RES real-TTS launched ($GPUS slots). logs: tail -f logs/lowres_tts_*.log"
