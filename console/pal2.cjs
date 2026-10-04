const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  const errs=[]; p.on("pageerror",e=>errs.push(e.message));
  await p.goto("http://localhost:8000/voxshield/#/overview", { waitUntil: "networkidle" });
  await p.getByRole("button", { name: /Search intelligence/i }).click();
  await p.waitForTimeout(400);
  const input = p.getByRole("combobox", { name: /Search commands/i });
  await input.fill("Hindi");
  await p.waitForTimeout(500);
  const res = await p.locator("#command-results button").count();
  const labels = await p.locator("#command-results button").allInnerTexts();
  console.log("results=" + res);
  console.log(labels.map(t=>t.replace(/\n/g," ")).slice(0,6).join(" | "));
  if (res) { await p.locator("#command-results button").first().click(); await p.waitForTimeout(600); console.log("navigated=" + p.url()); }
  console.log("errs=" + errs.length);
  await b.close();
})();
