import { useState } from "react";
import { Search, ArrowUpRight } from "lucide-react";
import {
  Panel,
  PageHeader,
  Chip,
  DataTable,
  Modal,
  DetailList,
  ExportButton,
  Bar,
  Tabs,
} from "../components/ui";
import {
  LineChart,
  Sparkline,
  EvidenceGraph,
  Waveform,
} from "../components/charts";
import {
  languages,
  detectors,
  generators,
  attackModes,
  recipes,
  intelNodes,
} from "../data/catalog";
import type { DetectorScore, LanguageMetric, Speaker } from "../types";
import { DetectorInspector } from "./Analyze";
import { useApp } from "../store";
export function Languages() {
  const [selected, setSelected] = useState<LanguageMetric | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");
  const rows = languages.filter(
    (l) =>
      l.name.toLowerCase().includes(query.toLowerCase()) &&
      (filter === "All" || l.status === filter),
  );
  return (
    <>
      <PageHeader
        eyebrow="INTELLIGENCE / LANGUAGE COVERAGE"
        title="Many languages. No blind certainty."
        description="Channel-aware evaluation across the Indic language landscape."
      >
        <ExportButton rows={languages} />
      </PageHeader>
      <div className="grid-main">
        <Panel
          title="A connected language field"
          eyebrow="23 IN SCOPE · 21 NAMED IN SOURCE"
        >
          <div className="language-field">
            <div className="language-core">
              <strong>12</strong>
              <span>SUPPLIED PAIRS</span>
            </div>
            {languages.map((l, i) => (
              <button
                key={l.iso}
                className={
                  "language-node " + (l.clean === null ? "pending" : "")
                }
                style={{
                  left: `${50 + Math.cos((i / languages.length) * Math.PI * 2) * (i % 2 ? 38 : 29)}%`,
                  top: `${50 + Math.sin((i / languages.length) * Math.PI * 2) * (i % 2 ? 40 : 29)}%`,
                }}
                onClick={() => setSelected(l)}
              >
                <span>{l.iso.toUpperCase()}</span>
                <small>{l.name}</small>
              </button>
            ))}
          </div>
        </Panel>
        <Panel title="Coverage, with context" eyebrow="SCIENTIFIC INTEGRITY">
          <div className="padded">
            <div className="big-number">
              23<span>languages in scope</span>
            </div>
            <DetailList
              items={[
                ["Supplied metric pairs", "12"],
                ["Named pending languages", "9"],
                ["Unspecified in source", "2"],
                ["Independent validation", "Not supplied"],
              ]}
            />
            <div className="notice">
              These are supplied benchmark examples, not live model
              measurements. Dataset provenance, run dates, and confidence
              intervals were not provided.
            </div>
          </div>
        </Panel>
      </div>
      <Panel
        title="Language scorecard"
        action={
          <div className="actions">
            <input
              aria-label="Search languages"
              placeholder="Find a language"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <select
              aria-label="Language validation status"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option>All</option>
              <option>Supplied</option>
              <option>Pending</option>
            </select>
          </div>
        }
      >
        <DataTable
          headers={[
            "LANGUAGE",
            "NATIVE SCRIPT",
            "ISO",
            "CLEAN EER",
            "G.711 EER",
            "DELTA (PP)",
            "DATA STATUS",
          ]}
          rows={rows.map((l) => [
            l.name,
            l.native,
            l.iso,
            l.clean === null ? "—" : l.clean.toFixed(2) + "%",
            l.phone === null ? "—" : l.phone.toFixed(2) + "%",
            l.clean === null ? "—" : "+" + (l.phone! - l.clean).toFixed(2),
            <Chip tone={l.status === "Pending" ? "amber" : "cyan"}>
              {l.status.toUpperCase()}
            </Chip>,
          ])}
          onRow={(i) => setSelected(rows[i])}
        />
      </Panel>
      {selected && (
        <Modal
          title={selected.name + " / " + selected.native}
          onClose={() => setSelected(null)}
          drawer
        >
          <Chip tone="cyan">SOURCE-SUPPLIED METRICS</Chip>
          <DetailList
            items={[
              [
                "Clean EER",
                selected.clean === null
                  ? "Pending"
                  : selected.clean.toFixed(2) + "%",
              ],
              [
                "G.711 EER",
                selected.phone === null
                  ? "Pending"
                  : selected.phone.toFixed(2) + "%",
              ],
              ["Dataset / samples", "Not supplied"],
              ["Model version / training date", "Not supplied"],
              ["Validation status", selected.status],
              [
                "Known weakness",
                selected.phone !== null && selected.phone > 5
                  ? "Material telephony error rate; use cautious review."
                  : "No per-language weakness analysis supplied.",
              ],
            ]}
          />
          <div className="notice">
            Lower EER is better. A low test-set EER does not guarantee
            performance on every caller or unseen generator.
          </div>
        </Modal>
      )}
    </>
  );
}
export function Evidence() {
  const [selected, setSelected] = useState<DetectorScore | null>(null);
  return (
    <>
      <PageHeader
        eyebrow="INTELLIGENCE / EVIDENCE BRAINS"
        title="Nine perspectives. One decision."
        description="Inspect the specialized systems behind every calibrated verdict."
      >
        <Chip tone="cyan">9 / 9 AVAILABLE · DEMO</Chip>
      </PageHeader>
      <Panel
        title="The evidence constellation"
        eyebrow="DETERMINISTIC SAMPLE CONTRIBUTIONS"
      >
        <EvidenceGraph items={detectors} onSelect={setSelected} />
      </Panel>
      <div className="module-grid">
        {detectors.map((d, i) => (
          <button
            className="module-card"
            key={d.name}
            onClick={() => setSelected(d)}
          >
            <div className="between">
              <span className="eyebrow">MODULE 0{i + 1}</span>
              <ArrowUpRight size={16} />
            </div>
            <h2>{d.name}</h2>
            <Sparkline seed={i * 3} tone={i === 8 ? "violet" : "cyan"} />
            <p>{d.detail}</p>
            <Bar value={d.score} label="Synthetic likelihood" />
            <div className="between small">
              <span>{d.version}</span>
              <Chip tone="green">HEALTHY · DEMO</Chip>
            </div>
          </button>
        ))}
      </div>
      {selected && (
        <DetectorInspector
          detector={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
export function Registries() {
  const [query, setQuery] = useState("");
  const [attack, setAttack] = useState("Voice cloning");
  const [selected, setSelected] = useState<(typeof generators)[number] | null>(
    null,
  );
  const rows = generators.filter((g) =>
    (g.name + " " + g.family).toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        eyebrow="INTELLIGENCE / REGISTRIES"
        title="Know the shape of the threat"
        description="A sample security registry for synthesis systems, attacks, and transformation recipes."
      >
        <ExportButton rows={generators} />
      </PageHeader>
      <div className="metric-grid">
        {[
          ["28", "GENERATORS"],
          ["26", "ATTACK MODES"],
          ["17", "RECIPE DIMENSIONS"],
          ["23", "LANGUAGES IN SCOPE"],
        ].map(([v, k]) => (
          <div className="metric-card" key={k}>
            <span className="eyebrow">{k}</span>
            <strong className="metric-value">{v}</strong>
            <small>Supplied scope · sample records</small>
          </div>
        ))}
      </div>
      <Panel
        title="Generator registry"
        action={
          <input
            aria-label="Search generators"
            placeholder="Search generator or family"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        }
      >
        <DataTable
          headers={[
            "GENERATOR",
            "FAMILY",
            "EXPOSURE",
            "RISK",
            "SAMPLES",
            "EER",
          ]}
          rows={rows.map((g) => [
            g.name,
            g.family,
            <Chip tone={g.seen ? "neutral" : "cyan"}>
              {g.seen ? "SEEN" : "UNSEEN"}
            </Chip>,
            g.risk,
            g.samples.toLocaleString(),
            "Not supplied",
          ])}
          onRow={(i) => setSelected(rows[i])}
        />
      </Panel>
      <div className="grid-two">
        <Panel title="Attack mode explorer" eyebrow="SELECT A TRANSFORMATION">
          <div className="attack-chips">
            {attackModes.map((a) => (
              <button
                key={a}
                className={attack === a ? "selected" : ""}
                onClick={() => setAttack(a)}
              >
                {a}
              </button>
            ))}
          </div>
        </Panel>
        <Panel title={attack + " recipe"} eyebrow="17-DIMENSION SAMPLE RECIPE">
          <div className="recipe-chart">
            {recipes.map((r, i) => (
              <div key={r}>
                <span>{r}</span>
                <Bar value={20 + ((i * 17 + attack.length * 7) % 78)} />
                <span className="mono">
                  {((20 + ((i * 17 + attack.length * 7) % 78)) / 100).toFixed(
                    2,
                  )}
                </span>
              </div>
            ))}
          </div>
        </Panel>
      </div>
      {selected && (
        <Modal title={selected.name} onClose={() => setSelected(null)} drawer>
          <DetailList
            items={[
              ["Registry ID", selected.id],
              ["Family", selected.family],
              ["Architecture", "Sample family classification"],
              ["Exposure", selected.seen ? "Seen" : "Unseen"],
              ["Samples", selected.samples + " · simulated"],
              ["First detected", "2026-09-28 · simulated"],
              ["Last observed", "2026-10-04 · simulated"],
              ["Evaluation EER", "Not supplied"],
            ]}
          />
        </Modal>
      )}
    </>
  );
}
export function Results() {
  const [coverage, setCoverage] = useState(85);
  return (
    <>
      <PageHeader
        eyebrow="INTELLIGENCE / RESULTS"
        title="Measure the uncertainty"
        description="Supplied research values, transparent limitations, and the cost of coverage."
      >
        <ExportButton
          rows={[
            {
              seen: 1.62,
              unseen: 15.94,
              gap: 9.43,
              ECE: 0.058,
              Cllr: 1.01,
              AURC: 0.0273,
            },
          ]}
        />
      </PageHeader>
      <Panel
        title="Generalization trajectory"
        eyebrow="SOURCE VALUES · EVALUATION PROTOCOL NOT SUPPLIED"
      >
        <div className="trajectory">
          {[
            ["1.62", "Seen EER"],
            ["19.00", "Reference stage 2"],
            ["27.19", "Reference stage 3"],
            ["15.94", "Unseen EER"],
          ].map(([n, l], i) => (
            <div key={n}>
              <span className="eyebrow">
                0{i + 1} / {l}
              </span>
              <strong>
                {n}
                <small>%</small>
              </strong>
              {i < 3 && <span className="trajectory-arrow">→</span>}
            </div>
          ))}
        </div>
        <div className="notice">
          The intermediate values are retained in source order. Stage
          definitions, zero-shot protocol, and confidence intervals were not
          supplied. +9.43 is a separately supplied gap metric; it is not the
          arithmetic difference between 1.62 and 15.94.
        </div>
      </Panel>
      <div className="grid-two">
        <Panel
          title="The value of abstention"
          eyebrow="INTERACTIVE POLICY ILLUSTRATION"
        >
          <div className="padded">
            <div className="between">
              <span>Target coverage</span>
              <strong className="mono">{coverage}%</strong>
            </div>
            <input
              type="range"
              aria-label="Target coverage"
              min="50"
              max="100"
              value={coverage}
              onChange={(e) => setCoverage(+e.target.value)}
            />
            <p className="small">
              Illustrative policy: {100 - coverage}% of calls routed to review.
              This control does not recalculate validated risk.
            </p>
            <LineChart
              values={[0.3, 0.4, 0.7, 1, 1.4, 2, 3, 4.8, 8, 14]}
              label="Illustrative risk"
              max={15}
            />
          </div>
        </Panel>
        <Panel title="False-positive progression" eyebrow="SUPPLIED REFERENCE">
          <div className="padded">
            {[
              ["Baseline", 2.55],
              ["Intermediate", 0.9],
              ["With abstention", 0.23],
            ].map(([l, n]) => (
              <div className="false-positive" key={l}>
                <span>{l}</span>
                <strong>{Number(n).toFixed(2)}%</strong>
                <Bar value={(Number(n) / 2.55) * 100} tone="green" />
              </div>
            ))}
            <div className="notice">
              Supplied reduction: −91%. Review volume and policy thresholds were
              not provided.
            </div>
          </div>
        </Panel>
      </div>
      <div className="metric-grid">
        {[
          [".058", "ECE"],
          ["1.01", "Cllr"],
          [".0273", "AURC"],
          ["+2.17 pp", "CHANNEL DEGRADATION"],
        ].map(([v, l]) => (
          <div className="metric-card" key={l}>
            <span className="eyebrow">{l}</span>
            <strong className="metric-value compact">{v}</strong>
            <small>Source-supplied reference</small>
          </div>
        ))}
      </div>
    </>
  );
}
export function Threats() {
  const [selected, setSelected] = useState(intelNodes[0]);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [drag, setDrag] = useState<{ x: number; y: number } | null>(null);
  const [query, setQuery] = useState("");
  const nodes = intelNodes.filter((n) =>
    (n.label + " " + n.kind).toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        eyebrow="INTELLIGENCE / THREAT INTEL"
        title="Connect the weak signals"
        description="Explore the relationships between an unknown generator, a call, and an emerging pattern."
      >
        <Chip tone="cyan">SIMULATED INTELLIGENCE</Chip>
      </PageHeader>
      <div className="grid-main">
        <Panel
          title="Intelligence graph"
          eyebrow="GEN-UNK-04 / RELATED EVIDENCE"
          action={
            <div className="actions">
              <button
                aria-label="Zoom graph out"
                onClick={() => setZoom(Math.max(0.6, zoom - 0.15))}
              >
                −
              </button>
              <span className="mono">{Math.round(zoom * 100)}%</span>
              <button
                aria-label="Zoom graph in"
                onClick={() => setZoom(Math.min(2, zoom + 0.15))}
              >
                +
              </button>
              <button
                onClick={() => {
                  setPan({ x: 0, y: 0 });
                  setZoom(1);
                }}
              >
                Reset
              </button>
            </div>
          }
        >
          <div className="graph-search">
            <Search size={15} />
            <input
              aria-label="Search graph nodes"
              placeholder="Search entities, languages, codecs…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <svg
            className="intel-graph"
            viewBox="0 0 700 430"
            onPointerDown={(e) => {
              if ((e.target as Element).closest("[data-node]")) return;
              setDrag({ x: e.clientX - pan.x, y: e.clientY - pan.y });
              e.currentTarget.setPointerCapture(e.pointerId);
            }}
            onPointerMove={(e) => {
              if (drag)
                setPan({ x: e.clientX - drag.x, y: e.clientY - drag.y });
            }}
            onPointerUp={() => setDrag(null)}
            aria-label="Threat relationship graph. Accessible entity controls below."
          >
            <defs>
              <pattern
                id="grid"
                width="25"
                height="25"
                patternUnits="userSpaceOnUse"
              >
                <circle cx="1" cy="1" r=".7" fill="#334159" />
              </pattern>
            </defs>
            <rect width="700" height="430" fill="url(#grid)" />
            <g
              transform={`translate(${350 + pan.x},${215 + pan.y}) scale(${zoom}) translate(-350,-215)`}
            >
              {nodes.slice(1).map((n) => (
                <line
                  key={n.id}
                  x1="350"
                  y1="200"
                  x2={n.x}
                  y2={n.y}
                  stroke={
                    selected.id === n.id || selected.id === "g"
                      ? "#22d3ee"
                      : "#25344b"
                  }
                  opacity=".6"
                />
              ))}
              {nodes.map((n) => (
                <g
                  key={n.id}
                  data-node={n.id}
                  onClick={() => setSelected(n)}
                  style={{ cursor: "pointer" }}
                >
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={n.id === "g" ? 42 : 25}
                    fill="#0e1826"
                    stroke={selected.id === n.id ? "#22d3ee" : "#33425d"}
                    strokeWidth={selected.id === n.id ? 2 : 1}
                  />
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r="6"
                    fill={n.id === "g" ? "#ff4d6a" : "#22d3ee"}
                  />
                  <text
                    x={n.x}
                    y={n.y + (n.id === "g" ? 60 : 42)}
                    textAnchor="middle"
                    fill="#d6dfed"
                    fontSize="12"
                  >
                    {n.label}
                  </text>
                  <text
                    x={n.x}
                    y={n.y + (n.id === "g" ? 75 : 57)}
                    textAnchor="middle"
                    fill="#8194af"
                    fontSize="9"
                  >
                    {n.kind.toUpperCase()}
                  </text>
                </g>
              ))}
            </g>
          </svg>
          <div className="entity-list">
            {nodes.map((n) => (
              <button
                key={n.id}
                className={selected.id === n.id ? "selected" : ""}
                onClick={() => setSelected(n)}
              >
                {n.label}
              </button>
            ))}
          </div>
          {nodes.length === 0 && (
            <p className="padded">
              No matching entities. Try Hindi, codec, or generator.
            </p>
          )}
        </Panel>
        <Panel title={selected.label} eyebrow={selected.kind.toUpperCase()}>
          <div className="padded">
            <Chip tone="cyan">
              {selected.kind === "Generator"
                ? "UNSEEN GENERATOR · DEMO"
                : "SAMPLE RELATIONSHIP"}
            </Chip>
            <h3>A candidate, not an attribution.</h3>
            <p>
              The selected entity is linked to the sample Hindi investment call.
              Connections describe co-occurrence, not proof of origin.
            </p>
            <DetailList
              items={[
                ["Entity", selected.id],
                ["Cluster similarity", "0.83 · demo"],
                ["Novelty score", "0.78 · demo"],
                ["Connected samples", "12 · demo"],
                ["Source", "Deterministic fixture"],
              ]}
            />
            <button
              className="wide"
              onClick={() => {
                setPan({
                  x: (350 - selected.x) * zoom,
                  y: (215 - selected.y) * zoom,
                });
              }}
            >
              Focus entity
            </button>
          </div>
        </Panel>
      </div>
      <div className="grid-two">
        <Panel title="Threat feed" eyebrow="RECENT SAMPLE OBSERVATIONS">
          <DataTable
            headers={["THREAT", "LANGUAGE / CHANNEL", "RISK"]}
            rows={["THR-017", "THR-016", "THR-015"].map((t, i) => [
              t,
              ["Hindi / G.711", "Bengali / PCM", "Tamil / G.711"][i],
              <Chip tone={i === 0 ? "red" : "amber"}>
                {i === 0 ? "ELEVATED" : "REVIEW"}
              </Chip>,
            ])}
            onRow={(i) => setSelected(intelNodes[i])}
          />
        </Panel>
        <Panel title="Generator hunter" eyebrow="UNKNOWN SAMPLE CLUSTER">
          <div className="padded">
            <Bar label="Candidate family: neural codec" value={83} />
            <Bar label="Novelty score" value={78} tone="violet" />
            <p className="small">
              12 simulated samples · open-set candidate · human attribution
              required.
            </p>
          </div>
        </Panel>
      </div>
    </>
  );
}
export function Speakers() {
  const [tab, setTab] = useState("Enroll");
  const [name, setName] = useState("");
  const [files, setFiles] = useState<(File | null)[]>([null, null]);
  const [speaker, setSpeaker] = useState<Speaker | null>(null);
  const [done, setDone] = useState(false);
  const [scenario, setScenario] = useState("SAME");
  const { log, notify } = useApp();
  return (
    <>
      <PageHeader
        eyebrow="INTELLIGENCE / SPEAKER IDENTITY"
        title="A voice is more than a name"
        description="Explore enrollment, pairwise verification, and speaker-separated timelines."
      >
        <Chip tone="cyan">DEMO WORKFLOWS</Chip>
      </PageHeader>
      <Tabs
        items={["Enroll", "Verify", "Diarize"]}
        value={tab}
        onChange={(s) => {
          setTab(s);
          setDone(false);
        }}
      />
      <div className="grid-main">
        <Panel
          title={
            tab === "Enroll"
              ? "Create a sample voiceprint"
              : tab === "Verify"
                ? "Compare two voices"
                : "Separate the conversation"
          }
          eyebrow="AUDIO REMAINS IN BROWSER MEMORY"
        >
          <div className="padded">
            {tab === "Enroll" && (
              <label className="field">
                Speaker display name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Sample speaker"
                />
              </label>
            )}
            {tab !== "Diarize" &&
              Array.from({ length: tab === "Verify" ? 2 : 1 }, (_, i) => (
                <label className="file-field" key={i}>
                  {tab === "Verify"
                    ? `Audio ${i === 0 ? "A" : "B"}`
                    : "Enrollment audio"}
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) =>
                      setFiles((f) =>
                        f.map((x, j) =>
                          j === i ? e.target.files?.[0] || null : x,
                        ),
                      )
                    }
                  />
                  <small>
                    {files[i]?.name ||
                      "Choose audio or use the deterministic sample below."}
                  </small>
                </label>
              ))}
            {tab === "Verify" && (
              <label className="field">
                Demo pair
                <select
                  value={scenario}
                  onChange={(e) => {
                    setScenario(e.target.value);
                    setDone(false);
                  }}
                >
                  <option>SAME</option>
                  <option>DIFFERENT</option>
                </select>
              </label>
            )}
            <Waveform />
            <button
              className="primary wide"
              onClick={() => {
                setDone(true);
                if (tab === "Enroll") {
                  setSpeaker({
                    id: "SPK-A941",
                    name: name || "Sample speaker",
                    quality: 92,
                  });
                  log("speaker.enrolled", "SPK-A941", "DEMO");
                }
                notify(tab + " simulation complete");
              }}
            >
              {tab === "Enroll"
                ? "Extract demo voiceprint"
                : tab === "Verify"
                  ? "Compare demo embeddings"
                  : "Run demo diarization"}
            </button>
            {done && tab === "Diarize" && (
              <div className="diarization">
                {["Speaker A", "Speaker B", "Unknown"].map((s, i) => (
                  <div key={s}>
                    <span>{s}</span>
                    <div>
                      {Array.from({ length: 6 }, (_, j) => (
                        <button
                          key={j}
                          style={{ opacity: (j + i) % 3 === 0 ? 1 : 0.2 }}
                          onClick={() =>
                            notify(
                              `${s} · ${j * 3}–${j * 3 + 3}s · Sample utterance`,
                            )
                          }
                        >
                          {j * 3}s
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
                <p>
                  Speaker A: introduction · Speaker B: reply · Unknown:
                  overlapping speech.
                </p>
              </div>
            )}
          </div>
        </Panel>
        <Panel title="Identity evidence" eyebrow="RESULT INSPECTOR">
          <div className="padded">
            {done ? (
              <>
                <Chip
                  tone={
                    tab === "Verify" && scenario === "DIFFERENT"
                      ? "amber"
                      : "cyan"
                  }
                >
                  {tab === "Enroll"
                    ? "ENROLLED"
                    : tab === "Verify"
                      ? scenario
                      : "3 SPEAKER LANES"}{" "}
                  · DEMO
                </Chip>
                <div className="voiceprint">
                  {Array.from({ length: 45 }, (_, i) => (
                    <i
                      key={i}
                      style={{
                        height: `${20 + Math.abs(Math.sin(i * 1.3)) * 75}%`,
                      }}
                    />
                  ))}
                </div>
                <DetailList
                  items={[
                    ["Speaker", speaker?.name || "Sample pair"],
                    ["ID", speaker?.id || "SPK-A941 / SPK-B812"],
                    [
                      tab === "Verify"
                        ? "Embedding similarity"
                        : "Extraction quality",
                      tab === "Verify"
                        ? scenario === "SAME"
                          ? "0.94"
                          : "0.31"
                        : "92%",
                    ],
                    ["Source", "Deterministic simulation"],
                  ]}
                />
              </>
            ) : (
              <div className="empty">
                <h3>No identity decision yet</h3>
                <p>
                  Run a sample workflow to inspect the voiceprint and result.
                </p>
              </div>
            )}
            <div className="notice">
              This prototype does not extract biometric identity from uploaded
              audio. Demo enrollment is session-only. Voice similarity is not
              proof of identity.
            </div>
          </div>
        </Panel>
      </div>
    </>
  );
}
