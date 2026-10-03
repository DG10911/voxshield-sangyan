"""
VoxShield — registry loader & validator (roadmap §4–6).

Loads and validates the three foundational registries every evaluation is built on:
    registries/generators.json     — Generator Capability Registry (versioned)
    registries/attack_modes.json   — Attack Mode Registry
    registries/attack_recipes.json — Attack Recipe Registry (references the other two)

Non-breaking, dependency-free (stdlib json). Validates required keys, that no
entry carries keys outside its declared `_schema`, and that every recipe's
`generator` + `attack_mode` resolve against the generator/mode registries.
"""
from __future__ import annotations
import os, json
from typing import Dict, List, Optional

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registries")


def _load(name):
    with open(os.path.join(_DIR, name)) as f:
        return json.load(f)


def _validate(doc, items_key, label):
    schema = set(doc.get("_schema", []))
    required = doc.get("_required", [])
    errs = []
    for i, e in enumerate(doc[items_key]):
        for r in required:
            if r not in e or e[r] in (None, ""):
                errs.append(f"{label}[{i}] missing required '{r}'")
        for k in e:
            if k.startswith("_"):
                continue
            if schema and k not in schema:
                errs.append(f"{label}[{i}] unknown key '{k}' (not in _schema)")
    return errs


class Registries:
    def __init__(self):
        self.gen_doc = _load("generators.json")
        self.mode_doc = _load("attack_modes.json")
        self.recipe_doc = _load("attack_recipes.json")
        self.generators: List[dict] = self.gen_doc["generators"]
        self.modes: List[dict] = self.mode_doc["modes"]
        self.recipes: List[dict] = self.recipe_doc["recipes"]

    # ---- queries ----
    def generators_by_capability(self, cap: str) -> List[dict]:
        return [g for g in self.generators if g.get(cap) is True]

    def get_generator(self, model: str, version: Optional[str] = None) -> Optional[dict]:
        for g in self.generators:
            if g["model"] == model and (version is None or str(g.get("version")) == str(version)):
                return g
        return None

    def mode_ids(self):
        return {m["id"] for m in self.modes}

    def generator_names(self):
        return {g["model"] for g in self.generators}

    # ---- validation ----
    def validate(self) -> List[str]:
        errs = []
        errs += _validate(self.gen_doc, "generators", "generator")
        errs += _validate(self.mode_doc, "modes", "attack_mode")
        errs += _validate(self.recipe_doc, "recipes", "recipe")
        # cross-reference: every recipe's generator + mode must resolve
        gnames = self.generator_names() | {"unknown"}
        mids = self.mode_ids()
        for r in self.recipes:
            if r.get("generator") not in gnames:
                errs.append(f"recipe {r.get('recipe_id')} references unknown generator '{r.get('generator')}'")
            if r.get("attack_mode") not in mids:
                errs.append(f"recipe {r.get('recipe_id')} references unknown attack_mode '{r.get('attack_mode')}'")
        return errs

    def summary(self) -> dict:
        seed = sum(1 for g in self.generators if g.get("status") == "seed")
        stub = sum(1 for g in self.generators if g.get("status") == "stub")
        return {"generators": len(self.generators), "seed": seed, "stub": stub,
                "attack_modes": len(self.modes), "recipes": len(self.recipes)}


_reg: Optional[Registries] = None
def get() -> Registries:
    global _reg
    if _reg is None:
        _reg = Registries()
    return _reg


def _selftest():
    r = get()
    print("summary:", r.summary())
    errs = r.validate()
    if errs:
        print("VALIDATION ERRORS:")
        for e in errs:
            print("  -", e)
    else:
        print("validation: PASS (all entries conform to schema; all recipe refs resolve)")
    # example queries
    print("\ngenerators with cross_lingual_cloning:",
          [g["model"] for g in r.generators_by_capability("cross_lingual_cloning")])
    print("XTTS v2 entry present:", r.get_generator("XTTS", "2") is not None)
    print("attack modes:", len(r.modes), "e.g.", [m["id"] for m in r.modes[:5]])
    assert not errs, "registry validation failed"
    assert r.get_generator("XTTS", "2"), "XTTS v2 should exist"
    print("\n[selftest] PASS")


if __name__ == "__main__":
    _selftest()
