#!/usr/bin/env bash
# VoxShield — live one-screen DGX dashboard.
# Shows: every GPU slot + the language it is on, per-language progress, overall
# progress bar, ETA, GPU utilization, disk, and the tail of the active round log.
# Safe to run anytime; read-only. Runs on the DGX.
#
# Usage:
#   bash dashboard.sh            # auto-refresh every 5s (Ctrl-C to quit)
#   bash dashboard.sh --once     # print one frame and exit (for logs/CI)
#   INTERVAL=2 bash dashboard.sh # custom refresh
#   ROUND_HOURS=5 bash dashboard.sh
set -uo pipefail

ROOT=${VOXSHIELD_ROOT:-$HOME/voxshield}
INTERVAL=${INTERVAL:-5}
ROUND_HOURS=${ROUND_HOURS:-6}
ONCE=0
[ "${1:-}" = "--once" ] && ONCE=1

LANGS="hindi bengali marathi telugu tamil gujarati kannada malayalam odia punjabi assamese urdu sanskrit nepali maithili bodo dogri kashmiri manipuri konkani santali sindhi english"
TOTAL=0; for _ in $LANGS; do TOTAL=$((TOTAL+1)); done

c(){ # colour if tty
  if [ -t 1 ]; then printf "\033[%sm%s\033[0m" "$1" "$2"; else printf "%s" "$2"; fi
}
bar(){ # $1=done $2=total $3=width
  local d=$1 t=$2 w=$3 filled empty pct i out=""
  [ "$t" -le 0 ] && t=1
  filled=$(( d*w/t )); empty=$(( w-filled )); pct=$(( d*100/t ))
  for ((i=0;i<filled;i++)); do out="$out#"; done
  for ((i=0;i<empty;i++)); do out="$out."; done
  printf "[%s] %d%% (%d/%d)" "$out" "$pct" "$d" "$t"
}
human_eta(){ # $1 = hours (float) -> "Xh Ym"
  awk -v h="$1" 'BEGIN{ if(h<=0){print "done"} else {H=int(h); M=int((h-H)*60); if(H>0) printf "%dh %dm",H,M; else printf "%dm",M } }'
}

render(){
  local now host up load
  now=$(date '+%Y-%m-%d %H:%M:%S')
  host=$(hostname 2>/dev/null || echo dgx)
  up=$(uptime 2>/dev/null | sed 's/.*up //; s/,.*//')

  # ---- completed languages ----
  local done=0; local donelist=""
  local L
  for L in $LANGS; do
    if [ -f "$ROOT/checkpoints/$L.done" ]; then done=$((done+1)); donelist="$donelist $L"; fi
  done
  local remain=$(( TOTAL - done ))

  # ---- tmux slots (parallel run) ----
  local sessions; sessions=$(tmux list-sessions -F '#{session_name}' 2>/dev/null | grep -E '^vox_' || true)
  local nslots; nslots=$(printf '%s\n' "$sessions" | grep -c . || true)

  echo "════════════════════════════════════════════════════════════════════════════"
  printf " VOXSHIELD · DGX DASHBOARD      %s      %s (up %s)\n" "$now" "$host" "$up"
  echo "════════════════════════════════════════════════════════════════════════════"

  # ---- overall ----
  printf " OVERALL   %s\n" "$(bar "$done" "$TOTAL" 40)"
  if [ "$remain" -gt 0 ]; then
    if [ "${nslots:-0}" -gt 1 ]; then
      local eta; eta=$(awk -v r="$remain" -v s="$nslots" -v h="$ROUND_HOURS" 'BEGIN{print r/s*h}')
      printf " REMAINING %d languages · %d active slot(s) · ETA ~%s (parallel, ~%sh/lang)\n" \
        "$remain" "$nslots" "$(human_eta "$eta")" "$ROUND_HOURS"
    else
      local eta; eta=$(awk -v r="$remain" -v h="$ROUND_HOURS" 'BEGIN{print r*h}')
      printf " REMAINING %d languages · sequential · ETA ~%s (parallel with launch_parallel.sh ≈ ~%s)\n" \
        "$remain" "$(human_eta "$eta")" "$(human_eta "$(awk -v r="$remain" -v h="$ROUND_HOURS" 'BEGIN{print r/8*h}')")"
    fi
  else
    printf " %s\n" "$(c '1;32' 'ALL 23 LANGUAGES COMPLETE')"
  fi

  # ---- per-slot view ----
  echo "────────────────────────────────────────────────────────────────────────────"
  if [ "${nslots:-0}" -gt 0 ]; then
    printf " %-10s %-12s %-9s %s\n" "SLOT" "SESSION" "LANG" "LAST LOG LINE"
    local s cur line
    for s in $sessions; do
      cur=$(tmux capture-pane -pt "$s" -S -400 2>/dev/null \
            | grep -Eo '(##########|##### LANGUAGE) [A-Za-z]+' | tail -1 \
            | awk '{print $NF}')
      [ -z "$cur" ] && cur="-"
      line=$(tmux capture-pane -pt "$s" -S -3 2>/dev/null | grep -v '^$' | tail -1 | cut -c1-60)
      printf " %-10s %-12s %-9s %s\n" "$s" "$s" "$(c '1;36' "$cur")" "$line"
    done
  else
    printf " (no tmux slots running — start with: bash launch_parallel.sh)\n"
  fi

  # ---- per-language progress grid ----
  echo "────────────────────────────────────────────────────────────────────────────"
  printf " LANGUAGES  "
  local i=0
  for L in $LANGS; do
    if [ -f "$ROOT/checkpoints/$L.done" ]; then printf "%s " "$(c '1;32' "$L")"
    else printf "%s " "$(c '0;90' "$L")"; fi
    i=$((i+1)); [ $((i%8)) -eq 0 ] && printf "\n            "
  done
  printf "\n"
  printf "            %s done   %s pending\n" "$(c '1;32' "$done")" "$(c '0;90' "$remain")"

  # ---- GPU ----
  echo "────────────────────────────────────────────────────────────────────────────"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu \
      --format=csv,noheader 2>/dev/null | awk -F', *' '{printf " GPU%-2s %4s util  %6s/%-6s mem  %s°C\n",$1,$2,$3,$4,$5}'
  else
    echo " (nvidia-smi not available)"
  fi

  # ---- disk ----
  echo "────────────────────────────────────────────────────────────────────────────"
  if [ -d "$ROOT" ]; then
    local dsz csz msz
    dsz=$(du -sh "$ROOT/data" 2>/dev/null | cut -f1); dsz=${dsz:--}
    csz=$(du -sh "$ROOT/checkpoints" 2>/dev/null | cut -f1); csz=${csz:--}
    msz=$(du -sh "$ROOT/models" 2>/dev/null | cut -f1); msz=${msz:--}
    printf " DISK  free %s\n" "$(df -h "$ROOT" | awk 'NR==2{print $4" of "$2" ("$5" used)"}')"
    printf " SIZE  data=%-8s checkpoints=%-8s models=%-8s\n" "$dsz" "$csz" "$msz"
  else
    printf " DISK  %s not found\n" "$ROOT"
  fi

  # ---- active log tail ----
  local LOG; LOG=$(ls -t "$ROOT"/logs/round_*.log 2>/dev/null | head -1)
  echo "────────────────────────────────────────────────────────────────────────────"
  if [ -n "$LOG" ]; then
    printf " ACTIVE LOG  %s\n" "$LOG"
    tail -n 6 "$LOG" | sed 's/^/   /'
  else
    printf " ACTIVE LOG  (none yet)\n"
  fi

  # ---- running processes ----
  local procs; procs=$(pgrep -af 'train_corpus|run_round|gen_worst_ai|hf download' 2>/dev/null | wc -l | tr -d ' ')
  printf " PROCESSES  %s active (train/round/gen/hf)\n" "$procs"
  echo "════════════════════════════════════════════════════════════════════════════"
  if [ "$ONCE" != "1" ]; then
    printf " refresh %ss · Ctrl-C quit · watch.sh (plain) · resume.sh --go (continue)\n" "$INTERVAL"
  fi
}

if [ "$ONCE" = "1" ]; then
  render
else
  while true; do
    tput clear 2>/dev/null || printf '\033[2J\033[H'
    render
    sleep "$INTERVAL"
  done
fi
