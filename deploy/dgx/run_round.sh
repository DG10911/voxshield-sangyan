#!/usr/bin/env bash
# VoxShield — ONE autonomous language round on the DGX (GPU-pinned, disk-safe, resume-safe).
# pull -> generate attacks -> train XLS-R+RawBoost -> eval -> checkpoint -> delete data.
# Runs DETACHED (tmux) so it keeps going after your laptop disconnects.
#
# Usage: bash run_round.sh "hindi" [--gpu 0] [--epochs 3] [--shards-end 9] [--keep-data] [--force]
set -uo pipefail

ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }

# --- secrets: tmux sessions inherit a STALE environment (no HF_TOKEN/Bhashini) ---
# Always load the canonical secrets file so gated downloads + API calls work here.
ENVF=${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}
if [ -f "$ENVF" ]; then . "$ENVF"; else echo "!! no $ENVF (gated downloads / Bhashini will fail)"; fi

LANGS=${1:?"usage: run_round.sh <langs-csv> [--gpu N] [--epochs N] [--shards-end N] [--keep-data] [--force]"}
shift || true
EPOCHS=3; KEEP_DATA=0; S1=9; S0=0; FORCE=0; GPU=""; SMOKE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --gpu) GPU=$2; shift;;
    --epochs) EPOCHS=$2; shift;;
    --keep-data) KEEP_DATA=1;;
    --shards-start) S0=$2; shift;;
    --shards-end) S1=$2; shift;;
    --force) FORCE=1;;
    --smoke) SMOKE=1; EPOCHS=1;;
  esac; shift
done
LIMIT=""; [ "$SMOKE" = "1" ] && LIMIT="--limit-per 50"
[ -n "$GPU" ] && export CUDA_VISIBLE_DEVICES=$GPU

TS=$(date +%Y%m%d_%H%M)
LANG_KEY=$(echo "$LANGS" | tr ',' '_')
DATA=$ROOT/data/$LANG_KEY                       # per-language data (no cross-job clashes)
CKPT=$ROOT/checkpoints/round_${TS}_${LANG_KEY}
LOG=$ROOT/logs/round_${TS}_${LANG_KEY}.log
DONE_MARK=$ROOT/checkpoints/${LANG_KEY}.done
mkdir -p "$DATA" "$ROOT"/{logs,checkpoints,models,curated}
exec > >(tee -a "$LOG") 2>&1

echo "==== VoxShield round $TS  langs=$LANGS  gpu=${GPU:-auto}  epochs=$EPOCHS ===="
[ -f "$DONE_MARK" ] && [ "$FORCE" != "1" ] && { echo "[resume] $LANGS already done — skip"; exit 0; }

command -v python >/dev/null || { echo "!! python missing"; exit 1; }
HF=$(command -v hf || command -v huggingface-cli)
[ -n "$HF" ] || { echo "!! hf CLI missing (python -m pip install -U huggingface_hub)"; exit 1; }
export HF_HOME=${HF_HOME:-$ROOT/hf_cache}
export SSL_CERT_FILE=${SSL_CERT_FILE:-$(python -c "import certifi;print(certifi.where())" 2>/dev/null)}
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
export DIARIZATION_BACKEND=${DIARIZATION_BACKEND:-nemo}

# ---- training deps (install once, quietly, if missing) ----
for pkg in datasets soundfile transformers; do
  python -c "import $pkg" 2>/dev/null || { echo "[deps] installing $pkg"; python -m pip install -q "$pkg"; }
done
python -c "import sklearn" 2>/dev/null || { echo "[deps] installing scikit-learn"; python -m pip install -q scikit-learn; }

# ---- disk guard: need MIN_FREE GB free before staging a language ----
# portable: `df -g` is BSD-only (macOS); GNU df on Linux rejects it. Use POSIX -Pk + convert.
MIN_FREE=${MIN_FREE:-120}
FREE=$(df -Pk "$ROOT" 2>/dev/null | awk 'NR==2{print int($4/1024/1024)}')
echo "[guard] free=${FREE}GB  need=${MIN_FREE}GB"
[ "${FREE:-0}" -lt "$MIN_FREE" ] && { echo "!! only ${FREE}GB free (< ${MIN_FREE}) — aborting this round"; exit 2; }
df -h "$ROOT" | tail -1

# ---- 1. pull data (spoof + genuine) into the layout train_corpus.py expects ----
#   IndicSynth   -> $DATA/indicsynth/<Capitalized>/train-000NN-of-*.parquet
#   IndicVoices  -> $DATA/indicvoices_real/<lower>/train-000NN-of-*.parquet
echo "[1/5] pulling data (shards 0..$S1 per language)"
TOKEN_ARG=(); [ -n "${HF_TOKEN:-}" ] && TOKEN_ARG=(--token "$HF_TOKEN")
for L in ${LANGS//,/ }; do
  ll=$(echo "$L" | tr 'A-Z' 'a-z')
  Cap=$(echo "$ll" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')
  # NB: the `hf` CLI wants `--include` ONCE PER PATTERN (repeatable flag).
  IS_ARGS=(); IV_ARGS=()
  for n in $(seq 0 "$S1"); do
    p=$(printf "%05d" "$n")
    IS_ARGS+=(--include "$Cap/train-$p-of-*")
    IV_ARGS+=(--include "$ll/train-$p-of-*")
  done
  echo "  [$ll] spoof  <- shards 0..$S1"
  "$HF" download vdivyasharma/IndicSynth --repo-type dataset "${TOKEN_ARG[@]}" \
     --local-dir "$DATA/indicsynth" "${IS_ARGS[@]}" 2>&1 | tail -n 3
  echo "  [$ll] genuine<- shards 0..$S1"
  "$HF" download ai4bharat/IndicVoices --repo-type dataset "${TOKEN_ARG[@]}" \
     --local-dir "$DATA/indicvoices_real" "${IV_ARGS[@]}" 2>&1 | tail -n 3
  is_n=$(find "$DATA/indicsynth/$Cap" -name '*.parquet' 2>/dev/null | wc -l | tr -d ' ')
  iv_n=$(find "$DATA/indicvoices_real/$ll" -name '*.parquet' 2>/dev/null | wc -l | tr -d ' ')
  echo "  [$ll] staged: $is_n spoof, $iv_n genuine"
  [ "${iv_n:-0}" -eq 0 ] && echo "  !! 0 genuine shards for $ll — see the hf output above (gated repo? token? shard name?)"
done

# ---- 1b. inject pre-generated fakes (e.g. MMS-TTS) for languages with no spoof set ----
if [ -n "${FAKES_MANIFEST:-}" ] && [ -f "$FAKES_MANIFEST" ]; then
  mkdir -p "$DATA/worst_ai"
  cat "$FAKES_MANIFEST" >> "$DATA/worst_ai/manifest.jsonl"
  echo "[fakes] injected $(wc -l < "$FAKES_MANIFEST" | tr -d ' ') rows from $FAKES_MANIFEST"
fi

# ---- 2. generate Worst-AI attacks (Bhashini + local generators) ----
echo "[2/5] generating attack clips"
python - "$LANGS" "$DATA" <<'PY' || true
import sys; sys.path.insert(0,'backend')
import gen_worst_ai as G
langs=[x.strip() for x in sys.argv[1].split(',') if x.strip()]; out=sys.argv[2]+"/worst_ai"
texts={"hi":"नमस्ते, मैं आपके बैंक से बोल रहा हूँ, कृपया अपना ओटीपी बताइए।","ta":"உங்கள் கணக்கை உறுதிப்படுத்த வேண்டும்.",
       "mr":"तुमचे खाते तपासा.","bn":"আপনার অ্যাকাউন্ট যাচাই করুন।","te":"మీ ఖాతా వివరాలు నిర్ధారించండి."}
for lg in langs:
    try: G.generate(texts.get(lg,"नमस्ते, कृपया पुष्टि करें।"), lg, telephony=True, out=out)
    except Exception as e: print("gen err", lg, str(e)[:120])
PY

# ---- 3. train (GPU) ----  (pass the SLOT's GPU, never a hardcoded 0)
echo "[3/5] training XLS-R + RawBoost on gpu=${GPU:-auto}"
TRAIN_OK=0
python backend/pipeline/train_corpus.py --data-root "$DATA" --langs "$LANGS" \
  --epochs "$EPOCHS" --gpu "${GPU:-0}" $LIMIT --out "$CKPT" && TRAIN_OK=1 \
  || echo "!! training failed (see log)"

# ---- 4. evaluate ----
echo "[4/5] evaluating"
if [ -f "$CKPT/scores.csv" ]; then python backend/eval_gengap.py --csv "$CKPT/scores.csv"; else echo "  (no scores.csv)"; fi

# ---- 5. cleanup ----
echo "[5/5] cleanup"
if [ "$KEEP_DATA" = "0" ]; then rm -rf "$DATA"; echo "  data deleted; checkpoint kept"; else echo "  --keep-data"; fi

# only mark done if training actually produced a checkpoint — otherwise leave it for retry
if [ "$TRAIN_OK" = "1" ] && [ -f "$CKPT/last.pt" ]; then
  touch "$DONE_MARK"
  echo "==== ROUND DONE $TS  ckpt=$CKPT ===="
else
  echo "==== ROUND FAILED $TS  (lang=$LANGS) — NOT marked done; resume.sh will retry ===="
  exit 3
fi
