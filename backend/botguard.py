"""
VoxShield — BotGuard: human vs AI-agent / automated-caller (roadmap §19).

Distinguishes a live human from an AI voice agent / automated bot using
CONVERSATION-LEVEL behaviour (response timing, turn-taking regularity, filler/
hesitation rate) rather than deepfake detection alone. AI agents tend to answer
with suspiciously LOW latency variance, very regular turn timing, and few natural
disfluencies.

CRITICAL (roadmap §14/§19): this must NEVER be a standalone human/AI proof — AI
agents can deliberately imitate human timing. It is one evidence stream for the
arbitration brain. [HYPOTHESIS] until validated on real agent-vs-human call data.

Input: a list of turn dicts with (all optional):
    response_latency_ms  time from end-of-prompt to start-of-reply
    turn_duration_ms     length of the reply
    fillers              count of um/uh/hesitations in the turn
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict


def _cv(x):
    x = np.asarray(x, float)
    return float(np.std(x) / (np.mean(x) + 1e-9)) if len(x) else 0.0


def bot_score(turns: List[Dict]) -> dict:
    if not turns:
        return {"bot_score": None, "verdict": "UNKNOWN", "_status": "no turn data"}
    lat = [t["response_latency_ms"] for t in turns if t.get("response_latency_ms") is not None]
    dur = [t["turn_duration_ms"] for t in turns if t.get("turn_duration_ms") is not None]
    fil = [t.get("fillers", 0) for t in turns]

    lat_cv = _cv(lat) if lat else None
    dur_cv = _cv(dur) if dur else None
    fast = float(np.mean([l < 350 for l in lat])) if lat else 0.0     # near-instant replies
    filler_rate = float(np.mean(fil)) if fil else 0.0

    # bot hints: very regular timing (low CV) + fast replies + almost no fillers
    reg = 0.0; nfeat = 0
    if lat_cv is not None: reg += 1 - min(1.0, lat_cv / 0.5); nfeat += 1
    if dur_cv is not None: reg += 1 - min(1.0, dur_cv / 0.5); nfeat += 1
    regularity = reg / max(nfeat, 1)
    score = float(np.clip(0.45*regularity + 0.30*fast + 0.25*(1 - min(1.0, filler_rate/1.5)), 0, 1))
    verdict = "LIKELY_AI_AGENT" if score >= 0.65 else ("POSSIBLE_AI_AGENT" if score >= 0.45 else "LIKELY_HUMAN")
    return {"bot_score": round(score, 3),
            "features": {"latency_cv": None if lat_cv is None else round(lat_cv,3),
                         "duration_cv": None if dur_cv is None else round(dur_cv,3),
                         "fast_reply_rate": round(fast,3), "filler_rate": round(filler_rate,3)},
            "verdict": verdict,
            "_status": "HYPOTHESIS — behavioural only; NEVER standalone (agents can mimic humans); validate on agent-vs-human calls."}


def _selftest():
    rng = np.random.default_rng(0)
    # human: variable latency, variable turns, some fillers
    human = [{"response_latency_ms": float(rng.normal(900, 500)),
              "turn_duration_ms": float(rng.normal(2500, 1200)),
              "fillers": int(rng.integers(0, 3))} for _ in range(12)]
    # bot: tight, fast, no fillers
    bot = [{"response_latency_ms": float(rng.normal(220, 30)),
            "turn_duration_ms": float(rng.normal(1800, 120)),
            "fillers": 0} for _ in range(12)]
    h = bot_score(human); b = bot_score(bot)
    print("HUMAN:", h["bot_score"], h["verdict"], h["features"])
    print("BOT  :", b["bot_score"], b["verdict"], b["features"])
    assert b["bot_score"] > h["bot_score"], "bot-like timing should score higher"
    print("\n[selftest] PASS — regular/fast/no-filler timing scores as AI-agent; variable human timing does not.")


if __name__ == "__main__":
    _selftest()
