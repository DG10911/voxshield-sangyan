"""
VoxShield — super-dataset training / evaluation harness.

Merges multiple datasets into one "super-dataset", applies RawBoost + codec
augmentation, trains the LFCC/CQCC fusion head, calibrates scores, and reports
cross-dataset EER (train on some datasets, test on a held-out one such as
In-the-Wild) — exactly the protocol that wins.

USAGE
-----
1) Real data — give one or more manifest CSVs (columns: path,label,dataset)
   where label is 1=spoof/fake, 0=bonafide:

   python train_fusion.py --train asvspoof19.csv wavefake.csv codecfake.csv \
                          --test  in_the_wild.csv --augment

2) No data yet — prove the whole pipeline end-to-end on synthetic clips:

   python train_fusion.py --selftest

Outputs artifacts/fusion_head.json and artifacts/calibrator.json, which the
running API automatically picks up.
"""
from __future__ import annotations
import os, csv, json, argparse, time
import numpy as np

from features import feature_vector, SR
from augment import augment, codec_8k, rawboost
from metrics import compute_eer, min_tdcf, PlattCalibrator, LogisticRegressionNP
try:
    from metrics import print_report
except Exception:
    print_report = None

ART = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ART, exist_ok=True)


def _read_manifest(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append((r["path"], int(r["label"]), r.get("dataset", os.path.basename(path))))
    return rows


def _load_wav(path, sr=SR):
    import librosa
    y, _ = librosa.load(path, sr=sr, mono=True)
    return y.astype(np.float32)


def build_xy(rows, do_augment=False, limit=None):
    import librosa  # noqa
    X, Y = [], []
    n = 0
    for path, label, ds in rows:
        try:
            y = _load_wav(path)
        except Exception:
            continue
        clips = [y]
        if do_augment:
            clips += [augment(y, SR, which=["rawboost"]),
                      codec_8k(y, SR)]            # robustness copies
        for c in clips:
            X.append(feature_vector(c, SR)); Y.append(label)
        n += 1
        if limit and n >= limit:
            break
    return np.array(X, float), np.array(Y, int)


def synth_clip(fake: bool, sr=SR, dur=3.0):
    """Crude but separable genuine/fake clips for the self-test."""
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    if fake:
        f0 = 150 * np.ones_like(t)                      # steady pitch
        y = 0.5 * np.sin(2 * np.pi * np.cumsum(f0) / sr)
        y += 0.18 * np.sin(2 * np.pi * 7200 * t)        # steady HF vocoder tone
        y += 0.02 * np.random.randn(len(t))
    else:
        f0 = 140 + 8 * np.sin(2 * np.pi * 4 * t) + np.random.randn(len(t)) * 3
        y = 0.5 * np.sin(2 * np.pi * np.cumsum(f0) / sr)
        y *= (1 + 0.2 * np.sin(2 * np.pi * 0.7 * t))    # natural amplitude wobble
        y += 0.05 * np.random.randn(len(t))             # breath-like noise
    return y.astype(np.float32)


def selftest(n=40):
    print("[selftest] synthesising", n * 2, "clips ...")
    X, Y = [], []
    for _ in range(n):
        X.append(feature_vector(synth_clip(True))); Y.append(1)
        X.append(feature_vector(synth_clip(False))); Y.append(0)
    X = np.array(X); Y = np.array(Y)
    # split
    idx = np.random.permutation(len(Y)); tr, te = idx[: int(.7 * len(Y))], idx[int(.7 * len(Y)):]
    head = LogisticRegressionNP(X.shape[1]).fit(X[tr], Y[tr])
    raw = head.predict_proba(X[te])
    eer, thr = compute_eer(raw, Y[te])
    cal = PlattCalibrator().fit(head.predict_proba(X[tr]), Y[tr])
    tdcf = min_tdcf(raw, Y[te])
    json.dump(head.dump(), open(os.path.join(ART, "fusion_head.json"), "w"))
    json.dump(cal.dump(), open(os.path.join(ART, "calibrator.json"), "w"))
    print(f"[selftest] features/clip = {X.shape[1]}")
    print(f"[selftest] held-out EER = {eer*100:.2f}%  min t-DCF = {tdcf:.3f}  thr = {thr:.3f}")
    print(f"[selftest] saved artifacts -> {ART}")
    return eer


def run(train_csvs, test_csvs, do_augment, limit):
    train_rows = [r for c in train_csvs for r in _read_manifest(c)]
    print(f"[train] {len(train_rows)} files from {len(train_csvs)} datasets "
          f"(augment={do_augment})")
    Xtr, Ytr = build_xy(train_rows, do_augment, limit)
    if len(Xtr) == 0:
        print("[train] no usable audio — falling back to self-test.")
        return selftest()

    # If no held-out test set was given, auto-split 80/20 for an honest EER.
    Xhold = Yhold = None
    if not test_csvs:
        idx = np.random.permutation(len(Ytr))
        cut = int(0.8 * len(idx))
        tr, ho = idx[:cut], idx[cut:]
        Xhold, Yhold = Xtr[ho], Ytr[ho]
        Xtr, Ytr = Xtr[tr], Ytr[tr]
        print(f"[train] auto-split: {len(Ytr)} train / {len(Yhold)} held-out")

    head = LogisticRegressionNP(Xtr.shape[1]).fit(Xtr, Ytr)
    cal = PlattCalibrator().fit(head.predict_proba(Xtr), Ytr)
    json.dump(head.dump(), open(os.path.join(ART, "fusion_head.json"), "w"))
    json.dump(cal.dump(), open(os.path.join(ART, "calibrator.json"), "w"))

    eer_in, _ = compute_eer(cal.transform(head.predict_proba(Xtr)), Ytr)
    print(f"[eval] in-domain EER = {eer_in*100:.2f}%")

    if Xhold is not None and len(Yhold):
        p = cal.transform(head.predict_proba(Xhold))
        if print_report:
            print_report(f"held-out (n={len(Yhold)})", p, Yhold)
        else:
            eer, _ = compute_eer(p, Yhold)
            print(f"[eval] held-out EER = {eer*100:.2f}%  (n={len(Yhold)})")

    for c in test_csvs:                       # explicit cross-dataset test sets
        rows = _read_manifest(c)
        Xte, Yte = build_xy(rows, do_augment=False, limit=limit)
        if len(Yte) == 0:
            continue
        p = cal.transform(head.predict_proba(Xte))
        eer, _ = compute_eer(p, Yte); tdcf = min_tdcf(p, Yte)
        print(f"[eval] OUT-OF-DOMAIN {os.path.basename(c)}: "
              f"EER = {eer*100:.2f}%  min t-DCF = {tdcf:.3f}  (n={len(Yte)})")
    print(f"[done] artifacts -> {ART}")


def _auto_from_dir(mdir):
    """Load every *.csv in a folder; auto-hold-out any 'in_the_wild'/'itw' set."""
    import glob
    csvs = sorted(glob.glob(os.path.join(mdir, "*.csv")))
    train = [c for c in csvs if not any(k in os.path.basename(c).lower()
                                        for k in ("in_the_wild", "itw", "wild"))]
    test = [c for c in csvs if c not in train]
    return train, test


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="*", default=[])
    ap.add_argument("--test", nargs="*", default=[])
    ap.add_argument("--manifests-dir", default=None,
                    help="train on every CSV in this folder (auto-holds-out In-the-Wild)")
    ap.add_argument("--augment", action="store_true",
                    help="apply RawBoost + 8kHz codec augmentation to training data")
    ap.add_argument("--limit", type=int, default=None, help="cap files per dataset")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    if a.manifests_dir:
        tr, te = _auto_from_dir(a.manifests_dir)
        if tr:
            print(f"[train] auto: {len(tr)} train CSV(s), {len(te)} held-out CSV(s)")
            run(tr, te, a.augment, a.limit)
        else:
            print("[train] no manifests found; running self-test."); selftest()
    elif a.selftest or not a.train:
        selftest()
    else:
        run(a.train, a.test, a.augment, a.limit)
    print(f"[time] {time.time()-t0:.1f}s")
