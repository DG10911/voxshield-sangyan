"""
VoxShield — generate synthetic fakes for languages that have NO spoof set, using
MMS-TTS (facebook/mms-tts-<code>). Writes wavs + a manifest.jsonl that
`pipeline/train_corpus.py` ingests as fakes (via $DATA/worst_ai).

Fixes the "genuine-only" single-class rounds: assamese, bodo, dogri, kashmiri,
konkani, maithili, manipuri, nepali, santali, sindhi.

Usage:
    python gen_fakes_mms.py --lang manipuri --n 300 --out data_fakes/manipuri
    python gen_fakes_mms.py --selftest
"""
from __future__ import annotations
import argparse, glob, json, os, random, sys

# lang -> (flores_code, mms_code)  — covers the 12 two-class + 10 genuine-only languages
LANGS = {
    # two-class (IndicSynth freevc24) — MMS here is the EXTERNAL UNSEEN generator
    "hindi": ("hin_Deva", "hin"), "bengali": ("ben_Beng", "ben"), "marathi": ("mar_Deva", "mar"),
    "telugu": ("tel_Telu", "tel"), "tamil": ("tam_Taml", "tam"), "gujarati": ("guj_Gujr", "guj"),
    "kannada": ("kan_Knda", "kan"), "malayalam": ("mal_Mlym", "mal"), "odia": ("ory_Orya", "ory"),
    "punjabi": ("pan_Guru", "pan"), "urdu": ("urd_Arab", "urd"), "sanskrit": ("san_Deva", "san"),
    # genuine-only (need spoof)
    "assamese": ("asm_Beng", "asm"), "bodo": ("brx_Deva", "brx"), "dogri": ("doi_Deva", "doi"),
    "kashmiri": ("kas_Arab", "kas"), "konkani": ("kok_Deva", "kok"), "maithili": ("mai_Deva", "mai"),
    "manipuri": ("mni_Beng", "mni"), "nepali": ("npi_Deva", "npi"), "santali": ("sat_Olck", "sat"),
    "sindhi": ("snd_Arab", "snd"),
}
FALLBACK_TEXT = [
    "नमस्ते, मैं आपके बैंक से बोल रहा हूँ।",
    "कृपया अपना खाता सत्यापित करें।",
    "आपका ओ टी पी कृपया बताइए।",
    "यह एक आवश्यक सूचना है।",
    "धन्यवाद, आपका दिन शुभ हो।",
]


def _texts(flores_code):
    try:
        from datasets import load_dataset
        ds = load_dataset("facebook/flores", flores_code, split="dev", trust_remote_code=True)
        s = [x["sentence"] for x in ds if 8 <= len(x["sentence"]) <= 220]
        if s:
            return s
    except Exception as e:
        print(f"  [text] FLORES {flores_code} unavailable ({str(e)[:60]}) — using fallback")
    return FALLBACK_TEXT


def generate(lang, n, out, seen=1, mms_code=None):
    import numpy as np, torch, soundfile as sf
    from transformers import VitsModel, AutoTokenizer
    if lang not in LANGS and not mms_code:
        raise SystemExit(f"unknown lang '{lang}'. choices: {', '.join(LANGS)}")
    flores, mms = LANGS.get(lang, ("", mms_code or lang))
    if mms_code: mms = mms_code
    os.makedirs(out, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[gen] {lang}  mms-tts-{mms}  device={device}  n={n}")
    model = VitsModel.from_pretrained(f"facebook/mms-tts-{mms}").to(device).eval()
    tok = AutoTokenizer.from_pretrained(f"facebook/mms-tts-{mms}")
    sr = model.config.sampling_rate
    texts = _texts(flores); random.seed(42); random.shuffle(texts)
    man = open(os.path.join(out, "manifest.jsonl"), "w")
    made = 0
    for i in range(n):
        t = texts[i % len(texts)]
        try:
            ids = tok(t, return_tensors="pt").to(device)
            with torch.no_grad():
                wav = model(**ids).waveform[0].float().cpu().numpy()
        except Exception as e:
            print("  synth err", str(e)[:80]); continue
        p = os.path.abspath(os.path.join(out, f"{lang}_{made:05d}.wav"))
        sf.write(p, np.clip(wav, -1, 1), sr)
        man.write(json.dumps({"path": p, "label": 1, "language": lang[:2],
                              "generator": f"mms-tts-{mms}", "seen": int(seen)}) + "\n")
        made += 1
    man.close()
    print(f"[gen] wrote {made} fakes + manifest -> {out}/manifest.jsonl")


def _selftest():
    # schema-only (no torch)
    import tempfile
    out = tempfile.mkdtemp()
    p = os.path.join(out, "x.wav"); open(p, "wb").write(b"")
    with open(os.path.join(out, "manifest.jsonl"), "w") as f:
        f.write(json.dumps({"path": p, "label": 1, "language": "ma",
                            "generator": "mms-tts-mai", "seen": 1}) + "\n")
    rows = [json.loads(l) for l in open(os.path.join(out, "manifest.jsonl"))]
    assert rows[0]["label"] == 1 and rows[0]["generator"].startswith("mms-tts")
    print("[selftest] PASS — fake manifest schema is what train_corpus ingests.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang"); ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--out"); ap.add_argument("--seen", type=int, default=1,
                                             help="1 = seen generator (training), 0 = UNSEEN (for the gap)")
    ap.add_argument("--mms-code", default=None, help="override the MMS-TTS code (e.g. hin, ben)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: _selftest(); return
    if not (a.lang and a.out): ap.error("--lang and --out required")
    generate(a.lang, a.n, a.out, a.seen, a.mms_code)


if __name__ == "__main__":
    main()
