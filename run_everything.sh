#!/usr/bin/env bash
# =============================================================================
#  VoxShield — ONE COMMAND, ZERO MANUAL WORK
#
#  bash run_everything.sh            -> retrain on ALL your data (bigger) + launch
#  bash run_everything.sh --serve    -> just launch the current model (for the demo)
#  bash run_everything.sh --get-data -> ALSO auto-download more datasets, then train + launch
#
#  No folders to make, no clips to paste. It handles everything.
# =============================================================================
set -e
cd "$(dirname "$0")/backend"
export SSD="${SSD:-/Volumes/KIOXIA}"
export HF_HOME="$SSD/hf_cache"
MODE="${1:-train}"

echo "[VoxShield] environment…"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || true

# ---- serve-only mode: skip training, just run the dashboard (use for the jury) ----
if [ "$MODE" = "--serve" ]; then
  echo "[VoxShield] launching dashboard (fast mode, 4 workers) on http://localhost:8000"
  export VOXSHIELD_DISABLE_ML=1
  exec uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
fi

# ---- optional: auto-download more datasets (no manual steps) ----
if [ "$MODE" = "--get-data" ]; then
  echo "[VoxShield] auto-downloading extra datasets…"
  pip install -q datasets pyarrow huggingface_hub 2>/dev/null || true
  python get_hf_datasets.py     || true
  python get_parquet_datasets.py || true
fi

# ---- build + train on EVERYTHING (bigger, with telephony+noise augmentation) ----
echo "[VoxShield] building dataset list…"
python make_manifests.py "$SSD/voxdata" --out manifests
export VOXSHIELD_CAP="${VOXSHIELD_CAP:-3000}"
python make_combined.py
echo "[VoxShield] backing up current model → artifacts_backup"
rm -rf artifacts_backup 2>/dev/null || true
cp -r artifacts artifacts_backup 2>/dev/null || true
echo "[VoxShield] training fusion model (this takes a while — let it run)…"
python train_fusion.py --train manifests/combined.csv --augment

# ---- launch ----
echo "[VoxShield] ✅ trained. Launching dashboard (fast mode, 4 workers) on http://localhost:8000"
export VOXSHIELD_DISABLE_ML=1
exec uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
