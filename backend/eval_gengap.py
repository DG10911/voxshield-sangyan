"""
VoxShield — Generalization-Gap evaluation harness  (roadmap §12, §22, §35).

The vision's #1 principle: optimise for the attack we've NEVER seen. The single
most important number is therefore the **Generalization Gap**:

    gap = EER(unseen generators) − EER(seen generators)

This harness ingests a scored CSV and reports, honestly and per-slice:
    * overall EER / ROC-AUC
    * per-generator EER, per-language EER, per-channel EER
    * SEEN vs UNSEEN generator EER  → the generalization gap
    * leave-one-generator-out (LOGO) protocol (each generator held out in turn)
    * calibration: ECE + Brier

Input CSV columns (header row):
    label     0 = genuine human, 1 = synthetic        (required)
    score     P(synthetic) in [0,1]                    (required)
    generator generator/model name    (optional; 'real'/'human' for genuine)
    language  language code            (optional)
    channel   codec/channel           (optional)
    seen      1 if generator was in training, 0 if held-out  (optional)

Nothing here touches production; it only measures. Every reported number carries
its slice and n so it can never be turned into a single misleading aggregate.

Usage:
    python eval_gengap.py --csv scores.csv
    python eval_gengap.py --csv scores.csv --logo        # leave-one-generator-out
    python eval_gengap.py --selftest
"""
from __future__ import annotations
import argparse, csv, sys, math
import numpy as np

try:
    from sklearn.metrics import roc_curve, roc_auc_score
    _SK = True
except Exception:
    _SK = False


def eer(y, s):
    y = np.asarray(y); s = np.asarray(s)
    if len(set(y.tolist())) < 2:
        return None
    if _SK:
        fpr, tpr, _ = roc_curve(y, s); fnr = 1 - tpr
        k = int(np.nanargmin(np.abs(fpr - fnr)))
        return float((fpr[k] + fnr[k]) / 2)
    # numpy fallback
    order = np.argsort(-s); y = y[order]
    P = y.sum(); N = len(y) - P
    tp = np.cumsum(y); fp = np.cumsum(1 - y)
    tpr = tp / max(P, 1); fpr = fp / max(N, 1); fnr = 1 - tpr
    k = int(np.argmin(np.abs(fpr - fnr)))
    return float((fpr[k] + fnr[k]) / 2)


def auc(y, s):
    if len(set(y)) < 2:
        return None
    if _SK:
        return float(roc_auc_score(y, s))
    # numpy Mann–Whitney fallback
    y = np.asarray(y); s = np.asarray(s)
    pos = s[y == 1]; neg = s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def ece(y, s, bins=10):
    y = np.asarray(y); s = np.asarray(s); n = len(y); e = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        m = (s >= lo) & (s < hi if b < bins - 1 else s <= hi)
        if m.sum() == 0:
            continue
        conf = s[m].mean(); acc = y[m].mean()
        e += (m.sum() / n) * abs(acc - conf)
    return float(e)


def brier(y, s):
    y = np.asarray(y, float); s = np.asarray(s, float)
    return float(np.mean((s - y) ** 2))


def _fmt(x, pct=True):
    if x is None:
        return "  —  "
    return f"{x*100:5.2f}%" if pct else f"{x:5.3f}"


def _slice_table(rows, key, title):
    groups = {}
    for r in rows:
        groups.setdefault(r.get(key, "?") or "?", []).append(r)
    print(f"\n  {title}")
    print(f"    {'value':<20} {'EER':>7} {'AUC':>7} {'n':>7} {'pos':>6}")
    for g in sorted(groups):
        gr = groups[g]; y = [r["label"] for r in gr]; s = [r["score"] for r in gr]
        print(f"    {g:<20} {_fmt(eer(y,s))} {_fmt(auc(y,s),0):>7} {len(gr):>7} {sum(y):>6}")


def report(rows):
    y = [r["label"] for r in rows]; s = [r["score"] for r in rows]
    print("=" * 60)
    print("VoxShield · Generalization-Gap Report")
    print("=" * 60)
    print(f"  overall   EER={_fmt(eer(y,s))}  AUC={_fmt(auc(y,s),0)}  "
          f"ECE={_fmt(ece(y,s),0)}  Brier={_fmt(brier(y,s),0)}  n={len(rows)}")

    have = lambda k: any(r.get(k) for r in rows)
    if have("generator"): _slice_table(rows, "generator", "per-generator")
    if have("language"):  _slice_table(rows, "language",  "per-language")
    if have("channel"):   _slice_table(rows, "channel",   "per-channel")

    # --- the headline: SEEN vs UNSEEN generalization gap ---
    # EER needs both classes, so each fake slice is scored against ALL genuine
    # samples (real speech is neither "seen" nor "unseen" — it's the anchor).
    if have("seen"):
        real = [r for r in rows if r["label"] == 0]
        seen_fake = [r for r in rows if r["label"] == 1 and str(r.get("seen")) in ("1", "true", "True")]
        unseen_fake = [r for r in rows if r["label"] == 1 and str(r.get("seen")) in ("0", "false", "False")]
        seen = real + seen_fake; unseen = real + unseen_fake
        e_seen = eer([r["label"] for r in seen], [r["score"] for r in seen]) if seen_fake else None
        e_unseen = eer([r["label"] for r in unseen], [r["score"] for r in unseen]) if unseen_fake else None
        print("\n  ┌ GENERALIZATION GAP (the #1 metric) ─────────────────")
        print(f"  │  SEEN generators    EER={_fmt(e_seen)}  (n={len(seen)})")
        print(f"  │  UNSEEN generators  EER={_fmt(e_unseen)}  (n={len(unseen)})")
        if e_seen is not None and e_unseen is not None:
            gap = e_unseen - e_seen
            verdict = "SMALL (generalises)" if gap < 0.05 else ("MODERATE" if gap < 0.15 else "LARGE (memorising known generators)")
            print(f"  │  GAP = {gap*100:+.2f} pts  → {verdict}")
        print("  └──────────────────────────────────────────────────────")


def logo(rows):
    """Leave-One-Generator-Out: hold each fake generator out, score it vs all real."""
    gens = sorted({r["generator"] for r in rows
                   if r.get("generator") and r["label"] == 1})
    real = [r for r in rows if r["label"] == 0]
    print("\n  LEAVE-ONE-GENERATOR-OUT (each fake generator as the 'unseen' test)")
    print(f"    {'held-out generator':<22} {'EER vs real':>11} {'n_fake':>7}")
    gaps = []
    for g in gens:
        fake_g = [r for r in rows if r.get("generator") == g and r["label"] == 1]
        test = real + fake_g
        e = eer([r["label"] for r in test], [r["score"] for r in test])
        if e is not None: gaps.append(e)
        print(f"    {g:<22} {_fmt(e):>11} {len(fake_g):>7}")
    if gaps:
        print(f"    {'MEAN unseen-generator EER':<22} {_fmt(float(np.mean(gaps))):>11}")


def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                r["label"] = int(float(r["label"])); r["score"] = float(r["score"])
            except Exception:
                continue
            rows.append(r)
    return rows


def _selftest():
    rng = np.random.default_rng(0)
    rows = []
    # real (genuine) — low scores
    for i in range(400):
        rows.append({"label": 0, "score": float(np.clip(rng.normal(0.12, 0.10), 0, 1)),
                     "generator": "real", "language": rng.choice(["hi", "bn", "ta"]),
                     "seen": 1})
    # SEEN generators — model separates them well (low EER)
    for gen in ["mms-tts", "xtts"]:
        for i in range(200):
            rows.append({"label": 1, "score": float(np.clip(rng.normal(0.88, 0.10), 0, 1)),
                         "generator": gen, "language": rng.choice(["hi", "bn", "ta"]), "seen": 1})
    # UNSEEN generators — model is much weaker (scores overlap real -> high EER)
    for gen in ["elevenlabs", "cartesia"]:
        for i in range(200):
            rows.append({"label": 1, "score": float(np.clip(rng.normal(0.55, 0.22), 0, 1)),
                         "generator": gen, "language": rng.choice(["hi", "bn", "ta"]), "seen": 0})
    report(rows)
    logo(rows)
    # sanity: unseen EER must exceed seen EER (a positive, meaningful gap)
    seen = [r for r in rows if r["seen"] == 1]; unseen = [r for r in rows if r["seen"] == 0]
    real = [r for r in rows if r["label"] == 0]
    es = eer([r["label"] for r in seen], [r["score"] for r in seen])
    eu = eer([r["label"] for r in (real + unseen)], [r["score"] for r in (real + unseen)])
    assert eu > es, "self-test expects a positive generalization gap"
    print("\n[selftest] PASS — unseen-generator EER > seen-generator EER (gap detected & reported).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--logo", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest(); return
    if not a.csv:
        ap.error("provide --csv PATH or --selftest")
    rows = load_csv(a.csv)
    if not rows:
        print("no valid rows"); sys.exit(1)
    report(rows)
    if a.logo:
        logo(rows)


if __name__ == "__main__":
    main()
