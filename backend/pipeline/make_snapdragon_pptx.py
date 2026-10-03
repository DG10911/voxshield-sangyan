#!/usr/bin/env python3
"""VoxShield Edge — Snapdragon AI Lab pitch deck (.pptx). Dark premium theme."""
import os, sys
from pptx import Presentation
from pptx.util import Inches as I, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snap_content as C

BG=RGBColor(0x0A,0x0E,0x14); PANEL=RGBColor(0x14,0x1A,0x24); PANEL2=RGBColor(0x1B,0x22,0x2E)
LINE=RGBColor(0x2A,0x33,0x43); RED=RGBColor(0xEE,0x27,0x37); CY=RGBColor(0x35,0xC7,0xF2)
TXT=RGBColor(0xE9,0xED,0xF4); MUT=RGBColor(0x93,0x9E,0xB0); MUT2=RGBColor(0x63,0x6E,0x80)
OK=RGBColor(0x2F,0xD0,0x7B); AMB=RGBColor(0xF6,0xA9,0x35); WHITE=RGBColor(0xFF,0xFF,0xFF)
FONT="Segoe UI"; MONO="Consolas"
W,H=13.333,7.5
prs=Presentation(); prs.slide_width=I(W); prs.slide_height=I(H)
BLANK=prs.slide_layouts[6]

def slide():
    s=prs.slides.add_slide(BLANK)
    r=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,I(W),I(H)); r.fill.solid(); r.fill.fore_color.rgb=BG; r.line.fill.background()
    r.shadow.inherit=False
    # subtle top accent
    a=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,I(W),Pt(4)); a.fill.solid(); a.fill.fore_color.rgb=RED; a.line.fill.background(); a.shadow.inherit=False
    return s
def _noshadow(sp): sp.shadow.inherit=False
def box(s,x,y,w,h,fill=None,line=None,lw=1.0,rad=True):
    sp=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rad else MSO_SHAPE.RECTANGLE,I(x),I(y),I(w),I(h))
    if fill is None: sp.fill.background()
    else: sp.fill.solid(); sp.fill.fore_color.rgb=fill
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb=line; sp.line.width=Pt(lw)
    _noshadow(sp)
    try: sp.adjustments[0]=0.06
    except Exception: pass
    return sp
def txt(s,x,y,w,h,runs,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,sp_after=4,line=1.05):
    tb=s.shapes.add_textbox(I(x),I(y),I(w),I(h)); tf=tb.text_frame; tf.word_wrap=True; tf.vertical_anchor=anchor
    if isinstance(runs[0],tuple): runs=[runs]
    for i,para in enumerate(runs):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(sp_after); p.space_before=Pt(0); p.line_spacing=line
        for (t,sz,col,bold,*rest) in para:
            r=p.add_run(); r.text=t; f=r.font; f.size=Pt(sz); f.color.rgb=col; f.bold=bold; f.name=rest[0] if rest else FONT
    return tb
def kicker(s,t): txt(s,0.9,0.5,11,0.3,[[(t,11,RED,True)]])
def title(s,t,y=0.85,sz=30): txt(s,0.9,y,11.5,1.0,[[(t,sz,TXT,True)]])

# ---- title slide ----
def s_title():
    s=slide()
    box(s,0,0,W,H,fill=BG,rad=False)
    # big glow panel
    txt(s,0.9,2.0,11.5,0.4,[[(C.EVENT,13,CY,True)]])
    txt(s,0.88,2.5,11.7,1.3,[[(C.TITLE,58,WHITE,True)]])
    txt(s,0.9,3.7,11.5,0.7,[[(C.SUB,19,MUT,False)]])
    box(s,0.9,4.7,11.5,0.9,fill=PANEL,line=LINE)
    txt(s,1.15,4.82,11,0.7,[[(C.ONELINE,14.5,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE,line=1.15)
    # stat chips
    cw=2.75; gap=0.2; x=0.9
    for big,lab in C.STATS:
        b=box(s,x,5.85,cw,1.0,fill=PANEL2,line=RED,lw=1.0)
        txt(s,x,5.95,cw,0.45,[[(big,22,RED,True,MONO)]],align=PP_ALIGN.CENTER)
        txt(s,x+0.1,6.42,cw-0.2,0.4,[[(lab.replace("\n"," "),8.5,MUT,False)]],align=PP_ALIGN.CENTER,line=1.0)
        x+=cw+gap
    txt(s,0.9,6.98,11.5,0.35,[[(f"{C.AUTHOR} · on-device · private · Snapdragon NPU",11,MUT2,False)]])

# ---- bulleted content ----
def bullets(s,items,x=0.9,y=2.4,w=11.5,sz=15,gap=10,col=TXT):
    tb=s.shapes.add_textbox(I(x),I(y),I(w),I(H-y-0.6)); tf=tb.text_frame; tf.word_wrap=True
    for i,it in enumerate(items):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.space_after=Pt(gap); p.line_spacing=1.1
        r=p.add_run(); r.text="▸  "; r.font.size=Pt(sz); r.font.color.rgb=RED; r.font.bold=True; r.font.name=FONT
        r2=p.add_run(); r2.text=it; r2.font.size=Pt(sz); r2.font.color.rgb=col; r2.font.name=FONT
    return tb
def s_bul(k,t,body=None,items=None,note=None):
    s=slide(); kicker(s,k); title(s,t)
    y=2.15
    if body: txt(s,0.9,1.95,11.5,1.0,[[(body,15,MUT,False)]],line=1.2); y=3.15
    if items: bullets(s,items,y=y)
    if note: txt(s,0.9,H-0.85,11.5,0.5,[[(note,11,MUT2,False)]],line=1.15)

# ---- flow (horizontal chips) ----
def flow(s,items,y,accent=CY,h=0.72,fs=12):
    n=len(items); gap=0.28; total=11.5; bw=(total-(n-1)*gap)/n; x=0.9
    for i,it in enumerate(items):
        last=i==n-1
        box(s,x,y,bw,h,fill=PANEL2 if not last else PANEL,line=accent if last else LINE,lw=1.0)
        txt(s,x+0.05,y,bw-0.1,h,[[(it,fs,accent if last else TXT,last)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE,line=1.0)
        if not last:
            ar=s.shapes.add_shape(MSO_SHAPE.CHEVRON,I(x+bw+0.02),I(y+h/2-0.12),I(gap-0.04),I(0.24))
            ar.fill.solid(); ar.fill.fore_color.rgb=RED; ar.line.fill.background(); _noshadow(ar)
        x+=bw+gap

def s_solution(k,t,body,fl):
    s=slide(); kicker(s,k); title(s,t)
    txt(s,0.9,2.0,11.5,1.3,[[(body,16,MUT,False)]],line=1.25)
    txt(s,0.9,3.9,11.5,0.3,[[("OPERATIONAL FLOW",11,CY,True)]])
    flow(s,fl,4.35,accent=RED,h=0.8,fs=13)
    txt(s,0.9,5.6,11.5,0.4,[[("Decision support for a fraud analyst — ",13,MUT,False),("never automatic blocking.",13,OK,True)]])

def s_arch(k,t,steps,note):
    s=slide(); kicker(s,k); title(s,t)
    # two rows of chips
    row1=steps[:4]; row2=steps[4:]
    flow(s,row1,2.5,accent=CY,h=0.85,fs=12.5)
    flow(s,row2,3.9,accent=CY,h=0.85,fs=12.5)
    box(s,0.9,5.35,11.5,1.1,fill=PANEL,line=LINE)
    txt(s,1.15,5.5,11,0.85,[[(note,14,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE,line=1.2)

def s_snap(k,t,pipe,items):
    s=slide(); kicker(s,k); title(s,t)
    txt(s,0.9,2.0,11.5,0.3,[[("ON-DEVICE INFERENCE PATH",11,CY,True)]])
    flow(s,pipe,2.45,accent=RED,h=0.85,fs=13)
    bullets(s,items,y=3.75,sz=14,gap=9)

def s_results(k,t,rows,note):
    s=slide(); kicker(s,k); title(s,t)
    hdr=["Model / setting","Evaluation","Metric","Result"]; widths=[3.9,3.4,2.6,1.6]
    x0=0.9; y=2.3; rh=0.62
    # header
    xx=x0
    for i,htext in enumerate(hdr):
        box(s,xx,y,widths[i],rh,fill=RED if i==0 else PANEL2,line=None);
        txt(s,xx+0.12,y,widths[i]-0.2,rh,[[(htext,12,WHITE if i==0 else CY,True)]],anchor=MSO_ANCHOR.MIDDLE)
        xx+=widths[i]
    y+=rh
    for ri,row in enumerate(rows):
        xx=x0; fill=PANEL if ri%2 else PANEL2
        for i,cell in enumerate(row):
            box(s,xx,y,widths[i],rh,fill=fill,line=None,rad=False)
            c=RED if i==3 else TXT; b=i==3
            txt(s,xx+0.12,y,widths[i]-0.2,rh,[[(cell,12 if i<3 else 13,c,b,MONO if i==3 else FONT)]],anchor=MSO_ANCHOR.MIDDLE,line=1.0)
            xx+=widths[i]
        y+=rh
    txt(s,0.9,H-0.9,11.5,0.6,[[(note,11,MUT2,False)]],line=1.2)

def s_diff(k,t,cols,note):
    s=slide(); kicker(s,k); title(s,t)
    cw=5.6; y=2.4; h=2.2
    for i,(head,txt2) in enumerate(cols):
        x=0.9+i*(cw+0.3); acc=MUT2 if i==0 else RED
        box(s,x,y,cw,h,fill=PANEL2,line=acc,lw=1.0 if i==0 else 1.5)
        txt(s,x+0.3,y+0.25,cw-0.6,0.5,[[(head,17,MUT if i==0 else RED,True)]])
        txt(s,x+0.3,y+0.95,cw-0.6,1.1,[[(txt2,14.5,MUT if i==0 else TXT,i==1)]],line=1.25)
    txt(s,0.9,y+h+0.35,11.5,0.9,[[(note,13.5,MUT,False)]],line=1.25)

def s_close(k,t,body,contact):
    s=slide(); kicker(s,"THANK YOU")
    txt(s,0.9,2.4,11.5,1.0,[[(t,34,WHITE,True)]])
    box(s,0.9,3.7,11.5,1.4,fill=PANEL,line=RED)
    txt(s,1.2,3.9,11,1.0,[[(body,16,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE,line=1.3)
    # stat recap
    cw=2.75; gap=0.2; x=0.9
    for big,lab in C.STATS:
        box(s,x,5.5,cw,0.95,fill=PANEL2,line=RED)
        txt(s,x,5.58,cw,0.45,[[(big,20,RED,True,MONO)]],align=PP_ALIGN.CENTER)
        txt(s,x+0.1,6.04,cw-0.2,0.4,[[(lab.replace("\n"," "),8.5,MUT,False)]],align=PP_ALIGN.CENTER,line=1.0)
        x+=cw+gap
    txt(s,0.9,6.75,11.5,0.4,[[(contact,12.5,CY,False)]])

# ---- build ----
for kind,t,p in C.SLIDES:
    K={'problem':'THE PROBLEM','why':'MOTIVATION','solution':'SOLUTION','arch':'ARCHITECTURE',
       'snap':'SNAPDRAGON','results':'EVIDENCE','deploy':'DEPLOYMENT','diff':'DIFFERENTIATION',
       'roadmap':'ROADMAP'}.get(kind,'')
    if kind=='title': s_title()
    elif kind=='solution': s_solution(K,t,p['body'],p['flow'])
    elif kind=='arch': s_arch(K,t,p['steps'],p['note'])
    elif kind=='snap': s_snap(K,t,p['pipe'],p['bullets'])
    elif kind=='results': s_results(K,t,p['rows'],p['note'])
    elif kind=='diff': s_diff(K,t,p['cols'],p['note'])
    elif kind=='close': s_close(K,t,p['body'],p['contact'])
    else: s_bul(K,t,body=p.get('body'),items=p.get('bullets'),note=p.get('note'))

OUT="VOXSHIELD_SNAPDRAGON_PITCH.pptx"
prs.save(OUT); print("wrote",OUT,"slides:",len(prs.slides._sldIdLst))
