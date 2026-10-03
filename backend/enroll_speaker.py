#!/usr/bin/env python3
"""
Enroll a REAL consented voice with Bhashini (IIT Dharwad) and store the speakerId.
Usage:  python backend/enroll_speaker.py --audio my_voice.wav --name "Devansh"
Notes:  WAV, 16 kHz mono, speech, ~3-10 s. TTS-synthesized audio does NOT verify —
        use a real recording. The speakerId is saved to ~/.config/voxshield_speakers.json.
"""
from __future__ import annotations
import argparse, base64, io, json, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bhashini as B

STORE = os.path.expanduser("~/.config/voxshield_speakers.json")


def load_wav16(path):
    with wave.open(path) as w:
        sr, n = w.getframerate(), w.getnframes()
        y = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    if sr != 16000:
        m = int(len(y) * 16000 / sr)
        y = np.interp(np.linspace(0, 1, m, endpoint=False), np.linspace(0, 1, len(y), endpoint=False), y)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    return base64.b64encode(buf.getvalue()).decode(), len(y) / 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    if not B.status()["have_keys"]:
        print("!! set BHASHINI_* env first"); return 1
    b64, dur = load_wav16(a.audio)
    print(f"enrolling {a.name} from {a.audio} ({dur:.2f}s @16k) …")
    r = B.speaker_enroll(b64, a.name)
    sid = B.enrolled_id(r)
    print("speakerId:", sid)
    if sid:
        db = json.load(open(STORE)) if os.path.exists(STORE) else {}
        db[a.name] = {"speaker_id": sid, "audio": os.path.abspath(a.audio), "duration_s": round(dur, 2)}
        os.makedirs(os.path.dirname(STORE), exist_ok=True); json.dump(db, open(STORE, "w"), indent=1)
        print("saved to", STORE)
        # immediate self-verify (real speech should match)
        v = B.speaker_verify(b64, sid)
        print("verify self:", B.verification_result(v) or v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
