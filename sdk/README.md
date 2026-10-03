# VoxShield SDKs

Thin, dependency-free client libraries over the VoxShield REST/WebSocket API
(`backend/app.py`). Each wraps the same endpoints so integrators don't hand-roll HTTP.

| Language | File | Runtime | Deps |
|---|---|---|---|
| Python | `python/voxshield.py` | 3.8+ | stdlib only (`urllib`) |
| JavaScript | `javascript/voxshield.js` | Node 18+ / browser | none (global `fetch`) |
| Java | `java/VoxShield.java` | JDK 11+ | none (`java.net.http`) |
| Go | `go/voxshield.go` | 1.18+ | stdlib only |

## Endpoints covered
- **Core:** `analyze`, `stream_analyze`, `speaker_verify` (multipart audio upload)
- **Risk/intel:** `risk_score`, `threats`, `threat_search`, `intel`
- **Product surfaces:** `gateway_decide` (never auto-blocks), `consumer_check`, `deployment_profile`, `warroom`

Every `analyze` response includes `voxscore` (meta-uncertainty + abstain) and the P2/P3
`brains` / `arbitration` / `unified_verdict` fields.

## Quick start (Python)
```python
from voxshield import VoxShield
vs = VoxShield("http://localhost:8000")

print(vs.analyze("call.wav"))                       # verdict + voxscore + brains
print(vs.risk_score({"neural:xls-r": 0.92}))        # score raw detector probs
print(vs.gateway_decide(voxscore, context={"high_value_action": True}))
print(vs.intel(language="ta", codec="g711_ulaw"))   # hardest generators under Tamil+G.711
```

## Quick start (Node)
```js
import { VoxShield } from "./voxshield.js";
const vs = new VoxShield("http://localhost:8000");
console.log(await vs.analyze("./call.wav"));
console.log(await vs.threats(5));
```

## Generating from OpenAPI (optional)
FastAPI serves the spec at `/openapi.json`. To regenerate typed clients for any language:
```bash
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g <lang> -o sdk/<lang>-generated
```
These hand-written clients stay small and readable; the generated route is for teams that
want fully-typed models. Both talk to the same API.

## Note
No detector runs client-side — the SDKs only call the server. Verdicts, abstain, and the
"never auto-block" guarantee are enforced server-side (see `backend/`).
