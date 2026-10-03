#!/usr/bin/env python3
"""
Bhashini LIVE test harness — exercises every implemented service once and prints a table.
Usage: BHASHINI_* env set, then  python backend/bhashini_livetest.py
Uses ~12 of the account's 2,000 calls. Services needing an image (OCR) are skipped unless
--image <path> is passed. Streaming ASR runs only if `websockets` is installed.
"""
from __future__ import annotations
import os, sys, io, base64, wave, argparse, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bhashini as B

try:
    import numpy as np
except Exception:
    np = None


def tts_clip(text="नमस्ते, मैं बैंक से बोल रहा हूँ।", lang="hi", gender="female"):
    r = B.synthesize(text, lang, gender)
    return r["pipelineResponse"][0]["audio"][0]["audioContent"]


def resample16(b64):
    raw = base64.b64decode(b64)
    with wave.open(io.BytesIO(raw)) as w:
        sr, n = w.getframerate(), w.getnframes()
        y = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    m = int(len(y) * 16000 / sr)
    y16 = np.interp(np.linspace(0, 1, m, endpoint=False), np.linspace(0, 1, len(y), endpoint=False), y)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((np.clip(y16, -1, 1) * 32767).astype("<i2").tobytes())
    return base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--image", default=None); a = ap.parse_args()
    if not B.status()["have_keys"]:
        print("!! set BHASHINI_USER_ID/BHASHINI_API_KEY/BHASHINI_INFERENCE_KEY first"); return 1
    print("quota before:", B.quota_status())
    results = []

    def run(name, fn):
        try:
            r = fn(); ok = True; note = str(r)[:120]
        except Exception as e:
            ok = False; note = f"{type(e).__name__}: {str(e)[:120]}"
        results.append((name, "OK" if ok else "FAIL", note)); print(f"[{'OK' if ok else 'FAIL'}] {name}: {note[:100]}")

    print("\n== running live services ==")
    run("config", lambda: (B.config([{"taskType": "asr"}]).get("pipelineResponseConfig") and "pipeline ok"))
    run("nmt(en->hi)", lambda: B.translate("Good morning, this is your bank.", "en", "hi"))
    run("transliteration(en->hi)", lambda: B.transliterate("ki", "en", "hi"))
    run("ner(hi)", lambda: B.ner("नरेंद्र मोदी दिल्ली में रहते हैं", "hi"))
    run("tld(hi)", lambda: B.detect_text_language("नमस्ते दुनिया"))
    clip = tts_clip()
    run("tts(hi)", lambda: {"len": len(clip)})
    clip16 = resample16(clip)
    run("asr(hi)", lambda: B.asr(clip16, "hi"))
    run("ald", lambda: B.detect_audio_language(clip16))
    run("speaker_diarization", lambda: B.diarize_speakers(clip16))
    run("language_diarization", lambda: B.diarize_languages(clip16))
    run("denoiser", lambda: B.denoise(clip16))
    run("voice_clone(indicf5)", lambda: B.voice_clone("नमस्ते", "नमस्ते, मैं बैंक से बोल रहा हूँ।", clip16, "hi"))
    if a.image:
        run("ocr", lambda: B.ocr(a.image, "hi"))
    else:
        results.append(("ocr", "SKIP", "pass --image <path>"))
    try:
        import websockets  # noqa
        run("stream_asr", lambda: B.stream_asr(base64.b64decode(clip16), 16000, "hi"))
    except Exception:
        results.append(("stream_asr", "SKIP", "pip install websockets"))

    print("\n== summary ==")
    for n, s, _ in results:
        print(f"  {s:5} {n}")
    print("\nquota after:", B.quota_status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
