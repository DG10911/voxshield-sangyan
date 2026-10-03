"""
VoxShield — Voice Identity (roadmap §7, §28).

Separates AUTHENTICITY ("is it human?") from IDENTITY ("is it the claimed person?")
and LIVENESS ("are they present now?"). Provides enroll → verify over the speaker
embedding (speaker.py), and combines identity with an anti-spoof signal (VoxScore)
so a perfect clone of the right person still fails if it's synthetic.

Liveness (challenge-response) is [PENDING] — flagged, never assumed. In-memory
enrollment store (swap for a real DB in production). numpy-only + speaker.py.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional
from speaker import embed, _cos

_ENROLL: Dict[str, np.ndarray] = {}     # speaker_id -> centroid embedding


def enroll(speaker_id: str, clips: List, sr: int) -> dict:
    if not clips:
        return {"ok": False, "reason": "no enrollment audio"}
    embs = [embed(y, sr) for y in clips]
    centroid = np.mean(embs, axis=0); centroid /= (np.linalg.norm(centroid) + 1e-9)
    _ENROLL[speaker_id] = centroid
    # cohesion: how tight the enrollment samples are (quality signal)
    cohesion = float(np.mean([_cos(e, centroid) for e in embs]))
    return {"ok": True, "speaker_id": speaker_id, "n_clips": len(clips), "cohesion": round(cohesion, 3)}


def verify(claimed_id: str, y, sr: int, voxscore: Optional[Dict] = None,
           threshold: float = 0.92) -> dict:   # calibrated for pseudo-embedding; recalibrate for ECAPA
    if claimed_id not in _ENROLL:
        return {"decision": "NO_ENROLLMENT", "reason": f"'{claimed_id}' not enrolled"}
    sim = _cos(embed(y, sr), _ENROLL[claimed_id])
    id_match = sim >= threshold

    # anti-spoof: even a correct-identity voice must be genuine, not synthetic
    synth = None; spoof = False
    if voxscore is not None:
        synth = float(voxscore.get("synthetic_score", voxscore.get("authenticity", {}).get("synthetic", 0.0)))
        spoof = synth >= 0.6 or voxscore.get("abstain", False)

    if not id_match:
        decision = "REJECT_IDENTITY"
    elif spoof:
        decision = "REJECT_SPOOF"          # right voice, but synthetic/abstain
    else:
        decision = "VERIFIED"
    return {"claimed_id": claimed_id, "similarity": round(sim, 4), "identity_match": bool(id_match),
            "anti_spoof_synthetic": None if synth is None else round(synth, 3),
            "liveness": "PENDING",         # challenge-response not built (roadmap)
            "decision": decision,
            "_status": "identity=pseudo-embedding (ECAPA pending); liveness=PENDING; never auto-block on this alone."}


def _selftest():
    from voxscore import voxscore as vscore
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False)
    def voice(f0, forms, seed):
        rng = np.random.default_rng(seed)
        ph = np.cumsum(2*np.pi*(f0 + rng.standard_normal(len(t)))/sr)
        return (sum(np.sin(k*ph)*np.exp(-abs(k*f0-fm)/600) for k in range(1,10) for fm in forms)
                + 0.02*rng.standard_normal(len(t))).astype(np.float32)
    A1, A2, A3 = voice(130,[700,1200,2600],1), voice(131,[710,1210,2610],2), voice(129,[705,1205,2605],3)
    B = voice(210,[500,1800,3000],9)
    print("enroll A:", enroll("alice", [A1, A2], sr))
    genuine_vs = vscore({"acoustic-dsp":0.1,"neural:xls-r":0.08})    # genuine
    spoof_vs   = vscore({"acoustic-dsp":0.9,"neural:xls-r":0.93})    # synthetic
    print("A genuine :", verify("alice", A3, sr, genuine_vs)["decision"])
    print("A cloned  :", verify("alice", A3, sr, spoof_vs)["decision"])   # right id, but synthetic
    print("B as alice:", verify("alice", B, sr, genuine_vs)["decision"])
    assert verify("alice", A3, sr, genuine_vs)["decision"] == "VERIFIED"
    assert verify("alice", A3, sr, spoof_vs)["decision"] == "REJECT_SPOOF"
    assert verify("alice", B, sr, genuine_vs)["decision"] == "REJECT_IDENTITY"
    print("\n[selftest] PASS — genuine+match=VERIFIED; match+synthetic=REJECT_SPOOF; wrong voice=REJECT_IDENTITY.")


if __name__ == "__main__":
    _selftest()
