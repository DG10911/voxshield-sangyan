"""
VoxShield — bulk resource downloader for the Indic corpus (datasets + TTS + ASR models).

Registry of every resource provided, with access class:
  hf_dataset : huggingface datasets  (repo_type=dataset)
  hf_model   : huggingface models
  openslr   : openslr.org SLR id (direct zip)
  zenodo    : zenodo record (direct)
  mendeley  : data.mendeley.com dataset (direct)
  github    : git clone
  aikosh    : IndiaAI AIKosh (needs the aikosh SDK / MCP; id-based)
  kaggle    : Kaggle (needs ~/.kaggle/kaggle.json)
  azure     : Azure AI catalog (needs auth) / external URL

Usage (DGX):
  python backend/download_resources.py --list                 # show the registry
  python backend/download_resources.py --download all --root data/indic
  python backend/download_resources.py --download hf,openslr  # only open classes
  python backend/download_resources.py --lang manipuri
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys

# lang, kind, access, ref, note
R = [
 # ---- Manipuri ----
 ("manipuri","asr_model","aikosh","ai4bharat_indicconformer_stt_mni_hybrid_ctc_rnnt_large","IndicConformer mni"),
 ("manipuri","tts","web","https://www.meiteimayek.com/tts","Meitei Mayek TTS"),
 ("manipuri","tts_data","hf_dataset","SPRINGLab/IndicTTS_Manipuri","IndicTTS Manipuri"),
 ("manipuri","tts_data","hf_dataset","DayanandaThokchom/MANIPUR-MEITEILON-TTS","Meiteilon TTS"),
 # ---- Konkani ----
 ("konkani","hub","hf_org","konkani","HF konkani org"),
 ("konkani","asr","kaggle","shreyashparsekar/konkani-audio-ml-lab-2445","Kaggle notebook"),
 ("konkani","asr_model","aikosh","ai4bharat_indicconformer_automatic_speech_recognition_asr_model_for_konkani","IndicConformer kok"),
 ("konkani","asr_model","hf_model","sandeepsawant28/whisper-small-konkani-numbers","whisper kok numbers"),
 # ---- Dogri ----
 ("dogri","asr_model","azure","harveenchadha/vakyansh-wav2vec2-dogri-doi-55","Vakyansh Dogri"),
 # ---- Bodo ----
 ("bodo","hub","hf_model","AyushSisodiya/BODOAI","BODO AI"),
 ("bodo","asr_model","hf_model","COCO1033/bodo-whisper-asr-v1","whisper bodo"),
 ("bodo","tts_data","aikosh","bodo_female_mono_indictts_phase3","IndicTTS bodo female"),
 # ---- Urdu ----
 ("urdu","datasets","hf_org","UmarRamzan/urdu-datasets","Urdu datasets collection"),
 ("urdu","deepfake","github","https://github.com/CSALT-LUMS/urdu-deepfake-dataset","Urdu deepfake dataset"),
 ("urdu","asr_data","aikosh","urdu_asr_benchmark_dataset_for_speech_recognition_commonvoice_urdu","CV Urdu ASR"),
 ("urdu","data","hf_dataset","humairawan/Urdu-aud01","Urdu aud01"),
 ("urdu","data","kaggle","muhammadahmedansari/urdu-dataset-20000","Urdu 20k"),
 # ---- VAANI ----
 ("multi","data","aikosh","vaani_multi_modal_multi_lingual_dataset","VAANI multimodal"),
 # ---- Santali ----
 ("santali","asr_model","aikosh","ai4bharat_indicconformer_stt_sat_hybrid_ctc_rnnt_large_santali","IndicConformer sat"),
 ("santali","asr_model","hf_model","thunderboltc/whisper-small-santali-ol-chiki","whisper sat Ol Chiki"),
 # ---- multilingual ASR ----
 ("multi","asr_model","hf_model","ai4bharat/indic-conformer-600m-multilingual","IndicConformer 600M"),
 # ---- Bengali ----
 ("bengali","asr_data","aikosh","bengali_asr_benchmark_dataset_fluers_bengali","FLUERS bn"),
 ("bengali","data","zenodo","6345107","Zenodo Bengali"),
 ("bengali","tts_data","hf_org","Mahadih534/bangla-tts-datasets","Bangla TTS datasets"),
 ("bengali","asr_data","aikosh","bengali_multilingual_speech_recognition_dataset_kathbath","Kathbath bn"),
 ("bengali","data","mendeley","swbxvhc44c","Mendeley Bengali"),
 ("bengali","data","openslr","53","OpenSLR bn"),
 ("bengali","data","kaggle","bengaliai-speech","BengaliAI speech"),
 ("bengali","av","web","https://researchdata.edu.au/bengali-audio-visual-speech-recognition/3475653","Bengali AV"),
 # ---- Kannada ----
 ("kannada","asr_data","aikosh","kannada_asr_benchmark_dataset_fluers_kannada","FLUERS kn"),
 ("kannada","data","kaggle","infobayai/audio-podcast-kannada","kannada podcast"),
 ("kannada","tts_data","syspin","kannada female tts data","SYSPIN kn female"),
 ("kannada","tts_data","hf_dataset","SPRINGLab/IndicTTS_Kannada","IndicTTS kn"),
 ("kannada","data","openslr","79","OpenSLR79 kn multispeaker"),
 ("kannada","asr_model","hf_model","vasista22/whisper-kannada-tiny","whisper kn tiny"),
 # ---- Tamil ----
 ("tamil","data","hf_dataset","Thanushs25/tamil-audio-emotion-classification","Tamil emotion"),
 ("tamil","asr_data","aikosh","tamil_asr_benchmark_dataset_commonvoice_tamil","CV Tamil ASR"),
 ("tamil","data","openslr","65","OpenSLR65 ta multispeaker"),
 ("tamil","data","github","https://github.com/Nexdata-AI/Tamil-Speech-Dataset-500-Hours-Monologue-Audio-Corpus","Tamil 500h"),
 ("tamil","data","kaggle","infobayai/audio-podcast-tamil","tamil podcast"),
 ("tamil","tts_data","hf_dataset","SPRINGLab/IndicTTS_Tamil","IndicTTS ta"),
 ("tamil","asr_data","openslr","127","IISc-MILE Tamil ASR (13G)"),
 # ---- Gujarati ----
 ("gujarati","data","openslr","78","OpenSLR78 gu multispeaker"),
 ("gujarati","asr_data","aikosh","gujarati_asr_benchmark_dataset_for_speech_recognition_fluers_gujarati","FLUERS gu"),
 ("gujarati","data","github","https://github.com/Nikunj1729/free-spoken-gujarati-digit-dataset","Gujarati digits"),
 ("gujarati","asr_data","aikosh","gujarati_asr_benchmark_dataset_for_news_and_general_speech_recognition_kathbath_hard_gujarati","Kathbath gu"),
 # ---- Malayalam ----
 ("malayalam","asr_data","aikosh","malayalam_asr_validation_dataset","Malayalam ASR val"),
 ("malayalam","data","github","https://github.com/aswinpradeep/malayalam-asr-datasets","Malayalam ASR datasets"),
 ("malayalam","data","openslr","63","OpenSLR63 ml multispeaker"),
 ("malayalam","data","kaggle","infobayai/audio-podcast-malayalam","malayalam podcast"),
 ("malayalam","asr_model","hf_model","thennal/whisper-medium-ml","whisper ml"),
 ("malayalam","tts_data","aikosh","malayalam_asr_benchmark_dataset_for_diverse_domains_indictts_malayalam","IndicTTS ml"),
 ("malayalam","asr_data","aikosh","malayalam_asr_benchmark_dataset_for_news_and_general_domains_kathbath_malayalam","Kathbath ml"),
 # ---- shared / TTS ----
 ("multi","tts_model","hf_model","ai4bharat/indic-parler-tts","Indic Parler (21 langs)"),
 ("multi","tts_model","hf_model","ai4bharat/indicf5","IndicF5"),
 ("multi","data","mendeley","3337bdvx3v","Mendeley seed"),
 ("multi","data","aikosh","ljspeech_1","LJSpeech"),
 ("multi","data","web","https://bhashini.gov.in/gyankosh?tab=publications","Bhashini GyanKosh"),
]

OPEN = {"hf_dataset", "hf_model", "openslr", "zenodo", "mendeley", "github"}


def _run(cmd):
    print("  $", " ".join(cmd[:4]), "...")
    return subprocess.run(cmd).returncode


def fetch(entry, root):
    lang, kind, access, ref, note = entry
    dest = os.path.join(root, lang if lang != "multi" else "shared", ref.replace("/", "__"))
    os.makedirs(dest, exist_ok=True)
    if access == "hf_dataset":
        return _run(["hf", "download", ref, "--repo-type", "dataset", "--local-dir", dest])
    if access == "hf_model":
        return _run(["hf", "download", ref, "--local-dir", dest])
    if access == "openslr":
        url = f"https://www.openslr.org/resources/{ref}/"
        # need the actual filename from the page; user lists them — fetch the dir index and grab zips
        return _run(["bash", "-lc", f"cd {dest} && curl -s {url} | grep -oE 'href=\"[^\"]+\\.(zip|tar\\.gz)\"' | sed 's/href=//;s/\"//g' | head -3 | xargs -I{{}} curl -O {url}{{}}"])
    if access == "zenodo":
        return _run(["bash", "-lc", f"cd {dest} && curl -s https://zenodo.org/api/records/{ref} | grep -oE '\"download\"[^,]+' | head -1"])
    if access == "github":
        return _run(["git", "clone", "--depth", "1", ref, dest])
    if access == "mendeley":
        return _run(["bash", "-lc", f"echo 'open https://data.mendeley.com/datasets/{ref}/1 and download' > {dest}/README_DOWNLOAD.txt"])
    if access == "kaggle":
        if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
            print(f"  [gated] kaggle {ref} — put kaggle.json at ~/.kaggle/kaggle.json")
            return 1
        return _run(["kaggle", "datasets", "download", "-d", ref, "-p", dest, "--unzip"])
    if access == "aikosh":
        return _aikosh_fetch(kind, ref, dest, note)
    # gated
    print(f"  [gated] {access} {ref} — needs credentials/SDK: {note}")
    return 1


def _aikosh_fetch(kind, ref, dest, note):
    """Resolve + download an AIKosh dataset/model via the aikosh SDK (API key required)."""
    key = os.environ.get("AIKOSH_API_KEY")
    if not key:
        print(f"  [gated] aikosh {ref} — set AIKOSH_API_KEY")
        return 1
    try:
        import aikosh
    except Exception:
        print("  [gated] aikosh — pip install aikosh")
        return 1
    aikosh.set_api_key(key)
    is_model = "model" in kind
    rtype = "model" if is_model else "dataset"
    ident = ref if (len(ref) == 36 and ref.count("-") == 4) else None
    if not ident:                                   # resolve slug/name -> id
        import re
        words = [w for w in re.split(r"[_\s]+", ref) if w and not w.isdigit()
                 and w.lower() not in ("phase3", "phase", "1")]
        cands = [" ".join(words)]
        if len(words) > 3: cands.append(" ".join(words[:3]))
        if len(words) > 2: cands.append(" ".join(words[:2]))
        if words: cands.append(words[0])                  # single-token fallback (e.g. "Vaani")
        for kw in cands:
            for typ in ([rtype + "s"] if rtype == "model" else ["datasets", "models"]):
                try:
                    found = aikosh.list_directory(typ, {"keyword": kw}, limit=5)
                    rows = found.get("data", {}).get("data", []) if isinstance(found, dict) else []
                    if rows:
                        ident = rows[0].get("id"); rtype = "model" if typ == "models" else "dataset"
                        print(f"  [res ] '{kw}' -> {rows[0].get('name','')[:40]}")
                        break
                except Exception:
                    pass
            if ident: break
    if not ident:
        print(f"  [miss] aikosh {ref}: no match"); return 1
    try:
        files = aikosh.list_files(rtype, ident).get("data", {}).get("files", [])
        reqs = [{"identifier": ident, "type": rtype, "file_path": f["relativeUrl"],
                 "destination_path": dest} for f in files]
        if not reqs:
            print(f"  [miss] aikosh {ref}: no files"); return 1
        aikosh.download(reqs)
        print(f"  [ok  ] aikosh {ref} -> {dest} ({len(reqs)} files)")
        return 0
    except Exception as e:
        print(f"  [err ] aikosh {ref}: {type(e).__name__}: {str(e)[:100]}")
        return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", default="")
    ap.add_argument("--lang", default="")
    ap.add_argument("--root", default="data/indic")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not (a.download or a.lang):
        for e in R:
            print(f"{e[0]:10} {e[1]:10} {e[2]:11} {e[3][:70]}")
        print(f"\n{len(R)} resources · open classes: {sorted(OPEN)}")
        return
    sel = [e for e in R if (not a.lang or e[0] == a.lang)]
    if a.download not in ("", "all"):
        want = set(a.download.split(","))
        sel = [e for e in sel if e[2] in want or e[2].startswith("hf") and "hf" in want]
    for e in sel:
        if e[2] in OPEN or e[2] in ("aikosh", "kaggle"):
            print(f"== {e[0]} {e[2]} {e[3]}")
            try:
                fetch(e, a.root)
            except Exception as ex:
                print("  fail:", ex)
        else:
            print(f"[gated] {e[0]} {e[2]} {e[3]} ({e[4]})")
    print("done.")


if __name__ == "__main__":
    assert len(R) >= 50, len(R)
    print(f"[ok] {len(R)} resources registered")
    main()
