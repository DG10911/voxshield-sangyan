"""
VoxShield — evaluation metrics & score calibration (pure numpy).
EER, a simplified min t-DCF, and Platt (logistic) calibration.
"""
from __future__ import annotations
import numpy as np


def compute_eer(scores, labels):
    """labels: 1 = spoof/fake (positive), 0 = bonafide. Returns (eer, threshold)."""
    scores = np.asarray(scores, float); labels = np.asarray(labels, int)
    order = np.argsort(scores)
    s = scores[order]; l = labels[order]
    P = (labels == 1).sum(); N = (labels == 0).sum()
    if P == 0 or N == 0:
        return float("nan"), float("nan")
    # sweep thresholds = each unique score
    fars, frrs, thr = [], [], []
    for t in np.unique(scores):
        far = np.mean(scores[labels == 0] >= t)   # bonafide called fake
        frr = np.mean(scores[labels == 1] < t)    # fake called bonafide
        fars.append(far); frrs.append(frr); thr.append(t)
    fars = np.array(fars); frrs = np.array(frrs); thr = np.array(thr)
    i = np.nanargmin(np.abs(fars - frrs))
    eer = (fars[i] + frrs[i]) / 2
    return float(eer), float(thr[i])


def min_tdcf(scores, labels, p_spoof=0.05, c_miss=1.0, c_fa=10.0):
    """Simplified detection cost function over the CM scores."""
    scores = np.asarray(scores, float); labels = np.asarray(labels, int)
    best = np.inf
    for t in np.unique(scores):
        p_miss = np.mean(scores[labels == 1] < t)        # missed spoof
        p_fa = np.mean(scores[labels == 0] >= t)          # false alarm
        cost = p_spoof * c_miss * p_miss + (1 - p_spoof) * c_fa * p_fa
        best = min(best, cost)
    norm = min(p_spoof * c_miss, (1 - p_spoof) * c_fa)
    return float(best / (norm + 1e-9))


def full_report(scores, labels, thr=0.5):
    """Comprehensive metrics. labels: 1=spoof/fake, 0=bonafide.
    Returns dict: eer, min_tdcf, accuracy, precision, recall, f1,
    balanced_acc, auc, tp/tn/fp/fn."""
    import numpy as _np
    s = _np.asarray(scores, float); y = _np.asarray(labels, int)
    eer, eer_thr = compute_eer(s, y)
    tdcf = min_tdcf(s, y)
    pred = (s >= thr).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    acc = (tp + tn) / max(len(y), 1)
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)
    tnr = tn / max(tn + fp, 1); bal = (rec + tnr) / 2
    # AUC via rank statistic (Mann-Whitney)
    pos = s[y == 1]; neg = s[y == 0]
    if len(pos) and len(neg):
        order = _np.argsort(_np.concatenate([pos, neg]))
        ranks = _np.empty_like(order, float); ranks[order] = _np.arange(1, len(order) + 1)
        auc = (ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
    else:
        auc = float("nan")
    return {"eer": eer, "eer_thr": eer_thr, "min_tdcf": tdcf, "accuracy": acc,
            "precision": prec, "recall": rec, "f1": f1, "balanced_acc": bal,
            "auc": float(auc), "tp": tp, "tn": tn, "fp": fp, "fn": fn}


def print_report(name, scores, labels, thr=0.5):
    r = full_report(scores, labels, thr)
    print(f"  ── {name} ──")
    print(f"     EER {r['eer']*100:.2f}%  min t-DCF {r['min_tdcf']:.3f}  AUC {r['auc']:.3f}")
    print(f"     Acc {r['accuracy']*100:.2f}%  Prec {r['precision']*100:.2f}%  "
          f"Recall {r['recall']*100:.2f}%  F1 {r['f1']*100:.2f}%  BalAcc {r['balanced_acc']*100:.2f}%")
    print(f"     Confusion: TP {r['tp']}  TN {r['tn']}  FP {r['fp']}  FN {r['fn']}")
    return r


class PlattCalibrator:
    """1-D logistic calibration:  p = sigmoid(a*score + b)."""
    def __init__(self): self.a, self.b = 1.0, 0.0

    def fit(self, scores, labels, lr=0.1, iters=2000):
        x = np.asarray(scores, float); y = np.asarray(labels, float)
        a, b = 1.0, 0.0
        for _ in range(iters):
            p = 1 / (1 + np.exp(-(a * x + b)))
            ga = np.mean((p - y) * x); gb = np.mean(p - y)
            a -= lr * ga; b -= lr * gb
        self.a, self.b = float(a), float(b)
        return self

    def transform(self, s):
        s = np.asarray(s, float)
        return 1 / (1 + np.exp(-(self.a * s + self.b)))

    def dump(self): return {"a": self.a, "b": self.b}

    def load(self, d): self.a, self.b = d["a"], d["b"]; return self


class LogisticRegressionNP:
    """Tiny numpy logistic regression = the trainable FUSION HEAD."""
    def __init__(self, n_features):
        self.w = np.zeros(n_features); self.b = 0.0
        self.mu = np.zeros(n_features); self.sd = np.ones(n_features)

    def fit(self, X, y, lr=0.05, iters=4000, l2=1e-3):
        X = np.asarray(X, float); y = np.asarray(y, float)
        self.mu = X.mean(0); self.sd = X.std(0) + 1e-6
        Xn = (X - self.mu) / self.sd
        w = np.zeros(Xn.shape[1]); b = 0.0
        n = len(y)
        for _ in range(iters):
            z = Xn @ w + b
            p = 1 / (1 + np.exp(-z))
            gw = Xn.T @ (p - y) / n + l2 * w
            gb = np.mean(p - y)
            w -= lr * gw; b -= lr * gb
        self.w, self.b = w, b
        return self

    def predict_proba(self, X):
        X = np.asarray(X, float)
        Xn = (X - self.mu) / self.sd
        return 1 / (1 + np.exp(-(Xn @ self.w + self.b)))

    def dump(self):
        return {"w": self.w.tolist(), "b": float(self.b),
                "mu": self.mu.tolist(), "sd": self.sd.tolist()}

    def load(self, d):
        self.w = np.array(d["w"]); self.b = d["b"]
        self.mu = np.array(d["mu"]); self.sd = np.array(d["sd"]); return self
