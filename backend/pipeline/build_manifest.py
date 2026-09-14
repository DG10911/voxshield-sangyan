"""
VoxShield unified manifest builder.

Scans the downloaded corpus and emits ONE manifest CSV with a common schema, so
train/val/test splits are just filters. Audio in the parquet datasets stays inside
the parquet (no wav explosion) — the manifest points to (parquet_file, row_index).

Verified schemas (2026-09):
  IndicSynth        parquet per-lang dir; cols: audio{bytes,path}, "Generative Model",
                    "Target Speaker ID", Gender ; ALL FAKE ; lang = dir name
  IndicVoices real  parquet; cols: audio_filepath{bytes,path}, speaker_id, lang, gender ; ALL REAL
  DFADD             parquet; cols: audio{bytes,path}, audio_name, split, label(spoofed/bonafide) ; EN
  MLAAD             wav tree fake/<lang>/<model>/*.wav + meta.csv ; ALL FAKE

Output columns:
  dataset, locator, is_parquet, row_index, label(0/1), speaker, lang, generator, orig_split

Usage:
  python build_manifest.py --data-root /Volumes/KIOXIA/voxdata/raw --out manifests_v2/manifest.csv
"""
import os, csv, glob, argparse

def _rel(p, root): return os.path.relpath(p, root)

def scan_indicsynth(root):
    base = os.path.join(root, "indicsynth")
    rows = []
    if not os.path.isdir(base): return rows
    import pyarrow.parquet as pq
    for lang_dir in sorted(glob.glob(os.path.join(base, "*"))):
        if not os.path.isdir(lang_dir): continue
        lang = os.path.basename(lang_dir).lower()
        for pf in sorted(glob.glob(os.path.join(lang_dir, "*.parquet"))):
            t = pq.read_table(pf, columns=["Generative Model", "Target Speaker ID"])
            gens = t.column("Generative Model").to_pylist()
            spks = t.column("Target Speaker ID").to_pylist()
            for i in range(t.num_rows):
                rows.append(dict(dataset="indicsynth", locator=_rel(pf, root), is_parquet=1,
                                 row_index=i, label=1, speaker=f"is_{lang}_{spks[i]}",
                                 lang=lang, generator=str(gens[i]).lower(), orig_split="train"))
    return rows

def scan_indicvoices_real(root):
    base = os.path.join(root, "indicvoices_real")
    rows = []
    if not os.path.isdir(base): return rows
    import pyarrow.parquet as pq
    for pf in sorted(glob.glob(os.path.join(base, "**", "*.parquet"), recursive=True)):
        t = pq.read_table(pf, columns=["speaker_id", "lang"])
        spk = t.column("speaker_id").to_pylist(); lg = t.column("lang").to_pylist()
        for i in range(t.num_rows):
            rows.append(dict(dataset="indicvoices", locator=_rel(pf, root), is_parquet=1,
                             row_index=i, label=0, speaker=f"iv_{spk[i]}",
                             lang=str(lg[i]).lower(), generator="real", orig_split="train"))
    return rows

def scan_dfadd(root):
    base = os.path.join(root, "dfadd")
    rows = []
    if not os.path.isdir(base): return rows
    import pyarrow.parquet as pq
    for pf in sorted(glob.glob(os.path.join(base, "**", "*.parquet"), recursive=True)):
        t = pq.read_table(pf, columns=["audio_name", "split", "label"])
        an = t.column("audio_name").to_pylist(); sp = t.column("split").to_pylist(); lb = t.column("label").to_pylist()
        for i in range(t.num_rows):
            name = an[i] or ""
            spk = name.split("_")[0] if name else "unk"           # e.g. p227
            gen = name.rsplit("_", 1)[-1].split(".")[0] if "_" in name else "unk"  # e.g. GradTTS
            rows.append(dict(dataset="dfadd", locator=_rel(pf, root), is_parquet=1, row_index=i,
                             label=0 if str(lb[i]).lower().startswith("bona") else 1,
                             speaker=f"dfadd_{spk}", lang="en", generator=gen.lower(),
                             orig_split=str(sp[i]).lower()))
    return rows

def scan_mlaad(root):
    base = os.path.join(root, "mlaad", "fake")
    rows = []
    if not os.path.isdir(base): return rows
    for wav in glob.glob(os.path.join(base, "*", "*", "*.wav")):
        parts = wav.split(os.sep)
        lang = parts[-3].lower(); model = parts[-2].lower()
        rows.append(dict(dataset="mlaad", locator=_rel(wav, root), is_parquet=0, row_index=-1,
                         label=1, speaker="mlaad_unk", lang=lang, generator=model, orig_split="ood"))
    return rows

SCANNERS = [scan_indicsynth, scan_indicvoices_real, scan_dfadd, scan_mlaad]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="/Volumes/KIOXIA/voxdata/raw")
    ap.add_argument("--out", default="manifests_v2/manifest.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    all_rows = []
    for fn in SCANNERS:
        r = fn(a.data_root)
        print(f"  {fn.__name__}: {len(r)} rows")
        all_rows += r
    fields = ["dataset", "locator", "is_parquet", "row_index", "label",
              "speaker", "lang", "generator", "orig_split"]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(all_rows)
    # quick stats
    from collections import Counter
    print(f"\n[manifest] {len(all_rows)} rows -> {a.out}")
    print("  by dataset:", dict(Counter(r["dataset"] for r in all_rows)))
    print("  by label  :", dict(Counter(r["label"] for r in all_rows)))
    print("  langs     :", sorted(set(r["lang"] for r in all_rows)))
    print("  generators:", sorted(set(r["generator"] for r in all_rows))[:25])

if __name__ == "__main__":
    main()
