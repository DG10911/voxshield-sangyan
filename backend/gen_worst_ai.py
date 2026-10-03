#!/usr/bin/env python3
"""
VoxShield — Worst-AI generator (roadmap §16, §27, §37.3).

Text -> [optional NMT to an Indic language] -> [Bhashini TTS or IndicF5 voice-clone]
     -> [telephony G.711 / nightmare channel render] -> WAV + manifest line.

Uses the LIVE Bhashini API for synthesis/translation and scenario_render.py for the
channel (μ-law, band-limit, noise, packet-loss, reverb, replay). This manufactures
Worst-AI attack clips to attack/train the detector.

Examples:
  python gen_worst_ai.py --text "आपका बैंक खाता बंद हो जाएगा" --lang hi --telephony
  python gen_worst_ai.py --text "transfer the money now" --nmt-from en --lang ta --nightmare
  python gen_worst_ai.py --text "..." --lang hi --ref-audio speaker.wav   # voice-clone attempt
"""
from __future__ import annotations
import argparse, base64, io, json, os, sys, wave, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bhashini as B
from scenario_render import render, nightmare_scenario


def _decode_wav(b64: str):
    raw = base64.b64decode(b64)
    with wave.open(io.BytesIO(raw)) as w:
        sr, n = w.getframerate(), w.getnframes()
        y = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    return y, sr


def _write_wav(path, y, sr):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(sr))
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())


def generate(text, lang="hi", nmt_from=None, gender="female", ref_audio=None,
             telephony=False, nightmare=False, out="worst_ai_out",
             ref_text=None, translit=None) -> dict:
    os.makedirs(out, exist_ok=True)
    model, attack = "bhashini/tts", "tts"
    if nmt_from:
        try:
            t = B.translate(text, nmt_from, lang)
            text = t["pipelineResponse"][0]["output"][0]["target"]
        except Exception as e:
            print("NMT failed, using original text:", str(e)[:80])
    if translit:  # (source_script_lang, target_script_lang) e.g. ("en","hi")
        try:
            t = B.transliterate(text, translit[0], translit[1])
            text = t["pipelineResponse"][0]["output"][0].get("target") or text
        except Exception as e:
            print("transliteration failed:", str(e)[:80])
    b64 = None
    if ref_audio and os.path.exists(ref_audio):
        try:
            ref_b64 = base64.b64encode(open(ref_audio, "rb").read()).decode()
            rt = ref_text
            if not rt:  # auto-transcribe the reference for IndicF5
                a = B.asr(ref_b64, lang)
                rt = a["pipelineResponse"][0]["output"][0].get("source")
            r = B.voice_clone(text, rt or "", ref_b64, lang)
            b64 = r["audio"][0]["audioContent"]        # flat voice-cloning endpoint shape
            model, attack = "bhashini/ai4b/indicf5-tts", "voice_cloning"
        except Exception as e:
            print("voice-clone failed, using TTS:", str(e)[:120])
    if not b64:
        r = B.synthesize(text, lang, gender)
        b64 = r["pipelineResponse"][0]["audio"][0]["audioContent"]
        if attack == "tts":
            model = "bhashini/tts"
    y, sr = _decode_wav(b64)
    steps = []
    if telephony:
        o = render(y, sr, {"codec": "g711_ulaw", "narrowband": True, "snr_db": 15, "seed": 0})
        y, steps = o["audio"], o["steps"]
    if nightmare:
        o = render(y, sr, nightmare_scenario()); y = o["audio"]; steps += o["steps"]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"worstai_{lang}_{attack}_{ts}.wav"; path = os.path.join(out, name)
    _write_wav(path, y, sr)
    man = {"sample_id": name, "language": lang, "text": text, "generator": model,
           "attack_mode": attack, "steps": steps, "path": path, "sample_rate": sr,
           "provenance": f"bhashini/{lang}", "license": "generated",
           "consent": "internal-generated", "label": "AI_GENERATED"}
    with open(os.path.join(out, "manifest.jsonl"), "a") as f:
        f.write(json.dumps(man, ensure_ascii=False) + "\n")
    print(f"wrote {path} ({len(y)/sr:.2f}s @ {sr}Hz) steps={steps}")
    return man


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--lang", default="hi")
    ap.add_argument("--nmt-from", default=None)
    ap.add_argument("--gender", default="female")
    ap.add_argument("--ref-audio", default=None)
    ap.add_argument("--ref-text", default=None, help="transcript of --ref-audio (auto-ASR if omitted)")
    ap.add_argument("--translit", nargs=2, metavar=("SRC", "TGT"), default=None,
                    help="transliterate text between script languages, e.g. --translit en hi")
    ap.add_argument("--telephony", action="store_true")
    ap.add_argument("--nightmare", action="store_true")
    ap.add_argument("--out", default="worst_ai_out")
    a = ap.parse_args()
    generate(a.text, a.lang, a.nmt_from, a.gender, a.ref_audio, a.telephony, a.nightmare, a.out,
             ref_text=a.ref_text, translit=a.translit)


if __name__ == "__main__":
    main()
