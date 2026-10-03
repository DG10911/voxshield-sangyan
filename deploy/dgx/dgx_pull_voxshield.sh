#!/usr/bin/env bash
# VoxShield on DGX A100 — FULL catalogue pull to the 14 TB RAID.
# Run on the DGX (account srmist2). No sudo needed.
# Usage:  bash dgx_pull_voxshield.sh [stage|full]
#   stage = core training set (~500 GB)   |   full = entire catalogue (~2.5 TB)
set -uo pipefail

# ---- where the data goes (RAID, 7.2 TB free) ----
ROOT=${VOXSHIELD_ROOT:-/raid/srmist2/voxshield}
if [ ! -w "$(dirname "$ROOT")" ] && [ ! -d "$ROOT" ]; then
  echo "!! $ROOT not writable — falling back to \$HOME/voxshield"; ROOT=$HOME/voxshield
fi
export VOXSHIELD_ROOT=$ROOT
export HF_HOME=$ROOT/hf_cache
export HF_HUB_ENABLE_HF_TRANSFER=1
mkdir -p "$ROOT"/{data,models,hf_cache,logs}
STAGE=${1:-stage}
LOG=$ROOT/logs/pull_$(date +%Y%m%d_%H%M).log
exec > >(tee -a "$LOG") 2>&1

echo "== VoxShield DGX pull ($STAGE) -> $ROOT   $(date)"

# ---- tooling (into current conda env; no sudo) ----
python -c "import huggingface_hub" 2>/dev/null || pip install -q -U huggingface_hub hf_transfer
HF=$(command -v hf || command -v huggingface-cli)
[ -n "$HF" ] || { echo "!! hf CLI missing"; exit 1; }

D=$ROOT/data
ds(){ "$HF" download "$1" --repo-type dataset --local-dir "$D/$2"; }
md(){ "$HF" download "$1" --local-dir "$ROOT/models/$2"; }

if [ "$STAGE" = "stage" ]; then
  echo "-- STAGE 1: core (attack + genuine + generators ~500 GB)"
  ds vdivyasharma/IndicSynth                  IndicSynth            # 540 GB full
  ds ai4bharat/IndicVoices                    IndicVoices           # 497 GB full
  ds ai4bharat/MANGO                          MANGO
  ds ai4bharat/Shrutilipi                     Shrutilipi
  md ai4bharat/IndicF5                        IndicF5
  md ai4bharat/indic-parler-tts               indic-parler-tts
  md bharatgenai/sooktam2                     sooktam2
  md ai4bharat/indic-conformer-600m-multilingual indic-conformer-600m
  md microsoft/speecht5_vc                    speecht5_vc
else
  echo "-- FULL catalogue"
  # ---- datasets ----
  ds vdivyasharma/IndicSynth      IndicSynth
  ds ai4bharat/IndicVoices        IndicVoices
  ds ai4bharat/indicvoices_r      IndicVoices-R
  ds ai4bharat/Shrutilipi         Shrutilipi
  ds ARTPARK-IISc/Vaani           Vaani
  ds ai4bharat/Rasa               Rasa
  ds ai4bharat/MANGO              MANGO
  ds ai4bharat/Lahaja             Lahaja
  ds ai4bharat/Svarah             Svarah
  ds ai4bharat/Rural_Women_Bhojpuri Rural_Women_Bhojpuri
  ds ai4bharat/Spoken-Tutorial    Spoken-Tutorial
  ds ai4bharat/Aksharantar        Aksharantar
  ds krutrim-ai-labs/IndicST      IndicST
  ds historyHulk/MoDeTrans        MoDeTrans
  # ---- models ----
  md ai4bharat/IndicF5             IndicF5
  md ai4bharat/indic-parler-tts    indic-parler-tts
  md bharatgenai/sooktam2          sooktam2
  md ai4bharat/indic-conformer-600m-multilingual indic-conformer-600m
  md ai4bharat/indicwav2vec_v1_hindi indicwav2vec-hi
  md microsoft/speecht5_vc         speecht5_vc
  md ai4bharat/Airavata            Airavata
fi

# ---- AIKosh HOSTED corpora (IndicTTS, SPICOR, SPRING-INX, tribals, …) ----
if [ -f "$(dirname "$0")/dgx_aikosh_pull.py" ]; then
  echo "-- AIKosh HOSTED corpora"
  python "$(dirname "$0")/dgx_aikosh_pull.py" "$ROOT/data/aikosh_hosted" || true
fi

echo "== DONE ($STAGE) $(date)  ->  $ROOT"
df -h "$ROOT" | tail -1
