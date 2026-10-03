#!/usr/bin/env bash
# VoxShield — resume the 23-language sweep where it left off.
# Detects completed languages (checkpoints/<lang>.done) and in-progress rounds (logs/state_*.json),
# then relaunches the sweep; run_round.sh skips any language already complete.
#
# Usage:  bash resume.sh            # just report status
#         bash resume.sh --go       # report + launch the remaining languages (detached)
set -uo pipefail
ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
cd "$ROOT" || { echo "no $ROOT"; exit 1; }
LANGS="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi assamese urdu sanskrit nepali maithili bodo dogri kashmiri manipuri konkani santali sindhi english"

echo "=== VoxShield 23-language sweep status ===  ($ROOT)"
done=0; pend=""
for L in $LANGS; do
  if [ -f "$ROOT/checkpoints/$L.done" ]; then
    printf "  ✅ %-10s\n" "$L"; done=$((done+1))
  else
    printf "  ⬜ %-10s\n" "$L"; pend="$pend $L"
  fi
done
echo "-----------------------------------------"
echo "  complete: $done / 23"
[ -f "$ROOT/checkpoints" ] && echo "  checkpoints: $(ls -1 "$ROOT/checkpoints" 2>/dev/null | grep -c '\.done$') done, $(ls -1d "$ROOT/checkpoints"/round_* 2>/dev/null | wc -l | tr -d ' ') dirs"
for s in "$ROOT"/logs/state_*.json; do [ -f "$s" ] && echo "  in-progress: $(cat "$s")"; done

if [ -n "${pend// }" ]; then
  echo
  echo "  remaining:$pend"
  if [ "${1:-}" = "--go" ]; then
    echo "  ▶ relaunching remaining languages (detached)…"
    bash launch_round.sh all
  else
    echo "  run:  bash resume.sh --go     (or: bash launch_round.sh all)"
  fi
else
  echo "  🎉 all 23 languages complete — run the per-language eval / export to KIOXIA"
fi
