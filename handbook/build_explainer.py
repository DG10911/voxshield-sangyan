# -*- coding: utf-8 -*-
"""VoxShield — Complete Explainer & Judge Guide (.docx).
Explains every part of the system end to end: the threat, how voice clones are
made, audio engineering (G.711/8kHz/48kHz), datasets, models + our fine-tuning,
the detection pipeline, every detector, competitors, scalability, security,
API, VPS/RAM, and roadmap. Grounded in the real deployed system."""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE=RGBColor(0x1F,0x4E,0x8C); DARK=RGBColor(0x11,0x11,0x11); GREY=RGBColor(0x55,0x55,0x55)
GREEN=RGBColor(0x1F,0x7A,0x33); RED=RGBColor(0xB0,0x2A,0x2A); PURPLE=RGBColor(0x5B,0x2A,0x86)
ACCENT=RGBColor(0x2F,0x6F,0xE0); AMBER=RGBColor(0xB0,0x6A,0x00)

doc=Document()
st=doc.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(10.5); st.font.color.rgb=DARK
for s in doc.sections:
    s.left_margin=s.right_margin=Inches(0.75); s.top_margin=s.bottom_margin=Inches(0.7)

def H1(t,color=BLUE):
    p=doc.add_heading(level=1); r=p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(16); r.bold=True
    p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(4); return p
def H2(t,color=ACCENT):
    p=doc.add_heading(level=2); r=p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(12.5); r.bold=True; return p
def para(t="",size=10.5,color=DARK,bold=False,italic=False,after=6):
    p=doc.add_paragraph()
    if t: r=p.add_run(t); r.font.size=Pt(size); r.font.color.rgb=color; r.bold=bold; r.italic=italic
    p.paragraph_format.space_after=Pt(after); return p
def eli5(t):
    p=doc.add_paragraph(); r=p.add_run("In simple words:  "); r.bold=True; r.font.color.rgb=GREEN
    r2=p.add_run(t); r2.italic=True; r2.font.color.rgb=GREY; r2.font.size=Pt(10.5); p.paragraph_format.space_after=Pt(6); return p
def bullet(t,bold_prefix=None,color=DARK):
    p=doc.add_paragraph(style="List Bullet")
    if bold_prefix: r=p.add_run(bold_prefix); r.bold=True; r.font.color.rgb=color
    r2=p.add_run(t); r2.font.size=Pt(10.5); return p
def numi(t,bold_prefix=None):
    p=doc.add_paragraph(style="List Number")
    if bold_prefix: r=p.add_run(bold_prefix); r.bold=True
    p.add_run(t); return p
def rich(parts,after=6):
    p=doc.add_paragraph()
    for tup in parts:
        txt=tup[0]; b=tup[1] if len(tup)>1 else False; c=tup[2] if len(tup)>2 else DARK; it=tup[3] if len(tup)>3 else False
        r=p.add_run(txt); r.bold=b; r.font.color.rgb=c; r.italic=it; r.font.size=Pt(10.5)
    p.paragraph_format.space_after=Pt(after); return p
def mono(t):
    from docx.oxml.ns import qn; from docx.oxml import OxmlElement
    p=doc.add_paragraph()
    for line in t.split("\n"):
        r=p.add_run(line+"\n"); r.font.size=Pt(8.5); rpr=r._element.get_or_add_rPr()
        rf=OxmlElement('w:rFonts'); rf.set(qn('w:ascii'),'Consolas'); rf.set(qn('w:hAnsi'),'Consolas'); rpr.append(rf)
    p.paragraph_format.space_after=Pt(6); return p
def table(headers,rows,widths=None,hi_last=False):
    t=doc.add_table(rows=1,cols=len(headers)); t.style="Light Grid Accent 1"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(headers):
        run=t.rows[0].cells[i].paragraphs[0].add_run(h); run.bold=True; run.font.size=Pt(9.5); run.font.color.rgb=BLUE
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            run=cells[i].paragraphs[0].add_run(str(val)); run.font.size=Pt(9.5)
            if hi_last and ri==len(rows)-1: run.bold=True; run.font.color.rgb=GREEN
    if widths:
        for i,w in enumerate(widths):
            for r in t.rows: r.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(2); return t
def pb(): doc.add_page_break()

# ===================== COVER =====================
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("VoxShield"); r.bold=True; r.font.size=Pt(32); r.font.color.rgb=BLUE
for txt,sz,col,it in [("Complete Explainer & Judge Guide",15,DARK,False),
  ("Every part of the system, explained end to end — from how voice clones are made to how we detect them.",10.5,GREY,True),
  ("AI voice-clone detection for Indian banking  ·  Team DigiSeva · PS2  ·  Live at 64.177.121.208.sslip.io",10,GREEN,False)]:
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr=q.add_run(txt); rr.font.size=Pt(sz); rr.font.color.rgb=col; rr.italic=it
para()
rich([("How to read this.  ",True,PURPLE),("Each topic starts with a plain-English explanation, then the technical detail a judge would probe. Every number is from the real, deployed system.",False)])
pb()

# ===================== 1. WHAT IS VOXSHIELD (ALL FEATURES) =====================
H1("1 · What VoxShield Is — Every Feature")
eli5("A smart security guard for the bank's phone line. It listens to a call and decides in ~2 seconds whether the voice is a real human or an AI clone — fairly, across Indian languages — and it never freezes your account by itself; it warns a human.")
para("VoxShield is a defence-in-depth system (not a single model). Its features:")
table(["Feature","What it does","Endpoint / page"],
 [["Deepfake detection","5 AI detectors fused → real/fake verdict + reason codes + spectrogram","/api/analyze · operator console"],
  ["Custom Indic detector","Our own fine-tuned model, catches Indian-language fakes","booster in fusion"],
  ["Speaker verification","Is it the SAME customer? (ECAPA voiceprint) × is it live-human?","/api/verify-speaker · /speaker"],
  ["Liveness challenge","Say a random number — a recording can't answer","/api/liveness · /liveness"],
  ["Digital Arrest Shield","Fuses clone-score + scam-intent from the transcript (Hindi/Hinglish)","/api/analyze-call · /scam"],
  ["Fraud-ring linkage","Links the same cloned voice across victims (across 8 kHz codec)","in /api/analyze"],
  ["Partial-fake localize","Which seconds of a call are AI-spliced","/api/localize"],
  ["Robustness self-test","We red-team ourselves: noise/codec/pitch attacks","/api/stress-test · /robust"],
  ["Explainability","Reason codes + exact SHAP per detector","/api/why-fusion"],
  ["Live streaming","Score a live call every ~2s; flag at 3.0s","/api/stream-analyze · /call"]],
 widths=[1.9,3.4,1.9])

# ===================== 2. THE THREAT: HOW VOICE CLONES ARE MADE =====================
H1("2 · How AI Voice Clones Are Made (the real-world attack)")
eli5("Modern AI can copy a person's voice from just a few seconds of audio — a voicemail, an Instagram reel, a customer-care recording. Then it can make that voice say anything. Criminals use this to call banks or families pretending to be someone you trust.")
H2("The two ways a clone is made")
bullet("Text-to-Speech (TTS) voice cloning — you type text, the AI speaks it in the target's voice. Modern zero-shot TTS (ElevenLabs, VALL-E, XTTS, MMS-TTS, Bark) needs only 3–10 seconds of reference audio.", "1) ", PURPLE)
bullet("Voice Conversion (VC) — an attacker speaks normally, and the AI converts their voice to sound like the target in real time. Used for live scam calls.", "2) ", PURPLE)
H2("The voice-cloning pipeline (how the machine builds a fake voice)")
mono(
"  [Reference audio: 3-10 s of the victim]\n"
"        │\n"
"  ▼ Speaker encoder  ──►  a 'voiceprint' embedding (who the voice is)\n"
"  ▼ Text / source speech ─┐\n"
"  ▼ Acoustic model (TTS/VC: VITS, Tacotron, VALL-E) ──► mel-spectrogram in the target voice\n"
"  ▼ Neural vocoder (HiFi-GAN, WaveNet, WaveGlow) ──► raw audio waveform\n"
"        │\n"
"  ▼ [Cloned speech — sounds human to the ear]")
para("The critical fact for detection: the **neural vocoder** (the last stage) leaves tell-tale artifacts — unnaturally regular phase, over-smooth high-frequency energy (>6 kHz), missing micro-variation (jitter/shimmer/breath). Humans can't hear these; VoxShield's detectors read exactly these fingerprints.")
H2("The real-world attack chain (why banks care)")
numi("Harvest the victim's voice — voicemail greeting, social media clip, a recorded customer-care call.")
numi("Clone it with a public tool (minutes, cheap, multilingual).")
numi("Call the bank / family: 'digital arrest', relative-in-distress, or voice-authorised transfer.")
numi("The human on the line can't tell — the clone knows names and passes the 'sounds right' test. Money moves in minutes.")

# ===================== 3. AUDIO ENGINEERING: G.711 / 8kHz / 48kHz =====================
H1("3 · Audio Engineering — G.711, 8 kHz Telephony vs 48 kHz Studio")
eli5("Sound is measured many times per second (the 'sample rate'). Studios record at high quality; phone lines record at low quality and squeeze the audio to save bandwidth. That squeezing throws away exactly the clues we use to spot a fake — which is why phone-line detection is the hard problem, and VoxShield's specialty.")
table(["","Studio","Phone line (telephony)"],
 [["Sample rate","48 kHz (or 44.1)","8 kHz"],
  ["Frequencies kept (Nyquist)","up to 24 kHz","up to 4 kHz only"],
  ["Codec","lossless / high-bitrate","G.711 µ-law (compressed, band-limited)"],
  ["Clone artifacts >6 kHz","preserved — easy to detect","DESTROYED by the codec — hard to detect"]],
 widths=[2.3,2.1,2.6])
bullet("G.711 (µ-law) is the classic telephony codec. It compresses and band-limits audio to ~3.4 kHz — smearing the high-frequency vocoder fingerprints most detectors depend on. A detector trained only on studio audio goes blind on a real bank call.", "Why it matters:  ", RED)
bullet("VoxShield trains WITH G.711 (and Opus, MP3) codec augmentation, so telephony is home turf, not hostile territory. Our robustness test shows Opus even improves and G.711 moves EER only +7.5 pts — while un-hardened detectors collapse.", "Our answer:  ", GREEN)
para("Note: VoxShield always resamples to 16 kHz internally (keeps the 6–8 kHz band where surviving artifacts live); '8 kHz' is a detected channel flag that raises the decision bar to 0.85 for phone audio.")

# ===================== 4. DETECTION PIPELINE =====================
H1("4 · The VoxShield Detection Pipeline (every part)")
eli5("The call goes through an assembly line: clean the audio → turn it into fingerprint numbers → run 5 AI detectors → a 6th 'referee' model combines them → turn the score into a probability → decide, and explain why.")
mono(
"  ☎ Call audio (8 kHz G.711 / 16 kHz)\n"
"   ▼ load_audio ....... resample→16 kHz mono · drop silence · cap first 3-6 s of speech\n"
"   ▼ Feature bank ..... 89-dim: LFCC(40) + CQCC(40) + 9 interpretable cues\n"
"   ▼ 5 detectors ...... run in parallel (acoustic-DSP · Deepfake-V2 · XLS-R · DistilHuBERT · LFCC/CQCC head)\n"
"   ▼ + Indic booster .. on Indian-language audio, OUR fine-tuned model votes\n"
"   ▼ Meta-fusion ...... a learned logistic 'referee' weighs the detectors\n"
"   ▼ Calibration ...... Platt scaling → a true probability (not a raw score)\n"
"   ▼ Channel-aware .... phone lines must clear a stricter 0.85 bar\n"
"   ▼ Decision ......... HIGH→step-up · MEDIUM→monitor · LOW→pass + reason codes + SHAP\n"
"   ▼ Never auto-block . a human always decides customer action")
para("Every step runs on the bank's own server (on-prem/air-gapped capable). Verdict in ~2 seconds on a commodity CPU.")

# ===================== 5. THE DETECTORS (WHY NOT ONE) =====================
H1("5 · The Detectors — and Why Not Just One")
eli5("We don't trust one AI. We run five different 'listeners', each good at catching a different kind of fake, and a sixth tiny model learns how much to trust each. Some are so unreliable the referee learns to bet AGAINST them — that honesty is the design.")
H2("Why an ensemble beats a single model")
bullet("Each detector fails differently — a generator that fools one often doesn't fool another. A single model = a single blind spot an attacker walks through.")
bullet("The proof (held-out): best single model = 16.0% error; a naive average is WORSE at 19.1%; only the LEARNED stacker hits 5.9%. You need learning-to-trust, not just more models.")
H2("The five detectors + our custom sixth")
table(["Detector","Type","Params","Standalone EER","Stacker weight"],
 [["XLS-R 300M","SSL transformer (multilingual)","~300M","16.0%","+1.21"],
  ["DistilHuBERT","SSL transformer (distilled)","~24M","23-25%","+2.22"],
  ["LFCC+CQCC head","classical + logistic (89-dim)","tiny","26.8%","+2.10"],
  ["Acoustic-DSP","hand-crafted heuristic (no ML)","0","46.9%","−0.55"],
  ["Deepfake-V2 (wav2vec2)","SSL transformer","~95M","62%","−1.17"],
  ["★ Indic XLS-R (OURS)","fine-tuned by us on Indic","~300M","see §7","booster"]],
 widths=[1.9,2.3,0.9,1.3,1.1])
para("The negative weights (−0.55, −1.17) are not bugs — they're contrarian features. When those two detectors fire in a certain pattern, that pattern itself is informative, so the referee uses it as evidence in the opposite direction. Removing them measurably hurt fusion.", italic=True, color=GREY)
H2("The 5 reason codes (an operator reads them aloud)")
table(["Code","Meaning"],
 [["SSL","overall neural synthesis likelihood"],["PH","unnaturally regular phase (group-delay)"],
  ["HF","neural-vocoder fingerprint (>6 kHz energy)"],["PR","missing prosody (F0 jitter, shimmer)"],
  ["BR","TTS inserts silence, not breath"]], widths=[1.0,5.7])

# ===================== 6. DATASETS =====================
H1("6 · Datasets — What We Used, From Where, and How")
table(["Dataset","Source","Role","How we used it"],
 [["In-the-Wild","public deepfake corpus","English real+fake","HELD OUT for honest testing (never trained on) → 5.9% EER"],
  ["ASVspoof / WaveFake","public anti-spoof","English train","training the classical fusion head"],
  ["IndicVoices","AI4Bharat (IIT-Madras), Bhashini","genuine Indic","4,000 real voices, 10 languages → train the Indic detector (bonafide class)"],
  ["Indic fakes (ours)","synthesized with Meta MMS-TTS","fake Indic","4,000 synthetic clips, 10 languages → the fake class our detector learns"],
  ["Demo pack","curated","live demo","genuine + clone + 10-language edge cases on the site"]],
 widths=[1.6,1.9,1.4,2.5])
para("The honesty protocol: In-the-Wild is held out entirely, neural models are frozen, and the meta-stacker trains on a disjoint 480-clip split and is evaluated on 320 clips it never saw. That's why our numbers survive scrutiny — no leakage.")

# ===================== 7. MODELS + FINE-TUNING =====================
H1("7 · Models — How We Got Them & What We Fine-Tuned")
H2("The models we use and where they came from")
table(["Model","Source","Params","Purpose"],
 [["Deepfake-audio-detection-V2","HuggingFace (MelodyMachine)","~95M","SSL anti-spoof"],
  ["wav2vec2-large-xlsr-deepfake","HuggingFace (Gustking)","~300M","multilingual anti-spoof (strong)"],
  ["distilhubert-in-the-wild","HuggingFace (Om-Parab)","~24M","SSL anti-spoof"],
  ["ECAPA-TDNN","SpeechBrain (VoxCeleb)","~22M","speaker voiceprint (192-D)"],
  ["Whisper (base/small)","OpenAI + faster-whisper","74M / 244M","liveness ASR + Hindi scam transcription + language-ID"],
  ["Silero VAD","open source","tiny","voice-activity gate (anti-hallucination)"],
  ["MMS-TTS (×10 langs)","Meta","~145M each","GENERATE Indic fakes for training"]],
 widths=[2.3,2.0,1.0,1.9])
H2("★ What WE fine-tuned (our unique IP)")
rich([("We trained our own Indic deepfake detector.  ",True,GREEN),
      ("We took XLS-R-300M and fine-tuned it on 4,000 IndicVoices genuine clips + 4,000 MMS-TTS Indic fakes (10 languages), on a rented GPU (RTX 5090, ~30 min, ~$2). It's deployed LIVE as an Indic-routed booster.",False)])
table(["Metric (held-out Indic)","Before (base ensemble)","After (our fine-tune)"],
 [["Genuine false positives","up to 13% (Telugu)","0%"],
  ["Indic fake recall","42% → 82% (routing)","100% (on trained engine)"],
  ["English EER","5.9%","unchanged (5.9%)"],
  ["Verified live","—","genuine Tamil LOW 0.06 · Tamil fake HIGH 1.0 +indic-boost"]],
 widths=[2.6,2.0,2.1], hi_last=True)
para("Honest caveat (say this to judges): the 100% recall is in-distribution (the MMS-TTS engine we trained against). Real-world coverage broadens as we add fakes from more engines (ElevenLabs, NVIDIA) — the training pipeline is committed and repeatable.", italic=True, color=AMBER)
H2("Fine-tune recipe (parameters)")
bullet("Base: facebook/wav2vec2-xls-r-300m (300M params) · head: 2-class audio-classification")
bullet("Data: 8,000 clips (4k genuine + 4k fake), 10 Indian languages · 3 epochs · batch 8 · lr 1e-5")
bullet("Augmentation: RawBoost + G.711/Opus/MP3 codec (channel robustness) · runtime: ~30 min on RTX 5090")
bullet("Integration: env-gated booster (VOXSHIELD_INDIC_BOOST); only raises the score on confident Indic fakes → no new false positives; zero English regression")

# ===================== 8. OTHER FEATURES =====================
H1("8 · Speaker Verification · Liveness · Scam Intelligence")
H2("Speaker verification (identity × liveness)")
para("A real ECAPA-TDNN voiceprint (192-D) answers TWO questions at once: is it the same customer? (cosine ≥ 0.18) AND is it a live human? (5-model synthesis check). Three outcomes: VERIFIED / REJECTED-CLONE (same voice but synthetic — the case biometrics miss) / REJECTED-IDENTITY.")
H2("Liveness challenge-response")
para("The system speaks a random number; the caller must say it. Three checks: Content (Whisper ASR + Silero VAD), Liveness (ensemble scores the reply), Timing (within the window). Replay fails content, real-time TTS fails liveness, human-relay fails timing.")
H2("Digital Arrest Shield (the intelligence layer)")
para("Fuses the clone score with a scam-intent read of the transcript (Hindi/Hinglish via faster-whisper) and tracks the scam stage (Authority → Threat → Isolation → Extraction). On a digital-arrest verdict it speaks a victim-protection warning in the caller's language ('no agency arrests over a call — hang up and call 1930').")

# ===================== 9. COMPETITORS =====================
H1("9 · Competitors — Honest Comparison")
table(["Dimension","VoxShield","Pindrop Pulse","Reality Defender","aivoicedetector"],
 [["Accuracy","~94% (5.9% EER, honest)","99% (w/ MFA)","98.5%","99% (clean)"],
  ["Speed","~2 s (CPU)","~2 s","real-time","0.48 s (GPU)"],
  ["Indian languages","✓ 10, own model","✗","✗","partial"],
  ["Phone/8kHz hardened","✓ built for it","✓","⚠","✗ struggles"],
  ["On-prem / air-gap","✓","✗ cloud","✗ cloud","✗ cloud"],
  ["Liveness challenge","✓","⚠ signals","✗","✗"],
  ["Explainable (SHAP)","✓","⚠","⚠","✗"],
  ["Scam-intent layer","✓ unique","✗","✗","✗"],
  ["Cost","free / self-host","$$$ enterprise","$0.05/scan","freemium"],
  ["Maturity","TRL-5 prototype","5B calls","govt contracts","live product"]],
 widths=[1.7,1.5,1.3,1.3,1.3])
rich([("The honest moat:  ",True,DARK),("We won't beat Pindrop on scale or raw accuracy — they're billion-dollar products. But NONE of them do Indian-language telephony, on-prem, with liveness + scam-intent. On the problem an Indian bank actually has, we're the only complete answer — and we trained our own Indic model to prove it.",False)])

# ===================== 10. DEPLOYMENT / VPS / RAM / API =====================
H1("10 · Deployment — VPS, RAM, Parameters, API")
H2("Where it runs (what to tell judges)")
table(["Item","Detail"],
 [["Live URL","https://64.177.121.208.sslip.io  (public, HTTPS)"],
  ["Host","Vultr cloud VPS · Ubuntu · AMD EPYC"],
  ["CPU / RAM","4 vCPU / 7.2 GB RAM (+8 GB swap) — a ~$25/month box"],
  ["Detection latency","~2 s (genuine/clone) · speaker verify ~1.5 s · TURN-relay for cross-network calls"],
  ["RAM used","~4–5 GB with all models loaded (3 SSL detectors + Whisper + ECAPA + our Indic model)"],
  ["Model footprint","~2 GB baked models + 1.2 GB our Indic model; no runtime downloads (air-gap real)"],
  ["Web server","Caddy (auto-HTTPS) → single-process FastAPI (uvicorn)"]],
 widths=[1.7,5.0])
H2("Total model parameters in the system")
bullet("Detection ensemble: ~420M params (XLS-R 300M + wav2vec2 95M + DistilHuBERT 24M) + our Indic XLS-R 300M")
bullet("Support: ECAPA 22M · Whisper base 74M / small 244M · Silero VAD tiny")
bullet("All run on CPU at inference — same accuracy as GPU, ~2 s/call")
H2("Using VoxShield as an API")
para("One HTTP call — JSON in, JSON out. Drop-in for any dialer, IVR, or core-banking system:")
mono(
"POST /api/analyze            → {score, label, reasons[], per_model{}, spectrogram, sha256}\n"
"POST /api/verify-speaker     → {decision: VERIFIED|REJECTED-CLONE|REJECTED-IDENTITY, similarity}\n"
"POST /api/liveness/new+verify→ random-digit challenge + pass/fail\n"
"POST /api/analyze-call       → Digital Arrest Shield (clone × scam-intent)\n"
"POST /api/stream-analyze     → live-call timeline + time-to-flag\n"
"GET  /docs                   → full OpenAPI documentation")
para("Stateless and horizontally scalable: add replicas behind a load balancer, capacity grows linearly. On-prem, so customer audio never leaves the bank.")

# ===================== 11. SCALABILITY & SECURITY =====================
H1("11 · Scalability & Security")
H2("Scaling from 1 to 1,000,000 calls")
table(["Scale","What runs","Cost driver"],
 [["1–100 calls","single CPU box (today)","one $25 VPS"],
  ["10,000 concurrent","K8s pods + GPU inference w/ batching + Redis/queue","GPU fleet"],
  ["1,000,000 concurrent","multi-region autoscale + sharded queue + DR/HA","GPU $$$ + ops"]],
 widths=[1.7,3.4,1.6])
para("Detection stays ~2 s and accuracy is identical on CPU; GPU only buys sub-second speed at scale. The app is stateless by design, so scale-out is standard web-service engineering once state (audit, enrolment) is externalised to a DB.")
H2("Security — honest status")
bullet("REAL today: SHA-256 audio audit hash · on-prem / air-gap-capable · never auto-block · self-signed/Caddy HTTPS · TURN relay for calls", color=GREEN)
bullet("Roadmap (be honest): API-key auth, rate-limiting, persistent encrypted DB, AES-256 at rest, SOC2/ISO27001. These are the production-hardening backlog — named, not hidden.", color=AMBER)
para("DPDP Act 2023 alignment by design: data minimisation (audio → one score, then discarded; only a hash kept), purpose limitation, no solely-automated decision, transparency (reason codes), on-prem localisation.")

# ===================== 12. ROADMAP =====================
H1("12 · Future Scope & Roadmap (TRL 5 → 9)")
table(["Phase","Milestones"],
 [["Now (TRL-5)","Live system: 5-detector fusion (5.9% EER), our Indic detector deployed, speaker verify, liveness, scam shield"],
  ["0–3 mo (TRL-6)","Harden Indic model with MORE TTS engines (ElevenLabs, NVIDIA magpie); bank sandbox pilot on recorded IVR; add auth + DB"],
  ["3–6 mo (TRL-7)","Close benign-DSP gap (matched augmentation); GPU inference + batching; rate-limit + RBAC; concurrency load-tests"],
  ["6–12 mo (TRL-8)","Live-line pilot; multi-worker/K8s; HA/DR; SOC2/ISO27001 begins; edge/quantised model"],
  ["12+ mo (TRL-9)","National infrastructure: multi-region autoscale; FGSM/PGD hardening; continuous retraining; expand to telecom/gov/insurance"]],
 widths=[1.5,5.2])
H2("Why VoxShield will be best in the real world")
bullet("It targets the exact real problem: Indian-language voice fraud on phone lines — which the global tools don't serve.")
bullet("It's a complete defence (detection + identity + liveness + intelligence), not a single classifier an attacker can evade.")
bullet("It's procurable by a real bank: on-prem, explainable, fair, never-auto-block, DPDP-aligned.")
bullet("We proved we can execute: trained and deployed our own Indic model overnight for $2 — the pipeline is committed and repeatable.")

para()
rich([("One-line summary for judges.  ",True,PURPLE),("VoxShield is a complete, live, on-prem voice-fraud defence built for India — five fused detectors plus our own fine-tuned Indic model, with speaker verification, liveness, and scam-intelligence — catching AI voice clones on 8 kHz phone lines, in Tamil and Hindi, in about two seconds, running right now on a $25 server.",False,DARK)])

out=os.path.join(HERE,"..","VoxShield_Complete_Explainer.docx")
doc.save(out); print("wrote",os.path.abspath(out))
