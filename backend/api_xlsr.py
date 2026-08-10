import io, os, time
import numpy as np, torch, soundfile as sf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import Wav2Vec2ForSequenceClassification

MODEL_ID = "facebook/wav2vec2-large-xlsr-53"
CKPT = os.path.expanduser("~/checkpoints/voxshield/wav2vec2_xlsr_itw/best.pt")
SR, CLIP_SEC = 16000, 3.0
CLIP_LEN = int(SR * CLIP_SEC)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[api] device={device}")

print(f"[api] loading base model {MODEL_ID}")
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    MODEL_ID, num_labels=2, ignore_mismatched_sizes=True)

print(f"[api] loading fine-tuned weights {CKPT}")
ck = torch.load(CKPT, map_location=device, weights_only=False)
model.load_state_dict(ck["model"])
model.to(device).eval()
print(f"[api] ready. checkpoint EER={ck.get('eer', '?'):.4f}")

app = FastAPI(title="VoxShield XLSR")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

def clip_prep(y, sr):
    if y.ndim > 1: y = y.mean(1)
    y = y.astype("float32")
    if sr != SR:
        import torchaudio.functional as F
        y = F.resample(torch.from_numpy(y), sr, SR).numpy()
    if len(y) < CLIP_LEN:
        y = np.pad(y, (0, CLIP_LEN - len(y)))
    elif len(y) > CLIP_LEN:
        s = (len(y) - CLIP_LEN) // 2
        y = y[s:s+CLIP_LEN]
    return y

@app.get("/")
def root():
    return {"model": MODEL_ID, "checkpoint_eer": float(ck.get("eer", 0.0)),
            "usage": "POST audio file to /predict"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        data = await file.read()
        y, sr = sf.read(io.BytesIO(data))
    except Exception as e:
        raise HTTPException(400, f"could not read audio: {e}")
    y = clip_prep(y, sr)
    x = torch.from_numpy(y).unsqueeze(0).to(device)
    t0 = time.time()
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        logits = model(input_values=x).logits
    probs = torch.softmax(logits, -1)[0].float().cpu().numpy()
    fake_p = float(probs[1])
    ms = int((time.time() - t0) * 1000)
    if fake_p >= 0.7:
        label, action = "HIGH", "Synthetic voice likely. Escalate: block or step-up verify."
    elif fake_p >= 0.4:
        label, action = "MEDIUM", "Inconclusive. Additional verification required."
    else:
        label, action = "LOW", "Voice consistent with human speech."
    return {
        "score": round(fake_p, 4),
        "label": label,
        "action": action,
        "confidence_pct": round(max(fake_p, 1-fake_p) * 100, 1),
        "inference_ms": ms,
        "backend": "wav2vec2-large-xlsr-53 fine-tuned on ITW",
        "filename": file.filename,
    }
