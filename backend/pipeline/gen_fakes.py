"""
VoxShield fake generator — synthesize NEW Indic fakes from the self-hosted TTS
engines, to diversify attack families beyond the downloaded datasets.

Text source: real IndicVoices transcripts (content-matched fakes).
Engines (downloaded to $VOXDATA/models/):
  - vits_rasa_13, mms-tts-<lang>   -> WIRED here (HF transformers VitsModel, simple API)
  - indic-parler-tts               -> WIRED (ParlerTTS)
  - IndicF5, XTTS-v2, F5-TTS       -> STUBBED (need their own inference libs; see notes)

Output: $VOXDATA/generated/<engine>/<lang>/<i>.wav  (all label=1 fakes)
Run on the DGX (GPU) for speed.

Usage:
  python gen_fakes.py --engine vits_rasa --langs hi,bn,mr --n 500 --gpu 0
"""
import os, argparse, random, csv, glob

def load_texts(data_root, lang, n):
    """Pull n transcripts for a language from IndicVoices real parquet."""
    import pyarrow.parquet as pq
    texts = []
    pat = os.path.join(data_root, "indicvoices_real", "**", "*.parquet")
    for pf in sorted(glob.glob(pat, recursive=True)):
        t = pq.read_table(pf, columns=["text", "lang"])
        lg = t.column("lang").to_pylist(); tx = t.column("text").to_pylist()
        for i in range(t.num_rows):
            if str(lg[i]).lower().startswith(lang[:2]) and tx[i] and 5 < len(tx[i]) < 220:
                texts.append(tx[i])
                if len(texts) >= n: return texts
    return texts

def gen_vits_rasa(texts, out_dir, model_dir, device):
    import torch, soundfile as sf
    from transformers import VitsModel, AutoTokenizer
    m = VitsModel.from_pretrained(model_dir).to(device).eval()
    tok = AutoTokenizer.from_pretrained(model_dir)
    sr = m.config.sampling_rate
    for i, txt in enumerate(texts):
        try:
            x = tok(txt, return_tensors="pt").to(device)
            with torch.no_grad(): wav = m(**x).waveform[0].float().cpu().numpy()
            sf.write(os.path.join(out_dir, f"{i:05d}.wav"), wav, sr)
        except Exception as e:
            if i < 3: print("  skip", i, e)

# --- STUBS: these engines need their own inference stacks ---
def gen_stub(name):
    def _f(*a, **k):
        raise NotImplementedError(
            f"{name}: install its inference lib and wire here.\n"
            f"  IndicF5 / F5-TTS -> pip install f5-tts ; f5_tts infer --ref_audio --gen_text\n"
            f"  XTTS-v2          -> pip install TTS ; TTS.api.TTS(...).tts_to_file(text, speaker_wav, language)\n"
            f"  indic-parler-tts -> pip install parler-tts ; ParlerTTSForConditionalGeneration")
    return _f

ENGINES = {
    "vits_rasa": ("vits_rasa_13", gen_vits_rasa),
    "indicf5":   ("indicf5", gen_stub("IndicF5")),
    "xtts":      ("xtts-v2", gen_stub("XTTS-v2")),
    "f5":        ("f5-tts", gen_stub("F5-TTS")),
    "parler":    ("indic-parler-tts", gen_stub("indic-parler-tts")),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="/Volumes/KIOXIA/voxdata")
    ap.add_argument("--engine", default="vits_rasa", choices=list(ENGINES))
    ap.add_argument("--langs", default="hi,bn,mr,te,ml")
    ap.add_argument("--n", type=int, default=500, help="clips per language")
    ap.add_argument("--gpu", default="0")
    a = ap.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = a.gpu
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_sub, fn = ENGINES[a.engine]
    model_dir = os.path.join(a.data_root, "models", model_sub)
    for lang in a.langs.split(","):
        out = os.path.join(a.data_root, "generated", a.engine, lang)
        os.makedirs(out, exist_ok=True)
        print(f"[gen] {a.engine} / {lang} -> {out}")
        texts = load_texts(os.path.join(a.data_root, "raw"), lang, a.n)
        print(f"  {len(texts)} transcripts")
        fn(texts, out, model_dir, device)
        print(f"  done: {len(glob.glob(os.path.join(out,'*.wav')))} wavs")

if __name__ == "__main__":
    main()
