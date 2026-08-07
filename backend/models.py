"""
VoxShield — model registry.

Each detector exposes .name and .fake_prob(y, sr) -> float in [0,1]
(probability the audio is SYNTHETIC). Diverse model families are loaded
when available so their errors decorrelate (the basis of fusion).

  - AcousticDetector     : always available (DSP + reason codes), no downloads.
  - HFDetector(model_id) : HuggingFace audio-classification (wav2vec2/XLS-R/etc.)
                           loaded lazily; silently skipped if torch/transformers
                           or the weights are unavailable.

Default neural ensemble (enabled when `pip install torch transformers`):
  MelodyMachine/Deepfake-audio-detection-V2        (wav2vec2-base)
  Gustking/wav2vec2-large-xlsr-deepfake-audio-classification
  Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild
"""
from __future__ import annotations
import os
import numpy as np
from features import extract_features

DEFAULT_HF_MODELS = [
    "MelodyMachine/Deepfake-audio-detection-V2",
    "Gustking/wav2vec2-large-xlsr-deepfake-audio-classification",
    "Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild",
]


class AcousticDetector:
    name = "acoustic-dsp"
    weight = 0.30

    def fake_prob(self, y, sr):
        f = extract_features(y, sr)
        hf = np.clip(0.6 * f["hf_energy_ratio"] * 2.2 + 0.4 * f["hf_regularity"], 0, 1)
        phase = np.clip(0.6 * f["phase_reg"] + 0.4 * f["spectral_flatness"], 0, 1)
        prosody = np.clip((0.025 - f["f0_jitter"]) / 0.025, 0, 1) * 0.7 \
            + (1 - f["f0_voiced_ratio"]) * 0.3
        breath = np.clip(f["breath_score"] * 1.3, 0, 1)
        return float(np.clip(0.34 * hf + 0.24 * phase + 0.24 * prosody + 0.18 * breath, 0, 1))


class HFDetector:
    weight = 0.5

    def __init__(self, model_id):
        self.name = "hf:" + model_id.split("/")[-1]
        self.model_id = model_id
        self._pipe = None
        self._tried = False

    def _load(self):
        if self._tried:
            return self._pipe
        self._tried = True
        if os.environ.get("VOXSHIELD_DISABLE_ML") == "1":
            return None
        try:
            from transformers import pipeline
            self._pipe = pipeline("audio-classification", model=self.model_id, device=0)
            print(f"[VoxShield] loaded {self.model_id}")
        except Exception as e:
            print(f"[VoxShield] skip {self.model_id} ({e.__class__.__name__})")
            self._pipe = None
        return self._pipe

    def fake_prob(self, y, sr):
        pipe = self._load()
        if pipe is None:
            return None
        try:
            preds = pipe({"array": y.astype("float32"), "sampling_rate": sr})
            fake = 0.0
            for p in preds:
                lbl = str(p["label"]).lower()
                if any(t in lbl for t in ("fake", "spoof", "synthetic", "deepfake", "ai")):
                    fake = max(fake, float(p["score"]))
            if fake == 0.0:
                reals = [float(p["score"]) for p in preds if any(
                    t in str(p["label"]).lower() for t in ("real", "bona", "genuine", "human"))]
                if reals:
                    fake = 1.0 - max(reals)
            return float(fake)
        except Exception as e:
            print(f"[VoxShield] inference failed {self.model_id}: {e}")
            return None


_REGISTRY = None


def get_registry():
    """Build the detector ensemble once."""
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY
    dets = [AcousticDetector()]
    if os.environ.get("VOXSHIELD_DISABLE_ML") != "1":
        ids = os.environ.get("VOXSHIELD_MODELS")
        ids = ids.split(",") if ids else DEFAULT_HF_MODELS
        for mid in ids:
            dets.append(HFDetector(mid.strip()))
    _REGISTRY = dets
    return dets
