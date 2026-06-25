#!/usr/bin/env bash
# =============================================================================
#  VoxShield — ONE COMMAND TO RULE THEM ALL
#
#  Usage:
#     bash run.sh                      # install + self-test train + launch UI
#     bash run.sh /path/to/data        # ALSO: auto-build manifests + train on
#                                      #       the merged super-dataset, then launch
#     bash run.sh /path/to/data --ml   # additionally install torch+transformers
#                                      #       (enables the neural model ensemble)
#
#  Data folder layout (any of these keywords in folder names work):
#     data/<dataset>/real|bonafide|genuine/*.wav
#     data/<dataset>/fake|spoof|synthetic|deepfake/*.wav
#  ASVspoof protocol .txt files are also auto-parsed.
# =============================================================================
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/backend"

DATA_DIR=""
WITH_ML=0
GET_DATA=0
for arg in "$@"; do
  case "$arg" in
    --ml) WITH_ML=1 ;;
    --get-data) GET_DATA=1 ;;
    *) DATA_DIR="$arg" ;;
  esac
done

# --- venv + deps ---
if [ ! -d ".venv" ]; then
  echo "[VoxShield] creating virtualenv…"
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "[VoxShield] installing requirements… (first run only, ~1-2 min)"
pip install -q --upgrade pip
pip install -q -r requirements.txt
if [ "$WITH_ML" = "1" ]; then
  echo "[VoxShield] installing neural stack (torch + transformers)…"
  pip install -q torch transformers
fi

# --- optionally download the real datasets first ---
if [ "$GET_DATA" = "1" ]; then
  echo "[VoxShield] downloading real datasets (In-the-Wild + ASVspoof LA, ~15GB)…"
  python download_data.py --itw --asvspoof --out ../data
  DATA_DIR="../data"
fi

# --- data -> manifests -> train ---
if [ -n "$DATA_DIR" ] && [ -d "$DATA_DIR" ]; then
  echo "[VoxShield] building manifests from: $DATA_DIR"
  python make_manifests.py "$DATA_DIR" --out manifests
  echo "[VoxShield] training fusion head on the super-dataset (RawBoost + 8kHz codec aug)…"
  python train_fusion.py --manifests-dir manifests --augment
else
  echo "[VoxShield] no data folder given — running self-test training so the model is ready."
  python train_fusion.py --selftest
fi

# --- launch ---
echo ""
echo "[VoxShield] ✅ ready. Opening API + dashboard on http://localhost:8000"
echo "[VoxShield]    (Ctrl+C to stop)"
exec uvicorn app:app --host 0.0.0.0 --port 8000
