#!/usr/bin/env python3
"""Render VoxShield_4Presenter_TED_Script.md into a styled DOCX teleprompter/handout."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BLUE=RGBColor(0x1F,0x4E,0x8C); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55)
GREEN=RGBColor(0x1F,0x7A,0x33); ACCENT=RGBColor(0x2F,0x6F,0xE0); AMBER=RGBColor(0x8A,0x54,0x00)
SLIDEBG="EAF1FB"; SAYBG="F4F7FB"; NOTEBG="FBF3E6"
PRES=[RGBColor(0x1F,0x4E,0x8C),RGBColor(0x1F,0x7A,0x33),RGBColor(0x8A,0x2B,0x6B),RGBColor(0x8A,0x54,0x00)]

doc=Document()
st=doc.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(11); st.font.color.rgb=DARK
st.paragraph_format.space_after=Pt(6); st.paragraph_format.line_spacing=1.15
for s in doc.sections:
    s.left_margin=s.right_margin=Inches(0.9); s.top_margin=s.bottom_margin=Inches(0.8)

def shade(p,hexc):
    pr=p._p.get_or_add_pPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),hexc); pr.append(sh)
def border_left(p,hexc,sz='18'):
    pr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); l=OxmlElement('w:left')
    l.set(qn('w:val'),'single'); l.set(qn('w:sz'),sz); l.set(qn('w:space'),'8'); l.set(qn('w:color'),hexc)
    pb.append(l); pr.append(pb)

import re
def add_runs(p,text,base=DARK,size=11,italic=False,bold_all=False):
    """render **bold** and *italic* inline."""
    for seg in re.split(r'(\*\*.+?\*\*|\*[^*]+?\*)',text):
        if not seg: continue
        if seg.startswith("**") and seg.endswith("**"):
            r=p.add_run(seg[2:-2]); r.bold=True
        elif seg.startswith("*") and seg.endswith("*"):
            r=p.add_run(seg[1:-1]); r.italic=True
        else:
            r=p.add_run(seg); r.bold=bold_all; r.italic=italic
        r.font.size=Pt(size); r.font.color.rgb=base

def slide_cue(text):
    p=doc.add_paragraph(); shade(p,SLIDEBG); border_left(p,"2F6FE0")
    p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(4)
    r=p.add_run("▶  "+text); r.bold=True; r.font.size=Pt(10.5); r.font.color.rgb=BLUE

def say(text):
    p=doc.add_paragraph(); shade(p,SAYBG); border_left(p,"9DB4D6",sz='12')
    p.paragraph_format.space_after=Pt(6); p.paragraph_format.left_indent=Inches(0.06)
    add_runs(p,text,base=RGBColor(0x14,0x24,0x3A),size=11.5)

def note(text):
    p=doc.add_paragraph(); shade(p,NOTEBG); border_left(p,"C79A3A")
    p.paragraph_format.space_after=Pt(6)
    add_runs(p,text,base=AMBER,size=10,italic=True)

def para(text,size=11,base=DARK,after=6):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after); add_runs(p,text,base=base,size=size); return p
def bullet(text):
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(2); add_runs(p,text,size=10.5)

def H_presenter(idx,title,mins):
    doc.add_page_break()
    bar=doc.add_paragraph(); shade(bar,"F0F0F0")
    r=bar.add_run(f"PRESENTER {idx+1}"); r.bold=True; r.font.size=Pt(13); r.font.color.rgb=PRES[idx]
    r2=bar.add_run(f"   —   {title}"); r2.bold=True; r2.font.size=Pt(13); r2.font.color.rgb=DARK
    r3=bar.add_run(f"    ({mins})"); r3.font.size=Pt(10.5); r3.font.color.rgb=GREY
    line=doc.add_paragraph(); pr=line._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bot=OxmlElement('w:bottom')
    bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'14'); bot.set(qn('w:space'),'1')
    bot.set(qn('w:color'),'%02X%02X%02X'%(PRES[idx][0],PRES[idx][1],PRES[idx][2]))
    pb.append(bot); pr.append(pb); line.paragraph_format.space_after=Pt(8)

# ---------- COVER ----------
for _ in range(3): doc.add_paragraph()
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("VoxShield"); r.bold=True; r.font.size=Pt(42); r.font.color.rgb=BLUE
for txt,sz,col,it in [("The 12–15 Minute Pitch — Four-Presenter Script",18,DARK,False),
    ("TED-style · follows presentation.html chapter by chapter",12,GREY,True),
    ("",8,DARK,False),
    ("Team DigiSeva",13,GREEN,False),
    ("UCO Bank × Punjab & Sind Bank × IIT Kharagpur Hackathon · PS2 — Audio Forensics",11,DARK,False),
    ("",10,DARK,False),
    ("Every number is from the real, live system. Nothing exaggerated.",10.5,GREY,True)]:
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    if txt: rr=q.add_run(txt); rr.font.size=Pt(sz); rr.font.color.rgb=col; rr.italic=it; rr.bold=(sz>=13 and col!=GREY)
doc.add_paragraph()
leg=doc.add_paragraph(); leg.alignment=WD_ALIGN_PARAGRAPH.CENTER; shade(leg,SLIDEBG)
add_runs(leg,"How to read this script:   ▶ blue = which slide is up  ·  shaded = the words you say  ·  amber italic = delivery/coaching note.  Never read the slide — you are the voice.",size=9.5,base=GREY,italic=True)

# ---------- PRESENTER SPLIT NOTE ----------
doc.add_paragraph()
box=doc.add_paragraph(); shade(box,SAYBG); border_left(box,"9DB4D6")
r=box.add_run("Presenter map (equal split, ~3–3.5 min each)"); r.bold=True; r.font.size=Pt(11); r.font.color.rgb=BLUE
for t in ["P1 — Opening & the Problem  (Hook → Threat → Why Banks Fail)",
          "P2 — The Architecture & the AI  (Innovation → Pipeline → Six Models → Meta-Fusion)",
          "P3 — Fairness, Liveness & Beyond Detection  (+ live product)",
          "P4 — Results, Deployment, Business & the Close"]:
    bullet(t)

# ================= SCRIPT BODY =================

# ---- P1 ----
H_presenter(0,"THE PROBLEM","≈ 3 min")
slide_cue('SLIDE: "Your voice is no longer yours alone." — Opening Story')
note("Walk to centre. Pause. Let the room settle before the first word.")
say('"9:30 in the morning. A father is having his tea. His phone rings — and it\'s his son. The voice is shaking: \'Papa, I\'ve had an accident, I need fifty thousand rupees, right now, please.\' He doesn\'t stop to wonder *is this really my son* — he knows that voice. He\'s known it for twenty years. So he sends the money.')
say('That evening his son walks in the door. Safe. Cheerful. Hungry. He never made that call.')
say('Nobody hacked a bank that morning. Nobody stole a password or broke any encryption. The attacker defeated the one security system a bank can never patch — a father\'s trust in his own son\'s voice.')
say('We are Team DigiSeva. And VoxShield exists because voice — the oldest password humanity has — has just been broken."')
slide_cue('SLIDE: "Seconds to clone" / "Telephony hides the evidence" / "The damage happens fast" — The Threat')
say('"Three facts make this urgent.')
say('One — it is cheap. A few seconds of anyone\'s voice, from a reel, a voice note, a YouTube clip, is now enough for free software to clone them convincingly. Your voice is already out in the open.')
say('Two — the phone line helps the attacker. A real call is squeezed through a codec called G.711 — 8 kilohertz telephony. Think of it as a narrow letterbox that throws away all the high-frequency detail to save bandwidth. The problem is: the tiny giveaways a clone leaves behind live in exactly that high-frequency detail. So the phone line quietly erases the very evidence we need. This is why a detector trained on clean studio audio falls apart on a real call.')
say('Three — it\'s fast. By the time a human feels something is \'off\', the money has already moved. Fraud like this happens in the length of one phone call."')
slide_cue('SLIDE: "One model. One language. One point of failure." — Why Banks Fail')
say('"So why don\'t the tools we already have stop this? Because most deepfake detectors fail in three ways at once. They\'re *brittle* — one AI model, one blind spot; a new voice-generator it hasn\'t seen slips right past. They\'re *black boxes* — they output \'fake: 87%\' with no reason, and no bank officer can freeze a customer\'s payment on a number they can\'t explain. And they\'re *English-centric* — trained on American English, so on Tamil, Bengali, Punjabi, they wrongly flag *genuine* Indian customers as fakes.')
say('A detector that insults honest Indian customers is not a security system — it\'s a liability. What a bank needs isn\'t a better single model. It\'s a layered, honest defence. Priya will show you how we built one."')
note("Handoff — step back, gesture to P2.")

# ---- P2 ----
H_presenter(1,"THE ARCHITECTURE & THE AI","≈ 3.5 min")
slide_cue('SLIDE: "One layered, honest defence." — 01 Detection / 02 Fairness / 03 Liveness / 04 Honesty')
say('"Thank you, Aarav. VoxShield is built on four pillars, and I\'ll be honest about each: **Detection** — catch the fake. **Fairness** — never punish a real Indian customer. **Liveness** — make sure there\'s a living person on the line, not a recording. And **Honesty, engineered** — every verdict comes with a reason a human can read. Let me start with detection — the core AI."')
slide_cue('SLIDE: "Weak alone. Strong together." — the Six AI Models scoreboard')
say('"Here is our first honest admission. Look at our six detectors *individually* — most are mediocre. Our best single model gets a 16% error rate. Our weakest is basically a coin toss.')
say('When I say \'error rate\' I mean EER — Equal Error Rate. It\'s the single fairest score for a detector: the point where the mistakes calling fakes \'real\' equal the mistakes calling real voices \'fake\'. Lower is better. Zero would be perfect.')
say('So how do six weak detectors become one strong system? Two ideas. First — they\'re deliberately *different*. Some are big self-supervised models — \'SSL\' just means they taught themselves the shape of human speech by listening to enormous amounts of audio, like a child learning sound before words. Others are hand-built signal detectors — LFCC and CQCC are two mathematical ways of turning sound into a fingerprint, one tuned to even frequencies, one tuned musically across octaves. Different detectors get fooled by different fakes — so a generator that beats one runs into the next."')
slide_cue('SLIDE: Meta-fusion detail — weights, bias, Platt calibration')
say('"Second — the clever part — we don\'t just average their votes. We *learn* who to trust. This is meta-learning: a small \'referee\' model that has watched all six detectors on real data and learned each one\'s track record.')
say('Now, the part judges love. Two of our detectors have *negative* weights. That sounds like a bug. It\'s our favourite feature. We found two detectors that are *reliably wrong* on our data — and a detector that\'s consistently wrong is as useful as one that\'s consistently right: you flip its vote. When it screams \'real!\', the referee hears \'probably fake\'. We turned our worst models into informants.')
say('One more term — Platt calibration — it makes the final score mean what it says. When VoxShield outputs 0.9, it should be genuinely nine-times-in-ten fake, so an officer can trust the number, not just the label.')
say('The result: simple averaging gives 19% error. Our learned referee cuts that to **5.9%**, with an AUC of **0.983**. AUC is \'how well can it separate real from fake across every setting\' — 1.0 perfect, 0.5 guessing; 0.983 is excellent. That\'s roughly **94% honest accuracy** on a held-out test — not the 99% some vendors advertise, but a real, measured, defensible number. Rohan will show you the pillar that makes this fair for India."')
note("Handoff to P3.")

# ---- P3 ----
H_presenter(2,"FAIRNESS, LIVENESS & BEYOND","≈ 3.5 min")
slide_cue('SLIDE: "A detector that flags honest customers is a failed detector." — Fairness 36.3% → 6.3%')
say('"Thanks, Priya. This slide is our conscience. We took English-trained detectors and measured them on *genuine* speech in ten Indian languages. They wrongly flagged 36% of real Indian customers as fake. One in three honest people — insulted by the security system meant to protect them.')
say('Fairness here isn\'t a slogan — it\'s a measured number we publish, including our weak spots. We fixed it two ways. First, Indic routing: a fast language detector listens for a second, and if the call is an Indian language, it sends it to an Indian-aware version of the referee. Second, channel-aware thresholds — a phone line and a studio line get judged by different bars, because they distort sound differently.')
say('Result: false alarms on genuine Indian speech dropped from **36.3% to 6.3%**. And English accuracy did not move — still 5.9%. We added an Indian skill without losing an English one."')
slide_cue('SLIDE: "The 6th detector — an Indic specialist that can only escalate"')
say('"Then we built our own — the model we\'re proudest of. A sixth detector, trained by our team, on a rented GPU, in about thirty minutes, for around two dollars. We fine-tuned a 300-million-parameter multilingual speech model on 4,000 real Indian voices and 4,000 Indian fakes we synthesised ourselves.')
say('The safety design: this specialist can only ever *raise* the alarm, never lower it — and only when it\'s very confident on Indian audio. It can rescue a fake the other five missed, but it can *never* turn a real customer into a false alarm. On held-out Indian audio: zero false positives on real speakers. It lifted Indian-language clone-catching from 42% to 82% — nearly double — without costing a single genuine customer."')
slide_cue('SLIDE: "A recording can\'t answer a question from one second ago." — Liveness')
say('"Detection alone has a loophole. What if the attacker doesn\'t clone at all, and just *replays* a real recording of your voice? That\'s a replay attack, and it defeats a pure detector, because the audio *is* genuinely you.')
say('So VoxShield adds liveness — challenge-response. The system asks the caller to say four random digits, right now. A recording from ten minutes ago can\'t answer a question from one second ago. We check the digits are correct, spoken by a live voice, within a tight time window. Living person passes; playback fails."')
slide_cue('SLIDE: "Catch the fraud, not just the fake." — Digital Arrest Shield & the extra shields')
say('"And detection is only half the fraud. Sometimes the *voice is real* but the *situation is a scam* — the \'digital arrest\' calls where a fake \'officer\' terrifies a victim into paying. Our Digital Arrest Shield listens to the *intent*, tracking the classic scam arc — authority, threat, isolation, extraction — in Hindi, English and Hinglish, and warns the citizen: \'No real agency arrests you over a call. Hang up and dial 1930.\' It stops the payment, not just logs the fraud.')
say('Around this sit voice enrolment and verification — a voiceprint check for the real account-holder — and fraud-ring linkage, connecting one fake voice across many victims. This isn\'t a slide deck. It\'s live. Meera will show you."')
note("Handoff to P4.")

# ---- P4 ----
H_presenter(3,"RESULTS, DEPLOYMENT, BUSINESS & CLOSE","≈ 3.5 min")
slide_cue('SLIDE: "Not a deck. A working system." — live demo')
say('"Thank you, Rohan. Everything you\'ve heard runs today. *(Gesture to demo.)* We drop in a call, and in about two seconds the verdict comes back — a score, a HIGH/MEDIUM/LOW label, and five plain-English reason codes an operator can read aloud: low jitter, too-regular high band, no breath. And it scores you *while you\'re still speaking* — flagging a fake around three seconds in, well inside a ten-second target."')
slide_cue('SLIDE: "Numbers we can defend." — scoreboard, fusion value, red-team')
say('"The honest scoreboard. Held-out test: **5.9% equal-error-rate**, AUC **0.983**, **93.4% accuracy** at our deployed threshold, precision 93.5%, recall 92.9%.')
say('What does fusion buy that a single-model API can\'t? Our best *single* detector was 16% error — the fusion is 5.9%. Nearly three times better, and it degrades gracefully when a new generator appears, because six different models don\'t share one blind spot.')
say('And we red-teamed *ourselves* — the honesty pillar. We\'re transparent about where we\'re weaker: we handle phone codecs and compression well — Opus actually *improves* us — but aggressive pitch-shifting and heavy background noise still push our error up. We publish that, because a bank should buy a system that knows its own limits, not one that hides them."')
slide_cue('SLIDE: "Built for a bank\'s basement, not our cloud." — architecture, scalability, DPDP')
say('"Deployment — this matters to a public-sector bank: VoxShield runs *on-premise*, on CPU, inside the bank\'s own walls. Customer voice never leaves the building — exactly what the DPDP Act, India\'s data-protection law, demands. Our live system today runs on a single modest box — 4 cores, 8 gigs of memory, about twenty-five dollars a month — and it scales like an ordinary web service, because that\'s all it is: an API. No exotic hardware. A bank can run this in the basement."')
slide_cue('SLIDE: "India\'s banking future is voice-first." + "One AI platform. Every voice." — Business & Vision')
say('"Why does this win? Voice is the channel Indian banking *cannot* abandon — IVR, phone banking, voice assistants, hundreds of millions of callers, many who can\'t type but can speak. Global players — Pindrop, Reality Defender — are excellent, but English-first and cloud-first. None do Indian languages *and* on-premise *and* liveness *and* scam-intent together. That combination is our moat, and fairness is the part a public-sector bank can actually procure.')
say('And the same engine — voice authentication with an explanation — extends beyond banking to insurance, telecom, healthcare, government. One API, many sectors."')
slide_cue('SLIDE: "The generators will improve. So will the shield." — Closing Story')
note("Slow down. Come back to the father.")
say('"Let\'s go back to that father, and that morning call. In a world with VoxShield, before the money moves, the system has already listened. It hears the too-perfect breath, the high band that\'s a shade too clean, and it says — gently, with its reasons — \'this voice was not born from a human throat.\' The transfer pauses. The father calls his son. His son picks up, safe, and confused why Papa sounds so shaken.')
say('The people building these fakes will keep getting better. We know that. So our honest promise isn\'t \'we\'ve won.\' It\'s this: the generators will improve — and so will the shield. VoxShield is how we make sure that when your family calls, the person on the line is really them.')
say('We are Team DigiSeva. Thank you."')
note("All four presenters step forward together for questions.")

# ---------- APPENDIX ----------
doc.add_page_break()
p=doc.add_paragraph(); r=p.add_run("Appendix — Fast answers to expected judge questions"); r.bold=True; r.font.size=Pt(15); r.font.color.rgb=BLUE
p.paragraph_format.space_after=Pt(8)
qa=[
 ("\"Why 94% and not 99%?\"","Ours is a held-out, honest number on real-world In-the-Wild data at a fixed threshold. Vendor 99%s are usually clean-audio, in-distribution, best-case. We defend a real number."),
 ("\"Negative weights — isn't that overfitting?\"","Learned on training folds, validated on a held-out set; two detectors are systematically anti-correlated with truth on our data, so flipping them is principled, not a fluke."),
 ("\"36.3% vs the 11.7% in your handbook?\"","Two baselines: 36.3% = English-only detectors on Indic speech (deck's before-any-Indic-work number); 11.7% = after Indic routing, before channel-aware thresholds. Both land at 6.3% deployed. Pick ONE baseline and state it consistently on stage."),
 ("\"100% Indic recall?\"","In-distribution, against the specific engine we trained on (MMS-TTS). Real-world coverage broadens as we add more generators; we say this plainly."),
 ("\"Security features on the slides (auth, encryption)?\"","Several are roadmap (\"AES-256-ready\"), not shipped. On-prem + DPDP-by-design is real today; enterprise auth/RBAC is next. Be honest if asked."),
]
for q,a in qa:
    pp=doc.add_paragraph(); pp.paragraph_format.space_after=Pt(1)
    r=pp.add_run("Q  "+q); r.bold=True; r.font.size=Pt(10.5); r.font.color.rgb=AMBER
    pa=doc.add_paragraph(); pa.paragraph_format.space_after=Pt(6); pa.paragraph_format.left_indent=Inches(0.2)
    add_runs(pa,"A  "+a,size=10.5)
# term one-liners
pp=doc.add_paragraph(); r=pp.add_run("Term one-liners"); r.bold=True; r.font.size=Pt(11); r.font.color.rgb=BLUE
for t in ["EER = error rate where false-real and false-fake mistakes are equal (lower better).",
          "AUC = separability across all settings; 1.0 perfect, 0.5 guessing.",
          "SSL = model that self-taught speech from raw audio.",
          "LFCC / CQCC = two ways to fingerprint sound (even-frequency vs musical/octave).",
          "Platt calibration = makes the score's probability honest.",
          "G.711 = 8 kHz phone codec that erases high-frequency clone artifacts."]:
    bullet(t)

out="/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/VoxShield_4Presenter_TED_Script.docx"
doc.save(out); print("SAVED",out)
