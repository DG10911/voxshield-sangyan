"""
VoxShield — dataset manifest auto-builder.

Scans a data folder, classifies each audio file as bonafide (0) or spoof/fake (1)
by looking at folder/file names, groups by top-level dataset folder, and writes
one CSV per dataset (columns: path,label,dataset) into backend/manifests/.

Recognised layouts (no config needed):
  data/
    asvspoof19/real/*.wav   data/asvspoof19/fake/*.wav
    wavefake/bonafide/...    wavefake/spoof/...
    in_the_wild/genuine/...  in_the_wild/deepfake/...
  ...or any tree where the path contains a real/fake keyword.

Also supports ASVspoof protocol files: if a *.txt/.trl/.cm with the words
'bonafide'/'spoof' is found, it is parsed (filename + label per line).

USAGE
  python make_manifests.py /path/to/data
  python make_manifests.py /path/to/data --out manifests
"""
from __future__ import annotations
import os, csv, sys, argparse, glob

AUDIO_EXT = (".wav", ".flac", ".mp3", ".m4a", ".ogg", ".aac", ".wma")
REAL_KEYS = ("bonafide", "bona_fide", "real", "genuine", "human", "clean", "original")
FAKE_KEYS = ("spoof", "fake", "synthetic", "deepfake", "tts", "clone",
             "generated", "vocoder", "attack")


def _scan(token: str):
    for k in FAKE_KEYS:
        if k in token:
            return 1
    for k in REAL_KEYS:
        if k in token:
            return 0
    return None


def _label_from_path(rel: str):
    """Classify on the path BELOW the dataset folder. Folder names take
    priority over the filename (so a file literally named '..._real_0.wav'
    inside a 'fake/' folder is still labelled correctly, and vice-versa)."""
    parts = rel.lower().replace("\\", "/").split("/")
    folders, fname = parts[:-1], parts[-1]
    for token in reversed(folders):        # nearest folder first
        lab = _scan(token)
        if lab is not None:
            return lab
    return _scan(fname)                     # fall back to filename


def _parse_protocol(txt_path, audio_root):
    """Best-effort ASVspoof-style protocol parsing -> list[(path,label)]."""
    rows = []
    try:
        with open(txt_path) as f:
            for line in f:
                parts = line.split()
                if not parts:
                    continue
                lab = None
                if "bonafide" in line.lower():
                    lab = 0
                elif "spoof" in line.lower():
                    lab = 1
                if lab is None:
                    continue
                # the token that looks like an utterance id (e.g. LA_T_1234567)
                fid = next((t for t in parts if t.startswith(("LA_", "PA_", "DF_", "CM_"))), parts[0])
                hit = glob.glob(os.path.join(audio_root, "**", fid + ".*"), recursive=True)
                if hit:
                    rows.append((hit[0], lab))
    except Exception:
        pass
    return rows


def build(data_dir: str, out_dir: str):
    data_dir = os.path.abspath(data_dir)
    os.makedirs(out_dir, exist_ok=True)
    if not os.path.isdir(data_dir):
        print(f"[manifests] data dir not found: {data_dir}")
        return []

    # dataset = first-level subfolder; loose files grouped as 'root'
    datasets: dict[str, list[tuple[str, int]]] = {}

    def add(ds, path, label):
        datasets.setdefault(ds, []).append((path, label))

    tops = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    scan_targets = tops if tops else ["."]

    for top in scan_targets:
        root = os.path.join(data_dir, top)
        ds = top if top != "." else "root"
        # protocol files first
        for proto in glob.glob(os.path.join(root, "**", "*.txt"), recursive=True) + \
                     glob.glob(os.path.join(root, "**", "*.trl*"), recursive=True):
            for path, lab in _parse_protocol(proto, root):
                add(ds, path, lab)
        # then plain folder-name classification — on the path BELOW the dataset
        # folder, so a dataset name like 'asvspoof'/'wavefake' can't false-trigger.
        for path in glob.glob(os.path.join(root, "**", "*"), recursive=True):
            if not path.lower().endswith(AUDIO_EXT):
                continue
            rel = os.path.relpath(path, root)
            lab = _label_from_path(rel)
            if lab is not None:
                add(ds, path, lab)

    written = []
    total = {"0": 0, "1": 0}
    for ds, rows in datasets.items():
        # de-dup
        rows = list(dict.fromkeys(rows))
        if not rows:
            continue
        out = os.path.join(out_dir, f"{ds}.csv")
        with open(out, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["path", "label", "dataset"])
            for p, l in rows:
                w.writerow([p, l, ds]); total[str(l)] += 1
        n0 = sum(1 for _, l in rows if l == 0); n1 = sum(1 for _, l in rows if l == 1)
        print(f"[manifests] {ds:20s}  bonafide={n0:6d}  spoof={n1:6d}  -> {out}")
        written.append(out)

    if not written:
        print("[manifests] no labelled audio found. Expected real/fake keywords in "
              "folder names (e.g. real/, fake/, bonafide/, spoof/).")
    else:
        print(f"[manifests] TOTAL bonafide={total['0']}  spoof={total['1']}  "
              f"across {len(written)} datasets.")
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "manifests"))
    a = ap.parse_args()
    build(a.data_dir, a.out)
