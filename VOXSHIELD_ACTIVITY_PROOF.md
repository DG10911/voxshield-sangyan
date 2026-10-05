# VoxShield — Activity Proof & Clarification (for the Centre for AI audit)

## 1 · The flagged process (not ours)
| Fact | Evidence |
|---|---|
| Software | `~/bin/cloudflared tunnel --url http://localhost:8090` |
| tmux session | `cftunnel` (created **Fri Sep 11 12:16:39 2026**) |
| Binary install time | `~/bin/cloudflared` → **2026-09-11 12:16:39** |
| What it exposed | a **separate** local app: `~/cpv/bin/python app.py` on `127.0.0.1:8090` |
| Created alongside | session `canonweb` (created Sep 11 12:16:09) — a different project |
| Status | **STOPPED** — `cloudflared` not running; `cftunnel` killed; 8090 local-only |

## 2 · Relationship to the tunnel (accurate)
The tunnel belongs to a **different application stack**, not VoxShield:
| Date | Activity |
|---|---|
| Sep 10 23:09 | `canon` tmux session created |
| **Sep 11 12:16:09** | `canonweb` session created |
| **Sep 11 12:16:39** | `cloudflared` binary installed + `cftunnel` started (→ `localhost:8090`) |
| Sep 15 onward | VoxShield DGX sessions (`vox`, `voxdl`, `trainvox`) |
| Oct 4–5 | All VoxShield work (commits below) |

The `cloudflared` binary and the `~/cpv` app (`python app.py` on `127.0.0.1:8090`) form a
**separate** stack (`canon`/`canonweb`), **not part of the VoxShield codebase**. VoxShield's
scripts contain **zero** tunneling usage.

## 3 · What VoxShield actually does on the DGX (no tunneling)
- **SSH/SCP only** (`ssh dgx`) for code sync and job control.
- Long jobs run in **tmux** (`vox*` sessions) doing: dataset download, TTS fake
  generation, XLS-R/AASIST training, evaluation. **No reverse proxies, no tunnels.**
- Our scripts (grep-checked): `deploy/dgx/*.sh`, `backend/*.py` — none invoke
  `cloudflared`, `ngrok`, `frp`, `localtunnel`, or `ssh -R`.
- The only local server we run is the FastAPI demo (`backend/app.py`) used in **local
  tests on our own laptop**, not exposed.

## 4 · Network facts (as requested)
| Item | Value |
|---|---|
| DGX host | `dgxa100` (**the server — not the user's machine**) |
| **DGX host IP** | **172.16.0.32** (primary), 10.0.0.32, Docker 172.17.0.1, link-local 169.254.0.18 |
| localhost | `127.0.0.1` |
| App that was tunnelled | `127.0.0.1:8090` (app under `~/cpv`, per `ps`) |
| Tunnel exit | Cloudflare edges (e.g. `198.41.192.57`, `maa04`) — **not a project endpoint** |
| The user's client IP | **not recorded** (all connections arrive via `tmux`, so `last -i` shows `0.0.0.0`) |

## 5 · Task log (64 commits, all VoxShield)
```
2026-09-15  multi-dataset trainer + run_everything orchestration (start of VoxShield)
2026-09-15  parquet-native multi-cloner corpus trainer (cross-generator + per-language EER)
2026-09-15  fixes: parquet decode, gradient-checkpointing, feature-encoder unfreeze
2026-10-04  Sangyan submission (deck, demo video, code, docs)
2026-10-05  Codex 17-screen console + spectrograms + QA
2026-10-05  Indic-Parler tokenizer fix; low-res real-TTS; Bhashini 11/13 live
2026-10-05  language orthogonalization; orth probe (C5); EER-improvement pass
2026-10-05  58-resource downloader; all-28 generator adapters; Kaggle + AIKosh wired
2026-10-05  all-detector ensemble + calibration; VoxShield vs existing systems
```
Full history: `git log` in `github.com/DG10911/voxshield-sangyan`.

## 6 · Remediation completed (all verified)
| Step | Status |
|---|---|
| `cloudflared` process terminated | ✅ not running |
| `cftunnel` tmux session killed | ✅ gone |
| **`~/bin/cloudflared` binary deleted** | ✅ `~/bin/` now empty |
| **`~/.cloudflared` config removed** | ✅ gone |
| **`~/cpv` app stopped** | ✅ process gone |
| **`0.0.0.0:8090` listener** | ✅ **NOT listening** (no public exposure) |
| Tunneling binary sweep (cloudflared/ngrok/frpc/lt) | ✅ none found |
| VoxShield tmux sessions intact | ✅ 9 `vox*` sessions running normally |
