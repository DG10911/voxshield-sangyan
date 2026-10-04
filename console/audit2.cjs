const { chromium } = require("playwright");
const base = "http://localhost:8000/voxshield/#/";
const routes = ["overview","analyze","live","calls","languages","evidence","registries","results","threats","speakers","products","integrations","corpus","training","ops","deployment","roadmap"];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  let errs = [];
  p.on("pageerror", e => errs.push("pageerror: " + e.message));
  p.on("console", m => { if (m.type() === "error") errs.push("console: " + m.text()); });
  p.on("response", r => { if (r.status() >= 400) errs.push("http" + r.status() + ": " + r.url()); });
  const out = [];
  for (const r of routes) {
    errs = [];
    await p.goto(base + r, { waitUntil: "networkidle" });
    await p.waitForTimeout(900);
    const h1 = (await p.locator("h1").first().textContent().catch(() => "-")) || "-";
    await p.screenshot({ path: "/tmp/a2_" + r + ".png" });
    out.push(r.padEnd(12) + " h1=" + h1.slice(0, 36).padEnd(38) + " errs=" + errs.length + (errs.length ? "  " + errs.slice(0,2).join(" | ") : ""));
  }
  errs = [];
  await p.goto(base + "analyze", { waitUntil: "networkidle" });
  await p.waitForTimeout(700);
  await p.getByText(/Investment voice clone/i).click().catch(e => errs.push("scenario:" + e.message));
  await p.getByRole("button", { name: /Analyze signal/i }).click().catch(e => errs.push("analyze:" + e.message));
  await p.waitForTimeout(2600);
  await p.getByRole("button", { name: /^Transcript$/ }).click().catch(() => {});
  await p.waitForTimeout(900);
  const spec = await p.getByText(/spectrogram/i).count();
  const canvases = await p.locator("canvas").count();
  const reportTab = await p.getByText(/Export report/i).count();
  await p.screenshot({ path: "/tmp/a2_analyze_result.png", fullPage: true });
  out.push("ANALYZE spLabel=" + spec + " canvases=" + canvases + " exportBtn=" + reportTab + " errs=" + errs.length + (errs.length ? "  " + errs.join(" | ") : ""));
  console.log(out.join("\n"));
  await b.close();
})();
