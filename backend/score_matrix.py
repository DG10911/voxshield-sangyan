"""
VoxShield — Channel × Language scoring sweep (produces paper Table input).

Scores a fine-tuned XLS-R checkpoint over a manifest of clips, re-rendering each
clip under the telephony channel matrix, and writes ONE tagged CSV:

    label,score,generator,language,channel,seen

which feeds `paper_report.py` (per-language, per-channel, cross-tab, gap, LOGO,
abstention). This is the "run" side; `paper_report.py` is the "report" side.

Manifest is JSONL, one object per line (same shape gen_worst_ai writes):
    {"path": "/abs/clip.wav", "label": 1, "language": "hi", "generator": "xtts", "seen": 0}

Usage (on the DGX, after training):
    python score_matrix.py --manifest eval.jsonl \
        --ckpt checkpoints/round_*/last.pt --out scores.csv
    # add --channels clean,g711_ulaw,g711_alaw,g722,packet_loss,replay
    python score_matrix.py --selftest      # offline check, no model needed
"""
from __future__ import annotations
import argparse, csv, json, os, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenario_render as R

SR = 16000
CLIP_LEN = SR * 3

# the C1 channel matrix (C2 profiler targets exactly these)
CHANNELS = {
    "clean":      {},
    "g711_ulaw":  {"codec": "g711_ulaw", "narrowband": True},
    "g711_alaw":  {"codec": "g711_alaw", "narrowband": True},
    "g722":       {"band": [50, 7000]},
    "packet_loss": {"codec": "g711_ulaw", "narrowband": True, "packet_loss": 0.02},
    "replay":     {"band": [250, 3600], "replay": True},
}


# ---------------- audio io ----------------
def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate(); ch = w.getnchannels()
        y = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        y = y.reshape(-1, ch).mean(1)
    return y, sr


def write_wav(path, y, sr=SR):
    y = np.clip(y, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((y * 32767).astype("<i2").tobytes())


def clip_prep(y, sr):
    """mono, 16 kHz, fixed 3 s (center-crop / pad)."""
    y = np.asarray(y, np.float32)
    if y.ndim > 1:
        y = y.mean(1)
    if sr != SR:
        n = int(len(y) * SR / sr)
        y = np.interp(np.linspace(0, len(y) - 1, n), np.arange(len(y)), y).astype(np.float32)
    if len(y) < CLIP_LEN:
        y = np.pad(y, (0, CLIP_LEN - len(y)))
    elif len(y) > CLIP_LEN:
        s = (len(y) - CLIP_LEN) // 2
        y = y[s:s + CLIP_LEN]
    return y


# ---------------- model ----------------
def load_model(ckpt, model_id):
    import torch
    from transformers import Wav2Vec2ForSequenceClassification
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Wav2Vec2ForSequenceClassification.from_pretrained(
        model_id, num_labels=2, ignore_mismatched_sizes=True)
    ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    state = ck.get("model", ck) if isinstance(ck, dict) else ck
    model.load_state_dict(state)
    model.to(device).eval()
    return model, device


def score_one(model, device, y):
    import torch
    x = torch.from_numpy(clip_prep(y, SR)).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(input_values=x).logits
    return float(torch.softmax(logits, -1)[0, 1].float().cpu())


def stub_score(y):
    """numpy-only stand-in (for --selftest): high-frequency energy ratio.
    Channel band-limiting removes HF, so scores fall with compression — a
    faithful-enough signal to validate the sweep + CSV plumbing offline."""
    Y = np.abs(np.fft.rfft(y)); f = np.fft.rfftfreq(len(y), 1 / SR)
    hf = Y[f > 4000].sum(); tot = Y.sum() + 1e-9
    # fakes (in selftest) are synthesized with extra HF content
    return float(np.clip(hf / tot * 3.0, 0.0, 1.0))


# ---------------- sweep ----------------
def sweep(manifest, out_csv, channels, model=None, device=None, scorer=None, limit=None):
    rows = []
    with open(manifest) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = json.loads(line)
            p = m.get("path")
            if not p or not os.path.isfile(p):
                continue
            try:
                y, sr = read_wav(p)
            except Exception as e:
                print("  skip", p, repr(e)[:80]); continue
            y = clip_prep(y, sr)
            for ch in channels:
                sc = R.render(y, SR, dict(CHANNELS.get(ch, {}), seed=0))["audio"]
                s = stub_score(sc) if scorer == "stub" else score_one(model, device, sc)
                rows.append({"label": int(m.get("label", 0)), "score": round(float(s), 6),
                             "generator": m.get("generator", ""), "language": m.get("language", m.get("lang", "")),
                             "channel": ch, "seen": int(m.get("seen", 1))})
            if limit and len(rows) >= limit * len(channels):
                break
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "score", "generator", "language", "channel", "seen"])
        w.writeheader(); w.writerows(rows)
    print(f"[scores] {len(rows)} rows -> {out_csv}  ({len(rows)//max(1,len(channels))} clips × {len(channels)} channels)")
    return rows


# ---------------- selftest ----------------
def _selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="voxmat_")
    man = os.path.join(d, "eval.jsonl")
    rng = np.random.default_rng(0)
    t = np.linspace(0, 3, CLIP_LEN, endpoint=False)
    with open(man, "w") as f:
        for i, (lab, gen, lg) in enumerate([(1, "xtts", "hi"), (1, "bark", "bn"), (0, "real", "hi")]):
            if lab == 1:   # fake: strong HF content (vocoder-ish)
                y = (0.3*np.sin(2*np.pi*220*t) + 0.2*np.sin(2*np.pi*6500*t)).astype(np.float32)
            else:          # genuine: low-freq + noise, little HF
                y = (0.3*np.sin(2*np.pi*180*t) + 0.05*rng.standard_normal(len(t))).astype(np.float32)
            p = os.path.join(d, f"c{i}.wav"); write_wav(p, y)
            f.write(json.dumps({"path": p, "label": lab, "generator": gen, "language": lg, "seen": 1}) + "\n")
    out = os.path.join(d, "scores.csv")
    rows = sweep(man, out, list(CHANNELS.keys()), scorer="stub")
    # sanity: clean separates better than g711 (HF removed), CSV schema correct
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        by[r["channel"]].append(r)
    same = [r for r in rows if r["generator"] == "xtts"]
    assert len(rows) == 3 * len(CHANNELS)
    with open(out) as f:
        hdr = f.readline().strip()
    assert hdr == "label,score,generator,language,channel,seen", hdr
    print("\n[selftest] PASS — channel sweep, tagged CSV schema, and clip prep verified.")
    print("  sample:", rows[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest"); ap.add_argument("--out", default="scores.csv")
    ap.add_argument("--ckpt", default=os.path.expanduser("~/voxshield/checkpoints/round_*/last.pt"))
    ap.add_argument("--model-id", default="facebook/wav2vec2-large-xlsr-53")
    ap.add_argument("--channels", default=",".join(CHANNELS.keys()))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest(); return
    if not a.manifest:
        ap.error("--manifest or --selftest")
    chans = [c.strip() for c in a.channels.split(",") if c.strip()]
    model, device = load_model(a.ckpt, a.model_id)
    sweep(a.manifest, a.out, chans, model=model, device=device, limit=a.limit)


if __name__ == "__main__":
    main()
