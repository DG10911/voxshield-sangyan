#!/usr/bin/env bash
# VoxShield — resilient Mac -> DGX sync of the fixed generators / support models.
# Survives flaky campus Wi-Fi: retries with backoff, resumes each attempt, and
# aborts a stalled transfer via rsync --timeout so the loop can retry. Idempotent.
#
# RUNS ON THE MAC (source lives on the KIOXIA SSD; destination is the DGX).
#
# Usage:
#   bash sync_generators.sh                 # generators: KIOXIA voxdata/models -> dgx:~/voxshield/models/generators
#   bash sync_generators.sh --loop          # keep retrying until it succeeds (walk away)
#   bash sync_generators.sh --max 12        # max attempts (default 8)
#   bash sync_generators.sh --src DIR --dst DIR
#   bash sync_generators.sh --host user@1.2.3.4
#   bash sync_generators.sh --check         # connectivity + sizes only, no copy
#
# Env overrides: DGX_HOST, SRC, DST, MAX_ATTEMPTS, RSYNC_TIMEOUT
set -uo pipefail

DGX_HOST=${DGX_HOST:-dgx}
SRC=${SRC:-/Volumes/KIOXIA/voxdata/models/}
DST=${DST:-voxshield/models/generators/}          # relative to the DGX home
MAX_ATTEMPTS=${MAX_ATTEMPTS:-8}
RSYNC_TIMEOUT=${RSYNC_TIMEOUT:-120}
LOOP=0; CHECK=0

while [ $# -gt 0 ]; do
  case "$1" in
    --loop) LOOP=1;;
    --check) CHECK=1;;
    --max) MAX_ATTEMPTS=$2; shift;;
    --host) DGX_HOST=$2; shift;;
    --src) SRC=$2; shift;;
    --dst) DST=$2; shift;;
    -h|--help) sed -n '2,16p' "$0"; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac; shift
done

# rsync 2.6.9 (macOS default) has no --mkpath/--append-verify/--info; keep flags old-safe.
RSYNC_OPTS=(-a --partial --partial-dir=.rsync-partial --progress --timeout="$RSYNC_TIMEOUT"
            --exclude='.cache' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git')

ts(){ date '+%H:%M:%S'; }
say(){ printf '%s  %s\n' "$(ts)" "$*"; }

[ -d "$SRC" ] || { echo "!! source not found: $SRC" >&2; echo "   (is KIOXIA mounted? ls /Volumes)" >&2; exit 1; }

# ---- preflight: DGX reachable? ----
say "host: $DGX_HOST   src: $SRC   dst: ~/$DST"
if ! ssh -o ConnectTimeout=10 -o BatchMode=no "$DGX_HOST" 'echo ok' >/dev/null 2>&1; then
  echo "!! cannot ssh to '$DGX_HOST' (are you on the SRM network?)" >&2
  exit 1
fi
say "DGX reachable ✓"
ssh "$DGX_HOST" "mkdir -p \"\$HOME/$DST\"" || { echo "!! remote mkdir failed" >&2; exit 1; }

# ---- sizes ----
local_sz=$(du -sh "$SRC" 2>/dev/null | cut -f1)
rem_sz=$(ssh "$DGX_HOST" "du -sh \"\$HOME/$DST\" 2>/dev/null | cut -f1")
say "size  local=$local_sz   remote(before)=$rem_sz"
if [ "$CHECK" = "1" ]; then
  say "--check only; done."
  exit 0
fi

attempt=1; backoff=5
while :; do
  say "──────── attempt $attempt/$MAX_ATTEMPTS ────────"
  rsync "${RSYNC_OPTS[@]}" "$SRC" "$DGX_HOST:\$HOME/$DST"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    say "rsync finished OK ✓"
    break
  fi
  say "rsync exited rc=$rc (network/timeout)."
  if [ "$attempt" -ge "$MAX_ATTEMPTS" ] && [ "$LOOP" != "1" ]; then
    say "!! giving up after $attempt attempts. Re-run the same command to resume."
    exit "$rc"
  fi
  attempt=$((attempt+1))
  say "retrying in ${backoff}s (resumes where it left off)…"
  sleep "$backoff"
  backoff=$(( backoff*2 )); [ "$backoff" -gt 60 ] && backoff=60
done

# ---- verify (count local WITHOUT the excluded dirs so the comparison is fair) ----
say "verifying…"
rem_sz=$(ssh "$DGX_HOST" "du -sh \"\$HOME/$DST\" 2>/dev/null | cut -f1")
rem_n=$(ssh "$DGX_HOST" "find \"\$HOME/$DST\" -type f 2>/dev/null | wc -l | tr -d ' '")
loc_n=$(find "$SRC" -type f \
          -not -path '*/.cache/*' -not -path '*/__pycache__/*' \
          -not -name '*.pyc' -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
say "size  local=$local_sz   remote(after)=$rem_sz"
say "files local(excl. caches)=$loc_n   remote=$rem_n"
if [ "${rem_n:-0}" -ge "${loc_n:-1}" ]; then
  say "✅ SYNC COMPLETE — generators ready on the DGX"
else
  say "⚠️  remote has fewer files than expected ($rem_n < $loc_n) — re-run to top up."
fi
