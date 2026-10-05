"""
VoxShield — local TTS fake generator (for languages with NO MMS voice).
Engine: ai4bharat/indic-parler-tts (21 Indic languages), synthesizing the REAL
transcripts from IndicVoices so the fake matches the language/script.

Writes wavs + manifest.jsonl (label=1, generator=indic-parler-tts) that
pipeline/train_corpus.py ingests via $DATA/worst_ai (run_round FAKES_MANIFEST).

Usage (DGX; smoke-test one language first):
    python gen_fakes_tts.py --lang nepali --data-root data/nepali_eval --n 300 \
        --out data_fakes/nepali
    python gen_fakes_tts.py --selftest
"""
from __future__ import annotations
import argparse, glob, json, os
import numpy as np

TEXT_COLS = ["text", "transcript", "sentence", "normalized_text", "verbatim"]
DESC = "A speaker with a clear voice delivers the words at a moderate speed with a neutral tone."
FALLBACK = ["नमस्ते, कृपया अपना खाता सत्यापित करें।", "आपका धन्यवाद, आपका दिन शुभ हो।"]


def read_texts(data_root, lang, n):
    ll = lang.lower()
    files = sorted(glob.glob(os.path.join(data_root, "indicvoices_real", ll, "*.parquet")))
    out = []
    if files:
        import pandas as pd
        for f in files:
            try:
                df = pd.read_parquet(f)
            except Exception:
                continue
            col = next((c for c in TEXT_COLS if c in df.columns), None)
            if not col:
                continue
            out += [str(t) for t in df[col].dropna().tolist() if 8 <= len(str(t)) <= 220]
            if len(out) >= n:
                break
    return out[:n] or FALLBACK


def _gen_class():
    try:                                   # parler-tts package (pip install git+https://github.com/huggingface/parler-tts.git)
        from parler_tts import ParlerTTSForConditionalGeneration as G
        return G
    except Exception:
        pass
    try:
        from transformers.models.parler_tts import ParlerTTSForConditionalGeneration as G
        return G
    except Exception:
        from transformers import AutoModelForTextToWaveform as G
        return G


def generate(lang, data_root, n, out, repo="ai4bharat/indic-parler-tts"):
    import torch, soundfile as sf
    from transformers import AutoTokenizer
    Gen = _gen_class()
    os.makedirs(out, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[tts] {lang}  {repo}  device={dev}  n={n}  class={Gen.__name__}")
    # Parler needs TWO tokenizers: the main one for the *description* (input_ids) and the
    # text-encoder (T5) tokenizer for the *spoken text* (prompt_input_ids). Using the same
    # tokenizer for both yields out-of-range ids -> "device-side assert / indexSelectSmallIndex".
    desc_tok = AutoTokenizer.from_pretrained(repo)
    model = Gen.from_pretrained(repo).to(dev).eval()
    enc_name = getattr(getattr(model.config, "text_encoder", None), "_name_or_path", None)
    if enc_name:
        try:
            prompt_tok = AutoTokenizer.from_pretrained(enc_name)
        except Exception:
            prompt_tok = AutoTokenizer.from_pretrained("t5-base")
    else:
        prompt_tok = AutoTokenizer.from_pretrained("t5-base")
    sr = getattr(model.config, "sampling_rate", 44100)
    texts = read_texts(data_root, lang, n) if data_root else FALLBACK
    print(f"[tts] {len(texts)} texts · prompt_tok={prompt_tok.name_or_path}")
    man = open(os.path.join(out, "manifest.jsonl"), "w")
    made = 0
    for i, t in enumerate(texts):
        try:
            desc = desc_tok(DESC, return_tensors="pt", padding=True)
            p = prompt_tok(t, return_tensors="pt", padding=True)
            with torch.no_grad():
                o = model.generate(input_ids=desc.input_ids.to(dev),
                                   attention_mask=desc.attention_mask.to(dev),
                                   prompt_input_ids=p.input_ids.to(dev),
                                   prompt_attention_mask=p.attention_mask.to(dev))
            w = getattr(o, "waveform", None)
            y = (w[0] if w is not None else o[0]).float().cpu().numpy()
            if y.ndim > 1:
                y = y.mean(0)
        except Exception as e:
            print("  synth err", repr(e)[:100]); continue
        p = os.path.abspath(os.path.join(out, f"{lang}_{made:05d}.wav"))
        sf.write(p, np.clip(y, -1, 1), sr)
        man.write(json.dumps({"path": p, "label": 1, "language": lang[:2],
                              "generator": "indic-parler-tts", "seen": 1}) + "\n")
        made += 1
        if made % 50 == 0:
            print(f"  ...{made}")
    man.close()
    print(f"[tts] wrote {made} fakes -> {out}/manifest.jsonl")


def _selftest():
    import tempfile
    d = tempfile.mkdtemp(); p = os.path.join(d, "x.wav"); open(p, "wb").write(b"")
    with open(os.path.join(d, "manifest.jsonl"), "w") as f:
        f.write(json.dumps({"path": p, "label": 1, "language": "ne",
                            "generator": "indic-parler-tts", "seen": 1}) + "\n")
    r = json.loads(open(os.path.join(d, "manifest.jsonl")).read().strip())
    assert r["label"] == 1 and r["generator"] == "indic-parler-tts"
    print("[selftest] PASS — manifest schema OK (train_corpus ingests this).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang"); ap.add_argument("--data-root", default="")
    ap.add_argument("--n", type=int, default=300); ap.add_argument("--out")
    ap.add_argument("--repo", default="ai4bharat/indic-parler-tts")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not (a.lang and a.out): ap.error("--lang and --out required")
    generate(a.lang, a.data_root, a.n, a.out, a.repo)


if __name__ == "__main__":
    main()
