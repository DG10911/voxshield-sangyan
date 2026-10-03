#!/usr/bin/env python3
"""
VoxShield — end-to-end telephony demo with LIVE Bhashini (roadmap §3, §27).

No real/consented telephony clip is bundled, so this builds one honestly:
  Bhashini TTS (Hindi) -> scenario_render G.711 μ-law + band-limit + noise (8 kHz).
Then runs the unified pipeline `orchestrate.run(..., use_bhashini=True)` and prints the
Bhashini ALD language + ASR transcript alongside the evidence/verdict.

Detector probabilities are injected to keep the demo fast/offline (the real fusion bank
runs on the DGX); ALD+ASR are LIVE Bhashini calls.
"""
from __future__ import annotations
import os, sys, wave, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np


def load_wav(path):
    with wave.open(path) as w:
        sr, n = w.getframerate(), w.getnframes()
        y = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    return y, sr


def resample(y, sr, target=8000):
    if sr == target: return y, target
    n = int(round(len(y) * target / sr))
    return np.interp(np.linspace(0, 1, n, endpoint=False),
                     np.linspace(0, 1, len(y), endpoint=False), y).astype(np.float32), target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="नमस्ते, मैं आपके बैंक से बोल रहा हूँ, कृपया अपना ओटीपी बताइए।")
    ap.add_argument("--lang", default="hi")
    ap.add_argument("--out", default="/tmp/voxshield_demo")
    a = ap.parse_args()

    import gen_worst_ai, orchestrate
    print("1) generating telephony clip (Bhashini TTS -> G.711 8k) …")
    man = gen_worst_ai.generate(a.text, a.lang, telephony=True, out=a.out)
    y48, sr48 = load_wav(man["path"])
    y8, sr8 = resample(y48, sr48, 8000)            # telephony 8 kHz
    print(f"   clip: {man['path']}  ({len(y8)/sr8:.2f}s @ {sr8} Hz) steps={man['steps']}")

    print("2) running orchestrate.run(..., use_bhashini=True) …")
    probs = {"acoustic-dsp": 0.72, "neural:xls-r": 0.79, "neural:distilhubert": 0.68}  # injected (demo)
    r = orchestrate.run(y8, sr8, detector_probs=probs, deep_on_lowrisk=True, use_bhashini=True)

    print("\n================= VERDICT =================")
    print("  pipeline     :", " -> ".join(r["pipeline"]))
    print("  profiler     :", r["profile"]["codec_hint"], "| narrowband:", r["profile"]["narrowband"])
    print("  language     :", r["profile"].get("language"), "(Bhashini ALD)" if r["profile"].get("language") else "")
    bh = r.get("bhashini") or {}
    print("  transcript   :", bh.get("transcript"))
    print("  unified      :", r.get("verdict"), "| abstain:", r.get("abstain"))
    if r.get("arbitration"):
        print("  arbitration  :", {k: r["arbitration"].get(k) for k in ("decision", "abstain", "synthetic")})
    print("==========================================\n")


if __name__ == "__main__":
    main()
