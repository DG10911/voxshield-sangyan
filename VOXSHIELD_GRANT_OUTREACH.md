# Govt Responsible-AI outreach — IIT Kharagpur / Saakshya

Outreach to India's deepfake-detection research groups (under the 13 Responsible-AI
projects) to position VoxShield as the **telephony-specific, Indic-language** voice
deepfake detector — a niche none of them cover head-on.

> ⚠️ **Before sending — verify these yourself (the research was a lead-sheet):**
> - Find the actual **PI / lab / email** for each group (search their institute page /
>   the govt Responsible-AI project list). Do NOT send to a guessed address.
> - Confirm the project is active and open to student collaboration.
> - Every metric below is measured & honest — keep 9.95% / 6.27% / 23%→3.3%; never add the in-corpus ~0% (leakage).

---

## TEMPLATE (works for either group — swap the bracketed bits)

**Subject:** Student collaboration — telephony-specific Indic voice-deepfake detection (VoxShield)

Dear [Prof. / Dr. Name],

I'm Devansh Goenka, a student at SRM Institute of Science and Technology. I came across
[your group's work on real-time voice deepfake detection / the Saakshya project on
multi-agent deepfake detection] and wanted to share a system I've built that I think
complements it: **VoxShield**, a voice-deepfake detector aimed specifically at
**Indic-language telephony fraud** — vishing calls over 8 kHz G.711 phone lines.

What I've built and measured (honestly, not on in-corpus data):
- A 5-detector ensemble (XLS-R-53 + wav2vec2 + DistilHuBERT + LFCC/CQCC + DSP) with
  learned meta-fusion, **open-set abstention** (returns UNKNOWN rather than guessing),
  and a governed pipeline that never auto-blocks a caller.
- **Leave-one-generator-out: 9.95% EER on unseen generators** (+9.95-pt generalization
  gap vs seen) — measured over ~37k clips.
- **6.27% EER on real telephony audio**; genuine-speaker false alarms reduced ~23% → ~3.3%
  with codec-aware handling.

The gap I keep hitting — and where I think we could work together — is that there's **no
public Indic telephony / vishing deepfake benchmark**, and detection coverage for Indian
languages lags far behind ASR/TTS. VoxShield is built end-to-end for exactly that niche
(telephony channel + Indic languages + unseen-generator robustness).

Would your group be open to [a short conversation / student collaboration / guidance on
aligning this with the Responsible-AI initiative]? I'd be glad to share the full technical
writeup, code, and measured results, and to contribute VoxShield as a public-good tool.

Thank you for your time and for the work you're doing on this problem.

Warm regards,
Devansh Goenka
SRM Institute of Science and Technology
[email] · [phone] · [GitHub / 1-page PDF link]

---

## Tailoring notes

**IIT Kharagpur (real-time voice deepfake detection):**
- Emphasize the **real-time / telephony** angle — it's their lane. Mention our streaming
  `/api/ws-stream` + cascade (L0–L3) latency design and the <300ms VoiceLink capture path.
- Ask specifically about their real-time evaluation setup and whether Indic telephony is in scope.

**Saakshya (IIT Jodhpur + IIT Madras, multi-agent deepfake detection):**
- Emphasize **evidence arbitration across independent brains** (our HEDS/arbitration is
  literally multi-agent evidence fusion) + the **Indic** angle (IIT Madras ↔ AI4Bharat overlap).
- Natural bridge to the AI4Bharat outreach — mention you're also in touch with them (if true).

## Sending tips
- Send **separately** to each (personalized), not a mass email.
- Attach a **1-page PDF**, don't paste more than the body above.
- If a **SRM faculty advisor** co-signs or is cc'd, it lands much better.
- Lead with what you BUILT + MEASURED (credibility), then the ask. Keep it ~200 words.
