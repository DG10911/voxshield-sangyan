"""
VoxShield — Unknown Vault (roadmap §17, P3).

Every interesting UNKNOWN (abstain/zero-day/high-novelty) is stored as consent- and
license-gated METADATA — never raw audio without a basis (enforced via security.py).
Stored fields per §17: sample_id, embedding, language, accent, device, channel,
environment, speaker, generator_hypothesis, detector_outputs, novelty, scenario,
timestamp, provenance, license, consent. Unknowns are clustered by embedding so
recurring novel patterns surface as RESEARCH CANDIDATES (feed Generator Hunter §18).

Persists to backend/registries/unknown_vault.json. stdlib + numpy, non-breaking.
**Never trains production directly** — this is a curation/candidate store only.
"""
from __future__ import annotations
import json, os, time
import numpy as np
from typing import Dict, List, Optional
from security import privacy_check, redact

_VAULT = os.path.join(os.path.dirname(__file__), "registries", "unknown_vault.json")
VAULT_FIELDS = ["sample_id", "embedding", "language", "accent", "device", "channel",
                "environment", "speaker", "generator_hypothesis", "detector_outputs",
                "novelty", "scenario", "timestamp", "provenance", "license", "consent"]


def _load() -> List[Dict]:
    if not os.path.exists(_VAULT): return []
    with open(_VAULT) as f: return json.load(f).get("entries", [])


def _save(entries: List[Dict]):
    with open(_VAULT, "w") as f:
        json.dump({"_note": "consent/license-gated UNKNOWN metadata; never_train; research candidates only",
                   "count": len(entries), "entries": entries}, f, indent=2)


def admit(record: Dict, persist: bool = False) -> Dict:
    """Admit an unknown IF it clears the privacy/consent gate. Stores metadata only;
    embedding kept (not raw audio); PII redacted."""
    pc = privacy_check(record)
    if not pc["retain_ok"]:
        return {"admitted": False, "reason": pc["issues"]}
    rec = redact({k: record.get(k) for k in VAULT_FIELDS if k in record})
    rec.setdefault("timestamp", time.time())
    if persist:
        entries = _load(); entries.append(rec); _save(entries)
    return {"admitted": True, "record": rec}


def _cos(a, b): return float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))


def cluster(entries: Optional[List[Dict]] = None, threshold: float = 0.85) -> List[Dict]:
    """Greedy single-link clustering over embeddings → recurring novel patterns.
    Clusters with >=2 members and high mean novelty are RESEARCH CANDIDATES."""
    entries = entries if entries is not None else _load()
    embs = [(i, np.asarray(e["embedding"], np.float32)) for i, e in enumerate(entries)
            if e.get("embedding") is not None]
    clusters: List[List[int]] = []
    centroids: List[np.ndarray] = []
    for i, v in embs:
        v = v/(np.linalg.norm(v)+1e-9)
        best, bj = threshold, -1
        for j, c in enumerate(centroids):
            s = _cos(v, c)
            if s >= best: best, bj = s, j
        if bj >= 0:
            clusters[bj].append(i); centroids[bj] = 0.7*centroids[bj] + 0.3*v
        else:
            clusters.append([i]); centroids.append(v)
    out = []
    for members in clusters:
        nov = [entries[m].get("novelty", 0.0) or 0.0 for m in members]
        out.append({"size": len(members), "members": members,
                    "mean_novelty": round(float(np.mean(nov)), 3),
                    "research_candidate": len(members) >= 2 and float(np.mean(nov)) >= 0.45})
    return sorted(out, key=lambda c: (-c["size"], -c["mean_novelty"]))


def research_candidates(entries: Optional[List[Dict]] = None) -> List[Dict]:
    return [c for c in cluster(entries) if c["research_candidate"]]


def _selftest():
    rng = np.random.default_rng(3)
    famA = rng.standard_normal(16)          # a recurring unknown family
    def mk(sid, base, nov, consent="public"):
        return {"sample_id": sid, "embedding": (base+0.03*rng.standard_normal(16)).tolist(),
                "language": "ta", "novelty": nov, "provenance": "live-abstain",
                "license": "research", "consent": consent, "scenario": "tamil+g711"}
    ok = [admit(mk(f"u{i}", famA, 0.7)) for i in range(3)]
    assert all(a["admitted"] for a in ok)
    # a no-consent unknown must be rejected
    bad = admit({"sample_id": "x", "phone": "+9199...", "consent": None, "provenance": "live"})
    print("no-consent admit:", bad["admitted"], bad.get("reason"))
    assert bad["admitted"] is False
    entries = [a["record"] for a in ok] + [mk("lone", rng.standard_normal(16), 0.5)]
    cands = research_candidates(entries)
    print("clusters:", [(c["size"], c["mean_novelty"], c["research_candidate"]) for c in cluster(entries)])
    assert len(cands) >= 1 and cands[0]["size"] == 3
    print("\n[selftest] PASS — consent-gated admit; recurring novel cluster surfaces as a research candidate.")


if __name__ == "__main__":
    _selftest()
