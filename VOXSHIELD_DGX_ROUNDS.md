# VoxShield — DGX Training Rounds (sizes + work)
### How to build the whole system on the DGX without ever needing 2.2 TB at once. 2026-10-01.

**Principle:** the big corpora are **per-language folders** → each round pulls only what it needs,
trains, saves the checkpoint, then **deletes the data**. Peak disk ≈ 300–450 GB (fits 1.54 TB free).

---

## 0 · Fixed setup (once, ~30 GB — keep across all rounds)
| Item | Size |
|---|---|
| Code (`backend/`, console, SDKs) | ~50 MB |
| Attack generators (IndicF5 1.4 · Indic-Parler 3.8 · F5-TTS 6.3 · XTTS 1.9 · Sooktam2 6.7 · Fastspeech2 0.2) | ~20 GB |
| Support models (IndicConformer-600M 2.6 · IndicWav2Vec 1.3 · IndicTrans2 · IndicXlit · LID) | ~5 GB |
| Detector + speaker (ensemble + ECAPA + NeMo Sortformer) | ~3 GB |
| Manifests / registries / curated sets | ~1 GB |

---

## 0b · Where each asset lives right now (2026-10-01)
| Asset | On DGX? | On KIOXIA? | Notes |
|---|---|---|---|
| Code (`backend/`, console, SDKs) | ✅ | ✅ | synced |
| Detector ensemble + fusion head | ✅ cached (`~/.cache/huggingface`) | ✅ exported (`voxshield/models/hf_cache`) | loaded by `fusion.analyze` |
| ECAPA + NeMo Sortformer | ✅ cached | ✅ | verified |
| Attack generators — IndicF5 · Indic-Parler · F5-TTS · XTTS-v2 · VITS-Rasa | ❌ | ✅ (`voxdata/models/`) | copy KIOXIA→DGX or re-download |
| Attack generators — Sooktam2 · Fastspeech2 | ❌ | ❌ | download (or skip → Bhashini) |
| Support — IndicConformer-600M · IndicWav2Vec · IndicTrans2 · IndicXlit · LID | ❌ (Fastspeech2 zip only) | ⚠️ partial | download **or use Bhashini** |
| **Bhashini TTS / voice-clone** | ☁️ cloud | — | **0 GB** — generates attacks without storing generators |

**So:** the generators are **not on the DGX yet** — they're on **KIOXIA** (5 of them) and the rest need a download; *or* generate attacks via **Bhashini** (cloud, 0 storage). The fixed setup must be pulled to the DGX **once** in Round 0.

### Copy the fixed set Mac → DGX (resilient, survives flaky Wi-Fi)
Run on the **Mac** (KIOXIA mounted, on the SRM network):
```bash
# one-shot, auto-retry (resumes each attempt; aborts stalled links via --timeout)
bash deploy/dgx/sync_generators.sh

# walk away — keep retrying until it lands
bash deploy/dgx/sync_generators.sh --loop

# just connectivity + sizes, no copy
bash deploy/dgx/sync_generators.sh --check
```
It syncs `/Volumes/KIOXIA/voxdata/models/` → `dgx:~/voxshield/models/generators/` with `--partial --partial-dir`,
excludes `.cache`/`__pycache__`/`.git`, retries with backoff (5→60 s, default 8 attempts), and verifies file counts at the end.

---

## 1 · Rounds (work + size)

### Round 1 — Hindi-belt core  (~300 GB peak)
| Pull | Size |
|---|---|
| IndicSynth — **Hindi 52 · Marathi 40 · Bengali 31** (spoof) | 123 GB |
| IndicVoices — **Hindi 50 · Marathi 38 · Bengali 41** (genuine) | 129 GB |
| OOD — MLAAD 27 · WaveFake 6.8 · ASVspoof19 1.1 | 35 GB |
| Generated attacks (Bhashini TTS + IndicF5 clone → `scenario_render` G.711) | ~10 GB |
| **Work:** fine-tune **XLS-R-300M + RawBoost**, ~20–40 GPU-hrs; run `eval_gengap` | |
| **Output:** checkpoint v1 (~1–3 GB) → **delete the ~300 GB** | |

### Round 2 — Southern / Western  (~300 GB peak)
| Pull | Size |
|---|---|
| IndicSynth — **Telugu 85 · Malayalam 23** (spoof) | 108 GB |
| IndicVoices — **Kannada 39 · Odia 37 · Gujarati 28** (genuine) | 104 GB |
| Shrutilipi — **Tamil 32** subset | 32 GB |
| Rasa / Vaani samples (cross-dataset diversity) | ~50 GB |
| **Work:** continue fine-tune (multi-language), re-eval per-language | |
| **Output:** checkpoint v2 → **delete data** | |

### Round 3 — Scale + OOD hardening  (~420 GB peak)
| Pull | Size |
|---|---|
| IndicVoices-R — subset (re-synthesized attacks) | ~200 GB |
| Shrutilipi — **Hindi 95** subset | 95 GB |
| Vaani — sample (real accents/dialects) | ~100 GB |
| Cross-lingual clones (IndicTrans2 → IndicF5, all langs) | ~20 GB |
| **Work:** adversarial training (FGSM/PGD) + AASIST3 back-end + validate novelty | |
| **Output:** final checkpoint (+ optional distill to edge) → **delete data** | |

### ⭐ MANDATORY — 23-language sweep (the real path to 0/23 → 23/23)
**One round per language** (22 Eighth-Schedule + Indian English). Each: pull that language's spoof +
genuine → generate attacks → train/fine-tune → **update the language scorecard** → delete. Peak ≈ 150 GB each.
**Not optional — this is how mastery is earned.**

- **spoof source:** IndicSynth `<lang>` if present; else Bhashini TTS / IndicF5 clone + `scenario_render` G.711
- **genuine source:** IndicVoices `<lang>` if present; else IndicTTS Phase-3 + Shrutilipi/Rasa

| # | Language | Spoof (size) | Genuine (size) | Round ≈ | GPU-h |
|---|---|---|---|---|---|
| 1 | Hindi | IndicSynth 52 | IndicVoices 50 | ~110 GB | 6–8 |
| 2 | Bengali | IndicSynth 31 | IndicVoices 41 | ~80 GB | 5–7 |
| 3 | Marathi | IndicSynth 40 | IndicVoices 38 | ~85 GB | 5–7 |
| 4 | Telugu | IndicSynth 85 | IndicVoices — → IndicTTS 3 + gen | ~90 GB | 6–8 |
| 5 | Tamil | gen (Bhashini) | IndicTTS 2.9 + gen | ~30 GB | 4–6 |
| 6 | Gujarati | IndicSynth 51 | IndicVoices 28 | ~80 GB | 5–7 |
| 7 | Kannada | IndicSynth 68 | IndicVoices 39 | ~110 GB | 6–8 |
| 8 | Malayalam | IndicSynth 24 | IndicVoices 41 | ~70 GB | 5–6 |
| 9 | Odia | IndicSynth 24 | IndicVoices 37 | ~65 GB | 5–6 |
| 10 | Punjabi | IndicSynth 101 | IndicVoices partial | ~120 GB | 6–8 |
| 11 | Assamese | gen | IndicVoices 50 | ~60 GB | 5–6 |
| 12 | Urdu | gen | IndicVoices partial | ~40 GB | 4–6 |
| 13 | Sanskrit | IndicSynth 140 | gen | ~150 GB | 6–8 |
| 14 | Nepali | gen | IndicVoices 28 | ~40 GB | 4–6 |
| 15 | Maithili | gen | IndicVoices 29 | ~40 GB | 4–6 |
| 16 | Bodo | gen | IndicVoices 32 | ~45 GB | 4–6 |
| 17 | Dogri | gen | IndicVoices 23 | ~35 GB | 4–5 |
| 18 | Kashmiri | gen | IndicVoices 22 + Kashmiri-TTS | ~35 GB | 4–5 |
| 19 | Manipuri | gen | IndicVoices 24 | ~35 GB | 4–5 |
| 20 | Konkani | gen | IndicTTS | ~20 GB | 3–5 |
| 21 | Santali | gen | IndicTTS | ~20 GB | 3–5 |
| 22 | Sindhi | gen | IndicTTS | ~20 GB | 3–5 |
| 23 | English (Indian) | gen | SPICOR 7 + CommonVoice | ~40 GB | 4–6 |

Total ≈ 40 GPU-h; scorecard flips green one language at a time; peak disk ≈ 150 GB/round.
*(Prefer speed? group 3–4 languages per round using the thematic plan in §1.)*

---

## 2 · Disk trajectory
| Moment | Disk used on DGX |
|---|---|
| Fixed setup only | ~30 GB |
| During a round (data staged) | ~350–500 GB |
| Between rounds (data deleted) | **~35 GB** (fixed + checkpoint) |
| All 3 checkpoints + fixed | ~40 GB |
| **Peak at any time** | **≈ 500 GB** (fits 1.54 TB with room) |

## 3 · Time
| Round | GPU-hours (A100) | Wall-clock |
|---|---|---|
| R1 | ~20–40 | ~1 day |
| R2 | ~20–40 | ~1 day |
| R3 | ~30–50 | ~1–2 days |
| Per-language sweep | ~4–8 each | hours each |

## 4 · The loop (per round)
```bash
# ON THE DGX
export VOXSHIELD_ROOT=~/voxshield            # or /raid/srmist2/voxshield when granted
# 1) pull the round's subset (per-language shards)
python backend/aikosh_ingest.py              # or hf download <repo> --include "<lang>/*"
# 2) generate attacks (uses the fixed generators)
python backend/gen_worst_ai.py --text "..." --lang hi --telephony
# 3) train
python backend/train_wav2vec2_aug.py ...     # XLS-R + RawBoost  (see pipeline/train_corpus.py)
# 4) evaluate the gap
python backend/eval_gengap.py                # watch +9.95pt → target +3–6pt
# 5) save checkpoint, then free the data
cp -r <checkpoint> $VOXSHIELD_ROOT/checkpoints/r1/
rm -rf $VOXSHIELD_ROOT/data/*                # keep only the checkpoint
```

## 5 · What you keep after all rounds (~35 GB)
checkpoint(s) · detector + speaker models · generators (optional) · curated Golden/Zero-Day/Worst-Human · manifests/registries.
→ Export to KIOXIA, wipe the DGX (see handoff).

---

## 6 · Autonomous operation (leave the building, GPU keeps working)
You can only reach the DGX from the SRM academic network — so **launch the round detached** and walk away. The DGX (a server) never sleeps, and `tmux` keeps the job alive across SSH drops.

**Scripts (deploy/dgx/):** `run_round.sh` (the pipeline) · `launch_round.sh` (detached tmux) · `launch_parallel.sh` (8-GPU parallel) · `resume.sh` (continue) · `watch.sh` (plain status) · `dashboard.sh` (live one-screen dashboard) · `sync_generators.sh` (Mac→DGX resilient copy) · **`dgx_setup_env.sh` (one-shot env)**.

```bash
# on the DGX, first time
scp dgx:~/voxshield/deploy/dgx/*.sh ~/voxshield/ 2>/dev/null || true   # or they arrive via your repo
chmod +x run_round.sh launch_round.sh launch_parallel.sh resume.sh watch.sh dashboard.sh

# one-shot env (reads secrets from ~/.config/voxshield.env; never stores them in the repo)
source dgx_setup_env.sh
```

# launch ONE language detached
bash launch_round.sh "hindi,marathi" --epochs 3
# launch the FULL 23-language sweep detached (runs sequentially for hours)
bash launch_round.sh all

# then just detach and leave:
#   Ctrl-b d
# come back later:
#   tmux attach -t vox_hindi_marathi   (or: bash watch.sh)
```

`run_round.sh` does, per language, **fully unattended**: preflight → pull IndicSynth+IndicVoices →
generate Worst-AI (Bhashini) → train `pipeline/train_corpus.py` → `eval_gengap` → keep checkpoint → delete data.
Everything is logged to `~/voxshield/logs/round_<ts>_<langs>.log`.

**Staged data layout (must match `train_corpus.py`):**
```
$DATA/indicsynth/<Capitalized>/train-000NN-of-*.parquet   # fakes  (HF IndicSynth dirs are Capitalized)
$DATA/indicvoices_real/<lower>/train-000NN-of-*.parquet   # genuine (HF IndicVoices dirs are lowercase)
$DATA/worst_ai/manifest.jsonl                             # Bhashini TTS/voice-clone attacks (now ingested)
```
`run_round.sh` builds the exact shard include-patterns (0..`--shards-end`) so only the needed shards download.
The trainer writes `checkpoints/round_<ts>_<lang>/scores.csv` (label,score,generator,language,channel,seen)
which `eval_gengap.py --csv` consumes to report the seen-vs-unseen **generalization gap**.

**Why it survives your laptop:** the job runs on the DGX under tmux (no `nohup`/network dependency after launch);
downloads happen **on the DGX** (it has internet), and servers don't suspend. If `tmux` is missing, `launch_round.sh`
falls back to `nohup … & disown`.

**Resume after a reboot:** checkpoints are per-round in `~/voxshield/checkpoints/round_<ts>/`; re-run with
`--keep-data` to avoid re-pulling, or start the next language.

## 7 · Updated DGX structure
```
~/voxshield/
├── backend/                     # code (all modules + pipeline/train_corpus.py)
├── models/
│   ├── generators/              # IndicF5, Indic-Parler, F5-TTS, XTTS, Sooktam2, Fastspeech2   (fixed, ~20 GB)
│   └── support/                 # IndicConformer-600M, IndicWav2Vec, IndicTrans2, IndicXlit   (fixed, ~5 GB)
├── data/                        # STAGED per round (deleted after)                            (~150 GB)
├── checkpoints/round_<ts>/      # per-round fine-tuned models + scores.csv                     (~1–3 GB each)
├── curated/                     # Golden/Zero-Day/Worst-Human + manifests
├── logs/round_*.log             # every round logged
├── run_round.sh  launch_round.sh  launch_parallel.sh  resume.sh  watch.sh  dashboard.sh
├── sync_generators.sh  dgx_setup_env.sh  voxshield.env.example
├── hf_cache/                    # model cache
└── voxshield_console.html
```

---

## 8 · PARALLEL build across 8× A100 (≈1 day, not a week)
`bash launch_parallel.sh` distributes the 23 languages **round-robin across 8 GPU slots**; each slot runs its
languages **sequentially on its own A100**, all in detached tmux sessions. Wall-clock ≈ ceil(23/8)=3 languages/slot × ~6 h ≈ **~18 h**.

**Safety features (all handled in `run_round.sh`):**
- **distinct GPU per slot** (`CUDA_VISIBLE_DEVICES=$slot`)
- **per-language data dir** (`data/<lang>/`) → no cross-job clashes
- **disk guard**: aborts a round if free < `MIN_FREE` (default 120 GB) → never fills the disk
- **resume markers** (`checkpoints/<lang>.done`) → `bash resume.sh --go` continues only missing languages
- **per-round logs** (`logs/round_<ts>_<lang>.log`) + `watch.sh` / `dashboard.sh`
- **bounded data** (`--shards-end 9`) keeps 8 concurrent languages ≈ ~400–500 GB total

**Commands:**
```bash
cd ~/voxshield && chmod +x *.sh
source dgx_setup_env.sh                  # HF/Bhashini/CA + cache dirs in one shot
bash launch_parallel.sh --smoke          # ~20 min, 1 language, tiny — validate the loop FAST
bash launch_parallel.sh                  # full 23 languages across 8 GPUs, detached
bash dashboard.sh                        # LIVE one-screen view: slots, languages, %, ETA, GPU, disk
bash watch.sh                            # plain status snapshot
bash resume.sh --go                      # continue anything unfinished
```
**`dashboard.sh`** auto-refreshes (default 5 s, `INTERVAL=2` to change); `--once` prints a single frame.
It shows: each GPU slot + the language it is on, per-language progress + overall %, ETA, GPU util/mem/temp,
disk free + `data`/`checkpoints`/`models` sizes, the active log tail, and live process count.
ETA assumes `ROUND_HOURS` per language (default 6; override with `ROUND_HOURS=5 bash dashboard.sh`).
**Waves (sequential, automatic):** slot 0 → hindi, odia, manipuri · slot 1 → bengali, punjabi, konkani · … ; 3 languages per slot → ~18 h total.
