# -*- coding: utf-8 -*-
"""VoxShield — Complete Engineering Handbook builder (.docx).
16 sections + 100 investor Q&A + 100 judge Q&A. Every number grounded in
VOXSHIELD_FACTS.md / committed artifacts. Honest about built-vs-slideware."""
import json, os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE=RGBColor(0x1F,0x4E,0x8C); DARK=RGBColor(0x11,0x11,0x11); GREY=RGBColor(0x55,0x55,0x55)
GREEN=RGBColor(0x1F,0x7A,0x33); RED=RGBColor(0xB0,0x2A,0x2A); PURPLE=RGBColor(0x5B,0x2A,0x86)
ACCENT=RGBColor(0x2F,0x6F,0xE0); AMBER=RGBColor(0xB0,0x6A,0x00)

doc=Document()
st=doc.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(10.5); st.font.color.rgb=DARK
for s in doc.sections:
    s.left_margin=s.right_margin=Inches(0.75); s.top_margin=s.bottom_margin=Inches(0.7)

def H1(t,color=BLUE):
    p=doc.add_heading(level=1); r=p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(17); r.bold=True
    p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(4); return p
def H2(t,color=BLUE):
    p=doc.add_heading(level=2); r=p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(13); r.bold=True; return p
def H3(t,color=ACCENT):
    p=doc.add_heading(level=3); r=p.add_run(t); r.font.color.rgb=color; r.font.size=Pt(11.5); r.bold=True; return p
def para(t="",size=10.5,color=DARK,bold=False,italic=False,after=6,before=0):
    p=doc.add_paragraph()
    if t: r=p.add_run(t); r.font.size=Pt(size); r.font.color.rgb=color; r.bold=bold; r.italic=italic
    p.paragraph_format.space_after=Pt(after); p.paragraph_format.space_before=Pt(before); return p
def rich(parts,after=6):
    p=doc.add_paragraph()
    for tup in parts:
        txt=tup[0]; b=tup[1] if len(tup)>1 else False; c=tup[2] if len(tup)>2 else DARK; it=tup[3] if len(tup)>3 else False
        r=p.add_run(txt); r.bold=b; r.font.color.rgb=c; r.italic=it; r.font.size=Pt(10.5)
    p.paragraph_format.space_after=Pt(after); return p
def bullet(t,bold_prefix=None,color=DARK):
    p=doc.add_paragraph(style="List Bullet")
    if bold_prefix: r=p.add_run(bold_prefix); r.bold=True; r.font.color.rgb=color
    r2=p.add_run(t); r2.font.size=Pt(10.5); return p
def numi(t,bold_prefix=None):
    p=doc.add_paragraph(style="List Number")
    if bold_prefix: r=p.add_run(bold_prefix); r.bold=True
    p.add_run(t); return p
def eli5(t):
    p=doc.add_paragraph(); r=p.add_run("Like you're 15:  "); r.bold=True; r.font.color.rgb=GREEN
    r2=p.add_run(t); r2.italic=True; r2.font.color.rgb=GREY; r2.font.size=Pt(10.5); p.paragraph_format.space_after=Pt(6); return p
def mono(t):
    p=doc.add_paragraph()
    for line in t.split("\n"):
        r=p.add_run(line+"\n"); r.font.name="Consolas"; r.font.size=Pt(8.5); r.font.color.rgb=DARK
        rpr=r._element.get_or_add_rPr(); rf=OxmlElement('w:rFonts'); rf.set(qn('w:ascii'),'Consolas'); rf.set(qn('w:hAnsi'),'Consolas'); rpr.append(rf)
    p.paragraph_format.space_after=Pt(6); return p
def eq(t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run(t); r.font.name="Consolas"; r.font.size=Pt(10); r.font.color.rgb=PURPLE; r.bold=True
    p.paragraph_format.space_after=Pt(6); p.paragraph_format.space_before=Pt(4); return p
def quote(t,color=BLUE):
    p=doc.add_paragraph(); r=p.add_run("“"+t+"”"); r.italic=True; r.font.color.rgb=color; r.font.size=Pt(11)
    p.paragraph_format.left_indent=Inches(0.3); p.paragraph_format.space_after=Pt(8); return p
def qa(q,a,n=None):
    p=doc.add_paragraph(); lbl=("Q%d  "%n) if n else "Q  "; r=p.add_run(lbl); r.bold=True; r.font.color.rgb=RED
    r2=p.add_run(q); r2.bold=True; r2.font.color.rgb=DARK; r2.font.size=Pt(10.5)
    p.paragraph_format.space_after=Pt(1); p.paragraph_format.space_before=Pt(6); p.paragraph_format.keep_with_next=True
    p2=doc.add_paragraph(); r3=p2.add_run("A  "); r3.bold=True; r3.font.color.rgb=GREEN
    r4=p2.add_run(a); r4.font.size=Pt(10.5); p2.paragraph_format.space_after=Pt(3)
def table(headers,rows,widths=None,hi_last=False,hi_col=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.style="Light Grid Accent 1"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    hdr=t.rows[0].cells
    for i,h in enumerate(headers):
        run=hdr[i].paragraphs[0].add_run(h); run.bold=True; run.font.size=Pt(9.5); run.font.color.rgb=BLUE
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            run=cells[i].paragraphs[0].add_run(str(val)); run.font.size=Pt(9.5)
            if hi_last and ri==len(rows)-1: run.bold=True; run.font.color.rgb=GREEN
            if hi_col is not None and i==hi_col: run.bold=True
    if widths:
        for i,w in enumerate(widths):
            for r in t.rows: r.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(2); return t
def pagebreak(): doc.add_page_break()

# ============================================================ COVER
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("VoxShield"); r.bold=True; r.font.size=Pt(34); r.font.color.rgb=BLUE
for txt,sz,col,it in [("The Complete Engineering Handbook",16,DARK,False),
    ("AI voice-clone detection for Indian banking  ·  Team DigiSeva · PS2  ·  TRL-5",11,GREY,True),
    ("Reverse-engineered from source. Every number traceable to a committed artifact.",10,GREEN,False),
    ("Written to be read by Google / Microsoft / AWS / NVIDIA / OpenAI / Anthropic / RBI engineers.",9.5,GREY,True)]:
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr=q.add_run(txt); rr.font.size=Pt(sz); rr.font.color.rgb=col; rr.italic=it
para()
rich([("How to read this document.  ",True,PURPLE),("Each major concept is taught in layers — a plain-English picture first, then the technical mechanism, then the mathematics, then the implementation as it exists in the repo, then how it deploys and scales, then the tradeoffs and honest weaknesses. Where the pitch deck claims something the code does not yet do, this handbook says so explicitly — that boundary is called out as ",False),("REAL vs SLIDEWARE.",True,RED)])
pagebreak()

# ============================================================ 1. VISION
H1("Section 1 · Project Vision")
eli5("Anyone can now copy your voice from a few seconds of audio — a voicemail, a reel, a call-centre recording. Criminals phone a bank pretending to be you (or pretending to be the police), and the human on the line can't tell the voice is fake. VoxShield is the software that listens to the call and says, in real time, 'this voice is probably a machine' — and does it fairly for people speaking Hindi, Tamil, Telugu, not just English.")
H3("The problem")
bullet("Voice cloning is cheap, public, multilingual, and needs only seconds of reference audio. The clone knows the customer's name and passes the 'sounds right' test.")
bullet("The bank phone channel is 8 kHz G.711 — the codec smears exactly the high-frequency artifacts most detectors rely on, so a studio-trained detector goes blind on a real call.")
bullet("Voice-authorised transfers and social-engineered agents act in minutes. A verdict after the call ends is forensics, not protection — detection must happen in the first seconds.")
bullet("'Digital arrest' and impersonation scams in India run ~₹19,000 cr and are conducted in Hindi/Hinglish, not English — an English-only detector is both blind and unfair.")
H3("Why now")
para("Three curves crossed: (1) open-source TTS/voice-conversion reached human parity from short samples; (2) India's banking moved voice-first (IVR, phone banking, UPI voice) reaching users apps never will; (3) DPDP Act 2023 + RBI fraud-risk pressure made a fair, on-prem, auditable defence procurable. The attack got cheap at the same moment the channel got critical and the regulation arrived.")
H3("Competition & what makes VoxShield different")
table(["Approach","Gap VoxShield closes"],
 [["Commercial deepfake-detection API (single model, cloud)","One model = one blind spot; English-centric; black box; cloud-only; no liveness."],
  ["Voice biometrics (speaker ID) alone","Says 'it's the customer's voice' — and a clone passes. No synthesis check."],
  ["Academic anti-spoof (ASVspoof/AASIST)","State-of-art on clean lab audio; not fairness-tested on Indic telephony, not a deployable product."],
  ["VoxShield","5 decorrelated detectors + learned stacker (5.9% EER), 10-language fairness measured, liveness that beats replay, explainable, on-prem, never auto-blocks."]],
 widths=[3.1,3.6])
H3("The moat")
bullet("Measured Indian-language fairness (per-language FP published, 11.7%→6.3%, Indic recall 42%→82%) — a PSU bank can procure this; a wrapped English model cannot.",color=DARK)
bullet("Defence-in-depth (detection + liveness + intelligence) — no single acoustic evasion wins the whole system.")
bullet("Explainability + on-prem + never-auto-block — the trust properties that get a tool out of pilot and into production at a regulated bank.")
H3("Path to a billion-dollar company (honest)")
para("Beachhead: PSU/private bank fraud desks (India), sold as per-line SaaS + on-prem licence. Expand along the same API to telecom anti-vishing, government citizen-helplines, insurance claims, BPO agent-assist — every place a voice must be provably human. This is an addressable expansion, not current deployment; banking is the only live (TRL-5) market today. The billion-dollar case rests on (a) voice fraud becoming a board-level line item, (b) fairness/on-prem as a durable regulatory moat, and (c) the engine generalising across 12 voice-fraud verticals.")

# ============================================================ 2. WALKTHROUGH
H1("Section 2 · End-to-End System Walkthrough")
para("Every stage a call passes through, in order. Stage names match the code.")
mono(
"  ☎ Incoming call (8 kHz G.711, telephony / IVR / SIP)\n"
"      │\n"
"  ▼ Audio ingest .......... multipart UploadFile → bytes  (app.py analyze/stream-analyze)\n"
"  ▼ load_audio() .......... resample→16 kHz mono · drop silence (top_db=30) · cap 6 s speech\n"
"  ▼ Feature bank .......... 89-dim: LFCC(40)+CQCC(40)+9 scalars (features.feature_vector)\n"
"  ▼ 5 detectors ........... acoustic-dsp · Deepfake-V2 · XLS-R · DistilHuBERT · LFCC/CQCC head\n"
"      │                     (run concurrently in a ThreadPoolExecutor; torch releases the GIL)\n"
"  ▼ Meta-fusion ........... logistic stacker on standardized scores → sigmoid  (meta_fusion)\n"
"  ▼ Calibration ........... Platt sigmoid p=σ(a·s+b) → probability-true score\n"
"  ▼ Channel-aware decision  wideband HIGH≥0.70 · narrowband(phone) HIGH≥0.85\n"
"  ▼ Reason codes + SHAP ... SSL·PH·HF·PR·BR + exact per-detector contributions\n"
"  ▼ Liveness (if action) .. random-digit challenge → Whisper ASR + ensemble + timing\n"
"  ▼ API response .......... JSON verdict + mel-spectrogram PNG + audit hash\n"
"  ▼ Dashboard ............. operator console renders verdict, breakdown, spectrogram\n"
"  ▼ 'Database' ............ IN-MEMORY lists (AUDIT/ACTIONS/…) — no persistence today\n"
"  ▼ Audit ................. SHA-256(raw)[:16] appended to in-RAM AUDIT log (cap 200)\n"
"  ▼ Operator .............. reads verdict + reason codes; may /api/action\n"
"  ▼ Bank workflow ......... HIGH → step-up verification alongside CNAP/caller-ID. NEVER auto-block.")
para("Two facts to internalise from this diagram: the WebSocket (/ws/call) only relays WebRTC signaling — audio is peer-to-peer, never through the server; and the 'database' is Python lists in RAM (a real weakness, addressed in §7/§14).",italic=True,color=GREY)

# ============================================================ 3. AUDIO
H1("Section 3 · Audio Engineering")
eli5("Sound is a wiggly line (a waveform). To spot a fake, we don't look at the raw wiggle — we turn it into 'fingerprint' numbers that describe its texture: which pitches are present, how steady the voice is, whether it breathes. Machines make voices that are too smooth and too steady, and these fingerprints reveal it.")
H3("Sampling, codecs, PCM")
bullet("Sampling rate: how many times/second we measure the wiggle. Phone lines are 8 kHz (captures up to 4 kHz by Nyquist); studio is 16–48 kHz. VoxShield resamples everything to 16 kHz mono (features.SR=16000).")
bullet("G.711 μ-law: the classic 8 kHz telephony codec. It compresses and band-limits, destroying >4 kHz content — exactly the high-frequency artifacts naïve detectors need. We train with G.711 augmentation so telephony is home turf.")
bullet("PCM: raw integer samples; we normalise int→float by dividing by 2^(bits−1).")
para("Note: 8 kHz is a DETECTED CHANNEL FLAG in VoxShield (set when hf_energy_ratio<0.02), not a resample target — we always work at 16 kHz but raise the decision bar to 0.85 when the audio looks narrowband.")
H3("Spectral features — FFT, Mel, MFCC, LFCC, CQCC")
bullet("FFT: turns a window of waveform into 'how much energy at each frequency'. The basis of every spectral feature.")
bullet("Mel spectrogram: FFT energy warped to the Mel (perceptual) scale, 128 bands — used only for the dashboard picture, not fed to models.")
bullet("MFCC vs LFCC vs CQCC: all are cepstral (DCT of log-filterbank energies). MFCC uses Mel spacing (speech-recognition bias). VoxShield uses LFCC (LINEAR filterbank — keeps high-frequency detail where vocoder artifacts live) and CQCC (Constant-Q Transform, log-frequency, 84 bins/12-per-octave — excellent pitch/harmonic resolution). Both are the standard anti-spoofing front-ends.")
rich([("In the 89-dim vector:  ",True,DARK),("LFCC contributes 40 dims (20 coeffs × mean+std), CQCC 40 dims (20 × mean+std), plus 9 scalar cues = 89.",False)])
H3("The 9 scalar cues (the human-interpretable part)")
table(["Scalar","What it measures","Why it betrays a fake"],
 [["hf_energy_ratio","energy >6 kHz vs total","neural vocoders leak/oversmooth HF"],
  ["hf_regularity","regularity of HF band","synthesis is unnaturally periodic"],
  ["spectral_flatness","noise-like vs tonal","TTS spectra are 'too clean'"],
  ["phase_reg","group-delay/phase regularity","clones have unnatural, over-regular phase"],
  ["f0_jitter","cycle-to-cycle pitch variation","humans jitter; TTS is too steady"],
  ["shimmer","cycle-to-cycle amplitude variation","humans shimmer; TTS is too even"],
  ["f0_voiced_ratio","fraction voiced","prosody signature"],
  ["silence_ratio","silence fraction","TTS inserts silence, not breath"],
  ["breath_score","breath-band energy","TTS omits real breath cues"]],
 widths=[1.5,2.6,2.6])
H3("Group delay & phase")
para("Most detectors use magnitude spectra and ignore phase. VoxShield computes group-delay variance (the derivative of unwrapped phase) — clones are unnaturally regular in phase because vocoders reconstruct phase synthetically. It enters as the scalar phase_reg = 1 − gd_var/3.")
H3("Prosody — pitch, jitter, shimmer")
para("Extracted with librosa.pyin (probabilistic YIN) over the first ~3 s. Jitter = mean|Δperiod|/mean(period); shimmer = std(amplitude)/mean(amplitude). Genuine speech carries micro-variation from a physical larynx; TTS is smoother. Reason code PR fires here.")
H3("Vocoder fingerprints & HF artifacts")
para("Neural vocoders (HiFi-GAN, WaveNet-style) leave tell-tale >6 kHz energy patterns and periodicities. hf_energy_ratio + hf_regularity capture this; reason code HF fires here. This is also the first thing an 8 kHz codec destroys — the core tension of telephony deepfake detection.")
H3("RawBoost & codec augmentation (training)")
para("RawBoost adds convolutive + impulsive + coloured-noise perturbations; G.711/Opus/MP3 codec augmentation passes training audio through real codecs. The LFCC/CQCC head is trained with both, which is WHY the robustness self-test shows codec conditions stay usable (Opus even improves to 2.5% EER) while un-augmented benign transforms (pitch/noise/tempo) still hurt — you are robust to what you trained on.")

# ============================================================ 4. ML
H1("Section 4 · Machine Learning — Every Model")
eli5("We don't trust one AI. We run five different 'listeners', each good at catching a different kind of fake, then a sixth tiny model learns how much to trust each listener. Some listeners are so unreliable the sixth model learns to bet AGAINST them.")
H3("The five detectors")
table(["Detector","Type / model","Standalone EER","Stacker weight"],
 [["XLS-R 300M","Gustking/wav2vec2-large-xlsr, deepfake-FT (SSL)","16.0%","+1.21"],
  ["DistilHuBERT","Om-Parab/distilhubert-FT-in-the-wild (SSL)","24.9%","+2.22"],
  ["LFCC+CQCC head","LogisticRegressionNP(89), RawBoost+codec aug","26.6%","+2.10"],
  ["Acoustic-DSP","hand-crafted heuristic (no ML)","47.4%","−0.55"],
  ["Deepfake-V2","MelodyMachine wav2vec2-base (SSL)","62.0%","−1.17"]],
 widths=[1.7,3.0,1.2,1.3])
H3("SSL anti-spoofing models (XLS-R, Wav2Vec2, HuBERT) — how they work")
bullet("Self-supervised speech models pre-trained on thousands of hours of raw audio learn rich representations via a transformer encoder (multi-head self-attention over CNN-extracted frames). We use them FROZEN and read a fine-tuned deepfake-classification head.")
bullet("XLS-R is the multilingual variant (128 languages) — critical for Indic speech; that's why it carries the largest positive SSL weight. Wav2Vec2-base (Deepfake-V2) proved weak on our held-out data (62% EER) and earned a negative weight.")
bullet("Why frozen? Fine-tuning 300M-param SSL models needs GPUs and risks overfitting our small set. Freezing them and learning a cheap stacker is the honest, reproducible, low-compute choice — and it generalises (held-out 5.9%).")
H3("The LFCC+CQCC fusion head")
para("A LogisticRegressionNP over the full 89-dim vector (b=−0.512). The name is a label — it sees all 89 features, not only LFCC/CQCC. It is the interpretable, codec-hardened classical detector and carries a large +2.10 weight.")
H3("Acoustic-DSP")
para("No ML at all: fake_prob = 0.34·hf + 0.24·phase + 0.24·prosody + 0.18·breath, from the scalar cues. Always-available fallback (the system runs even without torch/transformers). Weak alone (47% EER, w=−0.55) but contributes as a contrarian feature.")
H3("Supporting models")
bullet("Whisper (language-ID base; digit-ASR base.en→tiny.en; scam-ASR small) — transcription for liveness content-check and scam-intent. Silero VAD gates Whisper so it can't hallucinate digits on silence (arXiv 2501.11378).",color=DARK)
bullet("ECAPA-TDNN (speechbrain/spkrec-ecapa-voxceleb) — a 192-D speaker embedding. Answers identity (cosine ≥0.18 vs enrolled) AND, combined with the ensemble, liveness → VERIFIED / REJECTED-CLONE / REJECTED-IDENTITY. Also powers fraud-ring linkage across the 8 kHz codec.")
H3("Roadmap models (NOT deployed)")
bullet("Fine-tuned XLS-R+AASIST Indic anti-spoof head (1.2 GB, exists locally, gitignored, not baked into Docker) — the path to full Indic recall. Cite 42→82% routed as the real number; the '100% held-out Indic-synthetic' figure has no committed artifact.",color=AMBER)

# ============================================================ 5. META-LEARNING
H1("Section 5 · Meta-Learning & Calibration (the math)")
eli5("Averaging five opinions treats a fool and an expert equally. Stacking learns a weight for each opinion from data — and can give a consistently-wrong voice a negative weight, so its 'fake' vote actually pushes toward 'real'.")
H3("Ensemble methods, and why stacking wins")
bullet("Hard voting: majority of yes/no. Soft voting: average of probabilities. Both are fixed and equal-weight.")
bullet("Stacking: a meta-model learns weights on the base scores from a held-out split. Empirically: best single = 16.0% EER, naive average = 19.1% (WORSE than the best single!), learned stacker = 5.9%. Only learning-to-trust beats both.")
H3("The logistic meta-stacker — derivation")
para("Base scores x = [s1..s5] are standardized xn=(x−μ)/sd, then:")
eq("p_stack = σ(w·xn + b),   σ(z)=1/(1+e^(−z))")
para("Learned parameters: w = [−0.55, −1.17, +1.21, +2.22, +2.10], b = +0.134. Trained by minimising log-loss (binary cross-entropy):")
eq("L = −Σ [ y·log p + (1−y)·log(1−p) ]")
eq("∂L/∂w = Σ (p − y)·xn      (gradient descent)")
para("A negative wᵢ means detector i is anti-correlated with truth on our data — its 'fake' score is evidence of 'real'. Keeping it is strictly better than deleting it because the stacker extracts that anti-signal.")
H3("Platt calibration — derivation")
para("Raw stacker logits aren't probabilities. Platt scaling fits a 1-D logistic on the scores:")
eq("p_cal = σ(a·s + b),   fit (a,b) by log-loss on held-out")
para("Deployed stacker calibrator: a=6.446, b=−3.151. Effect measured by ECE/Brier below. (Honest note: calibration reshaped reliability but did not lower ECE vs raw — 0.031→0.044 — so we claim 'roughly trustworthy', not 'perfectly calibrated'.)")
H3("The recall-floor gate")
para("A tested override: if max(distilhubert, xlsr) ≥ 0.90 AND the LFCC/CQCC head ≥ 0.5, floor the final score to ≥ 0.70. This protects recall when the two most-trusted detectors are both highly confident — a deliberate precision/recall lever.")
H3("Closed-form SHAP (exact, not sampled)")
para("Because the head is linear-in-logit, Shapley values have a closed form — no sampling, no `shap` library:")
eq("φᵢ = (wᵢ / sdᵢ) · (xᵢ − μᵢ)   [logit space]")
para("Base value = intercept b; Σφᵢ = final_logit − base_logit exactly. Every verdict ships per-detector contributions that provably sum to the decision — this is the explainability a bank auditor can check.")
H3("Metric definitions (know these cold)")
table(["Metric","Definition","VoxShield value"],
 [["EER","threshold where FAR=FRR","5.9%"],
  ["ROC-AUC","P(score_fake > score_real)","0.983"],
  ["t-DCF","cost-weighted detection cost (ASVspoof)","0.252 (min)"],
  ["ECE","Σ over bins |acc−conf|·nᵦ/N","0.044"],
  ["Brier","mean (p − y)²","0.048"],
  ["Precision/Recall/F1","TP/(TP+FP) · TP/(TP+FN) · harmonic mean","93.5 / 92.9 / 0.93"]],
 widths=[1.5,3.6,1.6])

# ============================================================ 6. STREAMING
H1("Section 6 · Streaming Architecture")
eli5("We don't wait for the call to end. Every second we take the last 3 seconds of audio, score it, and average the last three scores. The moment that average crosses the alarm line, we flag — usually 3 seconds in.")
H3("Sliding windows & hop")
bullet("stream_analyze: 3.0 s window, 1.0 s hop, threshold 0.70, max 10 s. running = mean(last 3 window scores). fast-flag if any single window ≥ 0.85.")
bullet("Why 3 s window? Enough context for the SSL models to be reliable; the feature bank (pyin, CQT) needs ~seconds. Shorter → noisier scores; longer → slower first verdict.")
bullet("Why 1 s hop? A fresh verdict every second (good UX/latency) without re-scoring too aggressively. Tradeoff: smaller hop = more compute per second.")
bullet("The /api/live-call SSE path uses a 2.5 s window (faster first verdict for the live demo).")
H3("Measured latency")
para("Time-to-flag = 3.0 s on 5/5 clone clips ≥3 s (the first full window), all within the 10 s design target. Per-analysis compute: GPU sub-second; commodity CPU 3–8 s. The flag is gated on audio-time evidence, not on compute — on CPU the wall-clock trails real-time but the demo clips still decide at the first window.")
H3("Inference plumbing (real vs would-be)")
bullet("REAL: FastAPI async handlers; run_in_threadpool offloads blocking ML off the event loop; per-request ThreadPoolExecutor runs the 5 detectors concurrently (torch releases the GIL).",color=DARK)
bullet("ABSENT today: GPU batching (clips scored one at a time, no batch_size, no device placement), WebSocket audio streaming (WS only relays WebRTC signaling), message queues.",color=AMBER)

# ============================================================ 7. BACKEND
H1("Section 7 · Backend Architecture (REAL vs how-it-would-scale)")
H3("What exists today (REAL)")
bullet("Single FastAPI app (app.py, v3.0.0), ~30 REST endpoints + one SSE (/api/live-call) + one WebSocket (/ws/call signaling).")
bullet("Launched as a SINGLE uvicorn process (run_voxshield.sh — no --workers; auto-restarts on OOM). Docker: python:3.10-slim, CPU torch, bakes 4 models into HF_HOME, EXPOSE 7860.")
bullet("VPS: deploy_vps.sh → systemd service (127.0.0.1:8000, Restart=always) + Caddy reverse proxy on :80. Adds 4 GB swap if RAM<6 GB.")
bullet("State: 100% in-memory Python (AUDIT, _ENROLLED, ACTIONS, BLACKLIST, CHALLENGES, ROOMS, _RING). SHA-256 audit hash truncated to 16 hex chars. Lost on restart, not shared across workers.")
H3("What the deck shows but the code does NOT have (SLIDEWARE)")
table(["Claimed","Reality"],
 [["Kubernetes / autoscaling / load balancer","None. Single process. (Design only.)"],
  ["Redis / Kafka / RabbitMQ / message queue","None anywhere in repo."],
  ["Database (Postgres/SQLite/…)","None. All state in RAM."],
  ["JWT / OAuth / API keys / RBAC / CORS","None. All endpoints open & unauthenticated."],
  ["AES-256 at rest / TLS 1.3 / HSM / SIEM / SOC2 / Zero-Trust","None in code (copy says 'AES-256-ready'). Only self-signed HTTPS for a LAN demo + optional Caddy auto-TLS."],
  ["Immutable audit trail","Mutable in-RAM list, no signing/chaining/persistence."],
  ["CI/CD, automated test suite","No .github/, no pytest suite (only ad-hoc scripts)."],
  ["Air-gapped deployment","Not actually documented/supported; VPS path targets a public box."]],
 widths=[3.0,3.7])
H3("How a FAANG team would build it (the target architecture)")
mono(
"  [Client/IVR/SIP] → [API Gateway: authN/Z, API keys, rate-limit]\n"
"        → [L7 Load Balancer] → [K8s: N stateless FastAPI pods (HPA on QPS/GPU%)]\n"
"        → detector calls batched on a [GPU inference service (Triton/TorchServe, dynamic batching)]\n"
"        → [Redis] hot state (challenges, sessions) · [Kafka] async audit/events\n"
"        → [Postgres + object store] signed, chained, encrypted audit ledger\n"
"        → [Prometheus/Grafana + SIEM] metrics, alerts, security telemetry")
para("None of the middle tier exists yet — it is the TRL-6/7 hardening plan (§15). The current single-process design is honest for a TRL-5 demo; production needs auth, persistence, batching, and horizontal scale.",italic=True,color=GREY)

# ============================================================ 8. BANKING
H1("Section 8 · Banking Integration")
eli5("VoxShield is a smoke detector, not a door lock. It tells the fraud team 'this call smells fake'; a human decides what to do. It never freezes your account by itself.")
H3("How a PSU bank wires it in")
bullet("Telephony/IVR/SIP trunk → the call audio (or a recorded segment) is POSTed to /api/analyze or streamed via /api/stream-analyze.")
bullet("The risk score feeds the existing fraud engine alongside CNAP (caller-name), caller-ID, and device signals — VoxShield is one signal among several, not the sole arbiter.")
bullet("HIGH → step-up verification (OTP, security questions, agent callback) inside the bank's current workflow. Never auto-block — this is the RBI-friendly, customer-fairness posture.")
bullet("Agent desktop / fraud desk shows the verdict + reason codes + spectrogram; operator actions logged via /api/action.")
H3("Why banks never auto-block")
para("A false positive that freezes a genuine customer is a regulatory and reputational disaster (and at 6% Indic FP, common enough to matter). Anti-spoofing is a layered signal, not a judge. This also aligns with DPDP's 'no solely-automated decision' expectation.")
H3("RBI & DPDP alignment (by design, not certified)")
table(["Requirement","VoxShield design fact"],
 [["Data minimisation / retention (DPDP §8)","Audio → one score, discarded; only SHA-256 hash kept."],
  ["No solely-automated adverse decision","Never auto-blocks; human step-up always."],
  ["Data localisation","On-prem/self-host path (VPS/Docker) keeps data on bank infra."],
  ["Transparency / right to explanation","Reason codes + /api/why-fusion + exact SHAP."],
  ["Accountability / audit","SHA-256 audit + action log (needs real persistence — roadmap)."]],
 widths=[2.9,3.8])
para("Honest caveat: true localisation/air-gap and an immutable, encrypted, persisted audit trail are NOT implemented yet — they are the compliance-hardening items in §15. Present DPDP as 'aligned by design', never 'certified'.",italic=True,color=AMBER)

# ============================================================ 9. SECURITY
H1("Section 9 · Cybersecurity & Threat Model")
H3("Threat model — attacker capabilities")
table(["Attack","VoxShield defence","Status"],
 [["Replay (play a clone through a speaker)","Liveness challenge-response (random digits)","REAL"],
  ["Real-time TTS answering the challenge","Ensemble scores the reply → fails liveness","REAL"],
  ["Human relay of the challenge","Timing window (TTL 45 s)","REAL"],
  ["Voice conversion / TTS clone","5-detector fusion + calibration","REAL (codec-robust)"],
  ["Benign DSP evasion (pitch/tempo/noise)","— degrades detection +25..+49 pts","WEAK (top gap)"],
  ["White-box adversarial (FGSM/PGD)","— not covered","ROADMAP"],
  ["API abuse / scraping / model extraction","— no auth/rate-limit today","ABSENT"],
  ["Model poisoning","frozen public models, no online training","N/A (mitigated by design)"]],
 widths=[2.4,2.9,1.4])
H3("Adversarial ML primer")
bullet("FGSM: one-step perturbation x' = x + ε·sign(∇ₓL) — imperceptible audio change that flips the score. PGD: iterative FGSM, stronger. Both are white-box (need model gradients). Our self-test covers signal-level + channel robustness (reproducible); FGSM/PGD is stated roadmap, not claimed.")
bullet("Why pitch/noise/tempo hurt but codecs don't: we trained with codec augmentation (so Opus/G.711/MP3 are in-distribution — Opus even improves to 2.5% EER) but NOT with pitch/tempo/noise augmentation, so those are out-of-distribution. The fix is matched augmentation — a known, concrete lever.")
H3("Crypto & access control — REAL vs SLIDEWARE")
bullet("REAL: SHA-256 audio fingerprint (truncated 16 hex). Self-signed HTTPS for the LAN WebRTC demo. Path-traversal guard on /clips.",color=DARK)
bullet("ABSENT (deck-only): JWT/OAuth/API-keys, rate-limiting, RBAC, CORS, AES-256 at rest, TLS 1.3 pinning, HSM, SIEM, SOC2, Zero-Trust. These are the security-hardening backlog — a production bank deployment cannot ship without them.",color=RED)
para("SHA-256 (hashing) proves audit integrity of a clip's identity; AES-256 (encryption) would protect data at rest — the deck conflates 'AES-256-ready' with implemented. Be precise: hashing is real, encryption is not.",italic=True,color=GREY)

# ============================================================ 10. SCALABILITY
H1("Section 10 · Scalability — 1 → 1,000,000 Concurrent Calls")
para("Scenario: a national bank routes live-call screening through VoxShield. How the architecture must evolve (today it is a single process — this is the plan, honestly labelled).")
table(["Scale","What runs","What breaks / must change","Cost driver"],
 [["1 call","single uvicorn, CPU 3–8 s/analysis","nothing — demo tier","one box"],
  ["100 concurrent","uvicorn --workers N on one node","in-memory state not shared across workers → need Redis","1 GPU node"],
  ["10,000 concurrent","K8s pods + HPA, GPU inference service w/ dynamic batching","no batching/queue today → build Triton/Kafka; DB for audit","GPU fleet + queue"],
  ["1,000,000 concurrent","multi-region K8s, sharded queue, autoscale, DR/HA","everything stateful must be externalised; single-region SPOF","GPU $$$, egress, ops"]],
 widths=[1.5,2.3,2.4,1.1])
H3("Economics (order-of-magnitude, honest)")
bullet("GPU: batched SSL inference amortises well — a single modern GPU can do hundreds of 3-s windows/s batched. 1M concurrent calls scored every second ≈需 thousands of GPU-seconds/s → a GPU fleet with autoscaling; cost is the dominant line.")
bullet("CPU-only (current): 3–8 s/analysis, no batching — fine for pilots and recorded-traffic screening, not for 1M live streams. GPU + batching is mandatory at scale.")
bullet("Levers to cut cost: ONNX-quantised AASIST-L (roadmap) for cheap CPU streaming; score every 2 s not every 1 s; cascade (cheap DSP gate → SSL only on suspicious windows).")
H3("HA / DR")
para("Stateless pods make horizontal scale and rolling deploys trivial ONCE state is externalised (Redis/DB/object store). Multi-region active-active + queue replication give DR. None of this exists today; it is the TRL-7/8 build.")

# ============================================================ 11. BUSINESS
H1("Section 11 · Business")
H3("Model & pricing")
table(["Stream","Mechanism","Who"],
 [["Enterprise SaaS","per-line / per-seat subscription","banks, BPOs"],
  ["API usage","metered per voice-analysis call","volume buyers"],
  ["On-prem licence","annual, air-gapped self-host","banking, defense"],
  ["Government contracts","citizen-helpline / Digital-India tenders","public sector"],
  ["OEM / white-label","embed in contact-centre/telecom platforms","partners"]],
 widths=[1.8,3.0,1.9])
H3("Margins & GTM")
bullet("Software margins once GPU cost is amortised; on-prem licences are high-margin. Main COGS at scale is GPU inference — controllable via quantisation and cascading.")
bullet("GTM: land a PSU/private-bank fraud-desk pilot on recorded IVR traffic (low risk, TRL-6), prove FP budget on their own data, expand to live screening, then adjacent lines (UPI voice, loan/KYC).")
bullet("Procurement moat: measured Indic fairness + on-prem + explainability are RFP-ready differentiators a wrapped English API cannot answer.")
H3("Market")
para("Beachhead: Indian banking voice fraud (₹19,000 cr digital-arrest scam context). Addressable expansion: telecom anti-vishing, government helplines, insurance claims, healthcare tele-auth, BPO agent-assist, media/legal forensics — the same engine. Reiterate: banking is the only live market (TRL-5); the rest is addressable, not deployed.")

pagebreak()
# ============================================================ 12 & 13. Q&A from JSON
def load_qa(fn):
    path=os.path.join(HERE,fn)
    if not os.path.exists(path): return []
    try:
        data=json.load(open(path))
        return [d for d in data if isinstance(d,dict) and d.get("q") and d.get("a")]
    except Exception as e:
        print("WARN could not load",fn,e); return []

inv=load_qa("investor_qa.json"); jud=load_qa("judge_qa.json")
H1("Section 12 · Investor Questions — %d Answered"%len(inv))
para("Hard questions a YC/Sequoia partner, a banking-fraud expert, and a skeptical CISO buyer would ask — answered honestly, grounded in real numbers.")
for i,d in enumerate(inv,1): qa(d["q"],d["a"],i)
pagebreak()
H1("Section 13 · Judge / Professor Questions — %d Answered"%len(jud))
para("Technical viva questions from an IIT/MIT/Stanford panel and FAANG ML engineers — answered with real math and honest limitations.")
for i,d in enumerate(jud,1): qa(d["q"],d["a"],i)
pagebreak()

# ============================================================ 14. WEAKNESSES
H1("Section 14 · Weaknesses — Brutal Due Diligence")
para("What a hostile YC/Sequoia/Google reviewer would flag. No feelings protected.")
H3("What would get rejected today")
bullet("Benign-DSP evasion: pitch/noise/tempo degrade detection +25..+49 pts. A trivial attacker script defeats detection-only. FIX: matched augmentation + SSL fine-tune; and liveness/intent gate action regardless.","1) ",RED)
bullet("Zero production security: no auth, no rate-limit, no CORS, no encryption at rest, no persistence — the API is open and stateless-in-RAM. FIX: API-gateway + keys + Redis/DB + AES; a 2–3 week hardening sprint, but it is NOT done.","2) ",RED)
bullet("Single process, no batching, CPU-bound: cannot serve live scale today. FIX: GPU inference service + K8s + queue (TRL-7).","3) ",RED)
bullet("Small evaluation sets: n=320 test, 30 clips/language. Directionally honest but not statistically heavy. FIX: scale eval on pilot traffic.","4) ",RED)
bullet("'Wrapper' risk: 3 of 5 detectors are off-the-shelf HF models. The IP is the fusion/calibration/fairness/liveness system, not the base models — must be framed that way. The one differentiated model (XLS-R+AASIST Indic) is not yet deployed.","5) ",RED)
bullet("Deck overclaim surface: Kafka/K8s/SOC2/AES/air-gap/'100% recall' are not real. Any technical DD will catch this — the deck must be reconciled to the code (this handbook is the reconciliation).","6) ",RED)
bullet("Team/market execution: selling to PSU banks is slow, relationship-driven, and procurement-heavy; long sales cycles vs runway.","7) ",RED)
H3("What is genuinely strong")
bullet("Honest, reproducible 5.9% held-out EER with a leakage-controlled protocol.",color=GREEN)
bullet("Measured Indian-language fairness — a real, defensible moat.",color=GREEN)
bullet("Defence-in-depth (liveness + intent) that survives acoustic evasion.",color=GREEN)
bullet("Explainability (exact SHAP, reason codes) — the trust property banks need.",color=GREEN)

# ============================================================ 15. ROADMAP
H1("Section 15 · Roadmap — TRL 5 → 9")
table(["TRL","State","Milestones"],
 [["5 (today)","Validated working system","5-detector fusion 5.9% EER; 10-language fairness; liveness; live-call demo; Docker; SHA-256 audit."],
  ["6 (0–3 mo)","Bank sandbox pilot","Deploy fine-tuned XLS-R+AASIST Indic head; ONNX-quantised AASIST-L for CPU streaming; pilot on recorded IVR; threshold tuning to bank FP budget; add auth + persistence."],
  ["7 (3–6 mo)","Harden for India","Matched augmentation (close pitch/noise gap); GPU inference service + batching; Redis/DB + immutable signed audit; rate-limit + RBAC; concurrency load-tests on bank hardware."],
  ["8 (6–12 mo)","Production pilot in a live line","Multi-worker/K8s; HA/DR; SOC2/ISO27001 controls begin; real on-prem/air-gap package; SIEM integration."],
  ["9 (12+ mo)","Deployed national infrastructure","Multi-region autoscale; FGSM/PGD hardening; continuous retraining pipeline; multi-vertical expansion."]],
 widths=[0.8,1.9,4.0])

# ============================================================ 16. MASTER DOC
H1("Section 16 · Master Reference — REAL vs SLIDEWARE & Reproduction")
H3("The one table to remember")
table(["Capability","Built today?","Note"],
 [["5-detector fusion + calibration + SHAP","YES","meta_fusion.json, exact SHAP"],
  ["Channel-aware thresholds (0.70/0.85)","YES",""],
  ["Liveness (Whisper + Silero VAD + timing)","YES",""],
  ["ECAPA speaker enroll/verify + fraud-ring","YES","in-memory store"],
  ["Digital Arrest Shield (intent+stage+warning)","YES","English/Hindi/Hinglish"],
  ["Source attribution / partial-fake localize","YES","simple 3-class / windowed"],
  ["Docker model-baking (4 models, CPU)","YES","EXPOSE 7860"],
  ["systemd + Caddy VPS deploy","YES",":80 HTTP"],
  ["Auth / rate-limit / CORS / RBAC","NO","open API"],
  ["Database / persistence","NO","all in-RAM"],
  ["AES-256 at rest / TLS1.3 / HSM / SIEM / SOC2 / Zero-Trust","NO","slideware"],
  ["Kafka/Redis/K8s/autoscale/GPU-batch/multi-worker","NO","design only"],
  ["CI/CD, test suite, air-gap","NO","roadmap"],
  ["Fine-tuned XLS-R Indic head deployed","NO","1.2GB local, not baked"]],
 widths=[3.4,1.1,2.2])
H3("Reproduce every number")
bullet("calibration_report.py → meta_eval.json, calibration.json (EER 5.9%, AUC 0.983, ECE 0.044, confusion)")
bullet("eval_languages.py → lang_report.json (per-language FP 11.7%→6.3%)")
bullet("robustness_test.py --per-class 40 → robustness.json (7-condition self-test)")
bullet("latency_trace.py → latency_trace.json (3.0 s time-to-flag)")
bullet("Per-detector scoreboard recomputes from artifacts/meta_scores.csv (800 clips).")
bullet("Run the app: backend/run_voxshield.sh → http://localhost:8000/hub. Model card: backend/MODEL_CARD.md.")
para()
rich([("Final word.  ",True,PURPLE),("VoxShield's honest strength is a reproducible, fair, explainable detection-plus-liveness system at TRL-5. Its honest gaps are production security, persistence, scale, and benign-DSP robustness. This handbook documents both so no reviewer can surprise you with your own system.",False,DARK)])

out=os.path.join(HERE,"..","VoxShield_Engineering_Handbook.docx")
doc.save(out)
print("wrote",os.path.abspath(out),"| investor Q&A:",len(inv),"| judge Q&A:",len(jud))
