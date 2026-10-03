"""Build SANGYAN_VoxShield_demo.mp4 — narrated 3-5 min explainer/demo video.
Uses macOS `say` for narration + one real Hindi TTS scam clip, Pillow for frames,
ffmpeg to assemble. Run:  .venv_voxshield/bin/python make_video.py"""
import os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (11, 18, 32); FG = (230, 237, 243); ACC = (34, 211, 238); SUB = (148, 163, 184); WARN = (245, 158, 11)
OUT = "vid"; os.makedirs(OUT, exist_ok=True)
SCAM = "नमस्ते, मैं सेबी से बोल रहा हूँ। आपके खाते में समस्या है, कृपया तुरंत अपना ओटीपी और पैसे भेजें।"
SCAM_EN = "\"Hello, I'm calling from SEBI. There's a problem with your account — send your OTP and transfer the money immediately.\""

def font(size, bold=False):
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def frame(path, kicker, title, lines, foot=""):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    y = 90
    if kicker:
        d.text((90, y), kicker.upper(), font=font(34, True), fill=ACC); y += 70
    d.text((90, y), title, font=font(72, True), fill=FG); y += 120
    for ln in lines:
        d.text((110, y), ln, font=font(38), fill=SUB); y += 66
    if foot:
        d.text((90, H - 90), foot, font=font(30), fill=WARN)
    d.rectangle([0, H - 14, W, H], fill=ACC)
    img.save(path)

def say(text, out, voice="Samantha", rate=175):
    subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", out, text], check=True)

def aiff_to_wav(a, w):
    subprocess.run(["ffmpeg", "-y", "-i", a, "-ar", "44100", "-ac", "2", w],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def clip(png, wav, mp4):
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", wav,
                    "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-r", "30", mp4],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

scenes = [
    ("title", "SANGYAN · Track A", "VoxShield", ["Voice Scam Shield for India's investors",
     "Detect AI-cloned voices before money moves", "23 Indic languages · narrowband telephony · on-prem"],
     "VoxShield detects AI-cloned voices in investment scam calls before money moves. It works in twenty-three Indian languages, on phone-quality audio, and it never gives investment advice."),
    ("problem", "The problem", "Voice is the new attack surface",
     ["16+ crore Demat accounts; 70%+ from Tier-2/3 cities",
      "Attackers clone voices to impersonate brokers, SEBI and family",
      "Victims realise only after the money is gone",
      "No tool detects synthetic speech in Indic, over phone audio"],
     "India's retail investors are targeted by voice-based fraud. Attackers use A I voice cloning to impersonate brokers, regulators and even family. Most victims realise too late, after the money has left. And today, no accessible tool detects synthetic speech in Indian languages over phone-quality audio."),
    ("user", "Who we build for", "A first-time investor in Tier-2/3",
     ["More comfortable in a regional language than English",
      "Gets an urgent call: 'SEBI se hoon, turant paise bhejo'",
      "Journey: hears clip > forwards to VoxShield > verdict",
      "+ transcript + language + 'pause and verify'"],
     "We build for a first-time investor in a tier-two or tier-three city, who is more comfortable in a regional language. They receive an urgent call: this is S E B I, transfer the money now. They forward the clip to VoxShield and immediately get a verdict, a transcript, the language, and a clear pause-and-verify action."),
    ("scam", "Demo · synthetic scam call", "Listen: AI-cloned 'SEBI' voice",
     ["Transcript: " + SCAM_EN, "Detected language: hi  ·  Verdict: SYNTHETIC (AI-cloned)",
      "Reason codes: vocoder artefacts · channel mismatch · prosody",
      "Action: PAUSE & VERIFY via official channels"],
     None),   # uses the real Hindi clip as audio
    ("solution", "The solution", "Hear the human behind the call",
     ["Input: any suspicious call recording or voice note",
      "Output: HUMAN / SYNTHETIC / ABSTAIN + transcript + reason codes",
      "Plain-language warning and a pause-and-verify action",
      "Runs on-prem for privacy; never gives stock tips"],
     "VoxShield takes a suspicious call recording and returns one of three honest outcomes: human, synthetic, or abstain. Alongside it, the transcript, the detected language, and human-readable reason codes. Everything runs on-premise for privacy, and VoxShield never gives stock tips or recommendations."),
    ("arch", "Architecture", "From audio to an honest verdict",
     ["Input Profiler (codec / bandwidth / S N R) > adapter",
      "Fast gate > XLS-R + RawBoost detector + codec-aware branch",
      "Evidence: physics, replay, environment, cross-codec, speaker, semantic",
      "Evidence arbitration > accept / abstain > verdict + reason codes"],
     "The pipeline profiles the channel: codec, bandwidth and noise. A fast gate and a fine-tuned X L S R plus RawBoost detector run, alongside codec-aware branches. Multiple evidence signals are then arbitrated into an honest decision: accept, or abstain, with reason codes."),
    ("tech", "Technology", "What it's built on",
     ["Fine-tuned XLS-R-300M + RawBoost; telephony augmentation",
      "Bhashini for Indic A L D / A S R / T T S; AIKosh corpora and models",
      "E C A P A speaker verification + NeMo diarization",
      "PGD adversarial training + distilled edge student",
      "Third-party components disclosed; IndicSynth is research-only"],
     "Under the hood: a fine-tuned X L S R three-hundred-million detector with RawBoost, and telephony augmentation. Bhashini provides Indic language detection, speech recognition and synthesis, and AIKosh provides corpora and models. E C A P A handles speaker verification and NeMo handles diarization. We add P G D adversarial training and a distilled edge student for cheap phones. All third-party components are disclosed, and IndicSynth is used for research only."),
    ("results", "Evidence", "Results on Indic telephony",
     ["Seen clean E E R: 0.1 to 2 percent  (Odia clean 0.21%)",
      "G.711 mu / A-law E E R: 0.4 to 6 percent  (Odia G.711 0.40%)",
      "English-trained SOTA zero-shot on Indic: 33 to 93 percent E E R",
      "Unseen-generator E E R: 5 to 20 percent (the real gap)",
      "Abstention cuts genuine-caller false alarms 30 to 60 percent"],
     "On our Indic telephony benchmark, seen clean error rates are under two percent, for example Odia at zero-point-two-one percent, and G seven-eleven telephony stays low. English-trained state-of-the-art detectors get thirty-three to ninety-three percent error on Indic when used zero-shot; fine-tuning on Indic cuts that to single digits. On a truly unseen generator, error rises to five to twenty percent, and our calibrated abstention cuts genuine-caller false alarms by thirty to sixty percent."),
    ("guard", "Bharat-first & guardrails", "Safe, private, honest",
     ["23 Indic languages; voice-first; low-bandwidth; edge-ready",
      "Privacy-by-design: on-prem / on-device; no O T P or P I I harvesting",
      "No tips, no buy-sell-hold, no price prediction, no broker promotion",
      "Honest uncertainty: explicit ABSTAIN, never a false binary"],
     "VoxShield is Bharat-first: twenty-three languages, voice-first, low-bandwidth and edge-ready. It is private by design, running on-premise with no harvesting of O T Ps or financial data. It gives no tips, no buy-sell-hold, and no price prediction. And it communicates uncertainty honestly, with an explicit abstain."),
    ("close", "Impact", "Before money moves",
     ["Deploy by banks, brokers, SEBI helplines, I V R, S D K",
      "Scales across languages, cheap phones and Tier-2/3 users",
      "Public-good: investor-protection infrastructure",
      "VoxShield — hear the human behind the call."],
     "VoxShield can be deployed by banks, brokers, S E B I helplines, I V R systems and S D Ks. It scales across languages, cheap phones and tier-two and tier-three users. It is public-good investor-protection infrastructure. VoxShield: hear the human behind the call."),
]

parts = []
for i, (key, kicker, title, lines, narr) in enumerate(scenes):
    png = f"{OUT}/{i:02d}_{key}.png"
    frame(png, kicker, title, lines)
    wav = f"{OUT}/{i:02d}.wav"
    if narr is None:                      # demo scene -> the real Hindi scam clip
        aiff = f"{OUT}/{i:02d}.aiff"; say(SCAM, aiff, voice="Lekha", rate=150); aiff_to_wav(aiff, wav)
    else:
        aiff = f"{OUT}/{i:02d}.aiff"; say(narr, aiff); aiff_to_wav(aiff, wav)
    mp4 = f"{OUT}/{i:02d}.mp4"; clip(png, wav, mp4); parts.append(mp4)
    print("scene", i, key, "ok")

# concat
with open(f"{OUT}/list.txt", "w") as f:
    for p in parts: f.write(f"file '{os.path.abspath(p)}'\n")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt",
                "-c", "copy", "SANGYAN_VoxShield_demo.mp4"],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# duration
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=nk=1:nw=1", "SANGYAN_VoxShield_demo.mp4"],
                   capture_output=True, text=True).stdout.strip()
print(f"wrote SANGYAN_VoxShield_demo.mp4  ({float(d):.1f}s)")
