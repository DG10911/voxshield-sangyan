# VoxShield — VoiceLink Telephony Lab: resources & plan (2026-09-30)

How to get REAL Indian phone-call audio into VoxShield, legally and cheaply, and the
highest-leverage resources for a best-in-class Indic telephony deepfake detector.
Pairs with `backend/voicelink_readiness.py` (the 25-question GO/NO-GO gate).
⚠️ Verify links/pricing/arXiv IDs before relying on them.

## SIP / telephony providers (India) — best for streaming call audio into a detector
| Provider | Media access | Audio | Sandbox | ~₹/min all-in | Verdict |
|---|---|---|---|---|---|
| **Exotel AgentStream** | WebSocket | 16-bit PCM 8kHz mono | yes | ~0.94–1.28 | 🥇 India-native, cheap, no latency surprises |
| **Plivo Audio Streaming** | WebSocket bidi | 8kHz PCM | yes | ~0.94 | 🥇 dev-friendly, <300ms, **Pipecat-native** |
| Twilio Media Streams | WebSocket | abstracted | trial | ~₹1.5 (₹exp) | proven globally, pricey in India |
| Knowlarity | WSS | Opus/G.711 μ&A | ngrok dev | 0.30–1.20 | India-native, thinner docs |
| Telnyx / Vonage / Ozonetel | SIP | varies | varies | — | not India-cost-optimized / no public media API |

**Pick: Exotel or Plivo + Pipecat** — 8kHz/G.711, WebSocket media into Python, cheap.

## India compliance — the lightweight-legal research path (NO DLT needed)
- **Call consented numbers only** (friends/volunteers/own numbers) → DLT registration NOT required.
- **One-party consent + disclosure**: you're a party to the call; disclose upfront ("recorded for academic deepfake-detection research; you may decline"), allow refusal, store encrypted.
- Student pilot: recruit 50–100 consented volunteers, timestamped consent logs, secure storage. ✅ fully compliant.
- Only when scaling to strangers/commercial → DLT (₹5,900–7,500), DND scrubbing, 9am–9pm window, DPDP consent. (Governed by Telegraph Act 1885 + IT Act 2000 + DPDP 2023.)

## Real-call audio capture (into Python, real time)
- **Dev (lowest friction):** Plivo/Exotel + **Pipecat** WebSocket → our `/api/ws-stream`. <300ms.
- **Scale (no lock-in):** **FreeSWITCH `mod_ws_media`** → WebSocket (~100ms), Dockerable.
- **Full control:** Asterisk **AudioSocket** (8kHz 16-bit PCM, 320-byte/20ms frames) or PJSIP.
- **Bridge to WebRTC:** LiveKit SIP bridge (80–150ms).
- Latency budget realistic 200–400ms; guarantee 8kHz G.711 on the trunk, resample with librosa/SoX if needed.

## High-value resources (to reach master-class)
- **🔑 Indic-CodecFake + SATYAM** — largest public NAC-deepfake set across **12 Indic languages**; SATYAM baseline ~98.32%. `helixometry.github.io/IndicFake` (arXiv 2604.19949). **Single highest-leverage resource.**
- **IndieFake** (27 hr, 50 Indian-English speakers) · **VISHGUARD** (3k vishing calls, EN/FR/AR — no Indic yet = gap) · **ASVspoof 5** · **Speech DF Arena** (multi-dataset leaderboard).
- **AI4Bharat** (IIT Madras, ai4bharat@iitm.ac.in) — 15,000 hr Indic speech (Bhashini), IndicWhisper, Indic-TTS; open, responsive → **email for collaboration + Bhashini compute/data**.
- **Govt funding:** India's 13 Responsible AI projects — **IIT Kharagpur** (real-time voice deepfake), **Saakshya** (IIT Jodhpur+Madras). Propose VoxShield as the *telephony-specific Indic* detector. (~₹10–50 lakh grants; slow 2–3 mo cycles.)
- **No Indic vishing/telephony leaderboard exists yet → opportunity to create one.**

## Ranked plan (cheapest-fastest first)
1. **POC (2–4 wks, ~₹500–2,000):** Exotel/Plivo + Pipecat → call 100 consented volunteers → stream into VoxShield `/api/ws-stream`. Legal, cheap, real Indian call audio.
2. **Best-in-class (4–8 wks):** download **Indic-CodecFake**, replicate SATYAM, fine-tune our detector on it + IndieFake; email **AI4Bharat** for partnership + Bhashini data.
3. **Scale:** FreeSWITCH + K8s, multi-provider fallback, no vendor lock-in.
4. **Parallel:** apply to the govt Responsible-AI grant track (IIT Kgp / Saakshya).

## Honest assessment
- Cheapest real-audio POC ≈ ₹500–2,000; legal risk LOW if consented-only.
- Indic vishing corpus is a real GAP → our opening (and a fundable one).
- Reality check: a trained detector catches KNOWN synthesis (codecs) well but lags NOVEL TTS — keep the open-set/abstain discipline (we have it).
- **Single highest-leverage move: Indic-CodecFake + AI4Bharat partnership.**
