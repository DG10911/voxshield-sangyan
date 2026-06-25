#!/usr/bin/env bash
# ============================================================================
#  VoxShield — ONE COMMAND does everything:
#    bash start.sh
#  -> create venv · install deps · build dataset manifests (if you added data)
#     · train the fusion model (or self-test if no data) · launch the console
#
#  Optional:
#    bash start.sh --ml        also install torch+transformers (neural ensemble)
#    bash start.sh --no-train  skip training, just serve
#  Put datasets under  voxshield/data/<name>/{real,fake}/...  before running.
# ============================================================================
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"
cd backend

echo "==> [1/4] Python environment"
if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
if [ "$1" = "--ml" ] || [ "$2" = "--ml" ]; then
  echo "    installing torch + transformers (neural ensemble)…"
  pip install -q torch transformers
fi

echo "==> [2/4] Build dataset manifests from $ROOT/data"
python build_manifests.py --data "$ROOT/data" --out "$ROOT/backend/manifests"

echo "==> [3/4] Train fusion model"
if [ "$1" = "--no-train" ] || [ "$2" = "--no-train" ]; then
  echo "    (skipped)"
else
  shopt -s nullglob
  MANIFESTS=("$ROOT/backend/manifests"/*.csv)
  # hold out any manifest that looks like an in-the-wild / eval / test set
  TRAIN=(); TEST=()
  for m in "${MANIFESTS[@]}"; do
    b="$(basename "$m" | tr '[:upper:]' '[:lower:]')"
    if [[ "$b" == *wild* || "$b" == *itw* || "$b" == *eval* || "$b" == *test* ]]; then
      TEST+=("$m"); else TRAIN+=("$m"); fi
  done
  if [ ${#TRAIN[@]} -gt 0 ]; then
    echo "    training on: ${TRAIN[*]}"
    [ ${#TEST[@]} -gt 0 ] && echo "    holding out: ${TEST[*]}"
    python train_fusion.py --train "${TRAIN[@]}" ${TEST:+--test "${TEST[@]}"} --augment
  else
    echo "    no datasets found -> self-test (proves the pipeline end-to-end)"
    python train_fusion.py --selftest
  fi
fi

echo "==> [4/4] Launch console at http://localhost:8000  (Ctrl+C to stop)"
exec uvicorn app:app --host 0.0.0.0 --port 8000
