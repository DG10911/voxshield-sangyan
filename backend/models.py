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
        self._ort = None
        self._ext = None
        self._tried = False

    def _onnx_dir(self):
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "onnx")
        return os.path.normpath(os.path.join(base, self.model_id.replace("/", "_")))

    def _load(self):
        if self._tried:
            return self._pipe if self._pipe is not None else ("onnx" if self._ort is not None else None)
        self._tried = True
        if os.environ.get("VOXSHIELD_DISABLE_ML") == "1":
            return None
        d = self._onnx_dir()
        if os.path.isfile(os.path.join(d, "model.onnx")):   # fast int8/ONNX CPU path
            try:
                from optimum.onnxruntime import ORTModelForAudioClassification
                from transformers import AutoFeatureExtractor
                self._ort = ORTModelForAudioClassification.from_pretrained(d)
                self._ext = AutoFeatureExtractor.from_pretrained(d)
                print(f"[VoxShield] loaded ONNX {self.model_id}")
                return "onnx"
            except Exception as e:
                print(f"[VoxShield] ONNX failed {self.model_id}: {str(e)[:70]}")
        try:
            from transformers import pipeline
            import torch
            dev = 0 if torch.cuda.is_available() else -1
            self._pipe = pipeline("audio-classification", model=self.model_id, device=dev)
            print(f"[VoxShield] loaded {self.model_id} (device={dev})")
        except Exception as e:
            print(f"[VoxShield] skip {self.model_id} ({e.__class__.__name__})")
            self._pipe = None
        return self._pipe

    def fake_prob(self, y, sr):
        loaded = self._load()
        if loaded == "onnx" and self._ort is not None:
            try:
                import torch
                inputs = self._ext(y.astype("float32"), sampling_rate=sr, return_tensors="pt")
                logits = self._ort(**inputs).logits
                probs = torch.softmax(logits, -1)[0].cpu().numpy()
                id2 = self._ort.config.id2label
                fake = 0.0
                for i, lab in id2.items():
                    l = str(lab).lower()
                    if any(t in l for t in ("fake", "spoof", "synthetic", "deepfake", "ai")):
                        fake = max(fake, float(probs[i]))
                if fake == 0.0:
                    for i, lab in id2.items():
                        if any(t in str(lab).lower() for t in ("real", "bona", "genuine", "human")):
                            fake = max(fake, 1.0 - float(probs[i]))
                return float(fake)
            except Exception as e:
                print(f"[VoxShield] onnx inference failed {self.model_id}: {str(e)[:70]}")
                return None
        pipe = self._pipe
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
