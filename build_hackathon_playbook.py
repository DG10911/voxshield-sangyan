#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VoxShield × Sarvam BuildIn' Hours — the winning playbook. Styled DOCX."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY=RGBColor(0x14,0x2A,0x54); BLUE=RGBColor(0x1A,0x56,0xB0); DARK=RGBColor(0x1A,0x1A,0x1A)
GREY=RGBColor(0x55,0x55,0x55); GREEN=RGBColor(0x1B,0x7A,0x43); AMBER=RGBColor(0x8A,0x54,0x00)
RED=RGBColor(0xB0,0x2A,0x2A); PLUM=RGBColor(0x7A,0x27,0x5E)
HL="EAF1FB"; WIN="E7F5EC"; WARN="FBF3E6"; STEP="F3F0F8"

doc=Document()
st=doc.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(11); st.font.color.rgb=DARK
st.paragraph_format.space_after=Pt(6); st.paragraph_format.line_spacing=1.14
for s in doc.sections: s.left_margin=s.right_margin=Inches(0.85); s.top_margin=s.bottom_margin=Inches(0.75)

def shade(p,h):
    pr=p._p.get_or_add_pPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),h); pr.append(sh)
def bl(p,h,sz='18'):
    pr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); l=OxmlElement('w:left')
    l.set(qn('w:val'),'single'); l.set(qn('w:sz'),sz); l.set(qn('w:space'),'8'); l.set(qn('w:color'),h); pb.append(l); pr.append(pb)
import re
def runs(p,t,base=DARK,size=11,italic=False):
    for seg in re.split(r'(\*\*.+?\*\*)',t):
        if not seg: continue
        b=seg.startswith('**') and seg.endswith('**')
        r=p.add_run(seg[2:-2] if b else seg); r.bold=b; r.italic=italic; r.font.size=Pt(size); r.font.color.rgb=base
def H1(t,color=NAVY,size=17,before=16):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(before); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(t); r.bold=True; r.font.size=Pt(size); r.font.color.rgb=color
def H2(t,color=BLUE):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(t); r.bold=True; r.font.size=Pt(12.5); r.font.color.rgb=color
def para(t,size=11,base=DARK,after=6):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after); runs(p,t,base=base,size=size)
def bullet(t):
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(2); runs(p,t,size=10.5)
def num(t):
    p=doc.add_paragraph(style="List Number"); p.paragraph_format.space_after=Pt(2); runs(p,t,size=10.5)
def box(t,fill,bar,lead=None,leadcol=GREEN):
    p=doc.add_paragraph(); shade(p,fill); bl(p,bar); p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(8)
    if lead:
        r=p.add_run(lead); r.bold=True; r.font.size=Pt(10.5); r.font.color.rgb=leadcol
    runs(p,t,size=10.5,base=RGBColor(0x22,0x33,0x44))
def table(rows,widths=None,head=BLUE):
    t=doc.add_table(rows=1,cols=len(rows[0])); t.style="Light Grid Accent 1"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(rows[0]):
        c=t.rows[0].cells[i]; c.text=''; r=c.paragraphs[0].add_run(h); r.bold=True; r.font.size=Pt(9.5); r.font.color.rgb=RGBColor(0xFF,0xFF,0xFF)
        tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),'1A56B0'); tcPr.append(sh)
    for row in rows[1:]:
        cells=t.add_row().cells
        for i,v in enumerate(row):
            cells[i].text=''; runs(cells[i].paragraphs[0],v,size=9.3);
            if i==0:
                for rr in cells[i].paragraphs[0].runs: rr.bold=True
    if widths:
        for i,w in enumerate(widths):
            for row in t.rows: row.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

# ---------- COVER ----------
for _ in range(2): doc.add_paragraph()
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("How to WIN Sarvam BuildIn' Hours"); r.bold=True; r.font.size=Pt(28); r.font.color.rgb=NAVY
for txt,sz,col,it in [("The VoxShield Winning Playbook",17,BLUE,False),
    ("A Sarvam-powered voice-fraud shield — built to take the ₹5,00,000",12,GREY,True),
    ("",8,DARK,False),
    ("Team DigiSeva · Bengaluru · 9 Aug 2026 · 12-hour offline hackathon",11,GREEN,False)]:
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    if txt: rr=q.add_run(txt); rr.font.size=Pt(sz); rr.font.color.rgb=col; rr.italic=it; rr.bold=(col in (BLUE,GREEN))
doc.add_paragraph()
box("Two facts decide this hackathon, and we build around both. (1) Sarvam judges reward a polished product that does ONE thing brilliantly over a half-built \"platform\", AND they reward heavy, visible use of Sarvam's own APIs. (2) Your unfair advantage is that you have thought about voice fraud longer than anyone in that room. This plan turns both into a trophy.",HL,"1A56B0",lead="The whole strategy in one paragraph:  ",leadcol=NAVY)

# ---------- 1. THE REFRAME ----------
H1("1.  The Reframe — this is the single most important decision",before=6)
para("Do **not** pitch \"VoxShield, the deepfake detector.\" Sarvam has **no deepfake-detection API**, so a judge will ask \"where is Sarvam in this?\" and you lose. Instead, lead with the layer Sarvam genuinely powers, and keep your detector as the mic-drop bonus.")
box("Pitch this: \"SwarRaksha by VoxShield — a real-time, Sarvam-powered shield that listens to a scam call in any Indian language, understands the fraud as it unfolds, and warns the victim in their own language — before the money moves.\"  Your own AI-voice-clone detector rides along as the line no other team can say: \"and we also detect that the caller's voice itself is an AI clone.\"",WIN,"1B7A43",lead="YOUR ONE-LINER:  ")
para("This wins because it is **100% on-theme** (Voice AI + Multilingual + AI Agent for India), it **consumes four Sarvam APIs at once**, and it solves a real, frightening, uniquely-Indian problem — the ₹19,000-crore \"digital arrest\" scam.")

# ---------- 2. WHY IT WINS ----------
H1("2.  Why this beats every other team in the room")
table([
 ["What Sarvam judges reward","How SwarRaksha nails it"],
 ["Does ONE thing brilliantly","One demo: a live scam call → instant local-language warning. Not a platform."],
 ["Heavy Sarvam API usage","Saaras (STT) + Sarvam-30B (LLM) + Bulbul (TTS) + Sarvam-Translate — 4 products in one flow."],
 ["Real-world India impact","Digital-arrest scams stealing ₹19,000 cr from real families in real Indian languages."],
 ["Working live demo","Sub-250 ms streaming makes a real, on-stage live-call demo possible in 12 hours."],
 ["A team worth funding","You already have deep voice-fraud domain expertise + a deepfake detector no one else has."],
], widths=[2.4,4.2])

# ---------- 3. THE BUILD ----------
H1("3.  The product — exact Sarvam architecture (current Aug-2026 models)")
para("A live call flows through four Sarvam calls, then your detector. Every arrow is one API — that visible, heavy Sarvam usage is exactly what judges score.")
table([
 ["Stage","Sarvam model / API","What it does in the demo"],
 ["1. Listen","saaras:v3 (STT, WebSocket streaming)","Transcribes the live call in Hindi/Hinglish/Tamil… Supports 8 kHz telephony audio — perfect for a phone call."],
 ["2. Understand","sarvam-30b (chat completions)","Reads scam intent + tracks the digital-arrest script: Authority → Threat → Isolation → Extraction. Outputs a risk verdict + reason."],
 ["3. Translate","sarvam-translate:v1","Renders the warning into the victim's exact language (22 supported)."],
 ["4. Warn","bulbul:v3 (TTS, µ-law/streaming)","SPEAKS the warning back into the call: \"यह फर्ज़ी कॉल है — फ़ोन काटें, 1930 डायल करें.\" Outputs telephony µ-law audio."],
 ["5. Bonus ★","VoxShield detector (your own)","Flags that the caller's VOICE is an AI clone — the differentiator no other team has."],
], widths=[1.0,2.0,3.6])
box("Sarvam-M is DEPRECATED as of 2026 — use sarvam-30b (64K context) or sarvam-105b (128K). Saaras v3 and Bulbul v3 both stream over WebSocket at sub-250 ms first-byte, and Bulbul outputs µ-law/a-law — i.e. telephony-native. LiveKit or Pipecat can wire a Sarvam voice agent in under ~10 minutes; use one of them as the call scaffold so you spend your 12 hours on the scam-intelligence, not plumbing.",WARN,"C79A3A",lead="Technical must-knows (accuracy matters to judges):  ",leadcol=AMBER)

# ---------- 4. THE 12-HOUR PLAN ----------
H1("4.  The 12-hour build plan (10:00 → 18:30, elimination round)")
para("**Rule you must respect:** projects must be *developed during the hackathon* and be *original*. Do NOT submit pre-built VoxShield. Build the Sarvam integration fresh; your domain knowledge is the head start, the submitted code is new.")
plan=[
 ("Before you arrive","Register by 6 Aug. Read Saaras/Bulbul/chat-completions quickstarts. Claim the ₹5,000 Sarvam credits. Pre-write your scam-intent LLM prompt. Assign roles. Have 2 sample scam-call audio clips (Hindi + Tamil) ready."),
 ("H0–H1 (10–11)","Scaffold: LiveKit/Pipecat call loop + Saaras streaming STT printing live transcript. Get ONE sentence transcribed end-to-end. Commit."),
 ("H1–H3 (11–13)","The brain: Sarvam-30B prompt that classifies scam-intent and returns the stage (Authority→Threat→Isolation→Extraction) + a confidence. Tune on your sample clips."),
 ("H3–H5 (13–15)","The voice: on a CRITICAL verdict, Sarvam-Translate → Bulbul TTS speaks the 1930 warning in the caller's language. Close the loop: call in → warning out."),
 ("H5–H7 (15–17)","The differentiator: drop in your VoxShield clone-detector as a second signal on screen. Fuse: \"fake voice AND scam script = CRITICAL.\" Build the simple live dashboard."),
 ("H7–H9 (17–18)","Harden the demo path only. Two rehearsed clips that ALWAYS work. Screen-record a backup video in case wifi/mic fails on stage."),
 ("H9 (18–18:30)","Rehearse the 3-minute pitch twice. Freeze code. Submit deliverables before the deadline."),
]
for h,t in plan:
    p=doc.add_paragraph(); shade(p,STEP); bl(p,"7A275E")
    r=p.add_run(h+":  "); r.bold=True; r.font.size=Pt(10.5); r.font.color.rgb=PLUM
    runs(p,t,size=10.5,base=RGBColor(0x2A,0x22,0x33))

# ---------- 5. THE DEMO ----------
H1("5.  The 3-minute demo script (this is what actually wins)")
para("Judges score the demo more than the slides. Make it **live, dramatic, and about a person** — not architecture.")
num("**Hook (20s):** \"Last year, Indians lost nineteen thousand crore rupees to 'digital arrest' scam calls. Here is one — live.\"")
num("**Play the scam (30s):** Play a real-style Hindi scam clip. On screen, Saaras transcribes it *live*, word by word.")
num("**The brain reacts (30s):** Point to the screen: Sarvam-30B lights up the stages — 'Authority… Threat… Isolation…' — risk climbing to CRITICAL.")
num("**The save (40s):** At CRITICAL, Bulbul *speaks aloud* in Hindi: \"यह फ़र्ज़ी कॉल है, फ़ोन काटें, 1930 डायल करें.\" Let the room HEAR it.")
num("**The mic-drop (20s):** \"And one more thing — that caller's voice was itself an AI clone. Our own detector caught it.\" Show the fake-voice flag.")
num("**Close (20s):** \"Four Sarvam models, one flow, in the ten languages India actually gets scammed in. Detection. Understanding. Protection — before the money moves.\"")

# ---------- 6. RISKS & RULES ----------
H1("6.  Risks, rules & how to de-risk")
bullet("**Originality rule** → Build the Sarvam integration fresh on the day; present it as a hackathon build, cite VoxShield only as your team's background/expertise.")
bullet("**Live-demo failure** → Always have a screen-recorded backup video and two clips that are known to work. Never demo an untested language live.")
bullet("**\"Where's the AI?\" trap** → Keep the Sarvam calls visible on screen (live transcript, stage tracker, spoken warning) so API usage is obvious to judges.")
bullet("**Scope creep** → Resist adding speaker-verification, enrolment, fraud-ring, etc. ONE flow, brilliantly. Everything else is a spoken \"roadmap\" line.")
bullet("**Credits/latency** → ₹5,000 credits is plenty for a demo; pre-cache the warning audio for your two demo languages so TTS never stalls on stage.")

# ---------- 7. TEAM ----------
H1("7.  Team roles (2–4 people)")
table([
 ["Role","Owns"],
 ["Voice/Infra","LiveKit/Pipecat call loop + Saaras streaming STT + Bulbul TTS output."],
 ["AI/Prompt","Sarvam-30B scam-intent + stage-tracker prompt; Sarvam-Translate."],
 ["Detector/Demo","VoxShield clone-detector signal + the live dashboard + backup video."],
 ["Pitch/PM","The 3-min story, the person-centred framing, timekeeping, submission."],
], widths=[1.6,5.0])

# ---------- 8. PREP CHECKLIST ----------
H1("8.  Do these in the next 3 days (deadline: register by 6 Aug 11:59 PM)")
for t in ["Register the team of 2–4 on HackCulture; profile is used for shortlisting — do it today.",
 "Create a Sarvam account, generate an API key, read the Saaras + Bulbul + chat-completions quickstarts.",
 "Write and test the scam-intent LLM prompt offline on 2–3 sample transcripts.",
 "Record/collect 2 scam-call sample clips (Hindi + one South-Indian language).",
 "Install LiveKit or Pipecat locally; get a hello-world Sarvam voice loop running before the day.",
 "Carry a valid govt/college ID for verification at ZO House, Bengaluru."]:
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(2)
    r=p.add_run("☐  "); r.bold=True; runs(p,t,size=10.5)

# ---------- SOURCES ----------
H1("Sources",size=12,color=GREY,before=12)
for s in ["Sarvam API models & changelog: docs.sarvam.ai/api/getting-started/models · /changelog",
 "Sarvam capabilities 2026 (Saaras v3, Bulbul v3/v4, Sarvam-30B/105B): explainx.ai/blog/sarvam-ai-capabilities-api-models-guide-2026",
 "Sarvam streaming STT/TTS (sub-250 ms, WebSocket): docs.sarvam.ai/api-reference-docs/api-guides-tutorials",
 "Sarvam voice agents (Samvaad) + LiveKit/Pipecat: sarvam.ai/products/conversational-agents",
 "Hackathon judging (ONE thing brilliantly; execution > polish): taikai.network/en/blog/hackathon-judging · dorahacks.io",
 "Event: HackCulture — Sarvam BuildIn' Hours, 9 Aug 2026, Bengaluru, ₹5,00,000 prizes."]:
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(2); r=p.add_run(s); r.font.size=Pt(8.5); r.font.color.rgb=GREY

out="/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/VoxShield_Sarvam_Hackathon_WinPlan.docx"
doc.save(out); print("SAVED",out)
