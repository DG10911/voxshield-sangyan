#!/usr/bin/env python3
"""VoxShield — ONE-PAGE technical brief for Prof. H. A. Patil (the promised 1-pager)."""
import os,sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable,ListFlowable,ListItem)
INK=colors.HexColor("#111418"); RED=colors.HexColor("#B01326"); REDD=colors.HexColor("#7C0D1B")
RTINT=colors.HexColor("#FBEDEF"); GREY=colors.HexColor("#5B6470"); LGREY=colors.HexColor("#9AA3AE")
PANEL=colors.HexColor("#F4F6F8"); LINEC=colors.HexColor("#D3D9E0"); WHITE=colors.white
CW=A4[0]-36*mm
ss=getSampleStyleSheet()
def st(n,**k): k.setdefault("parent",ss["Normal"]); return ParagraphStyle(n,**k)
TITLE=st("t",fontName="Helvetica-Bold",fontSize=18,leading=20,textColor=INK,alignment=TA_CENTER)
SUBT =st("s",fontName="Helvetica",fontSize=9.5,leading=12.5,textColor=GREY,alignment=TA_CENTER)
KICK =st("k",fontName="Helvetica-Bold",fontSize=7.6,leading=10,textColor=RED,alignment=TA_CENTER,spaceAfter=1)
H    =st("h",fontName="Helvetica-Bold",fontSize=9.8,leading=12,textColor=REDD,spaceBefore=6,spaceAfter=2)
BODY =st("b",fontName="Helvetica",fontSize=8.6,leading=11.6,alignment=TA_JUSTIFY,textColor=colors.HexColor("#1A1D21"),spaceAfter=3)
BUL  =st("bu",parent=BODY,spaceAfter=1)
CELL =st("c",fontName="Helvetica",fontSize=7.7,leading=9.8,textColor=INK)
CELLH=st("ch",fontName="Helvetica-Bold",fontSize=7.7,leading=9.8,textColor=WHITE)
SMALL=st("sm",fontName="Helvetica",fontSize=7.2,leading=9.4,textColor=GREY)
def P(t,s=BODY): return Paragraph(t,s)
def bullets(items,s=BUL): return ListFlowable([ListItem(P(x,s),leftIndent=5,value="•") for x in items],bulletType="bullet",leftIndent=11,spaceAfter=2)
def tbl(rows,widths):
    data=[[Paragraph(str(c),CELLH if i==0 else CELL) for c in r] for i,r in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign="LEFT")
    cmds=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
          ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("LINEBELOW",(0,0),(-1,-1),0.4,LINEC),
          ("BOX",(0,0),(-1,-1),0.6,LGREY),("BACKGROUND",(0,0),(-1,0),INK),("LINEBELOW",(0,0),(-1,0),1.0,RED)]
    for r in range(1,len(rows)):
        if r%2==0: cmds.append(("BACKGROUND",(0,r),(-1,r),PANEL))
    t.setStyle(TableStyle(cmds)); return t
def callout(title,body):
    inner=[Paragraph(f'<b><font color="#7C0D1B">{title}</font></b>',st("co",fontName="Helvetica-Bold",fontSize=8,leading=10.5)),
           Paragraph(body,st("cob",fontName="Helvetica",fontSize=8,leading=10.8,textColor=INK))]
    t=Table([[inner]],colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),RTINT),("BOX",(0,0),(-1,-1),1,RED),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return t

E=[P("TECHNICAL RESEARCH BRIEF (1-PAGE) · FOR PROF. HEMANT A. PATIL, DA-IICT",KICK),
   P("VoxShield",TITLE),
   P("Indic-Language Voice-Deepfake Detection under Telephony Conditions — an early-stage research prototype",SUBT),
   Spacer(1,5),
   callout("Current status — early-stage prototype.",
     "We treat the numbers below as evidence to stress-test, not production claims. We would value your view on whether "
     "our evaluation methodology is rigorous enough — especially cross-generator generalisation and telephony/codec robustness."),
   Spacer(1,4),
   P("System (implemented).",H),
   P("8 kHz G.711 μ-law → Silero VAD → 3 s window / 1 s hop → <b>five complementary detectors</b> (Acoustic DSP · wav2vec2 · "
     "XLS-R 300M · DistilHuBERT · LFCC+CQCC) over an 89-dim feature bank at a 16 kHz analysis rate (group-delay phase, prosody, and a &gt;6 kHz band that is empty under 8 kHz telephony) → "
     "<b>learned meta-fusion</b> → Indic/telephony/general routing → Platt calibration → LOW/MEDIUM/HIGH + reason codes. "
     "Decision-support for a fraud workflow; never auto-blocks."),
   P("Strongest measured results (with scope).",H),
   tbl([["Result","Value","Evaluation scope"],
        ["Meta-fusion EER","5.9%","held-out In-the-Wild (cross-dataset)"],
        ["Best single detector / naive avg.","16.0% / 19.1% EER","same set — fusion beats both"],
        ["Indic fake recall","42% → 82%","MMS-TTS fakes; English EER unchanged (5.9%)"],
        ["Genuine-Indic false-positive rate","36.3% → 6.3%","tested Indic conditions; channel-aware"],
        ["ROC-AUC · calibration","0.983 · ECE 0.044","held-out; calibration distribution"]],
       [54*mm,32*mm,88*mm]),
   P("EER is not accuracy; Indic recall is not overall recall. Telephony results are on augmented narrowband, not captured "
     "PSTN/SIP; speaker-overlap and generator-disjoint testing are not yet documented.",SMALL),
   P("Where your expertise would most help.",H),
   bullets([
     "<b>Cross-generator generalisation</b> — our Indic evidence uses one generator (MMS-TTS). Is train-A/B/C → test-unseen-D/E (EER, AUC, TPR@FPR, per-generator) the right benchmark? [connects to your ASVspoof-generalisation survey]",
     "<b>Telephony/codec protocol</b> — clean→codec, a codec→noise→packet-loss cascade, or real captured calls? What baselines? [your replay / instantaneous-frequency feature work]",
     "<b>Generator × codec</b> — could the model learn codec rather than synthesis artifacts? How would you separate them?",
     "<b>Speaker disjointness</b> — should speaker- and generator-disjoint be the principal benchmark?",
     "<b>Metrics</b> — EER / AUC / TPR@1% FPR / t-DCF: which matter most for fraud screening?",
   ]),
   Spacer(1,3),
   callout("What we'd value (low-friction).",
     "Is our evaluation methodology sound? What would you change to establish cross-generator generalisation? Which failure "
     "mode should we test first? A detailed 6-page brief (methodology, figures, roadmap) is available if useful."),
   Spacer(1,4),
   P("Thank you for your time.  <b>Team DigiSeva · VoxShield · GBT BuildStorm 2026</b>  ·  devanshgoenka03@gmail.com  ·  GitHub: DG10911/voxshield",SMALL)]

def deco(c,doc):
    c.saveState(); c.setFillColor(RED); c.rect(0,A4[1]-6,A4[0],6,fill=1,stroke=0); c.restoreState()
OUT="VOXSHIELD_PATIL_ONEPAGER.pdf"
SimpleDocTemplate(OUT,pagesize=A4,topMargin=14*mm,bottomMargin=12*mm,leftMargin=18*mm,rightMargin=18*mm,
    title="VoxShield — 1-page brief (Prof. H. A. Patil)",author="Team DigiSeva").build(E,onFirstPage=deco,onLaterPages=deco)
print("wrote",OUT)
