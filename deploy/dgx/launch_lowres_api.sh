#!/usr/bin/env bash
# VoxShield — low-res languages via API TTS (Sarvam/Cartesia), fixing the SSL + Parler issues.
# For each language: ensure 1 IndicVoices shard, generate fakes (Sarvam/Cartesia/MMS), retrain.
#   CUDA_VISIBLE_DEVICES=1,2,3 bash launch_lowres_api.sh
#   bash launch_lowres_api.sh --only bodo 1
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
export COQUI_TOS_AGREED=1
export SSL_CERT_FILE=${SSL_CERT_FILE:-$HOME/miniconda3/envs/voxshield/lib/python3.11/site-packages/certifi/cacert.pem}
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
source "$HOME/.config/voxshield.env" 2>/dev/null || true
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN
HF=$(command -v hf || command -v huggingface-cli)

LANGS="${LANGS:-bodo dogri kashmiri konkani manipuri nepali santali sindhi}"
N=${N:-80}
ENGINES=${ENGINES:-bhashini}

worker(){ local L=$1 DEV=${2:-0}
  { echo "==== lowres-api $L (GPU $DEV) ===="
    local REAL="data/${L}/indicvoices_real/${L}"
    if ! ls "$REAL"/*.parquet >/dev/null 2>&1; then
      echo "  [data] 1 IndicVoices shard for $L"
      mkdir -p "$REAL"
      "$HF" download ai4bharat/IndicVoices --repo-type dataset \
        --include "${L}/train-00000-of-*" --local-dir "data/${L}/indicvoices_real" >/dev/null 2>&1 || true
    fi
    rm -f "data_fakes_multi/${L}/manifest.jsonl"
    python backend/gen_fakes_multi.py --lang "$L" --n "$N" --out "data_fakes_multi/${L}" --engines "$ENGINES"
    local rows; rows=$(wc -l < "data_fakes_multi/${L}/manifest.jsonl" 2>/dev/null | tr -d ' ')
    [ "${rows:-0}" = "0" ] && { echo "!! no fakes $L — skip"; exit 0; }
    rm -f "checkpoints/${L}.done"
    FAKES_MANIFEST="$ROOT/data_fakes_multi/${L}/manifest.jsonl" \
      CUDA_VISIBLE_DEVICES=$DEV bash run_round.sh "$L" --gpu "$DEV" --shards-end 0
    echo "==== lowres-api $L done ===="
  } 2>&1 | tee -a "logs/lowres_api_${L}.log"
}

case "${1:-}" in --only) worker "${2:?lang}" "${3:-0}"; exit $?;; esac

IFS=, read -ra VIS <<< "${CUDA_VISIBLE_DEVICES:-0,1,2,3}"; GPUS=${#VIS[@]}
read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  [ -z "${list// }" ] && continue
  dev=${VIS[$s]}
  tmux new-session -d -s "vox15_slot$s" \
    "cd $ROOT; for L in $list; do bash '$ROOT/launch_lowres_api.sh' --only \$L $dev; done; echo 'LOWRES-API SLOT $s COMPLETE'"
  echo "  slot $s -> GPU $dev :$list"
done
echo "LOW-RES API launched."
