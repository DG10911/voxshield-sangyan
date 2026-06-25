"""
VoxShield — detector.

Two-track design (mirrors the research strategy):
  PRIMARY  : a HuggingFace wav2vec2 deepfake classifier IF torch+transformers
             and the model are available (set VOXSHIELD_MODEL to override).
  FALLBACK : an explainable acoustic detector built from features.py, so the
             system ALWAYS runs offline with full reason codes.

Both paths return the same contract:
  {score, label, confidence, reasons{...}, backend, features{...}}
score = probability the voice is SYNTHETIC (0 genuine .. 1 fake).
"""
from __future__ import annotations
import os
import numpy as np
from features import extract_features

_HF_MODEL_ID = os.environ.get("VOXSHIELD_MODEL", "MelodyMachine/Deepfake-audio-detection-V2")
_pipe = None
_pipe_tried = False


def _try_load_pipeline():
    """Lazily try to load the neural model; degrade gracefully on any failure."""
    global _pipe, _pipe_tried
    if _pipe_tried:
        return _pipe
    _pipe_tried = True
    if os.environ.get("VOXSHIELD_DISABLE_ML") == "1":
        return None
    try:
        from transformers import pipeline  # noqa
        _pipe = pipeline("audio-classification", model=_HF_MODEL_ID)
        print(f"[VoxShield] Neural detector loaded: {_HF_MODEL_ID}")
    except Exception as e:  # no torch / no internet / no model -> fallback
        print(f"[VoxShield] Neural model unavailable ({e.__class__.__name__}); "
              f"using acoustic detector.")
        _pipe = None
    return _pipe


# ---- reason-code weights for the acoustic detector (sum ~1.0) ----
_W = {"hf": 0.28, "phase": 0.20, "prosody": 0.20, "breath": 0.14, "ssl": 0.18}


def _reason_scores(feats: dict, ssl_fake_prob: float | None) -> dict:
    """Map raw features to 0..1 'how synthetic' sub-scores per reason code."""
    hf = 0.6 * feats["hf_energy_ratio"] * 2.2 + 0.4 * feats["hf_regularity"]
    hf = float(np.clip(hf, 0, 1))

    phase = float(np.clip(feats["spectral_flatness"] * 0.7 +
                          feats["hf_regularity"] * 0.3, 0, 1))

    # genuine speech jitter ~0.01-0.03; very low jitter => synthetic-smooth
    jitter = feats["f0_jitter"]
    prosody = float(np.clip((0.025 - jitter) / 0.025, 0, 1)) * 0.7 \
        + (1.0 - feats["f0_voiced_ratio"]) * 0.3
    prosody = float(np.clip(prosody, 0, 1))

    breath = float(np.clip(feats["breath_score"] * 1.3, 0, 1))

    if ssl_fake_prob is None:
        # derive an SSL-proxy from the acoustic evidence
        ssl = float(np.clip(0.5 * hf + 0.3 * phase + 0.2 * prosody, 0, 1))
    else:
        ssl = float(np.clip(ssl_fake_prob, 0, 1))

    return {"ssl": round(ssl, 3), "phase": round(phase, 3),
            "hf": round(hf, 3), "prosody": round(prosody, 3),
            "breath": round(breath, 3)}


def _fuse(reasons: dict) -> float:
    return float(np.clip(sum(_W[k] * reasons[k] for k in _W), 0, 1))


def analyze(y: np.ndarray, sr: int) -> dict:
    feats = extract_features(y, sr)

    ssl_fake_prob = None
    backend = "acoustic-fallback"
    pipe = _try_load_pipeline()
    if pipe is not None:
        try:
            preds = pipe({"array": y.astype("float32"), "sampling_rate": sr})
            # normalize: find probability of the 'fake/spoof' class
            fake = 0.0
            for p in preds:
                lbl = str(p["label"]).lower()
                if any(t in lbl for t in ("fake", "spoof", "synthetic", "deepfake", "ai")):
                    fake = max(fake, float(p["score"]))
            # some models label 'real'/'bonafide' as positive class
            if fake == 0.0 and preds:
                reals = [float(p["score"]) for p in preds
                         if any(t in str(p["label"]).lower()
                                for t in ("real", "bona", "genuine", "human"))]
                if reals:
                    fake = 1.0 - max(reals)
            ssl_fake_prob = fake
            backend = f"neural:{_HF_MODEL_ID}"
        except Exception as e:
            print(f"[VoxShield] Neural inference failed ({e}); acoustic fallback.")

    reasons = _reason_scores(feats, ssl_fake_prob)
    # if neural model present, let it dominate the fused score
    if ssl_fake_prob is not None:
        score = float(np.clip(0.6 * ssl_fake_prob + 0.4 * _fuse(reasons), 0, 1))
    else:
        score = _fuse(reasons)

    if score >= 0.70:
        label, action = "HIGH", ("Synthetic voice likely. Escalate: trigger step-up "
                                 "verification; do not authorise transfer.")
    elif score >= 0.40:
        label, action = "MEDIUM", ("Inconclusive. Apply additional verification "
                                   "(OTP / knowledge check) before proceeding.")
    else:
        label, action = "LOW", ("Voice consistent with genuine human speech. "
                                "Continue standard checks.")

    confidence = round(max(score, 1 - score) * 100, 1)
    return {
        "score": round(score, 4),
        "label": label,
        "action": action,
        "confidence": confidence,
        "reasons": reasons,
        "features": feats,
        "backend": backend,
    }
