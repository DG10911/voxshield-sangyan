#!/usr/bin/env bash
# VoxShield — one-shot environment setup for a shell (Mac or DGX).
#
#   source deploy/dgx/dgx_setup_env.sh
#
# Secrets are NEVER stored in this file. It reads them from $VOXSHIELD_ENV
# (default: ~/.config/voxshield.env). Create that file once with:
#   mkdir -p ~/.config && cat > ~/.config/voxshield.env <<'EOF'
#   export HF_TOKEN=hf_xxx
#   export BHASHINI_USER_ID=xxx
#   export BHASHINI_API_KEY=xxx
#   export BHASHINI_INFERENCE_KEY=xxx
#   EOF
#   chmod 600 ~/.config/voxshield.env
#
# Must be SOURCED (not executed) so the exports land in your current shell.

# --- root + cache dirs (keep heavy data off the root disk) ---
export VOXSHIELD_ROOT="${VOXSHIELD_ROOT:-$HOME/voxshield}"
export HF_HOME="${HF_HOME:-$VOXSHIELD_ROOT/hf_cache}"
export TORCH_HOME="${TORCH_HOME:-$VOXSHIELD_ROOT/models}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$VOXSHIELD_ROOT/tmp/pip}"
mkdir -p "$VOXSHIELD_ROOT" "$HF_HOME" "$PIP_CACHE_DIR" 2>/dev/null

# --- TLS (DGX conda python often can't find a CA bundle) ---
if [ -z "${SSL_CERT_FILE:-}" ]; then
  _ca=$(python3 -c "import certifi;print(certifi.where())" 2>/dev/null \
        || python  -c "import certifi;print(certifi.where())" 2>/dev/null)
  [ -n "${_ca:-}" ] && export SSL_CERT_FILE="$_ca" && export REQUESTS_CA_BUNDLE="$_ca"
  unset _ca
fi

# --- VoxShield runtime defaults ---
export DIARIZATION_BACKEND="${DIARIZATION_BACKEND:-nemo}"
export BHASHINI_PIPELINE_ID="${BHASHINI_PIPELINE_ID:-64392f96daac500b55c543cd}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-1}"

# --- secrets ---
VOXSHIELD_ENV="${VOXSHIELD_ENV:-$HOME/.config/voxshield.env}"
if [ -f "$VOXSHIELD_ENV" ]; then
  # shellcheck disable=SC1090
  . "$VOXSHIELD_ENV"
else
  echo "!! no secrets file at $VOXSHIELD_ENV — HF/Bhashini calls will fail."
  echo "   create it (see header) then re-source this script."
fi

# --- masked status ---
mask(){ [ -n "${1:-}" ] && printf '%s…(len %s)' "$(printf '%s' "$1" | cut -c1-6)" "${#1}" || printf 'MISSING'; }
echo "── VoxShield env ──────────────────────────────"
printf "  root       : %s\n" "$VOXSHIELD_ROOT"
printf "  HF_HOME    : %s\n" "$HF_HOME"
printf "  HF_TOKEN   : %s\n" "$(mask "${HF_TOKEN:-}")"
printf "  BHASHINI   : user=%s api=%s inf=%s\n" \
  "$(mask "${BHASHINI_USER_ID:-}")" "$(mask "${BHASHINI_API_KEY:-}")" "$(mask "${BHASHINI_INFERENCE_KEY:-}")"
printf "  CA bundle  : %s\n" "${SSL_CERT_FILE:-none}"
printf "  diarization: %s\n" "$DIARIZATION_BACKEND"
echo "───────────────────────────────────────────────"
