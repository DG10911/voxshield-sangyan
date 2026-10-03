"""
VoxShield — Orchestrator: the unified pipeline (roadmap §3, §100).

Ties the pieces into ONE coherent flow, exactly as the master architecture describes:

    audio → Universal Profiler → Fast L0 (fast-pass low-risk)
          → [evidence brains: physics · replay · environment]
          → detector bank (per_model probs — from System-A fusion when available)
          → VoxScore (authenticity + open-set novelty + abstain)
          → Evidence Arbitration (family-diverse) + brains
          → [optional] CallGuard (voice+context fraud fusion)
          → unified verdict + all evidence

Runs the LOCAL modules on a waveform. Detector probabilities are injected (from
fusion.analyze on the DGX/server); if absent, the flow still returns profiler + L0 +
physics/replay/environment evidence. Non-breaking; numpy + local modules only.
"""
from __future__ import annotations
import io, os, wave, base64
import numpy as np
from typing import Dict, Optional

from profiler import profile
from fast_l0 import screen
from physics import human_physics
from replay import replay_score
from environment import environment
from reverse_time import forward_reverse
from temporal_dna import temporal_dna
from voxscore import voxscore
from arbitration import arbitrate
import bhashini


def _resample(y: np.ndarray, sr: int, target: int = 16000) -> np.ndarray:
    if sr == target or len(y) < 2:
        return y
    n = int(round(len(y) * target / sr))
    xp = np.linspace(0, 1, len(y), endpoint=False)
    x = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x, xp, y).astype(np.float32)


def _wav_b64(y: np.ndarray, sr: int) -> str:
    """Encode a waveform to 16 kHz 16-bit mono WAV base64 (what Bhashini ASR/ALD expect)."""
    if sr != 16000:
        y = _resample(y, sr, 16000)
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(pcm)
    return base64.b64encode(buf.getvalue()).decode()


def _ald_lang(resp: Dict) -> Optional[str]:
    try:
        out = resp.get("pipelineResponse", [{}])[0]["output"][0]["langPrediction"][0]
        return out.get("langCode")
    except Exception:
        try:
            return resp["output"][0].get("langCode")          # MOCK shape
        except Exception:
            return None


def _asr_text(resp: Dict) -> Optional[str]:
    try:
        return resp.get("pipelineResponse", [{}])[0]["output"][0]["source"]
    except Exception:
        try:
            return resp["output"][0].get("source")
        except Exception:
            return None


def bhashini_enrich(y: np.ndarray, sr: int, prof: Dict) -> Dict:
    """Optional Bhashini ALD + ASR enrichment (language routing + transcription evidence).
    No-op if keys are absent. Never raises — returns {'enabled': False} on any failure."""
    if not bhashini.status()["have_keys"]:
        return {"enabled": False, "_note": "set BHASHINI_USER_ID/BHASHINI_API_KEY/BHASHINI_INFERENCE_KEY"}
    try:
        b64 = _wav_b64(y, sr)
        ald = bhashini.detect_audio_language(b64)
        lang = _ald_lang(ald)
        if lang:
            prof["language"] = lang
            prof["language_source"] = "bhashini-ald"
        asr = bhashini.asr(b64, lang or "hi")
        txt = _asr_text(asr)
        return {"enabled": True, "mode": bhashini.status()["mode"], "ald_language": lang,
                "transcript": txt, "ald_raw": ald, "asr_raw": asr}
    except Exception as e:  # keep the pipeline alive if the API is down / quota exhausted
        return {"enabled": True, "error": str(e)[:300]}


def run(y: np.ndarray, sr: int,
        detector_probs: Optional[Dict[str, float]] = None,
        context: Optional[Dict] = None,
        deep_on_lowrisk: bool = False,
        use_bhashini: Optional[bool] = None,
        use_diarization: bool = False) -> Dict:
    if use_bhashini is None:                       # None => auto (BHASHINI_ALWAYS=1 enables)
        use_bhashini = os.environ.get("BHASHINI_ALWAYS") == "1"
    y = np.asarray(y, np.float32)
    result: Dict = {"pipeline": []}

    # 1) profile
    prof = profile(y, sr); result["profile"] = prof; result["pipeline"].append("profiler")

    # 2) fast L0 gate
    l0 = screen(y, sr); result["l0"] = {"decision": l0["decision"], "proxy": l0.get("proxy")}
    result["pipeline"].append("fast_l0")
    if not l0["escalate"] and not deep_on_lowrisk:
        result["verdict"] = "LOW_RISK_FAST_PASS"
        result["note"] = "L0 fast-passed as low-risk; detector bank not invoked (compute saved)."
        return result

    # 3) evidence brains (physical plausibility, replay, environment, time-arrow, trajectory)
    phys = human_physics(y, sr); rep = replay_score(y, sr); env = environment(y, sr)
    rev = forward_reverse(y, sr); dna = temporal_dna(y, sr)
    result["brains"] = {"human_physics": phys, "replay": rep, "environment": env,
                        "reverse_time": rev, "temporal_dna": dna}
    result["pipeline"].append("brains")

    # 3b) optional Bhashini enrichment: ALD -> language routing, ASR -> transcript evidence
    if use_bhashini:
        bh = bhashini_enrich(y, sr, prof)
        result["bhashini"] = bh
        result["pipeline"].append("bhashini(ald+asr)" if bh.get("enabled") else "bhashini(skipped)")
        tr = (bh or {}).get("transcript")
        if tr:                                  # consume transcript as conversational evidence (§9/§10)
            try:
                from conversational import text_forensics
                result.setdefault("brains", {})["conversational"] = text_forensics(tr)
                result["pipeline"].append("conversational(transcript)")
            except Exception:
                pass

    # 3c) provider-agnostic speaker diarization (pyannote / NeMo / built-in)
    if use_diarization:
        try:
            from diarization import diarize as _diar
            d = _diar(y, sr)
            prof["speakers"] = d.get("n_speakers", prof.get("speakers", 1)) or prof.get("speakers", 1)
            result["diarization"] = d
            result["pipeline"].append("diarization(%s)" % d.get("backend"))
        except Exception as e:
            result["diarization"] = {"error": str(e)[:160]}

    # 4) detector bank -> VoxScore (open-set / abstain)
    if detector_probs:
        vs = voxscore(detector_probs)
        result["voxscore"] = vs
        result["pipeline"].append("detectors+voxscore")

        # 5) evidence arbitration across families (SSL from detectors + physics + replay + env)
        brains = [{"name": "ssl", "family": "ssl", "score": vs["synthetic_score"], "confidence": vs["evidence_confidence"]},
                  {"name": "physics", "family": "physics", "score": 1 - phys["hpcs"], "confidence": 0.6},
                  {"name": "replay", "family": "replay", "score": rep["replay_score"], "confidence": 0.5},
                  {"name": "environment", "family": "environment",
                   "score": 1 - (env.get("svcs") or 0.5), "confidence": 0.4},
                  {"name": "reverse_time", "family": "physics", "score": rev.get("synthetic_lean") or 0.5, "confidence": 0.3},
                  {"name": "temporal_dna", "family": "temporal", "score": dna.get("synthetic_lean") or 0.5, "confidence": 0.35}]
        arb = arbitrate(brains)
        result["arbitration"] = arb
        result["pipeline"].append("arbitration")

        # unified verdict: prefer the arbiter's abstain discipline
        result["verdict"] = arb["decision"]
        result["abstain"] = arb["abstain"]
        result["synthetic_score"] = arb["synthetic"]
        result["novelty"] = vs["novelty"]

        # 6) optional CallGuard fraud fusion
        if context is not None:
            from callguard import assess
            result["callguard"] = assess(vs, context)
            result["pipeline"].append("callguard")
    else:
        result["verdict"] = "NEEDS_DETECTOR_BANK"
        result["note"] = "no detector_probs supplied (inject fusion.analyze per_model on server)."

    return result


def _selftest():
    sr = 16000; t = np.linspace(0, 2, sr*2, endpoint=False); rng = np.random.default_rng(0)
    y = (sum(np.sin(2*np.pi*f*t) for f in [180, 360, 900, 2400]) / 4 + 0.02*rng.standard_normal(len(t))).astype(np.float32)

    # (a) confident synthetic detectors + hostile context -> AI + callguard escalates
    r1 = run(y, sr, detector_probs={"acoustic-dsp": 0.9, "neural:xls-r": 0.93, "fusion-head(LFCC+CQCC)": 0.9},
             context={"device_known": False, "known_fraud_pattern": True}, deep_on_lowrisk=True)
    print("SYNTH+hostile:", "verdict", r1["verdict"], "| pipeline", r1["pipeline"])
    print("  callguard:", r1["callguard"]["tier"], r1["callguard"]["recommended_action"])
    # (b) disagreeing detectors -> UNKNOWN/abstain via arbitration
    r2 = run(y, sr, detector_probs={"acoustic-dsp": 0.82, "neural:xls-r": 0.31, "neural:distilhubert": 0.66},
             deep_on_lowrisk=True)
    print("ZERO-DAY   :", "verdict", r2["verdict"], "abstain", r2.get("abstain"), "novelty", r2.get("novelty"))
    assert r1["verdict"] == "AI" and r1["callguard"]["tier"] == "CRITICAL"
    assert r2.get("abstain") is True
    assert "arbitration" in r1 and "brains" in r1
    print("\n[selftest] PASS — full pipeline runs end-to-end: profiler→L0→brains→voxscore→arbitration→callguard.")


if __name__ == "__main__":
    _selftest()
