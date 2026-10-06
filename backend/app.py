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

import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool   # parallel calls without blocking

from features import load_audio, mel_spectrogram_png
from fusion import analyze, stream_analyze
from models import get_registry
from voxscore import from_analyze as voxscore_of   # P0: additive meta-uncertainty layer
from orchestrate import run as orchestrate_run     # P2/P3: unified evidence-brain pipeline
import threat_registry                             # P3 §19: living threat intel
from intel_graph import from_threats_and_eval      # P3 §20: queryable intelligence graph
from voxscore import voxscore as voxscore_probs     # score raw per-model dict
from callguard import assess as callguard_assess    # §28 fraud fusion
from telephony_gateway import decide as gateway_decide  # §28 P4 inline decision (never auto-block)
from self_critique import critique as self_critique  # §12 FP-guard
import deployment                                   # §28-29 deploy/product profiles
import warroom                                       # §28 live ops rollup
from consumer import answer as consumer_answer       # §28 P4 "is this voice real?"

app = FastAPI(title="VoxShield Audio Forensics API", version="3.0.0")


@app.middleware("http")
async def _no_cache_html(request, call_next):
    """Never let browsers serve a stale console build."""
    resp = await call_next(request)
    p = request.url.path
    if p.endswith("/") or p.endswith(".html"):
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
    return resp
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
AUDIT: list[dict] = []


@app.get("/api/health")
def health():
    dets = get_registry()
    active = [d.name for d in dets]
    neural = [n for n in active if n != "acoustic-dsp"]
    try:
        import bhashini as _bh
        _bstat = _bh.status(); _bq = _bh.quota_status()
        bhashini = {"mode": _bstat["mode"], "have_keys": _bstat["have_keys"],
                    "calls_used": _bq["used"], "calls_budget": _bq["budget"],
                    "calls_remaining": _bq["remaining"], "services": len(_bstat["services_known"])}
    except Exception as e:
        bhashini = {"error": str(e)[:120]}
    try:
        import speaker_engine as _se
        speakers = _se.available()
    except Exception as e:
        speakers = {"error": str(e)[:120]}
    return {
        "status": "live",
        "model": "Fusion ensemble · XLS-R + AASIST family",
        "detectors": active,
        "ensemble_size": len(active),
        "neural_active": len(neural) > 0,
        "bhashini": bhashini,
        "speaker_backends": speakers,
        "time": dt.datetime.now().isoformat(timespec="seconds"),
    }


def _evidence(y, sr, result, use_bhashini: bool = False, use_diarization: bool = False):
    """P2/P3: unified evidence-brain pipeline + optional Bhashini (ALD/ASR) and
    provider-agnostic speaker diarization. Additive — never overrides the fusion verdict."""
    try:
        o = orchestrate_run(y, sr, detector_probs=result.get("per_model") or None,
                            deep_on_lowrisk=True, use_bhashini=use_bhashini,
                            use_diarization=use_diarization)
        b = o.get("brains", {})
        brains = {
            "human_physics": (b.get("human_physics") or {}).get("hpcs"),
            "replay":        (b.get("replay") or {}).get("replay_score"),
            "environment":   (b.get("environment") or {}).get("svcs"),
            "reverse_time":  (b.get("reverse_time") or {}).get("synthetic_lean"),
            "temporal_dna":  (b.get("temporal_dna") or {}).get("synthetic_lean"),
        }
        bh = o.get("bhashini") or {}
        return {"brains": brains, "arbitration": o.get("arbitration"),
                "unified_verdict": o.get("verdict"), "abstain": o.get("abstain"),
                "language": (o.get("profile") or {}).get("language"),
                "transcript": bh.get("transcript"),
                "diarization": o.get("diarization"),
                "bhashini": bh if use_bhashini else None}
    except Exception as e:
        return {"brains_error": str(e)[:140]}


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
async def analyze_audio(file: UploadFile = File(...), bhashini: bool = Query(False),
                        diarization: bool = Query(False)):
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
    evidence = await run_in_threadpool(_evidence, y, sr, result, bhashini, diarization)
    latency = round(time.perf_counter() - t0, 3)
    digest = _audit(file.filename, raw, result, latency, "clip")
    return JSONResponse({**result, "voxscore": voxscore_of(result), **evidence,
                         "spectrogram": spec, "latency_s": latency,
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
    evidence = await run_in_threadpool(_evidence, y, sr, result)
    latency = round(time.perf_counter() - t0, 3)
    digest = _audit(file.filename, raw, result, latency, "stream")
    return JSONResponse({**result, "voxscore": voxscore_of(result), **evidence,
                         "spectrogram": spec, "latency_s": latency,
                         "audio_sha256": digest})


@app.websocket("/api/ws-stream")
async def ws_stream(ws: WebSocket):
    """P1 (roadmap §29): streaming Detect over WebSocket. Client sends the clip as
    bytes; server emits a per-window verdict as evidence accumulates, then a final
    verdict + VoxScore. Additive — does not affect the REST endpoints."""
    await ws.accept()
    try:
        raw = await ws.receive_bytes()
        y, sr = load_audio(raw)
        win, hop = int(3.0 * sr), int(1.0 * sr)
        start, acc = 0, []
        while start < len(y):
            seg = y[start:start + win]
            if len(seg) < sr // 2:
                break
            r = await run_in_threadpool(analyze, seg, sr)
            acc.append(r["score"]); running = float(np.mean(acc[-3:]))
            await ws.send_json({"t": round((start + win) / sr, 2), "window_score": r["score"],
                                "running": round(running, 4), "label": r["label"]})
            start += hop
        final = await run_in_threadpool(analyze, y, sr)
        await ws.send_json({"final": True, "score": final["score"], "label": final["label"],
                            "action": final["action"], "voxscore": voxscore_of(final)})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"error": str(e)[:120]})
        except Exception:
            pass
    finally:
        try:
            await ws.close()
        except Exception:
            pass


@app.get("/api/audit")
def audit():
    return {"entries": AUDIT[:50]}


@app.get("/api/threats")
def threats(n: int = Query(8, ge=1, le=50)):
    """P3 §19: hardest known generators from the Voice Threat Registry (measured LOGO)."""
    hardest = threat_registry.hardest(n)
    return {"count": len(hardest),
            "hardest": [{"generator": t["generator"],
                         "unseen_eer_pct": (t.get("detection_perf") or {}).get("unseen_eer_pct"),
                         "confidence": t.get("confidence"), "source": t.get("source")}
                        for t in hardest]}


@app.get("/api/intel")
def intel(language: str | None = None, codec: str | None = None,
          worst_by: str | None = None, metric: str = "eer_pct"):
    """P3 §20: query the Generator Intelligence Graph.
      • /api/intel?language=ta&codec=g711_ulaw  → hardest generators under those conditions
      • /api/intel?worst_by=codec&metric=eer_pct → conditions causing the worst metric"""
    g = from_threats_and_eval(threat_registry._load())
    if worst_by:
        return {"worst_conditions": g.worst_conditions(metric=metric, by=worst_by), "graph": g.summary()}
    cond = {k: v for k, v in (("language", language), ("codec", codec)) if v}
    return {"conditions": cond, "graph": g.summary(),
            "hard_under": g.hard_under(cond, metric=metric) if cond else []}


# ----------------------------- Detect API surface (§28) -----------------------------
@app.post("/api/risk/score")
def risk_score(body: dict = Body(...)):
    """Score a raw per-model probability dict → VoxScore + self-critique FP-guard.
    body: {"per_model": {"acoustic-dsp":0.9,...}, "context": {...}}"""
    per_model = body.get("per_model") or {}
    if not per_model:
        raise HTTPException(400, "provide per_model probabilities")
    vs = voxscore_probs(per_model)
    sc = self_critique(vs, body.get("context") or {})
    return {"voxscore": vs, "self_critique": sc if sc.get("applied") else None,
            "final_risk": sc.get("final_risk", vs.get("risk")), "abstain": sc.get("abstain", vs.get("abstain"))}


@app.get("/api/threat/search")
def threat_search(language: str | None = None, min_eer: float = 0.0):
    """§19: search the Voice Threat Registry."""
    return {"threats": threat_registry.query(min_eer=min_eer, language=language)}


@app.post("/api/gateway/decide")
def gateway(body: dict = Body(...)):
    """§28 P4: inline telephony decision (allow/warn/step-up/2FA/transfer) — NEVER auto-blocks.
    body: {"voxscore": {...}, "context": {...}}"""
    vs = body.get("voxscore") or {}
    cg = callguard_assess(vs, body.get("context") or {})
    return {"callguard": cg, "gateway": gateway_decide(vs, cg, body.get("context") or {})}


@app.post("/api/consumer/check")
def consumer_check(body: dict = Body(...)):
    """§28 P4: plain-language 'is this voice real?' from a voxscore. body: {"voxscore": {...}}"""
    return consumer_answer(body.get("voxscore") or body)


@app.get("/api/deployment/profile")
def deployment_profile(surface: str = "cloud"):
    """§28-29: resolve a product surface (cloud/enterprise/indic) to a safe deploy profile."""
    try:
        return deployment.profile(surface)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/warroom")
def warroom_view():
    """§28: live operations rollup over the in-memory audit stream."""
    events = [{"verdict": a.get("label"), "language": None, "score": a.get("score"),
               "latency_s": a.get("latency_s")} for a in AUDIT]
    return warroom.rollup(events)


@app.post("/api/speaker/verify")
async def speaker_verify(reference: UploadFile = File(...), probe: UploadFile = File(...)):
    """§28: one-shot speaker verification (reference vs probe) + anti-spoof on the probe.
    A matching voice that is also synthetic/abstain → REJECT_SPOOF, never a clean pass."""
    from speaker import verify as sv_verify
    ra, pb = await reference.read(), await probe.read()
    if not ra or not pb:
        raise HTTPException(400, "need both reference and probe audio")
    try:
        yr, sr_r = load_audio(ra); yp, sr_p = load_audio(pb)
    except Exception as e:
        raise HTTPException(415, f"decode error: {e}")
    match = await run_in_threadpool(sv_verify, yr, sr_r, yp, sr_p)
    result = await run_in_threadpool(analyze, yp, sr_p)
    vs = voxscore_of(result)
    spoof = (vs.get("synthetic_score", 0) or 0) >= 0.6 or vs.get("abstain", False)
    decision = ("REJECT_IDENTITY" if not match.get("match")
                else "REJECT_SPOOF" if spoof else "VERIFIED")
    return {"speaker_match": match, "anti_spoof_voxscore": vs, "decision": decision,
            "note": "identity=pseudo-embedding (ECAPA pending); liveness=PENDING; decision-support, never auto-block."}


if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")


@app.get("/")
def index():
    idx = FRONTEND / "index.html"
    return FileResponse(str(idx)) if idx.exists() else {"message": "API running", "docs": "/docs"}
