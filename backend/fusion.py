"""
VoxShield — fusion engine.

Combines:
  (a) every available detector's spoof probability (model fusion), and
  (b) the trainable LFCC/CQCC fusion head (if a trained model exists),
into one calibrated risk score, with reason codes and a verdict.

Also provides sliding-window streaming so a decision can fire within the
first ~10 seconds of a call (evidence accumulation).
"""
from __future__ import annotations
import os, json
import numpy as np
import librosa

from features import extract_features, feature_vector
from models import get_registry
from metrics import PlattCalibrator, LogisticRegressionNP

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
HEAD_PATH = os.path.join(ARTIFACT_DIR, "fusion_head.json")
CAL_PATH = os.path.join(ARTIFACT_DIR, "calibrator.json")

_W = {"hf": 0.28, "phase": 0.20, "prosody": 0.20, "breath": 0.14, "ssl": 0.18}

_head = None
_cal = None
_loaded = False


def _load_trained():
    global _head, _cal, _loaded
    if _loaded:
        return
    _loaded = True
    try:
        if os.path.exists(HEAD_PATH):
            d = json.load(open(HEAD_PATH))
            h = LogisticRegressionNP(len(d["w"])); h.load(d); _head = h
            print("[VoxShield] fusion head loaded.")
    except Exception as e:
        print(f"[VoxShield] no fusion head ({e}).")
    try:
        if os.path.exists(CAL_PATH):
            c = PlattCalibrator(); c.load(json.load(open(CAL_PATH))); _cal = c
            print("[VoxShield] calibrator loaded.")
    except Exception:
        pass


def _reason_codes(feats, ssl_prob):
    hf = float(np.clip(0.6 * feats["hf_energy_ratio"] * 2.2 + 0.4 * feats["hf_regularity"], 0, 1))
    phase = float(np.clip(0.6 * feats["phase_reg"] + 0.4 * feats["spectral_flatness"], 0, 1))
    prosody = float(np.clip((0.025 - feats["f0_jitter"]) / 0.025, 0, 1) * 0.7
                    + (1 - feats["f0_voiced_ratio"]) * 0.3)
    breath = float(np.clip(feats["breath_score"] * 1.3, 0, 1))
    ssl = float(np.clip(ssl_prob if ssl_prob is not None
                        else 0.5 * hf + 0.3 * phase + 0.2 * prosody, 0, 1))
    return {"ssl": round(ssl, 3), "phase": round(phase, 3), "hf": round(hf, 3),
            "prosody": round(prosody, 3), "breath": round(breath, 3)}


def _verdict(score):
    if score >= 0.70:
        return "HIGH", ("Synthetic voice likely. Escalate: trigger step-up "
                        "verification; do not authorise transfer.")
    if score >= 0.40:
        return "MEDIUM", ("Inconclusive. Apply additional verification "
                          "(OTP / knowledge check) before proceeding.")
    return "LOW", "Voice consistent with genuine human speech. Continue standard checks."


def analyze(y, sr):
    """Full fusion on a whole clip."""
    _load_trained()
    feats = extract_features(y, sr)

    # --- model fusion: collect per-detector probabilities ---
    per_model = {}
    weighted, wsum = 0.0, 0.0
    for det in get_registry():
        p = det.fake_prob(y, sr)
        if p is None:
            continue
        per_model[det.name] = round(float(p), 4)
        weighted += det.weight * p; wsum += det.weight
    model_fused = (weighted / wsum) if wsum > 0 else None

    # SSL prob = best neural prob if present, else acoustic
    ssl_prob = None
    for k, v in per_model.items():
        if k != "acoustic-dsp":
            ssl_prob = v if ssl_prob is None else max(ssl_prob, v)

    reasons = _reason_codes(feats, ssl_prob)
    reason_fused = float(np.clip(sum(_W[k] * reasons[k] for k in _W), 0, 1))

    # --- trainable fusion head over LFCC/CQCC features ---
    head_prob = None
    if _head is not None:
        try:
            head_prob = float(_head.predict_proba(feature_vector(y, sr)[None, :])[0])
            per_model["fusion-head(LFCC+CQCC)"] = round(head_prob, 4)
        except Exception:
            pass

    # --- final fusion (recall-aware) ---
    parts, ws = [], []
    if model_fused is not None: parts.append(model_fused); ws.append(0.5)
    parts.append(reason_fused); ws.append(0.3)
    if head_prob is not None: parts.append(head_prob); ws.append(0.4)
    ws = np.array(ws) / np.sum(ws)
    base = float(np.clip(np.dot(parts, ws), 0, 1))
    if _cal is not None:
        base = float(_cal.transform([base])[0])

    # Fraud is a high-recall problem: a confident fake signal from any trusted
    # detector must NOT be averaged away. We blend the weighted mean with the
    # strongest fake vote so a high-quality clone (caught by one model) still
    # escalates. False alarms only trigger step-up verification, never a block.
    signals = [v for v in per_model.values()]
    if head_prob is not None: signals.append(head_prob)
    mx = max(signals) if signals else base
    score = float(np.clip(0.45 * base + 0.55 * mx, 0, 1))

    label, action = _verdict(score)
    return {
        "score": round(score, 4),
        "label": label, "action": action,
        "confidence": round(max(score, 1 - score) * 100, 1),
        "reasons": reasons,
        "per_model": per_model,
        "fusion": {"model_fused": None if model_fused is None else round(model_fused, 4),
                   "reason_fused": round(reason_fused, 4),
                   "head": None if head_prob is None else round(head_prob, 4),
                   "calibrated": _cal is not None},
        "features": feats,
        "n_models": len(per_model),
    }


def stream_analyze(y, sr, win_s=3.0, hop_s=1.0, threshold=0.70, max_s=10.0):
    """Sliding-window evidence accumulation -> decision within `max_s`.
    Returns the timeline + time-to-flag (mirrors a live call)."""
    win, hop = int(win_s * sr), int(hop_s * sr)
    timeline, acc, flagged_at = [], [], None
    t = 0.0; start = 0
    while start < len(y) and t <= max_s:
        seg = y[start:start + win]
        if len(seg) < sr // 2:
            break
        r = analyze(seg, sr)
        acc.append(r["score"])
        running = float(np.mean(acc[-3:]))   # accumulate recent evidence
        t = round((start + win) / sr, 2)
        point = {"t": t, "window_score": r["score"], "running": round(running, 4),
                 "label": r["label"]}
        timeline.append(point)
        if flagged_at is None and running >= threshold:
            flagged_at = t
        start += hop
    final = analyze(y, sr)
    final["timeline"] = timeline
    final["flagged_at_s"] = flagged_at
    final["decided_within_10s"] = bool(flagged_at is not None and flagged_at <= 10.0)
    return final
