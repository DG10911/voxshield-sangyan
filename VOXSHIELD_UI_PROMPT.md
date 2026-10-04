# VoxShield — Master UI Generation Prompt (for GPT-6 / Astra / any frontend agent)
Copy everything in the fenced block into the model. It produces the full frontend; we then
integrate it against the real API (`backend/app.py`). Pair it with `VOXSHIELD_UI_SPEC.md`.

---

```text
ROLE
You are simultaneously a Principal Product Designer, Staff Frontend Engineer, Design-Systems
Architect, Motion Designer and Data-Visualization expert. You ship a complete, production-grade
web frontend — not a landing page, not disconnected mockups.

PRODUCT
Name: VoxShield.
One line: real-time detection of AI-cloned voices in investment scam calls across Indic
languages, on phone-quality (G.711) audio, on-prem, that never gives investment advice.
Users: fraud/risk analysts at banks, brokers and SEBI helplines; plus a consumer one-tap check.
Core AI capability: a fusion ensemble (acoustic-DSP + 3 neural detectors + LFCC/CQCC fusion head)
that returns HUMAN / SYNTHETIC / ABSTAIN with transcript, detected language and reason codes.
Problem: voice-clone vishing is the fastest-growing investor fraud; existing detectors are
English/wideband and fail on Indic telephony.

DELIVERABLE
One cohesive web app — a "voice-fraud intelligence console" — with ALL of these screens,
sharing one design language:
1 Overview / Command Center  2 Analyze a call  3 Live stream (time-to-flag)  4 Calls/History
5 Language scorecard (23 langs)  6 Evidence brains  7 Registries  8 Results/Benchmarks
9 Threat intel  10 Speaker identity  11 Product surfaces  12 Integrations (Bhashini/AIKosh)
13 Data & corpus  14 Training rounds (DGX)  15 Ops & audit  16 Deployment/Settings  17 Roadmap

STACK
Prefer React + TypeScript + Tailwind (or a single self-contained HTML file if a build step is
undesirable). No design-slop: no purple gradients everywhere, no generic SaaS hero, no stock
photos, no emoji-as-UI. Charts may be Recharts/D3 or hand-drawn SVG/Canvas. Must run offline
with mock data and upgrade to live API when available.

DESIGN TOKENS (use exactly)
bg #05070c · panel #0e1420 / #131b29 · line #222e44 · fg #eef3fb · sub #8fa0ba · mut #5f6f88
accent red #ff4d6a (+#ff7a90) · cyan #22d3ee · green #25d07c · amber #f6a935 · violet #8b5cff
Type: system sans (Inter/-apple-system) weights 500/700/850/900; data/meta in ui-monospace.
Scale display 34–54 · h1 26 · h2 20 · body 14 · meta 12 · mono-label 11 uppercase, tracking .14em.
Spacing 4px base (8/12/16/20/26/34) · radii cards 16 / chips 999 / inputs+buttons 11.
Motion: 150ms micro, 350ms view-enter, 900ms number count-up & bar fill, easing
cubic-bezier(.2,.7,.2,1); honor prefers-reduced-motion.
Semantics: green=human/safe, red=synthetic/danger, amber=abstain/uncertain, cyan=info/unseen.

GLOBAL SHELL
Left sidebar 252px (brand → grouped nav: Monitor / Intelligence / Platform → status footer
"DGX live"), top bar with breadcrumb + global search (⌘K) + API health pill, content max 1240.
Client-side routing, deep-linkable views, loading skeletons, empty states, toasts,
offline-demo banner.

COMPONENT LIBRARY (build all)
Sidebar, TopBar, KpiCard, Card, Table, Chip/Badge, VerdictCard, WaveformCanvas,
RiskCoverageChart, BarChart, LineChart, AreaChart, Donut, Timeline, Dropzone, Tabs, Drawer,
Modal, Toast, CommandPalette, CodeBlock, RegistryRow, LanguageCell.

SCREEN REQUIREMENTS (essentials per screen)
- Overview: 4 KPI tiles (seen EER 1.62%, unseen 15.94%, gap +9.43 pts, false-alarm −91%),
  risk–coverage chart (AURC 0.0273), ensemble list with per-model bars, channel matrix
  (clean 9.24% / G.711 11.41%), live activity feed.
- Analyze: dropzone + waveform + meta chips; verdict card (HUMAN/SYNTHETIC/ABSTAIN) + per-model
  bars + reason-code chips; POST /api/analyze (multipart file).
- Live stream: time-to-flag 4.0s, window 3.0s, threshold 0.70, latency ~120ms; decision timeline
  with a flag marker; WS /api/ws-stream.
- Language scorecard: table of 23 languages with clean and G.711 EER bars + validated/partial/
  pending status (data below).
- Evidence brains: 9 cards (Physics HPCS, Replay, Environment, Cross-codec, Speaker,
  Semantic↔Prosody, Causal, Temporal-DNA, Arbitration).
- Registries: 28 generators (seen/unseen + EER), 26 attack modes, 17-dim recipes, 23 languages.
- Results: generalization-gap line chart, zero-shot-SOTA vs ours bars, channel matrix,
  calibration (ECE .058, Cllr 1.01), abstention (FP 2.55%→0.90%→0.23%).
- Threat intel: threat feed + generator hunter + intel graph (GET /api/threats, /api/intel,
  /api/threat/search?q=).
- Speaker identity: enroll → speakerId, verify pair → SAME/DIFFERENT meter, diarization lanes
  (POST /api/speaker/verify).
- Product surfaces: CallGuard, Voice Identity, Transaction Shield, Telephony Gateway, War Room,
  Consumer (POST /api/risk/score, /api/gateway/decide, /api/consumer/check; GET /api/warroom).
- Integrations: Bhashini services (ASR/TTS/ALD/TLD/NMT/streaming) + quota; AIKosh 124 datasets /
  94 models; attribution.
- Data & corpus: dataset/model inventory with licence badges (CC-BY, NC/ND hold-list), sizes,
  pull status, location (KIOXIA/DGX).
- Training rounds: per-language round grid (done/running/pending), ETA, per-round EER, GPU strip
  (15/23 done; 12 two-class validated).
- Ops & audit: ECE/Cllr/drift/deployment tiles + append-only audit table (GET /api/audit,
  /api/deployment/profile).
- Deployment/Settings: profiles (Cloud/Enterprise/Indic on-prem/Edge), guardrail toggles
  (read-only policy), masked API keys, theme, data residency.
- Roadmap: P0–P4 + drop-in upgrades (XLS-R+SLS, RawBoost, AASIST3, adversarial, distillation).

REAL API (wire to these; mock fallback when offline; base = same origin or http://localhost:8000)
GET /api/health · POST /api/analyze?bhashini=true · POST /api/stream-analyze · WS /api/ws-stream
GET /api/audit · GET /api/threats · GET /api/intel · POST /api/risk/score
GET /api/threat/search?q= · POST /api/gateway/decide · POST /api/consumer/check
GET /api/deployment/profile · GET /api/warroom · POST /api/speaker/verify

MOCK DATA (used when API is down)
Language EER (clean / G.711): Punjabi 0.00/0.05, Telugu 0.00/0.11, Marathi 0.02/0.14,
Sanskrit 0.03/0.15, Hindi 0.09/0.29, Tamil 0.26/2.03, Kannada 0.65/1.62, Gujarati 1.28/6.01,
Bengali 3.30/10.36, Urdu 13.13/22.71, Odia 32.53/35.68, Malayalam 37.51/37.81;
Kashmiri/Santali/Sindhi/Manipuri/Nepali/Bodo/Dogri/Konkani/English pending.
Headline: seen 1.62% · unseen 15.94% (LOGO mean) · gap +9.43 · zero-shot SOTA 33–93%.

GUARDRAILS (must be visible)
No stock tips/price prediction/broker promotion; privacy-by-design; explicit ABSTAIN;
read-only War Room; third-party attribution (Bhashini, AIKosh, HF); IndicSynth CC-BY-NC.

QUALITY BAR
Accessible (WCAG 2.2 AA, focus-visible, keyboard, aria-live, colour-not-sole-signal).
Responsive (rail collapses < 820px). Naming/typing clean. No placeholder lorem. Every screen
functional with mock data. It must feel like a funded security company's real console.

OUTPUT
All source files + a README with run instructions. If single-file, produce index.html
self-contained (no CDN needed) plus a short integration note. Then we wire it to the live API.
```

---

## After generating
Drop the output into `frontend/` (replacing `index.html`) or a new `frontend/app/`, then:
1. point `API` base at same origin (FastAPI serves `frontend/`),
2. map each screen to the endpoints in §5 of the spec,
3. verify with `uvicorn app:app --port 8000` and the DGX results in `VOXSHIELD_RESULTS.md`.
