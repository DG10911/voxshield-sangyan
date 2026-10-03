#!/usr/bin/env python3
"""VoxShield Edge — Snapdragon pitch deck as 16:9 PDF (mirrors the .pptx)."""
import os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snap_content as C

W,H=960,540
BG=HexColor("#0A0E14"); PANEL=HexColor("#141A24"); PANEL2=HexColor("#1B222E"); LINE=HexColor("#2A3343")
RED=HexColor("#EE2737"); CY=HexColor("#35C7F2"); TXT=HexColor("#E9EDF4"); MUT=HexColor("#939EB0")
MUT2=HexColor("#636E80"); OK=HexColor("#2FD07B"); WHITE=HexColor("#FFFFFF")
F="Helvetica"; FB="Helvetica-Bold"
c=canvas.Canvas("VOXSHIELD_SNAPDRAGON_PITCH_PDFDECK.pdf",pagesize=(W,H))

def page():
    c.setFillColor(BG); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(RED); c.rect(0,H-5,W,5,fill=1,stroke=0)
def rrect(x,y,w,h,fill=None,line=None,lw=1,r=7):
    if fill is not None: c.setFillColor(fill)
    if line is not None: c.setStrokeColor(line); c.setLineWidth(lw)
    c.roundRect(x,y,w,h,r,fill=1 if fill is not None else 0,stroke=1 if line is not None else 0)
def T(x,y,s,size,col,font=F,center=False,right=False):
    c.setFillColor(col); c.setFont(font,size)
    (c.drawCentredString if center else (c.drawRightString if right else c.drawString))(x,y,s)
def para(x,y,s,size,col,w,font=F,lead=None,center=False):
    c.setFillColor(col); c.setFont(font,size); lead=lead or size*1.3
    for ln in simpleSplit(s,font,size,w):
        (c.drawCentredString(x+w/2,y,ln) if center else c.drawString(x,y,ln)); y-=lead
    return y
def kicker(t): T(64,H-52,t,13,RED,FB)
def title(t,size=27): T(64,H-92,t,size,WHITE,FB)
def bullets(items,x=64,y=None,size=15,col=TXT,w=832,gap=16):
    y=y if y is not None else H-150
    for it in items:
        T(x,y,"▸",size,RED,FB); yy=para(x+22,y,it,size,col,w-22,lead=size*1.25); y=yy-gap
    return y
def flow(items,y,h=54,fs=13,accent=CY,lastaccent=RED):
    n=len(items); gap=20; total=832; bw=(total-(n-1)*gap)/n; x=64
    for i,it in enumerate(items):
        last=i==n-1
        rrect(x,y,bw,h,fill=PANEL if last else PANEL2,line=lastaccent if last else LINE,lw=1.2)
        c.setFillColor(lastaccent if last else TXT); c.setFont(FB if last else F,fs)
        for j,ln in enumerate(simpleSplit(it,F,fs,bw-12)):
            c.drawCentredString(x+bw/2,y+h/2-4-(j*fs*1.05)+ (len(simpleSplit(it,F,fs,bw-12))-1)*fs*0.5,ln)
        if not last:
            c.setFillColor(RED); c.setFont(FB,15); c.drawCentredString(x+bw+gap/2,y+h/2-5,"›")
        x+=bw+gap

# ---- title ----
def s_title():
    page(); T(64,H-150,C.EVENT,14,CY,FB)
    T(62,H-205,C.TITLE,52,WHITE,FB)
    T(64,H-238,C.SUB,17,MUT,F)
    rrect(64,H-320,832,58,fill=PANEL,line=LINE)
    para(84,H-288,C.ONELINE,14,TXT,796,lead=18)
    cw=196; gap=16; x=64
    for big,lab in C.STATS:
        rrect(x,H-410,cw,72,fill=PANEL2,line=RED,lw=1.2)
        T(x+cw/2,H-378,big,22,RED,"Courier-Bold",center=True)
        c.setFillColor(MUT); c.setFont(F,8.5)
        for j,ln in enumerate(lab.split("\n")): c.drawCentredString(x+cw/2,H-395-j*11,ln)
        x+=cw+gap
    T(64,H-455,f"{C.AUTHOR}  ·  on-device · private · Snapdragon NPU",11,MUT2,F)

def s_bul(k,t,body=None,items=None,note=None):
    page(); kicker(k); title(t); y=H-135
    if body: y=para(64,H-135,body,15,MUT,832,lead=20)-10
    if items: bullets(items,y=y,gap=15)
    if note: para(64,44,note,11,MUT2,832,lead=14)

def s_solution(k,t,body,fl):
    page(); kicker(k); title(t)
    para(64,H-135,body,16,MUT,832,lead=22)
    T(64,H-235,"OPERATIONAL FLOW",11,CY,FB); flow(fl,H-300,h=58,fs=13,lastaccent=RED)
    c.setFillColor(MUT); c.setFont(F,13); c.drawString(64,H-345,"Decision support for a fraud analyst — ")
    wsofar=c.stringWidth("Decision support for a fraud analyst — ",F,13)
    T(64+wsofar,H-345,"never automatic blocking.",13,OK,FB)

def s_arch(k,t,steps,note):
    page(); kicker(k); title(t)
    flow(steps[:4],H-170,h=60,fs=12.5); flow(steps[4:],H-255,h=60,fs=12.5)
    rrect(64,H-360,832,80,fill=PANEL,line=LINE); para(84,H-315,note,14,TXT,796,lead=18)

def s_snap(k,t,pipe,items):
    page(); kicker(k); title(t)
    T(64,H-130,"ON-DEVICE INFERENCE PATH",11,CY,FB); flow(pipe,H-195,h=58,fs=13,lastaccent=RED)
    bullets(items,y=H-240,size=14,gap=13)

def s_results(k,t,rows,note):
    page(); kicker(k); title(t)
    hdr=["Model / setting","Evaluation","Metric","Result"]; wd=[262,232,180,158]; x0=64; y=H-150; rh=44
    xx=x0
    for i,htext in enumerate(hdr):
        c.setFillColor(RED if i==0 else PANEL2); c.rect(xx,y,wd[i],rh,fill=1,stroke=0)
        T(xx+10,y+rh/2-5,htext,12,WHITE if i==0 else CY,FB); xx+=wd[i]
    y-=rh
    for ri,row in enumerate(rows):
        xx=x0; c.setFillColor(PANEL if ri%2 else PANEL2); c.rect(x0,y,sum(wd),rh,fill=1,stroke=0)
        for i,cell in enumerate(row):
            isr=i==3; c.setFillColor(RED if isr else TXT); c.setFont("Courier-Bold" if isr else F,12 if i<3 else 13)
            for j,ln in enumerate(simpleSplit(cell,F,12,wd[i]-16)): c.drawString(xx+10,y+rh/2-5-j*13+(len(simpleSplit(cell,F,12,wd[i]-16))-1)*6.5,ln)
            xx+=wd[i]
        y-=rh
    para(64,44,note,11,MUT2,832,lead=14)

def s_diff(k,t,cols,note):
    page(); kicker(k); title(t); cw=404; y=H-320; h=150
    for i,(head,body) in enumerate(cols):
        x=64+i*(cw+24); acc=MUT2 if i==0 else RED
        rrect(x,y,cw,h,fill=PANEL2,line=acc,lw=1.2 if i==0 else 1.8)
        T(x+22,y+h-34,head,17,MUT if i==0 else RED,FB)
        para(x+22,y+h-66,body,14.5,MUT if i==0 else TXT,cw-44,lead=19)
    para(64,y-30,note,13.5,MUT,832,lead=19)

def s_close(k,t,body,contact):
    page(); kicker("THANK YOU"); T(64,H-160,t,30,WHITE,FB)
    rrect(64,H-260,832,84,fill=PANEL,line=RED); para(88,H-205,body,16,TXT,784,lead=22)
    cw=196; gap=16; x=64
    for big,lab in C.STATS:
        rrect(x,H-360,cw,68,fill=PANEL2,line=RED); T(x+cw/2,H-330,big,20,RED,"Courier-Bold",center=True)
        c.setFillColor(MUT); c.setFont(F,8.5)
        for j,ln in enumerate(lab.split("\n")): c.drawCentredString(x+cw/2,H-346-j*11,ln)
        x+=cw+gap
    T(64,H-395,contact,12.5,CY,F)

for kind,t,p in C.SLIDES:
    K={'problem':'THE PROBLEM','why':'MOTIVATION','solution':'SOLUTION','arch':'ARCHITECTURE',
       'snap':'SNAPDRAGON','results':'EVIDENCE','deploy':'DEPLOYMENT','diff':'DIFFERENTIATION','roadmap':'ROADMAP'}.get(kind,'')
    if kind=='title': s_title()
    elif kind=='solution': s_solution(K,t,p['body'],p['flow'])
    elif kind=='arch': s_arch(K,t,p['steps'],p['note'])
    elif kind=='snap': s_snap(K,t,p['pipe'],p['bullets'])
    elif kind=='results': s_results(K,t,p['rows'],p['note'])
    elif kind=='diff': s_diff(K,t,p['cols'],p['note'])
    elif kind=='close': s_close(K,t,p['body'],p['contact'])
    else: s_bul(K,t,body=p.get('body'),items=p.get('bullets'),note=p.get('note'))
    c.showPage()
c.save(); print("wrote VOXSHIELD_SNAPDRAGON_PITCH_PDFDECK.pdf")
