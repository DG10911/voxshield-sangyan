"""
VoxShield — multi-generator fake dispatcher.

Training on MANY generators is the strongest lever on unseen-generator EER
(SAFE Challenge, arXiv:2508.20983). This dispatches each language through every
engine that is actually available on the box, then merges the manifests into one
per language.

Engines are best-effort: each runs in try/except and reports `[skip] reason` if its
deps/key/weights are missing, so the pipeline never hard-fails on one engine.

Open/local engines wired here: mms, parler, xtts(coqui), f5(SWivid), kokoro, piper,
indicf5. API engines (need keys via env): sarvam (SARVAM_API_KEY). Everything else in
registries/generators.json is listed in the matrix doc and skipped with a reason.

Usage:
    python backend/gen_fakes_multi.py --lang nepali --n 200 --out data_fakes_multi/nepali
    python backend/gen_fakes_multi.py --lang hindi --n 200 --engines mms,parler,xtts
    python backend/gen_fakes_multi.py --selftest
"""
from __future__ import annotations
import argparse, base64, glob, json, os, subprocess, sys, time

# VoxShield language -> Bhashini TTS language code (IITM TTS: 25 Indic languages)
BHASHINI_CODE = {
    "hindi": "hi", "bengali": "bn", "marathi": "mr", "telugu": "te", "tamil": "ta",
    "gujarati": "gu", "kannada": "kn", "malayalam": "ml", "odia": "or", "punjabi": "pa",
    "urdu": "ur", "sanskrit": "sa", "assamese": "as", "maithili": "mai",
    "bodo": "brx", "dogri": "doi", "kashmiri": "ks", "konkani": "kok",
    "manipuri": "mni", "nepali": "ne", "santali": "sat", "sindhi": "sd", "english": "en",
}

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)


import contextlib, signal


@contextlib.contextmanager
def _deadline(name, secs):
    """Hard per-engine timeout so one hanging engine can never stall the pipeline."""
    if not hasattr(signal, "SIGALRM") or secs <= 0:
        yield; return

    def _h(signum, frame):
        raise TimeoutError(f"engine {name} exceeded {secs}s")

    old = signal.signal(signal.SIGALRM, _h)
    signal.alarm(secs)
    try:
        yield
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, old)


def _texts(lang, n):
    try:
        import gen_fakes_mms as G
        t = G._texts(G.LANGS.get(lang, ("", ""))[0]) or G.FALLBACK_TEXT
    except Exception:
        t = ["नमस्ते, यह एक परीक्षण है।"]
    return [t[i % len(t)] for i in range(n)]


def _write(man, path, lang, engine):
    man.write(json.dumps({"path": os.path.abspath(path), "label": 1,
                          "language": lang[:2], "generator": engine, "seen": 1}) + "\n")


def engine_mms(lang, n, out, man):
    import gen_fakes_mms as G
    G.generate(lang, n, os.path.join(out, "mms"))
    for l in open(os.path.join(out, "mms", "manifest.jsonl")):
        r = json.loads(l); r["generator"] = "mms-tts"; man.write(json.dumps(r) + "\n")


def engine_parler(lang, n, out, man):
    import gen_fakes_tts as G
    d = os.path.join(out, "parler"); os.makedirs(d, exist_ok=True)
    G.generate(lang, os.path.join("data", lang), n, d)
    for l in open(os.path.join(d, "manifest.jsonl")):
        man.write(l)


def engine_xtts(lang, n, out, man):
    from TTS.api import TTS                     # coqui
    import soundfile as sf
    d = os.path.join(out, "xtts"); os.makedirs(d, exist_ok=True)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    spk = tts.speakers[0] if tts.speakers else None
    import gen_fakes_mms as G
    texts = G._texts(G.LANGS.get(lang, ("", ""))[0]) or G.FALLBACK_TEXT
    for i in range(n):
        p = os.path.join(d, f"xtts_{i:05d}.wav")
        tts.tts_to_file(text=texts[i % len(texts)], speaker=spk, language=lang[:2], file_path=p)
        _write(man, p, lang, "xtts_v2")


def engine_f5(lang, n, out, man):
    from f5_tts.api import F5TTS
    import soundfile as sf
    d = os.path.join(out, "f5"); os.makedirs(d, exist_ok=True)
    f5 = F5TTS()
    ref = glob.glob("data/%s/indicvoices_real/**/*.wav" % lang, recursive=True)
    if not ref:
        raise RuntimeError("F5 needs a reference wav (none found)")
    import gen_fakes_mms as G
    texts = G._texts(G.LANGS.get(lang, ("", ""))[0]) or G.FALLBACK_TEXT
    for i in range(n):
        wav, sr, _ = f5.infer(ref_file=ref[0], ref_text="", gen_text=texts[i % len(texts)])
        p = os.path.join(d, f"f5_{i:05d}.wav"); sf.write(p, wav, sr)
        _write(man, p, lang, "f5-tts")


def engine_kokoro(lang, n, out, man):
    from kokoro import KPipeline
    import soundfile as sf, numpy as np
    d = os.path.join(out, "kokoro"); os.makedirs(d, exist_ok=True)
    pipe = KPipeline(lang_code=lang[:1])
    import gen_fakes_mms as G
    texts = G.FALLBACK_TEXT
    for i in range(n):
        for _, _, audio in pipe(texts[i % len(texts)]):
            p = os.path.join(d, f"kokoro_{i:05d}.wav")
            sf.write(p, np.asarray(audio), 24000); _write(man, p, lang, "kokoro"); break


def engine_piper(lang, n, out, man):
    exe = "piper"
    d = os.path.join(out, "piper"); os.makedirs(d, exist_ok=True)
    voice = os.environ.get("PIPER_VOICE", "")
    if not voice:
        raise RuntimeError("set PIPER_VOICE=<path.onnx>")
    import gen_fakes_mms as G
    for i in range(n):
        txt = G.FALLBACK_TEXT[i % len(G.FALLBACK_TEXT)]
        p = os.path.join(d, f"piper_{i:05d}.wav")
        subprocess.run([exe, "-m", voice, "-f", p], input=txt.encode(), check=True)
        _write(man, p, lang, "piper")


def engine_sarvam(lang, n, out, man):
    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        raise RuntimeError("SARVAM_API_KEY not set (Sarvam-TTS is api/proprietary)")
    import urllib.request, base64
    url = os.environ.get("SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech")
    d = os.path.join(out, "sarvam"); os.makedirs(d, exist_ok=True)
    import gen_fakes_mms as G
    for i in range(n):
        body = json.dumps({"inputs": [G.FALLBACK_TEXT[i % len(G.FALLBACK_TEXT)]],
                           "target_language_code": lang[:2] + "-IN" if len(lang[:2]) == 2 else "hi-IN",
                           "speaker": os.environ.get("SARVAM_SPEAKER", "meera")}).encode()
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "api-subscription-key": key})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        aud = data["audios"][0]; raw = base64.b64decode(aud)
        p = os.path.join(d, f"sarvam_{i:05d}.wav"); open(p, "wb").write(raw)
        _write(man, p, lang, "sarvam-tts")


def engine_bhashini(lang, n, out, man):
    """Bhashini TTS (govt ULCA) — covers all Indic incl. the low-res 8. Govt quota."""
    import bhashini as B
    code = BHASHINI_CODE.get(lang, lang[:2])
    d = os.path.join(out, "bhashini"); os.makedirs(d, exist_ok=True)
    texts = _texts(lang, n); made = 0
    for i, t in enumerate(texts):
        for attempt in range(5):
            try:
                r = B.synthesize(t, code, "female")
                aud = r["pipelineResponse"][0]["audio"][0]["audioContent"]
                p = os.path.join(d, f"bhashini_{i:05d}.wav")
                open(p, "wb").write(base64.b64decode(aud)); _write(man, p, lang, "bhashini")
                made += 1; break
            except Exception as e:
                if attempt == 4:
                    print(f"  bhashini err {i}: {str(e)[:70]}"); break
                time.sleep(2 * (attempt + 1))
        if made and made % 25 == 0: print(f"  bhashini ...{made}")
    if made == 0:
        raise RuntimeError("bhashini produced no audio (check BHASHINI keys/code)")


ENGINES = {
    "mms": engine_mms, "parler": engine_parler, "xtts": engine_xtts,
    "f5": engine_f5, "kokoro": engine_kokoro, "piper": engine_piper,
    "sarvam": engine_sarvam, "bhashini": engine_bhashini,
}
DEFAULT = "mms,parler,xtts,f5,kokoro,piper,sarvam"


def run(lang, n, out, engines):
    os.makedirs(out, exist_ok=True)
    man = open(os.path.join(out, "manifest.jsonl"), "w")
    used = []
    for name in engines.split(","):
        name = name.strip()
        fn = ENGINES.get(name)
        sub = os.path.join(out, name)
        have = glob.glob(os.path.join(sub, "*.wav"))
        if have:                                   # cache: reuse already-generated fakes
            for p in have:
                _write(man, p, lang, name)
            print(f"  [cache] {name}: {len(have)} wavs"); used.append(name + ":cached"); continue
        try:
            print(f"  [run ] {name}")
            if not fn:
                raise RuntimeError("not in local registry — trying adapter")
            with _deadline(name, int(os.environ.get("ENGINE_TIMEOUT", "900"))):
                fn(lang, n, out, man)
            used.append(name)
        except Exception as e:
            print(f"  [..  ] {name}: {type(e).__name__}: {str(e)[:80]}")
            # delegate to the full 28-generator adapter registry (Sarvam/Cartesia/Hume/…)
            try:
                import generator_adapters as GA
                amap = {"cartesia": "cartesia", "hume": "hume", "elevenlabs": "elevenlabs",
                        "sarvam": "sarvam_tts", "bark": "bark", "indicf5": "indicf5",
                        "openaudio": "openaudio_s2"}
                key = amap.get(name)
                if key and key in GA.GEREG:
                    a = GA.GEREG[key]; ok, why = a.available()
                    if not ok:
                        print(f"  [skip] {name} (adapter): {why}")
                    else:
                        os.makedirs(sub, exist_ok=True)
                        paths = a.synth(_texts(lang, n), sub)
                        for p in paths:
                            _write(man, p, lang, name)
                        used.append(name + ":adapter"); print(f"  [ok  ] {name} (adapter): {len(paths)}")
            except Exception as e2:
                print(f"  [skip] {name} (adapter): {type(e2).__name__}: {str(e2)[:80]}")
    man.close()
    rows = sum(1 for _ in open(os.path.join(out, "manifest.jsonl")))
    print(f"[multi] {lang}: engines={used} rows={rows} -> {out}/manifest.jsonl")


def _selftest():
    print("[selftest] engines registered:", ",".join(ENGINES))
    assert "sarvam" in ENGINES and "mms" in ENGINES
    print("[selftest] PASS — dispatcher wiring OK (engines self-report availability)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang"); ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out"); ap.add_argument("--engines", default=DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not (a.lang and a.out): ap.error("--lang and --out required")
    run(a.lang, a.n, a.out, a.engines)


if __name__ == "__main__":
    main()
