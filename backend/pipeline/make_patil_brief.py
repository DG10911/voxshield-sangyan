#!/usr/bin/env python3
"""VoxShield — Technical Research Brief for Prof. Hemant A. Patil (DA-IICT).
Researcher-to-researcher tone. Honest about implemented vs proposed. Same
black/white/deep-red aesthetic. Figures drawn as vectors; no stock images.
Verified Patil themes/papers filled from research (patil_refs.py) after search.
"""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, ListFlowable, ListItem, KeepTogether, Flowable)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF

INK=colors.HexColor("#111418"); RED=colors.HexColor("#B01326"); REDD=colors.HexColor("#7C0D1B")
RTINT=colors.HexColor("#FBEDEF"); GREY=colors.HexColor("#5B6470"); LGREY=colors.HexColor("#9AA3AE")
PANEL=colors.HexColor("#F4F6F8"); LINEC=colors.HexColor("#D3D9E0"); WHITE=colors.white
CW=A4[0]-40*mm
ss=getSampleStyleSheet()
def st(n,**k): k.setdefault("parent",ss["Normal"]); return ParagraphStyle(n,**k)
TITLE=st("t",fontName="Helvetica-Bold",fontSize=21,leading=24,textColor=INK,alignment=TA_CENTER,spaceAfter=2)
SUBT =st("s",fontName="Helvetica",fontSize=10.5,leading=14,textColor=GREY,alignment=TA_CENTER)
KICK =st("k",fontName="Helvetica-Bold",fontSize=8.5,leading=11,textColor=RED,alignment=TA_CENTER,spaceAfter=2)
H    =st("h",fontName="Helvetica-Bold",fontSize=12.5,leading=15,textColor=INK,spaceBefore=11,spaceAfter=4)
BODY =st("b",fontName="Helvetica",fontSize=9.6,leading=13.6,alignment=TA_JUSTIFY,textColor=colors.HexColor("#1A1D21"),spaceAfter=5)
BUL  =st("bu",parent=BODY,spaceAfter=2)
CAP  =st("cap",fontName="Helvetica-Oblique",fontSize=8,leading=10.5,textColor=GREY,alignment=TA_CENTER,spaceBefore=3,spaceAfter=8)
CELL =st("c",fontName="Helvetica",fontSize=8.2,leading=10.6,textColor=colors.HexColor("#1A1D21"))
CELLH=st("ch",fontName="Helvetica-Bold",fontSize=8.3,leading=10.6,textColor=WHITE)
SMALL=st("sm",fontName="Helvetica",fontSize=8,leading=11,textColor=GREY)
REF  =st("rf",fontName="Helvetica",fontSize=7.9,leading=11,textColor=colors.HexColor("#2A2E33"),spaceAfter=2)
QH   =st("qh",fontName="Helvetica-Bold",fontSize=9.8,leading=13,textColor=REDD,spaceBefore=6,spaceAfter=1)

def P(t,s=BODY): return Paragraph(t,s)
def head(n,t): return Paragraph(f'<font color="#B01326">{n}</font>&nbsp;&nbsp;{t}',H)
def rule(c=LINEC,th=0.6,sb=2,sa=8): return HRFlowable(width="100%",thickness=th,color=c,spaceBefore=sb,spaceAfter=sa)
def bullets(items,s=BUL): return ListFlowable([ListItem(P(x,s),leftIndent=6,value="•") for x in items],bulletType="bullet",leftIndent=12,spaceAfter=6)
def tbl(rows,widths,header=True):
    data=[[Paragraph(str(c),CELLH if(header and i==0)else CELL) for c in r] for i,r in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign="LEFT")
    cmds=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
          ("LINEBELOW",(0,0),(-1,-1),0.4,LINEC),("BOX",(0,0),(-1,-1),0.6,LGREY)]
    if header:
        cmds+=[("BACKGROUND",(0,0),(-1,0),INK),("LINEBELOW",(0,0),(-1,0),1.0,RED)]
        for r in range(1,len(rows)):
            if r%2==0: cmds.append(("BACKGROUND",(0,r),(-1,r),PANEL))
    t.setStyle(TableStyle(cmds)); return t
def callout(title,body):
    inner=[Paragraph(f'<b><font color="#7C0D1B">{title}</font></b>',st("co",fontName="Helvetica-Bold",fontSize=9,leading=12)),
           Paragraph(body,st("cob",fontName="Helvetica",fontSize=9,leading=12.5,textColor=INK))]
    t=Table([[inner]],colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),RTINT),("BOX",(0,0),(-1,-1),1,RED),
                           ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
                           ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t

# ---- diagram primitives ----
def _box(d,x,y,w,h,title,sub=None,fill=WHITE,stroke=INK,tc=INK,fs=8.2,bold=True,r=3):
    d.add(Rect(x,y,w,h,rx=r,ry=r,fillColor=fill,strokeColor=stroke,strokeWidth=1))
    if sub:
        d.add(String(x+w/2,y+h/2+2,title,textAnchor="middle",fontName="Helvetica-Bold" if bold else "Helvetica",fontSize=fs,fillColor=tc))
        d.add(String(x+w/2,y+h/2-8,sub,textAnchor="middle",fontName="Helvetica",fontSize=fs-1.4,fillColor=tc))
    else:
        d.add(String(x+w/2,y+h/2-3,title,textAnchor="middle",fontName="Helvetica-Bold" if bold else "Helvetica",fontSize=fs,fillColor=tc))
def _varrow(d,x,y0,y1,c=RED):
    d.add(Line(x,y0,x,y1,strokeColor=c,strokeWidth=1.4)); d.add(Polygon([x-3,y1+5,x+3,y1+5,x,y1],fillColor=c,strokeColor=c))
def _harrow(d,x0,x1,y,c=RED):
    d.add(Line(x0,y,x1,y,strokeColor=c,strokeWidth=1.4)); d.add(Polygon([x1-5,y-3,x1-5,y+3,x1,y],fillColor=c,strokeColor=c))
class Fig(Flowable):
    def __init__(self,d): self.d=d; self.width=d.width; self.height=d.height
    def wrap(self,a,b): return (self.width,self.height)
    def draw(self): renderPDF.draw(self.d,self.canv,0,0)

def fig_domain():
    W,Hh=CW,80; d=Drawing(W,Hh)
    labs=[("Benchmark / studio","clean, wideband, known TTS"),("Indic language","phonetics shift"),
          ("Narrowband G.711","8 kHz, HF removed"),("Noise / streaming","real call conditions"),
          ("Unseen generators","distribution shift")]
    n=len(labs); g=12; bw=(W-(n-1)*g)/n; bh=44; y=20
    for i,(t,s) in enumerate(labs):
        x=i*(bw+g); fill=RTINT if i>=2 else PANEL; stroke=RED if i>=2 else INK; tc=REDD if i>=2 else INK
        _box(d,x,y,bw,bh,t,s,fill=fill,stroke=stroke,tc=tc,fs=8.0)
        if i<n-1: _harrow(d,x+bw+1,x+bw+g-1,y+bh/2)
    d.add(String(W/2,7,"Each step widens the gap between where detectors are trained and where fraud calls occur",
                 textAnchor="middle",fontName="Helvetica-Oblique",fontSize=7.3,fillColor=GREY))
    return d

def fig_arch():
    W=CW; bh=27; arr=14; ph=76; top=6
    Hh=top+3*bh+ph+3*bh+6*arr+6
    d=Drawing(W,Hh); cx=W/2; bw=200; x=cx-bw/2; cur=[Hh-top]
    def pbox(t,s,fl,stk,tc,fs=8.1):
        _box(d,x,cur[0]-bh,bw,bh,t,s,fill=fl,stroke=stk,tc=tc,fs=fs); cur[0]-=bh
    def arrow(): _varrow(d,cx,cur[0]-2,cur[0]-arr+3); cur[0]-=arr
    for t,s in [("Call audio","8 kHz G.711 μ-law"),("Silero VAD","voice-activity gating"),
                ("Windowing","3 s window · 1 s hop · normalize")]:
        pbox(t,s,PANEL,INK,INK); arrow()
    pw=W-4; px=2; py=cur[0]-ph
    d.add(Rect(px,py,pw,ph,rx=4,ry=4,fillColor=colors.HexColor("#FCFCFD"),strokeColor=RED,strokeWidth=1.2,strokeDashArray=[3,2]))
    d.add(String(px+8,py+ph-12,"COMPLEMENTARY DETECTOR FAMILIES",fontName="Helvetica-Bold",fontSize=7.6,fillColor=RED))
    dets=["Acoustic DSP","wav2vec2","XLS-R 300M","DistilHuBERT","LFCC+CQCC"]
    dn=len(dets); dg=8; dbw=(pw-16-(dn-1)*dg)/dn; dby=py+9; dbh=40
    for i,nm in enumerate(dets):
        dx=px+8+i*(dbw+dg); d.add(Rect(dx,dby,dbw,dbh,rx=3,ry=3,fillColor=WHITE,strokeColor=INK,strokeWidth=0.9))
        d.add(String(dx+dbw/2,dby+dbh/2-2,nm,textAnchor="middle",fontName="Helvetica-Bold",fontSize=7.4,fillColor=INK))
    cur[0]=py; arrow()
    for t,s,tc,fl,stk in [("Learned meta-fusion","logistic stacker",INK,PANEL,INK),
                          ("Indic → telephony → general routing","specialised paths",REDD,RTINT,RED),
                          ("Platt calibration → risk + reason codes","LOW / MEDIUM / HIGH",INK,PANEL,INK)]:
        pbox(t,s,fl,stk,tc,fs=7.9)
        if t!="Platt calibration → risk + reason codes": arrow()
    return d

def fig_indic():
    W,Hh=CW,150; d=Drawing(W,Hh)
    def pair(ox,ow,title,b,n):
        d.add(String(ox+ow/2,Hh-14,title,textAnchor="middle",fontName="Helvetica-Bold",fontSize=8.4,fillColor=INK))
        base_y=26; sc=88/100.0; bw=46; g=34; x0=ox+(ow-(2*bw+g))/2
        for k,(val,lab,col,tc) in enumerate([(b,"before",LGREY,GREY),(n,"after",RED,REDD)]):
            xx=x0+k*(bw+g); h=val*sc; d.add(Rect(xx,base_y,bw,h,fillColor=col,strokeColor=None))
            d.add(String(xx+bw/2,base_y+h+3,f"{val:g}%",textAnchor="middle",fontName="Helvetica-Bold",fontSize=8,fillColor=tc))
            d.add(String(xx+bw/2,base_y-11,lab,textAnchor="middle",fontName="Helvetica",fontSize=7,fillColor=GREY))
        d.add(Line(ox+6,base_y,ox+ow-6,base_y,strokeColor=INK,strokeWidth=0.8))
    pair(0,W/2-6,"Indic recall (MMS-TTS fakes) ↑",42,82)
    pair(W/2+6,W/2-6,"Genuine-Indic false positives ↓",36.3,6.3)
    return d

# ---- verified references (shared) + Patil themes (filled from research) ----
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
try:
    from patil_refs import PATIL_INTERESTS, PATIL_PAPERS, REFS
except Exception:
    from gbt_refs import REFS
    PATIL_INTERESTS="audio anti-spoofing, voice liveness detection, and spoofed-speech countermeasures"
    PATIL_PAPERS=[]

E=[]
# ===== P1 Snapshot =====
E += [P("TECHNICAL RESEARCH BRIEF  ·  FOR PROF. HEMANT A. PATIL (DA-IICT)  ·  CONFIDENTIAL DRAFT",KICK),
      P("VoxShield",TITLE),
      P("Indic-Language Voice-Deepfake Detection under Telephony Conditions",SUBT),
      P("A multi-detector, telephony-hardened prototype for financial-fraud call screening",st("vp",fontName="Helvetica-Oblique",fontSize=10,leading=13,textColor=INK,alignment=TA_CENTER)),
      Spacer(1,6),
      callout("CURRENT STATUS — early-stage research prototype.",
              "We treat the results below as evidence/hypotheses to stress-test, not as claims of production readiness. "
              "We are writing specifically to ask whether our evaluation methodology is rigorous enough — particularly "
              "around cross-generator generalisation and telephony/codec robustness."),
      Spacer(1,6),
      P("<b>Strongest measured results (each with its evaluation scope).</b>",BODY),
      tbl([["Result","Value","Evaluation scope"],
           ["Meta-fusion EER","5.9%","held-out In-the-Wild (cross-dataset)"],
           ["Best single detector (XLS-R 300M)","16.0% EER","same evaluation set"],
           ["Naive averaging","19.1% EER","same set (worse than best single)"],
           ["Indic fake recall","42% → 82%","MMS-TTS-generated Indic fakes; English EER unchanged"],
           ["Genuine-Indic false-positive rate","36.3% → 6.3%","tested Indic conditions; channel-aware"],
           ["ROC-AUC · calibration","0.983 · ECE 0.044","held-out; calibration distribution"]],
          [58*mm,26*mm,86*mm]),
      P("EER is not accuracy; Indic recall is not overall recall; the false-positive rate is not universal. "
        "Scopes are stated precisely and are not conflated.",SMALL)]

# ===== P2 Research question =====
E += [head("1","The Research Question"),
      P("<b>Central question:</b> can voice-deepfake detectors that perform well on benchmark / studio speech "
        "remain reliable when speech is Indic-language, narrowband (8&nbsp;kHz G.711 μ-law), noisy, streamed, "
        "and produced by synthesis systems not seen during training? Each of these is a distribution shift, "
        "and they compound in exactly the setting we care about — a live fraud call to a bank."),
      Fig(fig_domain()), P("Figure 1 — The domain-gap chain between benchmark conditions and real fraud calls.",CAP),
      P("Our interest is less 'is this clip synthetic?' in the abstract and more: under these compounded "
        "shifts, what evaluation protocol would let us (and a reviewer) trust a reported number?")]

# ===== P3 Architecture =====
E += [head("2","System Architecture (what is implemented)"),
      P("VoxShield is a streaming pipeline. Each block below is implemented in the current prototype."),
      KeepTogether([Fig(fig_arch()), P("Figure 2 — Implemented inference pipeline: telephony audio → VAD → windowing → "
                    "complementary detectors → learned fusion → routing → calibrated risk + reason codes.",CAP)]),
      tbl([["Block","Input → process → output"],
           ["Front-end","8 kHz G.711 μ-law → Silero VAD → 3 s windows / 1 s hop → normalized frames"],
           ["Feature bank","frames → 89-dim vector at a 16 kHz analysis rate (LFCC, CQCC, group-delay phase, F0/prosody, jitter, shimmer, and a >6 kHz band)"],
           ["Detectors","features/audio → 5 complementary detector scores (DSP, wav2vec2, XLS-R 300M, DistilHuBERT, LFCC+CQCC)"],
           ["Fusion + routing","scores → learned logistic stacker → Indic/telephony/general routing → single score"],
           ["Decision","score → Platt calibration → LOW/MEDIUM/HIGH + reason codes → fraud workflow"]],
          [26*mm,144*mm])]

# ===== P4 Feature/model design =====
E += [head("3","Feature &amp; Model Design — Rationale"),
      P("We combine detector families that fail in different ways. <b>This is a working hypothesis, not a "
        "proven independence result</b> — we have not yet run a formal detector-error correlation analysis."),
      bullets([
        "<b>A. Signal-level evidence</b> — LFCC, CQCC [12], group-delay phase, prosody (F0, jitter, shimmer), and a &gt;6&nbsp;kHz band. (Features are computed at a 16&nbsp;kHz analysis rate, 8&nbsp;kHz Nyquist; the &gt;6&nbsp;kHz band is informative only for wideband audio and is empty under 8&nbsp;kHz G.711 — we treat that emptiness itself as a narrowband indicator rather than expecting HF artifacts there.)",
        "<b>B. Learned representations</b> — wav2vec2 [5], XLS-R 300M [6] (multilingual), DistilHuBERT [11]: self-supervised features with different pretraining.",
        "<b>C. Fusion</b> — a learned logistic meta-stacker over detector outputs (some weights negative), rather than naive averaging.",
        "<b>D. Routing</b> — Indic-aware → telephony/narrowband → general, selected by on-device language-ID.",
      ]),
      P("The measured detector/fusion comparison (§5) is our first evidence for the fusion hypothesis; a "
        "per-family ablation under disjoint conditions is a validation target, not yet complete.",SMALL)]

# ===== P5 Telephony =====
E += [head("4","Telephony Hardening — tested vs engineered"),
      P("Telephone audio discards most detail above ~3.4&nbsp;kHz [4] — often exactly where synthesis "
        "artifacts live — and adds codec distortion, noise and packet loss. We build for this, but we are "
        "careful to separate what is engineered from what is measured:"),
      tbl([["Telephony condition","Status in this work"],
           ["G.711 μ-law 8 kHz inference pipeline","Implemented"],
           ["Narrowband / codec training augmentation","Implemented"],
           ["Simulated narrowband (augmented) evaluation","Evaluated under augmented conditions"],
           ["Real PSTN / SIP captured-call evaluation","Not yet performed (pending)"]],
          [95*mm,75*mm]),
      P("We would especially value your view on whether augmentation-based telephony evaluation is an "
        "acceptable proxy, and what a minimal real-network evaluation should look like.",SMALL)]

# ===== P6 Indic =====
E += [head("5","Indic Experiment"),
      P("We synthesised an Indic fake set with MMS-TTS [9], added an Indic-aware path with language-ID "
        "routing, and retrained. On the tested Indic conditions:"),
      KeepTogether([Fig(fig_indic()),
        P("Figure 3 — Indic-aware retraining: recall on MMS-TTS Indic fakes and genuine-Indic false-positive rate.",CAP)]),
      P("<b>What it demonstrates:</b> language-specific adaptation can materially change detector behaviour "
        "under these conditions, and English EER did not regress (5.9%). <b>What it does not demonstrate:</b> "
        "it does not establish robustness across all Indic languages, all speakers, other generators, or "
        "real deployment — the evidence is specific to MMS-TTS and the tested set.")]

# ===== P7 Evaluation methodology =====
E += [head("6","Evaluation Methodology (with honest gaps)"),
      P("The most useful thing we can show you is exactly how the numbers were obtained — including what we "
        "have not pinned down. 'Requires confirmation' marks details not yet documented on our side.",SMALL),
      tbl([["Experiment","Source / generator","Composition","Channel","Train/test split","Metric → result"],
           ["English detection","In-the-Wild [7]","genuine + spoofed (n: requires confirmation)","clean + augmented","cross-dataset held-out; speaker split: requires confirmation","EER → 5.9%"],
           ["Detector/fusion","common scored set","per-detector scores","as above","same eval set","EER → 16.0–62.4% / 19.1% / 5.9%"],
           ["Indic fake recall","MMS-TTS [9]","synthetic Indic fakes","clean","before/after retrain; generator = MMS-TTS only","Recall → 42%→82%"],
           ["Genuine-Indic FP","genuine Indic speech","10 languages","channel-aware","tested conditions","FPR → 36.3%→6.3%"],
           ["Calibration","held-out","—","—","—","ECE 0.044 · Brier 0.048"]],
          [26*mm,28*mm,34*mm,22*mm,34*mm,26*mm])]

# ===== P8 Questions for expert review =====
E += [head("7","Research Questions for Expert Review"),
      P("These are the questions where your expertise would most change what we do next. We have <b>not</b> "
        "performed the proposed experiments below; they are how we currently think the claims should be tested."),
      P("Q1 — Cross-generator generalisation.",QH),
      P("Our Indic evidence uses a single generator (MMS-TTS). What is the most rigorous way to show the "
        "detector generalises to unseen synthesis systems? We are considering: train on generators A+B+C, "
        "test on held-out D+E, reporting EER, ROC-AUC, TPR@fixed-FPR, and per-generator EER. Is this the "
        "right framing, and which generator families would you prioritise?"),
      P("Q2 — Telephony / codec robustness.",QH),
      P("What evaluation protocol would you recommend for 8&nbsp;kHz G.711, noise and packet loss — clean→codec, "
        "a codec→noise→packet-loss cascade, or real captured PSTN/SIP audio? What baselines should accompany it?"),
      P("Q3 — Generator × codec interaction.",QH),
      P("Could a model learn <i>codec</i> artifacts rather than <i>synthesis</i> artifacts? We propose evaluating a "
        "matrix (below) to separate the two. (Proposed, not yet run.)"),
      tbl([["","Clean","G.711","Noise","Packet loss"],
           ["Generator A","train","eval","eval","eval"],
           ["Generator B","train","eval","eval","eval"],
           ["Generator C","train","eval","eval","eval"],
           ["Unseen D / E","eval*","eval*","eval*","eval*"]],
          [34*mm,26*mm,26*mm,26*mm,32*mm]),
      P("*held-out generators — the key generalisation cells.  Proposed evaluation design, not results.",SMALL),
      P("Q4 — Speaker disjointness.",QH),
      P("We have not yet documented speaker overlap between train and test. Should speaker-disjoint <i>and</i> "
        "generator-disjoint evaluation be the principal benchmark, to separate spoof detection from speaker memorisation?"),
      P("Q5 — Disentangling generalisation axes.",QH),
      P("How should evaluation separate language vs generator vs speaker vs channel generalisation — is a factorial design practical here?"),
      P("Q6 — Metric selection for fraud screening.",QH),
      P("For real fraud screening, which metrics are most informative — EER, ROC-AUC, PR-AUC, TPR@1%/0.1% FPR, FNR, "
        "calibration error, or t-DCF [8]? We currently lead with EER + AUC + ECE and would value your view.")]

# ===== P9 Limitations / failure modes =====
E += [head("8","Limitations &amp; Failure Modes"),
      tbl([["Risk","Why it matters","Current evidence","Needed experiment"],
           ["Unseen generators","attackers use new TTS","MMS-TTS only","generator-disjoint eval"],
           ["Real-network telephony","augmentation ≠ PSTN","augmented only","captured-call eval"],
           ["Speaker overlap","inflates EER","not documented","speaker-disjoint split"],
           ["Very short / noisy speech","calls are messy","not isolated","duration/noise sweep"],
           ["Code-switching / lang. imbalance","Indic reality","tested subset","per-language study"],
           ["Adversarial adaptation","attacker adapts","none","adversarial eval"]],
          [34*mm,42*mm,40*mm,54*mm])]

# ===== P10 Roadmap + ask =====
E += [head("9","Experiment Roadmap (priority-ordered)"),
      tbl([["#","Experiment","Metric","Interpretation sought"],
           ["1","Speaker-disjoint evaluation","EER, AUC","spoof detection vs speaker memorisation"],
           ["2","Generator-disjoint evaluation","EER by generator","true cross-generator generalisation"],
           ["3","Codec / channel robustness","EER under G.711/noise/loss","channel vs synthesis cues"],
           ["4","Per-language Indic evaluation","EER, FPR per language","language-wise reliability"],
           ["5","Detector-family ablation","ΔEER per family","evidence for fusion hypothesis"],
           ["6","Calibration analysis","ECE, Brier, reliability curve","probability trustworthiness"],
           ["7","Real telephone recordings","EER on captured calls","benchmark-to-field gap"],
           ["8","Adversarial robustness","EER under attack","worst-case behaviour"]],
          [8*mm,52*mm,44*mm,66*mm]),
      P("We deliberately give no expected numbers — these are the experiments, not predictions.",SMALL)]

# ===== Relevance to Prof. Patil + ask =====
E += [head("10","Why We Are Writing to You"),
      P(f"Your published work on {PATIL_INTERESTS} is directly relevant to the specific questions above. "
        "Your feature work on instantaneous-frequency and cochlear-filter cues (CFCCIF) and group-delay "
        "methods [15,16] speaks to the phase/HF components of our 89-dim bank; your ASVspoof-generalisation "
        "survey [17] frames our central cross-generator question (Q1); your replay / energy-separation "
        "instantaneous-frequency work [18] relates to our channel-robustness questions (Q2–Q3); and your "
        "voice-liveness (pop-noise) line [19] bears directly on our liveness option and how we should "
        "validate it. We are not asking for generic mentorship — we are asking whether our evaluation "
        "protocol is scientifically sound and what we should test first.")]
if PATIL_PAPERS:
    E += [P("Representative work we drew on (verified):",SMALL), bullets(PATIL_PAPERS, s=SMALL)]
E += [Spacer(1,4),
      callout("What we would value from you (low-friction).",
              "1. Is our current evaluation methodology scientifically sound?  2. What would you change to establish "
              "cross-generator generalisation?  3. What telephony/codec evaluation protocol would you recommend?  "
              "4. Are we missing important anti-spoofing metrics or baselines?  5. Which failure mode should we "
              "investigate first?"),
      Spacer(1,6),
      P("Thank you for taking the time to review this work.",BODY),
      P("<b>Team DigiSeva · VoxShield · GBT BuildStorm 2026</b><br/>Contact: devanshgoenka03@gmail.com · "
        "GitHub: DG10911/voxshield",SMALL),
      rule(RED,1.0,6,6), head("11","References")]
for r in REFS: E.append(P(r,REF))

def deco(c,doc):
    c.saveState(); c.setFillColor(RED); c.rect(0,A4[1]-6,A4[0],6,fill=1,stroke=0)
    c.setStrokeColor(LINEC); c.setLineWidth(0.5); c.line(20*mm,14*mm,A4[0]-20*mm,14*mm)
    c.setFont("Helvetica",7.6); c.setFillColor(GREY)
    c.drawString(20*mm,9.5*mm,"VoxShield · Technical Research Brief · Team DigiSeva")
    c.drawRightString(A4[0]-20*mm,9.5*mm,f"{doc.page}"); c.restoreState()

OUT="VOXSHIELD_PATIL_BRIEF.pdf"
doc=SimpleDocTemplate(OUT,pagesize=A4,topMargin=16*mm,bottomMargin=20*mm,leftMargin=20*mm,rightMargin=20*mm,
                      title="VoxShield — Technical Research Brief (Prof. H. A. Patil)",author="Team DigiSeva")
doc.build(E,onFirstPage=deco,onLaterPages=deco)
print("wrote",OUT)
