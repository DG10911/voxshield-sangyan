// VoxShield dashboard — fusion + streaming.
// All audio (uploads AND mic recordings) is decoded and re-encoded to clean
// 16 kHz mono WAV IN THE BROWSER before upload, so the backend never has to
// deal with webm/opus/mp3/m4a containers (this fixes "Format not recognised").
const $ = (s) => document.querySelector(s);
const API = "";
const TARGET_SR = 16000;

fetch(API + "/api/health").then(r => r.json()).then(h => {
  $("#hstatus").textContent = "● " + h.status + " · " + h.ensemble_size + " detectors";
  $("#mModel").textContent = h.model;
  $("#mBackend").textContent = (h.neural_active ? "Neural+Acoustic" : "Acoustic") + " · " + h.ensemble_size + " models";
}).catch(() => { $("#hstatus").textContent = "● backend offline"; });

// ---------- audio -> 16 kHz mono WAV (client-side) ----------
async function toWav(blobOrFile) {
  const buf = await blobOrFile.arrayBuffer();
  const AC = window.AudioContext || window.webkitAudioContext;
  const tmp = new AC();
  const decoded = await tmp.decodeAudioData(buf);          // handles wav/mp3/m4a/flac/webm
  tmp.close && tmp.close();
  // resample to 16k mono via OfflineAudioContext
  const dur = decoded.duration;
  const off = new OfflineAudioContext(1, Math.ceil(dur * TARGET_SR), TARGET_SR);
  const src = off.createBufferSource(); src.buffer = decoded; src.connect(off.destination); src.start();
  const rendered = await off.startRendering();
  return encodeWav(rendered.getChannelData(0), TARGET_SR);
}

function encodeWav(samples, sr) {
  const buf = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buf);
  const w = (off, s) => { for (let i = 0; i < s.length; i++) view.setUint8(off + i, s.charCodeAt(i)); };
  w(0, "RIFF"); view.setUint32(4, 36 + samples.length * 2, true); w(8, "WAVE");
  w(12, "fmt "); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, sr, true); view.setUint32(28, sr * 2, true);
  view.setUint16(32, 2, true); view.setUint16(34, 16, true);
  w(36, "data"); view.setUint32(40, samples.length * 2, true);
  let off = 44;
  for (let i = 0; i < samples.length; i++, off += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Blob([view], { type: "audio/wav" });
}

// ---------- file / drag-drop ----------
const drop = $("#drop"), fileInput = $("#file");
$("#browse").onclick = (e) => { e.stopPropagation(); fileInput.click(); };
drop.onclick = () => fileInput.click();
drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("drag"); };
drop.ondragleave = () => drop.classList.remove("drag");
drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove("drag"); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); };
fileInput.onchange = () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); };

// ---------- live recording ----------
let mediaRec, chunks = [];
$("#rec").onclick = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRec = new MediaRecorder(stream); chunks = [];
    mediaRec.ondataavailable = (e) => chunks.push(e.data);
    mediaRec.onstop = () => {
      const blob = new Blob(chunks, { type: mediaRec.mimeType || "audio/webm" });
      handleFile(blob, "live-recording.wav");
      stream.getTracks().forEach(t => t.stop());
    };
    mediaRec.start(); $("#rec").disabled = true; $("#stopRec").disabled = false; $("#recState").textContent = "● recording…";
  } catch (err) { $("#recState").textContent = "mic unavailable: " + err.message; }
};
$("#stopRec").onclick = () => { if (mediaRec && mediaRec.state !== "inactive") mediaRec.stop(); $("#rec").disabled = false; $("#stopRec").disabled = true; $("#recState").textContent = ""; };

// ---------- analyse ----------
async function handleFile(blob, nameOverride) {
  const name = nameOverride || blob.name || "audio.wav";
  $("#fileName").textContent = name;
  $("#vbig").textContent = "Preparing…"; $("#vaction").textContent = "Converting audio to 16 kHz WAV…";
  let wav;
  try { wav = await toWav(blob); }
  catch (e) { $("#vbig").textContent = "Error"; $("#vaction").textContent = "Could not read this audio file (" + e.message + "). Try a WAV/MP3."; return; }

  $("#vbig").textContent = "Analysing…"; $("#vaction").textContent = "Running fusion of all detectors.";
  const fd = new FormData(); fd.append("file", new File([wav], name.replace(/\.\w+$/, ".wav"), { type: "audio/wav" }));
  const endpoint = mode() === "stream" ? "/api/stream-analyze" : "/api/analyze";
  try {
    const res = await fetch(API + endpoint, { method: "POST", body: fd });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    render(await res.json());
  } catch (e) { $("#vbig").textContent = "Error"; $("#vaction").textContent = String(e.message || e); }
}

function mode() { return document.querySelector('input[name="mode"]:checked').value; }

function render(r) {
  const img = $("#spec"); img.src = r.spectrogram; img.style.display = "block"; $("#specEmpty").style.display = "none";

  const cls = r.label.toLowerCase();
  $("#verdict").className = "verdict " + cls;
  $("#vbig").textContent = r.label + " RISK";
  $("#vico").textContent = cls === "high" ? "⚠" : cls === "med" ? "!" : "✓";
  $("#vaction").textContent = r.action;
  $("#vconf").textContent = r.confidence + "%";
  $("#tlbar").style.width = Math.round(r.score * 100) + "%";
  $("#scoreTxt").textContent = "score " + r.score.toFixed(3) + " · " + r.n_models + " models";
  $("#kLat").textContent = r.latency_s + "s";

  document.querySelectorAll("#reasons li").forEach(li => {
    const k = li.dataset.k, val = r.reasons[k] ?? 0;
    li.querySelector(".val").textContent = val.toFixed(2);
    li.querySelector(".bar>i").style.width = Math.round(val * 100) + "%";
    li.classList.toggle("hit", val >= 0.55);
  });

  const pm = r.per_model || {};
  $("#perModel").innerHTML = Object.entries(pm).map(([k, v]) =>
    `<tr><td>${k}<div class="pm-bar"><i style="width:${Math.round(v * 100)}%"></i></div></td>
         <td class="mono" style="text-align:right;vertical-align:top">${v.toFixed(3)}</td></tr>`).join("")
    || '<tr><td colspan="2" class="muted">No detectors returned a score.</td></tr>';
  const f = r.fusion || {};
  $("#fusionNote").textContent = `model-fused ${f.model_fused ?? "—"} · reason-fused ${f.reason_fused ?? "—"} · head ${f.head ?? "—"} · calibrated ${f.calibrated ? "yes" : "no"}`;

  // feature analysis panel
  if (r.features && $("#featTable")) {
    const ft = r.features;
    const rows = [
      ["Duration", ft.duration + "s"], ["Sample rate", ft.sr + " Hz"],
      ["Narrowband (8 kHz)", ft.narrowband ? "yes ⚠" : "no"],
      ["HF energy ratio", ft.hf_energy_ratio], ["HF regularity", ft.hf_regularity],
      ["Spectral flatness", ft.spectral_flatness], ["Phase regularity", ft.phase_reg],
      ["F0 jitter", ft.f0_jitter], ["Shimmer", ft.shimmer],
      ["Voiced ratio", ft.f0_voiced_ratio], ["Silence ratio", ft.silence_ratio],
      ["Breath score", ft.breath_score],
    ];
    $("#featTable").innerHTML = rows.map(([k, v]) =>
      `<tr><td>${k}</td><td class="mono" style="text-align:right">${v}</td></tr>`).join("");
  }

  const sw = $("#streamWrap");
  if (r.timeline && r.timeline.length) {
    sw.style.display = "block"; drawTimeline(r.timeline);
    $("#flagTxt").textContent = r.flagged_at_s != null
      ? `flagged at ${r.flagged_at_s}s ${r.decided_within_10s ? "✓ within 10s" : ""}` : "no flag (low risk)";
  } else sw.style.display = "none";

  refreshLog();
}

function drawTimeline(tl) {
  const cv = $("#timeline"), ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height; ctx.clearRect(0, 0, W, H);
  const pad = 24, maxT = Math.max(10, tl[tl.length - 1].t);
  const x = (t) => pad + (t / maxT) * (W - pad * 1.5);
  const y = (s) => H - pad - s * (H - pad * 1.5);
  ctx.strokeStyle = "rgba(255,255,255,.35)"; ctx.setLineDash([4, 4]); ctx.beginPath();
  ctx.moveTo(pad, y(0.70)); ctx.lineTo(W - pad / 2, y(0.70)); ctx.stroke(); ctx.setLineDash([]);
  ctx.fillStyle = "#9fc6ff"; ctx.font = "10px monospace";
  ctx.fillText("0.70", 2, y(0.70) + 3); ctx.fillText("0s", pad, H - 6); ctx.fillText(maxT + "s", W - 26, H - 6);
  ctx.strokeStyle = "#36d27e"; ctx.lineWidth = 2; ctx.beginPath();
  tl.forEach((p, i) => { const px = x(p.t), py = y(p.running); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
  ctx.stroke();
  tl.forEach(p => { ctx.fillStyle = p.running >= 0.70 ? "#ff6b6b" : "#36d27e"; ctx.beginPath(); ctx.arc(x(p.t), y(p.running), 3, 0, 7); ctx.fill(); });
}

async function refreshLog() {
  try {
    const { entries } = await (await fetch(API + "/api/audit")).json();
    if (!entries.length) return;
    $("#log").innerHTML = entries.map(e => `<tr>
      <td class="mono">${e.time}</td><td class="mono">${e.audio_sha256}</td>
      <td><span class="tag ${e.label.toLowerCase()}">${e.label}</span></td>
      <td class="mono">${e.confidence}%</td></tr>`).join("");
  } catch {}
}
