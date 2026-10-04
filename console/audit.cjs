const { chromium } = require("playwright");
const base = "http://localhost:8000/voxshield/#/";
const routes = ["overview","analyze","live","calls","languages","evidence","registries","results","threats","speakers","products","integrations","corpus","training","ops","deployment","roadmap"];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1500, height: 950 } });
  const p = await ctx.newPage();
  let errs = [];
  const hook = () => {
    p.on("pageerror", e => errs.push("pageerror: " + e.message));
    p.on("console", m => { if (m.type() === "error") errs.push("console: " + m.text()); });
    p.on("requestfailed", r => { const f = r.failure(); if (f) errs.push("reqfail: " + r.url().slice(0, 60) + " " + f.errorText); });
  };
  hook();
  const out = [];
  for (const r of routes) {
    errs = [];
    await p.goto(base + r, { waitUntil: "networkidle" });
    await p.waitForTimeout(1100);
    const h1 = (await p.locator("h1").first().textContent().catch(() => null)) || "-";
    const crash = await p.locator("text=/something went wrong|view error/i").count().catch(() => 0);
    const links = await p.locator("a[href^='#/']").count();
    const buttons = await p.locator("button").count();
    await p.screenshot({ path: "/tmp/audit_" + r + ".png" });
    out.push(r.padEnd(12) + " h1=" + h1.slice(0, 40).padEnd(42) + " links=" + links + " buttons=" + buttons + " crash=" + crash + " errs=" + errs.length);
    if (errs.length) out.push("   " + errs.slice(0, 3).join(" | "));
  }
  errs = [];
  await p.goto(base + "analyze", { waitUntil: "networkidle" });
  await p.getByRole("button", { name: /Analyze signal/i }).click().catch(e => errs.push("click:" + e.message));
  await p.waitForTimeout(2600);
  const verdict = await p.locator("text=/SYNTHETIC|HUMAN|ABSTAIN/").first().textContent().catch(() => null);
  const canvases = await p.locator("canvas").count();
  const spec = await p.getByText(/spectrogram/i).count();
  await p.screenshot({ path: "/tmp/audit_analyze_result.png" });
  out.push("ANALYZE: verdict=" + verdict + " canvases=" + canvases + " spectrogramLabel=" + spec + " errs=" + errs.length);
  errs = [];
  await p.keyboard.press("Meta+k");
  await p.waitForTimeout(500);
  const palVisible = await p.locator("input").first().isVisible().catch(() => false);
  await p.keyboard.type("Hindi model");
  await p.waitForTimeout(600);
  const palRes = await p.getByText(/Hindi/i).count();
  await p.screenshot({ path: "/tmp/audit_palette.png" });
  out.push("PALETTE: open=" + palVisible + " hindiResults=" + palRes + " errs=" + errs.length);
  console.log(out.join("\n"));
  await b.close();
})();
