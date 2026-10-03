"""
VoxShield — Capture Manifest generator (roadmap §23, Device/Env/Distance data drop-in).

The eval code for the Device / Environment / Distance matrices already exists
(eval_matrix, eval_channel). What's missing is the real RECORDINGS. This module
produces the exact capture protocol — every (device × environment × distance × phrase)
cell to record — as a checklist, and then VALIDATES returned recordings against the
expected cells (so the collected data actually covers the matrix before you eval it).
stdlib + dataset_schema (records normalize into SAMPLE_SCHEMA).
"""
from __future__ import annotations
from typing import Dict, List
from itertools import product
from dataset_schema import build_sample, validate_sample

DEVICES = ["iphone", "android", "feature_phone", "laptop_mic", "headset", "speakerphone"]
ENVIRONMENTS = ["quiet_room", "office", "street", "vehicle", "restaurant"]
DISTANCES_M = [0.05, 0.5, 1.0, 2.0, 5.0]
PHRASES = ["read_sentence_1", "read_sentence_2", "spontaneous_1", "digits_otp", "code_switch_hi_en"]


def manifest(devices=None, environments=None, distances=None, phrases=None,
             languages=None) -> Dict:
    devices = devices or DEVICES; environments = environments or ENVIRONMENTS
    distances = distances or DISTANCES_M; phrases = phrases or PHRASES
    languages = languages or ["hi"]
    cells = []
    for dev, env, dist, ph, lang in product(devices, environments, distances, phrases, languages):
        cells.append({"cell_id": f"{dev}|{env}|{dist}m|{ph}|{lang}",
                      "device": dev, "environment": env, "distance": dist,
                      "phrase": ph, "language": lang, "recorded": False})
    return {"n_cells": len(cells), "axes": {"devices": len(devices), "environments": len(environments),
            "distances": len(distances), "phrases": len(phrases), "languages": len(languages)},
            "cells": cells,
            "protocol": ["fixed phrases per speaker", "label device+env+distance at capture",
                         "consent form before recording", "same speaker across cells for continuity",
                         "store only consent-cleared audio (security.privacy_check)"],
            "_note": "genuine-human capture → feeds Worst-Human FP minimisation + Device/Env/Distance matrices."}


def validate_capture(recordings: List[Dict], manifest_cells: List[Dict]) -> Dict:
    """recordings: [{cell_id, path, speaker_id, consent}]. Reports coverage + schema validity."""
    want = {c["cell_id"] for c in manifest_cells}
    got = {r.get("cell_id") for r in recordings}
    covered = want & got; missing = want - got; extra = got - want
    schema_errs = []
    for r in recordings:
        cell = next((c for c in manifest_cells if c["cell_id"] == r.get("cell_id")), {})
        s = build_sample(sample_id=r.get("path") or r.get("cell_id"),
                         language=cell.get("language", "hi"), generator="none",
                         attack_mode="bonafide", codec="wideband", label="HUMAN",
                         provenance="own-capture", license="consented",
                         consent=r.get("consent", False), split="golden",
                         device=cell.get("device"), environment=cell.get("environment"),
                         distance=cell.get("distance"), speaker_id=r.get("speaker_id"))
        e = validate_sample(s)
        if e: schema_errs.append({"cell": r.get("cell_id"), "errors": e})
    return {"coverage_pct": round(100*len(covered)/len(want), 1) if want else 0.0,
            "covered": len(covered), "missing": sorted(missing)[:10], "n_missing": len(missing),
            "unexpected": sorted(extra)[:10], "schema_errors": schema_errs[:10],
            "ready_for_eval": len(missing) == 0 and not schema_errs,
            "_note": "run eval_matrix / eval_channel once coverage is complete + schema-clean."}


def _selftest():
    m = manifest(devices=["iphone", "android"], environments=["quiet_room", "street"],
                 distances=[0.5, 2.0], phrases=["read_sentence_1"], languages=["hi"])
    print("manifest cells:", m["n_cells"], "| axes", m["axes"])
    assert m["n_cells"] == 2*2*2*1*1  # 8
    # simulate recording half the cells with consent
    recs = [{"cell_id": c["cell_id"], "path": f"rec/{i}.wav", "speaker_id": "s1", "consent": True}
            for i, c in enumerate(m["cells"][:4])]
    v = validate_capture(recs, m["cells"])
    print("coverage:", v["coverage_pct"], "% | missing", v["n_missing"], "| ready", v["ready_for_eval"])
    assert v["covered"] == 4 and v["n_missing"] == 4 and v["ready_for_eval"] is False
    # full + consented → ready
    full = [{"cell_id": c["cell_id"], "path": f"r{i}.wav", "speaker_id": "s1", "consent": True}
            for i, c in enumerate(m["cells"])]
    vf = validate_capture(full, m["cells"])
    assert vf["coverage_pct"] == 100.0 and vf["ready_for_eval"] is True
    print("\n[selftest] PASS — generates the capture checklist; validates coverage + schema + consent before eval.")


if __name__ == "__main__":
    _selftest()
