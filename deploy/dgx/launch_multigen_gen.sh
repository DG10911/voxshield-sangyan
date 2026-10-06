#!/usr/bin/env bash
# VoxShield — GENERATION ONLY (CPU/network, no GPU): build the multi-generator fake corpora
# for every language now, so the later training pass (launch_multigen.sh) reuses the cache.
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}; cd "$ROOT" || exit 1
export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
export COQUI_TOS_AGREED=1
export ENGINE_TIMEOUT=900
. "$HOME/voxshield/dgx_setup_env.sh" >/dev/null 2>&1 || source "$HOME/.config/voxshield.env" 2>/dev/null || true
[ -n "${HF_TOKEN:-}" ] && export HF_TOKEN

LANGS="${LANGS:-hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi urdu sanskrit bodo dogri kashmiri konkani manipuri nepali santali sindhi}"
N=${N:-200}
ENGINES=${ENGINES:-sarvam,cartesia,mms}

for L in $LANGS; do
  echo "==== gen $L ===="
  python backend/gen_fakes_multi.py --lang "$L" --n "$N" --out "data_fakes_multi/${L}" --engines "$ENGINES"
done
echo "MULTIGEN GENERATION COMPLETE"
