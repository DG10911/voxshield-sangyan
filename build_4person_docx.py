#!/usr/bin/env python3
"""Build VoxShield_4Person_Script.docx — a print-ready four-person presentation script."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x0B, 0x1F, 0x33)
BLUE = RGBColor(0x1E, 0x6F, 0xE0)
CYAN = RGBColor(0x0E, 0x7C, 0x9E)
GREY = RGBColor(0x5A, 0x6B, 0x7B)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
GREEN = RGBColor(0x1B, 0x8A, 0x4A)

doc = Document()
# base style
st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(10.5); st.font.color.rgb = DARK
for m in ("top_margin", "bottom_margin"): setattr(doc.sections[0], m, Inches(0.7))
for m in ("left_margin", "right_margin"): setattr(doc.sections[0], m, Inches(0.85))

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)

def para(text="", size=10.5, color=DARK, bold=False, italic=False, before=0, after=4, align=None, font="Calibri"):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(after)
    if align: p.alignment = align
    r = p.add_run(text); r.font.size = Pt(size); r.font.color.rgb = color; r.bold = bold; r.italic = italic; r.font.name = font
    return p

def rule():
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr(); pb = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "6"); b.set(qn("w:space"), "1"); b.set(qn("w:color"), "1E6FE0")
    pb.append(b); pPr.append(pb)

def h1(text, num=None):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(2)
    if num:
        r = p.add_run(num + "  "); r.font.size = Pt(15); r.bold = True; r.font.color.rgb = CYAN
    r = p.add_run(text); r.font.size = Pt(15); r.bold = True; r.font.color.rgb = NAVY
    return p

def h2(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(9); p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text); r.font.size = Pt(11.5); r.bold = True; r.font.color.rgb = BLUE
    return p

def script(text):
    """A spoken-script block: indented, italic, blue left tint."""
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.28); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.space_before = Pt(2)
    pPr = p._p.get_or_add_pPr(); pb = OxmlElement("w:pBdr"); l = OxmlElement("w:left")
    l.set(qn("w:val"), "single"); l.set(qn("w:sz"), "18"); l.set(qn("w:space"), "8"); l.set(qn("w:color"), "9DC3F0")
    pb.append(l); pPr.append(pb)
    r = p.add_run(text); r.font.size = Pt(10.5); r.italic = True; r.font.color.rgb = RGBColor(0x24,0x3B,0x55)
    return p

def stage(text):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text); r.font.size = Pt(9.5); r.bold = True; r.font.color.rgb = GREEN; r.font.name = "Consolas"

def table(headers, rows, widths=None, headfill="0B1F33"):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, htext in enumerate(headers):
        shade(hdr[i], headfill)
        pr = hdr[i].paragraphs[0]; pr.paragraph_format.space_after = Pt(1)
        run = pr.add_run(htext); run.bold = True; run.font.size = Pt(9.5); run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
    for r_i, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            if r_i % 2 == 1: shade(cells[i], "EEF4FB")
            pr = cells[i].paragraphs[0]; pr.paragraph_format.space_after = Pt(1)
            run = pr.add_run(str(val)); run.font.size = Pt(9)
            if i == 0: run.bold = True
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ───────────────────────── HEADER ─────────────────────────
para("VoxShield — Four-Person Presentation Script", 22, NAVY, bold=True, after=1)
para("Team DigiSeva · SRM Institute of Science & Technology · PS2, Audio Forensics for Voice Security",
     10, GREY, italic=True, after=2)
para("Run against presentation.html (15 chapters). Target 8–10 minutes + demo + Q&A. Fill in the four names, then rehearse the handoffs.",
     9.5, GREY, after=4)
rule()

# ───────────────────────── LINEUP ─────────────────────────
h1("The lineup — who owns what")
table(["#", "Presenter", "Role on stage", "Owns chapters", "Time"],
      [["S1", "[Name 1]", "Opener & Storyteller", "Hero (team intro) · 01 Threat · 02 Why Banks Fail", "~2:00"],
       ["S2", "[Name 2]", "AI Architect", "03 Innovation · 04 Five Models · 05 Fairness", "~2:30"],
       ["S3", "[Name 3]", "Product Lead (drives demo)", "06 Liveness · 07 Beyond Detection · 08 Real Product (LIVE) · 09 Results", "~3:00"],
       ["S4", "[Name 4]", "Strategist & Closer", "10 Deployment · 11 Market · Enterprise · 12 Vision · Thank You", "~2:30"]],
      widths=[0.4, 1.1, 1.7, 3.2, 0.7])
para("Golden rule: the person NOT speaking advances the slides and watches the room. One driver at a time. Let each animation land before you speak.",
     9.5, BLUE, bold=True, after=4)

# ───────────────────────── SPINE + NUMBERS ─────────────────────────
h1("The 30-second spine — everyone memorises this")
script("“Voice cloning turned the bank phone line into the easiest door into an account, a fake voice that knows your name, over an 8 kHz line that hides the evidence. VoxShield is a defence-in-depth system, not a model: five decorrelated detectors fused by a learned meta-stacker, a fairness layer measured across ten Indian languages, and a challenge-response liveness check that beats replay. It is explainable, never auto-blocks, runs air-gapped on the bank's own hardware, and flags a fraud call in three seconds, and it works today, TRL-5.”")

h2("Numbers everyone must know cold")
table(["Metric", "Value"],
      [["Meta-fusion equal-error-rate (held-out In-the-Wild)", "5.9%"],
       ["ROC-AUC · Accuracy @0.70", "0.983 · 94%"],
       ["Best single model alone (XLS-R)", "16.0% EER → fusion is ~3× better"],
       ["Fairness: false-positives on genuine Indic speech", "36.3% → single digits (Indic-aware)"],
       ["Streaming time-to-flag", "3.0 s (inside the 10 s target)"],
       ["Maturity", "TRL-5, working system"]],
      widths=[4.6, 2.5])
para("The honesty line (S2's mic-drop): “The learned stacker gave negative weight to two of its own five detectors, it taught itself which models to distrust.”",
     9.5, DARK, italic=True, after=4)

# ───────────────────────── SPEAKERS ─────────────────────────
def speaker(tag, name_role, time):
    doc.add_page_break()
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
    r = p.add_run(tag + "  "); r.font.size = Pt(17); r.bold = True; r.font.color.rgb = CYAN
    r = p.add_run(name_role); r.font.size = Pt(17); r.bold = True; r.font.color.rgb = NAVY
    r = p.add_run("   ·   " + time); r.font.size = Pt(11); r.font.color.rgb = GREY
    rule()

speaker("SPEAKER 1", "Opener & Storyteller", "~2:00")
h2("▸ HERO slide — the team introduction (warm, confident, ~20s)")
script("“Good [morning/afternoon]. We are Team DigiSeva from SRM Institute of Science and Technology. I'm [Name 1], I'll open with the problem. With me are [Name 2], who built our detection AI; [Name 3], who will show you the working product live; and [Name 4], who'll cover deployment and where this goes next. What you're looking at is VoxShield, real-time AI voice-clone detection for India's voice-first banking. Let me tell you why it has to exist.”")
para("Stand center. Let the “VoxShield” title animation finish before the first word.", 9, GREY, italic=True, after=4)
h2("▸ Chapter 01 — The Threat  (“Your voice is no longer yours alone”)")
script("“A cloned voice can be built from seconds of public audio, a voicemail, a social clip. It sounds human, it knows the customer's name, and it calls the branch. Worse: a real bank call rides an 8 kHz telephone line, and that compression smears the very artifacts most detectors rely on. And it acts in minutes, voice-authorised transfers don't wait. Detection after the call is forensics, not protection.”")
h2("▸ Chapter 02 — Why Banks Fail  (“One model. One language. One point of failure”)")
script("“So why doesn't off-the-shelf detection solve this? Three reasons. A single model is brittle, one unseen generator walks straight through. A black box can't freeze an account: no bank acts on ‘the AI said so’. And English-trained models are unfair, they flag genuine Tamil or Bengali customers as synthetic. A detector that punishes honest customers is one a bank can't deploy.”")
stage("➡ HANDOFF to S2:  “So we built the opposite of a single black box. [Name 2] will show you how.”")

speaker("SPEAKER 2", "AI Architect", "~2:30")
h2("▸ Chapter 03 — Our Innovation  (“One layered, honest defence”)")
script("“Thanks, [Name 1]. VoxShield isn't a model, it's defence-in-depth: detection, fairness, liveness, and honesty, engineered together. Let me take them in turn.”")
h2("▸ Chapter 04 — Five AI Models, One Brain  (“Weak alone. Strong together”)")
script("“Detection first. We run five decorrelated detectors, signal-processing, hand-crafted anti-spoofing features, and three neural models. Alone, the best of them sits at 16% error; some are near chance. But a learned meta-stacker combines them, and here's the honest part: it gave negative weight to two of its own detectors. It taught itself which to distrust. The result: 5.9% equal-error-rate on held-out data, about three times better than any single model, with calibrated scores and a plain-language reason code on every verdict.”")
para("Point to the scoreboard bars animating 62% → 5.9%.", 9, GREY, italic=True, after=4)
h2("▸ Chapter 05 — The Fairness Breakthrough  (“A detector that flags honest customers is a failed detector”)")
script("“Second layer: fairness. We measured false-positives on genuine speech in ten Indian languages, Hindi, Tamil, Bengali, Telugu, Marathi, and more. English-centric detectors fail here. After Indic-aware retraining we cut the false-positive rate on genuine Indian speech from 36.3% down to single digits, and we publish the per-language numbers, including our weak spots. Measured fairness is the moat: it's what a public-sector bank can actually procure.”")
stage("➡ HANDOFF to S3:  “Detection and fairness are the science. But detection alone loses to a replay attack, so [Name 3] will show you the layer that closes that door, live.”")

speaker("SPEAKER 3", "Product Lead (drives the demo)", "~3:00")
h2("▸ Chapter 06 — Liveness  (“A recording can't answer a question from one second ago”)")
script("“Thanks, [Name 2]. Play a clone through a speaker and the acoustic path launders the digital artifacts, pure detection can miss it. So we add challenge-response liveness: the system speaks a random prompt, ‘say four, seven, two’, and the caller must say it live. We verify three things at once: content, did they say the right digits; liveness, is it a live human, not a synthesis engine; and timing, inside the window. A recording can't answer a question generated one second ago.”")
h2("▸ Chapter 07 — Beyond Detection  (“Catch the fraud, not just the fake”)")
script("“And we go past ‘is it fake’ to ‘is it a scam.’ Our Digital Arrest Shield fuses the clone score with scam-intent read from the transcript, in Hindi, Hinglish or English. A cloned ‘CBI officer’ running the digital-arrest playbook lands as CRITICAL, with the scam script transcribed and flagged. That's catching the fraud, not just the fake.”")
h2("▸ Chapter 08 — Real Product  (LIVE DEMO)  (“Not a deck. A working system”)")
script("“And this is not a mock-up, it's running right now. Let me show you.”")
para("[ SWITCH to the live system / demo tab ]", 9.5, DARK, bold=True, after=2)
for line in ["1.  Genuine clip → reads LOW.",
             "2.  AI-clone clip → reads HIGH, even played through a phone.",
             "3.  Live call / streaming → watch it flag the clone at 3 seconds.",
             "4.  (If time) Arrest Shield → CRITICAL with the scam transcript."]:
    para(line, 10, DARK, after=1)
para("Keep it to 60–75s. If the network or mic misbehaves, say “here's the recorded run” and cut to a backup clip, never debug on stage.",
     9, GREY, italic=True, after=4)
h2("▸ Chapter 09 — Measured Results  (“Numbers we can defend”)")
script("“Every number here is held-out, clips the system never trained on. 5.9% error, 0.98 AUC, 94% accuracy, flagged at 3 seconds, fairness cut from 36% to single digits. No cherry-picking, no ‘up to’.”")
stage("➡ HANDOFF to S4:  “A working system is only useful if a bank can actually run it. [Name 4] will take you there.”")

speaker("SPEAKER 4", "Strategist & Closer", "~2:30")
h2("▸ Chapter 10 — Deployment & Trust  (“Built for a bank's basement, not our cloud”)")
script("“Thanks, [Name 3]. VoxShield runs on-premise, air-gapped, the Docker image bakes every model in, so it never phones home. Audio is SHA-256 hashed, never stored in the clear. And by design it never auto-blocks, high risk routes to step-up verification alongside the bank's existing caller-ID checks. A human stays in charge. It's built to GOV.UK / USWDS accessibility standards.”")
h2("▸ Chapter 11 — The Market  (“India's banking future is voice-first”)")
script("“Why now? Phone banking, IVR and voice payments reach hundreds of millions that apps never will, across languages, literacy levels and feature phones. Every one of those calls is an attack surface. Voice security isn't a feature; it's table stakes for every bank running a call centre.”")
h2("▸ Enterprise · Business Mode  (“One AI platform. Every voice. Every industry”)")
script("“And the same engine reaches beyond banking, government helplines, telecom anti-vishing, insurance claims, healthcare, legal forensics. One drop-in API, twelve sectors. That's the business: enterprise SaaS, usage-based API, on-prem licensing, and government and banking contracts.”")
h2("▸ Chapter 12 — Vision  (“The generators will improve. So will the shield”)")
script("“The clones will get better, so does the shield: continual learning for new generators, deeper Indic fine-tuning, source attribution, adversarial-robust training. We're TRL-5 today, with an honest path to production.”")
h2("▸ THANK YOU — the close (all four step forward)")
script("“Detection. Fairness. Liveness. One layered, honest defence for India's voice-first banking future. We're Team DigiSeva, thank you. We'd love your questions.”")

# ───────────────────────── Q&A + CHECKLIST ─────────────────────────
doc.add_page_break()
h1("Q&A — who fields what")
table(["Question theme", "Lead", "Backup"],
      [["Accuracy / EER / how it was measured", "S2", "S3"],
       ["Fairness / Indian languages / bias", "S2", "S1"],
       ["Live demo / product / latency", "S3", "S2"],
       ["Deployment / security / on-prem / compliance", "S4", "S3"],
       ["Business model / market / competition", "S4", "S1"],
       ["“Isn't this just a deepfake detector?”", "S1", "S4"]],
      widths=[4.2, 1.3, 1.3])
script("S1's answer to the last one: “No, real/fake is table stakes. We add fairness for India and liveness against replay, and we catch the scam, not just the fake.”")
para("If you don't know an answer: “Great question, that's on our roadmap; here's how we'd approach it,” then bridge to a strength. Never bluff a number.",
     9.5, DARK, bold=True, after=6)

h1("Rehearsal checklist")
for item in ["Each speaker can deliver their block without reading, in time.",
             "Handoff lines are memorised, no awkward “um, over to you.”",
             "The demo has a recorded backup clip ready in a second tab.",
             "Slides advance with arrow keys; the non-speaker drives.",
             "Numbers on your lips match the numbers on the slide.",
             "Timed a full run twice; you're under the limit with 30s to spare.",
             "One-line answers rehearsed for the six Q&A themes above."]:
    p = doc.add_paragraph(item, style=None); p.paragraph_format.space_after = Pt(2); p.paragraph_format.left_indent = Inches(0.25)
    p.runs[0].font.size = Pt(10)
    # checkbox bullet
    pr = p.insert_paragraph_before() if False else p
    r0 = p.runs[0]

h1("Timing at a glance")
para("S1  2:00   →   S2  2:30   →   S3  3:00 (incl. demo)   →   S4  2:30   →   Q&A     ≈ 10 minutes.",
     11, NAVY, bold=True, after=3, font="Consolas")
para("To cut to 6 minutes: S1 keeps only Hero + Threat; S2 drops the per-language detail; S3 does one demo (clone → HIGH at 3 s) and the results tile; S4 keeps Deployment + Close.",
     9.5, GREY, after=2)

out = "/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/VoxShield_4Person_Script.docx"
doc.save(out)
print("saved", out)
