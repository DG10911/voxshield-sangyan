#!/usr/bin/env bash
# VoxShield — GAP (external unseen generator). IndicSynth has only `freevc24`, so the
# generalization gap must come from a DIFFERENT generator. This builds it per language:
#   seen fakes  = IndicSynth freevc24  (extracted to wav)
#   real        = IndicVoices          (extracted to wav)
#   UNSEEN fakes= MMS-TTS              (gen_fakes_mms --seen 0)
# then scores the round checkpoint -> paper_report -> phase2/<lang>_gap.txt
#
# Detached, GPU-pinned, parallel, resume-safe. Run after Phase 2 has pulled data/<lang>_eval.
# Usage: bash launch_gap.sh
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}; [ -f "$ENVF" ] && . "$ENVF"
GPUS=${GPUS:-6}; NN=${NN:-800}
LANGS="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi urdu sanskrit"
mkdir -p logs phase2 data_gap
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

worker(){ # $1 lang
  local L=$1; local ll; ll=$(echo "$L"|tr 'A-Z' 'a-z')
  local Cap; Cap=$(echo "$ll"|awk '{print toupper(substr($0,1,1)) substr($0,2)}')
  local D="data/${L}_eval" G="data_gap/${L}"
  exec > >(tee -a "logs/gap_${L}.log") 2>&1
  echo "==== gap $L ===="
  [ -f "phase2/${L}_gap.txt" ] && { echo "[resume] $L done"; return 0; }
  [ -d "$D/indicsynth/$Cap" ] || { echo "!! no eval data in $D — run launch_phase2.sh first"; return 1; }
  mkdir -p "$G"

  # seen fakes + real  -> manifest
  python backend/parquet_to_wav.py --glob "$D/indicsynth/$Cap/*.parquet" --label 1 \
      --generator freevc24 --language "$L" --seen 1 --limit 1200 \
      --out-dir "$G/seen" --manifest "$G/m.jsonl"
  python backend/parquet_to_wav.py --glob "$D/indicvoices_real/$ll/*.parquet" --audio-col audio_filepath \
      --label 0 --generator real --language "$L" --seen 1 --limit 1200 \
      --out-dir "$G/real" --manifest "$G/m.jsonl" --append

  # UNSEEN fakes (MMS-TTS) -> append (seen=0)
  python backend/gen_fakes_mms.py --lang "$L" --n "$NN" --seen 0 --out "$G/mms"
  [ -f "$G/mms/manifest.jsonl" ] && cat "$G/mms/manifest.jsonl" >> "$G/m.jsonl"

  local CK; CK=$(ls -d checkpoints/round_*_"${L}"*/last.pt 2>/dev/null | head -1)
  [ -z "$CK" ] && { echo "!! no checkpoint for $L"; return 1; }
  echo "ckpt: $CK"
  python backend/score_matrix.py --manifest "$G/m.jsonl" --ckpt "$CK" \
      --channels clean,g711_ulaw --out "$G/scores.csv"
  python backend/paper_report.py --csv "$G/scores.csv" --out "phase2/${L}_gap.txt"
  echo "==== gap $L done -> phase2/${L}_gap.txt ===="
}

case "${1:-}" in --only) worker "${2:?lang}"; exit $?;; esac

read -ra A <<< "$LANGS"
for ((s=0; s<GPUS; s++)); do
  list=""; for ((k=s; k<${#A[@]}; k+=GPUS)); do list="$list ${A[k]}"; done
  tmux new-session -d -s "voxg_slot$s" \
    "cd $ROOT; for L in $list; do CUDA_VISIBLE_DEVICES=$s bash '$ROOT/launch_gap.sh' --only \$L; done; echo 'GAP SLOT $s COMPLETE'"
done
echo "▶ GAP sweep launched ($GPUS slots). results: phase2/<lang>_gap.txt ; logs: logs/gap_*.log"
