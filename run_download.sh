#!/usr/bin/env bash
# VoxShield approved 800GB dataset download — sequenced smallest→largest so
# essentials land first. Each step is non-fatal (|| true) and resumable.
set -u
VOX=/Volumes/KIOXIA/voxdata
HF=/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/.venv_voxshield/bin/hf
LOG="$VOX/download_$(date +%Y%m%d_%H%M).log"
export HF_HUB_DISABLE_TELEMETRY=1

say(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
free(){ df -h /Volumes/KIOXIA | tail -1 | awk '{print "   free:",$4}'; }
dl(){   # dl <repo_id> <localname> [extra hf args...]
  local id="$1" name="$2"; shift 2
  say "↓ $id → raw/$name"
  "$HF" download "$id" --repo-type dataset --local-dir "$VOX/raw/$name" "$@" >>"$LOG" 2>&1 \
    && say "✓ done $name $(free)" || say "✗ FAILED $name (see log; may need license-accept on the HF page)"
}
dlm(){  # model download
  local id="$1" name="$2"; shift 2
  say "↓ model $id → models/$name"
  "$HF" download "$id" --local-dir "$VOX/models/$name" "$@" >>"$LOG" 2>&1 \
    && say "✓ done model $name" || say "✗ FAILED model $name"
}

say "=== VoxShield download start ==="; free

# --- Tier 1: small high-value (fairness + Bengali fakes) ---
dl ai4bharat/indicvoices-cleaned indicvoices_cleaned
dl ai4bharat/Lahaja              lahaja
dl ai4bharat/Svarah              svarah
dl sifat1221/banglaFake          banglafake

# --- Tier 2: modern fakes + cross-lingual OOD + rural fairness ---
dl isjwdu/DFADD                  dfadd
dl mueller91/MLAAD               mlaad
dl ai4bharat/Rural_Women_Bhojpuri rural_bhojpuri

# --- Tier 3: TTS engines (generate our own fakes) ---
dlm ai4bharat/IndicF5            indicf5
dlm ai4bharat/indic-parler-tts   indic-parler-tts
dlm ai4bharat/vits_rasa_13       vits_rasa_13
dlm coqui/XTTS-v2                xtts-v2
dlm SWivid/F5-TTS               f5-tts

# --- Tier 4: real Indic class (Hindi + Bengali subset of IndicVoices) ---
dl ai4bharat/IndicVoices indicvoices_real --include "hindi/*" --include "bengali/*"

# --- Tier 5: THE MOAT — IndicSynth multi-cloner fakes (5 langs, ~246 GB) ---
dl vdivyasharma/IndicSynth indicsynth \
   --include "Hindi/*" --include "Bengali/*" --include "Marathi/*" \
   --include "Telugu/*" --include "Malayalam/*" --include "README.md"

# --- Tier 6: codec diversity (100 GB split archive; extract after) ---
dl CodecFake/CodecFake_Plus_Dataset codecfake_plus

say "=== ALL DOWNLOADS ATTEMPTED ==="; free
say "note: CodecFake+ is a split .xz archive under raw/codecfake_plus — extract before use."
