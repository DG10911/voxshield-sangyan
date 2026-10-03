"""
VoxShield — Generator Hunter (roadmap §18, P3).

Autonomous (governed) pipeline that turns recurring UNKNOWNS into actionable
intelligence. Ordered stages per §18:

  unknown → novelty check → cluster → representation analysis → compare to known
  generators → hypothesize family → propose attack recipe → benchmark plan →
  threat-registry entry → challenger-training CANDIDATE → validation gate

HARD RULE (roadmap §18/§21): **never auto-modifies production models.** The hunter
only PROPOSES — it emits a challenger-training candidate that must pass the governed
flywheel gates (flywheel.py) before anything ships. Pure orchestration over
unknown_vault (§17), registries (§4–6), threat_registry (§19). stdlib + numpy.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional
from unknown_vault import cluster as vault_cluster
import threat_registry


def _cos(a, b): return float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))


def _hypothesize_family(centroid: np.ndarray, known: Dict[str, np.ndarray]) -> Dict:
    """Compare an unknown cluster centroid to known-generator signatures →
    nearest family + confidence. If nothing is close, it's a candidate NEW family."""
    if not known:
        return {"family": "UNKNOWN_NEW", "nearest": None, "similarity": 0.0}
    sims = {g: _cos(centroid, np.asarray(sig, np.float32)) for g, sig in known.items()}
    nearest = max(sims, key=sims.get); s = sims[nearest]
    if s >= 0.85:   fam = f"{nearest}-like"
    elif s >= 0.6:  fam = f"related-to-{nearest}"
    else:           fam = "UNKNOWN_NEW"
    return {"family": fam, "nearest": nearest, "similarity": round(s, 3), "all": {k: round(v, 3) for k, v in sims.items()}}


def _propose_recipe(hypothesis: Dict, scenario_hint: Optional[str]) -> Dict:
    """Turn a family hypothesis into a proposed attack recipe to benchmark against."""
    return {"attack_mode": "voice_conversion" if "vc" in (hypothesis["family"] or "").lower() else "tts",
            "target_conditions": scenario_hint or "g711_ulaw+indic+noise",
            "note": "PROPOSED — render via VoiceStudio lab (§25) then benchmark; do not assume."}


def hunt(entries: List[Dict], known_signatures: Optional[Dict[str, np.ndarray]] = None,
         persist_threats: bool = False) -> Dict:
    """Run the hunter over vault entries. Returns proposed intel + challenger candidates.
    NEVER touches production — only proposes."""
    clusters = vault_cluster(entries)
    proposals = []
    for c in clusters:
        if not c["research_candidate"]:
            continue
        members = c["members"]
        embs = [np.asarray(entries[m]["embedding"], np.float32) for m in members
                if entries[m].get("embedding") is not None]
        centroid = np.mean([e/(np.linalg.norm(e)+1e-9) for e in embs], axis=0)
        scenario = entries[members[0]].get("scenario")
        hyp = _hypothesize_family(centroid, known_signatures or {})
        recipe = _propose_recipe(hyp, scenario)
        gen_name = f"hunter/{hyp['family']}"
        threat = {"generator": gen_name, "attack_method": recipe["attack_mode"],
                  "language": entries[members[0]].get("language", "multi"),
                  "observed_artifacts": ["recurring-high-novelty-cluster"],
                  "detection_perf": {"unseen_eer_pct": None},  # unknown until benchmarked
                  "confidence": "hypothesis", "evidence": f"vault cluster size={c['size']} novelty={c['mean_novelty']}",
                  "source": "generator_hunter", "provenance": "internal-hypothesis"}
        threat_registry.upsert(threat, persist=persist_threats)
        proposals.append({
            "cluster_size": c["size"], "mean_novelty": c["mean_novelty"],
            "family_hypothesis": hyp, "proposed_recipe": recipe,
            "threat_registered": gen_name, "scenario": scenario,
            "challenger_candidate": {
                "action": "PROPOSE_CHALLENGER_TRAINING",
                "requires_gates": ["curate", "qc", "consent_license", "adversarial_validation",
                                   "challenger", "golden_regression", "shadow", "promotion"],
                "auto_promote": False,
                "note": "Hunter proposes only. Must pass flywheel.py gates; live NEVER rewrites production."}})
    return {"clusters": len(clusters), "research_candidates": len(proposals),
            "proposals": proposals,
            "_governance": "Generator Hunter never auto-modifies production (roadmap §18/§21)."}


def _selftest():
    rng = np.random.default_rng(4)
    # a recurring unknown cluster (family A) + known signatures
    famA = rng.standard_normal(16)
    entries = [{"sample_id": f"u{i}", "embedding": (famA+0.03*rng.standard_normal(16)).tolist(),
                "novelty": 0.7, "language": "ta", "scenario": "tamil+g711+speakerphone"} for i in range(4)]
    known = {"elevenlabs": rng.standard_normal(16).tolist(), "xtts": rng.standard_normal(16).tolist()}
    out = hunt(entries, {k: np.asarray(v) for k, v in known.items()})
    print("research candidates:", out["research_candidates"])
    p = out["proposals"][0]
    print("  family hyp:", p["family_hypothesis"]["family"], "| recipe:", p["proposed_recipe"]["attack_mode"])
    print("  challenger auto_promote:", p["challenger_candidate"]["auto_promote"])
    assert out["research_candidates"] >= 1
    assert p["challenger_candidate"]["auto_promote"] is False           # governance
    assert "promotion" in p["challenger_candidate"]["requires_gates"]
    print("\n[selftest] PASS — recurring unknown → hypothesis + recipe + threat entry + governed challenger (never auto-promote).")


if __name__ == "__main__":
    _selftest()
