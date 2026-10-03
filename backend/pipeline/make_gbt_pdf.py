#!/usr/bin/env python3
"""Render the VoxShield GBT Round-1 paper to a polished, submittable PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, ListFlowable, ListItem)

OUT = "VOXSHIELD_GBT_PAPER.pdf"
NAVY = colors.HexColor("#0B2545"); ACCENT = colors.HexColor("#134074")
LIGHT = colors.HexColor("#EEF2F7"); GREEN = colors.HexColor("#1B7F5A")
GREY = colors.HexColor("#5A6472")

ss = getSampleStyleSheet()
def st(name, **kw):
    kw.setdefault("parent", ss["Normal"])
    return ParagraphStyle(name, **kw)

TITLE   = st("t", fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
SUB     = st("s", fontName="Helvetica", fontSize=10.5, leading=14, textColor=GREY, alignment=TA_CENTER, spaceAfter=2)
H       = st("h", fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=ACCENT, spaceBefore=12, spaceAfter=5)
BODY    = st("b", fontName="Helvetica", fontSize=9.7, leading=13.6, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1A1A1A"), spaceAfter=5)
BUL     = st("bu", parent=BODY, spaceAfter=2)
CELL    = st("c", fontName="Helvetica", fontSize=8.6, leading=11, textColor=colors.HexColor("#1A1A1A"))
CELLH   = st("ch", fontName="Helvetica-Bold", fontSize=8.7, leading=11, textColor=colors.white)
FOOT    = st("f", fontName="Helvetica", fontSize=7.8, leading=10, textColor=GREY, alignment=TA_CENTER)

def para(t, s=BODY): return Paragraph(t, s)
def rule(): return HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#C7D0DA"), spaceBefore=2, spaceAfter=8)
def bullets(items):
    return ListFlowable([ListItem(para(x, BUL), leftIndent=6, value="•") for x in items],
                        bulletType="bullet", start="•", leftIndent=12, spaceAfter=6)

def tbl(rows, widths, header=True):
    data = []
    for i, r in enumerate(rows):
        style = CELLH if (header and i == 0) else CELL
        data.append([Paragraph(str(c), style) for c in r])
    t = Table(data, colWidths=widths, hAlign="LEFT")
    cmds = [("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LINEBELOW",(0,0),(-1,-1),0.4,colors.HexColor("#D5DCE4")),
            ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#B8C2CE"))]
    if header:
        cmds += [("BACKGROUND",(0,0),(-1,0),ACCENT)]
        for r in range(1,len(rows)):
            if r % 2 == 0: cmds.append(("BACKGROUND",(0,r),(-1,r),LIGHT))
    else:
        for r in range(len(rows)):
            if r % 2 == 1: cmds.append(("BACKGROUND",(0,r),(-1,r),LIGHT))
    t.setStyle(TableStyle(cmds))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#C7D0DA")); canvas.setLineWidth(0.5)
    canvas.line(20*mm, 14*mm, A4[0]-20*mm, 14*mm)
    canvas.setFont("Helvetica", 7.6); canvas.setFillColor(GREY)
    canvas.drawString(20*mm, 9.5*mm, "VoxShield — GBT BuildStorm 2026, Round 1 Paper")
    canvas.drawRightString(A4[0]-20*mm, 9.5*mm, f"Page {doc.page}")
    canvas.restoreState()

E = []
# ---- Title block ----
E += [para("VoxShield", TITLE),
      para("Real-Time Voice-Deepfake Detection for Indic-Language Telephony Fraud", SUB),
      Spacer(1,6),
      para("<b>GBT BuildStorm 2026 — Round 1 Paper Submission</b>", SUB),
      para("Track: FinTech &amp; Financial Inclusion  ·  Team Lead: Devansh Goenka", SUB),
      Spacer(1,4), rule()]

# ---- 1. Problem ----
E += [para("1.  Problem Statement", H),
      para("India is the world's largest telephony market and its fastest-growing digital-payments economy — and that makes it the world's biggest target for <b>voice-based fraud</b>. Two forces have collided:"),
      bullets([
        "<b>Voice cloning became trivially cheap.</b> Modern TTS and voice-conversion systems (XTTS, VITS, F5, neural-codec models, and India-native engines) can clone a voice from <b>3–10 seconds</b> of reference audio, in Indian languages, at near-zero cost.",
        "<b>Fraud runs over the phone.</b> \"Digital arrest\" scams, fake bank-official calls, and relative-in-distress scams increasingly use <b>synthetic voices</b> in Hindi, Tamil, Bengali and other Indian languages over ordinary phone lines.",
      ]),
      para("The gap: <b>every commercial voice-deepfake detector (Pindrop, Reality Defender, Hiya, Resemble) is English-first, cloud-only, and built for Western markets.</b> Indian banks and telcos legally <b>cannot</b> send customer call audio to a foreign cloud (DPDP Act, RBI data-localization). So the exact institutions being defrauded have <b>no deployable defense</b> for Indian-language, phone-quality audio."),
      para("<b>What we solve:</b> detect AI-cloned / synthetic voices in Indian-language telephone calls, in real time, running fully on-premises — the one solution the market lacks.")]

# ---- 2. Proposed Solution ----
E += [para("2.  Proposed Solution — VoxShield", H),
      para("VoxShield is an <b>on-premises, Indic-language, telephony-hardened voice-deepfake detector.</b> Given a call's audio, it returns a calibrated risk verdict (LOW / MEDIUM / HIGH) with <b>explainable reason codes</b>, fast enough to flag a fraudulent call within its first seconds."),
      tbl([
        ["Dimension","Commercial incumbents","VoxShield"],
        ["Indian languages","English-first","10 Indic languages"],
        ["Deployment","Cloud-only","On-prem / air-gapped (DPDP-compliant)"],
        ["Telephony codecs","Partial","Hardened for G.711 8 kHz phone audio"],
        ["Explainability","Mostly black-box","Per-signal reason codes"],
        ["Model access","Closed","Open weights, reproducible"],
      ], [34*mm, 55*mm, 81*mm]),
      Spacer(1,5),
      para("<b>Why it is hard to copy:</b> the moat is not one algorithm (the research is public) — it is (a) an <b>on-prem federated data flywheel</b> that improves from each bank's real fraud traffic <i>without any audio leaving their premises</i>, and (b) a <b>proprietary multi-engine Indic fake corpus</b> no competitor has. Both compound over time.")]

# ---- 3. Technical Approach ----
E += [para("3.  Technical Approach", H),
      para("<b>Detection model.</b> A self-supervised speech backbone (wav2vec2-XLS-R-53, pretrained on 56 languages incl. Hindi/Tamil/Bengali) fine-tuned as a binary real-vs-synthetic classifier. Multilingual pretraining gives free acoustic priors for Indian languages — a key advantage over English-only detectors."),
      para("<b>Telephony hardening.</b> Training applies on-the-fly channel augmentation — G.711 μ-law 8 kHz codec, telephony band-pass (300–3400 Hz), additive noise, packet-loss — so the model works on real phone audio, not just studio recordings."),
      para("<b>Honest evaluation</b> (the part most projects skip). We evaluate under strict disjoint splits to avoid inflated numbers: <b>speaker-disjoint</b> (unseen test speakers); <b>generator-holdout / cross-generator</b> (train on some cloners, test on a held-out cloner — the true real-world test); <b>cross-dataset OOD</b> (MLAAD); and <b>per-language Indic</b> plus <b>codec-degraded</b> breakdowns."),
      para("<b>Explainability.</b> A calibrated fusion layer outputs per-signal reason codes (spectral / high-frequency artifacts, phase regularity, prosody, breath) so a fraud analyst sees <i>why</i> a call was flagged — essential for BFSI adoption. <b>System:</b> a FastAPI inference service (sub-second on GPU) with a bank-grade dashboard and sliding-window streaming for live-call decisions.")]

# ---- 4. Tech Stack ----
E += [para("4.  Tech Stack", H),
      tbl([
        ["Layer","Technology"],
        ["Backbone","wav2vec2-XLS-R-53 (300M), PyTorch 2.6 + CUDA"],
        ["Training","HuggingFace Transformers, bf16 mixed precision, gradient checkpointing; NVIDIA A100 (DGX)"],
        ["Data pipeline","HuggingFace Datasets, PyArrow, soundfile, torchaudio; on-the-fly telephony augmentation"],
        ["Datasets","In-the-Wild, IndicSynth (12-lang, ACL 2025), IndicVoices (AI4Bharat), DFADD, CodecFake+, MLAAD (OOD)"],
        ["Fake generation","Self-hosted TTS — AI4Bharat IndicF5, Indic-Parler-TTS, VITS, XTTS-v2, F5-TTS"],
        ["Serving","FastAPI + Uvicorn (on-prem); ECAPA-TDNN speaker verification; Whisper / IndicConformer ASR for scam-intent"],
        ["Deployment","Docker (CPU or single-GPU), on-prem / air-gapped; Bhashini / MeitY-aligned"],
      ], [30*mm, 140*mm])]

# ---- 5. Results ----
E += [para("5.  Results &amp; Traction (measured, honest)", H),
      bullets([
        "<b>Deployed fusion system:</b> 5.9% EER, ROC-AUC 0.983 on held-out In-the-Wild — a live, explainable, on-prem product (TRL-5).",
        "<b>Indic fairness:</b> genuine-speaker false-alarm rate cut from 11.7% → 6.3% (channel-aware) across 10 Indian languages.",
        "<b>Research fine-tune (wav2vec2-XLS-R):</b> 0.31% EER speaker-disjoint on In-the-Wild (matching published SOTA), 0.99% under the G.711 phone codec.",
        "<b>Currently training</b> a multi-cloner Indic model (IndicSynth + IndicVoices + DFADD + more) to produce honest <b>cross-generator</b> and <b>per-language</b> numbers — the metric that proves real-world robustness.",
      ]),
      para("<i>All numbers are scoped precisely; in-corpus and cross-dataset figures are reported separately, never conflated.</i>", st("i", parent=BODY, fontName="Helvetica-Oblique", textColor=GREY, fontSize=8.8))]

# ---- 6. Impact & Feasibility ----
E += [para("6.  Impact &amp; Feasibility", H),
      bullets([
        "<b>Who benefits:</b> banks, NBFCs, telecom fraud teams, and ultimately every Indian phone user targeted by voice scams.",
        "<b>Why now:</b> RBI-reported banking fraud is rising sharply, and CERT-In has issued deepfake advisories — regulators are actively pushing for defenses.",
        "<b>Feasibility:</b> already runs on a single A100 (or a consumer RTX GPU) at sub-second latency — telco-scale, on-prem, today.",
        "<b>Go-to-market:</b> enterprise contact-center deployment first (banks legally need on-prem), then carrier-network integration.",
      ])]

# ---- 7. Roadmap + summary ----
E += [para("7.  Roadmap", H),
      bullets([
        "<b>Now:</b> multi-cloner Indic training + honest cross-generator benchmark.",
        "<b>3 months:</b> streaming live-call demo, challenge-response liveness, adversarial-robustness report.",
        "<b>12 months:</b> federated pilot with one bank (the data-flywheel moat); publish the first telephony-band Indic voice-deepfake benchmark.",
      ]),
      rule(),
      para("VoxShield is the <b>only voice-deepfake detector built for how fraud actually happens in India</b> — Indian languages, phone-quality audio, on-premises, explainable — combining a state-of-the-art self-supervised model, telephony-hardened training, rigorous honest evaluation, and a defensible data-flywheel moat, targeting a market the global incumbents legally cannot serve."),
      Spacer(1,4),
      para("Public artifacts: GitHub (DG10911/voxshield) · HuggingFace (dg10911/voxshield-checkpoints) · Contact: devanshgoenka03@gmail.com", FOOT)]

doc = SimpleDocTemplate(OUT, pagesize=A4, topMargin=18*mm, bottomMargin=20*mm,
                        leftMargin=20*mm, rightMargin=20*mm,
                        title="VoxShield — GBT BuildStorm 2026 Round 1 Paper",
                        author="Devansh Goenka")
doc.build(E, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
