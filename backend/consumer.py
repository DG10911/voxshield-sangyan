"""
VoxShield — Consumer surface: "Is this voice real?" (roadmap §28, P4).

A plain-language wrapper over a VoxScore verdict for a non-expert end-user. It
translates the technical result into an honest, non-alarming answer with an explicit
confidence band and a standing caveat that no detector is ever 100% certain. It NEVER
says a flat "fake/real" with false certainty, and on uncertainty it says so plainly.
stdlib only, non-breaking.
"""
from __future__ import annotations
from typing import Dict


def answer(voxscore: Dict) -> Dict:
    verdict = voxscore.get("verdict") or voxscore.get("risk")
    abstain = bool(voxscore.get("abstain"))
    syn = voxscore.get("synthetic_score", voxscore.get("synthetic"))
    conf = voxscore.get("evidence_confidence", voxscore.get("evidence")) or 0.5

    if abstain or verdict in ("UNKNOWN", "REVIEW"):
        headline = "Not sure — treat with caution"
        body = ("We couldn't confidently tell whether this voice is real or AI-generated. "
                "That can happen with new AI voices, poor call quality, or unusual speech. "
                "Don't rely on this alone — verify through another channel.")
        emoji = "🟡"
    elif verdict in ("AI", "HIGH"):
        headline = "Likely AI-generated"
        body = ("Several signals suggest this voice may be synthetic. "
                "Be cautious with any request for money, codes, or personal details.")
        emoji = "🔴"
    elif verdict in ("HUMAN", "LOW"):
        headline = "Likely a real human voice"
        body = "We found no strong signs of AI synthesis — but stay alert if anything feels off."
        emoji = "🟢"
    else:
        headline = "Inconclusive"; body = "Not enough information to judge."; emoji = "🟡"

    band = "high" if conf >= 0.7 else "medium" if conf >= 0.45 else "low"
    return {"headline": headline, "emoji": emoji, "explanation": body,
            "confidence_band": band,
            "synthetic_likelihood_pct": round(syn*100, 1) if isinstance(syn, (int, float)) else None,
            "caveat": "No voice-detection tool is ever 100% certain. Use this as one signal, not proof.",
            "never": "We do not accuse or block anyone automatically."}


def _selftest():
    ai = answer({"verdict": "AI", "synthetic_score": 0.9, "evidence_confidence": 0.8})
    hu = answer({"verdict": "HUMAN", "synthetic_score": 0.1, "evidence_confidence": 0.75})
    un = answer({"verdict": "UNKNOWN", "abstain": True, "synthetic_score": 0.55, "evidence_confidence": 0.3})
    print("AI     :", ai["emoji"], ai["headline"], "| conf", ai["confidence_band"])
    print("HUMAN  :", hu["emoji"], hu["headline"])
    print("UNKNOWN:", un["emoji"], un["headline"], "| conf", un["confidence_band"])
    assert ai["headline"].startswith("Likely AI") and hu["headline"].startswith("Likely a real")
    assert un["headline"].startswith("Not sure")
    assert all("caveat" in r for r in (ai, hu, un))
    print("\n[selftest] PASS — plain-language answers with honest confidence + always-uncertain caveat; never auto-accuses.")


if __name__ == "__main__":
    _selftest()
