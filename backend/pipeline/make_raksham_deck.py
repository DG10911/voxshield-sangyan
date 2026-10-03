#!/usr/bin/env python3
"""VoxShield — RAKSHAM (IIT Delhi x Amazon) Round-1 submission (DARK theme).

One self-contained PDF, built to the official rubric:
  10 pitch slides  +  3 architecture slides  +  8 appendix slides (A1-A8).
Track 01 — Voice Cloning Fraud Detection (banking / payment workflows).

Design: dark, sophisticated, high-contrast financial-cybersecurity product.
Communication rule: every slide is understandable without narration.

Metrics policy = CONSERVATIVE / HONEST.
  GENUINE_FP_BEFORE toggles the genuine-Indic false-positive figure:
  "11.7%" = artifact-backed honest number (default);
  "36.3%" = the figure requested in the RAKSHAM brief template.
  All results carry: "Project evaluation; not independently validated by
  the hackathon organisers."
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, ListFlowable, ListItem,
                                PageBreak, KeepInFrame)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle, PolyLine
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = "VOXSHIELD_RAKSHAM_SUBMISSION.pdf"

# ------- metric toggle (see module docstring) -------
GENUINE_FP_BEFORE = "11.7%"      # honest, artifact-backed. Template asked for "36.3%".
GENUINE_FP_AFTER  = "6.3%"

# =====================  DARK PALETTE  =====================
BG      = colors.HexColor("#0A0E15")   # page background (near-black navy)
BG2     = colors.HexColor("#0E141E")
PANEL   = colors.HexColor("#141C28")   # card surface
PANEL2  = colors.HexColor("#1A2330")
LINE    = colors.HexColor("#28323F")   # hairlines
LINE2   = colors.HexColor("#3A4757")
INK     = colors.HexColor("#E7EDF5")   # primary text
MUT     = colors.HexColor("#93A1B3")   # muted text
FAINT   = colors.HexColor("#657286")
TEAL    = colors.HexColor("#2DD4BF")   # primary accent
CYAN    = colors.HexColor("#38BDF8")
BLUE    = colors.HexColor("#4C82F7")
LOW     = colors.HexColor("#22C55E")   # risk states
REVIEW  = colors.HexColor("#F5A524")
HIGH    = colors.HexColor("#EF4444")
PURPLE  = colors.HexColor("#A78BFA")
WHITE   = colors.white

PAGE = landscape(A4)                      # 297 x 210 mm
ML = MR = 15 * mm
MT = 26 * mm                              # header band room
MB = 12 * mm
CW = PAGE[0] - ML - MR
CH = PAGE[1] - MT - MB

ss = getSampleStyleSheet()
def st(name, **kw):
    kw.setdefault("parent", ss["Normal"])
    return ParagraphStyle(name, **kw)

LEAD  = st("lead", fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=INK, spaceAfter=6)
BODY  = st("b", fontName="Helvetica", fontSize=9.2, leading=12.6, textColor=INK, spaceAfter=4)
BODYM = st("bm", parent=BODY, textColor=MUT)
BODYJ = st("bj", parent=BODY, alignment=TA_JUSTIFY)
SUBH  = st("subh", fontName="Helvetica-Bold", fontSize=9.8, leading=12.5, textColor=TEAL, spaceBefore=3, spaceAfter=3)
BUL   = st("bu", parent=BODY, spaceAfter=2.5)
BULM  = st("bum", parent=BODYM, spaceAfter=2.5)
SMALL = st("sm", fontName="Helvetica", fontSize=7.7, leading=9.9, textColor=MUT, spaceAfter=2)
SMALLI= st("smi", parent=SMALL, fontName="Helvetica-Oblique", textColor=FAINT)
CELL  = st("c", fontName="Helvetica", fontSize=8.2, leading=10.6, textColor=INK)
CELLM = st("cm", parent=CELL, textColor=MUT)
CELLB = st("cbd", parent=CELL, fontName="Helvetica-Bold")
CELLH = st("ch", fontName="Helvetica-Bold", fontSize=8.2, leading=10.6, textColor=BG)
BIG   = st("big", fontName="Helvetica-Bold", fontSize=21, leading=23, textColor=TEAL, alignment=TA_CENTER)
BIGL  = st("bigl", fontName="Helvetica", fontSize=7.6, leading=9.6, textColor=MUT, alignment=TA_CENTER)

def P(t, s=BODY): return Paragraph(t, s)
def rule(c=LINE): return HRFlowable(width="100%", thickness=0.6, color=c, spaceBefore=3, spaceAfter=6)

def bullets(items, s=BUL, color=TEAL):
    return ListFlowable([ListItem(P(x, s), leftIndent=6, value="•") for x in items],
                        bulletType="bullet", leftIndent=12, spaceAfter=4, bulletColor=color)

def tbl(rows, widths, header=True, fs=8.2, headbg=TEAL, zebra=PANEL2):
    ch = st("ch_", parent=CELLH, fontSize=fs)
    cc = st("cc_", parent=CELL, fontSize=fs)
    data = [[Paragraph(str(c), ch if (header and i == 0) else cc) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    cmds = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
            ("BOX", (0, 0), (-1, -1), 0.6, LINE2),
            ("BACKGROUND", (0, 1), (-1, -1), PANEL)]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), headbg)]
        for r in range(1, len(rows)):
            if r % 2 == 0:
                cmds.append(("BACKGROUND", (0, r), (-1, r), zebra))
    t.setStyle(TableStyle(cmds))
    return t

def panel(flowables, bg=PANEL, border=LINE, pad=9, width=CW, accent=None):
    t = Table([[flowables]], colWidths=[width])
    style = [("BACKGROUND", (0, 0), (-1, -1), bg),
             ("BOX", (0, 0), (-1, -1), 0.8, border),
             ("LEFTPADDING", (0, 0), (-1, -1), pad), ("RIGHTPADDING", (0, 0), (-1, -1), pad),
             ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
             ("VALIGN", (0, 0), (-1, -1), "TOP")]
    if accent:
        style.append(("LINEBEFORE", (0, 0), (0, -1), 2.6, accent))
    t.setStyle(TableStyle(style))
    return t

def cols(cells, widths, valign="TOP", gap=7):
    t = Table([cells], colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), valign),
        ("LEFTPADDING", (0, 0), (0, -1), 0), ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ("LEFTPADDING", (1, 0), (-1, -1), gap), ("RIGHTPADDING", (0, 0), (-2, -1), gap),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t

def statcard(value, label, vc=TEAL, w=None):
    inner = [P(value, st("sv", parent=BIG, textColor=vc)), P(label, BIGL)]
    t = Table([[inner]], colWidths=[w or (CW - 3 * 8) / 4.0])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL), ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LINEABOVE", (0, 0), (-1, 0), 2.4, vc),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t

def statrow(cards, widths=None):
    n = len(cards)
    t = Table([cards], colWidths=widths or [CW / n] * n)
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t

def tag(text, color):
    """Small inline status pill as a 1-cell table."""
    t = Table([[Paragraph(text, st("tg", fontName="Helvetica-Bold", fontSize=6.8,
                                    textColor=BG, alignment=TA_CENTER))]],
              colWidths=[stringWidth(text, "Helvetica-Bold", 6.8) + 12])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
    return t

# ---------------- graphics primitives ----------------
def _fit(lines, w, fs, fn, pad=8):
    avail = w - 2 * pad
    while fs > 5.0 and not all(stringWidth(ln, fn, fs) <= avail for ln in lines):
        fs -= 0.3
    return fs

def gbox(g, x, y, w, h, lines, fill, stroke=None, tc=WHITE, fs=7.4, bold=True, sub=None):
    g.add(Rect(x, y, w, h, fillColor=fill, strokeColor=stroke or fill, strokeWidth=0.8, rx=3.5, ry=3.5))
    fn = "Helvetica-Bold" if bold else "Helvetica"
    fs = _fit(lines, w, fs, fn)
    lh = fs + 2.3
    cy = y + h / 2 + (len(lines) - 1) * lh / 2.0 - fs * 0.35
    for ln in lines:
        g.add(String(x + w / 2, cy, ln, fontName=fn, fontSize=fs, fillColor=tc, textAnchor="middle"))
        cy -= lh

def garrow(g, x1, y1, x2, y2, color=TEAL, w=1.3, dash=None):
    import math
    ln = Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=w)
    if dash:
        ln.strokeDashArray = dash
    g.add(ln)
    a = math.atan2(y2 - y1, x2 - x1); ah = 4.2
    g.add(Polygon([x2, y2,
                   x2 - ah * math.cos(a - 0.4), y2 - ah * math.sin(a - 0.4),
                   x2 - ah * math.cos(a + 0.4), y2 - ah * math.sin(a + 0.4)],
                  fillColor=color, strokeColor=color))

def glabel(g, x, y, text, color=MUT, fs=7.0, anchor="start", bold=False):
    g.add(String(x, y, text, fontName="Helvetica-Bold" if bold else "Helvetica",
                 fontSize=fs, fillColor=color, textAnchor=anchor))

# =====================  PAGE FRAME  =====================
META = []   # (kicker, title, mode) per page. mode: 'cover' | 'deck' | 'arch' | 'appx'

def paint_bg(canvas):
    canvas.setFillColor(BG); canvas.rect(0, 0, PAGE[0], PAGE[1], fill=1, stroke=0)

def frame(canvas, doc):
    canvas.saveState()
    paint_bg(canvas)
    idx = doc.page - 1
    kicker, title, mode = META[idx] if idx < len(META) else ("", "", "deck")
    if mode == "cover":
        # thin top rule only
        canvas.setFillColor(TEAL); canvas.rect(0, PAGE[1] - 2.2 * mm, PAGE[0], 2.2 * mm, fill=1, stroke=0)
    else:
        band = 18 * mm
        canvas.setFillColor(BG2); canvas.rect(0, PAGE[1] - band, PAGE[0], band, fill=1, stroke=0)
        canvas.setStrokeColor(LINE); canvas.setLineWidth(0.6)
        canvas.line(ML, PAGE[1] - band, PAGE[0] - MR, PAGE[1] - band)
        acc = {"deck": TEAL, "arch": CYAN, "appx": PURPLE}.get(mode, TEAL)
        canvas.setFillColor(acc); canvas.rect(ML, PAGE[1] - band, 26, 2.0 * mm, fill=1, stroke=0)
        canvas.setFillColor(acc); canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(ML, PAGE[1] - 8.6 * mm, kicker.upper())
        canvas.setFillColor(INK); canvas.setFont("Helvetica-Bold", 14.5)
        canvas.drawString(ML, PAGE[1] - 15.6 * mm, title)
        canvas.setFillColor(FAINT); canvas.setFont("Helvetica-Bold", 9)
        canvas.drawRightString(PAGE[0] - MR, PAGE[1] - 11.6 * mm, "VoxShield")
    # footer
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
    canvas.line(ML, 9 * mm, PAGE[0] - MR, 9 * mm)
    canvas.setFont("Helvetica", 7.1); canvas.setFillColor(FAINT)
    canvas.drawString(ML, 5.4 * mm,
                      "VoxShield · RAKSHAM (IIT Delhi × Amazon) · Round 1 · Challenge 01 — Voice Cloning Fraud Detection")
    canvas.drawRightString(PAGE[0] - MR, 5.4 * mm, f"{doc.page}")
    canvas.restoreState()

E = []
def slide(kicker, title, body, mode="deck", vmid=False):
    META.append((kicker, title, mode))
    va = "MIDDLE" if vmid else "TOP"
    E.append(KeepInFrame(CW, CH, body, mode="shrink", hAlign="LEFT", vAlign=va))
    E.append(PageBreak())

# =====================================================================
#  REUSABLE DRAWINGS
# =====================================================================
def threat_waveform(width, h=98):
    """Stylized call-waveform morphing through the attack stages (Slide 1 hero)."""
    import math
    d = Drawing(width, h); d.hAlign = "CENTER"
    wy = h - 40; amp0 = 10.0
    segs = [
        ("TRUSTED VOICE", CYAN, 0.9, "natural"),
        ("SYNTHETIC CLONE", TEAL, 0.85, "regular"),
        ("SOCIAL ENGINEERING", REVIEW, 1.0, "rising"),
        ("PAYMENT ACTION", colors.HexColor("#E8833A"), 1.15, "spike"),
        ("FRAUD", HIGH, 1.4, "jagged"),
    ]
    n = len(segs); seg_w = width / n
    d.add(Line(0, wy, width, wy, strokeColor=LINE, strokeWidth=0.5))
    for i, (label, col, af, kind) in enumerate(segs):
        x0 = i * seg_w; steps = 64; pts = []
        for s in range(steps + 1):
            t = s / steps; x = x0 + t * seg_w
            if kind == "regular":
                y = wy + af * amp0 * math.sin(t * 2 * math.pi * 5)
            elif kind == "natural":
                y = wy + af * amp0 * (0.6 * math.sin(t * 2 * math.pi * 6) + 0.4 * math.sin(t * 2 * math.pi * 13 + 1))
            elif kind == "rising":
                y = wy + af * amp0 * (0.5 + t) * math.sin(t * 2 * math.pi * 7)
            elif kind == "spike":
                env = 0.4 + 1.5 * math.exp(-((t - 0.6) ** 2) / 0.02)
                y = wy + af * amp0 * env * math.sin(t * 2 * math.pi * 9)
            else:
                y = wy + af * amp0 * math.sin(t * 2 * math.pi * 11) * (0.7 + 0.5 * math.sin(t * 2 * math.pi * 23))
            pts += [x, y]
        d.add(PolyLine(pts, strokeColor=col, strokeWidth=1.7))
        d.add(Circle(x0 + (2.5 if i == 0 else 0), wy, 2.6, fillColor=col, strokeColor=col))
        lx = x0 + seg_w / 2
        glabel(d, lx, 10, label, color=col, fs=7.0, anchor="middle", bold=True)
        if i < n - 1:
            garrow(d, x0 + seg_w - 14, wy - 20, x0 + seg_w + 6, wy - 20, color=LINE2, w=0.9)
    return d

def hchain(width, items, h=42, bh=28, fs=8.5, arrow_color=LINE2):
    """Horizontal labelled flow: items = [(label, color), ...]."""
    d = Drawing(width, h)
    n = len(items); gap = 14
    bw = (width - (n - 1) * gap) / n
    yb = (h - bh) / 2.0; xs = []
    for i, (label, col) in enumerate(items):
        x = i * (bw + gap); xs.append(x)
        lines = label if isinstance(label, (list, tuple)) else [label]
        gbox(d, x, yb, bw, bh, lines, PANEL, stroke=col, tc=INK, fs=fs)
        d.add(Rect(x, yb + bh - 3, bw, 3, fillColor=col, strokeColor=col))
        if i:
            garrow(d, xs[i - 1] + bw, yb + bh / 2, x, yb + bh / 2, color=arrow_color, w=1.2)
    return d

def risk_ladder(width=CW, h=112):
    """LOW / REVIEW / HIGH state ladder with actions."""
    d = Drawing(width, h)
    states = [
        (LOW,    "LOW RISK", ["Weak / no synthetic evidence"], "Continue normally", "No added friction"),
        (REVIEW, "REVIEW",   ["Uncertain or partial evidence"], "Step-up verification", "Callback / 2nd channel"),
        (HIGH,   "HIGH RISK", ["Strong multi-signal evidence"], "Authorised human review", "NO auto-block / accuse"),
    ]
    n = len(states); gap = 16
    bw = (width - (n - 1) * gap) / n
    for i, (c, name, ev, act, note) in enumerate(states):
        x = i * (bw + gap)
        d.add(Rect(x, 0, bw, h, fillColor=PANEL, strokeColor=c, strokeWidth=1.1, rx=5, ry=5))
        d.add(Rect(x, h - 7, bw, 7, fillColor=c, strokeColor=c))
        d.add(Circle(x + 15, h - 24, 5, fillColor=c, strokeColor=c))
        glabel(d, x + 26, h - 27, name, color=INK, fs=10.5, bold=True)
        glabel(d, x + 12, h - 46, ev[0], color=MUT, fs=7.6)
        d.add(Line(x + 12, h - 54, x + bw - 12, h - 54, strokeColor=LINE, strokeWidth=0.5))
        glabel(d, x + 12, h - 70, "ACTION", color=FAINT, fs=6.4, bold=True)
        glabel(d, x + 12, h - 82, act, color=c, fs=8.6, bold=True)
        glabel(d, x + 12, h - 97, note, color=MUT, fs=7.2)
        if i < n - 1:
            garrow(d, x + bw + 2, h / 2, x + bw + gap - 2, h / 2, color=LINE2, w=1.1)
    return d

def evidence_panel(width=250, h=190):
    """Product UI mockup: VoxShield evidence card (HIGH — review required)."""
    d = Drawing(width, h)
    d.add(Rect(0, 0, width, h, fillColor=PANEL, strokeColor=LINE2, strokeWidth=1.0, rx=7, ry=7))
    # title bar
    d.add(Rect(0, h - 22, width, 22, fillColor=PANEL2, strokeColor=PANEL2))
    d.add(Circle(14, h - 11, 4.5, fillColor=TEAL, strokeColor=TEAL))
    glabel(d, 24, h - 14.5, "VoxShield  ·  Voice Authenticity Evidence", color=INK, fs=8.6, bold=True)
    glabel(d, width - 8, h - 14.5, "UI EXAMPLE", color=FAINT, fs=6.6, anchor="end", bold=True)
    # risk banner
    by = h - 52
    d.add(Rect(10, by, width - 20, 24, fillColor=colors.HexColor("#2A1518"),
               strokeColor=HIGH, strokeWidth=1.0, rx=4, ry=4))
    d.add(Circle(24, by + 12, 5, fillColor=HIGH, strokeColor=HIGH))
    glabel(d, 36, by + 13.5, "RISK STATE:  HIGH", color=HIGH, fs=10.5, bold=True)
    glabel(d, 36, by + 4, "Review required — evidence indicates elevated voice-clone risk", color=MUT, fs=6.6)
    glabel(d, width - 16, by + 8, "91%", color=HIGH, fs=13, anchor="end", bold=True)
    # evidence checklist
    ev = ["Multiple detector agreement (4 / 5)",
          "Synthetic spectral characteristics",
          "Abnormal F0 / prosody dynamics",
          "Vocoder-like phase regularity",
          "Indic-TTS synthesis signature"]
    ey = by - 14
    for e in ev:
        d.add(Polygon([12, ey - 2, 15.5, ey - 5.5, 21, ey + 3], fillColor=None,
                      strokeColor=TEAL, strokeWidth=1.4))
        glabel(d, 26, ey - 4, e, color=INK, fs=7.6)
        ey -= 15
    # footer note + action
    d.add(Line(10, ey - 1, width - 10, ey - 1, strokeColor=LINE, strokeWidth=0.5))
    glabel(d, 12, ey - 12, "A risk signal — not proof of fraud.", color=REVIEW, fs=7.2, bold=True)
    d.add(Rect(10, ey - 33, width - 20, 15, fillColor=TEAL, strokeColor=TEAL, rx=3, ry=3))
    glabel(d, width / 2, ey - 28, "→  Step-up verification / authorised fraud review",
           color=BG, fs=7.6, anchor="middle", bold=True)
    return d

def pipeline_drawing(width=CW, h=92):
    """8kHz -> VAD -> stream -> 5 detectors -> fusion -> routing -> evidence."""
    d = Drawing(width, h)
    row = [
        (CYAN,  ["8 kHz G.711", "μ-law call"]),
        (BLUE,  ["VAD +", "preprocess"]),
        (BLUE,  ["Stream", "3 s / 1 s hop"]),
        (PURPLE,["5 detectors", "(see below)"]),
        (TEAL,  ["Meta-fusion", "stacker"]),
        (TEAL,  ["Indic /", "tel. router"]),
        (LOW,   ["Evidence +", "risk state"]),
    ]
    n = len(row); gap = 12
    bw = (width - (n - 1) * gap) / n
    yb = h - 42; bh = 30
    xs = []
    for i, (c, lns) in enumerate(row):
        x = i * (bw + gap); xs.append(x)
        gbox(d, x, yb, bw, bh, lns, PANEL, stroke=c, tc=INK, fs=7.2)
        d.add(Rect(x, yb + bh - 3.5, bw, 3.5, fillColor=c, strokeColor=c))
        if i:
            garrow(d, xs[i - 1] + bw, yb + bh / 2, x, yb + bh / 2, color=LINE2, w=1.1)
    # detector chips under the "5 detectors" box
    det = ["Acoustic DSP", "wav2vec2", "XLS-R-53", "DistilHuBERT", "LFCC+CQCC"]
    dx = 0; dy = yb - 30; dwid = width
    cw = (dwid) / len(det)
    d.add(Line(xs[3] + bw / 2, yb, xs[3] + bw / 2, dy + 14, strokeColor=LINE2, strokeWidth=0.9))
    for i, dn in enumerate(det):
        x = i * cw
        fs = _fit([dn], cw - 4, 6.8, "Helvetica")
        d.add(Rect(x, dy, cw - 6, 13, fillColor=PANEL2, strokeColor=LINE, rx=2.5, ry=2.5))
        glabel(d, x + (cw - 6) / 2, dy + 4, dn, color=MUT, fs=fs, anchor="middle")
    return d

def detection_hero(width=CW, h=125 * mm):
    """Slide 5 hero: input → 5-detector stack (+89-D bank) → fusion → router →
    calibration → risk engine → LOW/REVIEW/HIGH branch. No crossing arrows."""
    d = Drawing(width, h)
    yc = h * 0.5                       # main spine centre (content vertically centred)
    # ---- far-left input stack ----
    iw = 86; ih = 22; igap = 10
    inp = [("8 kHz G.711 µ-law", CYAN), ("VAD + preprocess", BLUE), ("3 s window / 1 s hop", BLUE)]
    ix = 0
    iy0 = yc + ih + igap
    for j, (lab, col) in enumerate(inp):
        iy = iy0 - j * (ih + igap)
        gbox(d, ix, iy, iw, ih, [lab], PANEL, stroke=col, tc=INK, fs=7.4)
        d.add(Rect(ix, iy, 2.4, ih, fillColor=col, strokeColor=col))
        if j:
            garrow(d, ix + iw / 2, iy + ih + igap, ix + iw / 2, iy + ih, color=LINE2, w=0.9)
    # ---- detector panel ----
    dx = ix + iw + 22
    dpw = 138
    det = [("Acoustic DSP", CYAN), ("wav2vec2", BLUE), ("XLS-R-53", TEAL),
           ("DistilHuBERT", PURPLE), ("LFCC + CQCC", colors.HexColor("#E8833A"))]
    rowh = 15; head = 16; fb_h = 30
    dph = head + len(det) * rowh + 6
    dpy = yc + ih / 2 - dph / 2 + 6
    d.add(Rect(dx, dpy, dpw, dph, fillColor=PANEL, strokeColor=LINE2, strokeWidth=1.0, rx=4, ry=4))
    d.add(String(dx + dpw / 2, dpy + dph - 11, "FIVE DETECTOR FAMILIES",
                 fontName="Helvetica-Bold", fontSize=7.0, fillColor=TEAL, textAnchor="middle"))
    for k, (dn, col) in enumerate(det):
        ry = dpy + dph - head - (k + 1) * rowh + 3
        d.add(Rect(dx + 6, ry, dpw - 12, rowh - 3, fillColor=PANEL2, strokeColor=LINE, rx=2, ry=2))
        d.add(Rect(dx + 6, ry, 2.2, rowh - 3, fillColor=col, strokeColor=col))
        d.add(String(dx + 14, ry + 3.2, dn, fontName="Helvetica", fontSize=7.2, fillColor=INK))
    # 89-D feature bank strip beneath detectors
    fby = dpy - fb_h - 8
    d.add(Rect(dx, fby, dpw, fb_h, fillColor=BG2, strokeColor=LINE, strokeWidth=0.8, rx=4, ry=4))
    d.add(String(dx + dpw / 2, fby + fb_h - 11, "89-D FEATURE BANK", fontName="Helvetica-Bold",
                 fontSize=6.6, fillColor=MUT, textAnchor="middle"))
    d.add(String(dx + dpw / 2, fby + 9, "LFCC · CQCC · group-delay phase", fontName="Helvetica",
                 fontSize=6.2, fillColor=FAINT, textAnchor="middle"))
    d.add(String(dx + dpw / 2, fby + 2, "F0 · jitter · shimmer · telephony-band cues", fontName="Helvetica",
                 fontSize=6.2, fillColor=FAINT, textAnchor="middle"))
    garrow(d, dx, fby + fb_h / 2, dx, dpy, color=LINE, w=0.8)  # bank feeds detectors
    garrow(d, ix + iw, yc + ih / 2, dx, dpy + dph / 2, color=LINE2, w=1.1)  # input->detectors
    # ---- spine nodes: fusion, router, calibration, risk ----
    sx = dx + dpw + 20
    spine = [("Meta-fusion", TEAL, ["Meta-fusion", "stacker"]),
             ("Router", TEAL, ["Indic / telephony", "router"]),
             ("Calibration", TEAL, ["Platt", "calibration"]),
             ("Risk", LOW, ["Evidence +", "risk engine"])]
    snw = 80; snh = 30; sgap = 10
    prev_r = dx + dpw; sxpos = []
    for i, (_, col, lns) in enumerate(spine):
        x = sx + i * (snw + sgap); sxpos.append(x)
        gbox(d, x, yc, snw, snh, lns, PANEL, stroke=col, tc=INK, fs=7.4)
        d.add(Rect(x, yc + snh - 3, snw, 3, fillColor=col, strokeColor=col))
        src_y = (dpy + dph / 2) if i == 0 else (yc + snh / 2)
        garrow(d, prev_r, src_y if i == 0 else yc + snh / 2, x, yc + snh / 2, color=LINE2, w=1.2)
        prev_r = x + snw
    # ---- trust boundary around model zone ----
    bx0 = dx - 8; bx1 = prev_r + 8
    by0 = fby - 6; by1 = dpy + dph + 20
    br = Rect(bx0, by0, bx1 - bx0, by1 - by0, fillColor=None, strokeColor=LINE2, strokeWidth=0.8)
    br.strokeDashArray = [3, 3]; d.add(br)
    d.add(String(bx0 + 4, by1 - 9, "ON-PREM MODEL ZONE — audio not exported",
                 fontName="Helvetica-Bold", fontSize=6.2, fillColor=FAINT))
    # ---- risk branch (far right, stacked) ----
    ox = prev_r + 18; ow = 116; oh = 24; ogap = 10
    outs = [("LOW → Continue", LOW), ("REVIEW → Step-up", REVIEW),
            ("HIGH → Human review", HIGH)]
    oy0 = yc + snh / 2 + (oh + ogap)
    risk_src = (prev_r, yc + snh / 2)
    for j, (lab, col) in enumerate(outs):
        oy = oy0 - j * (oh + ogap)
        gbox(d, ox, oy, ow, oh, [lab], PANEL, stroke=col, tc=INK, fs=7.6)
        d.add(Rect(ox, oy, 3, oh, fillColor=col, strokeColor=col))
        garrow(d, risk_src[0], risk_src[1], ox, oy + oh / 2, color=col, w=1.0)
    return d

def architecture_drawing(width=CW, h=138 * mm):
    """End-to-end system across 3 trust zones with boundaries + evidence store."""
    d = Drawing(width, h)
    lane_h = h / 3.0
    lanes = [
        ("ANALYST / FRAUD-OPS ZONE  —  governed evidence & human review", 0.0, colors.HexColor("#171016")),
        ("VOXSHIELD MODEL ZONE  —  air-gapped, no audio egress", 1.0, colors.HexColor("#0F1A18")),
        ("BANK / TELCO CAPTURE ZONE  —  authorised audio, on-prem", 2.0, colors.HexColor("#0E1622")),
    ]
    accents = {0: HIGH, 1: TEAL, 2: CYAN}
    for i, (label, k, bg) in enumerate(lanes):
        y = k * lane_h
        d.add(Rect(0, y, width, lane_h - 5, fillColor=bg, strokeColor=LINE, strokeWidth=0.7))
        d.add(Rect(0, y, 3, lane_h - 5, fillColor=accents[k if k in accents else 0], strokeColor=None))
        glabel(d, 9, y + lane_h - 15, label, color=MUT, fs=7.4, bold=True)
    bh = 28
    def rowy(k): return k * lane_h + (lane_h - 5) / 2 - bh / 2 - 5

    # top zone (k=2): capture
    yc = rowy(2)
    cap = [(CYAN, ["Banking / payment", "workflow"]),
           (CYAN, ["Consent / policy", "gate + authZ"]),
           (BLUE, ["Secure ingestion", "VAD + preprocess"]),
           (BLUE, ["Streaming", "3 s / 1 s hop"]),
           (NAVY_OK := PANEL, ["Provenance log", "hash · ts · route"])]
    n = len(cap); gap = 22
    bw = (width - 16 - (n - 1) * gap) / n
    xs = []
    for i, (c, lns) in enumerate(cap):
        x = 8 + i * (bw + gap); xs.append(x)
        gbox(d, x, yc, bw, bh, lns, PANEL, stroke=c, tc=INK, fs=7.0)
        d.add(Rect(x, yc + bh - 3, bw, 3, fillColor=c, strokeColor=c))
        if i:
            garrow(d, xs[i - 1] + bw, yc + bh / 2, x, yc + bh / 2, color=LINE2, w=1.0)

    # middle zone (k=1): detectors group -> fusion -> router -> risk engine
    ym = rowy(1)
    det = ["Acoustic DSP", "wav2vec2", "XLS-R-53", "DistilHuBERT", "LFCC + CQCC"]
    dgw = 108; dh = 70; dy = ym + bh / 2 - dh / 2
    d.add(Rect(8, dy, dgw, dh, fillColor=PANEL, strokeColor=PURPLE, strokeWidth=1.0, rx=4, ry=4))
    glabel(d, 8 + dgw / 2, dy + dh - 12, "5 complementary detectors", color=PURPLE, fs=6.8, anchor="middle", bold=True)
    for i, dn in enumerate(det):
        glabel(d, 8 + dgw / 2, dy + dh - 25 - i * 10, dn, color=INK, fs=7.0, anchor="middle")
    mids = [(TEAL, ["Meta-fusion", "layer"]),
            (TEAL, ["Indic / telephony", "router"]),
            (LOW,  ["Evidence + risk", "engine"])]
    mgap = 26; start = 8 + dgw + mgap
    mbw = (width - start - 8 - (len(mids) - 1) * mgap) / len(mids)
    prev = 8 + dgw; xm = []
    for i, (c, lns) in enumerate(mids):
        x = start + i * (mbw + mgap); xm.append(x)
        gbox(d, x, ym, mbw, bh, lns, PANEL, stroke=c, tc=INK, fs=7.4)
        d.add(Rect(x, ym + bh - 3, mbw, 3, fillColor=c, strokeColor=c))
        garrow(d, prev, ym + bh / 2, x, ym + bh / 2, color=LINE2, w=1.0)
        prev = x + mbw
    garrow(d, 8 + bw / 2, yc, 8 + dgw / 2, dy + dh, color=LINE2, w=1.0)  # capture->detectors

    # bottom zone (k=0): risk states -> actions -> evidence store / audit
    yb = rowy(0)
    outs = [(LOW,   ["LOW", "→ continue"]),
            (REVIEW,["REVIEW", "→ step-up verify"]),
            (HIGH,  ["HIGH", "→ human review"]),
            (PANEL, ["Encrypted evidence", "store + audit log"]),
            (BLUE,  ["Authorised action", "(human-approved)"])]
    n = len(outs); bgap = 18
    obw = (width - 16 - (n - 1) * bgap) / n
    xo = []
    for i, (c, lns) in enumerate(outs):
        x = 8 + i * (obw + bgap); xo.append(x)
        stroke = c if c != PANEL else LINE2
        gbox(d, x, yb, obw, bh, lns, PANEL, stroke=stroke, tc=INK, fs=7.0)
        d.add(Rect(x, yb + bh - 3, obw, 3, fillColor=stroke, strokeColor=stroke))
    # risk engine -> the three states
    for i in range(3):
        garrow(d, xm[2] + mbw / 2, ym, xo[i] + obw / 2, yb + bh, color=LINE2, w=0.9)
    for i in (2, 3):
        garrow(d, xo[i] + obw, yb + bh / 2, xo[i + 1], yb + bh / 2, color=LINE2, w=1.0)
    # dashed trust-boundary separators already implied by lanes; add labels
    glabel(d, width - 6, 1.0 * lane_h + 4, "▲ trust boundary — audio never leaves model zone",
           color=FAINT, fs=6.4, anchor="end")
    glabel(d, width - 6, 2.0 * lane_h + 4, "▲ data boundary — authorised capture only",
           color=FAINT, fs=6.4, anchor="end")
    return d

# =====================================================================
#  ============  SLIDE 1 — THE THREAT (cover/hero)  ============
# =====================================================================
c = []
c.append(Spacer(1, 3 * mm))
c.append(P("RAKSHAM · IIT DELHI × AMAZON · ROUND 1 · CHALLENGE 01 — VOICE CLONING FRAUD DETECTION",
           st("k", fontName="Helvetica-Bold", fontSize=9, textColor=TEAL, alignment=TA_CENTER, spaceAfter=10)))
c.append(P("The voice you trust can now be synthetic.",
           st("t1", fontName="Helvetica-Bold", fontSize=30, leading=34, textColor=INK,
              alignment=TA_CENTER, spaceAfter=6)))
c.append(P("AI voice cloning turns a trusted financial conversation into an attack surface.",
           st("t1s", fontName="Helvetica", fontSize=13, leading=17, textColor=MUT,
              alignment=TA_CENTER, spaceAfter=12)))
c.append(threat_waveform(CW * 0.9, h=98))
c.append(Spacer(1, 3))
c.append(P("A cloned voice — built from <b>3–10 s</b> of public audio, in an Indian language, over an "
           "ordinary phone line — manufactures urgency and turns a trusted call into a payment, a "
           "beneficiary change, or a disclosed OTP.",
           st("wcap", fontName="Helvetica", fontSize=9.5, leading=13, textColor=MUT,
              alignment=TA_CENTER, spaceAfter=2)))
c.append(Spacer(1, 8))
c.append(P("<b>VoxShield</b> — Real-Time Voice-Clone Fraud Detection for Safer Banking &amp; Payment Workflows",
           st("vs", fontName="Helvetica-Bold", fontSize=15, textColor=TEAL, alignment=TA_CENTER, spaceAfter=4)))
c.append(P("A privacy-conscious detection layer that scores suspicious voice interactions in real time and "
           "returns an <b>evidence-backed risk signal</b> for human or policy review. "
           "<font color='#2DD4BF'><b>It does not accuse, block, or deny a transaction from a model score alone.</b></font>",
           st("vs2", fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=INK,
              alignment=TA_CENTER, spaceAfter=10)))
c.append(statrow([
    statcard("5.9%", "EER · held-out in-the-wild"),
    statcard("42→82%", "Indic deepfake recall"),
    statcard("&lt;1 s", "verdict latency / GPU"),
    statcard("On-prem", "air-gapped · no egress", vc=LOW),
]))
c.append(Spacer(1, 6))
c.append(P("Team DigiSeva · Track 01 · Working prototype (TRL-5). Project evaluation; not independently "
           "validated by the hackathon organisers.", st("cf", parent=SMALLI, alignment=TA_CENTER)))
slide("", "", c, mode="cover", vmid=True)

# =====================================================================
#  ============  SLIDE 2 — USER + HARMFUL MOMENT  ============
# =====================================================================
s = []
s.append(P("The <b>primary user is a bank / NBFC fraud &amp; trust-and-safety operations analyst</b> — and "
           "behind them, every Indian phone customer targeted by a cloned voice.", LEAD))
s.append(cols([
    [P("The harmful moment (BEFORE)", st("h2", parent=SUBH, textColor=HIGH)),
     bullets([
        "Attacker clones a trusted person's voice; calls during a live banking / payment interaction.",
        "Customer trusts the familiar voice → social engineering → approves a transfer, changes a "
        "beneficiary, or discloses an OTP.",
        "Fraud completes in seconds. Recovery is slow and rarely successful.",
     ], color=HIGH)],
    [P("Who sees the signal — and what they may do", SUBH),
     tbl([
        ["Question", "Answer"],
        ["WHO receives it", "Authorised fraud-ops analyst"],
        ["WHAT they see", "Risk state + evidence + confidence"],
        ["WHEN", "Within the call's first seconds (streaming)"],
        ["ACTION allowed", "Step-up verify / escalate / review"],
        ["NOT allowed", "Auto-block / accuse from a score alone"],
     ], [30 * mm, 74 * mm], fs=7.9)],
], [CW * 0.5, CW * 0.5]))
s.append(Spacer(1, 6))
s.append(P("The current journey — today, with no defense", st("cj", parent=SUBH, textColor=HIGH)))
s.append(hchain(CW, [
    ("Cloned-voice call", HIGH), ("Familiar-voice trust", HIGH), ("Manufactured urgency", HIGH),
    ("Customer approves", HIGH), ("Irreversible fraud loss", HIGH)], h=40, fs=8.2))
s.append(Spacer(1, 6))
s.append(panel([P("<b>The India-specific deployment challenge.</b> Much commercial voice-deepfake "
                  "detection is cloud/API-oriented and English-centric, which can create deployment and "
                  "data-governance constraints for sensitive Indian telephony workflows (aligned with "
                  "DPDP and RBI data-localisation expectations). VoxShield is designed for on-prem, "
                  "Indian-language, phone-quality audio — and CERT-In has issued deepfake advisories as "
                  "the threat grows.", BODYJ)], accent=CYAN))
slide("The user & the harm", "A trusted voice, weaponised inside a live financial interaction", s)

# =====================================================================
#  ============  SLIDE 3 — THE PRODUCT  ============
# =====================================================================
s = []
s.append(P("<b>VoxShield: detect the signal before trust becomes loss.</b>  The product turns a blind "
           "judgment call into an evidence-backed, human-governed decision — "
           "<font color='#2DD4BF'><b>detection ≠ accusation</b></font>.", LEAD))
s.append(cols([
    [P("Product flow (AFTER)", st("h3", parent=SUBH, textColor=LOW)),
     bullets([
        "<b>Voice</b> → controlled, on-prem analysis of the live call.",
        "<b>Detection</b> → five detectors produce independent evidence.",
        "<b>Evidence + risk state</b> → LOW / REVIEW / HIGH, explained.",
        "<b>Verification</b> → REVIEW triggers step-up (callback / 2nd channel).",
        "<b>Human review</b> → HIGH escalates to authorised fraud-ops.",
        "<b>Safe action</b> → a person decides; the model never does.",
     ], color=LOW),
     Spacer(1, 4),
     P("The system communicates <i>“evidence indicates elevated voice-clone risk”</i> — never "
       "<i>“this person is a fraudster.”</i>", SMALL)],
    [P("What the analyst actually sees", SUBH),
     evidence_panel(width=CW * 0.46 - 6, h=192),
     Spacer(1, 3),
     P("Illustrative analyst console — the 91% is an example risk signal for a single call, not a "
       "benchmark result.", SMALLI)],
], [CW * 0.5, CW * 0.5]))
slide("The product", "Detect the signal before trust becomes loss — detection ≠ accusation", s)

# =====================================================================
#  ============  SLIDE 4 — WHY DIFFERENT (six pillars)  ============
# =====================================================================
s = []
s.append(P("Not “another deepfake detector.” VoxShield converts voice-clone detection into a "
           "<b>safe financial-risk workflow</b> — six pillars competitors and generic builds leave open.",
           LEAD))
pill = [
    ("Telephony-first", "Trained for 8 kHz G.711 phone audio, not studio clips — measured codec cost.", CYAN),
    ("Indic-aware", "XLS-R-53 backbone + Indic routing across 10 Indian languages.", TEAL),
    ("Streaming", "3 s window / 1 s hop → a verdict within a call's first seconds.", BLUE),
    ("Multi-detector fusion", "Five detector families + learned meta-fusion; no single point of evasion.", PURPLE),
    ("Explainable evidence", "Per-signal reason codes, not a bare score — legible to a fraud analyst.", TEAL),
    ("Safe escalation", "LOW/REVIEW/HIGH, human-in-the-loop, never auto-blocks. Fails safe.", LOW),
]
def pill_card(title, body, c):
    inner = [P(title, st("pt", fontName="Helvetica-Bold", fontSize=9.6, textColor=c, spaceAfter=2)),
             P(body, st("pb", fontName="Helvetica", fontSize=8.0, leading=10.6, textColor=MUT))]
    t = Table([[inner]], colWidths=[(CW - 2 * 10) / 3.0])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PANEL), ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, c),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t
rows = []
for r in range(0, 6, 3):
    rowcells = [pill_card(*pill[r + k]) for k in range(3)]
    t = Table([rowcells], colWidths=[CW / 3.0] * 3)
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    rows.append(t)
s += rows
s.append(Spacer(1, 6))
s.append(panel([P("<font color='#38BDF8'><b>Phone audio</b></font>  +  "
                  "<font color='#2DD4BF'><b>Indic language</b></font>  +  "
                  "<font color='#A78BFA'><b>Multi-model evidence</b></font>  +  "
                  "<font color='#4C82F7'><b>Financial workflow</b></font>  +  "
                  "<font color='#22C55E'><b>Human governance</b></font>"
                  "  <font color='#93A1B3'>=</font>  "
                  "<font color='#2DD4BF'><b>VOXSHIELD</b></font>",
                  st("eq", fontName="Helvetica", fontSize=11.5, leading=15, textColor=INK,
                     alignment=TA_CENTER))], bg=PANEL2, border=LINE2))
slide("Why VoxShield", "Six pillars — a safe financial-risk workflow, not a generic detector", s)

# =====================================================================
#  ============  SLIDE 5 — DETECTION ENGINE  ============
# =====================================================================
s = []
s.append(P("Five complementary detectors over a shared 89-D feature bank → <b>learned meta-fusion</b> "
           "(not a naive average) → Indic/telephony routing → calibration → a calibrated risk state. "
           "Multiple signals, one governed decision.", LEAD))
s.append(Spacer(1, 4))
s.append(detection_hero(width=CW, h=104 * mm))
s.append(Spacer(1, 4))
s.append(P("Under 8 kHz telephony, information above the Nyquist limit is not available; the system uses "
           "cues present within the available telephony band. Routing priority is Indic → telephony → "
           "general, fail-safe.  <b>Detection ≠ accusation.</b>", SMALL))
slide("Detection engine", "From 8 kHz telephony to a calibrated, explainable risk signal", s)

# =====================================================================
#  ============  SLIDE 6 — PROOF  ============
# =====================================================================
s = []
s.append(P("Measured on project corpora under disjoint splits, reported with scope. In-corpus and "
           "cross-dataset figures are never conflated.", LEAD))
s.append(statrow([
    statcard("5.9%", "Fusion EER · held-out in-the-wild (800 clips)"),
    statcard("42 → 82%", "Indic deepfake recall (MMS-TTS)"),
    statcard(f"{GENUINE_FP_BEFORE} → {GENUINE_FP_AFTER}", "Genuine-Indic false positives (channel-aware)", vc=LOW),
]))
s.append(Spacer(1, 5))
s.append(cols([
    [P("Methodology", SUBH),
     bullets([
        "Speaker-disjoint; cross-generator holdout (train on some cloners, test a held-out cloner); "
        "cross-dataset OOD (MLAAD); per-language & codec-degraded breakdowns.",
        "Fusion beats the best single detector (16.0% EER) and a naive average (19.1%) — the honesty check.",
        "ROC-AUC 0.983; calibration ECE 0.044. G.711 codec cost ≈ 1.6 pts cross-dataset.",
     ])],
    [P("Caveats (stated, not hidden)", st("cav", parent=SUBH, textColor=REVIEW)),
     bullets([
        "EER is not accuracy; Indic recall is not overall recall.",
        "In-the-wild phone figures are in-domain-optimistic; the robust cross-dataset finding is the "
        "≈1.6-pt codec cost.",
        "Multi-cloner Indic cross-generator numbers are in progress.",
     ], color=REVIEW)],
], [CW * 0.55, CW * 0.45]))
s.append(P("Project evaluation; not independently validated by the hackathon organisers. Axes never "
           "truncated to exaggerate.", SMALLI))
slide("Proof", "Measured, scoped, and honestly bounded — no hero numbers", s)

# =====================================================================
#  ============  SLIDE 7 — TRUST BY DESIGN (fail safely)  ============
# =====================================================================
s = []
s.append(P("<b>When AI is wrong, the product must fail safely.</b> A wrong high-impact action on a genuine "
           "customer is itself a harm — so the model's output is <b>evidence for a decision, never the "
           "decision</b>.", LEAD))
s.append(risk_ladder(width=CW, h=112))
s.append(Spacer(1, 4))
s.append(cols([
    [P("Trust guarantees", SUBH),
     bullets([
        "<b>No automatic blocking or accusation</b> from a score alone.",
        "<b>Privacy by design:</b> raw audio scored in the authorised boundary; least-data logging.",
        "<b>Auditability:</b> tamper-evident log of every verdict and action.",
     ])],
    [P("", SUBH),
     bullets([
        "<b>Explainability:</b> reason codes, not a bare score.",
        "<b>Fairness:</b> genuine-customer false-alarm rate tracked per language.",
        "<b>Misuse resistance:</b> access-controlled evidence; no fraudster look-up tool.",
     ])],
], [CW * 0.5, CW * 0.5]))
slide("Trust by design", "When AI is wrong, the product must fail safely", s)

# =====================================================================
#  ============  SLIDE 8 — FINANCIAL WORKFLOW  ============
# =====================================================================
s = []
s.append(P("VoxShield is a <b>risk-event source</b> inside the existing fraud stack — it emits signals; "
           "the bank's people and policies act on them.", LEAD))
flow = Drawing(CW, 58)
steps = [(CYAN, ["Call /", "audio stream"]), (TEAL, ["VoxShield", "API / SDK"]),
         (LOW, ["Risk event +", "evidence"]), (BLUE, ["Fraud platform /", "case mgmt"]),
         (REVIEW, ["Analyst", "review"]), (PURPLE, ["Authorised", "action"])]
n = len(steps); gap = 16; bw = (CW - (n - 1) * gap) / n; xs = []
for i, (col, lns) in enumerate(steps):
    x = i * (bw + gap); xs.append(x)
    gbox(flow, x, 14, bw, 30, lns, PANEL, stroke=col, tc=INK, fs=7.6)
    flow.add(Rect(x, 14 + 30 - 3, bw, 3, fillColor=col, strokeColor=col))
    if i:
        garrow(flow, xs[i - 1] + bw, 29, x, 29, color=LINE2, w=1.1)
s.append(flow)
s.append(Spacer(1, 4))
s.append(cols([
    [P("Risk-event payload (outputs)", SUBH),
     P("risk_state · evidence[] · confidence · model_version · language · latency_ms · timestamp · "
       "audit_id — a structured event, easy to route into an existing case-management queue.", SMALL)],
    [P("Latency & operational assumptions", SUBH),
     bullets([
        "&lt;1 s measured verdict latency on a single GPU; horizontal throughput scales via inference workers.",
        "Passive scoring first — no customer-facing change; step-up hooks added later.",
        "Alert routing tuned to REVIEW/HIGH only, to avoid analyst alert fatigue.",
     ], s=BULM)],
], [CW * 0.5, CW * 0.5]))
slide("Financial workflow", "A risk-event source in the fraud stack — people and policy decide", s)

# =====================================================================
#  ============  SLIDE 9 — 48-HOUR BUILD  ============
# =====================================================================
s = []
s.append(P("A deliberately narrow finale MVP: <b>a live Indian-language call, scored on-screen in real "
           "time, with evidence and a safe human-review action</b> — on synthetic / consented audio.", LEAD))
s.append(cols([
    [P("MVP scope (must-have)", SUBH),
     bullets([
        "Streaming ingestion → 5 detectors → fusion → LOW/REVIEW/HIGH.",
        "Evidence explanation + safe escalation + privacy boundary.",
        "Benchmark dashboard on synthetic / public / consented test data.",
     ]),
     P("Nice-to-have", st("nth", parent=SUBH, textColor=MUT)),
     P("Indic expansion · authorised-context mock · adversarial-test dashboard · model-update stub. "
       "<b>Do not overbuild.</b>", SMALL)],
    [P("Workstreams (owner · hours · demo proof)", SUBH),
     tbl([
        ["Workstream", "Owner", "Hrs", "Demo proof"],
        ["Ingestion + VAD + streaming", "Member 1", "0–10", "Live waveform in"],
        ["Detectors + fusion + routing", "Member 2", "10–26", "5 scores + verdict"],
        ["Risk engine + explainability", "Member 3", "18–26", "Evidence panel"],
        ["Workflow + escalation + UI", "Member 4", "26–40", "Review action"],
        ["Security / privacy / logging", "M1+M3", "34–40", "Audit log + boundary"],
        ["Eval + failure cases + demo", "All", "40–48", "Benchmark readout"],
     ], [50 * mm, 22 * mm, 16 * mm, 40 * mm], fs=7.7)],
], [CW * 0.42, CW * 0.58]))
s.append(P("Dependencies: phone-audio capture path (Twilio/SIP or replayed WAVs), one GPU, held-out eval "
           "clips. Fallback = replayed recordings if live telephony is unavailable.", SMALLI))
slide("The 48-hour build", "One narrow, provable slice: live call → evidence → safe human action", s)

# =====================================================================
#  ============  SLIDE 10 — THE OUTCOME  ============
# =====================================================================
s = []
s.append(P("Make voice a signal — not a blind spot.",
           st("o1", fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=INK, spaceAfter=6)))
s.append(P("BEFORE  ·  today", st("bl", fontName="Helvetica-Bold", fontSize=8, textColor=HIGH, spaceAfter=2)))
s.append(hchain(CW, [
    ("“Bank official” calls", HIGH), ("Trusted voice", HIGH), ("Social engineering", HIGH),
    ("Transaction approved", HIGH), ("Fraud", HIGH)], h=38, bh=26, fs=8.2))
s.append(Spacer(1, 5))
s.append(P("AFTER  ·  with VoxShield", st("al", fontName="Helvetica-Bold", fontSize=8, textColor=LOW, spaceAfter=2)))
s.append(hchain(CW, [
    ("Voice", CYAN), ("Evidence", TEAL), ("Risk state", PURPLE), ("Verification", REVIEW),
    ("Human review", BLUE), ("Safer decision", LOW)], h=38, bh=26, fs=8.6))
s.append(Spacer(1, 9))
s.append(panel([P("<b>VoxShield does not decide whether a person is a fraudster. It detects whether the "
                  "voice signal deserves scrutiny — and routes that uncertainty safely.</b>",
                  st("final", fontName="Helvetica", fontSize=12.5, leading=17, textColor=INK))],
               accent=TEAL, bg=PANEL2))
s.append(Spacer(1, 6))
s.append(P("VoxShield helps financial teams detect suspicious synthetic voices without turning an "
           "imperfect model into an irreversible decision.", st("o2", parent=BODYM, fontSize=10)))
slide("The outcome", "Make voice a signal — not a blind spot", s)

# =====================================================================
#  ===============  ARCHITECTURE 1/3 — END-TO-END  ===============
# =====================================================================
s = []
s.append(P("One end-to-end system across three trust zones (read bottom-up). "
           "<b>Audio never leaves the model zone</b>; only risk states, evidence and tamper-evident "
           "records cross into the analyst zone.", SMALL))
s.append(Spacer(1, 1))
s.append(architecture_drawing(width=CW, h=138 * mm))
slide("Architecture 1 / 3 — end-to-end system", "Capture → model → analyst, with trust & data boundaries",
      s, mode="arch")

# =====================================================================
#  ===============  ARCHITECTURE 2/3 — DETECTION + DECISION  ======
# =====================================================================
s = []
s.append(P("The decision path from input to escalation — deterministic, explainable, and safe by "
           "construction.", SMALL))
s.append(pipeline_drawing(width=CW, h=92))
s.append(Spacer(1, 3))
s.append(cols([
    [P("Detection → decision", SUBH),
     bullets([
        "Input (8 kHz call) → VAD + preprocess → 3 s/1 s streaming windows.",
        "5 detectors → meta-fusion → Indic/telephony router → Platt calibration.",
        "Optional <b>authorised contextual signals</b> (future integration / prototype mock) adjust risk "
        "— never the sole trigger.",
        "Evidence + risk engine → LOW / REVIEW / HIGH.",
     ], s=BULM)],
    [P("Escalation & outputs", SUBH),
     bullets([
        "LOW → continue · REVIEW → step-up verification · HIGH → authorised human review.",
        "No automatic block or accusation at any state.",
        "Emits a structured risk event (state, evidence, confidence, version, language, latency, audit id).",
     ], s=BULM)],
], [CW * 0.5, CW * 0.5]))
s.append(panel([P("<b>Authorised contextual signals</b> (caller-identity mismatch, unusual beneficiary, "
                  "abnormal timing, recent account changes, repeated failed verification) are "
                  "<b>future integration points / prototype mocks</b>. We do not claim access to bank "
                  "transaction data.", SMALL)], accent=REVIEW))
slide("Architecture 2 / 3 — detection & decision flow", "Input → preprocess → detectors → fusion → risk → escalation",
      s, mode="arch")

# =====================================================================
#  ===============  ARCHITECTURE 3/3 — SECURITY + PRIVACY  ========
# =====================================================================
s = []
s.append(cols([
    [P("Data & privacy", SUBH),
     bullets([
        "<b>Data minimisation:</b> collect only what is required to score the call.",
        "Raw audio processed in the authorised boundary; <b>not exported</b>. Least-data logging "
        "(hashes, verdicts, reason codes).",
        "If audio is retained for an authorised investigation: explicit authorisation, encryption, "
        "access control, audit logging, limited retention, deletion policy.",
        "We do <b>not</b> claim “zero data storage” — we claim controlled, minimised, auditable storage.",
     ], s=BULM)],
    [P("Security & model protection", SUBH),
     bullets([
        "On-prem / air-gapped deployment (DPDP + RBI localisation aligned).",
        "Encrypted evidence store; role-based access; tamper-evident audit log.",
        "Secure model serving; rate limiting; hidden/rotated thresholds where appropriate.",
        "Adversarial evaluation + drift detection + secure update mechanism.",
     ], s=BULM)],
], [CW * 0.5, CW * 0.5]))
s.append(Spacer(1, 2))
s.append(cols([
    [P("What we collect / don't", SUBH),
     tbl([
        ["Aspect", "Position"],
        ["Collect", "Call audio frames + minimal metadata (under authorisation)"],
        ["Process where", "Inside the bank's authorised boundary, on-prem"],
        ["Retain", "Verdicts/evidence by policy; raw audio only if authorised"],
        ["Access", "Role-based; logged"],
        ["Don't collect", "No external export; no unrelated PII"],
     ], [26 * mm, 108 * mm], fs=7.6)],
    [P("Human review is mandatory for high-impact action", st("hr", parent=SUBH, textColor=HIGH)),
     P("Every high-impact outcome passes through an authorised human. The model narrows attention and "
       "supplies evidence; it never executes an irreversible financial action.", SMALL),
     Spacer(1, 3),
     P("Boundaries (honest)", st("bh", parent=SUBH, textColor=REVIEW)),
     P("No complete adversarial robustness is claimed. Real noise/music robustness needs Indic "
       "fine-tuning of the backbones (roadmap). Contextual signals are mocks until integrated.", SMALL)],
], [CW * 0.5, CW * 0.5]))
slide("Architecture 3 / 3 — security & privacy", "Minimisation, consent, encryption, audit, adversarial mitigation",
      s, mode="arch")

# =====================================================================
#  =======================  APPENDIX A1–A8  =======================
# =====================================================================
# ---- A1 : detector architecture ----
s = []
s.append(P("Five complementary detector families over a shared 89-dim feature bank, combined into one "
           "calibrated risk score. Diversity is the anti-evasion property.", SMALL))
s.append(tbl([
    ["Detector", "Family / signal", "What it catches"],
    ["Acoustic DSP", "Hand-built spectral / prosodic DSP (ours)", "Vocoder + phase artifacts; narrowband cues"],
    ["wav2vec2-base", "SSL transformer (deepfake clf)", "General synthetic-speech representation"],
    ["wav2vec2-large-xlsr-53", "Multilingual SSL — 53 langs, ~315M", "Indic-aware synthetic cues"],
    ["DistilHuBERT", "Distilled SSL (fast, deepfake clf)", "Lightweight corroborating signal"],
    ["LFCC + CQCC head", "Trained cepstral logistic head (ours)", "Classic anti-spoofing front-end"],
], [40 * mm, 60 * mm, 66 * mm], fs=8.0))
s.append(Spacer(1, 3))
s.append(cols([
    [P("Feature bank (89-dim) — verified", SUBH),
     P("20 LFCC + 20 CQCC (mean+std = 80) + 9 interpretable scalars (HF ratio/regularity, spectral "
       "flatness, group-delay phase, F0 jitter, shimmer, voiced ratio, silence, breath) = <b>89</b>. "
       "Analysis at 16 kHz; under 8 kHz telephony, information above the Nyquist limit is not available, "
       "so the model relies on cues within the telephony band.", SMALL)],
    [P("Fusion & calibration", SUBH),
     P("A <b>trained LFCC/CQCC logistic head</b> + <b>Platt calibration</b>, blended with the neural "
       "detectors via Indic/telephony routing and a recall-aware max-vote (a confident fake from any "
       "trusted detector is not averaged away) → LOW / REVIEW / HIGH + reason codes. Not a naive average.",
       SMALL)],
], [CW * 0.5, CW * 0.5]))
slide("Appendix A1 — detector architecture", "Five families · 89-dim feature bank · learned meta-fusion",
      s, mode="appx")

# ---- A2 : dataset / provenance ----
s = []
s.append(P("Only synthetic, public, or consented research datasets — no confidential bank, customer, or "
           "platform data. Each dataset is used under its public research-release terms.", SMALL))
s.append(tbl([
    ["Dataset", "Purpose", "Licence / consent", "Usage", "Retention"],
    ["In-the-Wild", "Real/spoof eval (headline EER)", "Public research release", "Evaluation", "Eval only"],
    ["MLAAD", "Cross-dataset OOD", "Public research release", "Evaluation", "Eval only"],
    ["IndicSynth (ACL 2025)", "Indic synthetic fakes", "Public research release", "Train + eval", "Working set"],
    ["IndicVoices (AI4Bharat)", "Real Indic speech", "Public corpus (AI4Bharat)", "Train + eval", "Working set"],
    ["DFADD", "English diffusion/spoof fakes", "Public research release", "Train + eval", "Working set"],
    ["Rural (Bhojpuri)", "Real low-resource speech", "Public research release", "Train + eval", "Working set"],
    ["Self-generated TTS (MMS-TTS…)", "Attack diversity", "Self-produced (synthetic)", "Train + eval", "Working set"],
], [36 * mm, 46 * mm, 42 * mm, 22 * mm, 22 * mm], fs=7.6))
s.append(Spacer(1, 3))
s.append(panel([P("<b>No confidential bank, customer, or platform data is used.</b> Datasets are used "
                  "under their public research-release terms; the full per-dataset licence texts are "
                  "catalogued in the team data catalogue. garystafford is used as a balanced telephony "
                  "eval set. <b>CodecFake+ and BanglaFake are downloaded but not yet integrated into the "
                  "training set.</b> Self-generated fakes are produced in-house for attack diversity.",
                  SMALL)], accent=TEAL))
slide("Appendix A2 — data & provenance", "Synthetic / public / consented research data only — no confidential data",
      s, mode="appx")

# ---- A3 : AI / model disclosure ----
s = []
s.append(P("Full disclosure of models, their role, and how we use them.", SMALL))
s.append(tbl([
    ["Model / asset", "Role", "Source", "Our status"],
    ["wav2vec2-large-xlsr-53 (~315M)", "Indic detector backbone", "facebook/…-xlsr-53", "PRETRAINED → FINE-TUNED BY US"],
    ["wav2vec2-base deepfake clf", "SSL detector (demo ensemble)", "MelodyMachine (HF)", "OPEN-SOURCE"],
    ["xlsr-53 deepfake clf", "SSL detector (demo ensemble)", "Gustking (HF)", "OPEN-SOURCE"],
    ["DistilHuBERT deepfake clf", "Lightweight detector (demo)", "Om-Parab (HF)", "OPEN-SOURCE"],
    ["Acoustic DSP + LFCC/CQCC", "Feature front-ends", "Classic DSP", "IMPLEMENTED BY US"],
    ["Fusion head + Platt calib.", "Combine detectors → risk", "Ours", "TRAINED BY US"],
    ["Silero VAD", "Voice activity detection", "Open-source", "OPEN-SOURCE (unmodified)"],
    ["Liveness / context layer", "Anti-replay / context", "—", "PROPOSED"],
], [50 * mm, 42 * mm, 38 * mm, 40 * mm], fs=7.4))
s.append(P("AI-assisted writing/layout: this document was drafted with AI assistance and reviewed by the "
           "team. All quantitative results are the team's own measured experiments — not AI-fabricated. "
           "Libraries: PyTorch, HuggingFace Transformers/Datasets, torchaudio, soundfile, reportlab.", SMALLI))
slide("Appendix A3 — AI / model disclosure", "Trained · fine-tuned · pretrained · open-source · proposed",
      s, mode="appx")

# ---- A4 : evaluation methodology ----
s = []
s.append(P("Metrics × conditions, with honest status labels. We separate what is measured from what is a "
           "target or not-yet-measured.", SMALL))
s.append(cols([
    [P("Metrics", SUBH),
     P("EER · ROC-AUC · precision · recall · FPR · FNR · detection latency · time-to-warning · "
       "robustness (noise, compression) · unseen-generator · per-language Indic.", SMALL),
     Spacer(1, 3),
     P("Status labels", SUBH),
     P("<font color='#22C55E'><b>CURRENT</b></font> measured today · "
       "<font color='#F5A524'><b>TARGET</b></font> goal · "
       "<font color='#93A1B3'><b>TBM</b></font> to be measured at finale.", SMALL)],
    [tbl([
        ["Condition", "Metric", "Status"],
        ["Clean / in-the-wild", "5.9% EER · AUC 0.983", "CURRENT"],
        ["Telephony (G.711)", "≈1.6 pt codec cost", "CURRENT"],
        ["Indic (MMS-TTS)", "recall 42%→82%", "CURRENT"],
        ["Genuine-Indic fairness", f"FP {GENUINE_FP_BEFORE}→{GENUINE_FP_AFTER}", "CURRENT"],
        ["Noisy / compressed", "robustness", "TBM"],
        ["Unseen generators", "cross-generator EER", "TARGET / TBM"],
        ["Replay / attack", "detection rate", "TBM"],
     ], [42 * mm, 42 * mm, 30 * mm], fs=7.6)],
], [CW * 0.4, CW * 0.6]))
s.append(P("Project evaluation; not independently validated by the hackathon organisers. We do not "
           "fabricate future results.", SMALLI))
slide("Appendix A4 — evaluation methodology", "Metrics × conditions × honest status labels", s, mode="appx")

# ---- A5 : failure modes ----
s = []
s.append(cols([
    [P("False positives (harm to genuine users)", st("fp", parent=SUBH, textColor=REVIEW)),
     P("Causes: unusual genuine voice, illness, poor call quality, background noise, compression, "
       "code-switching, accents, speech impairment, emotional speech, unfamiliar speakers.", SMALL),
     P("<b>Handling:</b> a score over threshold is never “fraud confirmed.” Evidence → risk state → "
       "contextual checks → human/policy decision. Genuine false-alarm rate is tracked per language; "
       "REVIEW adds verification, not a block.", SMALL)],
    [P("False negatives (attacker evasion)", st("fn", parent=SUBH, textColor=HIGH)),
     P("Attackers adapt: new TTS/VC engines, replay, short utterances, threshold probing.", SMALL),
     P("<b>Handling:</b> ensemble diverse detector families; evaluate unseen generators; maintain "
       "adversarial test sets; monitor drift; update models; combine with authorised context; never "
       "present detection as proof of fraud.", SMALL)],
], [CW * 0.5, CW * 0.5]))
s.append(Spacer(1, 3))
s.append(panel([P("<b>Bias:</b> Indic fairness is a first-class metric — an earlier augmentation "
                  "experiment that regressed genuine-Marathi false positives was caught and reverted. "
                  "Fairness is measured per language, not assumed.", SMALL)], accent=TEAL))
slide("Appendix A5 — failure modes", "What happens when the system is wrong — both directions", s, mode="appx")

# ---- A6 : threat model ----
s = []
s.append(P("Adversarial threats and mitigations. No complete robustness is claimed — the goal is to raise "
           "attacker cost and fail safe.", SMALL))
s.append(cols([
    [tbl([
        ["Threat", "Mitigation"],
        ["Adaptive TTS / voice conversion", "Ensemble diversity; unseen-gen eval"],
        ["Replay attacks", "Liveness / anti-replay (proposed)"],
        ["Compression / noise injection", "Telephony-aware training; robustness eval"],
        ["Short-utterance evasion", "Streaming windows; min-evidence gating"],
        ["Model / threshold probing", "Rate limiting; hidden/rotated thresholds"],
     ], [46 * mm, 66 * mm], fs=7.5)],
    [tbl([
        ["Threat", "Mitigation"],
        ["Evidence theft", "Encryption; access control; audit log"],
        ["Unauthorised access", "RBAC; on-prem boundary"],
        ["Data poisoning", "Curated updates; provenance checks"],
        ["Model extraction", "Secure serving; rate limiting"],
        ["Drift over time", "Drift detection; secure update mechanism"],
     ], [46 * mm, 66 * mm], fs=7.5)],
], [CW * 0.5, CW * 0.5]))
slide("Appendix A6 — threat model", "Adversarial threats × mitigations · raise cost, fail safe", s, mode="appx")

# ---- A7 : edge / on-prem optimization ----
s = []
s.append(P("The on-prem constraint is a design driver, not an afterthought — the roadmap targets "
           "edge-class inference for cost and air-gapped deployability.", SMALL))
s.append(cols([
    [P("Deployment tiers", SUBH),
     bullets([
        "<b>Server GPU</b> (today): A100 / consumer RTX; &lt;1 s measured verdict latency; scale via workers.",
        "<b>On-prem CPU / small GPU</b>: DistilHuBERT-led lightweight route.",
        "<b>Edge / NPU</b> (roadmap): quantised INT8 + ONNX for embedded / handset-class hardware.",
     ])],
    [P("Optimisation roadmap", SUBH),
     bullets([
        "ONNX export + INT8 quantisation of the detector stack.",
        "Distillation to a compact narrowband model for telephony.",
        "Optional Snapdragon / NPU acceleration for edge fraud-ops appliances.",
     ]),
     P("Status: PROPOSED / roadmap — not yet benchmarked on edge silicon.", SMALLI)],
], [CW * 0.5, CW * 0.5]))
slide("Appendix A7 — edge & on-prem optimisation", "Server → on-prem CPU → edge/NPU (quantised, roadmap)",
      s, mode="appx")

# ---- A8 : detailed 48-hour plan ----
s = []
s.append(P("Hour-by-hour engineering plan for the finale MVP — deliberately narrow, with a demo proof at "
           "each stage.", SMALL))
s.append(tbl([
    ["Hours", "Focus", "Deliverable / demo proof"],
    ["0–4", "Environment, data prep, skeleton", "Repo + synthetic/consented eval set staged"],
    ["4–10", "Audio ingestion · VAD · streaming", "Live waveform → windows on screen"],
    ["10–18", "Detector integration · inference", "5 detector scores on a live clip"],
    ["18–26", "Fusion · risk engine · explainability", "LOW/REVIEW/HIGH + evidence panel"],
    ["26–34", "Financial workflow · escalation", "Review/step-up action wired to a mock queue"],
    ["34–40", "Security · privacy · logging", "Data boundary + tamper-evident audit log"],
    ["40–46", "UI · dashboard · live demo", "Analyst console + benchmark readout"],
    ["46–48", "Testing · failure cases · rehearsal", "Frozen demo + per-language fairness check"],
], [18 * mm, 60 * mm, 88 * mm], fs=7.7))
slide("Appendix A8 — detailed 48-hour plan", "Narrow MVP, hour-by-hour, with a demo proof at every stage",
      s, mode="appx")

# ---------------------------------------------------------------- build
doc = SimpleDocTemplate(
    OUT, pagesize=PAGE, topMargin=MT, bottomMargin=MB, leftMargin=ML, rightMargin=MR,
    title="VoxShield — RAKSHAM (IIT Delhi x Amazon) Round 1 Submission",
    author="Team DigiSeva — Devansh Goenka")
doc.build(E, onFirstPage=frame, onLaterPages=frame)
print("wrote", OUT, "— pages:", len(META),
      "| deck 10 + arch 3 + appendix 8 | genuine-FP:", GENUINE_FP_BEFORE)
