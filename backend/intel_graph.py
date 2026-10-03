"""
VoxShield — Generator Intelligence Graph (roadmap §20, P3).

A queryable graph over the intelligence we hold:
  Generator → Version → Voice → Attack-Mode → Language → Codec → Device →
  Environment → Artifact → Detector → Failure-Mode.

Built from the registries (§4–6), the Threat Registry (§19), and measured eval rows
(generator × condition × EER/FN). Answers the questions the roadmap names:
  * "which generators are hard under Tamil + G.711 + speakerphone?"
  * "which conditions cause the highest false-negatives?"

Lightweight adjacency store (no external graph DB); stdlib only, non-breaking.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class IntelGraph:
    def __init__(self):
        self.edges: Dict[str, set] = defaultdict(set)          # node -> {neighbours}
        self.node_type: Dict[str, str] = {}
        self.perf: List[Dict] = []                             # measured (gen,conditions)->metric rows

    def _add(self, a: Tuple[str, str], b: Tuple[str, str]):
        (ta, va), (tb, vb) = a, b
        na, nb = f"{ta}:{va}", f"{tb}:{vb}"
        self.node_type[na] = ta; self.node_type[nb] = tb
        self.edges[na].add(nb); self.edges[nb].add(na)

    def add_observation(self, generator: str, version: str = "unknown", voice: str = None,
                        attack_mode: str = None, language: str = None, codec: str = None,
                        device: str = None, environment: str = None, artifact: str = None,
                        detector: str = None, failure_mode: str = None,
                        eer_pct: Optional[float] = None, fn_rate: Optional[float] = None):
        g = ("generator", generator)
        chain = [("version", version), ("voice", voice), ("attack_mode", attack_mode),
                 ("language", language), ("codec", codec), ("device", device),
                 ("environment", environment), ("artifact", artifact),
                 ("detector", detector), ("failure_mode", failure_mode)]
        prev = g
        for typ, val in chain:
            if val is None: continue
            self._add(prev, (typ, val))       # path edge (Gen→Ver→Voice→…→FailureMode)
            self._add(g, (typ, val))          # + direct edge from generator (star) for querying
            prev = (typ, val)
        self.perf.append({"generator": generator, "version": version, "language": language,
                          "codec": codec, "device": device, "environment": environment,
                          "eer_pct": eer_pct, "fn_rate": fn_rate})

    # ---- queries ----
    def hard_under(self, conditions: Dict[str, str], metric: str = "eer_pct", top: int = 5) -> List[Dict]:
        """generators hardest under ALL given conditions (e.g. {'language':'ta','codec':'g711_ulaw'})."""
        rows = [r for r in self.perf
                if all(r.get(k) == v for k, v in conditions.items()) and r.get(metric) is not None]
        agg: Dict[str, List[float]] = defaultdict(list)
        for r in rows: agg[r["generator"]].append(r[metric])
        out = [{"generator": g, metric: round(sum(v)/len(v), 2), "n": len(v)} for g, v in agg.items()]
        return sorted(out, key=lambda x: -x[metric])[:top]

    def worst_conditions(self, metric: str = "fn_rate", by: str = "codec", top: int = 5) -> List[Dict]:
        """which values of `by` (codec/device/environment/language) cause the highest metric."""
        agg: Dict[str, List[float]] = defaultdict(list)
        for r in self.perf:
            if r.get(by) is not None and r.get(metric) is not None:
                agg[r[by]].append(r[metric])
        out = [{by: k, metric: round(sum(v)/len(v), 3), "n": len(v)} for k, v in agg.items()]
        return sorted(out, key=lambda x: -x[metric])[:top]

    def neighbours(self, node_type: str, value: str) -> Dict[str, List[str]]:
        n = f"{node_type}:{value}"; out: Dict[str, List[str]] = defaultdict(list)
        for m in self.edges.get(n, ()): out[self.node_type[m]].append(m.split(":", 1)[1])
        return dict(out)

    def summary(self) -> Dict:
        types = defaultdict(int)
        for t in self.node_type.values(): types[t] += 1
        return {"nodes": len(self.node_type), "observations": len(self.perf), "by_type": dict(types)}


def from_threats_and_eval(threats: List[Dict], eval_rows: Optional[List[Dict]] = None) -> IntelGraph:
    g = IntelGraph()
    for t in threats:
        g.add_observation(generator=t["generator"], version=t.get("version", "unknown"),
                          attack_mode=t.get("attack_method"), language=t.get("language"),
                          codec=t.get("codec"),
                          eer_pct=(t.get("detection_perf") or {}).get("unseen_eer_pct"))
    for r in (eval_rows or []):
        g.add_observation(**r)
    return g


def _selftest():
    import threat_registry
    g = from_threats_and_eval(threat_registry._load(), eval_rows=[
        {"generator": "bark", "language": "ta", "codec": "g711_ulaw", "device": "speakerphone", "eer_pct": 24.0, "fn_rate": 0.22},
        {"generator": "rvc",  "language": "ta", "codec": "g711_ulaw", "device": "speakerphone", "eer_pct": 20.0, "fn_rate": 0.18},
        {"generator": "elevenlabs-v3", "language": "hi", "codec": "opus", "device": "iphone", "eer_pct": 6.0, "fn_rate": 0.04},
    ])
    print("graph:", g.summary())
    hard = g.hard_under({"language": "ta", "codec": "g711_ulaw"})
    print("hard under Tamil+G.711:", [(h["generator"], h["eer_pct"]) for h in hard])
    worst = g.worst_conditions(metric="fn_rate", by="codec")
    print("worst codecs by FN:", [(w["codec"], w["fn_rate"]) for w in worst])
    assert hard and hard[0]["generator"] == "bark"
    assert worst and worst[0]["codec"] == "g711_ulaw"
    nb = g.neighbours("generator", "bark")
    print("bark neighbours:", nb)
    assert "ta" in nb.get("language", [])
    print("\n[selftest] PASS — graph answers 'hard under Tamil+G.711' and 'worst codec by FN'.")


if __name__ == "__main__":
    _selftest()
