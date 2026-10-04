const { chromium } = require("playwright");
const base = "http://localhost:8000/voxshield/#/overview";
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  let errs = [];
  p.on("pageerror", e => errs.push("pageerror:" + e.message));
  p.on("console", m => { if (m.type() === "error") errs.push("console:" + m.text()); });
  await p.goto(base, { waitUntil: "networkidle" });
  const nav = p.locator("nav[aria-label='Main navigation'] a");
  const n = await nav.count();
  let ok = 0, bad = [];
  for (let i = 0; i < n; i++) {
    const a = nav.nth(i);
    const label = (await a.innerText()).trim().split("\n")[0];
    await a.click();
    await p.waitForTimeout(550);
    const ch = await p.locator("h1").first().textContent().catch(() => "");
    if (ch && ch.length > 3) ok++; else bad.push(label);
  }
  console.log("NAV: " + ok + "/" + n + " screens loaded" + (bad.length ? " BAD=" + bad.join(",") : ""));
  // command palette -> open result
  await p.mouse.click(750, 300);
  await p.keyboard.press("Meta+k");
  await p.waitForTimeout(500);
  await p.keyboard.type("Hindi model");
  await p.waitForTimeout(500);
  const cmdResults = await p.locator("#command-results button").count();
  if (cmdResults) { await p.locator("#command-results button").first().click(); await p.waitForTimeout(600); }
  const afterCmd = p.url();
  console.log("PALETTE: results=" + cmdResults + " navigated=" + afterCmd.includes("languages"));
  // button smoke test on heavy pages
  for (const r of ["registries","languages","training","deployment","products"]) {
    await p.goto("http://localhost:8000/voxshield/#/" + r, { waitUntil: "networkidle" });
    await p.waitForTimeout(500);
    const btns = p.locator("main button");
    const cnt = await btns.count();
    let clicked = 0;
    for (let i = 0; i < Math.min(cnt, 6); i++) { try { await btns.nth(i).click({ timeout: 1200 }); clicked++; await p.waitForTimeout(120); } catch {} }
    console.log("BTNS " + r + ": " + clicked + "/" + Math.min(cnt,6) + " clicked");
  }
  console.log("TOTAL ERRORS: " + errs.length + (errs.length ? "\n" + errs.slice(0,8).join("\n") : ""));
  await b.close();
})();
