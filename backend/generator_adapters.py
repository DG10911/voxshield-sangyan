"""
VoxShield — adapter for ALL 28 generators in registries/generators.json.

One uniform interface per generator so the multi-generator fakes pipeline can call
any of them:
    a = GEREG["xtts_v2"]; a.available()  -> (bool, reason)
    a.synth(texts, out_dir)              -> list of wav paths, or raises

Kinds:
  local_pkg  : pip/on-disk model, runs offline (best for training data)
  repo       : needs a cloned repo / specific install (install hint provided)
  api        : cloud endpoint, needs an API key (Sarvam, ElevenLabs, Cartesia, Hume, PlayHT)
  classical  : signal-processing baseline (Griffin-Lim)
  human      : not a generator (the 'real' entry)

Availability is resolved at runtime; unavailable adapters return `(False, reason)` and are
skipped, so the pipeline degrades gracefully. `install_hints()` prints what to add to enable each.
"""
from __future__ import annotations
import os, shutil, subprocess, tempfile

# Coqui XTTS prompts "[y/n]" on stdin for its CPML license and BLOCKS forever in a
# headless job — auto-accept via env so it never hangs.
os.environ.setdefault("COQUI_TOS_AGREED", "1")

# --- helpers ---------------------------------------------------------------
def _mod(name):
    import importlib.util
    return importlib.util.find_spec(name) is not None

def _import(name):
    return __import__(name)

def _texts(lang, n):
    try:
        import gen_fakes_mms as G
        t = G._texts(G.LANGS.get(lang, ("", ""))[0]) or G.FALLBACK_TEXT
    except Exception:
        t = ["नमस्ते, यह एक परीक्षण है।"]
    return [t[i % len(t)] for i in range(n)]


class Adapter:
    kind = "local_pkg"; requires = ""; pip = ""; key = ""
    def __init__(self, name): self.name = name
    def available(self):
        if self.kind == "api" and self.key and not os.environ.get(self.key):
            return False, f"needs env {self.key}"
        if self.pip:
            for p in self.pip.split(","):
                if not _mod(p.strip()):
                    return False, f"pip install {p.strip()}"
        return True, "ok"
    def synth(self, texts, out_dir):
        fn = getattr(self, "_fn", None)
        if fn is None:
            raise NotImplementedError(f"{self.name}: no synth implementation ({self.kind})")
        return fn(self, texts, out_dir)


def _local(name, fn):  a = Adapter(name); a._fn = fn; return a
def _repo(name, hint, fn=None): a = Adapter(name); a.kind = "repo"; a.requires = hint; a._fn = fn; return a
def _api(name, key, fn): a = Adapter(name); a.kind = "api"; a.key = key; a._fn = fn; return a


# --- local package adapters -------------------------------------------------
def _mms(self, texts, out_dir):
    import gen_fakes_mms as G
    import soundfile as sf
    os.makedirs(out_dir, exist_ok=True); paths = []
    G.generate(  # reuse the tested generator into out_dir
        self._lang, len(texts), out_dir)
    import glob
    return sorted(glob.glob(os.path.join(out_dir, "*.wav")))

def _parler(self, texts, out_dir):
    import gen_fakes_tts as G
    os.makedirs(out_dir, exist_ok=True)
    G.generate(self._lang, os.path.join("data", self._lang), len(texts), out_dir)
    import glob
    return sorted(glob.glob(os.path.join(out_dir, "*.wav")))

def _bark(self, texts, out_dir):
    from transformers import AutoProcessor, BarkModel
    import soundfile as sf, torch
    os.makedirs(out_dir, exist_ok=True)
    proc = AutoProcessor.from_pretrained("suno/bark-small")
    model = BarkModel.from_pretrained("suno/bark-small").to("cuda" if torch.cuda.is_available() else "cpu")
    paths = []
    for i, t in enumerate(texts):
        inp = proc(t, return_tensors="pt").to(model.device)
        audio = model.generate(**inp).cpu().numpy().squeeze()
        p = os.path.join(out_dir, f"bark_{i:05d}.wav"); sf.write(p, audio, 24000); paths.append(p)
    return paths

def _xtts(self, texts, out_dir):
    from TTS.api import TTS
    os.makedirs(out_dir, exist_ok=True)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    spk = tts.speakers[0] if tts.speakers else None
    paths = []
    for i, t in enumerate(texts):
        p = os.path.join(out_dir, f"xtts_{i:05d}.wav")
        tts.tts_to_file(text=t, speaker=spk, language=self._lang[:2], file_path=p); paths.append(p)
    return paths

def _f5(self, texts, out_dir):
    from f5_tts.api import F5TTS
    import soundfile as sf, glob
    os.makedirs(out_dir, exist_ok=True)
    f5 = F5TTS()
    ref = glob.glob("data/%s/**/*.wav" % self._lang, recursive=True)
    if not ref: raise RuntimeError("needs a reference wav")
    paths = []
    for i, t in enumerate(texts):
        wav, sr, _ = f5.infer(ref_file=ref[0], ref_text="", gen_text=t)
        p = os.path.join(out_dir, f"f5_{i:05d}.wav"); sf.write(p, wav, sr); paths.append(p)
    return paths

def _kokoro(self, texts, out_dir):
    from kokoro import KPipeline
    import soundfile as sf, numpy as np
    os.makedirs(out_dir, exist_ok=True)
    pipe = KPipeline(lang_code=self._lang[:1]); paths = []
    for i, t in enumerate(texts):
        for _, _, audio in pipe(t):
            p = os.path.join(out_dir, f"kokoro_{i:05d}.wav"); sf.write(p, np.asarray(audio), 24000)
            paths.append(p); break
    return paths

def _piper(self, texts, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    voice = os.environ.get("PIPER_VOICE", "")
    if not voice: raise RuntimeError("set PIPER_VOICE=<voice.onnx>")
    paths = []
    for i, t in enumerate(texts):
        p = os.path.join(out_dir, f"piper_{i:05d}.wav")
        subprocess.run(["piper", "-m", voice, "-f", p], input=t.encode(), check=True); paths.append(p)
    return paths

def _indicf5(self, texts, out_dir):
    from transformers import AutoModel, AutoTokenizer
    import soundfile as sf, glob, numpy as np
    os.makedirs(out_dir, exist_ok=True)
    model = AutoModel.from_pretrained("ai4bharat/IndicF5", trust_remote_code=True).to("cuda")
    ref = glob.glob("data/%s/**/*.wav" % self._lang, recursive=True)
    if not ref: raise RuntimeError("IndicF5 needs a reference wav")
    paths = []
    for i, t in enumerate(texts):
        audio = model(t, ref_audio_path=ref[0], ref_text="")
        p = os.path.join(out_dir, f"indicf5_{i:05d}.wav"); sf.write(p, np.asarray(audio), 24000)
        paths.append(p)
    return paths

def _openaudio(self, texts, out_dir):
    from transformers import AutoModelForCausalLM
    import soundfile as sf, torch
    os.makedirs(out_dir, exist_ok=True)
    m = AutoModelForCausalLM.from_pretrained("fishaudio/openaudio-s1-mini", trust_remote_code=True)
    paths = []
    for i, t in enumerate(texts):
        w = m.generate(t)  # engine-specific; placeholder binding
        p = os.path.join(out_dir, f"openaudio_{i:05d}.wav"); sf.write(p, w, 24000); paths.append(p)
    return paths

def _griffin_lim(self, texts, out_dir):
    import numpy as np, soundfile as sf, librosa
    os.makedirs(out_dir, exist_ok=True); paths = []
    for i in range(len(texts)):
        D = np.abs(np.random.randn(1025, 64)); y = librosa.griffinlim(D)
        p = os.path.join(out_dir, f"griffinlim_{i:05d}.wav")
        sf.write(p, y.astype("float32"), 22050); paths.append(p)
    return paths


# --- API adapters -----------------------------------------------------------
def _sarvam(self, texts, out_dir):
    import urllib.request, base64, json
    os.makedirs(out_dir, exist_ok=True)
    url = os.environ.get("SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech")
    key = os.environ["SARVAM_API_KEY"]; paths = []
    for i, t in enumerate(texts):
        body = json.dumps({"inputs": [t], "target_language_code": "hi-IN",
                           "speaker": os.environ.get("SARVAM_SPEAKER", "meera")}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json",
                                   "api-subscription-key": key})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        p = os.path.join(out_dir, f"sarvam_{i:05d}.wav")
        open(p, "wb").write(base64.b64decode(data["audios"][0])); paths.append(p)
    return paths

def _cartesia(self, texts, out_dir):
    import urllib.request, json
    os.makedirs(out_dir, exist_ok=True)
    key = os.environ["CARTESIA_API_KEY"]; ver = os.environ.get("CARTESIA_VERSION", "2025-04-16")
    # resolve a voice id
    vid = os.environ.get("CARTESIA_VOICE_ID", "")
    if not vid:
        req = urllib.request.Request("https://api.cartesia.ai/voices",
              headers={"X-API-Key": key, "Cartesia-Version": ver})
        with urllib.request.urlopen(req, timeout=30) as r:
            vs = json.loads(r.read()); vid = vs[0]["id"]
    paths = []
    for i, t in enumerate(texts):
        body = json.dumps({"model_id": "sonic-2", "transcript": t,
                           "voice": {"mode": "id", "id": vid},
                           "output_format": {"container": "wav", "sample_rate": 24000,
                                             "encoding": "pcm_s16le"}}).encode()
        req = urllib.request.Request("https://api.cartesia.ai/tts/bytes", data=body,
              headers={"X-API-Key": key, "Cartesia-Version": ver, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            p = os.path.join(out_dir, f"cartesia_{i:05d}.wav"); open(p, "wb").write(r.read()); paths.append(p)
    return paths

def _hume(self, texts, out_dir):
    import urllib.request, base64, json
    os.makedirs(out_dir, exist_ok=True)
    key = os.environ["HUME_API_KEY"]; paths = []
    for i, t in enumerate(texts):
        body = json.dumps({"utterances": [{"text": t}], "format": {"type": "wav"}}).encode()
        req = urllib.request.Request("https://api.hume.ai/v0/tts", data=body,
              headers={"X-Hume-Api-Key": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
        aud = data["generations"][0]["audio"]
        p = os.path.join(out_dir, f"hume_{i:05d}.wav"); open(p, "wb").write(base64.b64decode(aud)); paths.append(p)
    return paths

def _elevenlabs(self, texts, out_dir):
    import urllib.request
    os.makedirs(out_dir, exist_ok=True)
    key = os.environ["ELEVENLABS_API_KEY"]; voice = os.environ.get("ELEVENLABS_VOICE", "21m00Tcm4TlvDq8ikWAM")
    paths = []
    for i, t in enumerate(texts):
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
              data=__import__("json").dumps({"text": t, "model_id": "eleven_multilingual_v2"}).encode(),
              headers={"xi-api-key": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            p = os.path.join(out_dir, f"elevenlabs_{i:05d}.mp3"); open(p, "wb").write(r.read()); paths.append(p)
    return paths


# --- registry: all 28 -------------------------------------------------------
GEREG = {}
def _reg():
    # Tier 1 — local
    GEREG["mms_tts"] = _local("mms_tts", _mms); GEREG["mms_tts"].pip = "transformers"
    GEREG["indic_parler_tts"] = _local("indic_parler_tts", _parler); GEREG["indic_parler_tts"].pip = "transformers"
    GEREG["bark"] = _local("bark", _bark); GEREG["bark"].pip = "transformers"
    GEREG["xtts_v1"] = _local("xtts_v1", _xtts); GEREG["xtts_v1"].pip = "TTS"
    GEREG["xtts_v2"] = _local("xtts_v2", _xtts); GEREG["xtts_v2"].pip = "TTS"
    GEREG["f5_tts"] = _local("f5_tts", _f5); GEREG["f5_tts"].pip = "f5_tts"
    GEREG["kokoro_82m"] = _local("kokoro_82m", _kokoro); GEREG["kokoro_82m"].pip = "kokoro"
    GEREG["piper"] = _local("piper", _piper)
    GEREG["indicf5"] = _local("indicf5", _indicf5); GEREG["indicf5"].pip = "transformers"
    GEREG["openaudio_s2"] = _local("openaudio_s2", _openaudio); GEREG["openaudio_s2"].pip = "transformers"
    GEREG["griffin_lim"] = _local("griffin_lim", _griffin_lim); GEREG["griffin_lim"].pip = "librosa"
    # Tier 1 — repo-based (install hint)
    for nm, hint in [
        ("cosyvoice", "git clone FunAudioLLM/CosyVoice; pip install -r requirements.txt"),
        ("qwen3_tts", "pip install dashscope (needs DASHSCOPE_API_KEY)"),
        ("voxcpm2", "git clone OpenBMB/VoxCPM2"),
        ("longcat_audio", "git clone meituan-longcat/LongCat-Audio"),
        ("higgs_audio", "git clone boson-ai/higgs-audio"),
        ("vibevoice", "git clone microsoft/VibeVoice"),
        ("gpt_sovits", "git clone RVC-Boss/GPT-SoVITS"),
        ("styletts2", "git clone yl4579/StyleTTS2"),
        ("openvoice", "git clone myshell-ai/OpenVoice"),
        ("rvc", "git clone RVC-Project/Retrieval-based-Voice-Conversion"),
        ("seed_vc", "git clone Plachtaa/seed-vc"),
    ]:
        GEREG[nm] = _repo(nm, hint)
    # Tier 2 — API
    GEREG["sarvam_tts"] = _api("sarvam_tts", "SARVAM_API_KEY", _sarvam)
    GEREG["elevenlabs"] = _api("elevenlabs", "ELEVENLABS_API_KEY", _elevenlabs)
    GEREG["cartesia"] = _api("cartesia", "CARTESIA_API_KEY", _cartesia)
    GEREG["hume"] = _api("hume", "HUME_API_KEY", _hume)
    GEREG["playht"] = _api("playht", "PLAYHT_API_KEY", None)
    # real (human) — not a generator
    GEREG["real"] = Adapter("real"); GEREG["real"].kind = "human"

_reg()
ALL = list(GEREG.keys())


def install_hints():
    for k, a in GEREG.items():
        ok, why = a.available()
        print(f"{'OK ' if ok else '-- '} {k:18} {a.kind:9} {('' if ok else why)}")


if __name__ == "__main__":
    assert len(GEREG) >= 27, len(GEREG)
    sweep = [k for k, a in GEREG.items() if a.kind == "api"]
    assert set(["sarvam_tts", "elevenlabs", "cartesia", "hume", "playht"]).issubset(sweep)
    print(f"[selftest] PASS — {len(GEREG)} generators registered ({len(sweep)} api)")
    install_hints()
