# VoxShield — Vast.ai GPU Rental Runbook (2026-09-30)

For training XLS-R-300M + RawBoost, running local TTS/clone generators, and batch scoring —
when the SRM DGX is locked out by campus network/allocation.

## GPU pick
| Pick | GPU | VRAM | ~$/hr (interruptible / on-demand) | Why |
|---|---|---|---|---|
| **Primary** | **RTX 4090** | 24 GB | $0.15–0.25 / $0.30–0.50 | XLS-R fine-tune (batch 8–12) + one TTS model concurrently; best price/perf |
| **Budget/alt** | **A100 40 GB PCIe** | 40 GB | $0.15–0.26 / $0.29–0.52 | Cheap on Vast; better memory bandwidth (1.55 TB/s) for long audio |
| Headroom | A6000 | 48 GB | $0.25–0.40 / $0.50–0.80 | Run multiple TTS models in parallel / bigger batches |
| ❌ Skip | H100 | 80 GB | $1–4 | 8–10× cost, not justified for a 300M fine-tune |

**Decision:** start on **RTX 4090 interruptible** (~$0.20/hr); upgrade to A6000 only if you hit OOM or need parallel TTS jobs.

## Cost for a realistic run (~36–52 GPU-hrs)
| Stage | ~hrs | Cost @ $0.20/hr |
|---|---|---|
| XLS-R fine-tune (10 epochs, batch 8) | 30–40 | $6–8 |
| TTS synthesis (10K clips) | 4–8 | $0.80–1.60 |
| Batch scoring / EER | 2–4 | $0.40–0.80 |
| **Total** | | **~$7–10** · monthly ~100 hrs ≈ $20–25 |

Save 50%+ with **interruptible** — checkpoint every 30–60 min (tmux) and resume on reclaim.

## Setup (fresh instance)
1. **Account:** cloud.vast.ai → add credit (card/crypto) → add SSH key (`ssh-keygen -t ed25519 -f ~/.ssh/vast_ai_key`).
2. **Rent:** Browse → filter RTX 4090, **min VRAM 24 GB, min disk 100 GB, download ≥100 Mbps, reliability >99%** → pick **PyTorch template** → Rent.
3. **Connect:** `ssh root@<ip> -p <port> -i ~/.ssh/vast_ai_key` → `nvidia-smi` to confirm.
4. **Env:** `python -m venv venv && source venv/bin/activate && pip install torch torchaudio transformers datasets librosa scikit-learn`; RawBoost from `github.com/TakHemlata/RawBoost-antispoofing`; TTS: `pip install TTS f5-tts`.
5. **Data:** pull PUBLIC/SYNTHETIC only (see security) into `/workspace/data` via `wget`/`git`.
6. **Train in tmux** (survives disconnect): `tmux new -s train` → run fine-tune → `Ctrl-B D` to detach → `tmux attach -t train` to check.
7. **Save:** copy checkpoints to a persistent volume or `scp` results back before **Destroy** (not just Stop).
   - **Stop** = pause billing, keep disk. **Destroy** = wipe everything.

## ⚠️ Data security (VoxShield handles consented voice — this is mandatory)
- **Never upload real/consented human audio** to a rented, shared host. Use only **synthetic + public** data there (IndicSynth, MLAAD, our generated attack clips, VoxCeleb/CommonVoice).
- Keep real Indic recordings on the **SRM DGX / local** only.
- If you ever must upload sensitive data: `gpg --symmetric --cipher-algo AES256`, decrypt in-instance, delete after, **Destroy** the instance.
- Stream logs to wandb (off-host); sign checkpoints.

## Vast vs SRM DGX A100 — honest
- **Vast wins:** always-available, full root, no campus firewall/allocation lockouts (your actual blocker), trivial parallelism, ~$7–10 per prototype run.
- **DGX wins:** free, more capable for big (>500 hr) jobs, local fast data, IT/compliance support.
- **Recommended hybrid:** prototype + iterate on Vast with synthetic/public data → run the final large-scale train on DGX when you can get in (fall back to Vast reserved if locked out) → batch inference/eval on Vast so it doesn't tie up the DGX.
- **Alternatives:** RunPod (99% SLA, ~$0.34–0.69/hr 4090), Lambda (enterprise, H100), Colab Pro+ ($50/mo, session limits).

Sources: vast.ai/pricing · docs.vast.ai · HF "fine-tune-xlsr-wav2vec2" · RawBoost (arXiv 2111.04433). Verify live $/hr at rent time — rates fluctuate hourly.
