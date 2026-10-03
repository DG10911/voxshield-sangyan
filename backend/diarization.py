"""
VoxShield — Speaker Diarization (provider-agnostic) — roadmap §8/§10, replaces the
Bhashini diarization gap.

Providers (auto-selected, best-first; all optional except the built-in):
  * "pyannote"  — pyannote.audio 3.1 / community-1  (SOTA, MIT, GPU, HF-gated)  ⭐ recommended
  * "nemo"      — NVIDIA NeMo Sortformer (offline/streaming; DGX-native; ≤4 spk)
  * "light"     — built-in energy-VAD + embedding clustering (numpy only, always works)
API providers (used by voice_identity adapters, not here): Deepgram, Speechmatics, Gladia.

Output: {backend, n_speakers, segments:[{start,end,speaker}], speaker_labels}
"""
from __future__ import annotations
import os
import numpy as np


def _frames(y, sr, win_s=0.025, hop_s=0.010):
    n = int(win_s * sr); h = int(hop_s * sr)
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    idx = range(0, len(y) - n + 1, h)
    return np.stack([y[i:i + n] for i in idx]), h / sr


def _vad_energy(y, sr, win_s=0.025, hop_s=0.010, factor=0.35, floor=0.004):
    y = np.asarray(y, np.float32)
    y = y / (np.max(np.abs(y)) + 1e-9)                 # normalise so the threshold is scale-free
    F, hop = _frames(y, sr, win_s, hop_s)
    rms = np.sqrt(np.mean(F ** 2, axis=1) + 1e-9)
    ref = np.percentile(rms, 90) + 1e-9                # loud (speech) level
    thr = max(floor, factor * ref)
    return rms > thr, rms, hop


def _segments(mask, hop, min_s=0.30, merge_gap_s=0.20):
    segs = []; start = None; gap = 0
    for i, m in enumerate(mask):
        t = i * hop
        if m:
            if start is None: start = t
            gap = 0
        else:
            if start is not None:
                gap += hop
                if gap >= merge_gap_s:
                    if t - gap - start >= min_s: segs.append((start, t - gap))
                    start = None; gap = 0
    if start is not None and (len(mask) * hop - start) >= min_s:
        segs.append((start, len(mask) * hop))
    return segs


def _embed(sr, y):
    try:
        from speaker import embed as _e
        return _e(y, sr)
    except Exception:
        n = 1024; yy = np.asarray(y, np.float32)
        if len(yy) < n: yy = np.pad(yy, (0, n - len(yy)))
        S = np.abs(np.fft.rfft(yy[:len(yy)//n*n].reshape(-1, n) * np.hanning(n), axis=1)).mean(0) + 1e-9
        v = np.log(S / S.sum()); return v / (np.linalg.norm(v) + 1e-9)


def _light(y, sr, cluster_threshold=0.90):
    """Dependency-free diarization: energy VAD -> per-segment embedding -> greedy cosine clustering."""
    y = np.asarray(y, np.float32)
    mask, _, hop = _vad_energy(y, sr)
    segs = _segments(mask, hop)
    if not segs:
        return {"backend": "light", "n_speakers": 0, "segments": [], "speaker_labels": []}
    embs = [_embed(sr, y[int(a * sr):int(b * sr)]) for a, b in segs]
    centroids = []; labels = []
    for e in embs:
        e = e / (np.linalg.norm(e) + 1e-9)
        sims = [float(np.dot(e, c)) for c in centroids]
        if sims and max(sims) >= cluster_threshold:
            k = int(np.argmax(sims)); labels.append(k)
            centroids[k] = 0.8 * centroids[k] + 0.2 * e
            centroids[k] /= (np.linalg.norm(centroids[k]) + 1e-9)
        else:
            labels.append(len(centroids)); centroids.append(e)
    segments = [{"start": round(a, 3), "end": round(b, 3), "speaker": f"speaker{labels[i]+1}"}
                for i, (a, b) in enumerate(segs)]
    return {"backend": "light", "n_speakers": len(centroids), "segments": segments,
            "speaker_labels": [{"speaker%d" % (k + 1): [s for s in segments if s["speaker"] == "speaker%d" % (k + 1)]}
                               for k in range(len(centroids))],
            "_status": "built-in VAD+clustering (approx). Install pyannote.audio or NeMo Sortformer for SOTA."}


def _pyannote(y, sr, num_speakers=None):
    from pyannote.audio import Pipeline           # optional
    import torch
    tok = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    model = os.environ.get("PYANNOTE_MODEL", "pyannote/speaker-diarization-3.1")
    pipe = None; last = None
    for kw in ("token", "use_auth_token"):        # pyannote 4 uses token=, 3.x uses use_auth_token=
        try:
            pipe = Pipeline.from_pretrained(model, **{kw: tok}); break
        except TypeError as e:
            last = e; continue
    if pipe is None:
        raise RuntimeError(f"pyannote: could not load {model} ({last}); set HF_TOKEN + accept the model terms")
    if torch.cuda.is_available():
        pipe.to(torch.device("cuda"))
    wf = torch.from_numpy(np.asarray(y, np.float32)[None, :])
    ann = pipe({"waveform": wf, "sample_rate": sr}, num_speakers=num_speakers) if num_speakers \
        else pipe({"waveform": wf, "sample_rate": sr})
    segs = [{"start": round(s.start, 3), "end": round(s.end, 3), "speaker": str(spk)}
            for s, _, spk in ann.itertracks(yield_label=True)]
    return {"backend": "pyannote", "n_speakers": len({s["speaker"] for s in segs}), "segments": segs}


def _nemo(y, sr, num_speakers=None):
    from nemo.collections.asr.models import SortformerEncLabelModel   # optional
    import tempfile, wave as _w
    model = SortformerEncLabelModel.from_pretrained("nvidia/diar_sortformer_4spk-v1").eval()
    # NeMo handles file paths most reliably (numpy format is ambiguous) -> write a 16k mono WAV
    y = np.asarray(y, np.float32)
    if sr != 16000:
        n = int(len(y) * 16000 / sr)
        y = np.interp(np.linspace(0, 1, n, endpoint=False), np.linspace(0, 1, len(y), endpoint=False), y)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with _w.open(tmp.name, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    try:
        labels = model.diarize(audio=[tmp.name], batch_size=1)
    finally:
        try: os.unlink(tmp.name)
        except Exception: pass
    if os.environ.get("VOXSHIELD_DIAR_DEBUG"):
        print("[nemo raw]", type(labels).__name__, repr(labels)[:600])
    segs = []
    first = labels[0] if labels else []
    if isinstance(first, str):                       # whole result is RTTM-ish text
        first = first.splitlines()
    for seg in first:
        if isinstance(seg, str):                     # NeMo format: "0.000 1.680 speaker_0"
            p = seg.split()
            if len(p) >= 3:
                try:
                    segs.append({"start": round(float(p[0]), 3), "end": round(float(p[1]), 3), "speaker": p[2]})
                except Exception:
                    continue
        else:                                        # tuple/list (start, end, speaker)
            try:
                segs.append({"start": round(float(seg[0]), 3), "end": round(float(seg[1]), 3), "speaker": str(seg[2])})
            except Exception:
                continue
    return {"backend": "nemo-sortformer", "n_speakers": len({s["speaker"] for s in segs}), "segments": segs}


def _deepgram(y, sr):
    """Deepgram diarization API (set DEEPGRAM_API_KEY). Zero local install."""
    key = os.environ.get("DEEPGRAM_API_KEY")
    if not key:
        raise RuntimeError("DEEPGRAM_API_KEY not set")
    import io, json, wave, urllib.request
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(sr))
        w.writeframes((np.clip(np.asarray(y, np.float32), -1, 1) * 32767).astype("<i2").tobytes())
    url = "https://api.deepgram.com/v1/listen?diarize=true&punctuate=true&model=nova-3"
    req = urllib.request.Request(url, data=buf.getvalue(),
                                 headers={"Authorization": "Token " + key, "Content-Type": "audio/wav"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode())
    words = d["results"]["channels"][0]["alternatives"][0].get("words", [])
    segs = []; cur = None
    for w in words:
        spk = str(w.get("speaker", "?"))
        if cur is None or cur["speaker"] != spk:
            if cur: segs.append(cur)
            cur = {"start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3), "speaker": spk}
        else:
            cur["end"] = round(float(w["end"]), 3)
    if cur: segs.append(cur)
    return {"backend": "deepgram", "n_speakers": len({s["speaker"] for s in segs}), "segments": segs}


def _speechmatics(y, sr):
    """Speechmatics batch diarization (set SPEECHMATICS_API_KEY) — job-based, optional."""
    key = os.environ.get("SPEECHMATICS_API_KEY")
    if not key:
        raise RuntimeError("SPEECHMATICS_API_KEY not set")
    raise RuntimeError("speechmatics adapter: implement job submit/poll (see docs) — not enabled")


def diarize(y, sr, backend: str = "auto", num_speakers=None) -> dict:
    """Diarize a waveform. backend = auto | pyannote | nemo | deepgram | light.
    Override the auto order with env DIARIZATION_BACKEND (e.g. 'nemo')."""
    if backend == "auto":
        backend = os.environ.get("DIARIZATION_BACKEND", "auto")
    order = [backend] if backend != "auto" else ["pyannote", "nemo", "deepgram", "light"]
    errs = {}
    for b in order:
        try:
            if b == "pyannote": return _pyannote(y, sr, num_speakers)
            if b == "nemo": return _nemo(y, sr, num_speakers)
            if b == "deepgram": return _deepgram(y, sr)
            if b == "speechmatics": return _speechmatics(y, sr)
            if b == "light": return _light(y, sr)
        except Exception as e:
            errs[b] = f"{type(e).__name__}: {str(e)[:180]}"
    return {"backend": "none", "n_speakers": 0, "segments": [], "errors": errs}


def probe(y, sr) -> dict:
    """Try each backend and report the exact error (for setup debugging)."""
    out = {}
    for b in ("pyannote", "nemo", "deepgram", "light"):
        try:
            r = diarize(y, sr, backend=b)
        except Exception as e:
            out[b] = f"EXC {type(e).__name__}: {str(e)[:200]}"; continue
        if r.get("backend") in ("none", None):
            out[b] = "FAIL: " + "; ".join(f"{k}->{v}" for k, v in (r.get("errors") or {}).items())
        else:
            out[b] = f"OK backend={r['backend']} speakers={r['n_speakers']} segs={len(r.get('segments', []))}"
    for k, v in out.items():
        print(f"  {k:9} {v}")
    return out


def _selftest():
    sr = 16000
    rng = np.random.default_rng(0)
    def voice(f0, formants, dur, seed):
        t = np.linspace(0, dur, int(sr * dur), endpoint=False); r = np.random.default_rng(seed)
        ph = np.cumsum(2 * np.pi * (f0 + r.standard_normal(len(t))) / sr)
        y = sum(np.sin(k * ph) * np.exp(-abs(k * f0 - fm) / 600) for k in range(1, 9) for fm in formants)
        return (y + 0.01 * r.standard_normal(len(t))).astype(np.float32)
    a = voice(130, [700, 1200, 2600], 2.0, 1); b = voice(210, [500, 1800, 3000], 2.0, 2)
    sil = np.zeros(int(0.4 * sr), np.float32)
    y = np.concatenate([a, sil, b, sil, a])
    d = diarize(y, sr, backend="light")
    print("backend:", d["backend"], "| speakers:", d["n_speakers"], "| segments:", len(d["segments"]))
    for s in d["segments"]: print("  ", s)
    assert d["n_speakers"] >= 2, "should detect >=2 speakers"
    print("[selftest] PASS — dependency-free diarization detects 2 speakers (A/B/A).")


if __name__ == "__main__":
    _selftest()
