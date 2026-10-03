# VoxShield — Threat & Detection Intel (2026-09-30)

Voice-agent / realtime-clone attack landscape + latest detection research, to drive our
Attack Mode/Recipe registries and detector roadmap. ⚠️ Lead-sheet — verify arXiv links +
specific product claims (latency/pricing/model-names) before citing.

## Realtime voice-AGENT frameworks to SIMULATE as attacks (§5/§6)
| Framework | Latency | Local? | Threat | Simulate? |
|---|---|---|---|---|
| **OpenAI Realtime** | ~150–300ms | API | CRITICAL (reasoning-grade, no STT/LLM seam) | yes (primary) |
| **Vapi / Retell** | ~400–500ms | API | CRITICAL (phone# in minutes, zero ops) | yes (primary) |
| **LiveKit Agents** | ~300–600ms | **self-host** | HIGH (no audit trail, cheap at scale) | yes |
| **Pipecat** | ~300–700ms | **self-host** | MODERATE (frame-level control, SIP spoof) | yes |
| **Ultravox** | faster (speech-native) | API | EMERGING (no transcript seam) | watch |

## Realtime voice CONVERSION / cloning — the live weapon
| Tool | Latency | Local VRAM | Threat |
|---|---|---|---|
| **RVC** (retrieval VC) | **<50ms CPU** | 2 GB / CPU | CRITICAL — attacker default, offline, no telemetry |
| **Seed-VC** | ~400ms | 6–12 GB | VERY HIGH — 3–5s reference, zero-shot, singing |
| **XTTS-v2 streaming** | 150–200ms | 4–6 GB | HIGH — Indic-capable, edge-deployable |
| **IndicF5 / Gnani Vachana** | 200–400ms | 6–8 GB / API | CRITICAL for India — native Indic clone |

→ **Add to Attack Mode/Recipe registries:** realtime-VC (RVC/Seed-VC), agent-driven vishing (OpenAI-Realtime/Vapi), Indic cross-lingual clone, all × G.711 telephony render.

## Latest DETECTION research & datasets (2025–2026)
- **RTCFake** (600 hrs through Zoom/Teams/Discord codecs; Phoneme-guided Consistency Learning) — **the most relevant public set for us**: models trained offline score ~95% but **<55% on live RTC**. HF: `JunXueTech/RTCFake`. Pull via `corpus_ingest.py`.
- **ASVspoof 5** (2025, 1M+ utts) — new gold standard; detectors trained on ASVspoof21 fail on it → confirms generalization is THE problem.
- **AASIST3** (KAN-enhanced) + **Wavelet-prompt-tuned XLSR-AASIST** — ~2.84% EER LA single-model; **XLS-R-300M + AASIST = de facto baseline** (matches our earlier scan's #1 rec).
- **Indic-CodecFake / SATYAM** — neural-codec deepfakes in Indic; the Indic detection gap, again.
- **Adversarial**: FGSM/PGD/C&W fool clean-trained detectors → adversarial training + ensemble + input preprocessing needed. No single detector is bulletproof.
- **Liveness / challenge-response (PITCH)**: mid-call random challenges catch ~95% of current TTS (attackers can fine-tune around it → arms race). Fraunhofer SIT real-time local warning system (2026).
- **Startups to track**: isVerified (continuous liveness), Aurigin.ai (anti-spoof API), Sumsub (self-learning). Labs: Fraunhofer SIT, ASVspoof organizers (Evans/Yamagishi).

## Concrete actions for VoxShield
1. **Add RTCFake to the eval + training mix** — it's our real threat surface (codec-compressed RTC). Highest-value new dataset.
2. **Add attack modes:** realtime-VC (RVC/Seed-VC), agent-vishing (OpenAI-Realtime/Vapi), Indic cross-lingual clone — all through `scenario_render` G.711.
3. **SASV (spoofing-aware speaker verification):** pair detection + speaker verify (our `voice_identity.py` already does clone→REJECT_SPOOF) — high-confidence when identity mismatch AND synthetic.
4. **Streaming/frame detection** (flag if synthetic ≥2 consecutive frames) — our `/api/ws-stream` + cascade already scaffold this; validate latency budget (<100ms/frame at 8kHz).
5. **Challenge-response** as a step-up when confidence is moderate — fits our gateway's `step_up_verification` action.

## Honest hype filter
- ❌ "99% accuracy" = clean audio only; real telephony ~50–70%. ❌ single-model SOTA generalizes poorly. ❌ watermark-detection assumes you control the TTS (you don't).
- ✅ Real: codec compression is the attacker's friend (EER +25–40%); Vapi+RVC = fastest attack path; **Indic detection has no mature benchmark = our opening**; reasoning-grade agents sustain multi-turn vishing.
