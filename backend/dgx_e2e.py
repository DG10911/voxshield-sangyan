#!/usr/bin/env python3
"""
VoxShield — DGX end-to-end on one call (roadmap §3): profile → Bhashini ALD+ASR →
NeMo/pyannote diarization → ECAPA speaker verify → fusion verdict.

Usage:
  python backend/dgx_e2e.py call.wav
  python backend/dgx_e2e.py call.wav --enroll ref_speaker.wav   # also verify caller vs a known voice
  python backend/dgx_e2e.py call.wav --probs '{"xls-r":0.9,"acoustic-dsp":0.8}'
Env: BHASHINI_* (ALD/ASR), optionally DEEPGRAM_API_KEY (diarization fallback), HF_TOKEN.
"""
from __future__ import annotations
import argparse, json, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np


def load(path):
    with wave.open(path) as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        y = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
        if ch > 1: y = y.reshape(-1, ch).mean(1)
    if sr != 16000:
        m = int(len(y) * 16000 / sr)
        y = np.interp(np.linspace(0, 1, m, endpoint=False), np.linspace(0, 1, len(y), endpoint=False), y)
    return y.astype(np.float32), 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--enroll", default=None)
    ap.add_argument("--probs", default=None)
    a = ap.parse_args()

    import orchestrate
    y, sr = load(a.wav)
    probs = json.loads(a.probs) if a.probs else None
    print(f"audio: {a.wav}  ({len(y)/sr:.2f}s @16k)")

    r = orchestrate.run(y, sr, detector_probs=probs, deep_on_lowrisk=True,
                        use_bhashini=True, use_diarization=True)
    prof = r.get("profile", {}); bh = r.get("bhashini") or {}
    print("\n================= VOXSHIELD =================")
    print(" pipeline   :", " → ".join(r["pipeline"]))
    print(" language   :", prof.get("language"), "(Bhashini ALD)")
    print(" transcript :", (bh.get("transcript") or "")[:200])
    d = r.get("diarization") or {}
    print(" diarization:", d.get("backend"), "| speakers:", d.get("n_speakers"),
          "| segments:", len(d.get("segments", [])))
    cb = (r.get("brains") or {}).get("conversational")
    if cb: print(" transcript-forensics:", cb.get("verdict"), "scripted_lean", cb.get("scripted_lean"))
    print(" verdict    :", r.get("verdict"), "| abstain:", r.get("abstain"))
    if r.get("arbitration"): print(" arbitration:", {k: r["arbitration"].get(k) for k in ("decision", "abstain", "synthetic")})

    if a.enroll:
        try:
            from speaker_engine import enroll, verify_against
            ref, _ = load(a.enroll)
            prof_spk = enroll(ref, sr)
            # verify the first diarized segment against the enrolled voice
            segs = d.get("segments", [])
            if segs:
                s = segs[0]; seg = y[int(s["start"]*sr):int(s["end"]*sr)]
                v = verify_against(prof_spk, seg, sr)
                print(" speaker    :", v["decision"], v["similarity"], "vs enrolled (", v["backend"], ")")
        except Exception as e:
            print(" speaker err:", str(e)[:160])
    print("=============================================")


if __name__ == "__main__":
    main()
