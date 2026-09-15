#!/usr/bin/env bash
# VoxShield — ONE hands-off command: download all datasets on the DGX, then train
# on everything. Run inside tmux; it downloads + trains unattended and logs to
# ~/logs/voxshield/everything_<ts>.log. Safe to re-run (downloads resume, skips done).
set -u
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1
PY=$HOME/miniconda3/envs/voxshield/bin/python
RAW=$HOME/data/voxdata/raw
LOG=$HOME/logs/voxshield/everything_$(date +%Y%m%d_%H%M).log
mkdir -p "$RAW" "$HOME/logs/voxshield"
exec > >(tee -a "$LOG") 2>&1     # everything to the log AND screen
say(){ echo "[$(date +%H:%M:%S)] $*"; }

say "==================== DOWNLOAD PHASE ===================="
cd "$RAW"
$PY - <<'PYEOF'
from huggingface_hub import snapshot_download as dl
jobs = [
  ("vdivyasharma/IndicSynth","indicsynth",
     ['Hindi/*','Bengali/*','Marathi/*','Telugu/*','Malayalam/*','README.md']),
  ("ai4bharat/IndicVoices","indicvoices_real", ['hindi/*','bengali/*']),
  ("isjwdu/DFADD","dfadd", None),
  ("mueller91/MLAAD","mlaad", None),
  ("ai4bharat/Rural_Women_Bhojpuri","rural_bhojpuri", None),
]
for repo,name,pat in jobs:
    for attempt in range(4):
        try:
            print(f">>> {repo} -> {name}")
            dl(repo, repo_type="dataset", local_dir=name,
               allow_patterns=pat, max_workers=4)
            print(f"=== {name} done ==="); break
        except Exception as e:
            print(f"!! {name} attempt {attempt} failed: {e.__class__.__name__}; retry in 120s")
            import time; time.sleep(120)
print(">>> ALL DOWNLOADS ATTEMPTED")
PYEOF

say "==================== TRAIN PHASE ===================="
cd "$HOME/projects/voxshield/backend/pipeline"
# --limit-per caps per-source so the run finishes in hours not days.
# Raise it (e.g. 40000) or delete it for the full uncapped run (30h+).
$PY train_corpus.py --data-root "$RAW" \
    --limit-per 25000 --epochs 4 --bs 16 --lr 5e-5 --holdout-generator xtts --gpu 0

say "==================== ALL DONE ===================="
say "checkpoint: ~/checkpoints/voxshield/xlsr_corpus/last.pt"
