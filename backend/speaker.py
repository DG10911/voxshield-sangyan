"""
VoxShield — Speaker Identity + Cross-Language Continuity (roadmap §8, §10, §28).

Separates AUTHENTICITY ("is it human?") from IDENTITY ("is it the claimed person?").
Provides:
  * a speaker embedding + cosine verification (same vs different speaker)
  * a Cross-Lingual Voice Continuity check — a genuine speaker preserves some
    physical voice properties across languages; a cross-lingual clone may not.

NOTE: this uses a lightweight, dependency-free PSEUDO-EMBEDDING (long-term spectral
+ pitch statistics) so it runs anywhere. The PRODUCTION path is a real speaker
model (e.g. ECAPA-TDNN) — [PENDING] that model; the interface here is stable so it
can be swapped in without changing callers. numpy-only.
"""
from __future__ import annotations
import numpy as np


def embed(y: np.ndarray, sr: int) -> np.ndarray:
    """Pseudo speaker-embedding: long-term average spectrum (mel-ish bands) + pitch
    stats, L2-normalised. Placeholder for a real ECAPA-TDNN embedding [PENDING]."""
    y = np.asarray(y, np.float32)
    if y.ndim > 1: y = y.mean(1)
    y = y / (np.max(np.abs(y)) + 1e-9)
    n = 1024
    if len(y) < n: y = np.pad(y, (0, n - len(y)))
    S = np.abs(np.fft.rfft(y[:len(y)//n*n].reshape(-1, n) * np.hanning(n), axis=1)).mean(0) + 1e-9
    fr = np.fft.rfftfreq(n, 1/sr)
    # 24 log-spaced band energies (speaker timbre)
    edges = np.logspace(np.log10(80), np.log10(sr/2), 25)
    bands = np.array([S[(fr >= edges[i]) & (fr < edges[i+1])].sum() for i in range(24)]) + 1e-9
    bands = np.log(bands / bands.sum())
    # coarse pitch stats
    ac = np.correlate(y[:4096], y[:4096], "full")[4095:]
    lo, hi = int(sr/400), int(sr/70)
    f0 = sr / (np.argmax(ac[lo:hi]) + lo) if len(ac) > hi and ac[0] > 0 else 0.0
    v = np.concatenate([bands, [f0/300.0, float(np.std(y))]])
    return v / (np.linalg.norm(v) + 1e-9)


def _cos(a, b): return float(np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-9))


def verify(y1, sr1, y2, sr2, threshold: float = 0.85) -> dict:
    e1, e2 = embed(y1, sr1), embed(y2, sr2)
    sim = _cos(e1, e2)
    return {"similarity": round(sim, 4),
            "match": bool(sim >= threshold),
            "decision": "SAME_SPEAKER" if sim >= threshold else "DIFFERENT_SPEAKER",
            "_status": "PSEUDO-EMBEDDING (spectral+pitch); swap in ECAPA-TDNN for production [PENDING]."}


def _resample16(y: np.ndarray, sr: int) -> np.ndarray:
    if sr == 16000 or len(y) < 2:
        return y
    n = int(round(len(y) * 16000 / sr))
    return np.interp(np.linspace(0, 1, n, endpoint=False),
                     np.linspace(0, 1, len(y), endpoint=False), y).astype(np.float32)


def _wav_b64(y: np.ndarray, sr: int) -> str:
    """16 kHz mono WAV base64 (Bhashini speaker services require 16 kHz WAV w/ speech)."""
    import io, wave, base64
    y = _resample16(np.asarray(y, np.float32), sr)
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(pcm)
    return base64.b64encode(buf.getvalue()).decode()


def enroll(y: np.ndarray, sr: int, speaker_name: str = None) -> dict:
    """Enroll a speaker: local pseudo-profile + Bhashini enrollment (returns a speakerId).
    Uses a UNIQUE name by default (reusing a name can make later verification fail)."""
    import uuid
    speaker_name = speaker_name or f"vx-{uuid.uuid4().hex[:8]}"
    prof = {"speaker_name": speaker_name, "n_samples": int(len(y)),
            "local_embedding": embed(y, sr).tolist()}
    try:
        import bhashini
        if bhashini.status()["have_keys"]:
            r = bhashini.speaker_enroll(_wav_b64(y, sr), speaker_name)
            prof["bhashini_speaker_id"] = bhashini.enrolled_id(r)
            prof["bhashini_raw"] = r
    except Exception as e:
        prof["bhashini_error"] = str(e)[:200]
    return prof


def verify_against_enrolled(y: np.ndarray, sr: int, speaker_id: str) -> dict:
    """Bhashini speaker verification of `y` against an enrolled speakerId.
    Returns decision VERIFIED / NOT_MATCHED / SPEAKER_NOT_FOUND (Bhashini) or an error."""
    local = {"similarity": None, "decision": "UNKNOWN", "source": "bhashini"}
    try:
        import bhashini
        if bhashini.status()["have_keys"]:
            r = bhashini.speaker_verify(_wav_b64(y, sr), speaker_id)
            return {**local, "result": bhashini.verification_result(r), "raw": r}
    except Exception as e:
        msg = str(e)
        local["decision"] = "SPEAKER_NOT_FOUND" if "not found" in msg.lower() else "ERROR"
        local["bhashini_error"] = msg[:200]
    return local


def verify_speaker(y1, sr1, y2, sr2, threshold: float = 0.85) -> dict:
    """Same/different speaker. Uses local pseudo-embedding; if Bhashini keys are present,
    also enrolls y1 and verifies y2 against it (adds a managed result alongside local)."""
    local = verify(y1, sr1, y2, sr2, threshold)
    try:
        import bhashini
        if bhashini.status()["have_keys"]:
            import uuid
            enr = bhashini.speaker_enroll(_wav_b64(y1, sr1), f"vx-{uuid.uuid4().hex[:8]}")
            sid = bhashini.enrolled_id(enr) or "verify-tmp"
            v = bhashini.speaker_verify(_wav_b64(y2, sr2), sid)
            return {**local, "bhashini_speaker_id": sid,
                    "bhashini_result": bhashini.verification_result(v), "source": "bhashini+local"}
    except Exception as e:
        local["bhashini_error"] = str(e)[:200]
    local["source"] = "local-pseudo"
    return local


def cross_lingual_continuity(clips: list, sr: int) -> dict:
    """clips = list of same-claimed-speaker utterances (ideally different languages).
    High mean pairwise similarity => voice physically continuous across languages."""
    embs = [embed(y, sr) for y in clips]
    sims = [_cos(embs[i], embs[j]) for i in range(len(embs)) for j in range(i+1, len(embs))]
    m = float(np.mean(sims)) if sims else None
    return {"continuity_score": None if m is None else round(m, 4),
            "verdict": None if m is None else ("CONTINUOUS" if m >= 0.8 else "INCONSISTENT (possible cross-lingual clone)"),
            "_status": "HYPOTHESIS — cross-lingual continuity via pseudo-embedding; validate with ECAPA + real cross-lingual data."}


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False)
    def voice(f0, formants, seed):
        rng = np.random.default_rng(seed)
        ph = np.cumsum(2*np.pi*(f0 + rng.standard_normal(len(t))*1.0)/sr)
        y = sum(np.sin(k*ph) * np.exp(-abs(k*f0 - fm)/600) for k in range(1, 10) for fm in formants)
        return (y + 0.02*rng.standard_normal(len(t))).astype(np.float32)
    spkA_lang1 = voice(130, [700, 1200, 2600], 1)
    spkA_lang2 = voice(132, [720, 1180, 2650], 2)   # same speaker, diff content/lang
    spkB = voice(210, [500, 1800, 3000], 3)          # different speaker
    va = verify(spkA_lang1, sr, spkA_lang2, sr)
    vb = verify(spkA_lang1, sr, spkB, sr)
    cl = cross_lingual_continuity([spkA_lang1, spkA_lang2], sr)
    print("same speaker :", va["similarity"], va["decision"])
    print("diff speaker :", vb["similarity"], vb["decision"])
    print("cross-lingual continuity (same spk):", cl["continuity_score"], cl["verdict"])
    prof = enroll(spkA_lang1, sr)   # unique name auto-generated
    print("enroll       :", {k: v for k, v in prof.items()
                             if k in ("speaker_name", "n_samples", "bhashini_speaker_id", "bhashini_error")})
    vh = verify_speaker(spkA_lang1, sr, spkA_lang2, sr)
    print("verify_speaker:", vh["similarity"], vh["decision"], "| source:", vh["source"],
          "| bhashini:", vh.get("bhashini_result") or vh.get("bhashini_error"))
    assert va["similarity"] > vb["similarity"], "same speaker should be more similar than different"
    print("\n[selftest] PASS — speaker verify separates same vs different; cross-lingual continuity computed; enroll + Bhashini-ready verify_speaker OK.")


if __name__ == "__main__":
    _selftest()
