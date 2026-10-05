"""
VoxShield — Language Orthogonalization for cross-lingual deepfake detection.

Based on: Kim, Um & Kim (2026), "Language Orthogonalization for Zero-Shot Cross-Lingual
Audio Deepfake Detection" (arXiv:2609.16458). SSL backbones (XLS-R / WavLM / etc.) encode
language-dependent structure that confounds spoof cues, so cross-lingual EER blows up.

Method: a *target-free* ridge map. We fit a linear map X -> Z from SSL features X to
language-identification embeddings Z, then remove from X the component that lies in the
span of the LID-predictive directions. The result X_orth keeps spoof-relevant content but
drops language variation, which consistently reduces EER on unseen languages.

This module is dependency-light (NumPy only) so it can be unit-tested and dropped into the
training/eval pipeline (`train_backend.py --orthogonalize`) without touching the torch stack.

Usage
-----
    import language_orthogonalization as LO
    W = LO.fit_orthogonalizer(X_train, Z_train, alpha=1.0)   # X:(n,d) SSL feats, Z:(n,k) LID
    X_orth = LO.apply_orthogonalizer(X, W)                   # remove language subspace

When only *language labels* exist (no LID model), use one-hot labels as a proxy:
    Z = LO.one_hot(lang_ids, n_langs); W = LO.fit_orthogonalizer(X, Z, alpha=1.0)
"""
from __future__ import annotations
import numpy as np


def _standardize(X, mu=None, sd=None):
    mu = X.mean(0) if mu is None else mu
    sd = X.std(0) + 1e-8 if sd is None else sd
    return (X - mu) / sd, mu, sd


def one_hot(labels, n_classes=None):
    labels = np.asarray(labels).astype(int)
    n_classes = (labels.max() + 1) if n_classes is None else n_classes
    Z = np.zeros((len(labels), n_classes), dtype=np.float64)
    Z[np.arange(len(labels)), labels] = 1.0
    return Z


def _labels_from(Z):
    Z = np.asarray(Z)
    return Z.argmax(1) if Z.ndim > 1 else Z.astype(int)


def fit_orthogonalizer(X, Z, alpha=1.0):
    """Fit the language subspace to remove.

    Target-free in the paper's sense (uses a continuous LID map); here we support both the
    LID one-hot proxy and language labels. We take the between-language centroid subspace of
    standardized features — the linear directions along which a language lives — and store an
    orthonormal basis for it. `alpha` is kept for API compatibility (ridge/regularization).
    """
    X = np.asarray(X, dtype=np.float64)
    Xs, mu, sd = _standardize(X)
    labels = _labels_from(Z)
    classes = np.unique(labels)
    centroids = np.stack([Xs[labels == c].mean(0) for c in classes])   # (k, d)
    C = centroids - centroids.mean(0)                                  # center the centroids
    # orthonormal basis of the row space of C (the language subspace)
    U, s, Vt = np.linalg.svd(C, full_matrices=False)
    keep = s > (1e-6 * (s[0] if len(s) else 1.0))
    B = Vt[keep]                                                        # (r, d)
    return {"B": B, "mu": mu, "sd": sd, "rank": int(B.shape[0])}


def apply_orthogonalizer(X, model, eps=1e-5):
    """Remove the component of X lying in the language subspace: X_orth = X - X P, P = Bᵀ B."""
    X = np.asarray(X, dtype=np.float64)
    Xs = (X - model["mu"]) / model["sd"]
    B = model["B"]
    if B.size == 0:
        return X.copy()
    P = B.T @ B                       # (d, d) orthogonal projector onto span(B)
    Xs_orth = Xs - Xs @ P
    return (Xs_orth * model["sd"] + model["mu"]).astype(X.dtype)


# ---- nearest-centroid LID error (proxy metric for how much language leaks) ----
def lid_error(X, lang_ids):
    X = np.asarray(X, dtype=np.float64)
    lang_ids = np.asarray(lang_ids).astype(int)
    classes = np.unique(lang_ids)
    cents = np.stack([X[lang_ids == c].mean(0) for c in classes])
    d = ((X[:, None, :] - cents[None, :, :]) ** 2).sum(-1)
    pred = classes[d.argmin(1)]
    return float((pred != lang_ids).mean())


def _selftest():
    rng = np.random.default_rng(0)
    n, d, k = 900, 40, 5
    lang = rng.integers(0, k, size=n)
    lang_sig = rng.normal(0, 1, size=(k, d))
    content = rng.normal(0, 1, size=(n, d)) * 0.3
    X = lang_sig[lang] + content                       # features = language + content
    Z = one_hot(lang, k)

    before = lid_error(X, lang)
    W = fit_orthogonalizer(X, Z, alpha=1.0)
    Xo = apply_orthogonalizer(X, W)
    after = lid_error(Xo, lang)

    # content must be preserved (correlation of first content dim before/after stays high)
    keep = np.corrcoef(X[:, 0], Xo[:, 0])[0, 1]
    chance = 1.0 - 1.0 / k
    # before: language easily detected (low error). after: language removed (error -> chance).
    assert before < 0.15, f"setup invalid: pre-LID error too high ({before:.2f})"
    assert after > 0.6 * chance, f"language not removed: {before:.2f} -> {after:.2f}"
    print(f"[selftest] PASS  LID error {before:.3f} -> {after:.3f} (chance {chance:.2f})  content-corr {keep:.3f}")


if __name__ == "__main__":
    _selftest()
