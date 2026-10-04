import { useEffect, useState } from "react";
import {
  ArrowRight,
  RefreshCw,
  LockKeyhole,
  Copy,
  Cpu,
  Network,
  Shield,
  Phone,
  Radio,
  Fingerprint,
  Layers,
  Check,
} from "lucide-react";
import {
  PageHeader,
  Panel,
  Chip,
  DataTable,
  Modal,
  DetailList,
  Tabs,
  Bar,
  ExportButton,
  CopyButton,
} from "../components/ui";
import { LineChart, Sparkline, Spectrogram, Waveform } from "../components/charts";
import { datasets, rounds, languages } from "../data/catalog";
import { useApp, usePreference } from "../store";
import { config, endpoints, download } from "../services/api";
import type {
  AuditEvent,
  Dataset,
  DeploymentProfile,
  TrainingRound,
} from "../types";
const products = [
  {
    name: "CallGuard",
    icon: Phone,
    desc: "Voice risk at the point of contact.",
    metric: "91.4%",
    label: "SYNTHETIC LIKELIHOOD",
  },
  {
    name: "Voice Identity",
    icon: Fingerprint,
    desc: "Speaker verification with context.",
    metric: "0.94",
    label: "EMBEDDING SIMILARITY",
  },
  {
    name: "Transaction Shield",
    icon: Shield,
    desc: "Fuse voice and transaction signals.",
    metric: "REVIEW",
    label: "SAMPLE POLICY DECISION",
  },
  {
    name: "Telephony Gateway",
    icon: Network,
    desc: "Route uncertainty to the right team.",
    metric: "BLOCK",
    label: "SIMULATED ROUTING",
  },
  {
    name: "War Room",
    icon: Radio,
    desc: "A shared, read-only intelligence view.",
    metric: "12",
    label: "SAMPLE THREAT CLUSTERS",
  },
  {
    name: "Consumer",
    icon: Layers,
    desc: "One voice check. A clearer next step.",
    metric: "CHECK",
    label: "SIMPLE VOICE REVIEW",
  },
];
export function Products() {
  const [selected, setSelected] = useState<string | null>(null);
  const [risk, setRisk] = useState(72);
  const [checked, setChecked] = useState(false);
  const [file, setFile] = useState("");
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / PRODUCT SURFACES"
        title="One intelligence. Six front lines."
        description="Purpose-built experiences on a shared evidence and policy foundation."
      >
        <Chip tone="cyan">INTERACTIVE DEMOS</Chip>
      </PageHeader>
      <div className="product-grid">
        {products.map((p, i) => (
          <button
            className="product-card"
            key={p.name}
            onClick={() => {
              setSelected(p.name);
              setChecked(false);
            }}
          >
            <div className="between">
              <p.icon size={23} />
              <span className="eyebrow">SURFACE 0{i + 1} ↗</span>
            </div>
            <h2>{p.name}</h2>
            <p>{p.desc}</p>
            <div className="product-simulation">
              <span className="eyebrow">{p.label}</span>
              <strong>{p.metric}</strong>
              <Sparkline seed={i} tone={i === 0 ? "red" : "cyan"} />
              <div className="mini-flow">
                <span>Signal</span>
                <ArrowRight size={12} />
                <span>Evidence</span>
                <ArrowRight size={12} />
                <span>Action</span>
              </div>
            </div>
            <span className="text-link">
              Open simulation <ArrowRight size={14} />
            </span>
          </button>
        ))}
      </div>
      {selected && (
        <Modal title={selected} onClose={() => setSelected(null)}>
          <Chip tone="cyan">LOCAL DEMO · NO EXTERNAL ACTION</Chip>
          {selected === "War Room" ? (
            <>
              <h3>Shared situational awareness</h3>
              <DataTable
                headers={["CLUSTER", "CALLS", "STATUS"]}
                rows={["Neural codec", "Replay", "Unattributed"].map((s, i) => [
                  s,
                  12 - i * 3,
                  <Chip tone="amber">REVIEW</Chip>,
                ])}
              />
              <div className="notice">
                Read-only War Room. No incident or policy mutations are
                available.
              </div>
            </>
          ) : (
            <>
              <p>
                {selected === "Consumer"
                  ? "Check a suspicious voice message. No stock tips, predictions, or broker recommendations."
                  : "Adjust the sample risk input to explore the decision surface."}
              </p>
              {selected === "Consumer" && (
                <label className="file-field">
                  Voice message
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) => {
                      setFile(e.target.files?.[0]?.name || "");
                      setChecked(false);
                    }}
                  />
                  <small>{file || "Or run the included sample."}</small>
                </label>
              )}
              <Waveform suspicious={risk >= 80} />
              <Spectrogram
                suspicious={risk >= 80}
                caption={
                  selected === "Consumer"
                    ? "Voice-message mel spectrogram · log frequency"
                    : "Input mel spectrogram · log frequency, 0–4 kHz"
                }
              />
              <label className="field">
                Simulated{" "}
                {selected === "Voice Identity" ? "similarity" : "risk"} · {risk}
                %
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={risk}
                  onChange={(e) => {
                    setRisk(+e.target.value);
                    setChecked(false);
                  }}
                />
              </label>
              <button className="primary wide" onClick={() => setChecked(true)}>
                {selected === "Consumer"
                  ? "Check demo voice"
                  : "Run simulation"}
              </button>
              {checked && (
                <div className="padded" aria-live="polite">
                  <Chip
                    tone={risk >= 80 ? "red" : risk >= 40 ? "amber" : "green"}
                  >
                    {selected === "Voice Identity"
                      ? risk >= 80
                        ? "SAME"
                        : "DIFFERENT"
                      : risk >= 80
                        ? "BLOCK"
                        : risk >= 40
                          ? "REVIEW"
                          : "ALLOW"}{" "}
                    · DEMO
                  </Chip>
                  <p>
                    {risk >= 40
                      ? "Independent verification recommended. Do not rely on voice alone."
                      : "Continue standard verification. This does not establish legitimacy."}
                  </p>
                </div>
              )}
              <small>
                Simulated policy outcome. No real call or transaction is
                blocked.
              </small>
            </>
          )}
        </Modal>
      )}
    </>
  );
}
export function Integrations() {
  const [syncing, setSyncing] = useState(false);
  const [synced, setSynced] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const { notify, log } = useApp();
  const sync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      setSynced(true);
      notify("Demo catalog sync completed");
      log("integration.sync", "AIKosh", "SIMULATED");
    }, 1200);
  };
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / INTEGRATIONS"
        title="Connected by design"
        description="Language services and dataset catalogs, with visible provenance and licensing."
      >
        <Chip tone="amber">NOT CONNECTED TO PROVIDERS</Chip>
      </PageHeader>
      <Panel
        title="Integration architecture"
        eyebrow="PROPOSED CONTRACT BOUNDARIES"
      >
        <div className="architecture-flow">
          {[
            "Audio intake",
            "VoxShield API",
            "Bhashini language services",
            "Evidence & arbitration",
            "Product surfaces",
          ].map((s, i) => (
            <button key={s} onClick={() => setSelected(s)}>
              <span className="eyebrow">0{i + 1}</span>
              <Network size={20} />
              <strong>{s}</strong>
              {i < 4 && <ArrowRight className="flow-arrow" size={15} />}
            </button>
          ))}
        </div>
      </Panel>
      <div className="grid-two">
        <Panel title="Bhashini" eyebrow="LANGUAGE SERVICE ADAPTER">
          <DataTable
            headers={["SERVICE", "STATE", "DEMO LATENCY", "QUOTA"]}
            rows={["ASR", "TTS", "ALD", "TLD", "NMT", "Streaming"].map(
              (s, i) => [
                s,
                <Chip tone="cyan">SIMULATED</Chip>,
                120 + i * 17 + "ms",
                "Not configured",
              ],
            )}
            onRow={(i) =>
              setSelected(
                "Bhashini / " +
                  ["ASR", "TTS", "ALD", "TLD", "NMT", "Streaming"][i],
              )
            }
          />
          <div className="notice">
            Attribution: Bhashini. Provider authentication, quotas, and licenses
            must be verified during integration.
          </div>
        </Panel>
        <Panel title="AIKosh" eyebrow="SOURCE-SUPPLIED CATALOG COUNTS">
          <div className="padded">
            <div className="catalog-metrics">
              <div>
                <strong>124</strong>
                <span>DATASETS</span>
              </div>
              <div>
                <strong>94</strong>
                <span>MODELS</span>
              </div>
            </div>
            <DetailList
              items={[
                [
                  "Catalog status",
                  synced ? "Demo sync completed" : "Sample snapshot",
                ],
                [
                  "Last sync",
                  synced ? "This session · simulated" : "Not connected",
                ],
                ["Attribution", "AIKosh · dataset owners retain licenses"],
                ["Usage restrictions", "Per-dataset license review required"],
              ]}
            />
            <button className="wide" disabled={syncing} onClick={sync}>
              <RefreshCw size={14} className={syncing ? "spin" : ""} />
              {syncing ? "Simulating sync…" : "Sync demo catalog"}
            </button>
          </div>
        </Panel>
      </div>
      {selected && (
        <Modal title={selected} onClose={() => setSelected(null)} drawer>
          <DetailList
            items={[
              ["Adapter state", "Not connected"],
              ["Authentication", "Backend-managed provider credential"],
              ["Input", "Audio or normalized language request"],
              ["Output", "Typed service response with provenance"],
              ["Timeout", "8 seconds in proposed client"],
              ["Fallback", "Explicit demo or unavailable state"],
            ]}
          />
          <div className="notice">
            Provider credentials never belong in VITE environment variables.
            Configure secrets on the server.
          </div>
        </Modal>
      )}
    </>
  );
}
export function Corpus() {
  const [filter, setFilter] = useState("All licenses");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Dataset | null>(null);
  const rows = datasets.filter(
    (d) =>
      (filter === "All licenses" || d.license === filter) &&
      d.name.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / DATA & CORPUS"
        title="The foundations of evidence"
        description="A sample corpus inventory with storage, attribution, and licensing controls."
      >
        <ExportButton rows={rows} />
      </PageHeader>
      <div className="metric-grid">
        {[
          [datasets.length, "DATASETS"],
          [datasets.reduce((s, d) => s + d.hours, 0), "AUDIO HOURS"],
          [
            datasets.reduce((s, d) => s + d.samples, 0).toLocaleString(),
            "SAMPLES",
          ],
          ["1", "LICENSE HOLD"],
        ].map(([v, k]) => (
          <div className="metric-card" key={k}>
            <span className="eyebrow">{k}</span>
            <strong className="metric-value">{v}</strong>
            <small>Simulated inventory</small>
          </div>
        ))}
      </div>
      <Panel title="Storage topology" eyebrow="DEMO CAPACITY">
        <div className="storage-grid">
          {[
            ["DGX", 68, "Model-ready working set"],
            ["KIOXIA", 42, "Corpus and checkpoints"],
            ["local", 16, "Temporary processing"],
          ].map(([s, v, n]) => (
            <div key={s}>
              <div className="between">
                <strong>{s}</strong>
                <span>{v}%</span>
              </div>
              <Bar value={Number(v)} />
              <p>{n}</p>
            </div>
          ))}
        </div>
      </Panel>
      <Panel
        title="Dataset inventory"
        action={
          <div className="actions">
            <input
              aria-label="Search datasets"
              placeholder="Search datasets"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <select
              aria-label="Filter licenses"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              {[
                "All licenses",
                "CC-BY",
                "CC-BY-NC",
                "ND",
                "internal",
                "hold",
              ].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>
        }
      >
        <DataTable
          headers={[
            "DATASET",
            "LANGUAGE",
            "SAMPLES",
            "HOURS",
            "CODEC",
            "LICENSE",
            "LOCATION",
            "STATUS",
          ]}
          rows={rows.map((d) => [
            d.name,
            d.language,
            d.samples.toLocaleString(),
            d.hours,
            "PCM / G.711",
            <Chip
              tone={
                d.license === "hold" || d.license === "CC-BY-NC"
                  ? "amber"
                  : "neutral"
              }
            >
              {d.license}
            </Chip>,
            d.storage,
            d.status,
          ])}
          onRow={(i) => setSelected(rows[i])}
        />
      </Panel>
      {selected && (
        <Modal title={selected.name} onClose={() => setSelected(null)} drawer>
          <DetailList
            items={[
              ["Source", "Simulated corpus record"],
              ["Language", selected.language],
              ["License", selected.license],
              [
                "Restrictions",
                selected.license === "CC-BY-NC"
                  ? "Research-only / noncommercial"
                  : selected.license === "ND"
                    ? "No derivatives; review before transformations"
                    : selected.license === "hold"
                      ? "Use blocked pending licensing review"
                      : "Confirm actual terms before ingestion",
              ],
              ["Storage", selected.storage],
              ["Last pull", "2026-10-03 · sample"],
              [
                "Attribution",
                "Dataset owner metadata required before live use",
              ],
            ]}
          />
        </Modal>
      )}
    </>
  );
}
export function Training() {
  const [jobs, setJobs] = useState(rounds);
  const [paused, setPaused] = useState(false);
  const [selected, setSelected] = useState<TrainingRound | null>(null);
  const { log, notify } = useApp();
  useEffect(() => {
    if (paused) return;
    const t = setInterval(
      () =>
        setJobs((js) =>
          js.map((j) =>
            j.status === "RUNNING"
              ? { ...j, progress: Math.min(99, j.progress + 0.15) }
              : j,
          ),
        ),
      1800,
    );
    return () => clearInterval(t);
  }, [paused]);
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / TRAINING OPERATIONS"
        title="Inside the learning system"
        description="A simulated DGX training control plane. No infrastructure commands are sent."
      >
        <button
          onClick={() => {
            setPaused(!paused);
            log(
              paused ? "training.resumed" : "training.paused",
              "R-46",
              "SIMULATED",
            );
          }}
        >
          {paused ? "Resume demo job" : "Pause demo job"}
        </button>
      </PageHeader>
      <div className="gpu-grid">
        {[0, 1, 2, 3].map((g) => (
          <Panel key={g}>
            <div className="gpu-head">
              <Cpu size={18} />
              <span className="eyebrow">DGX / GPU {g}</span>
              <Chip tone="green">DEMO</Chip>
            </div>
            <div className="gpu-number">
              {paused ? 8 : 87 - g * 9}
              <small>%</small>
            </div>
            <Bar value={paused ? 8 : 87 - g * 9} />
            <div className="between small">
              <span>{paused ? 7 : 64 - g * 3} / 80 GB</span>
              <span>{paused ? 42 : 68 - g * 2}°C</span>
            </div>
          </Panel>
        ))}
      </div>
      <div className="grid-main">
        <Panel title="Convergence trace" eyebrow="SIMULATED LOSS & VALIDATION">
          <LineChart
            values={[
              0.94, 0.79, 0.62, 0.48, 0.42, 0.36, 0.29, 0.25, 0.21, 0.19,
            ]}
            max={1}
            unit=""
            label="Validation loss"
            xLabel="Training progress"
          />
        </Panel>
        <Panel
          title="Active round R-46"
          eyebrow={paused ? "PAUSED · DEMO" : "RUNNING · DEMO"}
        >
          <div className="padded">
            <h3>Hindi / Cross-codec adaptation</h3>
            <Bar label="Epoch progress" value={Math.round(jobs[4].progress)} />
            <DetailList
              items={[
                ["Epoch", "26 / 40"],
                ["Best checkpoint", "demo-r46-e24"],
                ["Dataset", "Telephony stress set"],
                ["ETA", paused ? "Paused" : "~18 minutes · illustrative"],
                ["EER", "Not validated in this prototype"],
              ]}
            />
          </div>
        </Panel>
      </div>
      <Panel title="Language training rounds" eyebrow="DEMO JOB QUEUE">
        <DataTable
          headers={[
            "ROUND",
            "LANGUAGE",
            "STATE",
            "EPOCH",
            "PROGRESS",
            "GPU",
            "ACTION",
          ]}
          rows={jobs.map((j) => [
            j.id,
            j.language,
            <Chip
              tone={
                j.status === "DONE"
                  ? "green"
                  : j.status === "FAILED"
                    ? "red"
                    : j.status === "RUNNING"
                      ? "cyan"
                      : "amber"
              }
            >
              {j.status === "RUNNING" && paused ? "PAUSED" : j.status}
            </Chip>,
            j.epoch + "/40",
            Math.floor(j.progress) + "%",
            j.gpu,
            j.status === "FAILED" ? (
              <button
                onClick={() => {
                  setJobs((js) =>
                    js.map((x) =>
                      x.id === j.id ? { ...x, status: "PENDING" } : x,
                    ),
                  );
                  log("training.retry", j.id, "DEMO QUEUED");
                  notify("Demo round requeued");
                }}
              >
                Retry demo
              </button>
            ) : (
              "Inspect ↗"
            ),
          ])}
          onRow={(i) => setSelected(jobs[i])}
        />
      </Panel>
      {selected && (
        <Modal
          title={selected.id + " / " + selected.language}
          onClose={() => setSelected(null)}
          drawer
        >
          <DetailList
            items={[
              ["Status", selected.status],
              ["Epoch", selected.epoch],
              ["Progress", Math.floor(selected.progress) + "%"],
              ["Checkpoint", "demo-checkpoint-" + selected.id],
              ["Dataset", "Simulated language subset"],
              [
                "Failure detail",
                selected.status === "FAILED"
                  ? "Simulated checksum mismatch; retry after corpus check."
                  : "No recorded failure",
              ],
            ]}
          />
        </Modal>
      )}
    </>
  );
}
export function Ops() {
  const { audit } = useApp();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<AuditEvent | null>(null);
  const rows = audit.filter((a) =>
    (a.event + " " + a.call + " " + a.actor)
      .toLowerCase()
      .includes(query.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / OPS & AUDIT"
        title="Accountability is a system property"
        description="Inspect decisions and operational events. This session’s audit is append-only in the UI."
      >
        <ExportButton rows={rows} name="voxshield-audit" />
      </PageHeader>
      <div className="metric-grid">
        {[
          [".058", "ECE · SUPPLIED"],
          ["1.01", "CLLR · SUPPLIED"],
          ["0.014", "DRIFT · SIMULATED"],
          ["148 ms", "LATENCY · SIMULATED"],
        ].map(([v, k]) => (
          <div className="metric-card" key={k}>
            <span className="eyebrow">{k}</span>
            <strong className="metric-value compact">{v}</strong>
          </div>
        ))}
      </div>
      <div className="grid-main">
        <Panel
          title="Distribution drift"
          eyebrow="ILLUSTRATIVE MONITORING TRACE"
        >
          <LineChart
            values={[0.012, 0.014, 0.011, 0.015, 0.012, 0.013, 0.016, 0.014]}
            max={0.03}
            unit=""
            label="Drift"
            xLabel="Observation window"
          />
        </Panel>
        <Panel title="Deployment timeline" eyebrow="SIMULATED EVENTS">
          <div className="event-timeline">
            <div>
              <span>13:42</span>
              <strong>Calibration snapshot loaded</strong>
              <small>vox-fusion-2.4.1-demo</small>
            </div>
            <div>
              <span>12:10</span>
              <strong>Demo detector health verified</strong>
              <small>9 / 9 systems available</small>
            </div>
            <div>
              <span>09:00</span>
              <strong>Console session initialized</strong>
              <small>Privacy guardrails active</small>
            </div>
          </div>
        </Panel>
      </div>
      <Panel
        title="Audit ledger"
        action={
          <input
            aria-label="Search audit"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search events, calls, actors"
          />
        }
      >
        <DataTable
          headers={[
            "EVENT",
            "TIMESTAMP",
            "ACTOR",
            "CALL / ENTITY",
            "ACTION",
            "REFERENCE",
            "ENV",
          ]}
          rows={rows.map((a) => [
            a.event,
            new Date(a.timestamp).toLocaleString(),
            a.actor,
            a.call,
            a.action,
            <span className="mono">{a.hash}</span>,
            a.source.toUpperCase(),
          ])}
          onRow={(i) => setSelected(rows[i])}
        />
        <div className="notice">
          Demo references are identifiers, not cryptographic attestations.
          Durable, tamper-evident storage requires a backend audit service.
        </div>
      </Panel>
      {selected && (
        <Modal title={selected.id} onClose={() => setSelected(null)} drawer>
          <DetailList
            items={Object.entries(selected).map(([k, v]) => [k, String(v)])}
          />
          <CopyButton value={JSON.stringify(selected, null, 2)} />
        </Modal>
      )}
    </>
  );
}
const profiles: DeploymentProfile[] = [
  "Cloud",
  "Enterprise",
  "Indic On-Prem",
  "Edge",
];
export function Deployment() {
  const { notify, log, mode, retry, busy } = useApp();
  const [profile, setProfile] = usePreference<DeploymentProfile>(
    "deployment",
    "Indic On-Prem",
  );
  const [tab, setTab] = useState("Deployment");
  const [region, setRegion] = usePreference("region", "India");
  const [env, setEnv] = usePreference("environment", "DEMO");
  const [threshold, setThreshold] = usePreference("threshold", 80);
  const [reduced, setReduced] = usePreference("reduced-motion", false);
  const [key, setKey] = useState("vs_demo_" + "0".repeat(24));
  const [confirm, setConfirm] = useState<string | null>(null);
  useEffect(() => {
    document.documentElement.classList.toggle("reduce-motion", reduced);
  }, [reduced]);
  const tabs = [
    "Deployment",
    "Detection",
    "Guardrails",
    "Data residency",
    "Integrations",
    "API",
    "Security",
    "Appearance",
    "Developer",
  ];
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / DEPLOYMENT & SETTINGS"
        title="Your intelligence. Your boundary."
        description="Configure prototype preferences and inspect integration boundaries."
      >
        <Chip tone="cyan">LOCAL SETTINGS ONLY</Chip>
      </PageHeader>
      <Tabs items={tabs} value={tab} onChange={setTab} />
      {tab === "Deployment" ? (
        <>
          <div className="profile-grid">
            {profiles.map((p, i) => (
              <button
                key={p}
                className={"profile-card " + (profile === p ? "selected" : "")}
                onClick={() => {
                  setProfile(p);
                  log("deployment.profile_selected", p, "LOCAL DEMO");
                  notify("Prototype profile saved: " + p);
                }}
              >
                <div className="between">
                  <Network size={22} />
                  {profile === p && <Check size={18} />}
                </div>
                <h2>{p}</h2>
                <div className="architecture-mini">
                  {["INPUT", "FUSION", "POLICY"].map((s) => (
                    <span key={s}>{s}</span>
                  ))}
                </div>
                <p>
                  {
                    [
                      "Managed service boundary",
                      "Dedicated tenant and policy",
                      "Private inference within residency boundary",
                      "Compact inference near the signal",
                    ][i]
                  }
                </p>
                <Chip tone={profile === p ? "cyan" : "neutral"}>
                  {profile === p ? "SELECTED" : "AVAILABLE PROFILE"}
                </Chip>
              </button>
            ))}
          </div>
          <Panel title="Operating environment">
            <div className="padded">
              <label className="field">
                Environment preference
                <select
                  value={env}
                  onChange={(e) =>
                    e.target.value === "DEMO"
                      ? setEnv("DEMO")
                      : setConfirm(e.target.value)
                  }
                >
                  {["DEMO", "STAGING", "PRODUCTION"].map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </label>
              <div className="notice">
                Environment selection is a prototype preference. All operational
                data remains explicitly marked demo; this does not deploy or
                switch infrastructure.
              </div>
            </div>
          </Panel>
        </>
      ) : (
        <Panel title={tab}>
          <div className="settings-body">
            {tab === "Detection" ? (
              <>
                <label className="field">
                  Synthetic review threshold · {threshold}%
                  <input
                    type="range"
                    min="50"
                    max="99"
                    value={threshold}
                    onChange={(e) => setThreshold(+e.target.value)}
                  />
                </label>
                <p>
                  Saved policy preference only. Demo scenarios use fixed
                  calibrated outcomes; live enforcement belongs to the server.
                </p>
                <DetailList
                  items={[
                    ["Abstain policy", "Always available"],
                    ["Uncertainty handling", "Human review"],
                    ["Minimum audio quality", "Backend calibration required"],
                  ]}
                />
              </>
            ) : tab === "Guardrails" ? (
              <>
                {[
                  "No stock tips",
                  "No price prediction",
                  "No broker promotion",
                  "Privacy-by-design",
                  "Explicit ABSTAIN outcome",
                  "Read-only War Room",
                  "Third-party attribution",
                  "Research-only licensing where required",
                ].map((s) => (
                  <div className="guardrail" key={s}>
                    <LockKeyhole size={16} />
                    <span>{s}</span>
                    <Chip tone="neutral">LOCKED</Chip>
                  </div>
                ))}
              </>
            ) : tab === "Data residency" ? (
              <>
                <label className="field">
                  Preferred region
                  <select
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                  >
                    {["India", "EU", "US", "Customer-managed"].map((r) => (
                      <option key={r}>{r}</option>
                    ))}
                  </select>
                </label>
                <div className="notice">
                  Preference does not enforce residency. Backend routing, logs,
                  storage, and subprocessors must respect the selected policy
                  before production use.
                </div>
              </>
            ) : tab === "API" ? (
              <>
                <label className="field">
                  Prototype API key
                  <input readOnly value={"vs_demo_••••••••••••••••••••••••"} />
                </label>
                <div className="actions">
                  <CopyButton value={key} />
                  <button onClick={() => setConfirm("regenerate")}>
                    Regenerate mock key
                  </button>
                </div>
                <p>Mock key only. Never authorizes a real request.</p>
                <code className="code-block">{config.api}</code>
                <button disabled={busy} onClick={() => void retry()}>
                  <RefreshCw size={14} />
                  {busy ? "Checking…" : "Check API connection"}
                </button>
              </>
            ) : tab === "Appearance" ? (
              <>
                <label className="toggle-row">
                  <span>Reduce motion</span>
                  <input
                    type="checkbox"
                    checked={reduced}
                    onChange={(e) => setReduced(e.target.checked)}
                  />
                </label>
                <p>System reduced-motion preferences are also respected.</p>
              </>
            ) : tab === "Developer" ? (
              <>
                <DetailList
                  items={[
                    ["API base", config.api],
                    ["WebSocket base", config.ws],
                    ["Mode", mode],
                    ["WebSocket", "Disconnected · simulation is local"],
                    ["Build", "0.1.0"],
                    ["3D", config.three ? "Enabled with fallback" : "Disabled"],
                  ]}
                />
                <pre className="code-block">
                  {JSON.stringify(endpoints, null, 2)}
                </pre>
                <button
                  onClick={() =>
                    download(
                      "voxshield-settings.json",
                      JSON.stringify(
                        { profile, region, env, threshold, reduced },
                        null,
                        2,
                      ),
                      "application/json",
                    )
                  }
                >
                  Export local configuration
                </button>
              </>
            ) : tab === "Security" ? (
              <>
                <DetailList
                  items={[
                    ["Audio retention", "Memory only · no localStorage"],
                    ["Credentials", "Server-managed in live deployment"],
                    ["Session authentication", "Not implemented in prototype"],
                    ["Audit durability", "Session only"],
                    ["Transport", "Configure TLS before live deployment"],
                  ]}
                />
                <div className="notice">
                  No regulatory certification or production security assurance
                  is claimed.
                </div>
              </>
            ) : (
              <>
                <DetailList
                  items={[
                    ["Bhashini", "Not configured"],
                    ["AIKosh", "Not configured"],
                    [
                      "Provider credentials",
                      "Configure only in backend secret storage",
                    ],
                  ]}
                />
                <a className="button" href="#/integrations">
                  Open integration architecture <ArrowRight size={14} />
                </a>
              </>
            )}
          </div>
        </Panel>
      )}
      {confirm && (
        <Modal
          title={
            confirm === "regenerate"
              ? "Regenerate mock key?"
              : "Select " + confirm + " preference?"
          }
          onClose={() => setConfirm(null)}
        >
          <p>
            {confirm === "regenerate"
              ? "This replaces the session-only demo token. It does not revoke any real credential."
              : "No infrastructure will change. The console continues to show demo data until a real backend is configured."}
          </p>
          <div className="actions">
            <button onClick={() => setConfirm(null)}>Cancel</button>
            <button
              className="primary"
              onClick={() => {
                if (confirm === "regenerate") {
                  setKey("vs_demo_" + crypto.randomUUID().replaceAll("-", ""));
                  notify("Mock key regenerated");
                } else {
                  setEnv(confirm);
                  notify(
                    "Environment preference saved · operational data unchanged",
                  );
                }
                log("settings.updated", confirm, "LOCAL DEMO");
                setConfirm(null);
              }}
            >
              Confirm
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
const roadmap = [
  [
    "P0",
    "XLS-R + SLS",
    "Evaluation",
    "High",
    "Medium",
    "Corpus licensing",
    "Next research round",
  ],
  [
    "P1",
    "RawBoost augmentation",
    "Planned",
    "High",
    "Medium",
    "P0 baseline",
    "After baseline",
  ],
  [
    "P2",
    "AASIST3 comparison",
    "Planned",
    "High",
    "High",
    "Evaluation harness",
    "Protocol review",
  ],
  [
    "P3",
    "Adversarial robustness",
    "Research",
    "High",
    "High",
    "P1 + P2",
    "Research gate",
  ],
  [
    "P4",
    "Edge distillation",
    "Planned",
    "Medium",
    "High",
    "P3 stability",
    "Deployment gate",
  ],
];
export function Roadmap() {
  const [selected, setSelected] = useState<string[] | null>(null);
  const [filter, setFilter] = useState("All priorities");
  return (
    <>
      <PageHeader
        eyebrow="PLATFORM / ENGINEERING ROADMAP"
        title="Progress, with dependencies"
        description="A proposed research and engineering sequence. Targets are gates, not delivery promises."
      >
        <select
          aria-label="Roadmap priority"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          {["All priorities", "P0", "P1", "P2", "P3", "P4"].map((p) => (
            <option key={p}>{p}</option>
          ))}
        </select>
      </PageHeader>
      <div className="roadmap">
        {roadmap
          .filter((r) => filter === "All priorities" || r[0] === filter)
          .map((r, i) => (
            <button
              className="roadmap-row"
              key={r[0]}
              onClick={() => setSelected(r)}
            >
              <div className="priority">
                {r[0]}
                <span className="dependency-line" />
              </div>
              <div>
                <span className="eyebrow">RESEARCH TRACK / 0{i + 1}</span>
                <h2>{r[1]}</h2>
                <p>Depends on {r[5]}</p>
              </div>
              <Chip
                tone={
                  r[2] === "Evaluation"
                    ? "cyan"
                    : r[2] === "Research"
                      ? "violet"
                      : "neutral"
                }
              >
                {r[2].toUpperCase()}
              </Chip>
              <div className="roadmap-meta">
                <span>
                  IMPACT <strong>{r[3]}</strong>
                </span>
                <span>
                  COMPLEXITY <strong>{r[4]}</strong>
                </span>
              </div>
              <ArrowRight size={18} />
            </button>
          ))}
      </div>
      <Panel title="Acceptance before advancement" eyebrow="ENGINEERING GATES">
        <div className="storage-grid">
          {[
            [
              "01",
              "Reproducible evaluation",
              "Freeze datasets, partitions, codec pipelines and metrics.",
            ],
            [
              "02",
              "Generalization evidence",
              "Measure unseen generators and report uncertainty.",
            ],
            [
              "03",
              "Operational readiness",
              "Validate latency, privacy, calibration and failure handling.",
            ],
          ].map(([n, t, d]) => (
            <div key={n}>
              <span className="eyebrow">GATE {n}</span>
              <h3>{t}</h3>
              <p>{d}</p>
            </div>
          ))}
        </div>
      </Panel>
      {selected && (
        <Modal title={selected[1]} onClose={() => setSelected(null)} drawer>
          <DetailList
            items={[
              ["Priority", selected[0]],
              ["Status", selected[2]],
              ["Impact", selected[3]],
              ["Complexity", selected[4]],
              ["Dependency", selected[5]],
              ["Target gate", selected[6]],
            ]}
          />
          <p>
            Acceptance requires reproducible comparison, documented limitations,
            and a review of channel and language regression. No benchmark gain
            is assumed.
          </p>
        </Modal>
      )}
    </>
  );
}
