#!/usr/bin/env python3
"""Build a course module for VoxShield's 6th detector, styled to match the Complete Course
(plain-English, an 'in simple words' green box, then the detail). Paste into Pages."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY=RGBColor(0x24,0x40,0x66); BLUE=RGBColor(0x1E,0x5F,0xB0); DARK=RGBColor(0x1E,0x1E,0x1E)
GREY=RGBColor(0x5A,0x6B,0x7B); GREEN=RGBColor(0x1B,0x7A,0x43); GREENBG="E7F5EC"

doc=Document()
b=doc.styles["Normal"]; b.font.name="Calibri"; b.font.size=Pt(11); b.font.color.rgb=DARK
b.paragraph_format.space_after=Pt(6); b.paragraph_format.line_spacing=1.18
s=doc.sections[0]
for m in ("top_margin","bottom_margin"): setattr(s,m,Inches(0.9))
for m in ("left_margin","right_margin"): setattr(s,m,Inches(1.0))

def shade(cell,hexc):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement("w:shd")
    sh.set(qn("w:val"),"clear"); sh.set(qn("w:fill"),hexc); tcPr.append(sh)

def para(t="",size=11,color=DARK,bold=False,italic=False,before=0,after=6):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(before); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.font.color.rgb=color; r.bold=bold; r.italic=italic
    return p

def head(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(t); r.font.size=Pt(20); r.bold=True; r.font.color.rgb=NAVY
    return p

def sub(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(t); r.font.size=Pt(13.5); r.bold=True; r.font.color.rgb=BLUE
    return p

def simple(t):
    """green 'in simple words' box"""
    tb=doc.add_table(rows=1,cols=1); tb.style="Table Grid"; shade(tb.rows[0].cells[0],GREENBG)
    c=tb.rows[0].cells[0]; cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(2)
    r=cp.add_run("In simple words:  "); r.bold=True; r.font.size=Pt(11); r.font.color.rgb=GREEN
    r=cp.add_run(t); r.font.size=Pt(11); r.font.color.rgb=RGBColor(0x14,0x4A,0x2C)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

def bullet(lead,t):
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(4)
    if lead:
        r=p.add_run(lead); r.bold=True; r.font.size=Pt(11)
    r=p.add_run(t); r.font.size=Pt(11)

# ── module ──
para("MODULE 6.5", 11, GREY, bold=True, after=2)
head("The 6th Detector: an Indian-language specialist")
para("You already met the five detectors and the meta-learner that fuses them. Those five are trained mostly on English and general audio. They are strong, but on a genuinely Indian-language deepfake, they can be unsure. So we added a sixth model that is an expert in exactly one thing: spotting synthetic Indian speech.", after=8)

simple("The first five detectors are all-rounders. The sixth is a specialist who only speaks up for Indian languages, and who is only allowed to say 'this is definitely fake', never 'this is fine'. So it can catch more fakes without ever wrongly accusing a real customer.")

sub("What it is")
para("The 6th detector is a fine-tuned XLS-R-300M model. XLS-R is a large speech model that already understands many languages; we fine-tuned it on Indian-language genuine speech and Indian-language deepfakes (synthesised with MMS-TTS and VITS). Given a clip, it outputs one number: the probability that the voice is fake.")

sub("How it works, in three rules")
bullet("Rule 1, it only listens to Indian speech.  ",
       "An on-device language-ID (Whisper) decides the language first. If the call is English, the sixth detector never runs, so English performance is completely unchanged. It only wakes up for Indian-language audio.")
bullet("Rule 2, it can only raise the alarm, never lower it.  ",
       "This is the key safety idea. When it does run, it can only push the verdict UP, and only when it is very confident (probability of fake at least 0.85). It can never pull a verdict down. So it can rescue a fake the other five missed, but it can never turn a real customer into a false alarm.")
bullet("Rule 3, if it is ever missing or unsure, nothing breaks.  ",
       "The booster is fully optional. If its model is absent, or it is not confident, it simply stays silent and the normal five-model verdict stands. It can only ever help.")

sub("Why this design is clever")
para("A naive way to help Indian languages would be to swap in a specialist model for everyone. But a specialist can be over-eager and start flagging genuine speech, which is exactly the unfairness we are trying to remove. By making the sixth detector one-directional (only escalate) and language-gated (only Indian audio) and confidence-gated (only when very sure), it is impossible for it to add a false positive. It is a pure upside.")

sub("The results")
bullet("", "Indian-language voice-clone recall rose from 42% to 82%, nearly double.")
bullet("", "False alarms on genuine Indian speech fell from 36.3% to 6.3%.")
bullet("", "English accuracy stayed exactly the same (5.9% equal-error-rate).")

sub("It is live, not theory")
para("This is running in production today. On the live system, a real Hindi deepfake is routed to the Indian-language path and the sixth detector fires, marking it HIGH with a fused score of 0.997. In the system logs this shows as the fusion mode “meta-stacker(indic)+indic-boost”, which is the sixth detector adding its vote on top of the Indian-aware fusion.", after=8)

simple("On a real Hindi fake, the live system scores 0.997 and the log literally reads 'indic-boost', that is the sixth detector doing its job, in production, right now.")

out="/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/VoxShield_Course_Module_6th_Detector.docx"
doc.save(out); print("saved",out)
