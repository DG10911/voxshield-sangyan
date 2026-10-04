const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  await p.goto("http://localhost:8000/voxshield/#/overview", { waitUntil: "networkidle" });
  await p.waitForTimeout(600);
  await p.keyboard.press("Meta+k");
  await p.waitForTimeout(500);
  const open = await p.locator("#command-results").count();
  await p.keyboard.type("Hindi");
  await p.waitForTimeout(600);
  const res = await p.locator("#command-results button").count();
  const first = res ? (await p.locator("#command-results button").first().innerText()).replace(/\n/g," ") : "-";
  console.log("palette open=" + open + " results=" + res + " first=[" + first + "]");
  if (res) { await p.locator("#command-results button").first().click(); await p.waitForTimeout(700); console.log("navigated to " + p.url()); }
  await b.close();
})();
