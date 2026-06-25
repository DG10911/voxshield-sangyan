"""
VoxShield — concurrent call SIMULATION / load test.
Fires many calls at the API at once and reports throughput + latency,
proving the system handles multiple simultaneous calls.

USAGE (server must be running):
  python simulate_load.py --file /path/clip.wav --concurrency 8 --total 40
  python simulate_load.py --dir  /path/clips    --concurrency 12 --total 60   # mixed call feed

Tip for max throughput, run the server with workers:
  uvicorn app:app --port 8000 --workers 4
"""
from __future__ import annotations
import os, sys, time, glob, random, argparse, statistics
import concurrent.futures as cf
import urllib.request, mimetypes, uuid

def _post(url, path):
    """Minimal multipart POST using stdlib (no extra installs)."""
    boundary = "----vox" + uuid.uuid4().hex
    fname = os.path.basename(path)
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"{fname}\"\r\nContent-Type: {ctype}\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    t = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=180)
        import json
        j = json.loads(r.read())
        return True, time.time() - t, j.get("label")
    except Exception as e:
        return False, time.time() - t, str(e)[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000/api/analyze")
    ap.add_argument("--file", help="single clip to fire repeatedly")
    ap.add_argument("--dir", help="folder of clips (mixed feed)")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--total", type=int, default=40)
    a = ap.parse_args()

    if a.dir:
        pool = [p for p in glob.glob(os.path.join(a.dir, "*"))
                if p.lower().endswith((".wav", ".mp3", ".flac", ".m4a", ".ogg"))]
        if not pool: sys.exit("no audio files in --dir")
        clips = [random.choice(pool) for _ in range(a.total)]
    elif a.file:
        clips = [a.file] * a.total
    else:
        sys.exit("give --file or --dir")

    print(f"\n  Simulating {a.total} incoming calls, {a.concurrency} at a time → {a.url}\n")
    t0 = time.time(); lat = []; ok = 0; labels = {}
    with cf.ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(_post, a.url, c) for c in clips]
        for i, fu in enumerate(cf.as_completed(futs), 1):
            good, dt, label = fu.result(); lat.append(dt); ok += good
            if good: labels[label] = labels.get(label, 0) + 1
            sys.stdout.write(f"\r  done {i}/{a.total}"); sys.stdout.flush()
    T = time.time() - t0
    lat.sort()
    p = lambda q: lat[min(len(lat) - 1, int(len(lat) * q))]
    print("\n\n  ===== LOAD TEST RESULT =====")
    print(f"  Calls         : {a.total}   (success {ok}/{a.total})")
    print(f"  Concurrency   : {a.concurrency}")
    print(f"  Wall time     : {T:.1f} s")
    print(f"  Throughput    : {a.total / T:.1f} calls/sec  =  {a.total / T * 60:.0f} calls/min")
    print(f"  Latency  avg  : {statistics.mean(lat):.2f} s")
    print(f"  Latency  p50  : {p(0.50):.2f} s   p95 : {p(0.95):.2f} s   max : {max(lat):.2f} s")
    print(f"  Verdicts      : {labels}")
    print("  ============================\n")


if __name__ == "__main__":
    main()
