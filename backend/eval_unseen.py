"""
VoxShield — Post-hoc unseen-generator evaluation (recover the generalization gap
without retraining).

The training rounds held out `--holdout-generator xtts`, but the downloaded shards
contained only one generator, so the "unseen" bucket was empty and the gap was not
reported. This script scores an EXISTING checkpoint on the full staged corpus with a
chosen held-out generator, then writes a tagged scores.csv (seen=0 for the held-out
generator, seen=1 for the rest) that `paper_report.py` turns into the gap table.

Reuses `pipeline/train_corpus.load_corpus` + `score_rows` (same layout + metric as
training), so numbers are directly comparable.

Staged layout expected under --data-root:
    <root>/indicsynth/<Capitalized>/*.parquet     (fakes; "Generative Model" column)
    <root>/indicvoices_real/<lower>/*.parquet     (genuine)

Usage (on the DGX, after re-pulling a language's shards):
    python eval_unseen.py --ckpt checkpoints/round_*_hindi/last.pt \
        --data-root ~/voxshield/data/hindi --lang hindi \
        --holdout vits --out scores_hindi_unseen.csv
    # then:  python paper_report.py --csv scores_hindi_unseen.csv
"""
from __future__ import annotations
import argparse, csv, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "pipeline"))


def _load_model(ckpt, model_id):
    import torch
    from transformers import Wav2Vec2ForSequenceClassification
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Wav2Vec2ForSequenceClassification.from_pretrained(
        model_id, num_labels=2, ignore_mismatched_sizes=True)
    ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    state = ck.get("model", ck) if isinstance(ck, dict) else ck
    model.load_state_dict(state)
    model.to(device).eval()
    return model, device


def _generator_counts(rows):
    import collections
    return collections.Counter(r.get("generator", "?") for r in rows if r["label"] == 1)


def list_generators(data_root, lang, limit_per=None):
    import train_corpus as TC
    rows, _ = TC.load_corpus(data_root, "__none__", [lang], limit_per)   # no holdout -> all fakes in train/val/test
    c = _generator_counts(rows)
    print(f"generators present in {data_root} [{lang}]  (fakes={sum(c.values())}):")
    for g, n in c.most_common():
        print(f"    {g:<24} {n}")
    print("\npick a generator that is NOT in your training shard range as --holdout.")
    return c


def run(ckpt, data_root, lang, holdout, out, model_id, g711=True, limit_per=None):
    import train_corpus as TC                      # heavy deps (torch/datasets/sklearn)
    print(f"[load] corpus  root={data_root}  lang={lang}  holdout={holdout}")
    rows, stores = TC.load_corpus(data_root, holdout, [lang], limit_per)
    if not rows:
        print("!! no rows — is the staged layout present under --data-root?"); return []
    n_fake = sum(r["label"] for r in rows)
    n_unseen = sum(1 for r in rows if r.get("split") == "test_gen")
    print(f"[load] rows={len(rows)}  fakes={n_fake}  unseen({holdout})={n_unseen}")
    if n_unseen == 0:
        print(f"!! no fakes from holdout '{holdout}' in this data. Generators actually present:")
        for g, n in _generator_counts(rows).most_common():
            print(f"     {g}  ({n})")
        print("   -> re-run with --holdout <one of these>, but choose one NOT used in training.")

    model, device = _load_model(ckpt, model_id)
    scored = TC.score_rows(model, rows, stores, device, force_codec=False)
    if g711:
        scored += TC.score_rows(model, rows, stores, device, force_codec=True)

    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "score", "generator", "language", "channel", "seen"])
        w.writeheader(); w.writerows(scored)
    print(f"[scores] {len(scored)} rows -> {out}")

    import eval_gengap as G
    G.report(scored)
    return scored


def _selftest():
    # schema/round-trip only (no torch/datasets needed)
    rows = [{"label": 1, "score": 0.9, "generator": "vits", "language": "hi", "channel": "clean", "seen": 0},
            {"label": 1, "score": 0.2, "generator": "xtts", "language": "hi", "channel": "clean", "seen": 1},
            {"label": 0, "score": 0.1, "generator": "real", "language": "hi", "channel": "clean", "seen": 1}]
    import tempfile, os as _os
    p = _os.path.join(tempfile.mkdtemp(), "s.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "score", "generator", "language", "channel", "seen"])
        w.writeheader(); w.writerows(rows)
    import eval_gengap as G
    loaded = G.load_csv(p)
    assert len(loaded) == 3 and loaded[0]["score"] == 0.9
    print("[selftest] PASS — CSV schema round-trips; hand off to eval_gengap/paper_report.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt"); ap.add_argument("--data-root"); ap.add_argument("--lang", required=False)
    ap.add_argument("--holdout", default="vits", help="generator to treat as unseen (must exist in data)")
    ap.add_argument("--out", default="scores_unseen.csv")
    ap.add_argument("--model-id", default="facebook/wav2vec2-large-xlsr-53")
    ap.add_argument("--no-g711", action="store_true")
    ap.add_argument("--limit-per", type=int, default=None)
    ap.add_argument("--list-generators", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest(); return
    if a.list_generators:
        if not (a.data_root and a.lang):
            ap.error("--list-generators needs --data-root and --lang")
        list_generators(a.data_root, a.lang, a.limit_per); return
    if not (a.ckpt and a.data_root and a.lang):
        ap.error("--ckpt, --data-root and --lang required")
    run(a.ckpt, a.data_root, a.lang, a.holdout, a.out, a.model_id, not a.no_g711, a.limit_per)


if __name__ == "__main__":
    main()
