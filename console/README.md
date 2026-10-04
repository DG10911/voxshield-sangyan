# VoxShield — Voice Fraud Intelligence Console

A runnable, desktop-first React / TypeScript product prototype with 17 operational screens, a state-responsive Three.js Vox Orb, explainable evidence views, and deterministic demo journeys. This is a frontend prototype, not a functioning voice-fraud detector.

## Run

Requires Node.js 20.19+ (tested with Node 22.16) and npm.

```sh
npm install
npm run dev
```

Open the local address printed by Vite, usually `http://localhost:5173`. Hash routing works without server rewrite rules.

```sh
npm run build     # TypeScript checks + production bundle in dist/
npm run preview   # Serve the production bundle
npm test          # Domain, benchmark integrity, CSV and API-boundary tests
npm run format    # Format source and tests
```

For a reproducible dependency installation, use `npm ci`. The lockfile is included. The development server uses filesystem polling because native change notifications were unreliable in the authoring workspace. Remove `server.watch` in `vite.config.ts` if native watching works on your machine.

## What is implemented

| Route | Working prototype interactions |
| --- | --- |
| `#/overview` | Orb, supplied benchmark cards, risk curve tooltips, detector contributions, history links |
| `#/analyze` | Drag/drop, file picker, microphone capture, browser-decoded waveform, real local playback, seek/zoom, staged sample analysis, three verdicts, evidence inspectors, transcript, JSON report |
| `#/live` | Deterministic streaming simulation, pause/resume/stop, threshold crossing at 4 seconds, moving decision window, detector inspection |
| `#/calls` | Search, language/verdict/channel/date/confidence/threat/status filters, sorting, pagination, saved view, investigation drawer, review updates, CSV |
| `#/languages` | Language constellation, search, status filter, exact supplied EER pairs, per-language inspector, CSV |
| `#/evidence` | Nine evidence modules, clickable graph and equivalent evidence list, model inspectors |
| `#/registries` | 28 sample generators, search, inspectors, 26 attack modes, 17-dimensional recipe explorer, CSV |
| `#/results` | Supplied generalization sequence, uncertainty notes, illustrative risk curve, abstention control, false-positive progression, CSV |
| `#/threats` | Searchable, pannable, zoomable entity graph; selection, focus, neighbors, feed, candidate family |
| `#/speakers` | Sample enrollment, SAME/DIFFERENT comparison, sample diarization lanes |
| `#/products` | Six interactive product panels; configurable simulated policy outcomes; read-only War Room |
| `#/integrations` | Bhashini service inventory, AIKosh catalog counts, demo sync, architecture inspectors |
| `#/corpus` | Dataset search/license filters, storage view, licensing inspector, CSV |
| `#/training` | Simulated DGX telemetry, training progression, pause/resume, failed-round retry, job inspection |
| `#/ops` | Append-only session event list, search, audit inspection/export, illustrative drift trace |
| `#/deployment` | Four persistent profile preferences, policy/residency/environment settings, locked guardrails, mock keys, reduced motion, developer panel |
| `#/roadmap` | P0–P4 research tracks, priorities, dependencies, targets, inspectors |

Global command palette: **Cmd/Ctrl+K**, arrow keys, Enter, Escape. Navigation shortcuts: **G O**, **G A**, **G L**, **G T**. Notification and analyst menus are functional. Native dialogs trap focus and restore it on close.

## Demonstration journeys

1. Open Analyze Call → choose **SYNTHETIC / Investment voice clone** → Analyze signal. Observe preprocessing, evidence, arbitration, and calibration. Inspect a detector and the transcript. Open related intelligence, then Calls and Ops & Audit to find the session result and its event.
2. Repeat with **ABSTAIN / Degraded ambiguous audio**. The report shows disagreement, poor channel quality, and human-review guidance. HUMAN is also available.
3. Open Live Stream → Start simulation. Confidence stays below the threshold until four seconds, then the timeline flags. Pause/resume and stop/reset work.
4. Search **Hindi model** in the command palette. Inspect Hindi's supplied clean/G.711 EER values, **0.09% / 0.29%**. Continue to Training and Deployment.

## Architecture

```text
src/
  App.tsx                    Application shell, navigation, command palette, lazy routes
  store.tsx                  Session calls/audit + browser preference hook
  types/index.ts             Typed analysis, language, threat, dataset, training, identity contracts
  data/catalog.ts            Navigation, supplied benchmark data, deterministic catalog fixtures
  services/
    api.ts                   Central request client, endpoints, config, typed adapters, exports
    mock.ts                  Deterministic verdicts, evidence, calls, audit, live confidence
    ws.ts                    WebSocket lifecycle and bounded exponential reconnect
  components/
    ui.tsx                   Panels, buttons, tables, dialogs, status chips, details, exports
    charts.tsx               Native SVG charts, waveform decoding/playback, evidence graph
    VoxOrb.tsx               Lazy Three.js scene with CSS fallback and cleanup
    ErrorBoundary.tsx        Recoverable top-level view failure
  features/
    Overview.tsx             Command center
    Analyze.tsx              Intake, staged analysis, verdict, evidence inspector
    Monitoring.tsx           Live stream and call investigation
    Intelligence.tsx         Languages, evidence, registries, results, threats, speakers
    Platform.tsx             Products, integrations, corpus, training, audit, settings, roadmap
  styles.css                 Central semantic tokens, shell, visualizations, responsive/motion rules
```

React Context holds session state, local component state holds inspectors/filters, and `usePreference` persists only non-sensitive UI preferences. The API client does not live inside visual primitives. No global audio persistence, Redux, chart framework, or heavyweight graph engine is required.

Dependencies: React, React DOM, React Router, Lucide, Three.js. Tooling: Vite, TypeScript, React Vite plugin, esbuild, Prettier. The font stack uses Inter from Google Fonts when available and native system fallbacks otherwise; self-host the font for an isolated deployment.

## Data honesty

- The top bar identifies demo/offline/live API connectivity. Screens also identify simulated infrastructure and catalog records. Connecting the analysis API does **not** turn the remaining demo surfaces into live data.
- Uploaded or recorded audio can be decoded and played locally. In demo mode, it is **not classified**. Its selected scenario determines the sample result. Demo transcript and evidence are not derived from that audio.
- The specified values are preserved: seen 1.62%, unseen 15.94%, gap +9.43, false-alarm reduction −91%, ECE .058, Cllr 1.01, AURC .0273, clean/G.711 9.24%/11.41%, and false positives 2.55% → 0.90% → 0.23%.
- +9.43 is a separately supplied metric, **not** 15.94 − 1.62. Its protocol was not provided. The intermediate trajectory values 19.00 and 27.19 have no supplied stage definitions, so the UI does not invent any.
- The source says 23 languages but names 21: 12 metric pairs and 9 pending languages. Two unspecified languages remain explicitly unassigned. Pending values remain null.
- Supplied values are not independently verified. No dataset split, run date, confidence interval, deployment customer, certification, or regulatory approval is invented.
- Fixture generator names, versions, latencies, corpus records, training traces, threat relationships, and audit references are simulated. Registry recipes are illustrative, not model-derived explanations.

## Environment configuration

Copy `.env.example` to `.env.local` and restart Vite when changing it.

```dotenv
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_DEMO_MODE=true
VITE_ENABLE_3D=true
VITE_ENABLE_ADVANCED_MOTION=true
```

`VITE_DEMO_MODE` defaults to true. Only the literal `false` opts into the configured backend. API base defaults to localhost:8000 in development and same origin in a production build. All VITE values are public client configuration: **never put private credentials in them**.

## Live API mode and contract boundaries

Health and Analyze have connected UI flows. Set `VITE_DEMO_MODE=false`; the client checks health, sends audio using multipart field `file`, and validates the normalized analysis response. A failed connection or invalid analysis response switches to **OFFLINE DEMO** with visible feedback and a deterministic scenario result. The banner and API settings provide retry; a successful health check restores API connectivity.

The following centralized adapters exist. Other than health and analysis, these are extension points: the current view models intentionally continue using labeled fixtures until actual server schemas/authentication are agreed and connected.

| Method | Path | Adapter / expected normalized shape |
| --- | --- | --- |
| GET | `/api/health` | `api.health()` → HealthStatus |
| POST | `/api/analyze?bhashini=true` | `api.analyze()` → AnalysisResult; multipart `file` |
| POST | `/api/stream-analyze` | `api.streamWindow()` → AnalysisResult |
| WS | `/api/ws-stream` | StreamConnection; message schema not supplied |
| GET | `/api/audit` | `api.audit()` → AuditEvent[] |
| GET | `/api/threats` | `api.threats()` → Threat[] |
| GET | `/api/intel` | `api.intel()` → nodes/edges |
| POST | `/api/risk/score` | `api.risk()` → ProductRisk |
| GET | `/api/threat/search?q=` | `api.searchThreats()` → Threat[] |
| POST | `/api/gateway/decide` | `api.gateway()` → ProductRisk |
| POST | `/api/consumer/check` | `api.consumer()` → AnalysisResult |
| GET | `/api/deployment/profile` | `api.deployment()` → profile |
| GET | `/api/warroom` | `api.warroom()` → threats, read-only |
| POST | `/api/speaker/verify` | `api.verifySpeaker()` → SpeakerVerification |

These response shapes are frontend integration proposals because the request supplied endpoint paths, not a backend schema. Map real responses in `services/api.ts`; do not silently treat unknown values as validated results. Cross-origin development requires the backend to allow the Vite origin. Configure real authentication, authorization, retention and TLS on the backend before any operational deployment.

### Analysis response example

```json
{
  "id": "VX-8A91F",
  "filename": "call.wav",
  "verdict": "ABSTAIN",
  "confidence": 52.1,
  "language": "Hindi",
  "channel": "G.711 μ-law",
  "duration": 18,
  "timestamp": "2026-10-04T13:42:00Z",
  "detectors": [{"name":"Physics / HPCS","score":45,"weight":19,"detail":"Insufficient quality","version":"server-version"}],
  "reasons": ["LOW_CHANNEL_QUALITY", "MODEL_DISAGREEMENT"],
  "transcript": "Server-provided transcript",
  "source": "live"
}
```

Confidence and detector scores use the **0–100** scale; times use seconds; timestamps use ISO 8601. ABSTAIN is a complete outcome, not an exception.

### WebSocket integration

`StreamConnection` exposes CONNECTING, CONNECTED, RECONNECTING, DISCONNECTED and FAILED. It reconnects with 1/2/4/8/16-second delays, caps retries, accepts text/Blob/ArrayBuffer, and cleans up timers/socket on close. Instantiate with `config.ws + '/api/ws-stream'`, state/message handlers; close it in an effect cleanup. The supplied prompt did not define audio packet framing, session negotiation, or response schema, so the Live page remains an explicit local simulation. Agree those contracts before sending real media.

## Accessibility and motion

Semantic landmarks, input labels, keyboard-operable controls, focus-visible rings, accessible native modal dialogs, Escape handling, a skip link, table headers, textual status labels, live verdict/toast feedback, and non-spatial evidence lists are included. Graph entities have equivalent buttons. Reduced motion respects the OS setting and a persistent Appearance preference; the latter disables CSS motion and orb animation. Color is always accompanied by a text verdict/state. This is an accessibility baseline, not a formal WCAG certification.

## Performance and 3D strategy

Routes are lazy-loaded by feature group. Named icon imports preserve tree shaking. Three.js is an independent dynamic chunk; CSS/SVG handle charts and graph relationships. The orb uses a bounded 450-point cloud, three wire shells, three thin rings, low-power WebGL preference, pixel ratio capped at 1.5, resize observation, hidden-tab render suspension, and explicit geometry/material/renderer disposal. WebGL failure or disabled 3D falls back to CSS. No user audio is stored in localStorage.

The production build has a roughly 304 KB initial JavaScript chunk (~98 KB gzip), plus route/CSS assets. The lazy Three.js chunk is ~696 KB (~179 KB gzip); Vite reports its expected >500 KB chunk warning. The scene is intentionally modest; it is not a GPU benchmark or a full adaptive-quality renderer. FPS depends on device and browser. Reduced-motion mode retains all textual decisions and controls.

## Known prototype limitations

- No real detection, biometric extraction, transcription, model training, provider sync, transaction blocking, or deployment action is performed by demo controls.
- Calls/audit/enrollment are session-only. Refresh resets them. Browser storage retains sidebar, motion, deployment, region, environment, threshold and saved-filter preferences only.
- Model-level evidence and inference metadata are fixtures in demo mode. The browser waveform is real when decoding succeeds; unsupported codecs get a labeled illustrative fallback.
- The WebSocket abstraction is provided but not wired to an unspecified streaming protocol. Remaining typed API adapters need real response mapping and data hooks.
- The demo audit is append-only in the UI but is not cryptographically signed, durable, or tamper-proof. `sim-` references are identifiers.
- No production authentication/authorization, data residency enforcement, secrets management, or compliance claim is included. Mock API key regeneration changes only a local dummy token.
- Optional architecture/model/incident routes beyond the 17 required screens are not added. Architecture is represented within Integrations and Deployment.
- Illustrative risk/drift/training curves are not measured research outputs. The coverage slider explains review volume without inventing recalculated risk.

## Future integration steps

1. Confirm normalized REST and WebSocket schemas, units, calibration semantics, version fields and authentication.
2. Add server-state hooks for the existing typed adapters and replace each fixture view model explicitly.
3. Persist calls and immutable audit events server-side; implement authorization and retention policies.
4. Connect provider-backed ASR and language detection with licensing/provenance metadata.
5. Stream real windowed evidence through the WebSocket adapter; validate reconnect/session recovery.
6. Run accessibility, load, browser/device, security and model calibration reviews with real deployment constraints.

See `QA.md` for the checks performed on this delivery.
