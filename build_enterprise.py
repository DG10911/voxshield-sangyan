#!/usr/bin/env python3
"""Inject a new ENTERPRISE / BUSINESS MODE chapter into presentation.html.
Additive only, no existing section, route, or style is modified. Re-runnable:
if the chapter already exists it is replaced (between the sentinel markers)."""
import math, re, sys

PATH = "/Users/devanshgoenka/conductor/workspaces/voxshield/san-antonio/presentation.html"
CSS_START = "/* == ENTERPRISE MODE CSS (added) == */"
CSS_END   = "/* == /ENTERPRISE MODE CSS == */"
SEC_START = "<!-- == ENTERPRISE MODE (added chapter) == -->"
SEC_END   = "<!-- == /ENTERPRISE MODE == -->"

html = open(PATH).read()

# strip any prior injection so the script is idempotent
html = re.sub(re.escape(CSS_START) + r".*?" + re.escape(CSS_END), "", html, flags=re.S)
html = re.sub(re.escape(SEC_START) + r".*?" + re.escape(SEC_END), "", html, flags=re.S)

# ---------------------------------------------------------------- CSS
CSS = CSS_START + """
.ent-hub-wrap{border-radius:22px;border:1px solid var(--line);overflow:hidden;overflow-x:auto;position:relative;
  background:radial-gradient(900px 460px at 50% 46%,rgba(59,130,246,.10),transparent 62%),linear-gradient(170deg,#0a1526,#070f1d);
  box-shadow:0 40px 100px -40px rgba(0,0,0,.9);padding:clamp(10px,2vw,24px)}
.ent-hub-wrap svg{width:100%;min-width:920px;height:auto;display:block}
.ent-core{fill:rgba(13,27,48,.96);stroke:rgba(59,130,246,.65);stroke-width:1.6}
.ent-core-ring{fill:none;stroke:rgba(59,130,246,.3);stroke-width:1;stroke-dasharray:4 8;animation:entspin 24s linear infinite;transform-origin:600px 360px}
@keyframes entspin{to{transform:rotate(360deg)}}
.ent-inode{fill:rgba(13,27,48,.92);stroke:rgba(147,169,200,.3);stroke-width:1}
.ent-glow{filter:drop-shadow(0 0 22px rgba(59,130,246,.5))}
.ent-ind{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:18px}
.ent-icard{position:relative;border-radius:var(--r);padding:24px 22px;overflow:hidden;
  background:linear-gradient(160deg,rgba(13,27,48,.94),rgba(11,23,40,.78));border:1px solid var(--line);
  box-shadow:0 24px 60px -30px rgba(0,0,0,.75), inset 0 1px 0 rgba(232,240,255,.06);
  transition:transform .5s var(--ease),border-color .5s,box-shadow .5s}
.ent-icard:hover{transform:translateY(-6px);border-color:var(--line-strong);box-shadow:0 34px 80px -30px rgba(2,8,20,.9),0 0 0 1px rgba(59,130,246,.12)}
.ent-icard .eic{width:46px;height:46px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:21px;
  background:var(--acc-soft);border:1px solid var(--line-strong);color:#8ab6ff}
.ent-icard h4{font-size:16.5px;font-weight:700;margin:14px 0 4px}
.ent-badge{position:absolute;top:18px;right:18px;font-family:var(--mono);font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;
  color:#7fe0a2;border:1px solid rgba(34,197,94,.35);background:rgba(34,197,94,.08);padding:4px 9px;border-radius:100px}
.ent-icard .ehint{font-size:12px;color:var(--t3);margin-top:6px}
.ent-uses{list-style:none;margin-top:10px;max-height:0;overflow:hidden;opacity:0;transition:max-height .55s var(--ease),opacity .4s,margin .4s}
.ent-icard:hover .ent-uses{max-height:240px;opacity:1;margin-top:12px}
.ent-icard:hover .ehint{opacity:0;height:0;margin:0;transition:.3s}
.ent-uses li{font-size:12.5px;color:var(--t2);padding:3px 0;display:flex;gap:9px;align-items:baseline}
.ent-uses li::before{content:"›";color:var(--acc);flex:none}
.ent-arch{display:flex;flex-direction:column;align-items:center;gap:0}
.ent-anode{width:min(600px,100%);border-radius:14px;border:1px solid var(--line);text-align:center;padding:15px 22px;
  background:linear-gradient(160deg,rgba(13,27,48,.94),rgba(11,23,40,.72));box-shadow:0 20px 50px -32px rgba(0,0,0,.8)}
.ent-anode.core{border-color:var(--line-strong);box-shadow:0 0 42px -14px rgba(59,130,246,.4)}
.ent-anode h5{font-size:15px;font-weight:700}
.ent-anode p{font-size:11.5px;color:var(--t3);font-family:var(--mono);margin-top:2px;letter-spacing:.04em}
.ent-micro{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:10px}
.ent-micro span{font-family:var(--mono);font-size:10.5px;color:#a9c8ff;border:1px solid var(--line-strong);background:var(--acc-soft);padding:5px 10px;border-radius:8px}
.ent-conn{width:2px;height:24px;background:repeating-linear-gradient(180deg,var(--acc) 0 5px,transparent 5px 11px);animation:entdash .8s linear infinite;opacity:.7}
@keyframes entdash{to{background-position:0 11px}}
.ent-work{display:flex;flex-wrap:wrap;align-items:stretch;gap:8px}
.ent-wstep{flex:1 1 130px;border-radius:12px;border:1px solid var(--line);background:rgba(13,27,48,.86);padding:14px 12px;text-align:center;transition:.4s var(--ease)}
.ent-wstep:hover{border-color:var(--line-strong);transform:translateY(-3px)}
.ent-wstep .wn{font-family:var(--mono);font-size:10px;color:var(--t3)}
.ent-wstep h5{font-size:12.5px;font-weight:600;margin-top:4px}
.ent-dec{display:flex;gap:12px;justify-content:center;margin-top:16px;flex-wrap:wrap}
.ent-dec span{font-family:var(--mono);font-size:12.5px;font-weight:700;padding:9px 18px;border-radius:10px;border:1px solid}
.ent-dec .ap{color:#7fe0a2;border-color:rgba(34,197,94,.4);background:rgba(34,197,94,.08)}
.ent-dec .fl{color:#f2c266;border-color:rgba(245,158,11,.4);background:rgba(245,158,11,.08)}
.ent-dec .rj{color:#ff9a9a;border-color:rgba(239,68,68,.45);background:rgba(239,68,68,.08)}
.ent-rev{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:16px}
.ent-rcard{border-radius:14px;border:1px solid var(--line);background:linear-gradient(160deg,rgba(13,27,48,.92),rgba(11,23,40,.72));padding:22px 20px;transition:.5s var(--ease);position:relative;overflow:hidden}
.ent-rcard::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--grn),transparent)}
.ent-rcard:hover{transform:translateY(-6px);border-color:var(--line-strong)}
.ent-rcard .rt{font-family:var(--mono);font-size:10px;color:#7fe0a2;letter-spacing:.14em;text-transform:uppercase}
.ent-rcard h5{font-size:16px;font-weight:700;margin:8px 0 6px}
.ent-rcard p{font-size:12px;color:var(--t2);line-height:1.55}
.ent-logos{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:12px}
.ent-logo{border-radius:11px;border:1px solid var(--line);background:var(--glass);padding:16px 12px;text-align:center;
  font-family:var(--mono);font-size:12.5px;color:var(--t2);letter-spacing:.02em;transition:.4s var(--ease)}
.ent-logo:hover{border-color:var(--line-strong);color:#a9c8ff;transform:translateY(-3px)}
.ent-journey{display:flex;flex-wrap:wrap;gap:0;align-items:flex-start}
.ent-jstep{flex:1 1 130px;text-align:center;position:relative;padding:0 6px}
.ent-jdot{width:16px;height:16px;border-radius:50%;background:var(--bg);border:2px solid var(--acc);margin:0 auto 14px;box-shadow:0 0 14px rgba(59,130,246,.7);position:relative;z-index:2}
.ent-jline{position:absolute;top:7px;left:55%;width:90%;height:2px;background:linear-gradient(90deg,var(--acc),rgba(59,130,246,.12))}
.ent-jstep:last-child .ent-jline{display:none}
.ent-jstep h5{font-size:13.5px;font-weight:700}
.ent-jstep p{font-size:11px;color:var(--t3);margin-top:3px;line-height:1.4}
.ent-scale{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
@media(max-width:760px){.ent-scale{grid-template-columns:repeat(2,1fr)}}
.ent-scard{border-radius:12px;border:1px solid var(--line);background:rgba(13,27,48,.86);padding:18px 14px;text-align:center}
.ent-scard .sv{font-family:var(--mono);font-size:clamp(17px,1.9vw,25px);font-weight:700;color:#8ab6ff}
.ent-scard .sk{font-size:10.5px;color:var(--t3);margin-top:4px;font-family:var(--mono);letter-spacing:.08em;text-transform:uppercase}
.ent-scard .sbar{height:6px;border-radius:100px;background:rgba(147,169,200,.12);margin-top:12px;overflow:hidden;border:1px solid rgba(147,169,200,.08)}
.ent-scard .sbar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#2f6fe0,#8ab6ff);transition:width 1.4s var(--ease);box-shadow:0 0 12px -2px rgba(59,130,246,.7)}
.in .ent-scard .sbar i{width:var(--w)}
""" + CSS_END + "\n"

# ---------------------------------------------------------------- HUB SVG
industries = [
    ("Banking & Finance", "🏦", "Call centres · mobile & net banking · UPI verification · loan approval · KYC", "PRIMARY MARKET"),
    ("Telecom", "📡", "Customer care · SIM verification · voice auth · fraud-call screening", "ANTI-VISHING"),
    ("Government", "🏛", "Citizen helplines · police · emergency calls · Aadhaar verification", "DIGITAL INDIA"),
    ("Healthcare", "⚕", "Telemedicine · medical helplines · insurance & doctor authentication", "TELEHEALTH"),
    ("Insurance", "📋", "Claims intake · customer & agent verification · call investigation", "CLAIMS FRAUD"),
    ("BPO / Contact", "🎧", "Contact centres · quality monitoring · AI-agent verification", "AGENT ASSIST"),
    ("Media", "📰", "News verification · fake-audio detection · journalist authentication", "DEEPFAKE"),
    ("Legal", "⚖", "Court evidence · audio verification · digital forensics · investigation", "EVIDENCE"),
    ("Enterprise", "🏢", "Internal meetings · HR interviews · executive & secure comms", "EXEC IMPERSONATION"),
    ("Education", "🎓", "Online exams · viva authentication · remote interviews · voice identity", "EXAM INTEGRITY"),
    ("Cybersecurity", "🔐", "SOC signal · incident response · threat hunting · digital evidence", "SOC"),
    ("Defense", "🛰", "Secure comms · intelligence · tactical & command authentication", "COMMAND AUTH"),
]

cx, cy, rx, ry = 600, 360, 470, 268
nw, nh = 168, 50
nodes, lines, dots = [], [], []
for i, (name, ic, uses, badge) in enumerate(industries):
    a = math.radians(-90 + i * 30)
    x = cx + rx * math.cos(a)
    y = cy + ry * math.sin(a)
    # edge of core toward node
    ex = cx + 152 * math.cos(a)
    ey = cy + 152 * math.sin(a)
    pid = f"entp{i}"
    lines.append(f'<path id="{pid}" class="pline" d="M{ex:.0f} {ey:.0f} L{x-0:.0f} {y:.0f}"/>')
    nodes.append(
        f'<g class="ent-inode-g"><rect class="ent-inode" x="{x-nw/2:.0f}" y="{y-nh/2:.0f}" width="{nw}" height="{nh}" rx="11"/>'
        f'<text x="{x:.0f}" y="{y-3:.0f}" text-anchor="middle" class="ptext" font-size="12.5">{ic}  {name.split(" / ")[0].split(" & ")[0]}</text>'
        f'<text x="{x:.0f}" y="{y+13:.0f}" text-anchor="middle" class="ptext2" font-size="8.5">{badge}</text></g>')
    if i % 2 == 0:  # flowing packet on every other spoke (perf)
        dots.append(f'<circle class="pdot" r="3"><animateMotion dur="2.6s" begin="{i*0.18:.2f}s" repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion></circle>')

core_caps = ["Voice Authentication", "AI Deepfake Detection", "Liveness Detection", "Risk Engine", "Fraud Intelligence", "API Gateway"]
core_txt = "".join(
    f'<text x="600" y="{330 + k*20:.0f}" text-anchor="middle" class="ptext2" font-size="11">{c}</text>'
    for k, c in enumerate(core_caps))

HUB_SVG = (
    '<svg viewBox="0 0 1200 720" role="img" aria-label="VoxShield enterprise ecosystem: a central AI core connected to twelve industry sectors">'
    + "".join(lines)
    + '<circle class="ent-core-ring" cx="600" cy="360" r="200"/>'
    + '<circle class="ent-core ent-glow" cx="600" cy="360" r="152"/>'
    + '<text x="600" y="300" text-anchor="middle" class="ptext" font-size="17" font-weight="700">VOXSHIELD AI CORE</text>'
    + core_txt
    + "".join(nodes) + "".join(dots)
    + "</svg>")

# ---------------------------------------------------------------- section HTML
def icards():
    out = []
    for name, ic, uses, badge in industries:
        lis = "".join(f"<li>{u.strip()}</li>" for u in uses.split("·"))
        out.append(
            f'<div class="ent-icard" data-reveal><span class="ent-badge">{badge}</span>'
            f'<div class="eic">{ic}</div><h4>{name}</h4>'
            f'<div class="ehint">Hover to see use-cases →</div>'
            f'<ul class="ent-uses">{lis}</ul></div>')
    return "\n".join(out)

arch_layers = [
    ("Client", "User · web · mobile · IVR · SIP trunk", None, False),
    ("API Gateway", "auth · routing · rate-limit", None, False),
    ("Load Balancer", "horizontal fan-out · health checks", None, False),
    ("VoxShield AI Cluster", "stateless replicas", ["Detection Engine", "Speaker Verification", "Liveness", "Risk Engine", "Audio Processing"], True),
    ("Message Queue", "async jobs · backpressure", None, False),
    ("GPU Cluster", "batched neural inference · sub-second", None, False),
    ("Database + Analytics", "hash-keyed audit ledger · metrics", None, False),
    ("Dashboard + Enterprise API", "operator console · webhooks · SDK", None, False),
]
def arch_html():
    out = []
    for i, (h, p, micro, core) in enumerate(arch_layers):
        cls = "ent-anode core" if core else "ent-anode"
        m = ('<div class="ent-micro">' + "".join(f"<span>{x}</span>" for x in micro) + "</div>") if micro else ""
        out.append(f'<div class="{cls}"><h5>{h}</h5><p>{p}</p>{m}</div>')
        if i < len(arch_layers) - 1:
            out.append('<div class="ent-conn" aria-hidden="true"></div>')
    return "\n".join(out)

modes = [
    ("☁", "Cloud SaaS", "Multi-tenant, elastic, zero-ops. Fastest path to pilot, spin up and integrate in days."),
    ("⬢", "Private Cloud", "Single-tenant VPC in the customer's cloud account. Data residency + isolation."),
    ("🏛", "On-Premise", "Air-gapped in the bank's data centre. Docker image bakes every model, no runtime downloads."),
    ("▣", "Edge Deployment", "Quantised models at the branch / gateway for lowest-latency, offline-capable screening."),
]
def modes_html():
    return "\n".join(
        f'<div class="card tilt" data-reveal><div><div class="ic">{ic}</div><h3>{h}</h3><p>{p}</p></div></div>'
        for ic, h, p in modes)

workflow = ["Incoming Voice", "Noise Removal", "Speaker Verification", "Liveness Check", "Deepfake Detection", "Risk Score", "Decision Engine"]
def work_html():
    return "".join(
        f'<div class="ent-wstep" data-reveal style="--d:{i*.05}s"><div class="wn">{i+1:02d}</div><h5>{w}</h5></div>'
        for i, w in enumerate(workflow))

revenue = [
    ("RECURRING", "Enterprise SaaS", "Per-seat / per-line subscriptions for banks, BPOs and enterprises."),
    ("USAGE", "API Usage Pricing", "Metered per voice-analysis call, scales with the customer's call volume."),
    ("LICENSE", "On-Prem Licensing", "Annual license for air-gapped, self-hosted deployments (banking / defense)."),
    ("CONTRACT", "Government Contracts", "Citizen-helpline & Digital-India anti-fraud programs; multi-year tenders."),
    ("CONTRACT", "Banking Contracts", "Fraud-desk integration alongside CNAP / caller-ID; the beachhead market."),
    ("VERTICAL", "Healthcare & Insurance", "Telehealth doctor auth and claims-call investigation packages."),
    ("PARTNER", "OEM Partnerships", "Embed the engine inside contact-centre / telecom platforms."),
    ("PARTNER", "White-Label", "Rebrandable detection for MSSPs and cloud-comms vendors."),
    ("PLATFORM", "Marketplace", "Cloud-marketplace listings (AWS / Azure) for frictionless procurement."),
]
def rev_html():
    return "\n".join(
        f'<div class="ent-rcard" data-reveal><div class="rt">{t}</div><h5>{h}</h5><p>{p}</p></div>'
        for t, h, p in revenue)

integrations = ["AWS", "Azure", "Google Cloud", "Twilio", "Zoom", "Microsoft Teams", "Genesys", "Cisco",
                "Salesforce", "Zendesk", "WhatsApp Business", "Slack", "REST API", "Webhooks", "SIP", "SDK"]
def logos_html():
    return "\n".join(f'<div class="ent-logo" data-reveal>{g}</div>' for g in integrations)

journey = [
    ("Prospect", "discovery + threat assessment"),
    ("Pilot", "sandbox on recorded traffic"),
    ("Integration", "drop-in API / SIP hook"),
    ("Training", "tune thresholds to their FP budget"),
    ("Production", "live fraud-desk signal"),
    ("Monitoring", "24×7 dashboards + audit"),
    ("Expansion", "new lines, new sectors"),
]
def journey_html():
    return "".join(
        f'<div class="ent-jstep" data-reveal style="--d:{i*.06}s"><div class="ent-jline"></div><div class="ent-jdot"></div><h5>{h}</h5><p>{p}</p></div>'
        for i, (h, p) in enumerate(journey))

security = ["TLS 1.3", "JWT", "OAuth 2.0", "RBAC", "Audit Logs", "SIEM", "SOC", "Zero Trust",
            "HSM Keys", "API Keys", "Rate Limiting", "Threat Intelligence", "AES-256 at rest"]
def sec_html():
    return "\n".join(f'<div class="chip" data-reveal><span class="code">✓</span><span class="d">{x}</span></div>' for x in security)

scale = [("10", "pilot", 6), ("1K", "branch", 20), ("100K", "regional", 45), ("1M", "national bank", 72), ("100M", "multi-bank", 100)]
def scale_html():
    return "\n".join(
        f'<div class="ent-scard" data-reveal><div class="sv">{v}</div><div class="sk">{k}</div><div class="sbar"><i style="--w:{w}%"></i></div></div>'
        for v, k, w in scale)

SECTION = SEC_START + f"""
<!-- ================= ENTERPRISE / BUSINESS MODE ================= -->
<section id="enterprise" aria-label="Enterprise & Business Mode">
  <div class="ch-head" data-reveal>
    <span class="ch-kicker">Enterprise · Business Mode</span>
    <h2>One AI platform. <span class="grad">Every voice. Every industry.</span></h2>
    <p class="ch-sub">The banking fraud desk is the beachhead. The same drop-in engine, detection, liveness, risk, secures every sector where a voice must be provably human. Here is the deployment ecosystem, the architecture, and the business model behind it.</p>
  </div>

  <h3 class="sub-h" data-reveal>Enterprise deployment <span class="grad">ecosystem</span></h3>
  <div class="ent-hub-wrap" data-reveal>{HUB_SVG}</div>

  <div style="height:6vh"></div>
  <h3 class="sub-h" data-reveal>Twelve sectors, <span class="grad">one API</span></h3>
  <div class="ent-ind">
    {icards()}
  </div>
  <p class="footnote" data-reveal>Banking is live today (TRL-5). The other sectors are the same engine applied to adjacent voice-fraud problems, the addressable expansion, not current deployments.</p>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Deployment <span class="grad">architecture</span></h3>
  <div class="ent-arch" data-reveal>
    {arch_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Deployment <span class="grad">modes</span></h3>
  <div class="cards">
    {modes_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Enterprise <span class="grad">workflow</span></h3>
  <div class="ent-work">
    {work_html()}
  </div>
  <div class="ent-dec" data-reveal>
    <span class="ap">✓ APPROVE</span><span class="fl">⚑ FLAG → step-up</span><span class="rj">✕ REJECT</span>
  </div>
  <p class="footnote" data-reveal>Every hop is a boundary a security team can inspect. The decision engine never auto-blocks, HIGH routes to step-up verification, a human stays in charge.</p>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Business <span class="grad">model</span></h3>
  <div class="ent-rev">
    {rev_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Customer <span class="grad">journey</span></h3>
  <div class="ent-journey">
    {journey_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Integrations &amp; <span class="grad">channels</span></h3>
  <div class="ent-logos">
    {logos_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Security <span class="grad">architecture</span></h3>
  <div class="reason-chips">
    {sec_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Scales like a web service, <span class="grad">because it is one</span></h3>
  <div class="ent-scale">
    {scale_html()}
  </div>

  <div style="height:8vh"></div>
  <h3 class="sub-h" data-reveal>Enterprise <span class="grad">SLAs &amp; readiness</span></h3>
  <div class="stats">
    <div class="stat blue" data-reveal><div class="v"><span class="cnt" data-to="99.9" data-dec="1">0.0</span><span class="u">%</span></div><div class="k">Availability target for the managed service, stateless replicas + health-checked load balancing.</div><div class="m">Target SLA</div></div>
    <div class="stat good" data-reveal style="--d:.08s"><div class="v">&lt;<span class="cnt" data-to="300" data-dec="0">0</span><span class="u">ms</span></div><div class="k">Detection latency target on GPU, a fresh fused verdict inside the live call.</div><div class="m">Target · GPU</div></div>
    <div class="stat blue" data-reveal style="--d:.16s"><div class="v"><span class="cnt" data-to="24" data-dec="0">0</span><span class="u">×7</span></div><div class="k">Monitoring, audit and alerting, every decision hash-keyed for the ledger.</div><div class="m">Operations</div></div>
    <div class="stat good" data-reveal style="--d:.24s"><div class="v">N<span class="u">×</span></div><div class="k">Linear horizontal scale, add replicas, capacity grows. No shared session state.</div><div class="m">Architecture</div></div>
  </div>
  <div class="reason-chips" data-reveal style="margin-top:22px">
    <div class="chip"><span class="code">SOC 2</span><span class="d">controls, roadmap</span></div>
    <div class="chip"><span class="code">GDPR</span><span class="d">/ DPDP-aligned by design</span></div>
    <div class="chip"><span class="code">ISO 27001</span><span class="d">, roadmap</span></div>
    <div class="chip"><span class="code">WCAG 2.1 AA</span><span class="d">accessible UI today</span></div>
  </div>
  <p class="footnote" data-reveal>SLAs and certifications are targets for the managed service as it hardens from the TRL-5 core, stated as goals, not current certifications. Accessibility (WCAG 2.1 AA) and the hash-keyed audit trail are implemented today.</p>
</section>

""" + SEC_END + "\n\n"

# ---------------------------------------------------------------- inject
marker = "<!-- ================= CH 11 · VISION ================= -->"
assert marker in html, "vision marker not found"
html = html.replace(marker, SECTION + marker, 1)

css_marker = "/* ---------- reduced motion ---------- */"
assert css_marker in html, "reduced-motion css marker not found"
html = html.replace(css_marker, CSS + "\n" + css_marker, 1)

# nav arrays
assert "'market','vision'" in html, "chapters array anchor not found"
html = html.replace("'market','vision'", "'market','enterprise','vision'", 1)
assert "'11 · Market','12 · Vision'" in html, "labels array anchor not found"
html = html.replace("'11 · Market','12 · Vision'", "'11 · Market','Enterprise · Scale','12 · Vision'", 1)

open(PATH, "w").write(html)
print("injected enterprise chapter · chapters now include 'enterprise'")
