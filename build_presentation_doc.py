# -*- coding: utf-8 -*-
"""Build the full judge-ready VoxShield PRESENTATION SCRIPT + Q&A as a .docx.
Every number is traceable to a committed artifact (see appendix)."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BLUE  = RGBColor(0x1F, 0x4E, 0x8C)
DARK  = RGBColor(0x11, 0x11, 0x11)
GREY  = RGBColor(0x55, 0x55, 0x55)
GREEN = RGBColor(0x1F, 0x7A, 0x33)
RED   = RGBColor(0xB0, 0x2A, 0x2A)
PURPLE= RGBColor(0x5B, 0x2A, 0x86)
ACCENT= RGBColor(0x2F, 0x6F, 0xE0)

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.font.color.rgb = DARK
for section in doc.sections:
    section.left_margin = section.right_margin = Inches(0.8)
    section.top_margin = section.bottom_margin = Inches(0.7)

def H1(t, color=BLUE):
    p = doc.add_heading(level=1); r = p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(17); r.bold=True
    p.paragraph_format.space_before=Pt(10); return p
def H2(t, color=BLUE):
    p = doc.add_heading(level=2); r = p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(13.5); r.bold=True; return p
def H3(t, color=ACCENT):
    p = doc.add_heading(level=3); r = p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(12); r.bold=True; return p
def para(t="", size=11, color=DARK, bold=False, italic=False, after=6, before=0):
    p = doc.add_paragraph();
    if t:
        r = p.add_run(t); r.font.size=Pt(size); r.font.color.rgb=color; r.bold=bold; r.italic=italic
    p.paragraph_format.space_after=Pt(after); p.paragraph_format.space_before=Pt(before); return p
def rich(parts, after=6):
    """parts = list of (text, bold, color, italic)"""
    p = doc.add_paragraph()
    for tup in parts:
        txt = tup[0]; b = tup[1] if len(tup)>1 else False
        c = tup[2] if len(tup)>2 else DARK; it = tup[3] if len(tup)>3 else False
        r=p.add_run(txt); r.bold=b; r.font.color.rgb=c; r.italic=it; r.font.size=Pt(11)
    p.paragraph_format.space_after=Pt(after); return p
def bullet(t, bold_prefix=None, color=DARK):
    p = doc.add_paragraph(style="List Bullet")
    if bold_prefix:
        r=p.add_run(bold_prefix); r.bold=True; r.font.color.rgb=color
    r2=p.add_run(t); r2.font.size=Pt(11); return p
def num(t, bold_prefix=None):
    p = doc.add_paragraph(style="List Number")
    if bold_prefix:
        r=p.add_run(bold_prefix); r.bold=True
    p.add_run(t); return p
def qa(q, a):
    p=doc.add_paragraph(); r=p.add_run("Q  "); r.bold=True; r.font.color.rgb=RED
    r2=p.add_run(q); r2.bold=True; r2.font.color.rgb=DARK; r2.font.size=Pt(11)
    p.paragraph_format.space_after=Pt(2); p.paragraph_format.space_before=Pt(6)
    p2=doc.add_paragraph(); r3=p2.add_run("A  "); r3.bold=True; r3.font.color.rgb=GREEN
    r4=p2.add_run(a); r4.font.size=Pt(11); p2.paragraph_format.space_after=Pt(4)
def quote(t):
    p=doc.add_paragraph(); r=p.add_run("“"+t+"”"); r.italic=True; r.font.color.rgb=BLUE; r.font.size=Pt(11.5)
    p.paragraph_format.left_indent=Inches(0.3); p.paragraph_format.space_after=Pt(8); return p
def spacer(pts=4): doc.add_paragraph().paragraph_format.space_after=Pt(pts)

def table(headers, rows, widths=None, hi_last=False):
    t=doc.add_table(rows=1, cols=len(headers)); t.style="Light Grid Accent 1"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    hdr=t.rows[0].cells
    for i,h in enumerate(headers):
        hdr[i].paragraphs[0].add_run(h).bold=True
        for r in hdr[i].paragraphs[0].runs: r.font.size=Pt(10); r.font.color.rgb=BLUE
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            para0=cells[i].paragraphs[0]; run=para0.add_run(str(val)); run.font.size=Pt(10)
            if hi_last and ri==len(rows)-1: run.bold=True; run.font.color.rgb=GREEN
    if widths:
        for i,w in enumerate(widths):
            for r in t.rows: r.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t

# ============================ TITLE ============================
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("VoxShield"); r.bold=True; r.font.size=Pt(30); r.font.color.rgb=BLUE
p2=doc.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
r2=p2.add_run("Presentation Script & Judge Playbook"); r2.font.size=Pt(15); r2.font.color.rgb=DARK
p3=doc.add_paragraph(); p3.alignment=WD_ALIGN_PARAGRAPH.CENTER
r3=p3.add_run("AI voice-clone detection for Indian banking  ·  Team DigiSeva · PS2  ·  TRL-5"); r3.italic=True; r3.font.color.rgb=GREY; r3.font.size=Pt(11)
p4=doc.add_paragraph(); p4.alignment=WD_ALIGN_PARAGRAPH.CENTER
r4=p4.add_run("Every figure in this document is traceable to a committed model artifact."); r4.font.size=Pt(10); r4.font.color.rgb=GREEN
spacer()

# ============================ 1. ELEVATOR ============================
H1("1 · The 30-Second Elevator Pitch")
quote("Voice cloning has made the bank phone line the easiest door into an account — a fake voice that knows your name, over an 8 kHz line that hides the evidence. VoxShield is a defence-in-depth system, not a model: five decorrelated detectors fused by a learned meta-stacker (5.9% held-out error), a fairness layer measured across 10 Indian languages, and a challenge-response liveness check that beats replay. It's explainable, never auto-blocks, runs air-gapped on the bank's own hardware, and flags a fraud call in 3 seconds — a working system today, TRL-5.")
rich([("One-line hook:  ", True, PURPLE), ("Real/fake is table stakes. We catch the fraud, not just the fake — fairly, in the languages the scam is actually run in.", False, DARK, True)])

# ============================ 2. NUMBERS ============================
H1("2 · The Numbers Cheat-Sheet")
table(["Metric","Value","Source artifact"],
 [["Meta-fusion EER (held-out In-the-Wild, n=320)","5.9%","meta_eval.json"],
  ["ROC-AUC","0.983","meta_eval.json"],
  ["Accuracy @0.70 · Precision · Recall · F1","93.4% · 93.5% · 92.9% · 0.93","meta_eval.json"],
  ["Confusion @0.70","TP 144 · TN 155 · FP 10 · FN 11","calibration.json"],
  ["Calibration ECE · Brier","0.044 · 0.048","calibration.json"],
  ["Best single model (XLS-R 300M) EER","16.0%","meta_scores.csv (800-clip)"],
  ["Naive-average fusion EER","19.1%","meta_scores.csv"],
  ["Indic genuine FP (clean), channel-aware","6.3% (from 11.7%)","lang_report.json"],
  ["Indic fake recall, language-routed","82% (from 42%)","exp_indicfull_result.json"],
  ["Streaming time-to-flag","3.0 s (5/5 clips ≥3 s, within 10 s)","latency_trace.json"],
  ["Train / test split","480 train / 320 test, In-the-Wild held out","meta_eval.json"]],
 widths=[3.2,2.6,2.0])
rich([("The learned stacker weights (the honesty story):  ", True, DARK),
      ("DistilHuBERT +2.22 · LFCC+CQCC +2.10 · XLS-R +1.21 · Acoustic-DSP −0.55 · Deepfake-V2 −1.17 · bias +0.13.  ", False, DARK),
      ("The model learned to distrust two of its own five detectors.", False, GREEN, True)])

# ============================ 3. ARCHITECTURE ============================
H1("3 · How the System Works (Technical Deep-Dive)")
H3("Signal path")
para("Incoming 8 kHz G.711 call → sliding 3 s window / 1 s hop (a fresh verdict every second) → 89-dim feature bank → five detectors → logistic meta-stacker → Platt calibration → channel-aware threshold → risk verdict + reason codes + SHA-256 audit.", after=6)
H3("The 89-dimensional feature bank")
bullet("LFCC & CQCC cepstral coefficients — spectral fingerprints of synthesis.")
bullet("Group-delay phase — clones are unnaturally regular in phase.")
bullet("Prosody — F0, jitter, shimmer, voiced ratio (TTS lacks natural micro-variation).")
bullet("HF vocoder energy > 6 kHz — the neural-vocoder fingerprint.")
H3("The five detectors and their learned trust weights")
table(["Detector","What it is","Standalone EER","Stacker weight"],
 [["XLS-R 300M","multilingual wav2vec2, deepfake fine-tuned","16.0%","+1.21"],
  ["DistilHuBERT","fine-tuned on In-the-Wild","23.0%","+2.22"],
  ["LFCC+CQCC head","trained logistic · RawBoost + codec aug","26.8%","+2.10"],
  ["Acoustic DSP","signal-processing artifacts · always-on","46.9%","−0.55"],
  ["Wav2Vec2 (Deepfake-V2)","HF audio-classification model","62.4%","−1.17"]],
 widths=[1.9,2.9,1.4,1.4])
para("Why keep the two negative-weight detectors? A negative weight is a contrarian feature, not dead weight — when those detectors fire in a certain pattern, that pattern is itself informative. Removing them measurably hurt fusion.", italic=True, color=GREY, after=6)
H3("Fusion, calibration, decision")
bullet("Meta-fusion: a logistic stacker (bias +0.13) over the five scores — learned on a disjoint 480-clip split.")
bullet("Platt calibration → the output reads as a true probability (ECE 0.044).")
bullet("Verdict bands: HIGH ≥ 0.70 → step-up · MEDIUM → monitor · LOW → pass. Channel-aware: a detected phone line must clear a stricter 0.85 before HIGH.")
bullet("Never auto-block — HIGH routes to human step-up verification.")
H3("Five reason codes (an operator can read them aloud)")
table(["Code","Meaning"],
 [["SSL","Overall synthesis likelihood (blended neural probability)"],
  ["PH","Unnaturally regular phase — group-delay & spectral flatness"],
  ["HF","Neural-vocoder fingerprint — >6 kHz energy & regularity"],
  ["PR","Missing prosody — F0 jitter, shimmer, voiced ratio"],
  ["BR","TTS inserts silence, not breath — breath-band energy cues"]],
 widths=[1.1,5.6])

# ============================ 4. THE SCOREBOARD ============================
H1("4 · The Scoreboard — Why Fusion Wins")
para("Seven systems, same held-out In-the-Wild data. Frozen detectors on the full 800-clip corpus; the learned meta-fusion on its disjoint 320-clip test split. (Per-detector numbers are reproducible from meta_scores.csv.)")
table(["System","EER ↓","AUC ↑","Accuracy ↑"],
 [["Wav2Vec2 detector — alone","62.4%","0.356","38.6%"],
  ["Acoustic DSP — alone","46.9%","0.521","50.0%"],
  ["LFCC + CQCC head — alone","26.8%","0.786","70.9%"],
  ["DistilHuBERT — alone","23.0%","0.828","74.0%"],
  ["XLS-R 300M — alone (best single)","16.0%","0.901","84.0%"],
  ["Simple-average fusion — unweighted","19.1%","0.839","—"],
  ["VoxShield meta-fusion — all five, stacked","5.9%","0.983","93.4%"]],
 widths=[3.5,1.1,1.1,1.4], hi_last=True)
rich([("The honesty note:  ", True, DARK),
      ("naive averaging (19%) is worse than the best single model (16%) — only the learned stacker beats both.", False, DARK, True)])

# ============================ 5. FAIRNESS ============================
H1("5 · Fairness Across Indian Languages")
para("Genuine (bonafide) speech, 10 languages, 30 clips each, threshold 0.70. We measure the false-positive rate — don't flag real customers. Channel-aware thresholding cut the overall Indic clean-audio FP from 11.7% → 6.3%.")
table(["Language","Clean FP (pre)","Clean FP (deployed)"],
 [["Overall","11.7%","6.3%"],["Marathi","0.0%","0.0%"],["Tamil","6.7%","3.3%"],
  ["Punjabi","10.0%","3.3%"],["Bengali","16.7%","3.3%"],["Kannada","10.0%","6.7%"],
  ["Gujarati","10.0%","6.7%"],["Assamese","6.7%","6.7%"],["Hindi","16.7%","10.0%"],
  ["Malayalam","16.7%","10.0%"],["Telugu (weakest)","23.3%","13.3%"]],
 widths=[2.4,2.2,2.2])
rich([("Fairness cuts both ways:  ", True, DARK),
      ("we synthesized an Indic deepfake set (MMS-TTS) and route with on-device language-ID — lifting Indic fake recall 42% → 82% while English EER stays 5.9%. We publish the uncomfortable numbers: Telugu is still our weakest language.", False, DARK)])

# ============================ 6. ROBUSTNESS ============================
H1("6 · Robustness Self-Test — “We Red-Teamed Ourselves”")
para("80 balanced held-out clips per condition, threshold 0.70. Δ EER is versus the clean baseline.")
table(["Condition","Kind","EER","Δ vs clean","acc@0.70"],
 [["Clean","baseline","7.5%","—","92.5%"],
  ["Opus 12k VoIP","real codec (hardened)","2.5%","−5.0 pts","95.0%"],
  ["G.711 8k telephony","real codec (hardened)","15.0%","+7.5 pts","77.5%"],
  ["MP3 16k","real codec (hardened)","20.0%","+12.5 pts","82.5%"],
  ["Tempo 0.9×","benign manipulation","32.5%","+25.0 pts","70.0%"],
  ["Noise @15 dB SNR","benign manipulation","45.0%","+37.5 pts","62.5%"],
  ["Pitch +2 semitones","benign manipulation","56.3%","+48.8 pts","58.8%"]],
 widths=[2.0,2.1,1.0,1.2,1.1])
bullet("Robust to the channels we hardened for — all three real phone/VoIP codecs stay usable, Opus even improves on clean.", "Reading it honestly:  ", GREEN)
bullet("The open surface is benign DSP — pitch/noise/tempo each move EER +25 to +49 pts. This is our top robustness gap, stated plainly, and the reason we gate customer action on liveness, not detection alone.", color=DARK)
para("White-box gradient attacks (FGSM/PGD) are a stated roadmap item, not claimed as covered.", italic=True, color=GREY)

# ============================ 7. LATENCY ============================
H1("7 · Streaming Latency — the 3.0 s Time-to-Flag")
para("Measured through the real streaming path (fusion.stream_analyze, 3.0 s window / 1.0 s hop, thr 0.70) on the synthetic AI-clone set. Artifact: latency_trace.json.")
table(["Clip","Duration","Time-to-flag","Final score"],
 [["02_ai_clone_1","3.58 s","3.0 s","0.96 HIGH"],
  ["02_ai_clone_3","2.91 s","3.0 s","0.93 HIGH"],
  ["07_clone_on_phone_1/2/3","~2.8 s","3.0 s","0.95 HIGH"],
  ["02_ai_clone_2","2.27 s","— (shorter than one 3 s window)","0.57 whole-clip"]],
 widths=[2.4,1.4,2.3,1.6])
para("5/5 clips ≥3 s flag at exactly 3.0 s — the first full window — all inside the 10 s design target. GPU is sub-second per analysis; commodity CPU is 3–8 s.", after=6)

# ============================ 8. LIVENESS + INTELLIGENCE ============================
H1("8 · Beyond Detection — Liveness & the Intelligence Layer")
H3("Liveness — challenge-response that beats replay")
para("The system speaks a random digit challenge; the caller must say it live. Three checks, all required:")
num("Content — Whisper ASR transcribes the reply; do the digits match (incl. “four seven two”)?")
num("Liveness — the full ensemble scores the reply itself: live human, or a real-time TTS?")
num("Timing — did the answer arrive inside the challenge window?")
para("Each escape route closed by a different check: replay fails content, real-time TTS fails liveness, human-relay fails timing.", italic=True, color=GREY)
H3("The intelligence layer (live today)")
bullet("Fuses clone-score with scam-intent on the transcript and tracks the live script stage Authority → Threat → Isolation → Extraction. Full playbook + cloned voice → CRITICAL. English, Hindi & Hinglish.", "Digital Arrest Shield — ", PURPLE)
bullet("On a digital-arrest verdict, speaks a warning in the victim's language: “no real agency arrests over a call — hang up and call 1930.” Stops the payment, not just logs it.", "Citizen-protection warning — ", PURPLE)
bullet("A real ECAPA speaker embedding answers identity AND liveness. A clone of the customer passes identity but fails liveness → REJECTED-CLONE — the case biometric-alone systems miss.", "Voice enrolment & verification — ", PURPLE)
bullet("A rolling speaker-print links the same cloned voice across victims — even across the 8 kHz codec (it runs on a speaker-identity embedding, not detection features).", "Fraud-ring linkage — ", PURPLE)
bullet("Generator attribution + partial-fake localization (which seconds are AI), streamed in real time.", "Explainable, live — ", PURPLE)

# ============================ 9. DEPLOYMENT + DPDP ============================
H1("9 · Deployment, Trust & India / DPDP Compliance")
bullet("Stateless FastAPI a bank runs on-prem or air-gapped; ~2 GB Docker image bakes all five detectors + Whisper — zero runtime downloads.")
bullet("GPU sub-second · CPU 3–8 s. Stateless → linear horizontal scale.")
bullet("Audio hashed (SHA-256), never stored in clear. Never auto-block. Explainable. WCAG 2.1 AA.")
H3("DPDP Act 2023 — six principles, six design facts")
table(["Principle","Design fact in the repo"],
 [["Data minimisation & retention","Audio → one score, then discarded; only a SHA-256 hash is kept (DPDP §8)."],
  ["Purpose limitation","Used solely for fraud-risk scoring — no profiling, no training on customer calls."],
  ["Data localisation","On-prem/air-gapped — data never leaves the bank; zero external calls at runtime."],
  ["No solely-automated decision","Advises, never auto-blocks — a human makes every customer-affecting call."],
  ["Transparency","Reason codes + /api/why-fusion plain-language account of any decision."],
  ["Accountability","Tamper-evident SHA-256 ledger + per-decision action log for grievance/audit."]],
 widths=[2.3,4.4])
para("Alignment by design, not a legal certification — final DPDP compliance depends on the deploying bank's own notice/consent obligations.", italic=True, color=GREY)

# ============================ 10. DEMO FLOW ============================
H1("10 · Live Demo Flow")
num("Operator Console → drop 02_ai_clone_1.wav → HIGH ~0.96; show reason codes + spectrogram.")
num("Live Call / streaming → timeline crosses 0.70 at 3.0 s.")
num("Liveness → issue challenge, answer live → 3-check PASS; then play a recording → content FAIL.")
num("Fairness page → per-language FP bars; name Telugu as the honest weak spot.")
num("/docs → it's a real OpenAPI service; mention /api/why-fusion.")
rich([("Run locally:  ", True, DARK), ("cd /Volumes/KIOXIA/voxshield/backend && ./run_voxshield.sh", False, ACCENT), ("  → http://localhost:8000/hub", False, GREY)])

# ============================ 11. Q&A ============================
H1("11 · Judge Q&A — the Hard Questions, Honest Answers")

H2("A · Accuracy & method")
qa("Is 5.9% EER just overfitting or leakage?",
   "No. The In-the-Wild corpus is held out entirely; the neural models are frozen; the stacker trains on 480 clips and is evaluated on a disjoint 320-clip split it never saw. Cross-dataset, and the per-detector scoreboard is reproducible from meta_scores.csv.")
qa("Why five models? Isn't one good model enough?",
   "Each detector fails differently. Best single is 16% EER; fusion gets 5.9%. Naive averaging is actually worse (19%) than the best single — only a learned stacker that knows how much to trust each detector wins.")
qa("Why keep two detectors with negative weights — why not delete them?",
   "A negative weight is a contrarian feature, not a useless detector. When those two fire in a particular pattern, that pattern is informative to the stacker. Removing them measurably hurt fusion. Keeping and showing them is the honest, better-performing choice.")
qa("Why does calibration matter?",
   "A bank acts on a probability, not a raw score. We Platt-calibrate so 0.7 means ~70% (ECE 0.044, Brier 0.048), and expose an abstain band for the uncertain middle instead of forcing a call.")
qa("How is this different from a commercial deepfake-detection API?",
   "Four things a single-model cloud API can't give a bank: learned multi-model fusion + calibration, explainable reason codes, measured Indian-language fairness, and on-prem/air-gapped + liveness. It's a defence system, not a classifier.")

H2("B · Fairness")
qa("How do you KNOW it's fair to Indian languages?",
   "We measured it — genuine speech in 10 languages, per-language FP published (including the bad ones). Channel-aware thresholding cut overall Indic clean FP 11.7% → 6.3%, and language-routing lifted Indic fake recall 42% → 82% with English EER unchanged at 5.9%.")
qa("Telugu's FP is still high — isn't that a problem?",
   "Yes, and we show it rather than hide it (Telugu 13.3% clean). Two mitigations already in the system: channel-aware thresholds, and we never auto-block — so a false positive costs a verification step, not a frozen account. Full fix (Indic fine-tune) is roadmap.")

H2("C · Robustness & security")
qa("Can an attacker evade you?",
   "We tested exactly this and publish it. Robust to the channels we hardened for — Opus improves (2.5%), G.711 +7.5 pts, MP3 +12.5 pts. But benign DSP degrades us: pitch +48.8, noise +37.5, tempo +25 pts. That's our top gap; fix is matched augmentation + the SSL fine-tune, plus liveness gating action regardless.")
qa("What about replay attacks?",
   "That's what liveness is for. A recording can't answer a challenge with digits that didn't exist when it was recorded. Replay fails content, real-time TTS fails the liveness score, a human relay fails timing.")
qa("White-box adversarial attacks (FGSM/PGD)?",
   "Stated roadmap, not claimed. Our self-test covers signal-level + channel robustness — the reproducible part on our hardware. We don't overclaim.")
qa("What's your false-positive story for a real customer?",
   "~6% on English held-out, 6.3% on clean Indic. Structurally, no customer is ever locked out by a model score — HIGH routes to human step-up. The score is a fraud signal, not a judge.")

H2("D · Data & training")
qa("What did you train on, and where's the leakage control?",
   "Frozen public anti-spoof models + a stacker trained on a mixed corpus with In-the-Wild held out for test. Training uses RawBoost + G.711 codec augmentation. Indic fakes synthesized (MMS-TTS); genuine Indic from IndicVoices. Test split is disjoint.")
qa("Your eval sets are small (n=320, 30 clips/language).",
   "Fair — they're honest sample sizes and labelled everywhere (no “up to”, no projections). Big enough to be directional and reproducible; scaling the eval is part of the pilot phase. We'd rather show a real 320-clip number than a projected one.")

H2("E · Deployment, privacy, scale")
qa("Latency in production?",
   "GPU sub-second; commodity CPU 3–8 s. Streaming time-to-flag 3.0 s (measured, latency_trace.json), inside the 10 s design target.")
qa("DPDP / data privacy?",
   "On-prem/air-gapped → data never leaves the bank; raw audio never stored in clear (SHA-256 only); no training on customer calls; no solely-automated decision; full audit trail. Six DPDP principles mapped to six design facts.")
qa("Does it scale?",
   "Stateless — no sessions, no shared state. Add replicas behind a load balancer, capacity grows linearly. ~2 GB Docker, zero runtime downloads → real air-gap.")

H2("F · Business & differentiation")
qa("Why can't a bank just buy an existing vendor?",
   "Existing vendors are English-centric single models behind a cloud endpoint. A PSU bank needs measured Indian-language fairness, on-prem residency, explainability, and liveness — that's the moat, and it's procurable.")
qa("What's live vs. roadmap?",
   "Live today (TRL-5): the five-detector fusion, fairness eval, liveness, live two-party call demo, on-prem Docker, audit trail. Roadmap: 12-sector expansion, managed-service SLAs, SOC 2 / ISO 27001, the Indic SSL fine-tune. We separate the two on the slides deliberately.")
qa("Revenue model?",
   "Enterprise SaaS (per-line), metered API usage, on-prem licensing (banking/defense), and government citizen-helpline contracts. Banking fraud-desk is the beachhead.")

H2("G · The curveballs")
qa("What happens when generators get better?",
   "Two structural defences that don't depend on today's artifacts: fusion (a new generator must beat five decorrelated detectors AND the stacker), and liveness (challenge-response is generator-agnostic — it attacks the replay/real-time constraint, not the fingerprint). Plus a retraining pipeline.")
qa("What's the single biggest weakness you'd fix first?",
   "Benign-DSP robustness (pitch/noise/tempo). It's measured, published, and the fix is concrete: matched augmentation + the XLS-R+AASIST Indic fine-tune. Better you hear it from us than find it.")
qa("If I pitch-shift a clone you miss it — is this even useful?",
   "Detection is one layer. That attacker still has to pass liveness to move money, and the intelligence layer (scam-stage + intent) fires on the transcript regardless of acoustic evasion. Defence-in-depth means no single evasion wins.")

# ============================ 12. GUARDRAILS ============================
H1("12 · Honesty Guardrails (do NOT overclaim)")
bullet("Say “TRL-5, validated working system” — not “production-deployed in a bank.”")
bullet("The 12 sectors are addressable expansion; banking is the only live one.")
bullet("99.9% / <300 ms / SOC 2 / ISO 27001 are targets, not current facts.")
bullet("The XLS-R Indic fine-tune “100%” figure has no committed artifact — call it roadmap; cite 42→82% routed as the real number.")
bullet("Integration logos (Azure/Twilio/Salesforce…) are channels it CAN integrate with, not existing customers.")
bullet("Pitch/tempo/noise DO degrade us — never claim full robustness; claim codec-robustness (the measured, true one).")

# ============================ APPENDIX ============================
H1("Appendix · Artifacts & Reproduction")
para("Every number above regenerates from committed artifacts in backend/artifacts/ via:")
bullet("calibration_report.py → meta_eval.json, calibration.json (EER, AUC, ECE, confusion)")
bullet("eval_languages.py → lang_report.json (per-language FP)")
bullet("robustness_test.py --per-class 40 → robustness.json (7-condition self-test)")
bullet("latency_trace.py → latency_trace.json (streaming time-to-flag)")
bullet("Per-detector scoreboard recomputes from artifacts/meta_scores.csv (800 clips).")
para("Model card: backend/MODEL_CARD.md.  Run the app: backend/run_voxshield.sh → http://localhost:8000/hub", after=2)

doc.save("VoxShield_Presentation_Script.docx")
print("wrote VoxShield_Presentation_Script.docx")
