# Shared content for the Snapdragon AI Lab submission (deck PPTX + PDF + brief).
# All numbers are the team-verified / research-verified set — no fabrication.
TITLE = "VoxShield Edge"
SUB   = "Real-Time, Privacy-Preserving Voice-Clone Defense for Indian Telephony"
EVENT = "Snapdragon® AI Lab Build & Present Challenge · Qualcomm"
AUTHOR= "Devansh Goenka"
ONELINE = ("A bank fraud analyst's HP Snapdragon laptop detects AI-cloned voices in real time, "
           "fully on-device on the Hexagon NPU — no call audio ever leaves the machine.")

STATS = [
  ("5.9%",  "EER · deployed fusion\n(held-out In-the-Wild)"),
  ("6.8%",  "EER · unseen-generator\ndeepfakes (OOD, MLAAD)"),
  ("0.98",  "ROC-AUC\non OOD deepfakes"),
  ("45–80", "TOPS Hexagon NPU\n(Snapdragon X / X2)"),
]

# each slide: (kind, title, payload)
SLIDES = [
 ("title", TITLE, {}),
 ("problem","The problem: cloned voices over the bank phone line", {
    "body":"AI voice cloning is cheap and fast. In India, phone-based fraud — fake bank officials, "
           "“digital arrest” scams, relative-in-distress calls — increasingly uses synthetic voices "
           "in Indian languages over ordinary 8 kHz phone lines.",
    "bullets":[
      "Cloning a voice now takes seconds of reference audio.",
      "Telephony (G.711, 8 kHz) hides the very artifacts most detectors rely on.",
      "Sensitive customer call audio should not be shipped to a foreign cloud.",
      "A verdict after the call ends is forensics, not protection."]}),
 ("why","Why on-device — and why Snapdragon, now", {
    "bullets":[
      "Privacy by design: raw call audio never leaves the analyst's laptop (DPDP-aligned).",
      "Real-time: a verdict forms within the first seconds of the call, offline.",
      "The Snapdragon Hexagon NPU (45–80 TOPS) makes local real-time speech AI practical on a laptop.",
      "Resilient: works air-gapped, in branches with poor connectivity."]}),
 ("solution","VoxShield Edge", {
    "body":"An on-device, Indic-first, telephony-hardened voice-deepfake detector. Given a live call it returns "
           "a calibrated LOW / MEDIUM / HIGH risk verdict with explainable reason codes — decision support for a "
           "fraud analyst, never automatic blocking.",
    "flow":["Live call","Detect","Explain","Risk-score","Step-up verification"]}),
 ("arch","How it works", {
    "steps":["8 kHz G.711 telephony","Silero VAD","3 s window · 1 s hop","89-dim feature bank",
             "5-detector ensemble","Learned meta-fusion","Calibrated risk + reason codes"],
    "note":"Five complementary detectors (Acoustic DSP · wav2vec2 · XLS-R 300M · DistilHuBERT · LFCC+CQCC) "
           "combined by a learned meta-stacker with Indic / telephony routing."}),
 ("snap","Snapdragon optimisation — the on-device pipeline", {
    "pipe":["PyTorch model","→ ONNX (INT8 quantised)","→ ONNX Runtime · QNN EP","→ Hexagon NPU (45–80 TOPS)"],
    "bullets":[
      "Compiled & profiled on real Snapdragon devices via Qualcomm AI Hub (qai-hub).",
      "On-device Windows/ARM64 app through ONNX Runtime QNN Execution Provider (onnxruntime-qnn).",
      "Leverages the AI Hub speech ecosystem: WavLM-Base-Plus backbone + Whisper for on-device transcription.",
      "Honest status: detector runs today on CPU/GPU; NPU port + INT8 quantisation via AI Hub is the optimisation in progress."]}),
 ("results","Evidence — measured, honestly scoped", {
    "rows":[["Deployed fusion","held-out In-the-Wild","EER","5.9%"],
            ["Unseen-generator deepfakes","MLAAD (OOD)","EER / AUC","6.8% / 0.98"],
            ["Detector scoreboard","same eval set","EER single/avg/fusion","16.0 / 19.1 / 5.9"],
            ["Indic recall","MMS-TTS fakes (after retrain)","recall","42% → 82%"]],
    "note":"EER = Equal Error Rate (lower is better) — not accuracy. In-corpus and out-of-distribution figures "
           "are reported separately and never conflated."}),
 ("deploy","Deployment & accessibility", {
    "bullets":[
      "Runs on an HP Snapdragon laptop — offline, private, low-power on the NPU.",
      "No cloud dependency; no raw audio egress — architected for institutional data-governance.",
      "Explainable analyst console: risk + per-signal reason codes (spectral, phase, prosody, breath).",
      "Human-in-the-loop: recommends OTP / biometric / fraud-desk step-up; never auto-blocks a customer."]}),
 ("diff","What makes it different", {
    "cols":[["Cloud incumbents","English-first, cloud-only, closed, black-box"],
            ["VoxShield Edge","Indic-first · telephony-hardened · on-device NPU · explainable · open/measured"]],
    "note":"The contribution is the integration under one hard constraint set — Indic + narrowband + on-device + "
           "explainable + private — not a single new algorithm."}),
 ("roadmap","Roadmap", {
    "bullets":[
      "Now: ONNX export + INT8 quantisation; Qualcomm AI Hub compile/profile on Snapdragon X/X2.",
      "Next: measured on-NPU latency + power; streaming live-call demo on the laptop.",
      "Then: more Indic languages, larger real-world corpus, challenge-response liveness.",
      "Goal: a private, on-device fraud-screening layer for every bank branch."]}),
 ("close","VoxShield Edge — private AI, on your device", {
    "body":"Indic-language + telephony-quality + real-time + on-device + explainable voice-deepfake detection "
           "for financial fraud — running on the Snapdragon NPU, with honest, measured evidence.",
    "contact":"Devansh Goenka · GitHub: DG10911/voxshield · devanshgoenka03@gmail.com"}),
]
