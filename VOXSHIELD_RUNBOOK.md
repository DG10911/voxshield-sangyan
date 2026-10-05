# VoxShield — OPERATIONS RUNBOOK (do these in order)

## Phase 0 · What is already running on the DGX (nothing to do)
tmux sessions, autonomous, survive your laptop closing:
```
vox5p_slot0/1/2 + vox5p_w0/w1/w2   low-res 8 languages (Indic-Parler) → 2-class retrain
vox6_wait                          improve ur/or/ml (AASIST + adversarial)
vox7_wait                          orthogonalized XLS-R probe (C5)
vox8_wait                          multi-generator pass
vox_setup                          installing TTS / f5-tts / kokoro / piper
```
Check: `ssh dgx 'tmux ls'`

## Phase 1 · YOU: add the API keys (5 min, unblocks Sarvam + commercial fakes)
```
ssh dgx
nano ~/.config/voxshield.env
```
Add:
```
SARVAM_API_KEY=<from sarvam.ai>
ELEVENLABS_API_KEY=<optional>
CARTESIA_API_KEY=<optional>
HUME_API_KEY=<optional>
PLAYHT_API_KEY=<optional>
```
Then `source ~/.config/voxshield.env`

## Phase 2 · Install/verify the open generators (on DGX)
```
cd ~/voxshield && export PATH="$HOME/miniconda3/envs/voxshield/bin:$HOME/miniconda3/bin:$PATH"
bash setup_generators.sh
python backend/generator_adapters.py      # shows OK / --reason per generator
```

## Phase 3 · Let the queue finish (≈4–8 h) — no laptop needed
Watch (optional):
```
ssh dgx 'cd ~/voxshield; tail -f logs/lowres_parler_*.log logs/improve_*.log logs/orth_*.log logs/multigen_*.log'
```
Confirm when done: `ssh dgx 'tmux ls | grep -E "vox5p|vox6|vox7|vox8"'` → should be empty.

## Phase 4 · Pull the new results (from your Mac)
```
ssh dgx 'cd ~/voxshield; for L in kashmiri nepali sindhi bodo dogri konkani manipuri santali; do echo "== $L"; cat checkpoints/round_*_${L}*/report* 2>/dev/null | tail -5; done'
ssh dgx 'cd ~/voxshield; cat phase4/improve_c2_*.txt; grep -H "EER" logs/orth_*.log'
```
Then give the outputs to me → I update the all-numbers digest + paper.

## Phase 5 · Re-measure & update
On DGX: `python backend/paper_report.py --csv checkpoints/round_*/scores.csv --baseline clean --out results/report_all_norm.txt`
I then refresh `VOXSHIELD_ALL_NUMBERS.md`, `voxshield_numbers.html`, and paper Tables 1–5.

## Phase 6 · Backup to KIOXIA (from your Mac; ~70 GB)
```
rsync -avh --progress \
  dgx:'~/voxshield/{backend,deploy,models,checkpoints,data_fakes,registries,results,phase2,phase4,*.md,*.pptx,*.mp4}' \
  /Volumes/KIOXIA/voxshield/dgx_snapshot/
```

## Phase 7 · Prepare remaining docs
- Bhashini live proof: `ssh dgx 'cd ~/voxshield && python backend/bhashini_livetest.py'` (save output).
- AIKosh: keep `VOXSHIELD_AIKOSH_MASTER_LIST.md` + adapter.
- Fix console label: "Seen EER 1.62%" → "seen (freevc24) 1.62% / seen aggregate 9.57%".

## Phase 8 · Submit (SANGYAN)
- Explain-your-solution (≤500 chars) → in `SANGYAN_SUBMISSION.md`
- Source: `https://github.com/DG10911/voxshield-sangyan`
- Video: `SANGYAN_VoxShield_demo.mp4`
- Deck: `SANGYAN_VoxShield.pptx`

## Quick reference — what each script does
| Script | Purpose |
|---|---|
| `deploy/dgx/setup_generators.sh` | install all open TTS engines |
| `backend/generator_adapters.py` | registry of all 28 generators |
| `deploy/dgx/launch_lowres_parler.sh` | real fakes for low-res langs |
| `deploy/dgx/launch_improve_eer.sh` | ur/or/ml stronger training |
| `deploy/dgx/launch_orth.sh` | orthogonalized XLS-R probe (C5) |
| `deploy/dgx/launch_multigen.sh` | all-generators augmentation pass |
