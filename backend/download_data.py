"""
VoxShield — real dataset downloader.

Downloads the public benchmark datasets to ./data/ and arranges them in the
real/ + fake/ layout VoxShield expects (so make_manifests.py works directly).

These files are LARGE and must download to YOUR machine (not a sandbox):
  - In-the-Wild      ~7.5 GB   (real+fake, the generalisation test set)   [HuggingFace]
  - ASVspoof 2019 LA ~7.1 GB   (real+fake + protocols, standard train)   [Edinburgh DataShare]
  - WaveFake         ~30 GB    (vocoder fakes; real side = LJSpeech)      [Zenodo]   (optional)

USAGE
  python download_data.py --itw                 # just In-the-Wild (smallest, most useful)
  python download_data.py --itw --asvspoof      # both core datasets
  python download_data.py --all                 # everything (huge)
  python download_data.py --asvspoof --out ../data

After it finishes:
  python make_manifests.py ../data --out manifests
  python train_fusion.py --manifests-dir manifests --augment
(or simply:  bash ../run.sh ../data --ml )

Verified sources (June 2026):
  In-the-Wild  : https://huggingface.co/datasets/mueller91/In-The-Wild
  ASVspoof LA  : https://datashare.ed.ac.uk/handle/10283/3336  (LA.zip)
  WaveFake     : https://zenodo.org/records/4904579
"""
from __future__ import annotations
import os, sys, csv, glob, json, zipfile, argparse, urllib.request, shutil

ASV_LA_URL = "https://datashare.ed.ac.uk/bitstream/handle/10283/3336/LA.zip"
ZENODO_WAVEFAKE_API = "https://zenodo.org/api/records/4904579"
ITW_REPO = "mueller91/In-The-Wild"   # HuggingFace dataset repo


def _dl(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print(f"  ✓ already have {os.path.basename(dst)}"); return dst
    print(f"  ↓ downloading {url}")
    tmp = dst + ".part"

    def hook(b, bs, total):
        if total > 0:
            pct = min(100, b * bs * 100 // total)
            sys.stdout.write(f"\r    {pct:3d}%  ({b*bs//(1<<20)} / {total//(1<<20)} MB)")
            sys.stdout.flush()
    urllib.request.urlretrieve(url, tmp, hook); print()
    os.replace(tmp, dst); return dst


def _unzip(zp, to):
    print(f"  ⤓ extracting {os.path.basename(zp)} …")
    with zipfile.ZipFile(zp) as z:
        z.extractall(to)


# ---------------------------------------------------------------- In-the-Wild
def get_in_the_wild(out):
    dst = os.path.join(out, "in_the_wild")
    os.makedirs(dst, exist_ok=True)
    try:
        from huggingface_hub import snapshot_download
    except Exception:
        print("  ! pip install huggingface_hub   (needed for In-the-Wild)"); return
    print("  ↓ fetching In-the-Wild from HuggingFace (mueller91/In-The-Wild) …")
    path = snapshot_download(repo_id=ITW_REPO, repo_type="dataset",
                             local_dir=os.path.join(dst, "_raw"))
    # find audio + a meta csv mapping file -> label (bona-fide / spoof)
    metas = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    realdir = os.path.join(dst, "real"); fakedir = os.path.join(dst, "fake")
    os.makedirs(realdir, exist_ok=True); os.makedirs(fakedir, exist_ok=True)
    arranged = 0
    for m in metas:
        try:
            with open(m) as f:
                for row in csv.DictReader(f):
                    fn = row.get("file") or row.get("filename") or row.get("path")
                    lab = (row.get("label") or row.get("type") or "").lower()
                    if not fn:
                        continue
                    hits = glob.glob(os.path.join(path, "**", os.path.basename(fn)), recursive=True)
                    if not hits:
                        continue
                    target = realdir if ("bona" in lab or "real" in lab or "genuine" in lab) else fakedir
                    link = os.path.join(target, os.path.basename(fn))
                    if not os.path.exists(link):
                        try: os.symlink(hits[0], link)
                        except Exception: shutil.copy(hits[0], link)
                    arranged += 1
        except Exception as e:
            print("   meta parse issue:", e)
    print(f"  ✓ In-the-Wild arranged: {arranged} files into real/ + fake/")


# ---------------------------------------------------------------- ASVspoof LA
def get_asvspoof(out):
    dst = os.path.join(out, "asvspoof19_LA"); os.makedirs(dst, exist_ok=True)
    zp = os.path.join(dst, "LA.zip")
    _dl(ASV_LA_URL, zp)
    if not glob.glob(os.path.join(dst, "LA", "**", "*.flac"), recursive=True):
        _unzip(zp, dst)
    n = len(glob.glob(os.path.join(dst, "**", "*.flac"), recursive=True))
    protos = glob.glob(os.path.join(dst, "**", "*cm_protocol*", "*.txt"), recursive=True) \
        or glob.glob(os.path.join(dst, "**", "*.trl.txt"), recursive=True)
    print(f"  ✓ ASVspoof LA: {n} flac files, {len(protos)} protocol file(s). "
          f"make_manifests.py reads the protocols automatically.")


# ---------------------------------------------------------------- WaveFake
def get_wavefake(out):
    dst = os.path.join(out, "wavefake", "fake"); os.makedirs(dst, exist_ok=True)
    print("  ↓ querying Zenodo record 4904579 …")
    meta = json.loads(urllib.request.urlopen(ZENODO_WAVEFAKE_API).read())
    files = meta.get("files", [])
    for fobj in files:
        url = fobj["links"]["self"]; name = fobj["key"]
        zp = os.path.join(out, "wavefake", name)
        _dl(url, zp)
        if name.endswith(".zip"):
            _unzip(zp, dst)
    print("  ✓ WaveFake (all FAKE/vocoded). Real side = LJSpeech: "
          "https://keithito.com/LJ-Speech-Dataset/  -> put under wavefake/real/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    ap.add_argument("--itw", action="store_true", help="In-the-Wild")
    ap.add_argument("--asvspoof", action="store_true", help="ASVspoof 2019 LA")
    ap.add_argument("--wavefake", action="store_true", help="WaveFake (huge)")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    if not any([a.itw, a.asvspoof, a.wavefake, a.all]):
        print(__doc__); print("Pick at least one: --itw / --asvspoof / --wavefake / --all"); return
    print(f"[download] target: {out}\n")
    if a.itw or a.all:      print("== In-the-Wild =="); get_in_the_wild(out)
    if a.asvspoof or a.all: print("== ASVspoof 2019 LA =="); get_asvspoof(out)
    if a.wavefake or a.all: print("== WaveFake =="); get_wavefake(out)
    print(f"\n[done] Next:\n  python make_manifests.py {out} --out manifests"
          f"\n  python train_fusion.py --manifests-dir manifests --augment")


if __name__ == "__main__":
    main()
