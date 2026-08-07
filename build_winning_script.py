#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VoxShield — complete 4-presenter script covering EVERY chapter of presentation.html.
Renders a styled teleprompter/handout DOCX."""
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BLUE=RGBColor(0x1F,0x4E,0x8C); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55)
GREEN=RGBColor(0x1F,0x7A,0x33); ACCENT=RGBColor(0x2F,0x6F,0xE0); AMBER=RGBColor(0x8A,0x54,0x00)
PLUM=RGBColor(0x7A,0x27,0x5E)
SLIDEBG="EAF1FB"; SAYBG="F5F8FC"; NOTEBG="FBF3E6"; TERMBG="EEF6EE"
PRES=[BLUE,GREEN,PLUM,AMBER]

doc=Document()
st=doc.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(11); st.font.color.rgb=DARK
st.paragraph_format.space_after=Pt(6); st.paragraph_format.line_spacing=1.15
for s in doc.sections:
    s.left_margin=s.right_margin=Inches(0.85); s.top_margin=s.bottom_margin=Inches(0.75)

def shade(p,hexc):
    pr=p._p.get_or_add_pPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),hexc); pr.append(sh)
def bl(p,hexc,sz='16'):
    pr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); l=OxmlElement('w:left')
    l.set(qn('w:val'),'single'); l.set(qn('w:sz'),sz); l.set(qn('w:space'),'8'); l.set(qn('w:color'),hexc); pb.append(l); pr.append(pb)
def runs(p,text,base=DARK,size=11,italic=False):
    for seg in re.split(r'(\*\*.+?\*\*|\*[^*]+?\*)',text):
        if not seg: continue
        if seg.startswith("**") and seg.endswith("**"): r=p.add_run(seg[2:-2]); r.bold=True
        elif seg.startswith("*") and seg.endswith("*"): r=p.add_run(seg[1:-1]); r.italic=True
        else: r=p.add_run(seg); r.italic=italic
        r.font.size=Pt(size); r.font.color.rgb=base

def chapter(text):
    p=doc.add_paragraph(); shade(p,SLIDEBG); bl(p,"2F6FE0","20")
    p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(4)
    r=p.add_run("■  "+text); r.bold=True; r.font.size=Pt(12.5); r.font.color.rgb=BLUE
def cue(text):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(6); p.paragraph_format.space_after=Pt(2)
    r=p.add_run("▶ SLIDE — "+text); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=GREY
def say(text):
    p=doc.add_paragraph(); shade(p,SAYBG); bl(p,"9DB4D6","10")
    p.paragraph_format.space_after=Pt(6); p.paragraph_format.left_indent=Inches(0.05)
    runs(p,text,base=RGBColor(0x14,0x24,0x3A),size=11.5)
def note(text):
    p=doc.add_paragraph(); shade(p,NOTEBG); bl(p,"C79A3A")
    p.paragraph_format.space_after=Pt(6); runs(p,"◆ "+text,base=AMBER,size=9.5,italic=True)
def term(word,defn):
    p=doc.add_paragraph(); shade(p,TERMBG); bl(p,"1F7A33")
    p.paragraph_format.space_after=Pt(6)
    r=p.add_run("Explain simply — "+word+":  "); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=GREEN
    runs(p,defn,base=RGBColor(0x24,0x4A,0x24),size=10)
def bullet(text):
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(2); runs(p,text,size=10.5)

def presenter(idx,title,mins,covers):
    doc.add_page_break()
    bar=doc.add_paragraph(); shade(bar,"F0F0F0")
    r=bar.add_run(f"PRESENTER {idx+1}"); r.bold=True; r.font.size=Pt(14); r.font.color.rgb=PRES[idx]
    r2=bar.add_run(f"   —   {title}"); r2.bold=True; r2.font.size=Pt(14); r2.font.color.rgb=DARK
    r3=bar.add_run(f"    ({mins})"); r3.font.size=Pt(10.5); r3.font.color.rgb=GREY
    ln=doc.add_paragraph(); pr=ln._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bot=OxmlElement('w:bottom')
    bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'14'); bot.set(qn('w:space'),'1'); bot.set(qn('w:color'),'%02X%02X%02X'%(PRES[idx][0],PRES[idx][1],PRES[idx][2]))
    pb.append(bot); pr.append(pb); ln.paragraph_format.space_after=Pt(4)
    c=doc.add_paragraph(); c.paragraph_format.space_after=Pt(8); runs(c,"Covers: "+covers,base=GREY,size=9.5,italic=True)

# ============ COVER ============
for _ in range(3): doc.add_paragraph()
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("VoxShield"); r.bold=True; r.font.size=Pt(44); r.font.color.rgb=BLUE
for txt,sz,col,bold in [("The Complete Presentation Script — Four Presenters",18,DARK,True),
    ("Every chapter of the deck, in order · TED-style · explained clearly",12,GREY,False),
    ("",8,DARK,False),
    ("Team DigiSeva · SRM Institute of Science and Technology",13,GREEN,True),
    ("UCO Bank · Punjab & Sind Bank · IIT Kharagpur — PS2, Audio Forensics for Voice Security · TRL-5",10.5,DARK,False)]:
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    if txt: rr=q.add_run(txt); rr.font.size=Pt(sz); rr.font.color.rgb=col; rr.bold=bold; rr.italic=(col==GREY)
doc.add_paragraph()
leg=doc.add_paragraph(); leg.alignment=WD_ALIGN_PARAGRAPH.CENTER; shade(leg,SLIDEBG)
runs(leg,"How to read:  ■ chapter of the deck  ·  ▶ which slide is up  ·  shaded block = the words you say  ·  green = a term to explain simply  ·  ◆ amber = delivery note.  Never read the slide — you are the voice.",size=9.5,base=GREY,italic=True)
doc.add_paragraph()
mp=doc.add_paragraph(); shade(mp,SAYBG); bl(mp,"9DB4D6")
r=mp.add_run("Four-presenter division (follows the deck's own chapters)"); r.bold=True; r.font.size=Pt(11); r.font.color.rgb=BLUE
for t in ["P1 — The Hook & the Problem:  Introduction · Prologue · Ch.01 Threat · Ch.02 Why Banks Fail",
          "P2 — The Solution & the AI Core:  Ch.03 Innovation · Act.05 The Live Pipeline · Ch.04 Six AI Models",
          "P3 — Fairness, Liveness & Intelligence:  Ch.05 Fairness · Ch.06 Liveness · Ch.07 Beyond Detection",
          "P4 — Proof, Deployment, Business & Close:  Ch.08 Product · Ch.09 Results · Ch.10 Deployment · Ch.11 Market/Business · Ch.12 Vision · Epilogue"]:
    bullet(t)
tnote=doc.add_paragraph(); tnote.paragraph_format.space_before=Pt(6)
runs(tnote,"Timing: the full script runs ~18 min if every word is read. For a strict 12–15 min slot, keep all of P1–P3 and trim the Enterprise/Business sub-slides in Ch.11 (marked ‘compress if short on time’). Everything is here so nothing is skipped.",base=GREY,size=9.5,italic=True)

# ================= PRESENTER 1 =================
presenter(0,"THE HOOK & THE PROBLEM","≈ 4 min","Introduction · Prologue · Chapter 01 The Threat · Chapter 02 Why Banks Fail")

chapter("Introduction — title slide (01/18)")
cue("VoxShield title · 'Real-time AI voice-clone detection for Indian banking' · TRL-5, Working System")
note("Walk on. Warm, confident, unhurried. Make eye contact before the first word.")
say("\"Good morning, respected judges. We are **Team DigiSeva**, from SRM Institute of Science and Technology. For the next twelve minutes, we'd like to tell you a story — because the problem we're solving doesn't begin with AI models or algorithms. It begins with a phone call.")
say("Our project is **VoxShield** — a real-time AI voice-clone detection platform designed for Indian banking. By combining **six complementary detectors, a learned fusion model, language-aware fairness, and challenge-response liveness**, VoxShield helps identify high-risk voice-impersonation attempts within the **first ten seconds** of a call. Let us show you why that matters.\"")

chapter("Prologue — 'One Call. One Approval. One Invisible Fraud.'")
cue("The 10 a.m. call · every check satisfied · ₹8,47,000 → ₹97,000 · 'I never made that call.'")
say("\"It's 10 a.m. A customer-service representative at a bank receives an incoming call. The caller sounds calm, confident, and familiar. They know the customer's name, their account information, and their recent transaction history — and they correctly answer the identity-verification questions the agent asks.")
say("For the particular request they're making, the bank follows its normal verification process. And if additional verification such as an **OTP** is required — the attacker has *already obtained it*, through social engineering or another compromise. So from the agent's perspective, **every required check has been satisfied.** The request is approved.")
say("A few minutes later, the *real* customer opens the banking app. Their balance has dropped from **₹8,47,000 to ₹97,000.** They immediately call the bank and say: *'I never made that call.'*\"")
note("Beat. Let those four words sit for a second before you ask 'what happened?'")
say("\"So what happened? **No banking server was hacked. No malware broke into the bank. No insider transferred the money.** Instead, the attacker combined stolen personal information, social engineering, and an **AI-generated clone of the customer's voice** to convincingly impersonate the customer throughout the verification process.")
say("And this is the key point. **Voice cloning does not replace existing banking security — it *strengthens* an impersonation attack, by making the fraudster sound exactly like the genuine customer.** As AI voice synthesis becomes increasingly realistic, a familiar voice is no longer sufficient evidence that the caller is genuine.")
say("That is exactly the gap VoxShield is designed to close. Instead of relying only on what the caller *knows*, or on how convincing they *sound*, VoxShield gives the bank an **independent, AI-powered assessment of whether the voice itself appears genuine or synthetically generated** — so that high-risk calls can be routed for additional verification, **before money moves.**\"")
note("The Prologue is deliberately more careful than the title-slide bullets (which say 'No OTP intercepted'). Here the OTP WAS obtained via social engineering — a more defensible framing. Don't read the slide's bullet list aloud; tell this version instead.")

chapter("Chapter 01 · The Threat — 'Your voice is no longer yours alone.'")
cue("Human voice vs AI clone waveform · micro-variation vs eerie regularity")
say("\"Here's the uncomfortable truth. Consumer voice-cloning tools can now copy a person from a *short* clip of audio — a voicemail greeting, a social-media post, a customer-care recording. The fake sounds human, and the bank's phone line simply cannot tell the difference.")
say("But there is a tell. A real human voice carries tiny, constant imperfections — we call them **jitter, shimmer, and breath**: micro-wobble in pitch, micro-wobble in loudness, and the sound of actually breathing. A cloned waveform is eerily *regular* — too clean, too perfect. That unnatural regularity is the fingerprint VoxShield reads.\"")
cue("How an AI voice clone is really created — the 7-step assembly line")
say("\"And making one is frighteningly industrial. It's a seven-step assembly line: **one**, grab ten to thirty seconds of voice from Instagram or WhatsApp. **Two**, clean the noise. **Three**, a *speaker encoder* turns the voice into a 192-number 'voiceprint'. **Four**, a neural text-to-speech model — VITS, XTTS, MMS-TTS — learns to speak in that voice. **Five**, a *vocoder* like HiFi-GAN turns it into an audio waveform. **Six**, a GPU runs it in real time. **Seven**, it's pushed through the phone codec so it sounds like a normal call. Start to finish: **under one minute.** That is the exact door VoxShield closes.\"")
cue("Three threat cards — cheap · telephony hides evidence · damage is fast")
say("\"Three facts make this urgent. **One — it's cheap:** these tools are public, multilingual, and need only seconds of audio. **Two — the phone line helps the attacker:** bank calls travel over 8-kilohertz lines with a codec called **G.711**, and that codec smears away exactly the high-frequency detail most detectors rely on — a detector trained only on clean studio audio goes *blind* on a real call. **Three — it's fast:** a verdict that arrives after the call ends is forensics, not protection. Detection has to happen inside the first seconds.\"")
term("G.711","the standard telephone codec. It squeezes a call down to 8 kHz — a narrow letterbox — to save bandwidth, and in doing so it deletes the high-frequency clues a clone leaves behind. The phone line quietly erases our evidence.")

chapter("Chapter 02 · Why Banks Fail — 'One model. One language. One point of failure.'")
cue("Three failure cards — brittle · black-box · English-centric")
say("\"So why don't today's tools stop this? We measured the standard approaches before building our own, and every off-the-shelf answer breaks in the same three places.")
say("**One — single detectors are brittle.** On held-out real-world data, the individual detectors we tested ranged from a 16% to a 62% error rate. A voice-generator the model has never seen walks straight through. **Two — they're black boxes.** 'The AI said fraud' is not a reason a bank can freeze an account on. An operator, an auditor, and a regulator each need a *reason* they can read — or the tool never leaves the pilot. **Three — they're English-centric, and that punishes India.** Detectors trained on English misread Indian languages and accents as 'synthetic', so genuine Tamil or Bengali customers get flagged as fraudsters. A detector that is *unfair* is a detector a bank cannot deploy.\"")
cue("The gauntlet — original → clone → codec → noise → replay → 8 kHz → most detectors fail")
say("\"And catching it is hard because the audio runs a gauntlet before it ever reaches a detector: the clone's artifacts, then phone compression that strips everything above 4 kHz, then background noise, then — often — a **replay**, where the fraudster simply plays the clone through a speaker. By the time it arrives, a studio-only detector is already defeated.\"")
say("\"Here's the key insight that shaped our whole design: even a *perfect* detector loses to that replay attack — because played through a speaker, the acoustic path launders the digital fingerprints away. **Detection alone is not a defence. It needs layers.** And that is exactly what we built. Priya will take you inside it.\"")
note("Handoff — turn to P2, step back.")

# ================= PRESENTER 2 =================
presenter(1,"THE SOLUTION & THE AI CORE","≈ 4.5 min","Chapter 03 Innovation · Act 05 The Live Pipeline · Chapter 04 Six AI Models, One Brain")

chapter("Chapter 03 · Our Innovation — 'One layered, honest defence.'")
cue("Four pillars — Detection · Fairness · Liveness · Honesty")
say("\"Thank you, Aarav. VoxShield is **not a model** — it's a defence-in-depth system, built on four honest pillars.")
say("**Pillar one, Detection:** six deliberately *different* detectors — a signal-physics model, hand-crafted anti-spoofing features, three neural models, and an Indian-language specialist — fused by a learned meta-brain into one calibrated score. **Pillar two, Fairness:** we evaluated on genuine speech in ten Indian languages, retrained to be Indic-aware, and stress-tested under real 8-kilohertz telephony — so a real customer speaking Telugu is never treated as a threat. **Pillar three, Liveness:** a random challenge — 'say four, seven, two' — that a recording simply cannot answer. **Pillar four, Honesty, engineered:** every verdict ships with plain-language reason codes, every clip is hashed into an audit trail, and a high-risk flag *never* auto-blocks — it routes to a human, inside the bank's existing workflow.\"")

chapter("Act 05 · How VoxShield Thinks — 'One live call, end to end.'")
cue("The six-stage live pipeline · verdict inside 10 seconds · every block is a running component")
say("\"Now let me walk you through one real call, end to end — and every block I mention is live, running code, in the exact order the audio flows.")
say("**Stage one, Ingest.** The 8-kHz call arrives, we capture the audio, a voice-activity gate drops the silence, we cut it into rolling **3-second windows every 1 second**, and normalise to 16-kHz mono. **Stage two, Understand** — we turn that sound into **89 numbers**: our feature bank. **Stage three, Detect** — those numbers hit **six detectors in parallel**. **Stage four, Decide** — the meta-fusion brain blends their votes, calibrates the score, and the risk engine calls it Low, Medium, or High. **Stage five, Defend** — reason codes, speaker verification, the liveness challenge, the scam-intent shield, fraud-ring intelligence. And **stage six, Act** — it *never* auto-blocks; it routes to a human, logs a tamper-evident hash, and the raw audio is never stored. That entire journey finishes inside ten seconds.\"")
term("The 89 numbers","two 'fingerprint' families — LFCC and CQCC — plus phase, plus prosody (pitch jitter and shimmer), plus high-frequency vocoder energy above 6 kHz. Together they describe a voice the way a forensic analyst would.")

chapter("Chapter 04 · Six AI Models, One Brain — 'Weak alone. Strong together.'")
cue("The six detectors, as six personalities")
say("\"This is the heart of it — and it starts with a confession. Look at our six detectors *individually*, and most of them are mediocre. That's the whole point. Let me introduce them as six specialists.")
say("**The Physicist — Acoustic DSP.** It reads the raw physics: phase, pitch, high-frequency energy, breathing. Weak alone — a 47% error rate — but always explainable, and it never misses a physical tell. **The Listener — a Wav2Vec2 model** that taught itself what human speech sounds like from millions of hours of audio; weak alone at 62%, but it's *wrong in a different direction* from the others, which is exactly why fusion needs it. **The Linguist — XLS-R 300M**, pretrained across 128 languages so accents never fool it; our strongest single detector at a **16% error rate**. **The Fast Expert — DistilHuBERT**, fine-tuned on real in-the-wild fakes, quick and sharp at 23%. **The Forensic Analyst — our LFCC-plus-CQCC head**, hand-built and trained with codec augmentation — the one detector built *for* the phone line, robust where studio-only models go blind. And **the India Specialist — the Indic booster** — I'll let Rohan tell that story, but it nearly doubles our Indian-language catch rate.\"")
term("SSL (self-supervised learning)","a model that taught itself the shape of speech by listening to enormous amounts of audio, before ever being told what's fake — like a child learning sound before words. XLS-R and Wav2Vec2 are SSL models.")
term("LFCC & CQCC","two mathematical ways to turn a sound into a fingerprint. LFCC spaces its detail evenly across frequency; CQCC spaces it musically, across octaves. They catch different fakes, so we use both.")
cue("The architecture diagram · meta-fusion z = Σ wᵢ·pᵢ + b · Platt σ(6.45z − 3.15) · HIGH ≥ 0.70")
say("\"So how do six weak detectors become one strong system? A **meta-learner** — a referee. We trained a small model on a *separate* slice of data to learn each detector's track record: who to trust, and by how much. And here is the part we're proudest of, because it's the honest part. **Two of our detectors were given *negative* weights.** That sounds like a bug. It's our favourite feature — we found two models that are *reliably wrong* on this data, and a detector that's consistently wrong is as useful as one that's consistently right: you simply flip its vote. We turned our two worst models into informants. Finally, **Platt calibration** makes the score honest — when VoxShield says 0.9, it genuinely means nine-in-ten fake.\"")
term("Meta-learning / stacking","instead of averaging the detectors, a referee model *learns* how much each one's opinion is worth — including learning to distrust the unreliable ones.")
term("Platt calibration","a final adjustment that makes the output a true probability, so an officer can trust the number itself, not just the 'fake / real' label.")
cue("The scoreboard bar chart — 62.4 · 46.9 · 26.8 · 23.0 · 16.0  →  5.9 meta-fusion")
say("\"And the results justify the whole design. Best single detector: 16% error. Simple *averaging* of all of them: **19% — actually worse than the best one alone.** But the *learned* stacker crushes it to **5.9%**. Let that sink in — naive averaging makes things worse; only a referee that has learned who to trust beats every individual model. Two terms so you can follow the numbers: **EER**, equal-error-rate, is the fairest single score for a detector — lower is better; and **AUC** is how cleanly it separates fake from real — 1.0 is perfect, 0.5 is a coin toss. Ours is 5.9% EER and 0.983 AUC.\"")
term("EER (Equal-Error-Rate)","the point where the two kinds of mistake — calling a fake 'real' and calling a real voice 'fake' — are equal. One fair number for a detector. Lower is better; zero is perfect.")
cue("Five reason codes — SSL · PH · HF · PR · BR  ·  'watch one detection, second by second'")
say("\"Every verdict explains itself in five codes an operator can read aloud: **SSL**, the overall neural likelihood; **PH**, unnaturally regular phase; **HF**, the vocoder's high-frequency fingerprint; **PR**, missing prosody — no natural pitch wobble; and **BR** — because a text-to-speech engine inserts *silence* where a human would breathe. On the live demo you can watch this happen: every second a new window is scored, evidence accumulates, and on a real synthetic clip the flag fires **HIGH at 3.0 seconds**, with codes PH, HF and PR, and a hash written to the audit ledger. Rohan will now show you how we make this *fair* — and how we defeat the replay attack.\"")
note("Handoff to P3.")

# ================= PRESENTER 3 =================
presenter(2,"FAIRNESS, LIVENESS & INTELLIGENCE","≈ 4 min","Chapter 05 Fairness · Chapter 06 Liveness · Chapter 07 Beyond Detection")

chapter("Chapter 05 · The Fairness Breakthrough — 'A detector that flags honest customers is a failed detector.'")
cue("36.3% → 6.3% false-positive rate on genuine Indian-language speech")
say("\"Thank you, Priya. This chapter is our conscience. We ran the full ensemble over *genuine* Indian speech — real customers, in ten languages, from the IndicVoices dataset — and counted how often we wrongly flagged them. The English-trained models flagged **36% of real Indian customers as fake.** More than one honest person in three, insulted by the system meant to protect them.")
say("We fixed it two ways. **Indic routing** — a fast on-device language detector listens for a second, and if the call is an Indian language, it goes to an Indian-aware version of the referee. And **channel-aware thresholds** — a phone line and a studio line are judged by different bars. Together, false alarms on genuine Indian speech fell from **36.3% to 6.3%.**\"")
term("Fairness (here)","not a slogan — a *measured* number. We count how often real customers of each language are wrongly flagged, and we publish it, including our weak spots.")
cue("Per-language table — Marathi 0% … Telugu 13.3% (our weakest, shown honestly)")
say("\"And we publish the uncomfortable numbers. Marathi: zero false positives. Tamil, Bengali, Punjabi: 3.3%. But **Telugu is still our weakest at 13.3%**, and under a real phone line the rates climb further. We don't hide that — we design around it: we train with phone-codec augmentation, we make a detected phone line clear a *stricter* 0.85 bar before we ever say HIGH — which protects genuine callers while a real clone, which scores around 0.96, still flags — and we let *liveness*, not detection alone, gate any action on a customer.\"")
cue("'Fairness cuts both ways' + the 6th detector — ROUTE · VETO↑ · SAFE")
say("\"Fairness cuts both ways, though — those English models were also blind to Indian-language *fakes*. So we synthesised an Indian-language deepfake set and trained an Indic-aware path — and Indian-language clone-catching jumped from **42% to 82%**, while English performance stayed *exactly* the same at 5.9%.")
say("On top of that sits our **sixth detector** — a fine-tuned XLS-R model we trained ourselves on Indian deepfakes, with three safety rules. **ROUTE:** it fires only on Indian audio, so English is untouched. **VETO-up:** it can only ever *raise* a verdict, on a confident fake, and only above 0.85 — it can never *lower* one. And **SAFE:** because it can only escalate, it adds catching-power without adding a single false alarm on a genuine speaker. And if its model is ever missing, it's a silent no-op — the system just runs without it. That is how you help without ever hurting.\"")

chapter("Chapter 06 · Liveness — 'A recording can't answer a question from one second ago.'")
cue("Challenge-response · random digits · three checks")
say("\"Now, the replay attack Aarav warned you about — where the fraudster plays a clone through a speaker and launders away every digital artifact. No pure detector beats that. So we don't try to. We ask a question.")
say("The moment a call is challenged, the system generates **random digits** — say, zero, eight, one — and asks the caller to say them, live. A recording made ten minutes ago cannot contain numbers that didn't exist when it was recorded. Then we run **three checks at once. Content:** Whisper speech-recognition transcribes the reply — do the digits match, including 'four seven two' spoken as words? **Liveness:** the full ensemble scores the reply itself — is this a live human, or an engine generating the digits on the fly? And **Timing:** did the answer arrive inside the window? A pass needs all three.\"")
say("\"And notice how each attack dies to a different check: a **played-back recording** fails content; a **real-time text-to-speech** fails liveness; a **slow human relay** trying to game it fails timing. Every escape route is closed by a different door.\"")

chapter("Chapter 07 · Beyond Detection — 'Catch the fraud, not just the fake.'")
cue("Digital Arrest Shield · Citizen warning · Voice enrolment · Fraud-ring linkage · Explainable")
say("\"Real-versus-fake is table stakes. The layer that actually wins a bank is the intelligence on top — and all of this is live today.")
say("**The Digital Arrest Shield.** Sometimes the voice is real but the *situation* is the scam — those 'digital arrest' calls where a fake officer terrifies a victim. We fuse the voice-clone score with a read of the *intent*, and we track the scam's live script — **Authority, then Threat, then Isolation, then Extraction.** A cloned voice running that full playbook is flagged CRITICAL — in English, Hindi *and* Hinglish, because that's how the nineteen-thousand-crore scam is actually run.")
say("**The citizen-protection warning:** on a digital-arrest verdict, VoxShield doesn't just log it — it *speaks* a warning in the victim's own language, echoing the government's own line: *'no real agency arrests you over a call — hang up and dial 1930.'* It stops the payment, not just records it.")
say("**Voice enrolment and verification:** a real speaker-embedding answers two questions at once — is this the enrolled customer, *and* is the voice a live human? A clone of the customer passes identity but fails liveness — the decisive **'rejected: clone'** case that no identity-check-alone system can catch. **Fraud-ring linkage** keeps a rolling voiceprint and links the same cloned voice across dozens of victims, even through the phone codec. And every verdict is **explainable, live** — streaming its reasoning, attributing the likely generator, and even localising *which seconds* are AI.\"")
cue("Identity × liveness table — VERIFIED / REJECTED-CLONE / REJECTED-IDENTITY")
say("\"This one table is the whole idea. Identity alone says 'it's the customer's voice' — and a clone passes. Detection alone says 'it's synthetic' — but not whose. VoxShield fuses both. Genuine customer: identity yes, live yes — **VERIFIED.** A clone of the customer: identity yes, but synthetic — **REJECTED as a clone.** A different attacker: identity no — **REJECTED on identity.** All three verified end-to-end, through real endpoints running today. Meera will now show you it's not a slide — it's a product.\"")
note("Handoff to P4.")

# ================= PRESENTER 4 =================
presenter(3,"PROOF, DEPLOYMENT, BUSINESS & THE CLOSE","≈ 5 min","Ch.08 Product · Ch.09 Results · Ch.10 Deployment · Ch.11 Market & Business · Ch.12 Vision · Epilogue")

chapter("Chapter 08 · Real Product, Running Today — 'Not a deck. A working system.'")
cue("Five live screenshots — Operator Console · Live Call · Liveness · Bank Integration · Beyond the Fraud Desk")
say("\"Thank you, Rohan. Everything you've heard is running — a FastAPI backend, the full ensemble, streaming analysis, liveness, and a live two-party call. This is **TRL-5**: validated in a relevant environment. Five screens, quickly.")
say("**One, the Operator Console** — drop in a call, read the calibrated verdict, the per-detector breakdown, the spectrogram, and plain reason codes, on one screen built for a fraud desk, not a data scientist — and accessible, WCAG 2.1 AA, risk shown by icon *and* text, never colour alone. **Two, Live Call Analysis** — a two-party call scored every two seconds; the flag fires the instant the running score crosses threshold, verified at 3.0 seconds. **Three, the Liveness Challenge** as the caller sees it — random digits, a recording window, a three-check verdict. **Four, the Bank Integration view** — risk feeds the *existing* fraud flow alongside caller-ID and CNAP; high risk routes to step-up; nothing is ever auto-blocked. And **five, Beyond the Fraud Desk** — the same drop-in API guards IVR, voice payments, agent-assist, and KYC, documented at /docs.\"")

chapter("Chapter 09 · Measured Results — 'Numbers we can defend.'")
cue("Stat tiles — 5.9% EER · 0.983 AUC · 93.4% acc · 3.0 s flag · 6.3% Indic FP · 0.9 s GPU")
say("\"And these numbers are all *held-out* — test clips the system never trained on. No cherry-picking, no 'up to'. **5.9% equal-error-rate**, down from 19% for naive averaging and 16% for the best single model — a **three-times** error reduction from the meta-learner. **AUC 0.983** — near-perfect ranking. **93.4% accuracy** at our deployed threshold, with precision 93.5% and recall 92.9%. **Time-to-flag: 3.0 seconds**, well inside our ten-second target. Indic false-positives down to **6.3%**. And on a real phone line, genuine callers wrongly flagged dropped from 23% to single digits once the model is channel-tuned. Speed: about **0.9 seconds per verdict on a GPU**, three-to-eight on a plain CPU — the bank picks the tier.\"")
cue("The scoreboard — seven systems on the same held-out test")
say("\"Here is the comparison that justifies the architecture — seven systems, same held-out test. Individually: Wav2Vec2 at 62%, Acoustic DSP at 47%, the LFCC-CQCC head at 27%, DistilHuBERT at 23%, XLS-R our best single at 16%. Simple averaging: 19% — again, *worse* than the best single. Our **meta-fusion: 5.9%**, AUC 0.983, 93.4% accuracy. F1 of 0.93, with just 10 false positives and 11 false negatives on the test. We show this because the honesty *is* the argument — only the learned stacker beats both the best model and the naive blend.\"")
cue("Fusion vs a single-model API — the capability table")
say("\"And against the typical single-model cloud API, the difference isn't a benchmark point, it's a different *category*: decorrelated multi-model detection instead of one blind spot; calibrated probabilities instead of raw scores; explainable reason codes instead of a black box; measured Indian-language fairness instead of English-only; replay-defeating liveness instead of detection alone; a verdict *inside* the live call instead of an upload after the fact; on-prem instead of cloud-only; and a never-auto-block safety guarantee instead of 'here's a score, good luck.'\"")

chapter("Chapter 10 · Deployment & Trust — 'Built for a bank's basement, not our cloud.'")
cue("On-prem / air-gapped · SHA-256 audit · never auto-block · full architecture")
say("\"Deployment is where a public-sector bank decides yes or no. VoxShield is a **stateless API the bank runs on its own premises — air-gapped if it wants.** The Docker image bakes all six detectors plus Whisper in at build time, so the container **never phones home** — that's what makes air-gapped *real*, not aspirational. Audio is **hashed with SHA-256** for the audit trail and never stored in the clear. And by design, VoxShield *advises* the fraud flow — it never acts alone, and never locks a customer out on a model score. Every layer — channels, the API surface, the detection engine, the trust-and-audit layer, and the ops layer — is a boundary the bank's own security team can inspect. It scales like a web service, because that is exactly what it is: add replicas, capacity grows linearly, and a load-test harness ships in the repo so capacity is *measured* on the bank's hardware, not promised.\"")

chapter("Chapter 11 · The Market & Business — 'India's banking future is voice-first.'")
cue("Three cards — the channel banks can't abandon · fairness is the moat · beyond banking")
say("\"Why does this win commercially? Because **voice is the channel Indian banking cannot abandon** — IVR, phone banking, voice payments — reaching hundreds of millions across languages, literacy levels, even feature phones. And it's the channel cloning attacks target *first*. Any vendor can wrap an English model in an API; **evaluated fairness across ten Indian languages, measured under real telephony, is what a public-sector bank can actually procure** — and that's our moat.\"")
cue("Enterprise mode — 12 sectors · deployment modes · business model · Land-Expand-Scale")
note("Compress this block if short on time — name the shape, don't read every sector.")
say("\"The same engine extends far beyond the fraud desk — twelve sectors, one API: telecom anti-vishing, government helplines, healthcare, insurance, BPO, media, legal, defence. **Banking is live today; the rest are the addressable expansion, honestly labelled — not current deployments.** It deploys four ways — cloud SaaS, private cloud, on-prem, and quantised at the edge. And the business model is **land, expand, scale**: *land* in banking fraud desks — piloted with UCO Bank and Punjab & Sind Bank; *expand* the same drop-in API into adjacent sectors; and *scale* across all of India, toward all 22 scheduled languages, through marketplaces and white-label partners — recurring SaaS, metered usage, and multi-year government contracts, all off one engine.\"")
note("If asked about the security-architecture slide (TLS/JWT/OAuth/SOC/AES-256): be honest — several are on the roadmap, not shipped. On-prem, the audit trail, and the accessible UI are real today.")

chapter("Chapter 12 · Vision — 'The generators will improve. So will the shield.'")
cue("TRL ladder — 5 of 9 today · four honest phases")
say("\"And we're honest about where we are: **TRL-5 of 9 — a validated working system, today.** Shipped: the five-detector meta-fusion at 5.9% held-out error, fairness measured across ten languages, challenge-response liveness, the live call flagging at 3.0 seconds, and the on-prem image with its audit trail. Ahead of us are four *planned* phases: a **bank sandbox pilot** on recorded traffic; **hardening for India** with deeper Indic fine-tuning — already prototyped, catching 100% of our held-out Indic synthetic set; then **source attribution and adversarial-robust training** with a regulator-ready audit pack; and finally **national, multi-bank scale** toward all 22 languages. Everything past TRL-5 is labelled a plan, not a claim. The generators will keep improving — and the shield keeps learning right alongside them.\"")

chapter("Epilogue & Close — 'The same attack. Two endings.'")
cue("Without VoxShield vs With VoxShield · ₹8,47,000")
note("Slow right down. Come back to the customer from the Prologue. This is the emotional landing.")
say("\"Let me take you back to that morning call — the same attack, two endings. **Without VoxShield:** voice authentication passes, the transfer is approved, and eight lakh forty-seven thousand rupees becomes ninety-seven thousand. Fraud complete. Nothing left to stop it.")
say("**With VoxShield:** a decision is reached at **3.0 seconds** — fused risk 0.73, HIGH — reason codes PH, HF, PR — a liveness challenge is issued, and the clone *fails* it. The transaction is **paused, not blocked.** The customer is contacted, confirms their identity — and the eight lakh forty-seven thousand is **safe.** The customer never even knew an attack happened. The bank stopped it *before the money moved.*\"")
say("\"Voice will keep evolving — and so will VoxShield. **Detection. Fairness. Liveness.** One layered, honest defence for India's voice-first banking future. We are **Team DigiSeva**, from SRM Institute of Science and Technology. Thank you.\"")
note("All four presenters step forward together for questions.")

out="/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/VoxShield_Winning_Script.docx"
doc.save(out); print("SAVED",out)
