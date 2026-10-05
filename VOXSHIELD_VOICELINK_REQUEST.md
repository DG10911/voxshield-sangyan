# VoxShield — What to request from VoiceLink (voicelink.co.in)

**Goal:** stream real Indian **phone-call audio** (8 kHz, G.711 µ-law/A-law) in real time into
VoxShield's `/api/ws-stream` for a legal, low-cost telephony POC (100 consented calls).
Everything below is what to ask VoiceLink to provide; item 1–3 unblock the POC, 4–9 make it usable.

## 1 · Telephony access
- **SIP trunk + at least one India DID** (local number) — inbound + outbound.
- **India-native termination** (low jitter, no international routing hairpin).

## 2 · Real-time media streaming (the critical piece)
- **Bidirectional WebSocket media**, delivering **raw PCM: 16-bit, 8 kHz, mono, 20 ms frames**
  (G.711 µ-law/A-law on the trunk, decoded before the socket).
- Ability to **fork the live stream to our URL** while the call continues (no bridge rewrite).
- **Latency target < 300 ms** end-to-end into Python.

## 3 · Sandbox + call control
- **Sandbox account + test DID** and sandbox credits.
- **Call-control API** (make/receive/answer/transfer/hangup) with a Python SDK or clear REST.
- **Call recording access** (WAV/MP3) for offline labels.

## 4 · Codec & channel fidelity (for honest G.711 experiments)
- Guarantee the trunk carries **G.711 µ-law/A-law** (or expose the exact codec), so we can measure
  clean vs narrowband detection rather than an unknown transcode.
- Optionally a switch to **G.722 / wideband** for comparison.

## 5 · Consent & compliance (research, no DLT needed)
- Support calling **consented numbers only** (our own + volunteers) — **no DLT required** in that mode.
- **Disclosure + opt-out** on connect ("recorded for academic deepfake-detection research; you may
  decline") — provide a way to play a pre-roll prompt.
- Confirm what compliance data you retain: **DLT status**, DND scrubbing, call-time windows, DPDP.

## 6 · Volume, budget, billing
- Target **~100 calls, 2–4 weeks**, budget **~₹500–2,000** all-in (~₹0.94–1.28/min).
- Per-minute pricing table, quota, and overage policy.

## 7 · Engineering support
- Working **sample code** (WebSocket media → Python) and a reference for **Pipecat / FreeSWITCH
  `mod_ws_media` / Asterisk AudioSocket** compatibility.
- A named contact for latency/codec debugging.

## 8 · Optional (nice to have)
- **Outbound campaign** mode (dial a consented list) and **concurrent-call** limits.
- Multi-region failover and a **no-vendor-lock-in** export of numbers.

## 9 · Fallbacks to compare (if VoiceLink can't cover something)
- **Exotel AgentStream** or **Plivo Audio Streaming** (WebSocket, 8 kHz PCM, Pipecat-native,
  ~₹0.94–1.28/min, sandbox) — the doc's top two picks.
- **Self-hosted** FreeSWITCH / Asterisk for full control, no lock-in.

**One-line ask:** *India DID(s) + bidirectional 8 kHz G.711 WebSocket media (raw PCM, <300 ms) +
sandbox + consented-calling mode, ~100 calls, ~₹500–2,000.*
