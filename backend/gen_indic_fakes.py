import os, time, random
import torch, soundfile as sf
from datasets import load_dataset
from transformers import VitsModel, AutoTokenizer

random.seed(42)
OUT = os.path.expanduser("~/data/voxdata/indicvoices/fake")
os.makedirs(OUT, exist_ok=True)

LANGS = [
    ("hin_Deva", "hindi",     "hin"),
    ("tam_Taml", "tamil",     "tam"),
    ("ben_Beng", "bengali",   "ben"),
    ("tel_Telu", "telugu",    "tel"),
    ("mar_Deva", "marathi",   "mar"),
    ("kan_Knda", "kannada",   "kan"),
    ("mal_Mlym", "malayalam", "mal"),
    ("guj_Gujr", "gujarati",  "guj"),
    ("pan_Guru", "punjabi",   "pan"),
    ("asm_Beng", "assamese",  "asm"),
]
PER_LANG = 400
device = torch.device("cuda")
print(f"[gen] device={device} out={OUT}")

for flores_code, name, mms_code in LANGS:
    t0 = time.time()
    print(f"\n=== {name} ({mms_code}) ===")
    try:
        ds = load_dataset("facebook/flores", flores_code, split="dev", trust_remote_code=True)
        sents = [x["sentence"] for x in ds if 8 <= len(x["sentence"]) <= 220]
        random.shuffle(sents)
        print(f"  [text] {len(sents)} sentences from FLORES/{flores_code}")
    except Exception as e:
        print(f"  [text] FLORES failed ({e}); skipping {name}")
        continue

    try:
        model = VitsModel.from_pretrained(f"facebook/mms-tts-{mms_code}").to(device).eval()
        tok = AutoTokenizer.from_pretrained(f"facebook/mms-tts-{mms_code}")
        sr = model.config.sampling_rate
        print(f"  [tts] loaded facebook/mms-tts-{mms_code} (sr={sr})")
    except Exception as e:
        print(f"  [tts] load failed ({e}); skipping {name}")
        continue

    ok = 0
    for i in range(PER_LANG):
        text = sents[i % len(sents)]
        try:
            inputs = tok(text, return_tensors="pt").to(device)
            with torch.no_grad():
                audio = model(**inputs).waveform[0].float().cpu().numpy()
            sf.write(f"{OUT}/{name}_{i:04d}.wav", audio, sr)
            ok += 1
        except Exception as e:
            if i < 3:
                print(f"    skip i={i}: {e}")
        if i and i % 100 == 0:
            print(f"  [gen] {i}/{PER_LANG}  {time.time()-t0:.0f}s")
    del model, tok
    torch.cuda.empty_cache()
    print(f"  ✓ {name}: {ok}/{PER_LANG} fakes  time={time.time()-t0:.0f}s")

total = sum(1 for f in os.listdir(OUT) if f.endswith(".wav"))
print(f"\n[done] total fake clips: {total}")
