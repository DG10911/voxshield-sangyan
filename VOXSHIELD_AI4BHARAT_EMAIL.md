# AI4Bharat outreach — VoxShield collaboration

**To:** ai4bharat@iitm.ac.in
**Subject:** Student research collaboration — Indic telephony voice-deepfake detection (VoxShield)

---

Dear AI4Bharat team,

I'm Devansh Goenka, a student at SRM Institute of Science and Technology, building
**VoxShield** — a voice-deepfake / AI-clone detector focused on **Indic-language
telephony fraud** (the vishing calls that target Indian bank customers over 8 kHz
G.711 phone lines).

I've built a working system and measured it honestly rather than on in-corpus data:

- A 5-detector ensemble (XLS-R-53 + wav2vec2 + DistilHuBERT + LFCC/CQCC + DSP) with
  learned meta-fusion, open-set abstention (it says "UNKNOWN" instead of guessing),
  and a governed learning pipeline that never auto-blocks a caller.
- On a **leave-one-generator-out** test over 37k clips, the **unseen-generator EER
  was 9.95%** (a +9.95-point generalization gap vs seen data) — i.e. it holds up
  reasonably on generators it was never trained on, which is the hard part.
- On telephony conditions I measured **6.27% EER on real phone audio** and cut
  genuine-speaker false alarms from ~23% to ~3.3% with codec-aware handling.

The gap I keep hitting is **Indic-specific data**: detection coverage for Indian
languages is far behind ASR/TTS coverage, and there's no public Indic *vishing /
telephony* deepfake benchmark yet. Your work — IndicVoices-R, IndicWhisper, Indic-TTS,
and the Bhashini corpus — is the most relevant foundation I've found, and I'd love to:

1. Learn whether I could use Indic speech data (Bhashini / IndicVoices-R) to build a
   consented, telephony-realistic Indic deepfake **detection** benchmark.
2. Explore whether this could fit under Bhashini as a public-good safety tool, or a
   joint publication on Indic telephony deepfake detection.
3. Get your guidance on the right, responsible way to do this.

Happy to share the full technical writeup, code, and measured results. Thank you for
making Indic speech research so open — it's the reason a student can even attempt this.

Warm regards,
Devansh Goenka
SRM Institute of Science and Technology
[email] · [phone] · [GitHub/link]

---

### Notes before sending
- Fill in your email / phone / a link (GitHub repo or a 1-page PDF).
- Every number here is measured and honest — do NOT change 9.95% / 6.27% / 23%→3.3%; don't add the in-corpus ~0% (leakage).
- Keep it short; this version is ~200 words of body — good. Attach the 1-pager if you have one, don't paste more.
- If you want a warmer intro: mention any SRM faculty advisor who can co-sign.
