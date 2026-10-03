#!/usr/bin/env python3
"""VoxShield Edge — Master Technical Submission Document (Snapdragon AI Lab)."""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable,ListFlowable,ListItem,KeepTogether,Flowable,PageBreak)
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
from reportlab.graphics import renderPDF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snap_content as C

INK=colors.HexColor("#12161C"); RED=colors.HexColor("#EE2737"); REDD=colors.HexColor("#B3121F")
CY=colors.HexColor("#0E7FA6"); GREY=colors.HexColor("#5B6470"); LGREY=colors.HexColor("#9AA3AE")
LINE=colors.HexColor("#D3D9E0"); PANEL=colors.HexColor("#F4F6F8"); RTINT=colors.HexColor("#FDECEE")
DARK=colors.HexColor("#0A0E14"); WHITE=colors.white
OKG=colors.HexColor("#1B7F5A"); AMB=colors.HexColor("#B26A00"); BLUE=colors.HexColor("#1553B0")
CW=A4[0]-40*mm
ss=getSampleStyleSheet()
def st(n,**k): k.setdefault("parent",ss["Normal"]); return ParagraphStyle(n,**k)
H1=st("h1",fontName="Helvetica-Bold",fontSize=13,leading=15,textColor=INK,spaceBefore=12,spaceAfter=5)
H2=st("h2",fontName="Helvetica-Bold",fontSize=10.5,leading=13,textColor=REDD,spaceBefore=7,spaceAfter=3)
BODY=st("b",fontName="Helvetica",fontSize=9.5,leading=13.4,alignment=TA_JUSTIFY,textColor=colors.HexColor("#1A1D21"),spaceAfter=5)
BUL=st("bu",parent=BODY,spaceAfter=2)
SMALL=st("sm",fontName="Helvetica",fontSize=8,leading=10.5,textColor=GREY)
CAP=st("cap",fontName="Helvetica-Oblique",fontSize=8,leading=10.5,textColor=GREY,alignment=TA_CENTER,spaceBefore=3,spaceAfter=8)
CELL=st("c",fontName="Helvetica",fontSize=8.1,leading=10.4,textColor=INK)
CELLB=st("cb",fontName="Helvetica-Bold",fontSize=8.1,leading=10.4,textColor=INK)
CELLH=st("ch",fontName="Helvetica-Bold",fontSize=8.2,leading=10.4,textColor=WHITE)
def P(t,s=BODY): return Paragraph(t,s)
def H(t): return Paragraph(t,H1)
def h2(t): return Paragraph(t,H2)
def bullets(items,s=BUL): return ListFlowable([ListItem(P(x,s),leftIndent=6,value="•") for x in items],bulletType="bullet",leftIndent=12,spaceAfter=6)
LBL={'V':('VERIFIED',OKG),'PR':('PROJECT RESULT',BLUE),'IMP':('IMPLEMENTED',OKG),
     'EXP':('EXPERIMENTAL',AMB),'PROP':('PROPOSED',GREY),'TGT':('TARGET',CY),'ILL':('ILLUSTRATIVE',GREY)}
def lbl(code):
    t,c=LBL[code]; return f'<font size="7" color="#{c.hexval()[2:]}"><b>[{t}]</b></font>'
def tbl(rows,w,header=True,boldcols=()):
    data=[]
    for i,r in enumerate(rows):
        row=[Paragraph(str(c),CELLH if(header and i==0) else (CELLB if j in boldcols else CELL)) for j,c in enumerate(r)]
        data.append(row)
    t=Table(data,colWidths=w,hAlign="LEFT")
    cmds=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),
          ("BOX",(0,0),(-1,-1),0.6,colors.HexColor("#B8C2CE"))]
    if header:
        cmds+=[("BACKGROUND",(0,0),(-1,0),INK),("LINEBELOW",(0,0),(-1,0),1.0,RED)]
        for r in range(1,len(rows)):
            if r%2==0: cmds.append(("BACKGROUND",(0,r),(-1,r),PANEL))
    t.setStyle(TableStyle(cmds)); return t
# ---- diagram helpers ----
def _box(d,x,y,w,h,title,sub=None,fill=WHITE,stroke=INK,tc=INK,fs=7.6):
    d.add(Rect(x,y,w,h,rx=3,ry=3,fillColor=fill,strokeColor=stroke,strokeWidth=1))
    if sub:
        d.add(String(x+w/2,y+h/2+2,title,textAnchor="middle",fontName="Helvetica-Bold",fontSize=fs,fillColor=tc))
        d.add(String(x+w/2,y+h/2-7,sub,textAnchor="middle",fontName="Helvetica",fontSize=fs-1.4,fillColor=GREY))
    else:
        d.add(String(x+w/2,y+h/2-3,title,textAnchor="middle",fontName="Helvetica-Bold",fontSize=fs,fillColor=tc))
def _har(d,x0,x1,y,c=RED): d.add(Line(x0,y,x1,y,strokeColor=c,strokeWidth=1.2)); d.add(Polygon([x1-4,y-2.5,x1-4,y+2.5,x1,y],fillColor=c,strokeColor=c))
def _var(d,x,y0,y1,c=RED): d.add(Line(x,y0,x,y1,strokeColor=c,strokeWidth=1.2)); d.add(Polygon([x-2.5,y1+4,x+2.5,y1+4,x,y1],fillColor=c,strokeColor=c))
class Fig(Flowable):
    def __init__(self,d): self.d=d; self.width=d.width; self.height=d.height
    def wrap(self,a,b): return (self.width,self.height)
    def draw(self): renderPDF.draw(self.d,self.canv,0,0)
def fig_pipeline():
    W,Hh=CW,66; d=Drawing(W,Hh)
    steps=[("8kHz G.711","μ-law telephony"),("Silero VAD","speech gate"),("3s / 1s","window·hop"),
           ("89-dim","feature bank"),("5 detectors","ensemble"),("Meta-fusion","learned"),("Risk + why","reason codes")]
    n=len(steps);g=6;bw=(W-(n-1)*g)/n;y=18;bh=40
    for i,(t,s) in enumerate(steps):
        x=i*(bw+g);last=i==n-1
        _box(d,x,y,bw,bh,t,s,fill=RTINT if last else PANEL,stroke=RED if last else INK,tc=REDD if last else INK,fs=7.4)
        if i<n-1:_har(d,x+bw+0.5,x+bw+g-0.5,y+bh/2)
    d.add(String(W/2,6,"Streaming: a verdict forms within the first seconds and refines as the call proceeds",textAnchor="middle",fontName="Helvetica-Oblique",fontSize=7,fillColor=GREY))
    return d
def fig_arch():
    W=CW;bh=24;arr=13;ph=66;top=4;Hh=top+2*bh+ph+3*bh+6*arr+4
    d=Drawing(W,Hh);cx=W/2;bw=190;x=cx-bw/2;cur=[Hh-top]
    def pb(t,s,fl,stk,tc):_box(d,x,cur[0]-bh,bw,bh,t,s,fill=fl,stroke=stk,tc=tc,fs=7.8);cur[0]-=bh
    def ar():_var(d,cx,cur[0]-1,cur[0]-arr+3);cur[0]-=arr
    pb("Call audio","8 kHz G.711 μ-law · on device",PANEL,INK,INK);ar()
    pb("Preprocess","VAD · 3s/1s windows · normalize · 16 kHz",PANEL,INK,INK);ar()
    pw=W-2;px=1;py=cur[0]-ph
    d.add(Rect(px,py,pw,ph,rx=4,ry=4,fillColor=colors.HexColor("#FCFCFD"),strokeColor=RED,strokeWidth=1.1,strokeDashArray=[3,2]))
    d.add(String(px+6,py+ph-11,"FIVE COMPLEMENTARY DETECTORS",fontName="Helvetica-Bold",fontSize=7,fillColor=REDD))
    dets=["Acoustic DSP","wav2vec2","XLS-R 300M","DistilHuBERT","LFCC+CQCC"];dn=len(dets);dg=6;dbw=(pw-12-(dn-1)*dg)/dn;dby=py+8;dbh=34
    for i,nm in enumerate(dets):
        dx=px+6+i*(dbw+dg);d.add(Rect(dx,dby,dbw,dbh,rx=2,ry=2,fillColor=WHITE,strokeColor=INK,strokeWidth=0.8))
        d.add(String(dx+dbw/2,dby+dbh/2-2,nm,textAnchor="middle",fontName="Helvetica-Bold",fontSize=6.8,fillColor=INK))
    cur[0]=py;ar()
    pb("Learned meta-fusion","stacker + Platt calibration",PANEL,INK,INK);ar()
    pb("Router: Indic → telephony → general","language-ID + narrowband aware",RTINT,RED,REDD);ar()
    pb("Risk verdict LOW / MED / HIGH","+ reason codes · never auto-block",RTINT,RED,REDD)
    return d
def fig_edge():
    W,Hh=CW,120;d=Drawing(W,Hh)
    d.add(String(6,Hh-10,"CLOUD DETECTION (typical)",fontName="Helvetica-Bold",fontSize=7.5,fillColor=GREY))
    row=[("Voice",PANEL),("→ Internet",PANEL),("→ Cloud AI",PANEL),("→ Verdict",PANEL)]
    n=len(row);g=8;bw=(W-(n-1)*g)/n;y=Hh-46
    for i,(t,f) in enumerate(row):
        x=i*(bw+g);_box(d,x,y,bw,26,t,fill=f,stroke=LGREY,tc=GREY,fs=8)
        if i<n-1:_har(d,x+bw+1,x+bw+g-1,y+13,c=LGREY)
    d.add(String(W-6,y-8,"audio leaves the device · bandwidth · latency · privacy exposure",textAnchor="end",fontName="Helvetica-Oblique",fontSize=6.8,fillColor=GREY))
    d.add(String(6,42,"VOXSHIELD EDGE (this project)",fontName="Helvetica-Bold",fontSize=7.5,fillColor=REDD))
    row2=[("Voice",RTINT),("→ Snapdragon AI PC",RTINT),("→ Local inference",RTINT),("→ Verdict",RTINT)]
    y2=8
    for i,(t,f) in enumerate(row2):
        x=i*(bw+g);_box(d,x,y2,bw,26,t,fill=f,stroke=RED,tc=REDD,fs=8)
        if i<n-1:_har(d,x+bw+1,x+bw+g-1,y2+13)
    return d
def fig_snap():
    W,Hh=CW,62;d=Drawing(W,Hh)
    steps=[("PyTorch","trained detector"),("ONNX","INT8 quantised"),("ONNX Runtime","QNN EP"),("Hexagon NPU","45–80 TOPS")]
    n=len(steps);g=10;bw=(W-(n-1)*g)/n;y=16;bh=38
    for i,(t,s) in enumerate(steps):
        x=i*(bw+g);last=i==n-1
        _box(d,x,y,bw,bh,t,s,fill=RTINT if last else PANEL,stroke=RED if last else INK,tc=REDD if last else INK,fs=8.2)
        if i<n-1:_har(d,x+bw+1,x+bw+g-1,y+bh/2)
    d.add(String(W/2,5,"Compiled & profiled on real Snapdragon devices via Qualcomm AI Hub (qai-hub)",textAnchor="middle",fontName="Helvetica-Oblique",fontSize=7,fillColor=GREY))
    return d

def _mock():
    mono=st("mk",fontName="Courier",fontSize=8.4,leading=12.5,textColor=colors.HexColor("#D8DEE8"))
    monob=st("mkb",fontName="Courier-Bold",fontSize=9,leading=13,textColor=colors.HexColor("#35C7F2"))
    red=st("mkr",fontName="Courier-Bold",fontSize=9.5,leading=13,textColor=colors.HexColor("#FF6B78"))
    lines=[Paragraph("VOXSHIELD EDGE — LIVE CALL ANALYSIS",monob),
           Paragraph("Language: Hindi   Signal: 8 kHz telephony   Window 3.0s / Hop 1.0s",mono),
           Paragraph("Acoustic [OK]   SSL [!]   Indic [!]   Prosody [OK]   Cepstral [!]",mono),
           Paragraph("FUSION RISK  91%   ->   LIKELY SYNTHETIC VOICE",red),
           Paragraph("Evidence: synthetic spectral · abnormal prosody · vocoder-like energy · detector agreement",mono),
           Paragraph("Processing: LOCAL DEVICE      Internet required: NO",monob)]
    t=Table([[l] for l in lines],colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("BOX",(0,0),(-1,-1),1,RED),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),("TOPPADDING",(0,0),(0,0),8),
        ("BOTTOMPADDING",(-1,-1),(-1,-1),8),("TOPPADDING",(0,1),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-2),1)]))
    return t

def deco(cv,doc):
    cv.saveState();cv.setFillColor(RED);cv.rect(0,A4[1]-5,A4[0],5,fill=1,stroke=0)
    cv.setStrokeColor(LINE);cv.setLineWidth(0.5);cv.line(20*mm,13*mm,A4[0]-20*mm,13*mm)
    cv.setFont("Helvetica",7.4);cv.setFillColor(GREY)
    cv.drawString(20*mm,9*mm,"VoxShield Edge · Snapdragon AI Lab Build & Present Challenge · Master Technical Document")
    cv.drawRightString(A4[0]-20*mm,9*mm,f"{doc.page}");cv.restoreState()

E=[]
# cover
class Cover(Flowable):
    def __init__(self):self.width=CW;self.height=70
    def wrap(self,a,b):return(self.width,70)
    def draw(self):
        c=self.canv;c.setFillColor(DARK);c.roundRect(0,0,CW,70,5,fill=1,stroke=0)
        c.setFillColor(RED);c.rect(0,66,CW,4,fill=1,stroke=0)
        c.setFillColor(colors.HexColor("#35C7F2"));c.setFont("Helvetica-Bold",8.5);c.drawString(15,50,C.EVENT.upper())
        c.setFillColor(WHITE);c.setFont("Helvetica-Bold",26);c.drawString(14,22,C.TITLE)
        c.setFillColor(colors.HexColor("#B9C2D0"));c.setFont("Helvetica",11);c.drawString(15,8,C.SUB)
E+=[Cover(),Spacer(1,8),
    P("<b>“When a cloned voice can sound like someone you trust, the device needs to know the difference.”</b>",st("q",fontName="Helvetica-Oblique",fontSize=11,leading=15,textColor=INK,alignment=TA_CENTER)),
    Spacer(1,6)]
# stat cards
sc_cells=[Paragraph(f'<b><font color="#EE2737" size="13">{b}</font></b><br/><font color="#5B6470" size="7">{l.replace(chr(10)," ")}</font>',st("sc",alignment=TA_CENTER,leading=10)) for b,l in C.STATS]
sct=Table([sc_cells],colWidths=[CW/4]*4);sct.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.6,LINE),("INNERGRID",(0,0),(-1,-1),0.6,LINE),("BACKGROUND",(0,0),(-1,-1),PANEL),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
E+=[sct,Spacer(1,4),
    P("Evidence labels used throughout: "+" · ".join(f'<b>[{LBL[k][0]}]</b>' for k in ['V','PR','IMP','EXP','PROP','TGT','ILL']),SMALL),
    P(f"Individual submission · {C.AUTHOR} · GitHub: DG10911/voxshield · Working system at TRL-5 {lbl('PR')}",SMALL)]

E+=[H("1 · Executive Summary"),
    P("VoxShield Edge is an on-device AI security layer that detects AI-generated and cloned voices during "
      "telephony conversations and explains <i>why</i> — running locally on a Snapdragon-powered HP PC so sensitive "
      "call audio need not leave the device. It is <b>telephony-first</b> (8&nbsp;kHz G.711), <b>Indic-aware</b> "
      "(10 Indian languages), <b>multi-detector</b> (five complementary models + learned fusion), <b>streaming</b> "
      "(a verdict within the first seconds), <b>explainable</b>, and <b>non-destructive</b> (recommends step-up "
      "verification; never auto-blocks). "+lbl('IMP')),
    P(f"<b>Measured evidence {lbl('PR')}:</b> 5.9% EER on a held-out in-the-wild corpus; 6.8% EER / 0.98 AUC on "
      "out-of-distribution deepfakes from unseen generators; Indic fake recall 42% → 82% after Indic-aware retraining; "
      "genuine-Indic false positives 11.7% → 6.3%. <b>Snapdragon status:</b> the detector runs today on CPU/GPU; the "
      f"NPU port via ONNX Runtime QNN + Qualcomm AI Hub is a defined optimisation roadmap {lbl('PROP')} — no on-NPU "
      "latency is claimed until measured.")]

E+=[H("2 · Problem &amp; Indian Telephony Threat Model"),
    P("Voice cloning is now cheap and fast. In India, phone-based fraud — fake bank officials, “digital arrest” "
      "scams, relative-in-distress calls — increasingly uses synthetic voices in Indian languages over ordinary "
      "8&nbsp;kHz phone lines. The attack chain:"),
    P("<b>Attacker → cloned voice of a trusted person → victim over a phone call → social-engineered financial fraud.</b>",st("tm",parent=BODY,alignment=TA_CENTER,textColor=REDD)),
    bullets([
      "Cloning needs only seconds of reference audio; scripts are localised per language.",
      "Telephony (G.711, 8&nbsp;kHz) strips the high-frequency detail many detectors rely on.",
      "Sensitive customer audio should not be shipped to a foreign cloud (data-governance).",
      "A verdict <i>after</i> the call ends is forensics, not protection — detection must be real-time."])]

E+=[H("3 · Why Voice-Clone Detection Is Hard Here"),
    tbl([["Dimension","Common assumption","This setting"],
         ["Channel","Studio / wideband","8 kHz G.711 narrowband, codec loss, noise"],
         ["Language","English-centric data","Indic phonetics; code-switching"],
         ["Attack coverage","Single detector / known generators","Diverse, evolving TTS &amp; voice-conversion"],
         ["Output","Black-box score","Operational risk + reason for an analyst"],
         ["Deployment","Cloud inference","On-device / controlled infrastructure"]],
        [30*mm,55*mm,80*mm]),
    P("Why the specifics matter: <b>8&nbsp;kHz</b> is the real telephony rate; <b>G.711 μ-law</b> is the dominant "
      "codec, and both discard cues above ~3.4&nbsp;kHz. A <b>3-second window</b> gives enough context to judge a "
      "voice; a <b>1-second hop</b> yields an early verdict that refines during the call. <b>Multiple detectors</b> "
      "reduce single-model fragility; <b>Indic-aware</b> handling prevents both missed Indic fakes and over-flagging "
      "genuine Indian speakers; <b>low false positives</b> matter because over-flagging real customers is costly.")]

E+=[H("4 · VoxShield Edge — Solution &amp; Product Experience"),
    P("An endpoint application on an HP Snapdragon AI PC. Audio is processed locally; VAD gates speech; streaming "
      "windows feed five specialist detectors; an adaptive fusion layer combines the evidence; the user sees a risk "
      "verdict and the reasons behind it. No automatic blocking occurs. "+lbl('IMP')),
    _mock(),
    P("(UI is an illustrative concept; a working streaming console is included in the prototype materials.)",CAP)]

E+=[H("5 · System Architecture"),
    KeepTogether([Fig(fig_arch()),P("Figure 1 — On-device architecture: audio → preprocessing → five detectors → learned fusion → routing → explainable risk. "+'[IMPLEMENTED]',CAP)])]

E+=[H("6 · Detector Architecture &amp; Fusion"),
    P("VoxShield mixes detector families on the hypothesis that they respond differently to synthesis artifacts and "
      "channel distortion, so fusion improves robustness. The 89-dimensional feature bank (LFCC, CQCC, group-delay "
      "phase, F0, jitter, shimmer, and a &gt;6&nbsp;kHz band computed at a 16&nbsp;kHz analysis rate) feeds classical "
      "detectors; self-supervised models (wav2vec2, XLS-R&nbsp;300M, DistilHuBERT) add learned representations; a "
      "learned meta-stacker combines them. "+lbl('IMP')),
    tbl([["Configuration","EER","Reading"],
         ["Best single detector (XLS-R 300M)","16.0%","strong but fragile"],
         ["Naive averaging","19.1%","worse than best single"],
         ["Learned meta-fusion","5.9%","the fusion produces the gain"]],
        [70*mm,25*mm,70*mm],boldcols=(1,)),
    P(f"The learned stacker — not any single model — produces the performance gain {lbl('PR')}. Naive averaging is "
      "worse than the best single model, which is why a <i>learned</i> fusion matters.")]

E+=[H("7 · Streaming Pipeline"),
    KeepTogether([Fig(fig_pipeline()),P("Figure 2 — Streaming inference pipeline (3s window · 1s hop). "+'[IMPLEMENTED]',CAP)])]

E+=[H("8 · Indic-Language Intelligence"),
    P("A multilingual backbone does not by itself make a detector language-robust: synthesis artifacts and genuine-"
      "speaker distributions shift across languages. VoxShield adds an Indic-aware detection path with on-device "
      "language-ID routing (Indic → telephony → general) and retrains on Indic material. Measured on the tested Indic "
      f"conditions {lbl('PR')}:"),
    tbl([["Metric","Before","After","Scope"],
         ["Indic fake recall (MMS-TTS)","42%","82%","single-generator, tested set; English EER unchanged"],
         ["Genuine-Indic false-positive rate","11.7%","6.3%","channel-aware; fewer genuine-customer flags"]],
        [55*mm,20*mm,20*mm,50*mm],boldcols=(1,2)),
    P("Supported languages (target): Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Gujarati, Punjabi, "
      "English. "+lbl('TGT'))]

E+=[PageBreak(),H("9 · Snapdragon Optimisation"),
    P("Snapdragon is core to the product, not a label. VoxShield Edge targets the Hexagon NPU for power-efficient, "
      "offline, sustained inference on an HP Snapdragon AI PC."),
    KeepTogether([Fig(fig_snap()),P("Figure 3 — On-device inference path (proposed optimisation). "+'[PROPOSED]',CAP)]),
    tbl([["Layer","Approach","Status"],
         ["Hardware","Snapdragon X Elite/Plus (45 TOPS NPU); X2 Elite (80 TOPS)","[VERIFIED]"],
         ["Inference runtime","ONNX Runtime + QNN Execution Provider (onnxruntime-qnn), Windows/ARM64","[PROPOSED]"],
         ["Compile / profile","Qualcomm AI Hub (qai-hub) on real Snapdragon devices","[PROPOSED]"],
         ["Optimisation","INT8 quantisation; heterogeneous CPU/GPU/NPU placement","[PROPOSED]"],
         ["Ecosystem models","WavLM-Base-Plus backbone + Whisper (both on AI Hub)","[VERIFIED]"]],
        [30*mm,90*mm,35*mm]),
    P("Honest note: not every model is claimed to run on the NPU today. wav2vec2/XLS-R are not pre-packaged on AI Hub "
      "and, like Qualcomm's own edge Whisper port (which adapted attention/linear ops), may need adaptation for full "
      "NPU offload — validated via AI Hub profiling. This is the optimisation roadmap, not a measured result.")]

E+=[H("10 · Privacy / On-Device Architecture"),
    KeepTogether([Fig(fig_edge()),P("Figure 4 — Cloud path vs on-device path. "+'[ILLUSTRATIVE]',CAP)]),
    bullets([
      "Raw call audio is processed locally — architected so it need not leave the device. "+lbl('IMP'),
      "Offline operation: works air-gapped / in low-connectivity branches. "+lbl('TGT'),
      "Latency: streaming windows form an early verdict; on-NPU latency to be measured. "+lbl('PROP'),
      "Power efficiency: sustained NPU inference targeted for all-day endpoint use. "+lbl('TGT')])]

E+=[H("11 · Evaluation Methodology &amp; Results"),
    P("Detectors are trained on some corpora and evaluated on held-out / out-of-distribution data the models did not "
      "see in training — a deliberately hard generalisation test. EER (Equal Error Rate) is the operating point where "
      "false-accept and false-reject rates are equal (lower is better); it is not accuracy. In-corpus and "
      "out-of-distribution figures are reported separately and never conflated."),
    tbl([["Evaluation","Metric","Result","Label"],
         ["Held-out in-the-wild (fusion)","EER","5.9%","[PROJECT RESULT]"],
         ["Unseen-generator deepfakes (MLAAD, OOD)","EER / AUC","6.8% / 0.98","[PROJECT RESULT]"],
         ["Indic fake recall (MMS-TTS)","recall","42% → 82%","[PROJECT RESULT]"],
         ["Genuine-Indic false positives","FPR","11.7% → 6.3%","[PROJECT RESULT]"],
         ["On-NPU latency / power","ms · W","to be measured","[PROPOSED]"]],
        [58*mm,24*mm,38*mm,35*mm],boldcols=(2,))]

E+=[H("12 · Explainability"),
    P("Each verdict carries reason codes derived from detector outputs and the feature bank, so an analyst sees "
      "<i>why</i> a call scored high — spectral inconsistency, vocoder-like &gt;6&nbsp;kHz energy (wideband only), "
      "phase / group-delay irregularity, missing prosody (F0/jitter/shimmer), absence of natural breath, and "
      "detector disagreement. These are signal-derived indicators, not formally faithfulness-tested explanations. "+lbl('IMP'))]

E+=[H("13 · Competitive Positioning"),
    tbl([["Capability","Cloud voice detection","Single-model deepfake","Generic audio deepfake","VoxShield Edge"],
         ["Telephony (8 kHz) optimised","Varies","Varies","Rarely","Designed for"],
         ["Indic-language aware","Varies","Rarely","Rarely","Designed for"],
         ["Streaming / early detection","Varies","Varies","Post-hoc","Designed for"],
         ["Multi-detector fusion","Varies","No","Varies","Demonstrated"],
         ["Explainable evidence","Varies","Rarely","Varies","Demonstrated"],
         ["On-device / offline","No","Varies","Varies","Targeted"],
         ["Privacy (no audio egress)","No","Varies","Varies","Designed for"]],
        [42*mm,26*mm,26*mm,26*mm,30*mm],boldcols=(4,)),
    P("Language is deliberately conservative — “Designed for / Demonstrated / Targeted” — and “Varies” where a "
      "general claim cannot be evidenced across products.",CAP)]

E+=[H("14 · Evidence Matrix"),
    tbl([["Claim","Evidence","Status","Demonstration"],
         ["Real-time detection","3s window / 1s hop streaming","Implemented","Live streaming audio"],
         ["Multi-detector fusion beats single","16.0 / 19.1 / 5.9 EER scoreboard","Project result","Result table"],
         ["Generalises to unseen generators","6.8% EER / 0.98 AUC on MLAAD (OOD)","Project result","Held-out eval"],
         ["Indic-aware helps","recall 42→82; FP 11.7→6.3","Project result","Before/after eval"],
         ["On-device / private","local pipeline, no audio egress","Implemented (CPU/GPU)","Offline demo"],
         ["Runs on Snapdragon NPU","ONNX→QNN→Hexagon path + AI Hub","Proposed","AI Hub profiling (next)"],
         ["Explainable verdict","reason codes from detectors","Implemented","Evidence panel"]],
        [42*mm,50*mm,28*mm,30*mm])]

E+=[H("15 · Limitations"),
    bullets([
      "Unseen generators / codecs can evade until incorporated; cross-generator remains a validation target.",
      "Speaker-disjoint and real captured-PSTN evaluation are not yet complete.",
      "Very short segments, heavy noise and code-switching reduce reliability.",
      "On-NPU latency/power are not yet measured; NPU offload of transformer detectors may need adaptation.",
      "In-corpus figures reflect corpus separability; the honest generalisation number is the OOD 6.8% EER."])]

E+=[H("16 · Roadmap &amp; Adoption"),
    tbl([["Horizon","Milestone","Label"],
         ["Now","ONNX export + INT8 quantisation; AI Hub compile/profile on Snapdragon X/X2","[PROPOSED]"],
         ["Next","Measured on-NPU latency + power; Windows endpoint app; streaming demo","[TARGET]"],
         ["Then","More Indic languages; larger real-world corpus; challenge-response liveness","[TARGET]"],
         ["Product","Contact-centre integration; enterprise SDK/API; telecom pilots","[PROPOSED]"]],
        [22*mm,100*mm,33*mm]),
    P("Adoption: banks, NBFCs and contact centres that need Indic-language, telephony-quality, private fraud "
      "screening on endpoints — a Snapdragon AI PC per fraud-desk analyst, no per-call cloud cost.")]

E+=[H("17 · Conclusion"),
    P("VoxShield Edge is a technically serious, evidence-driven edge-AI security prototype for a real Indian problem, "
      "with a credible path to Snapdragon deployment. It detects early, explains clearly, and is designed to protect "
      "privately — on the device. "),
    P("<b>Detect early. Explain clearly. Protect privately.</b>",st("end",parent=BODY,alignment=TA_CENTER,textColor=REDD)),
    Spacer(1,4),
    P("GitHub: DG10911/voxshield · Pitch deck (PDF + PPTX), prototype console, and one-page summary submitted "
      "alongside · Contact: devanshgoenka03@gmail.com",SMALL)]

OUT="VOXSHIELD_SNAPDRAGON_MASTER.pdf"
SimpleDocTemplate(OUT,pagesize=A4,topMargin=14*mm,bottomMargin=15*mm,leftMargin=20*mm,rightMargin=20*mm,
                  title="VoxShield Edge — Master Technical Document",author=C.AUTHOR).build(E,onFirstPage=deco,onLaterPages=deco)
print("wrote",OUT)
