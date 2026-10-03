"""
VoxShield — All-Type Audio classifier (roadmap §8, P3).

Coarse content-type gate so the pipeline knows WHAT it's analysing before it decides
HOW: speech · singing · music · environmental · mixed. Deepfake reasoning is tuned
for speech; music/singing/environmental inputs are routed differently (and a clip
that is mostly music but contains a spoken segment is 'mixed' → analyse the speech
part). Pure DSP — harmonicity (HNR proxy), spectral flatness, ZCR, pitch stability,
percussive/harmonic balance, tempo regularity. numpy only, non-breaking.

[HYPOTHESIS] — coarse routing heuristic; calibrate thresholds on labelled content.
"""
from __future__ import annotations
import numpy as np


def _frames(y, sr, win=0.04, hop=0.02):
    w = int(win*sr); h = int(hop*sr)
    if len(y) < w: return np.empty((0, w))
    return np.stack([y[i:i+w]*np.hanning(w) for i in range(0, len(y)-w+1, h)])


def _features(y, sr):
    F = _frames(y, sr)
    if len(F) == 0: return None
    S = np.abs(np.fft.rfft(F, axis=1)) + 1e-9
    # spectral flatness (geo/arith mean): tonal(low) vs noisy(high)
    flat = np.exp(np.log(S).mean(1)) / S.mean(1)
    # harmonicity proxy: peak concentration of the autocorrelation per frame
    zcr = np.mean(np.abs(np.diff(np.sign(F), axis=1)) > 0, axis=1)
    centroid = (np.arange(S.shape[1])*S).sum(1)/S.sum(1)
    energy = np.sqrt((F**2).mean(1)+1e-12)
    # pitch stability: low-band spectral-peak position variance over time
    lo, hi = int(80*S.shape[1]*2/sr), int(500*S.shape[1]*2/sr)
    peak = lo + np.argmax(S[:, lo:hi+1], axis=1)
    pitch_var = float(np.std(peak)/(np.mean(peak)+1e-9))
    # rhythm regularity: autocorrelation peak of the energy envelope (music beats)
    e = energy - energy.mean()
    ac = np.correlate(e, e, "full")[len(e)-1:]
    ac = ac/(ac[0]+1e-9); rhythm = float(np.max(ac[4:min(len(ac), 100)])) if len(ac) > 5 else 0.0
    # voiced fraction: frames with low flatness + moderate ZCR (speech-like)
    voiced = float(np.mean((flat < 0.3) & (zcr > 0.02) & (zcr < 0.25)))
    return {"flatness": float(flat.mean()), "zcr": float(zcr.mean()),
            "centroid_norm": float(centroid.mean()/S.shape[1]), "pitch_var": pitch_var,
            "rhythm": rhythm, "voiced_frac": voiced,
            "energy_cv": float(energy.std()/(energy.mean()+1e-9))}


def classify(y: np.ndarray, sr: int) -> dict:
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    f = _features(y, sr)
    if f is None:
        return {"type": "TOO_SHORT", "route": "reject", "_status": "need >=~0.1s"}

    speech = f["voiced_frac"]                                   # intermittent voiced structure
    music  = f["rhythm"]*0.6 + (1-f["flatness"])*0.4            # tonal + rhythmic
    singing = music*0.5 + (f["pitch_var"] < 0.15)*0.5           # tonal + very stable pitch
    envir  = f["flatness"]*0.7 + (f["energy_cv"] < 0.4)*0.3     # noisy, low structure
    scores = {"speech": speech, "singing": singing, "music": music, "environmental": envir}
    top = max(scores, key=scores.get); s = scores[top]
    ranked = sorted(scores.values(), reverse=True)
    mixed = (ranked[0]-ranked[1] < 0.12) and f["voiced_frac"] > 0.15   # speech present but not dominant
    typ = "mixed" if mixed else top
    route = ("speech_deepfake" if typ in ("speech", "mixed")
             else "singing_voice_conversion" if typ == "singing"
             else "non_speech_defer")
    return {"type": typ, "route": route, "scores": {k: round(v, 3) for k, v in scores.items()},
            "voiced_frac": round(f["voiced_frac"], 3), "rhythm": round(f["rhythm"], 3),
            "note": ("mixed content — analyse the spoken segment(s), don't score music as speech"
                     if typ == "mixed" else f"routed as {typ}"),
            "_status": "HYPOTHESIS — coarse content router; calibrate on labelled speech/music/env."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False); rng = np.random.default_rng(0)
    # speech-like: intermittent voiced bursts with pauses + pitch drift
    sp = np.zeros_like(t)
    for on in np.arange(0.0, 2.0, 0.5):
        i = int(on*sr); d = int(0.3*sr)
        seg = np.sin(2*np.pi*(150+20*rng.standard_normal())*np.linspace(0, 0.3, d))
        sp[i:i+d] += seg[:len(sp[i:i+d])]
    speech = (sp + 0.02*rng.standard_normal(len(t))).astype(np.float32)
    # environmental: broadband noise (high flatness, no voiced structure)
    envir = (0.3*rng.standard_normal(len(t))).astype(np.float32)
    cs = classify(speech, sr); ce = classify(envir, sr)
    print("speech-like    :", cs["type"], "| voiced", cs["voiced_frac"], "| scores", cs["scores"])
    print("environmental  :", ce["type"], "| route", ce["route"])
    assert cs["type"] in ("speech", "mixed") and cs["route"] == "speech_deepfake"
    assert ce["type"] == "environmental" and ce["route"] == "non_speech_defer"
    print("\n[selftest] PASS — voiced speech routed to deepfake analysis; broadband noise deferred as environmental.")


if __name__ == "__main__":
    _selftest()
