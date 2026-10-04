# VoxShield — Full Screen-wise Prototype Specification
The single source of truth for the **voice-fraud intelligence console** frontend.
Hand this to a design engineer (or an AI frontend agent) to build the production UI.
Everything here matches the real backend in `backend/app.py`.

---

## 0 · Product in one line
**VoxShield** detects AI-cloned voices in investment scam calls across Indic languages, on
phone-quality audio, on-prem, and never gives advice. Output is always
**HUMAN · SYNTHETIC · ABSTAIN** with transcript, language and reason codes.

## 1 · Design language (tokens)
**Palette**
| Token | Hex | Use |
|---|---|---|
| `--bg` | `#05070c` | app background |
| `--panel` / `--panel2` | `#0e1420` / `#131b29` | cards |
| `--line` / `--line2` | `#222e44` / `#2c3a55` | borders |
| `--fg` / `--sub` / `--mut` | `#eef3fb` / `#8fa0ba` / `#5f6f88` | text |
| `--red` / `--red2` | `#ff4d6a` / `#ff7a90` | primary accent · SYNTHETIC · danger |
| `--cyan` | `#22d3ee` | info · unseen |
| `--grn` | `#25d07c` | HUMAN · pass |
| `--amb` | `#f6a935` | ABSTAIN · caution |
| `--vio` | `#8b5cff` | secondary/intel |

Semantics: **green = human/safe, red = synthetic/danger, amber = abstain/uncertain, cyan = info/unseen.**
**Type**: system sans (`-apple-system, Inter`), weights 500/700/850/900; meta/data in monospace (`SF Mono, ui-monospace`).
**Scale**: display 34–54 / H1 26 / H2 20 / body 14 / meta 12 / mono-label 11 (letter-spacing .14em, uppercase).
**Spacing**: 4px base → 8/12/16/20/26/34. **Radii**: cards 16, chips 999, inputs 11, buttons 11.
**Elevation**: soft `0 40px 120px rgba(0,0,0,.6)` on hero/film; cards flat with 1px border.
**Motion**: 150ms micro, 350ms view-enter (`translateY(8px)→0`), 900ms count-up, 900ms bar fill; easing `cubic-bezier(.2,.7,.2,1)`; respect `prefers-reduced-motion`.
**Iconography**: minimal glyph set (◈ ⌁ ◉ अ ✷ ⛁ ◱ ⛨ ⇄ ⚙ ◇) or a 1.5px-stroke line set.

## 2 · Global shell
- **Left sidebar (252px)**: brand → grouped nav (Monitor · Intelligence · Platform) → status footer (DGX live, build).
- **Top bar**: breadcrumb · global search (⌘K) · API health pill (● live · N detectors).
- **Content**: max-width 1240, 26px padding, responsive down to 64px rail.
- **Router**: hash or client-side view switch; deep-linkable (`#/languages`).
- **Global states**: loading skeletons, empty states, error toasts, offline demo-mode banner.

## 3 · Component library
`Sidebar` · `TopBar` · `KpiCard` · `Card` · `Table` · `Chip/Badge` · `VerdictCard` ·
`WaveformCanvas` · `RiskCoverageChart` · `BarChart` · `LineChart` · `AreaChart` · `Donut` ·
`Timeline` · `Dropzone` · `Tabs` · `Drawer` · `Modal` · `Toast` · `CommandPalette` ·
`CodeBlock` · `RegistryRow` · `LanguageCell`.

## 4 · Screens

### S1 · Overview / Command Center
- **Purpose**: at-a-glance health + the headline science.
- **Layout**: 4 KPI tiles → 2-up (risk–coverage chart | ensemble list) → 2-up (channel matrix | activity feed).
- **Data**: seen EER 1.62%, unseen 15.94%, gap +9.43, false-alarm −91%, ECE .058, AURC .0273; ensemble per-model scores; recent verdicts.
- **API**: `GET /api/health`.
- **States**: live / offline-demo.

### S2 · Analyze a call
- **Purpose**: upload/record → explainable verdict.
- **Layout**: left = dropzone + waveform + meta chips (language, duration, channel); right = verdict card + per-model bars + reason-code chips.
- **Data**: `{score,label,action,reasons{},per_model{},features{},voxscore}`.
- **API**: `POST /api/analyze` (multipart `file`), `?bhashini=true` optional.
- **States**: idle · analyzing · verdict(high/mid/low) · error.

### S3 · Live stream (time-to-flag)
- **Purpose**: real-time call monitoring.
- **Layout**: 4 stat tiles (time-to-flag 4.0s, window 3.0s, threshold 0.70, latency ~120ms) + scrolling decision timeline bar-chart with a flag marker.
- **API**: `POST /api/stream-analyze`, `WS /api/ws-stream`.

### S4 · Calls / History
- **Purpose**: searchable log of analysed calls.
- **Layout**: filter bar (language, verdict, channel, date, min-score) + table + row → drawer detail (waveform, transcript, reason codes, audit trail).
- **API**: `GET /api/audit` (extend with filters).

### S5 · Language scorecard
- **Purpose**: 23-language coverage & EER.
- **Layout**: scorecard table (language, ISO, clean EER, G.711 EER, bar, status) + grid of script tiles.
- **Data**: pa 0.00/0.05 … ml 37.51/37.81; status validated/partial/pending.
- **States**: validated (green), partial (amber), pending GPU (grey).

### S6 · Evidence brains
- **Purpose**: show the decision machinery.
- **Layout**: 3-col cards; each brain = name, one-line, live signal dot, last contribution.
- **Brains**: Physics(HPCS), Replay, Environment, Cross-codec, Speaker, Semantic↔Prosody, Causal, Temporal-DNA, Arbitration.

### S7 · Registries
- **Purpose**: living catalogues.
- **Layout**: 4 KPIs (generators 28, attacks 26, recipes 17-dim, languages 23) + generators table (seen/unseen + EER) + attack-mode chips.

### S8 · Results / Benchmarks
- **Purpose**: honest, per-slice numbers.
- **Layout**: gap line-chart (1.62 → 19.00 → 27.19 → 15.94) · zero-shot-vs-ours bars · channel matrix · calibration · abstention.
- **Data**: gap +9.43; channel +2.17 pts; ECE .058; Cllr 1.01; FP 2.55→0.23%.

### S9 · Threat intel
- **Purpose**: generators, unknown vault, intel graph.
- **Layout**: threat feed + generator hunter cards + queryable intel graph panel.
- **API**: `GET /api/threats`, `GET /api/intel`, `GET /api/threat/search?q=`.

### S10 · Speaker identity
- **Purpose**: enroll/verify/diarize.
- **Layout**: enroll dropzone → speakerId chip; verify pair → similarity meter (SAME/DIFFERENT); diarization lanes.
- **API**: `POST /api/speaker/verify`.

### S11 · Product surfaces
- **Layout**: 3-col cards: CallGuard, Voice Identity, Transaction Shield, Telephony Gateway, War Room, Consumer.
- **APIs**: `POST /api/risk/score` (CallGuard), `POST /api/gateway/decide`, `POST /api/consumer/check`, `GET /api/warroom`.

### S12 · Integrations
- **Layout**: Bhashini panel (ASR/TTS/ALD/TLD/NMT/stream + quota) · AIKosh catalogue (124 datasets / 94 models) + attribution.
- **API**: `GET /api/health` (bhashini block).

### S13 · Data & corpus
- **Layout**: dataset/model inventory with sizes, licence badges (CC-BY / NC / ND holdlist), pull status, KIOXIA/DGX location.

### S14 · Training rounds (DGX)
- **Layout**: per-language round grid (✅ done / ⬜ pending / ⏳ running), ETA, per-round EER output; GPU util strip.
- **Data**: 15/23 done, 12 two-class validated, low-res pending.

### S15 · Ops & audit
- **Layout**: ECE/Cllr/drift/deployment-profile tiles · append-only audit table · quota.
- **API**: `GET /api/audit`, `GET /api/deployment/profile`.

### S16 · Deployment & settings
- **Layout**: profiles (Cloud / Enterprise / Indic on-prem / Edge), guardrail toggles (read-only policy), API keys (masked), theme, data-residency.

### S17 · Roadmap
- **Layout**: P0–P4 columns + drop-in upgrade chips (XLS-R+SLS · RawBoost · AASIST3 · adversarial · distillation).

## 5 · API contract (real, from `backend/app.py`)
```
GET  /api/health
POST /api/analyze?bhashini=true            (multipart: file)
POST /api/stream-analyze
WS   /api/ws-stream
GET  /api/audit
GET  /api/threats
GET  /api/intel
POST /api/risk/score                        (CallGuard body)
GET  /api/threat/search?q=
POST /api/gateway/decide
POST /api/consumer/check
GET  /api/deployment/profile
GET  /api/warroom
POST /api/speaker/verify
GET  /                                      (dashboard)
```
Base URL: same origin (served by FastAPI) or `http://localhost:8000` (CORS enabled).

## 6 · Guardrails (must show in UI)
No tips/price prediction; privacy-by-design; explicit **ABSTAIN**; read-only War Room;
third-party attribution (Bhashini / AIKosh / HF); IndicSynth = CC-BY-NC (research only).

## 7 · Accessibility
WCAG 2.2 AA: 4.5:1 text contrast, focus-visible rings, keyboard nav for all tables/drawers,
`aria-live` for verdicts, reduced-motion, colour never the sole signal (icon + label).
