"""VoxShield local API + browser UI.

Start:  ./.venv_voxshield/bin/python voxshield_api.py
Then open http://localhost:8000/ in a browser.
"""
import io, os, time
import numpy as np
import torch
import soundfile as sf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import Wav2Vec2ForSequenceClassification

CKPT = os.path.expanduser("~/voxshield_backup/checkpoints/wav2vec2_xlsr_itw_aug/best.pt")
MODEL_ID = "facebook/wav2vec2-large-xlsr-53"
SR = 16000
CLIP_LEN = SR * 3

if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
print(f"[api] device={device}")

print(f"[api] loading base model...")
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    MODEL_ID, num_labels=2, ignore_mismatched_sizes=True)
print(f"[api] loading fine-tuned weights...")
ck = torch.load(CKPT, map_location="cpu", weights_only=False)
model.load_state_dict(ck["model"])
model.to(device).eval()
print(f"[api] ready. EER_clean={ck.get('eer_clean', '?')}, EER_codec={ck.get('eer_codec', '?')}")

app = FastAPI(title="VoxShield")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


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


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>VoxShield</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 640px; margin: 40px auto;
           padding: 20px; background: #0b0d10; color: #e6e6e6; }
    h1 { margin: 0 0 8px; color: #7fd7ff; }
    .sub { color: #8a8f96; margin-bottom: 24px; font-size: 14px; }
    .card { background: #14181c; border: 1px solid #22282e; border-radius: 10px;
            padding: 20px; margin-bottom: 16px; }
    input[type=file] { padding: 10px; background: #1a1f24; border: 1px dashed #3a4048;
                       border-radius: 8px; width: 100%; color: #e6e6e6; }
    button { background: #7fd7ff; color: #000; border: 0; padding: 10px 20px;
             font-weight: 600; border-radius: 8px; cursor: pointer; margin-top: 12px; }
    button:hover { background: #52c0ff; }
    button:disabled { opacity: 0.5; cursor: wait; }
    .verdict { font-size: 32px; font-weight: 700; margin: 8px 0; }
    .LOW { color: #4ade80; }
    .MEDIUM { color: #facc15; }
    .HIGH { color: #f87171; }
    .row { display: flex; justify-content: space-between; margin: 4px 0;
           font-size: 14px; color: #b0b6bd; }
    .row b { color: #e6e6e6; }
    .hint { color: #8a8f96; font-size: 13px; }
  </style>
</head>
<body>
  <h1>VoxShield</h1>
  <div class="sub">Voice deepfake detector — wav2vec2-XLSR-53, codec-hardened for G.711 phone audio</div>

  <div class="card">
    <input type="file" id="f" accept=".wav,.mp3,.flac,.m4a,audio/*">
    <button id="go">Analyze</button>
    <div class="hint" style="margin-top:10px">Or record with mic app / QuickTime and upload the file.</div>
  </div>

  <div class="card" id="out" style="display:none">
    <div class="verdict" id="v"></div>
    <div id="a" class="sub"></div>
    <div class="row"><span>Fake probability</span><b id="score"></b></div>
    <div class="row"><span>Confidence</span><b id="conf"></b></div>
    <div class="row"><span>Latency</span><b id="lat"></b></div>
    <div class="row"><span>Filename</span><b id="fn"></b></div>
  </div>

<script>
const f = document.getElementById('f'), go = document.getElementById('go'),
      out = document.getElementById('out'), v = document.getElementById('v'),
      a = document.getElementById('a');
go.onclick = async () => {
  if (!f.files.length) return alert('pick an audio file first');
  go.disabled = true; go.textContent = 'analyzing...';
  const fd = new FormData(); fd.append('file', f.files[0]);
  try {
    const r = await fetch('/predict', { method:'POST', body: fd });
    const j = await r.json();
    v.textContent = j.label; v.className = 'verdict ' + j.label;
    a.textContent = j.action;
    document.getElementById('score').textContent = j.score;
    document.getElementById('conf').textContent = j.confidence_pct + '%';
    document.getElementById('lat').textContent = j.inference_ms + ' ms';
    document.getElementById('fn').textContent = j.filename;
    out.style.display = 'block';
  } catch (e) { alert('error: ' + e); }
  go.disabled = false; go.textContent = 'Analyze';
};
</script>
</body>
</html>
"""


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        data = await file.read()
        y, sr = sf.read(io.BytesIO(data))
    except Exception as e:
        raise HTTPException(400, f"could not read audio: {e}")
    y = prep(y, sr)
    x = torch.from_numpy(y).unsqueeze(0).to(device)
    t0 = time.time()
    with torch.no_grad():
        logits = model(input_values=x).logits
    probs = torch.softmax(logits, -1)[0].float().cpu().numpy()
    fake = float(probs[1])
    ms = int((time.time() - t0) * 1000)
    if fake >= 0.7:
        label, action = "HIGH", "Synthetic voice likely — block or step-up verify"
    elif fake >= 0.4:
        label, action = "MEDIUM", "Inconclusive — additional verification required"
    else:
        label, action = "LOW", "Voice consistent with human speech"
    return {
        "score": round(fake, 4),
        "label": label,
        "action": action,
        "confidence_pct": round(max(fake, 1 - fake) * 100, 1),
        "inference_ms": ms,
        "backend": "wav2vec2-large-xlsr-53 + G.711 aug",
        "filename": file.filename,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
