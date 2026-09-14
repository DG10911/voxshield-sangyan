"""
VoxShield local test.

Usage:
    python voxshield_test.py                    # runs synthetic demo (clean vs AI voice)
    python voxshield_test.py path/to/clip.wav   # scores a real audio file
"""
import os, sys, time
import numpy as np
import torch
import soundfile as sf
from transformers import Wav2Vec2ForSequenceClassification

CKPT = os.path.expanduser("~/voxshield_backup/checkpoints/wav2vec2_xlsr_itw_aug/best.pt")
MODEL_ID = "facebook/wav2vec2-large-xlsr-53"
SR = 16000
CLIP_SEC = 3.0
CLIP_LEN = int(SR * CLIP_SEC)

if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
print(f"[voxshield] device: {device}")

print(f"[voxshield] loading base model {MODEL_ID} (first run downloads ~1.2 GB)...")
t0 = time.time()
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    MODEL_ID, num_labels=2, ignore_mismatched_sizes=True)
print(f"[voxshield] base loaded in {time.time()-t0:.0f}s")

print(f"[voxshield] loading fine-tuned weights from {CKPT}")
ck = torch.load(CKPT, map_location="cpu", weights_only=False)
model.load_state_dict(ck["model"])
model.to(device).eval()

meta = {k: v for k, v in ck.items() if k not in ("model",)}
print(f"[voxshield] checkpoint EER_clean={meta.get('eer_clean', '?')}, "
      f"EER_codec={meta.get('eer_codec', '?')}, epoch={meta.get('epoch', '?')}")


def prep(y, sr):
    if y.ndim > 1:
        y = y.mean(1)
    y = y.astype("float32")
    if sr != SR:
        import torchaudio.functional as F
        y = F.resample(torch.from_numpy(y), sr, SR).numpy()
    if len(y) < CLIP_LEN:
        y = np.pad(y, (0, CLIP_LEN - len(y)))
    elif len(y) > CLIP_LEN:
        y = y[:CLIP_LEN]
    return y


def score(y):
    x = torch.from_numpy(y).unsqueeze(0).to(device)
    t0 = time.time()
    with torch.no_grad():
        logits = model(input_values=x).logits
    probs = torch.softmax(logits, -1)[0].float().cpu().numpy()
    ms = int((time.time() - t0) * 1000)
    fake_p = float(probs[1])
    if fake_p >= 0.7:
        label, action = "HIGH", "Synthetic voice likely — block / escalate"
    elif fake_p >= 0.4:
        label, action = "MEDIUM", "Inconclusive — extra verification"
    else:
        label, action = "LOW", "Consistent with human speech"
    return {
        "score": round(fake_p, 4),
        "label": label,
        "action": action,
        "confidence": round(max(fake_p, 1 - fake_p) * 100, 1),
        "latency_ms": ms,
    }


def synth(fake, dur=3.0, sr=SR):
    """Crude but separable synthetic clips (mirrors train_fusion.selftest)."""
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    if fake:
        f0 = 150 * np.ones_like(t)
        y = 0.5 * np.sin(2 * np.pi * np.cumsum(f0) / sr)
        y += 0.18 * np.sin(2 * np.pi * 7200 * t)
        y += 0.02 * np.random.randn(len(t))
    else:
        f0 = 140 + 8 * np.sin(2 * np.pi * 4 * t) + np.random.randn(len(t)) * 3
        y = 0.5 * np.sin(2 * np.pi * np.cumsum(f0) / sr)
        y *= (1 + 0.2 * np.sin(2 * np.pi * 0.7 * t))
        y += 0.05 * np.random.randn(len(t))
    return y.astype(np.float32)


print()
if len(sys.argv) > 1:
    path = sys.argv[1]
    y, sr = sf.read(path)
    print(f"[voxshield] scoring {path}  ({len(y)/sr:.1f}s @ {sr} Hz)")
    result = score(prep(y, sr))
    print()
    print(f"  score       : {result['score']}")
    print(f"  label       : {result['label']}")
    print(f"  action      : {result['action']}")
    print(f"  confidence  : {result['confidence']}%")
    print(f"  latency     : {result['latency_ms']} ms")
else:
    print("[voxshield] synthetic self-test — clean human vs synthetic-like voice")
    print()
    for is_fake in (False, True):
        tag = "SYNTHETIC (fake)" if is_fake else "HUMAN (real)"
        y = synth(is_fake)
        r = score(prep(y, SR))
        print(f"  {tag:20s}  score={r['score']:.4f}  label={r['label']:6s}  "
              f"confidence={r['confidence']:.1f}%  latency={r['latency_ms']}ms")
    print()
    print("For a real audio file:  python voxshield_test.py path/to/clip.wav")
