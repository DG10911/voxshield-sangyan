"""
VoxShield Python SDK — thin client over the REST/WebSocket API.

    from voxshield import VoxShield
    vs = VoxShield("http://localhost:8000")
    print(vs.analyze("call.wav"))              # whole-clip verdict + voxscore + brains
    print(vs.risk_score({"neural:xls-r": 0.92}))
    print(vs.gateway_decide(voxscore, context={"high_value_action": True}))

Stdlib only (urllib) — no third-party deps. Mirrors backend/app.py endpoints.
"""
from __future__ import annotations
import json, urllib.request, urllib.parse, mimetypes, uuid
from typing import Dict, Optional


class VoxShield:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 60.0):
        self.base = base_url.rstrip("/"); self.timeout = timeout

    # ---- core ----
    def health(self) -> Dict: return self._get("/api/health")
    def analyze(self, path: str) -> Dict: return self._upload("/api/analyze", path)
    def stream_analyze(self, path: str, threshold: float = 0.70) -> Dict:
        return self._upload(f"/api/stream-analyze?threshold={threshold}", path)
    def speaker_verify(self, reference: str, probe: str) -> Dict:
        return self._upload("/api/speaker/verify", {"reference": reference, "probe": probe})

    # ---- intelligence / risk ----
    def risk_score(self, per_model: Dict[str, float], context: Optional[Dict] = None) -> Dict:
        return self._post("/api/risk/score", {"per_model": per_model, "context": context or {}})
    def threats(self, n: int = 8) -> Dict: return self._get(f"/api/threats?n={n}")
    def threat_search(self, language: Optional[str] = None, min_eer: float = 0.0) -> Dict:
        q = urllib.parse.urlencode({k: v for k, v in (("language", language), ("min_eer", min_eer)) if v is not None})
        return self._get(f"/api/threat/search?{q}")
    def intel(self, language: Optional[str] = None, codec: Optional[str] = None,
              worst_by: Optional[str] = None, metric: str = "eer_pct") -> Dict:
        q = urllib.parse.urlencode({k: v for k, v in
              (("language", language), ("codec", codec), ("worst_by", worst_by), ("metric", metric)) if v})
        return self._get(f"/api/intel?{q}")

    # ---- product surfaces ----
    def gateway_decide(self, voxscore: Dict, context: Optional[Dict] = None) -> Dict:
        return self._post("/api/gateway/decide", {"voxscore": voxscore, "context": context or {}})
    def consumer_check(self, voxscore: Dict) -> Dict:
        return self._post("/api/consumer/check", {"voxscore": voxscore})
    def deployment_profile(self, surface: str = "cloud") -> Dict:
        return self._get(f"/api/deployment/profile?surface={surface}")
    def warroom(self) -> Dict: return self._get("/api/warroom")

    # ---- transport ----
    def _get(self, path: str) -> Dict:
        with urllib.request.urlopen(self.base + path, timeout=self.timeout) as r:
            return json.loads(r.read().decode())

    def _post(self, path: str, payload: Dict) -> Dict:
        req = urllib.request.Request(self.base + path, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode())

    def _upload(self, path: str, files) -> Dict:
        if isinstance(files, str):
            files = {"file": files}
        boundary = uuid.uuid4().hex; body = b""
        for field, fp in files.items():
            ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
            with open(fp, "rb") as fh:
                data = fh.read()
            body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
                     f"filename=\"{fp.split('/')[-1]}\"\r\nContent-Type: {ctype}\r\n\r\n").encode()
            body += data + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(self.base + path, data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode())


if __name__ == "__main__":
    # offline sanity: builds requests without a live server
    vs = VoxShield("http://localhost:8000")
    assert vs.base == "http://localhost:8000"
    print("[VoxShield py-sdk] methods:", [m for m in dir(vs) if not m.startswith("_")])
    print("OK — point at a running VoxShield API to use.")
