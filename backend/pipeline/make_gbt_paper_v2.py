#!/usr/bin/env python3
"""VoxShield — GBT BuildStorm 2026 Round-1 paper.
Submission-grade PDF with vector diagrams. Aesthetic: black / white / deep-red.
Content facts are the team-verified set; citations filled from verified research.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, ListFlowable, ListItem,
                                KeepTogether, Flowable, PageBreak)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, PolyLine
from reportlab.graphics import renderPDF

# ---------------- palette ----------------
INK   = colors.HexColor("#111418")   # near-black
RED   = colors.HexColor("#B01326")   # deep red accent
REDD  = colors.HexColor("#7C0D1B")   # darker red
RTINT = colors.HexColor("#FBEDEF")   # red tint fill
GREY  = colors.HexColor("#5B6470")
LGREY = colors.HexColor("#9AA3AE")
PANEL = colors.HexColor("#F4F6F8")
LINEC = colors.HexColor("#D3D9E0")
WHITE = colors.white

CW = A4[0] - 40*mm  # content width

ss = getSampleStyleSheet()
def st(name, **kw):
    kw.setdefault("parent", ss["Normal"]); return ParagraphStyle(name, **kw)

TITLE = st("t", fontName="Helvetica-Bold", fontSize=26, leading=28, textColor=INK, alignment=TA_CENTER, spaceAfter=2)
SUBT  = st("s", fontName="Helvetica", fontSize=11.5, leading=15, textColor=GREY, alignment=TA_CENTER)
KICK  = st("k", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=RED, alignment=TA_CENTER, spaceAfter=2)
VP    = st("vp", fontName="Helvetica-Oblique", fontSize=11.5, leading=16, textColor=INK, alignment=TA_CENTER)
H     = st("h", fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=INK, spaceBefore=11, spaceAfter=4)
HNUM  = st("hn", fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=RED)
BODY  = st("b", fontName="Helvetica", fontSize=9.6, leading=13.4, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1A1D21"), spaceAfter=5)
BUL   = st("bu", parent=BODY, spaceAfter=2)
CAP   = st("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)
CELL  = st("c", fontName="Helvetica", fontSize=8.3, leading=10.6, textColor=colors.HexColor("#1A1D21"))
CELLB = st("cb", fontName="Helvetica-Bold", fontSize=8.3, leading=10.6, textColor=colors.HexColor("#1A1D21"))
CELLH = st("ch", fontName="Helvetica-Bold", fontSize=8.4, leading=10.6, textColor=WHITE)
SMALL = st("sm", fontName="Helvetica", fontSize=8, leading=11, textColor=GREY)
REF   = st("rf", fontName="Helvetica", fontSize=7.9, leading=11, textColor=colors.HexColor("#2A2E33"), alignment=TA_LEFT, spaceAfter=2)

def P(t, s=BODY): return Paragraph(t, s)
def head(n, t): return Paragraph(f'<font color="#B01326">{n}</font>&nbsp;&nbsp;{t}', H)
def rule(c=LINEC, th=0.6, sb=2, sa=8): return HRFlowable(width="100%", thickness=th, color=c, spaceBefore=sb, spaceAfter=sa)
def bullets(items, s=BUL):
    return ListFlowable([ListItem(P(x, s), leftIndent=6, value="•") for x in items],
                        bulletType="bullet", leftIndent=12, spaceAfter=6)

def tbl(rows, widths, header=True, boldcol=None):
    data=[]
    for i,r in enumerate(rows):
        row=[]
        for j,c in enumerate(r):
            sty = CELLH if (header and i==0) else (CELLB if boldcol==j else CELL)
            row.append(Paragraph(str(c), sty))
        data.append(row)
    t=Table(data,colWidths=widths,hAlign="LEFT")
    cmds=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),
          ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
          ("TOPPADDING",(0,0),(-1,-1),4.5),("BOTTOMPADDING",(0,0),(-1,-1),4.5),
          ("LINEBELOW",(0,0),(-1,-1),0.4,LINEC),("BOX",(0,0),(-1,-1),0.6,LGREY)]
    if header:
        cmds+=[("BACKGROUND",(0,0),(-1,0),INK),("LINEBELOW",(0,0),(-1,0),1.0,RED)]
        for r in range(1,len(rows)):
            if r%2==0: cmds.append(("BACKGROUND",(0,r),(-1,r),PANEL))
    t.setStyle(TableStyle(cmds)); return t

# ---------------- diagram primitives ----------------
def _box(d,x,y,w,h,title,sub=None,fill=WHITE,stroke=INK,tc=INK,fs=8.2,bold=True,r=3):
    d.add(Rect(x,y,w,h,rx=r,ry=r,fillColor=fill,strokeColor=stroke,strokeWidth=1))
    if sub:
        d.add(String(x+w/2,y+h/2+2,title,textAnchor="middle",fontName="Helvetica-Bold" if bold else "Helvetica",fontSize=fs,fillColor=tc))
        d.add(String(x+w/2,y+h/2-8,sub,textAnchor="middle",fontName="Helvetica",fontSize=fs-1.2,fillColor=tc))
    else:
        d.add(String(x+w/2,y+h/2-3,title,textAnchor="middle",fontName="Helvetica-Bold" if bold else "Helvetica",fontSize=fs,fillColor=tc))

def _varrow(d,x,y0,y1,c=RED):
    d.add(Line(x,y0,x,y1,strokeColor=c,strokeWidth=1.4))
    d.add(Polygon([x-3,y1+5,x+3,y1+5,x,y1],fillColor=c,strokeColor=c))
def _harrow(d,x0,x1,y,c=RED):
    d.add(Line(x0,y,x1,y,strokeColor=c,strokeWidth=1.4))
    d.add(Polygon([x1-5,y-3,x1-5,y+3,x1,y],fillColor=c,strokeColor=c))

class Fig(Flowable):
    def __init__(self,drawing): self.d=drawing; self.width=drawing.width; self.height=drawing.height
    def wrap(self,aw,ah): return (self.width,self.height)
    def draw(self): renderPDF.draw(self.d,self.canv,0,0)

# ---- Fig 1: threat landscape (horizontal chain) ----
def fig1():
    W,Hh=CW,74; d=Drawing(W,Hh)
    labels=[("Voice cloning","cheap synthetic voices"),("Telephone fraud","scam call delivery"),
            ("Indic languages","Hindi/Tamil/Bengali+"),("Telephony loss","8 kHz G.711 codec"),
            ("Detection gap","no fit-for-context tool")]
    n=len(labels); gap=14; bw=(W-(n-1)*gap)/n; bh=42; y=18
    for i,(t,s) in enumerate(labels):
        x=i*(bw+gap)
        fill=RTINT if i==n-1 else PANEL; stroke=RED if i==n-1 else INK
        tc=REDD if i==n-1 else INK
        _box(d,x,y,bw,bh,t,s,fill=fill,stroke=stroke,tc=tc,fs=8.4)
        if i<n-1: _harrow(d,x+bw+1,x+bw+gap-1,y+bh/2)
    d.add(String(W/2,6,"Compounding risk chain",textAnchor="middle",fontName="Helvetica-Oblique",fontSize=7.5,fillColor=GREY))
    return d

# ---- Fig 2: architecture / streaming pipeline (vertical, top-down cursor) ----
def fig_arch():
    W=CW; bh=28; arr=15; ph=82; top=6; bot=6
    # 8 elements (3 pre-boxes, panel, 4 tail) -> 7 arrows
    Hh=top+3*bh+ph+4*bh+7*arr+bot
    d=Drawing(W,Hh); cx=W/2; bw=190; x=cx-bw/2
    cur=[Hh-top]
    def pbox(t,s,fl,stk,tc,fs=8.2):
        _box(d,x,cur[0]-bh,bw,bh,t,s,fill=fl,stroke=stk,tc=tc,fs=fs); cur[0]-=bh
    def arrow():
        _varrow(d,cx,cur[0]-2,cur[0]-arr+3); cur[0]-=arr
    for t,s in [("Call audio","8 kHz G.711 μ-law telephony"),
                ("Silero VAD","voice-activity gating"),
                ("Windowing","3 s window · 1 s hop · normalize / resample")]:
        pbox(t,s,PANEL,INK,INK); arrow()
    # parallel detectors panel
    pw=W-4; px=2; py=cur[0]-ph
    d.add(Rect(px,py,pw,ph,rx=4,ry=4,fillColor=colors.HexColor("#FCFCFD"),strokeColor=RED,strokeWidth=1.2,strokeDashArray=[3,2]))
    d.add(String(px+8,py+ph-13,"PARALLEL DETECTION ENGINES",fontName="Helvetica-Bold",fontSize=7.8,fillColor=RED))
    dets=["Acoustic DSP\n(89-dim bank)","wav2vec2","XLS-R 300M","DistilHuBERT","LFCC + CQCC\nfusion head"]
    dn=len(dets); dg=8; dbw=(pw-16-(dn-1)*dg)/dn; dby=py+10; dbh=44
    for i,name in enumerate(dets):
        dx=px+8+i*(dbw+dg)
        d.add(Rect(dx,dby,dbw,dbh,rx=3,ry=3,fillColor=WHITE,strokeColor=INK,strokeWidth=0.9))
        parts=name.split("\n")
        if len(parts)==2:
            d.add(String(dx+dbw/2,dby+dbh/2+3,parts[0],textAnchor="middle",fontName="Helvetica-Bold",fontSize=7.4,fillColor=INK))
            d.add(String(dx+dbw/2,dby+dbh/2-8,parts[1],textAnchor="middle",fontName="Helvetica",fontSize=6.5,fillColor=GREY))
        else:
            d.add(String(dx+dbw/2,dby+dbh/2-2,parts[0],textAnchor="middle",fontName="Helvetica-Bold",fontSize=7.6,fillColor=INK))
    cur[0]=py; arrow()
    tail=[("Meta-fusion","complementary detector fusion",INK,PANEL,INK),
          ("Indic → Telephony → General router","specialised meta-classifiers",REDD,RTINT,RED),
          ("Calibrated risk · LOW / MEDIUM / HIGH","+ explainable reason codes",INK,PANEL,INK),
          ("Step-up verification / fraud workflow","decision support (not auto-block)",REDD,RTINT,RED)]
    for i,(t,s,tc,fl,stk) in enumerate(tail):
        pbox(t,s,fl,stk,tc,fs=7.9)
        if i<len(tail)-1: arrow()
    return d

# ---- Fig 4: fusion → routers ----
def fig_fusion():
    W,Hh=CW,165; d=Drawing(W,Hh)
    dets=["Acoustic DSP","wav2vec2","XLS-R 300M","DistilHuBERT","LFCC+CQCC"]
    n=len(dets); gap=10; bw=(W-(n-1)*gap)/n; y=Hh-30; bh=24
    fx=W/2
    for i,dt in enumerate(dets):
        x=i*(bw+gap); _box(d,x,y,bw,bh,dt,fill=WHITE,fs=7.6)
        d.add(Line(x+bw/2,y-1,fx,y-24,strokeColor=LGREY,strokeWidth=0.8))
    # meta fusion node
    mw=180; mx=fx-mw/2; my=y-52
    _box(d,mx,my,mw,24,"META-FUSION / meta-classification",fill=INK,tc=WHITE,fs=8.2)
    _varrow(d,fx,my-1,my-13)
    routers=[("Indic-aware","priority 1"),("Telephony","priority 2"),("General","fallback")]
    rn=len(routers); rg=12; rbw=(W-(rn-1)*rg)/rn; ry=my-52
    for i,(t,s) in enumerate(routers):
        x=i*(rbw+rg); fl=RTINT if i==0 else PANEL; stroke=RED if i==0 else INK
        _box(d,x,ry,rbw,26,t,s,fill=fl,stroke=stroke,tc=(REDD if i==0 else INK),fs=8.0)
        d.add(Line(fx,my-13,x+rbw/2,ry+26,strokeColor=LGREY,strokeWidth=0.8))
    return d

# ---- Fig 5: Indic improvement bars ----
def fig_indic():
    W,Hh=CW,150; d=Drawing(W,Hh)
    base=42; new=82; # recall
    fp_b=36.3; fp_n=6.3
    # two grouped charts
    def barpair(ox,ow,title,b,n,binv=False,unit="%"):
        d.add(String(ox+ow/2,Hh-14,title,textAnchor="middle",fontName="Helvetica-Bold",fontSize=8.4,fillColor=INK))
        base_y=26; maxh=88; scale=maxh/100.0
        bw=46; g=34; x0=ox+(ow- (2*bw+g))/2
        # before
        h1=b*scale
        d.add(Rect(x0,base_y,bw,h1,fillColor=LGREY,strokeColor=None))
        d.add(String(x0+bw/2,base_y+h1+3,f"{b:g}{unit}",textAnchor="middle",fontName="Helvetica-Bold",fontSize=8,fillColor=GREY))
        d.add(String(x0+bw/2,base_y-11,"before",textAnchor="middle",fontName="Helvetica",fontSize=7,fillColor=GREY))
        # after
        h2=n*scale
        d.add(Rect(x0+bw+g,base_y,bw,h2,fillColor=RED,strokeColor=None))
        d.add(String(x0+bw+g+bw/2,base_y+h2+3,f"{n:g}{unit}",textAnchor="middle",fontName="Helvetica-Bold",fontSize=8,fillColor=REDD))
        d.add(String(x0+bw+g+bw/2,base_y-11,"after",textAnchor="middle",fontName="Helvetica",fontSize=7,fillColor=GREY))
        d.add(Line(ox+6,base_y,ox+ow-6,base_y,strokeColor=INK,strokeWidth=0.8))
    barpair(0,W/2-6,"Indic recall  (MMS-TTS fakes) ↑",base,new)
    barpair(W/2+6,W/2-6,"Genuine-Indic false positives ↓",fp_b,fp_n)
    return d

# ---- Fig 6: fraud workflow ----
def fig_workflow():
    W,Hh=CW,150; d=Drawing(W,Hh)
    cx=W/2; bw=150
    _box(d,cx-bw/2,Hh-30,bw,24,"Incoming call → VoxShield analysis",fill=PANEL,fs=8.2)
    _varrow(d,cx,Hh-31,Hh-43)
    _box(d,cx-bw/2,Hh-70,bw,24,"Risk score + reason codes",fill=INK,tc=WHITE,fs=8.2)
    # three branches
    br=[("LOW","normal call flow",PANEL,INK,INK),
        ("MEDIUM","step-up verification",RTINT,RED,REDD),
        ("HIGH","analyst / enhanced fraud check",RTINT,RED,REDD)]
    n=len(br); g=14; bbw=(W-(n-1)*g)/n; by=18
    for i,(t,s,fl,stk,tc) in enumerate(br):
        x=i*(bbw+g)
        d.add(Rect(x,by,bbw,40,rx=3,ry=3,fillColor=fl,strokeColor=stk,strokeWidth=1))
        d.add(String(x+bbw/2,by+24,t,textAnchor="middle",fontName="Helvetica-Bold",fontSize=9,fillColor=tc))
        d.add(String(x+bbw/2,by+10,s,textAnchor="middle",fontName="Helvetica",fontSize=7.2,fillColor=GREY))
        d.add(Line(cx,Hh-71,x+bbw/2,by+40,strokeColor=LGREY,strokeWidth=0.8))
    return d

# ---- Fig 6: detector scoreboard (EER per config) ----
def fig_scoreboard():
    W,Hh=CW,180; d=Drawing(W,Hh)
    data=[("Wav2Vec2",62.4,LGREY),("Acoustic DSP",46.9,LGREY),("LFCC+CQCC",26.8,LGREY),
          ("DistilHuBERT",23.0,LGREY),("Naive average",19.1,colors.HexColor("#C98A90")),
          ("XLS-R 300M",16.0,LGREY),("Meta-fusion",5.9,RED)]
    d.add(String(W/2,Hh-12,"Equal Error Rate by configuration  (lower is better)",textAnchor="middle",
                 fontName="Helvetica-Bold",fontSize=8.6,fillColor=INK))
    base_y=30; maxh=120; scale=maxh/65.0
    n=len(data); g=12; bw=(W-(n-1)*g-8)/n; x0=4
    for i,(lab,val,col) in enumerate(data):
        x=x0+i*(bw+g); h=val*scale
        d.add(Rect(x,base_y,bw,h,fillColor=col,strokeColor=None))
        vc = REDD if col==RED else GREY
        d.add(String(x+bw/2,base_y+h+3,f"{val:g}%",textAnchor="middle",fontName="Helvetica-Bold",fontSize=7.6,fillColor=vc))
        lc = REDD if col==RED else colors.HexColor("#3A3F45")
        d.add(String(x+bw/2,base_y-11,lab,textAnchor="middle",fontName="Helvetica" if col!=RED else "Helvetica-Bold",fontSize=6.7,fillColor=lc))
    d.add(Line(x0,base_y,x0+n*(bw+g)-g,base_y,strokeColor=INK,strokeWidth=0.8))
    d.add(String(W/2,8,"Best single model 16.0%; naive averaging is worse (19.1%); only the learned stacker reaches 5.9%.",
                 textAnchor="middle",fontName="Helvetica-Oblique",fontSize=7,fillColor=GREY))
    return d

# ---------------- references (VERIFIED set — fill after research) ----------------
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbt_refs import REFS

# ---------------- stat cards for cover ----------------
def statcards():
    cards=[("5.9%","meta-fusion EER · held-out\nIn-the-Wild (cross-dataset)"),
           ("42% → 82%","Indic recall on MMS-TTS\nfakes · English EER unchanged"),
           ("36.3% → 6.3%","genuine-Indic false\npositives (retrained)"),
           ("8 kHz G.711","telephony-native\nstreaming pipeline")]
    W=CW; d=Drawing(W,58); n=4; g=10; bw=(W-(n-1)*g)/n
    for i,(big,lab) in enumerate(cards):
        x=i*(bw+g)
        d.add(Rect(x,0,bw,56,rx=4,ry=4,fillColor=INK,strokeColor=RED,strokeWidth=1))
        d.add(String(x+bw/2,34,big,textAnchor="middle",fontName="Helvetica-Bold",fontSize=13.5,fillColor=WHITE))
        for j,ln in enumerate(lab.split("\n")):
            d.add(String(x+bw/2,20-j*9,ln,textAnchor="middle",fontName="Helvetica",fontSize=6.7,fillColor=colors.HexColor("#C9CED4")))
    return Fig(d)

# ---------------- header/footer ----------------
def deco(canvas,doc):
    canvas.saveState()
    canvas.setFillColor(RED); canvas.rect(0, A4[1]-6, A4[0], 6, fill=1, stroke=0)
    canvas.setStrokeColor(LINEC); canvas.setLineWidth(0.5)
    canvas.line(20*mm,14*mm,A4[0]-20*mm,14*mm)
    canvas.setFont("Helvetica",7.6); canvas.setFillColor(GREY)
    canvas.drawString(20*mm,9.5*mm,"VoxShield · Team DigiSeva · GBT BuildStorm 2026 — Round 1")
    canvas.drawRightString(A4[0]-20*mm,9.5*mm,f"{doc.page}")
    canvas.restoreState()

# ===================================================================
E=[]
# ---- COVER ----
E += [Spacer(1,6), P("GBT BUILDSTORM 2026  ·  FINTECH &amp; FINANCIAL INCLUSION  ·  ROUND 1 PAPER", KICK),
      P("VoxShield", TITLE),
      P("Real-Time Voice-Deepfake Detection for Indic-Language Telephony Fraud", SUBT),
      Spacer(1,6),
      P("An on-premises, Indic-first, telephony-hardened prototype that detects AI-cloned voices in "
        "phone-quality Indian-language calls and returns a calibrated, explainable fraud-risk verdict "
        "within the first seconds of a call (streaming).", VP),
      Spacer(1,10), statcards(), Spacer(1,6),
      P("Team DigiSeva · Team Lead: Devansh Goenka", SUBT),
      rule(RED,1.0,4,6)]

# ---- 1 Executive summary ----
E += [head("1","Executive Summary"),
      P("<b>Problem.</b> AI voice cloning has made convincing synthetic speech cheap and fast, and it is "
        "increasingly used in phone-based financial scams in India — often in Indian languages and over "
        "ordinary, low-quality telephone lines. <b>Why now.</b> Public authorities in India have flagged a "
        "sharp rise in digital financial fraud and in AI-enabled impersonation scams [1][2]. <b>Gap.</b> "
        "Most voice-deepfake detectors are tuned for clean, English-centric, cloud-processed audio; their "
        "effectiveness on Indian-language, narrowband (8&nbsp;kHz) telephone audio and inside an "
        "institution's own infrastructure varies and is rarely reported."),
      P("<b>What VoxShield is.</b> A real-time detector purpose-built for this setting: it ingests G.711 "
        "μ-law 8&nbsp;kHz telephony audio, runs five complementary detectors under a meta-fusion layer "
        "with Indic- and telephony-aware routing, and outputs a LOW/MEDIUM/HIGH risk verdict with "
        "explainable reason codes to drive a step-up-verification workflow — not automatic blocking. "
        "<b>Evidence.</b> On a held-out In-the-Wild set (cross-dataset), the learned meta-fusion reaches "
        "<b>5.9% EER</b> — versus 16.0% for the best single detector and 19.1% for naive averaging, so the "
        "observed gain comes from the learned fusion, not any single model. After Indic-aware retraining, recall on MMS-TTS Indic "
        "deepfakes rose <b>42% → 82%</b> with English EER unchanged at 5.9%, and genuine-Indic false "
        "positives fell <b>36.3% → 6.3%</b>. Scores are Platt-calibrated (ECE 0.044). These are "
        "research-corpus and generator-/language-specific evaluations, not production metrics.")]

# ---- 2 Problem ----
E += [head("2","The Problem"),
      P("Three trends intersect. First, modern text-to-speech and voice-conversion systems can produce "
        "natural-sounding speech from short reference samples, lowering the cost and skill needed to "
        "impersonate a voice. Second, a large share of Indian fraud is delivered over the phone — "
        "impersonation of bank officials, \"digital arrest\" intimidation, and relative-in-distress "
        "scams [3] — including documented cases of AI voice cloning used against Indian targets [14]. Third, "
        "much of this happens in Indian languages and over degraded telephone channels."),
      Fig(fig1()), P("Figure 1 — The compounding risk chain that defines VoxShield's operating context.", CAP),
      P("For a fraud team, the operational problem is not an academic 'is this audio synthetic?' label. It "
        "is: can we flag a suspicious live call early enough, in the right language, over a real phone "
        "line, with a reason a human analyst can act on — without moving sensitive customer audio out of "
        "controlled infrastructure?")]

# ---- 3 Why existing detection breaks ----
E += [head("3","Why Existing Detection Breaks in This Setting"),
      P("The difficulty is a set of domain gaps between where detectors are usually built and where Indian "
        "telephony fraud actually occurs:"),
      tbl([["Dimension","Common assumption","This setting"],
           ["Audio channel","Studio / wideband","8 kHz G.711 narrowband, codec loss, noise"],
           ["Language","English-centric data","Indic phonetics; code-switching"],
           ["Attack coverage","Single detector / known generators","Diverse, evolving TTS &amp; voice-conversion"],
           ["Output","Black-box score","Operational risk + reason for an analyst"],
           ["Deployment","Cloud inference","Controlled / on-prem infrastructure"]],
          [30*mm,58*mm,82*mm]),
      Spacer(1,3),
      P("Narrowband telephony discards exactly the high-frequency detail (roughly above 3.4&nbsp;kHz) where "
        "many synthesis artifacts live [4], so a model trained on clean speech can degrade on phone audio. "
        "Indic-language coverage in public anti-spoofing data is limited, so an English-tuned detector can "
        "both miss Indic fakes and over-flag genuine Indic speakers — the two failure modes VoxShield "
        "targets directly in §8.")]

# ---- 4 Solution ----
E += [head("4","The VoxShield Solution"),
      P("<b>In one line:</b> VoxShield listens to a call the way a phone network delivers it, asks five "
        "complementary detector families ('is this voice real?'), and combines them with a learned, "
        "calibrated meta-stacker into a single risk score plus a plain-language reason — routed through paths "
        "specialised for Indian languages and telephone audio."),
      bullets([
        "<b>Indic-first</b> — an Indic-aware detection path with language-ID routing, not English models applied as an afterthought.",
        "<b>Telephony-hardened</b> — built and evaluated on G.711 μ-law 8&nbsp;kHz narrowband conditions.",
        "<b>Learned multi-detector fusion</b> — five complementary detector families combined by a trained stacker, so no single model is a point of failure.",
        "<b>Explainable, calibrated risk</b> — Platt-calibrated LOW/MEDIUM/HIGH with reason codes, not a bare binary label.",
        "<b>Liveness option</b> — a random challenge-response provides an additional signal against replayed/pre-recorded audio (implemented; not yet experimentally validated).",
        "<b>Honesty engineered</b> — never auto-blocks; every verdict carries reason codes and a SHA-256 audit record.",
        "<b>On-prem architecture</b> — designed so raw call audio can stay inside the institution's environment.",
        "<b>Fraud-workflow native</b> — detect → explain → risk-score → trigger step-up verification.",
      ])]

# ---- 5 Architecture ----
E += [head("5","System Architecture"),
      P("VoxShield is a streaming pipeline. Audio arrives in telephony format, is gated for speech, sliced "
        "into overlapping windows, and scored by parallel detectors whose outputs are fused and routed to "
        "a calibrated risk decision and reason codes."),
      KeepTogether([Fig(fig_arch()), P("Figure 2 — VoxShield streaming architecture, from telephony audio to fraud-workflow trigger.", CAP)])]

# ---- 6 Model architecture / fusion ----
E += [head("6","Model Architecture &amp; Multi-Detector Fusion"),
      P("VoxShield deliberately mixes detector families on the hypothesis that they respond differently to "
        "synthesis artifacts and channel distortions, so fusion may improve robustness. It combines "
        "self-supervised speech representations — wav2vec2 [5], wav2vec2-XLS-R-53 (multilingual, 300M) [6], "
        "and DistilHuBERT [11] — with classical spoofing-sensitive acoustic features (LFCC and CQCC [12]) "
        "and a DSP detector over an 89-dimensional feature bank (LFCC, CQCC, group-delay phase, F0/prosody, "
        "jitter, shimmer, and a high-frequency &gt;6&nbsp;kHz band). Features are computed at a 16&nbsp;kHz "
        "analysis rate (8&nbsp;kHz Nyquist), so the &gt;6&nbsp;kHz band carries information only for wideband "
        "audio; under 8&nbsp;kHz G.711 telephony it is essentially empty, and VoxShield uses that emptiness "
        "as a narrowband indicator rather than relying on high-frequency artifacts there. A meta-classifier fuses the "
        "detector outputs; a router then prioritises the Indic-aware meta-detector, then the "
        "telephony/narrowband meta-detector, then the general detector."),
      KeepTogether([Fig(fig_fusion()), P("Figure 3 — Complementary detectors feed a meta-fusion layer with Indic → telephony → general routing.", CAP)])]

# ---- 7 Methodology ----
E += [head("7","Methodology"),
      P("<b>Inference pipeline.</b> Call audio (8&nbsp;kHz G.711 μ-law) → Silero VAD [10] → 3-second "
        "windows at a 1-second hop → an 89-dimensional acoustic feature vector computed at a 16&nbsp;kHz "
        "analysis rate (LFCC, CQCC, group-delay phase, F0/prosody, jitter, shimmer, and a &gt;6&nbsp;kHz "
        "high-frequency band that is informative for wideband audio and empty under 8&nbsp;kHz telephony) → five "
        "detectors scored in parallel → a learned logistic meta-stacker → Platt calibration → a "
        "LOW/MEDIUM/HIGH verdict with reason codes. Windows are re-scored continuously so a verdict forms "
        "early and is refined as the call proceeds."),
      P("<b>Evaluation protocol.</b> The headline detection number is a <i>cross-dataset</i> figure: "
        "detectors are trained on other corpora and evaluated on held-out In-the-Wild [7] audio the models "
        "did not see in training — a deliberately hard generalisation test rather than an in-distribution "
        "score. Per-detector and fusion scores are computed on a common scored evaluation set so the "
        "stacker can be compared directly against each single model and against naive averaging. EER (Equal "
        "Error Rate) is the operating point where false-accept and false-reject rates are equal [8]; "
        "calibration quality is reported with Expected Calibration Error (ECE) and Brier score. Indic "
        "evaluation uses genuine Indic speech for false positives and MMS-TTS-generated [9] Indic speech for "
        "fake recall; these are generator- and language-specific and are reported separately from the "
        "English detection metric."),
      tbl([["Experiment","Data / generator","Train→Test","Metric","Result","Scope"],
           ["Detection","In-the-Wild [7]","other corpora → held-out ITW","EER","5.9%","cross-dataset; speaker overlap not documented"],
           ["Detector comparison","common scored set","—","EER","16.0–62.4% single; 19.1% naive; 5.9% learned","same eval set"],
           ["Indic fake recall","MMS-TTS [9] Indic","before/after Indic retrain","Recall","42%→82%","single generator (MMS-TTS)"],
           ["Genuine-Indic FP","genuine Indic speech","channel-aware","FPR","36.3%→6.3%","tested Indic conditions"],
           ["Calibration","held-out","—","ECE / Brier","0.044 / 0.048","calibration distribution"]],
          [24*mm,32*mm,34*mm,18*mm,34*mm,28*mm]),
      Spacer(1,3),
      P("<b>What is measured vs engineered.</b> Detection EER, the detector/fusion comparison, calibration, "
        "and the Indic recall / false-positive figures are <b>measured</b>. Telephony robustness is "
        "primarily <b>engineered</b> via G.711/8&nbsp;kHz augmentation and a narrowband path; per-window "
        "compute latency and live-network robustness are <b>not yet formally benchmarked</b> and are flagged "
        "as such throughout.", SMALL)]

# ---- 8 Telephony hardening ----
E += [head("8","Telephony Hardening"),
      P("Telephone audio is not studio audio. VoxShield's pipeline is native to G.711 μ-law at 8&nbsp;kHz, "
        "with the ~300–3400&nbsp;Hz narrowband limit [4], codec distortion, background noise and packet "
        "loss treated as first-class conditions rather than nuisances. Speech is gated with Silero VAD [10] "
        "and processed in 3-second sliding windows at a 1-second hop, so a verdict can form within the "
        "first seconds of a call and be refined as more audio arrives."),
      tbl([["Stage","Studio speech","Telephone speech","VoxShield handling"],
           ["Bandwidth","Full-band (≤ ~20 kHz)","~0.3–3.4 kHz","narrowband-aware features + routing"],
           ["Sample rate","16–48 kHz","8 kHz","native 8 kHz path"],
           ["Coding","Lossless / high-rate","G.711 μ-law","codec-condition training/eval"],
           ["Artifacts kept","HF synthesis cues","much HF removed","DSP + fusion recover residual cues"]],
          [26*mm,42*mm,40*mm,62*mm]),
      Spacer(1,4),
      P("<b>What is actually tested vs engineered</b> — an important distinction for telephony claims:"),
      tbl([["Telephony condition","Status in this work"],
           ["G.711 μ-law 8 kHz inference pipeline","Implemented"],
           ["Narrowband / codec training augmentation","Implemented"],
           ["Simulated narrowband (augmented) evaluation","Evaluated (augmented conditions)"],
           ["Real PSTN / SIP captured-call evaluation","Pending (not yet measured)"]],
          [95*mm,75*mm])]

# ---- 9 Indic-aware (flagship) ----
E += [head("9","Indic-Aware Detection"),
      P("A multilingual pretrained backbone does <b>not</b> automatically make a deepfake detector "
        "language-robust: synthesis artifacts and genuine-speaker distributions both shift across languages, "
        "so a detector tuned on English can misjudge Indic speech in both directions — missing Indic fakes "
        "and over-flagging genuine Indic speakers. Public Indian-language resources such as AI4Bharat's "
        "IndicVoices [13] help ground genuine Indic speech, while multilingual TTS such as Meta's MMS [9] "
        "can synthesise Indic fakes. VoxShield adds an Indic-aware detection path with on-device "
        "language-ID routing and retrains on Indic material. Measured on the tested Indic conditions, this "
        "moved two metrics substantially — <b>without regressing English</b>, whose EER stayed at 5.9%:"),
      KeepTogether([Fig(fig_indic()),
        P("Figure 4 — Indic-aware retraining: recall on MMS-TTS [9] Indic deepfakes and false-positive rate "
          "on genuine Indic speech. These figures are specific to the tested Indic conditions and should not "
          "be read as covering every Indian language.", CAP)]),
      P("The false-positive result is the one a bank cares about most: over-flagging genuine customers is "
        "expensive and erodes trust, so cutting genuine-Indic false positives from 36.3% to 6.3% is as "
        "important as raising recall.")]

# ---- 10 Results & ablation ----
E += [head("10","Results &amp; Ablation"),
      P("Every number is labelled with its exact evaluation. EER is not accuracy; Indic recall is not "
        "overall recall; a false-positive rate is not a false-negative rate. The headline results:"),
      tbl([["Evaluation setting","Metric","Baseline","VoxShield","Scope / reading"],
           ["Held-out In-the-Wild [7] (cross-dataset)","EER","16.0%*","<b>5.9%</b>","*best single model; fusion nearly 3× better"],
           ["MMS-TTS [9] Indic deepfakes","Recall","42%","<b>82%</b>","generator-specific; English EER unchanged (5.9%)"],
           ["Genuine Indic speech","False-positive rate","36.3%","<b>6.3%</b>","channel-aware; fewer genuine-user flags"],
           ["Held-out In-the-Wild","ROC-AUC","—","<b>0.983</b>","threshold-independent separability"]],
          [50*mm,24*mm,20*mm,22*mm,54*mm]),
      Spacer(1,4),
      P("<b>Why multi-detector fusion? (ablation).</b> We measured the standard single-model approaches "
        "first. On the same evaluation, individual detectors range from 16.0% to 62.4% EER, and — critically "
        "— <b>naive averaging (19.1%) is worse than the best single model (16.0%)</b>. Only the "
        "<i>learned</i> meta-stacker, which assigns each detector a weight (some negative, i.e. it learns "
        "which detectors to distrust), reaches 5.9%. Under this evaluation the evidence supports the value of "
        "<i>learned</i> fusion: the observed performance gain (EER) comes from the fusion, not any single "
        "model. This does not by itself establish universal fusion superiority."),
      KeepTogether([Fig(fig_scoreboard()),
        P("Figure 5 — Equal Error Rate by configuration. Fusion beats every single detector and, importantly, "
          "beats naive averaging — evidence that the gain is from learned weighting, not model choice alone.", CAP)]),
      P("<b>Calibration.</b> After Platt calibration, scores are intended to approximate empirical event "
        "probabilities under the calibration distribution — what a bank acts on rather than a raw ranking; "
        "calibration quality is <b>ECE 0.044, Brier 0.048</b>, and an abstain band leaves the uncertain "
        "middle unforced. Probabilistic validity outside the evaluated distribution is not claimed. "
        "<b>Scope.</b> All figures are research-corpus / generator-/language-specific evaluations under "
        "held-out (and, for telephony, augmented narrowband) conditions — not production or live-network "
        "measurements. VoxShield is a working prototype (TRL-5), not a deployed service.", SMALL)]

# ---- 11 Real-time + explainability ----
E += [head("11","Real-Time Operation &amp; Explainability"),
      P("<b>Streaming, not batch.</b> Scoring runs on 3-second windows at a 1-second hop, so a first verdict "
        "forms as soon as a 3-second window fills and is then refined continuously — a verdict after the "
        "call ends is forensics, not protection. This is a streaming-capable architecture designed for "
        "early-call risk formation; <b>per-window compute latency and end-to-end system latency are not yet "
        "formally benchmarked</b> on target hardware and are stated as pending, not claimed."),
      P("<b>Explainability.</b> Each verdict carries reason codes derived from the detector outputs and the "
        "89-dim feature bank, so an analyst sees <i>why</i> a call scored high rather than a bare label. The "
        "implemented codes are:"),
      bullets([
        "<b>SSL</b> — high neural-synthesis likelihood from the self-supervised detectors",
        "<b>PH</b> — unnaturally regular phase / group-delay structure",
        "<b>HF</b> — anomalous energy in the &gt;6&nbsp;kHz band (wideband audio only; not available under 8&nbsp;kHz telephony)",
        "<b>PR</b> — missing or flattened prosody (F0, jitter, shimmer)",
        "<b>BR</b> — absence of natural breath (TTS inserts silence, not breathing)",
      ], s=st("bu2",parent=BUL,fontSize=9.2)),
      P("These are signal-derived indicators surfaced to the analyst; we do not claim they are formally "
        "faithfulness-tested explanations.", SMALL)]

# ---- 12 Fraud workflow ----
E += [head("12","Fraud Workflow Integration"),
      P("VoxShield is a decision-support layer, not an autonomous account-blocking system. Its output feeds "
        "an institution's existing fraud process:"),
      KeepTogether([Fig(fig_workflow()), P("Figure 6 — Risk-tiered routing into an existing fraud workflow; humans stay in the loop.", CAP)])]

# ---- 13 Security & deployment ----
E += [head("13","Security &amp; Deployment"),
      P("VoxShield is architected to support institutional data-governance requirements: it can run on "
        "controlled or on-premises infrastructure, so raw call audio need not be sent to an external "
        "inference service, and it can operate in air-gapped configurations where required. The design "
        "anticipates auditability, model/version management, and secure integration with banking and "
        "contact-centre systems. We do not claim formal regulatory certification; a compliance assessment "
        "against specific frameworks would be part of any real deployment.")]

# ---- 14 Innovation / moat ----
E += [head("14","Innovation &amp; Defensibility"),
      P("The contribution is not a single new algorithm — the component techniques are published. It is the "
        "<b>integration under one hard set of constraints</b>: Indic-language adaptation + telephony-native "
        "processing + learned multi-detector fusion + specialised routing + calibrated explainable risk + "
        "fraud-workflow integration + controlled-infrastructure deployment, holding all of them "
        "simultaneously. Each constraint individually is known; satisfying them together — e.g. keeping "
        "English EER flat while lifting Indic recall, on 8&nbsp;kHz audio, on-prem — is the engineering "
        "difficulty."),
      tbl([["Implemented today (measured)","Future defensibility (proposed)"],
           ["Indic-aware path + language-ID routing","Privacy-preserving institutional data flywheel"],
           ["G.711 8 kHz telephony hardening","Proprietary Indic synthetic-voice corpus"],
           ["Learned five-detector meta-stacker + calibration","Broader generator diversity &amp; continual eval"],
           ["Explainable reason codes + SHA-256 audit","Bank-specific calibration"],
           ["Liveness challenge-response option","Production-scale SIP/VoIP integration"],
           ["On-prem / air-gapped architecture","Federated cross-institution learning"]],
          [85*mm,85*mm]),
      P("The left column is built and measured; the right column is future work and is labelled as such throughout.", SMALL)]

# ---- 15 Scalability (brief) ----
E += [head("15","Scalability"),
      P("The same pipeline is intended to sit behind bank contact centres, telco fraud systems and "
        "SIP/VoIP gateways, feeding fraud-analyst dashboards. Streaming, windowed inference makes "
        "per-call cost predictable; on-prem deployment keeps data in place. Concrete throughput and "
        "latency figures are deferred to measured benchmarks on target hardware (future work).")]

# ---- 16 Limitations ----
E += [head("16","Limitations &amp; Validation Targets"),
      P("We state these plainly; several are active validation targets rather than solved problems.", SMALL),
      bullets([
        "<b>Cross-generator generalisation</b> — the Indic fake evidence uses MMS-TTS as the generator; generator-disjoint testing (train on some synthesis systems, test on entirely unseen ones) is a key validation target and is not yet demonstrated.",
        "<b>Speaker disjointness</b> — train/test speaker overlap is not documented here; speaker-disjoint evaluation is needed to isolate spoof detection from speaker-memorisation effects.",
        "<b>Real-network telephony</b> — telephony results are on augmented narrowband, not captured PSTN/SIP audio; real-network evaluation is pending.",
        "<b>Very short segments</b> and heavy background noise reduce reliability.",
        "<b>Code-switching and language imbalance</b> — Indic results are specific to tested conditions, not all Indian languages.",
        "<b>Adversarial adaptation</b> — attackers aware of the detector may adapt.",
        "<b>Benchmark-to-production gap</b> — corpus/augmented results are not live-network guarantees.",
      ])]

# ---- 17 Future work + 18 conclusion ----
E += [head("17","Future Work"),
      P("Measured latency/throughput benchmarks on target hardware; a formal ablation report; more Indic "
        "languages and a larger real-world fraud corpus; privacy-preserving federated learning across "
        "institutions; continuous model adaptation and better calibration; adversarial-robustness "
        "hardening; and measured production-scale SIP integration with human-in-the-loop fraud operations."),
      head("18","Conclusion"),
      P("VoxShield addresses a specific, under-served deployment gap: Indic-language + telephony-quality + "
        "real-time + controlled-infrastructure + explainable voice-deepfake detection for financial fraud. "
        "It is an honest prototype with measured, carefully-scoped evidence — 5.9% EER on held-out "
        "In-the-Wild audio, and large Indic-specific gains in recall and false-positive rate after "
        "Indic-aware retraining — and a clear separation between what is built and what is proposed."),
      rule(RED,1.0,6,6)]

# ---- References ----
E += [head("19","References")]
for r in REFS:
    E.append(P(r, REF))
E += [Spacer(1,6),
      P("Public artifacts: GitHub (DG10911/voxshield) · HuggingFace (dg10911/voxshield-checkpoints) · "
        "Team DigiSeva · Contact: devanshgoenka03@gmail.com", SMALL)]

OUT="VOXSHIELD_GBT_PAPER.pdf"
doc=SimpleDocTemplate(OUT,pagesize=A4,topMargin=16*mm,bottomMargin=20*mm,leftMargin=20*mm,rightMargin=20*mm,
                      title="VoxShield — GBT BuildStorm 2026 Round 1 Paper",author="Team DigiSeva — Devansh Goenka")
doc.build(E,onFirstPage=deco,onLaterPages=deco)
print("wrote",OUT)
