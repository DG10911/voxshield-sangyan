"""
VoxShield API — FastAPI service (fusion edition).

  GET  /                  -> bank-grade dashboard
  GET  /api/health        -> status + active detector ensemble
  POST /api/analyze       -> whole-clip fusion verdict + spectrogram + per-model
  POST /api/stream-analyze-> sliding-window timeline + time-to-flag (<10s)
  GET  /api/audit         -> in-memory audit log

Run:  uvicorn app:app --reload --port 8000   (from backend/)
"""
from __future__ import annotations
import time, hashlib, datetime as dt
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool   # parallel calls without blocking

from features import load_audio, mel_spectrogram_png
from fusion import analyze, stream_analyze
from models import get_registry

app = FastAPI(title="VoxShield Audio Forensics API", version="3.0.0")
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
AUDIT: list[dict] = []


@app.get("/api/health")
def health():
    dets = get_registry()
    active = [d.name for d in dets]
    neural = [n for n in active if n != "acoustic-dsp"]
    return {
        "status": "live",
        "model": "Fusion ensemble · XLS-R + AASIST family",
        "detectors": active,
        "ensemble_size": len(active),
        "neural_active": len(neural) > 0,
        "time": dt.datetime.now().isoformat(timespec="seconds"),
    }


def _audit(filename, raw, result, latency, mode):
    digest = hashlib.sha256(raw).hexdigest()[:16]
    AUDIT.insert(0, {
        "time": dt.datetime.now().strftime("%H:%M:%S"),
        "file": filename or "stream", "audio_sha256": digest,
        "label": result["label"], "score": result["score"],
        "confidence": result["confidence"], "latency_s": latency,
        "n_models": result.get("n_models"), "mode": mode,
    })
    del AUDIT[200:]
    return digest


@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    raw = await file.read()
    if not raw:
        raise HTTPException(400, "Empty upload.")
    t0 = time.perf_counter()
    try:
        y, sr = load_audio(raw)
    except Exception as e:
        raise HTTPException(415, f"Could not decode audio: {e}")
    result = await run_in_threadpool(analyze, y, sr)
    spec = await run_in_threadpool(mel_spectrogram_png, y, sr)
    latency = round(time.perf_counter() - t0, 3)
    digest = _audit(file.filename, raw, result, latency, "clip")
    return JSONResponse({**result, "spectrogram": spec, "latency_s": latency,
                         "audio_sha256": digest})


@app.post("/api/stream-analyze")
async def stream_audio(file: UploadFile = File(...),
                       threshold: float = Query(0.70)):
    raw = await file.read()
    if not raw:
        raise HTTPException(400, "Empty upload.")
    t0 = time.perf_counter()
    try:
        y, sr = load_audio(raw)
    except Exception as e:
        raise HTTPException(415, f"Could not decode audio: {e}")
    result = await run_in_threadpool(stream_analyze, y, sr, 3.0, 1.0, threshold)
    spec = await run_in_threadpool(mel_spectrogram_png, y, sr)
    latency = round(time.perf_counter() - t0, 3)
    digest = _audit(file.filename, raw, result, latency, "stream")
    return JSONResponse({**result, "spectrogram": spec, "latency_s": latency,
                         "audio_sha256": digest})


@app.get("/api/audit")
def audit():
    return {"entries": AUDIT[:50]}


if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")


@app.get("/")
def index():
    idx = FRONTEND / "index.html"
    return FileResponse(str(idx)) if idx.exists() else {"message": "API running", "docs": "/docs"}
