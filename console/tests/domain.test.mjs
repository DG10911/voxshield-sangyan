import { test } from "node:test";
import assert from "node:assert/strict";
import { build } from "esbuild";
async function load(path, defines = {}) {
  const result = await build({
    entryPoints: [new URL("../src/" + path, import.meta.url).pathname],
    bundle: true,
    write: false,
    format: "esm",
    platform: "node",
    define: defines,
  });
  return import(
    "data:text/javascript;base64," +
      Buffer.from(result.outputFiles[0].text).toString("base64")
  );
}
const mock = await load("services/mock.ts");
const catalog = await load("data/catalog.ts");
const client = await load("services/api.ts", {
  "import.meta.env": '{"VITE_DEMO_MODE":"true"}',
});
test("all verdicts preserve uncertainty and complete evidence", () => {
  for (const v of ["HUMAN", "SYNTHETIC", "ABSTAIN"]) {
    const r = mock.mockAnalysis(v, "sample.wav", "TEST");
    assert.equal(r.verdict, v);
    assert.equal(r.source, "demo");
    assert.equal(r.detectors.length, 9);
    assert.ok(r.confidence > 0 && r.confidence < 100);
    assert.ok(r.reasons.length >= 3);
  }
  assert.ok(
    mock.mockAnalysis("ABSTAIN").reasons.includes("MODEL_DISAGREEMENT"),
  );
});
test("stream threshold crosses at four seconds, never earlier", () => {
  for (let t = 0; t < 4; t += 0.25) assert.ok(mock.liveConfidence(t) < 80);
  assert.ok(mock.liveConfidence(4) >= 80);
  assert.ok(mock.liveConfidence(120) <= 94);
});
test("supplied benchmarks and pending language data are preserved", () => {
  const hi = catalog.languages.find((l) => l.iso === "hi");
  assert.equal(hi.clean, 0.09);
  assert.equal(hi.phone, 0.29);
  assert.equal(catalog.languages.filter((l) => l.clean !== null).length, 12);
  assert.equal(catalog.languages.filter((l) => l.clean === null).length, 9);
  assert.equal(catalog.languages.find((l) => l.iso === "ml").phone, 37.81);
  assert.equal(
    catalog.detectors.reduce((s, d) => s + d.weight, 0),
    100,
  );
});
test("registry and navigation scope matches requested core surfaces", () => {
  assert.equal(catalog.pages.length, 17);
  assert.equal(catalog.generators.length, 28);
  assert.equal(catalog.attackModes.length, 26);
  assert.equal(catalog.recipes.length, 17);
  assert.equal(
    new Set(mock.initialCalls.map((c) => c.id)).size,
    mock.initialCalls.length,
  );
});
test("CSV quotes commas and embedded quotes", () => {
  assert.equal(
    client.csv([{ name: "one, two", detail: 'a "quote"' }]),
    '"name","detail"\n"one, two","a ""quote"""',
  );
});
test("demo analysis never sends a network request", async () => {
  const old = globalThis.fetch;
  globalThis.fetch = () => {
    throw new Error("Unexpected network");
  };
  try {
    const r = await client.api.analyze(null, "ABSTAIN", "test");
    assert.equal(r.id, "test");
    assert.equal(r.verdict, "ABSTAIN");
  } finally {
    globalThis.fetch = old;
  }
});
test("HTTP errors are surfaced to the fallback boundary", async () => {
  const old = globalThis.fetch;
  globalThis.fetch = async () => new Response("", { status: 503 });
  try {
    await assert.rejects(() => client.request("/api/health"), /503/);
  } finally {
    globalThis.fetch = old;
  }
});

test("live analysis rejects incomplete backend contracts", async () => {
  const live = await load("services/api.ts", {
    "import.meta.env": '{"VITE_DEMO_MODE":"false"}',
  });
  const old = globalThis.fetch;
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        verdict: "SYNTHETIC",
        confidence: 99,
        detectors: [],
        reasons: [],
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  try {
    await assert.rejects(
      () =>
        live.api.analyze(
          new File(["audio"], "sample.wav"),
          "SYNTHETIC",
          "test",
        ),
      /Unexpected analysis response/,
    );
  } finally {
    globalThis.fetch = old;
  }
});
