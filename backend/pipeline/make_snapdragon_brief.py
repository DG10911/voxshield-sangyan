#!/usr/bin/env python3
"""VoxShield Edge — Brief Project Description (Snapdragon AI Lab). Clean 2-page PDF."""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable,ListFlowable,ListItem,Flowable)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snap_content as C

INK=colors.HexColor("#111418"); RED=colors.HexColor("#EE2737"); REDD=colors.HexColor("#B3121F")
CY=colors.HexColor("#0E7FA6"); GREY=colors.HexColor("#5B6470"); LINE=colors.HexColor("#D3D9E0")
PANEL=colors.HexColor("#F5F6F8"); DARK=colors.HexColor("#0A0E14"); WHITE=colors.white
CW=A4[0]-40*mm
ss=getSampleStyleSheet()
def st(n,**k): k.setdefault("parent",ss["Normal"]); return ParagraphStyle(n,**k)
H=st("h",fontName="Helvetica-Bold",fontSize=12,leading=14,textColor=INK,spaceBefore=10,spaceAfter=4)
BODY=st("b",fontName="Helvetica",fontSize=9.7,leading=13.6,alignment=TA_JUSTIFY,textColor=colors.HexColor("#1A1D21"),spaceAfter=5)
BUL=st("bu",parent=BODY,spaceAfter=2)
SMALL=st("sm",fontName="Helvetica",fontSize=8,leading=11,textColor=GREY)
CELL=st("c",fontName="Helvetica",fontSize=8.4,leading=10.8,textColor=INK)
CELLH=st("ch",fontName="Helvetica-Bold",fontSize=8.5,leading=10.8,textColor=WHITE)
def P(t,s=BODY): return Paragraph(t,s)
def head(t): return Paragraph(f'<font color="#EE2737">▍</font> {t}',H)
def bullets(items): return ListFlowable([ListItem(P(x,BUL),leftIndent=6,value="•") for x in items],bulletType="bullet",leftIndent=12,spaceAfter=6)
def tbl(rows,w):
    data=[[Paragraph(str(c),CELLH if i==0 else CELL) for c in r] for i,r in enumerate(rows)]
    t=Table(data,colWidths=w,hAlign="LEFT")
    cmds=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),
          ("BOX",(0,0),(-1,-1),0.6,colors.HexColor("#B8C2CE")),("BACKGROUND",(0,0),(-1,0),INK),("LINEBELOW",(0,0),(-1,0),1.0,RED)]
    for r in range(1,len(rows)):
        if r%2==0: cmds.append(("BACKGROUND",(0,r),(-1,r),PANEL))
    t.setStyle(TableStyle(cmds)); return t

class Header(Flowable):
    def __init__(self): self.width=CW; self.height=66
    def wrap(self,a,b): return (self.width,self.height)
    def draw(self):
        c=self.canv; c.setFillColor(DARK); c.roundRect(0,0,CW,66,5,fill=1,stroke=0)
        c.setFillColor(RED); c.rect(0,62,CW,4,fill=1,stroke=0)
        c.setFillColor(colors.HexColor("#35C7F2")); c.setFont("Helvetica-Bold",8.5); c.drawString(14,48,C.EVENT.upper())
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",22); c.drawString(13,22,C.TITLE)
        c.setFillColor(colors.HexColor("#B9C2D0")); c.setFont("Helvetica",10); c.drawString(14,9,C.SUB)

def statcards():
    d=[[Paragraph(f'<font color="#EE2737"><b>{b}</b></font>',st("bg",fontName="Helvetica-Bold",fontSize=14,alignment=TA_CENTER)),
        ] for b,_ in C.STATS]
    cells=[]
    for b,l in C.STATS:
        cells.append(Paragraph(f'<b><font color="#EE2737" size="13">{b}</font></b><br/><font color="#5B6470" size="7">{l.replace(chr(10)," ")}</font>',
                     st("sc",alignment=TA_CENTER,leading=10)))
    t=Table([cells],colWidths=[CW/4.0]*4)
    t.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.6,LINE),("INNERGRID",(0,0),(-1,-1),0.6,LINE),
        ("BACKGROUND",(0,0),(-1,-1),PANEL),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return t

E=[Header(),Spacer(1,8),
  P(f"<b>{C.ONELINE}</b>",st("vp",fontName="Helvetica",fontSize=11,leading=15,textColor=INK,alignment=TA_CENTER)),
  Spacer(1,7), statcards(), Spacer(1,4),
  P(f"Individual submission · {C.AUTHOR} · GitHub: DG10911/voxshield",SMALL),
  HRFlowable(width="100%",thickness=0.6,color=LINE,spaceBefore=4,spaceAfter=4),

  head("Problem"),
  P(C.SLIDES[1][2]['body']+" A verdict after the call ends is forensics, not protection — and sensitive customer "
    "call audio should not be shipped to a foreign cloud."),

  head("Solution — VoxShield Edge"),
  P("VoxShield Edge is an <b>on-device, Indic-first, telephony-hardened</b> voice-deepfake detector for banking. "
    "Given a live call it returns a calibrated <b>LOW / MEDIUM / HIGH</b> risk verdict with explainable reason codes — "
    "decision support for a fraud analyst, <b>never automatic blocking</b>. It runs entirely on a Snapdragon-powered "
    "HP laptop, so raw call audio never leaves the device."),

  head("Technical implementation"),
  P("A streaming pipeline: 8&nbsp;kHz G.711 telephony audio → Silero VAD → 3&nbsp;s windows at a 1&nbsp;s hop → an "
    "89-dimensional acoustic feature bank (computed at a 16&nbsp;kHz analysis rate) → <b>five complementary detectors</b> "
    "(Acoustic&nbsp;DSP · wav2vec2 · XLS-R&nbsp;300M · DistilHuBERT · LFCC+CQCC) → a <b>learned meta-stacker</b> with "
    "Indic / telephony routing → Platt-calibrated risk + per-signal reason codes (spectral, phase, prosody, breath)."),

  head("Snapdragon optimisation &amp; on-device deployment"),
  P("VoxShield Edge is built to run on the Snapdragon Hexagon NPU (45&nbsp;TOPS on Snapdragon&nbsp;X&nbsp;Elite/Plus, "
    "80&nbsp;TOPS on X2&nbsp;Elite). The on-device path: <b>PyTorch → ONNX (INT8-quantised) → ONNX&nbsp;Runtime with the "
    "QNN Execution Provider (onnxruntime-qnn) → Hexagon NPU</b>, packaged as a Windows/ARM64 app. Models are compiled and "
    "profiled on real Snapdragon devices via <b>Qualcomm AI&nbsp;Hub (qai-hub)</b>, and the design leverages the AI&nbsp;Hub "
    "speech ecosystem — <b>WavLM-Base-Plus</b> (a self-supervised speech backbone) and <b>Whisper</b> for on-device "
    "transcription. <b>Honest status:</b> the detector runs today on CPU/GPU; the NPU port and INT8 quantisation via "
    "AI&nbsp;Hub are the optimisation in progress — no on-NPU latency is claimed until measured."),

  head("Evidence (measured, honestly scoped)"),
  tbl([["Model / setting","Evaluation","Metric","Result"],
       ["Deployed fusion","held-out In-the-Wild","EER","5.9%"],
       ["Unseen-generator deepfakes","MLAAD (out-of-distribution)","EER / AUC","6.8% / 0.98"],
       ["Detector scoreboard","same eval set","EER single/avg/fusion","16.0 / 19.1 / 5.9"],
       ["Indic recall","MMS-TTS fakes (after retrain)","recall","42% → 82%"]],
      [42*mm,52*mm,44*mm,32*mm]),
  P("EER (Equal Error Rate) is not accuracy; in-corpus and out-of-distribution figures are reported separately and "
    "never conflated. The 6.8% EER on unseen generators is the honest cross-generator generalisation result.",SMALL),

  head("Innovation, accessibility &amp; impact"),
  bullets([
    "<b>Innovation:</b> the integration under one hard constraint set — Indic language + narrowband telephony + on-device NPU + explainable + private — not a single new algorithm.",
    "<b>Accessibility:</b> offline, low-power on the NPU, works in poorly-connected branches; no cloud cost per call.",
    "<b>Privacy:</b> no raw-audio egress — architected to support institutional data-governance requirements.",
    "<b>Impact:</b> a private, on-device fraud-screening layer any bank can run on a Snapdragon laptop.",
  ]),
  HRFlowable(width="100%",thickness=0.6,color=LINE,spaceBefore=4,spaceAfter=4),
  P("GitHub: DG10911/voxshield · Pitch deck (PDF + PPTX) submitted separately · Contact: devanshgoenka03@gmail.com",SMALL),
]
OUT="VOXSHIELD_SNAPDRAGON_BRIEF.pdf"
SimpleDocTemplate(OUT,pagesize=A4,topMargin=15*mm,bottomMargin=15*mm,leftMargin=20*mm,rightMargin=20*mm,
                  title="VoxShield Edge — Brief Project Description",author=C.AUTHOR).build(E)
print("wrote",OUT)
