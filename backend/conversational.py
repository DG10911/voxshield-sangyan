"""
VoxShield — Conversational Forensics (roadmap §9, P3).

Turn-level cues for live AI-agent / cloned-caller detection. THREE signals, all
of which are EVIDENCE-ONLY and MUST NOT be used standalone (agents increasingly
mimic human timing — roadmap explicitly warns this):

  * Human Timing Complexity (HTC) — distribution of response latencies, filler/pause
    structure, turn-length variability. Bots are often too regular (low entropy) OR
    unnaturally fast; humans are irregular.
  * Semantic↔Prosody consistency — does the prosodic emphasis track the semantic
    content, or is it flat/mismatched (typical of TTS reading)? (proxy score input)
  * Voice Conservation Principle — across turns the SAME human keeps stable voice
    identity + physiology; a mid-call swap/clone breaks conservation.

This module scores conversation-level metadata (per-turn timings + optional
per-turn embeddings/prosody proxies). [HYPOTHESIS] — never auto-decide; feeds
arbitration as one low-weight family. stdlib + numpy, non-breaking.
"""
from __future__ import annotations
import numpy as np
from typing import List, Optional, Dict


def _entropy(x, bins=8):
    h, _ = np.histogram(x, bins=bins); p = h / (h.sum() + 1e-9); p = p[p > 0]
    return float(-(p*np.log2(p)).sum()) if len(p) else 0.0


def human_timing_complexity(response_latencies_s: List[float], turn_durations_s: List[float]) -> dict:
    lat = np.asarray(response_latencies_s, np.float32)
    dur = np.asarray(turn_durations_s, np.float32)
    if len(lat) < 3:
        return {"htc": None, "verdict": "TOO_FEW_TURNS", "_status": "need >=3 turns"}
    lat_cv = float(lat.std() / (lat.mean() + 1e-9))          # humans: high variability
    lat_ent = _entropy(lat)
    too_fast = float(np.mean(lat < 0.15))                     # sub-150ms replies = suspicious
    too_regular = lat_cv < 0.15                              # metronomic = bot-like
    htc = float(np.clip(0.5*np.tanh(lat_cv) + 0.5*(lat_ent/3.0), 0, 1))
    bot_lean = float(np.clip((0.15-lat_cv)*3 + too_fast*0.6 + (0.2 if too_regular else 0), 0, 1))
    return {"htc": round(htc, 3), "latency_cv": round(lat_cv, 3), "latency_entropy": round(lat_ent, 3),
            "frac_sub150ms": round(too_fast, 3), "bot_lean": round(bot_lean, 3),
            "verdict": "REGULAR/FAST timing (agent-leaning)" if bot_lean > 0.5 else "IRREGULAR timing (human-leaning)",
            "_status": "HYPOTHESIS — evidence only, NEVER standalone (agents mimic timing)."}


def voice_conservation(turn_embeddings: List[np.ndarray]) -> dict:
    """Same human => voice identity conserved across turns. A mid-call swap/clone
    breaks it (a turn whose embedding diverges from the running centroid)."""
    if turn_embeddings is None or len(turn_embeddings) < 3:
        return {"conserved": None, "verdict": "TOO_FEW_TURNS"}
    E = [np.asarray(e, np.float32) for e in turn_embeddings]
    E = [e/(np.linalg.norm(e)+1e-9) for e in E]
    running = E[0].copy(); sims = []
    for e in E[1:]:
        sims.append(float(np.dot(e, running/(np.linalg.norm(running)+1e-9))))
        running = 0.8*running + 0.2*e
    min_sim = float(min(sims)); breaks = [i+1 for i, s in enumerate(sims) if s < 0.92]
    return {"conserved": min_sim >= 0.92, "min_turn_similarity": round(min_sim, 3),
            "conservation_breaks": breaks,
            "verdict": "VOICE_CONSERVED" if not breaks else "CONSERVATION_BREAK (mid-call swap/clone?)",
            "_status": "HYPOTHESIS — pseudo-embedding thresholds (0.92); recalibrate for ECAPA."}


def text_forensics(transcript: str, prosody=None) -> dict:
    """Transcript-level conversational forensics (semantic↔prosody proxy).
    Read-aloud/scripted speech tends to have low filler rate + uniform sentence length;
    spontaneous human conversation is irregular. EVIDENCE ONLY — never standalone."""
    import re
    t = (transcript or "").strip()
    if not t:
        return {"available": False, "_status": "no transcript"}
    words = re.findall(r"\S+", t)
    sents = [s for s in re.split(r"[।.!?]+", t) if s.strip()]
    fillers = re.findall(r"\b(um+|uh+|hmm+|erm+|well|अरे|हाँ|तो|मतलब|वो|अं)\b", t, flags=re.I)
    lens = [len(re.findall(r"\S+", s)) for s in sents] or [len(words)]
    filler_ratio = len(fillers) / max(1, len(words))
    len_cv = float(np.std(lens) / (np.mean(lens) + 1e-9))
    scripted = float(np.clip((0.02 - filler_ratio) * 10 + (1 - min(1.0, len_cv / 0.6)) * 0.5, 0, 1))
    out = {"available": True, "n_words": len(words), "n_sentences": len(sents),
           "filler_ratio": round(filler_ratio, 4), "sentence_len_cv": round(len_cv, 3),
           "scripted_lean": round(scripted, 3),
           "verdict": "SCRIPTED/READ-ALOUD-leaning" if scripted > 0.5 else "CONVERSATIONAL-leaning",
           "_status": "HYPOTHESIS — transcript evidence only, never standalone."}
    if prosody is not None:
        try:
            p = np.asarray(prosody, np.float32)
            out["prosody_cv"] = round(float(p.std() / (p.mean() + 1e-9)), 3)
        except Exception:
            pass
    return out


def analyze(turns: List[Dict], turn_embeddings: Optional[List[np.ndarray]] = None) -> dict:
    """turns: [{latency_s, duration_s, semantic_prosody_match?}]  (per-turn metadata)."""
    lat = [t.get("latency_s", 0.0) for t in turns]
    dur = [t.get("duration_s", 0.0) for t in turns]
    htc = human_timing_complexity(lat, dur)
    spm = [t["semantic_prosody_match"] for t in turns if t.get("semantic_prosody_match") is not None]
    sem_pros = round(float(np.mean(spm)), 3) if spm else None
    vc = voice_conservation(turn_embeddings) if turn_embeddings is not None else {"conserved": None}
    agent_lean = htc.get("bot_lean") or 0.0
    if sem_pros is not None and sem_pros < 0.4: agent_lean = min(1.0, agent_lean + 0.2)
    if vc.get("conserved") is False: agent_lean = min(1.0, agent_lean + 0.3)
    return {"timing": htc, "semantic_prosody_match": sem_pros, "voice_conservation": vc,
            "agent_lean": round(float(agent_lean), 3),
            "_status": "HYPOTHESIS — conversation-level evidence; feeds arbitration as ONE low-weight family, never standalone."}


def _selftest():
    rng = np.random.default_rng(2)
    human = [{"latency_s": float(x), "duration_s": float(d), "semantic_prosody_match": 0.8}
             for x, d in zip(0.4+0.6*rng.random(6), 1.0+2.0*rng.random(6))]
    bot = [{"latency_s": 0.08+0.01*i%2*0.0, "duration_s": 2.0, "semantic_prosody_match": 0.3} for i in range(6)]
    h = analyze(human); b = analyze(bot)
    print("human conv:", h["timing"]["verdict"], "agent_lean", h["agent_lean"])
    print("bot   conv:", b["timing"]["verdict"], "agent_lean", b["agent_lean"])
    assert b["agent_lean"] > h["agent_lean"]
    # voice conservation: stable speaker vs mid-call swap
    base = rng.standard_normal(32); swap = rng.standard_normal(32)
    stable = [base + 0.02*rng.standard_normal(32) for _ in range(5)]
    swapped = stable[:3] + [swap + 0.02*rng.standard_normal(32) for _ in range(2)]
    vc_ok = voice_conservation(stable); vc_bad = voice_conservation(swapped)
    print("stable spk:", vc_ok["verdict"], "| swapped:", vc_bad["verdict"], "breaks", vc_bad["conservation_breaks"])
    assert vc_ok["conserved"] and vc_bad["conserved"] is False
    print("\n[selftest] PASS — fast/regular bot flagged; mid-call voice swap breaks conservation.")


if __name__ == "__main__":
    _selftest()
