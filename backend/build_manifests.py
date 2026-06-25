"""
VoxShield — dataset manifest auto-builder.

Scans a data directory and writes one CSV per dataset (columns: path,label,dataset;
label 1 = spoof/fake, 0 = bonafide/real). Auto-detects common layouts so you don't
hand-write protocols.

Put datasets under  voxshield/data/<dataset_name>/  in ANY of these shapes:

  A) Split folders:   <dataset>/real/*.wav      <dataset>/fake/*.wav
     (also accepts bonafide|genuine|human  vs  spoof|synthetic|generated|tts|vc)

  B) ASVspoof protocol: a *.txt protocol with lines like
         LA_0001 LA_T_123 - - bonafide
     plus a folder of .flac/.wav. We map utt-id -> file and bonafide/spoof -> 0/1.

  C) Meta CSV:        <dataset>/meta.csv  with columns containing a path/file and a
     label/type column (values real/fake/bonafide/spoof).

  D) Fallback:        any audio whose path contains spoof|fake|synth|tts|vc -> 1,
     else 0  (best-effort; prints a warning).

Usage:
    python build_manifests.py                 # scans ../data, writes ./manifests
    python build_manifests.py --data /path     --out ./manifests
"""
from __future__ import annotations
import os, csv, argparse, glob, re

AUDIO_EXT = (".wav", ".flac", ".mp3", ".m4a", ".ogg", ".webm")
REAL_TOK = ("real", "bonafide", "bona-fide", "genuine", "human", "live")
FAKE_TOK = ("fake", "spoof", "synthetic", "generated", "tts", "vc", "clone", "deepfake")


def _is_audio(p): return p.lower().endswith(AUDIO_EXT)


def _audio_under(d):
    out = []
    for ext in AUDIO_EXT:
        out += glob.glob(os.path.join(d, "**", "*" + ext), recursive=True)
    return out


def _label_from_path(p):
    low = p.lower()
    if any(t in low for t in FAKE_TOK): return 1
    if any(t in low for t in REAL_TOK): return 0
    return None


def from_split_folders(ds_dir):
    rows = []
    for sub in os.listdir(ds_dir):
        full = os.path.join(ds_dir, sub)
        if not os.path.isdir(full):
            continue
        low = sub.lower()
        lab = 1 if any(t in low for t in FAKE_TOK) else 0 if any(t in low for t in REAL_TOK) else None
        if lab is None:
            continue
        for f in _audio_under(full):
            rows.append((f, lab))
    return rows


def from_protocol(ds_dir):
    rows = []
    protos = glob.glob(os.path.join(ds_dir, "**", "*.txt"), recursive=True) + \
             glob.glob(os.path.join(ds_dir, "**", "*protocol*"), recursive=True)
    audio = {os.path.splitext(os.path.basename(f))[0]: f for f in _audio_under(ds_dir)}
    if not audio:
        return rows
    for proto in protos:
        try:
            with open(proto) as fh:
                for line in fh:
                    toks = line.split()
                    if not toks:
                        continue
                    lab = None
                    if "bonafide" in toks: lab = 0
                    elif "spoof" in toks: lab = 1
                    if lab is None:
                        continue
                    uid = next((t for t in toks if t in audio), None)
                    if uid:
                        rows.append((audio[uid], lab))
        except Exception:
            pass
    return rows


def from_meta_csv(ds_dir):
    rows = []
    for meta in glob.glob(os.path.join(ds_dir, "**", "*.csv"), recursive=True) + \
               glob.glob(os.path.join(ds_dir, "*.txt")):
        try:
            with open(meta, newline="") as fh:
                rdr = csv.DictReader(fh)
                if not rdr.fieldnames:
                    continue
                cols = {c.lower(): c for c in rdr.fieldnames}
                pcol = next((cols[c] for c in cols if c in ("path", "file", "filename", "utt", "audio")), None)
                lcol = next((cols[c] for c in cols if c in ("label", "type", "class", "key", "target")), None)
                if not (pcol and lcol):
                    continue
                base = os.path.dirname(meta)
                for r in rdr:
                    val = str(r[lcol]).lower()
                    lab = 1 if any(t in val for t in FAKE_TOK) else 0 if any(t in val for t in REAL_TOK) else None
                    if lab is None:
                        continue
                    p = r[pcol]
                    if not os.path.isabs(p):
                        cand = os.path.join(base, p)
                        p = cand if os.path.exists(cand) else (p + (".wav" if not _is_audio(p) else ""))
                    rows.append((p, lab))
        except Exception:
            pass
    return rows


def from_fallback(ds_dir):
    rows, unknown = [], 0
    for f in _audio_under(ds_dir):
        lab = _label_from_path(f)
        if lab is None:
            unknown += 1; lab = 0
        rows.append((f, lab))
    if unknown:
        print(f"   ! {unknown} files had no real/fake hint -> defaulted to bonafide(0). "
              f"Rename folders real/ & fake/ for correctness.")
    return rows


def build_dataset(ds_dir, ds_name, out_dir):
    for fn in (from_split_folders, from_protocol, from_meta_csv, from_fallback):
        rows = fn(ds_dir)
        if rows:
            # de-dup, keep existing files only
            seen, clean = set(), []
            for p, l in rows:
                if p in seen:
                    continue
                seen.add(p)
                if os.path.exists(p):
                    clean.append((p, l))
            if clean:
                out = os.path.join(out_dir, ds_name + ".csv")
                with open(out, "w", newline="") as fh:
                    w = csv.writer(fh); w.writerow(["path", "label", "dataset"])
                    for p, l in clean:
                        w.writerow([p, l, ds_name])
                pos = sum(l for _, l in clean)
                print(f"  ✓ {ds_name}: {len(clean)} files ({pos} fake / {len(clean)-pos} real) "
                      f"via {fn.__name__} -> {os.path.basename(out)}")
                return out
    print(f"  · {ds_name}: no audio found, skipped")
    return None


def main(data_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    if not os.path.isdir(data_dir):
        print(f"[manifests] no data dir at {data_dir} — nothing to build "
              f"(the system will self-test instead).")
        return []
    built = []
    for name in sorted(os.listdir(data_dir)):
        d = os.path.join(data_dir, name)
        if os.path.isdir(d):
            m = build_dataset(d, name, out_dir)
            if m:
                built.append(m)
    print(f"[manifests] built {len(built)} dataset manifest(s) in {out_dir}")
    return built


if __name__ == "__main__":
    here = os.path.dirname(__file__)
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(here, "..", "data"))
    ap.add_argument("--out", default=os.path.join(here, "manifests"))
    a = ap.parse_args()
    main(os.path.abspath(a.data), os.path.abspath(a.out))
