/**
 * VoxShield JavaScript/Node SDK — thin client over the REST/WebSocket API.
 *
 *   import { VoxShield } from "./voxshield.js";
 *   const vs = new VoxShield("http://localhost:8000");
 *   console.log(await vs.analyze("./call.wav"));
 *   console.log(await vs.riskScore({ "neural:xls-r": 0.92 }));
 *
 * Uses global fetch (Node 18+ / browsers). No third-party deps.
 * Mirrors backend/app.py endpoints.
 */
export class VoxShield {
  constructor(baseUrl = "http://localhost:8000") {
    this.base = baseUrl.replace(/\/+$/, "");
  }

  // ---- core ----
  health() { return this._get("/api/health"); }
  analyze(file) { return this._upload("/api/analyze", { file }); }
  streamAnalyze(file, threshold = 0.7) { return this._upload(`/api/stream-analyze?threshold=${threshold}`, { file }); }
  speakerVerify(reference, probe) { return this._upload("/api/speaker/verify", { reference, probe }); }

  // ---- intelligence / risk ----
  riskScore(perModel, context = {}) { return this._post("/api/risk/score", { per_model: perModel, context }); }
  threats(n = 8) { return this._get(`/api/threats?n=${n}`); }
  threatSearch({ language, minEer = 0 } = {}) {
    const q = new URLSearchParams({ min_eer: minEer, ...(language ? { language } : {}) });
    return this._get(`/api/threat/search?${q}`);
  }
  intel({ language, codec, worstBy, metric = "eer_pct" } = {}) {
    const q = new URLSearchParams({ metric, ...(language && { language }), ...(codec && { codec }), ...(worstBy && { worst_by: worstBy }) });
    return this._get(`/api/intel?${q}`);
  }

  // ---- product surfaces ----
  gatewayDecide(voxscore, context = {}) { return this._post("/api/gateway/decide", { voxscore, context }); }
  consumerCheck(voxscore) { return this._post("/api/consumer/check", { voxscore }); }
  deploymentProfile(surface = "cloud") { return this._get(`/api/deployment/profile?surface=${surface}`); }
  warroom() { return this._get("/api/warroom"); }

  // ---- transport ----
  async _get(path) {
    const r = await fetch(this.base + path);
    if (!r.ok) throw new Error(`VoxShield ${r.status}: ${await r.text()}`);
    return r.json();
  }
  async _post(path, payload) {
    const r = await fetch(this.base + path, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    if (!r.ok) throw new Error(`VoxShield ${r.status}: ${await r.text()}`);
    return r.json();
  }
  async _upload(path, files) {
    // Node: files are paths; browser: pass File/Blob objects directly.
    const form = new FormData();
    for (const [field, val] of Object.entries(files)) {
      if (typeof val === "string") {
        const fs = await import("node:fs/promises");
        const buf = await fs.readFile(val);
        form.append(field, new Blob([buf]), val.split("/").pop());
      } else {
        form.append(field, val);
      }
    }
    const r = await fetch(this.base + path, { method: "POST", body: form });
    if (!r.ok) throw new Error(`VoxShield ${r.status}: ${await r.text()}`);
    return r.json();
  }
}

export default VoxShield;
