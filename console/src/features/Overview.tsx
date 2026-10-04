import { Link } from "react-router-dom";
import { ArrowRight, ArrowUpRight, AudioLines } from "lucide-react";
import VoxOrb from "../components/VoxOrb";
import { Panel, PageHeader, Chip, Bar, DataTable } from "../components/ui";
import { LineChart, Sparkline } from "../components/charts";
import { metrics, detectors } from "../data/catalog";
import { useApp } from "../store";
export default function Overview() {
  const { calls } = useApp();
  return (
    <>
      <PageHeader
        eyebrow="MONITOR / COMMAND CENTER"
        title="Every voice leaves a signal"
        description="Voice fraud intelligence. Evidence you can inspect. Decisions you can trust."
      >
        <Link className="button primary" to="/analyze">
          <AudioLines size={16} /> Analyze a call <ArrowUpRight size={15} />
        </Link>
      </PageHeader>
      <section className="hero">
        <div className="hero-copy">
          <Chip tone="cyan">INTELLIGENCE ONLINE · SIMULATED</Chip>
          <h2>
            Listening beyond
            <br />
            <span>the human ear.</span>
          </h2>
          <p>
            Nine evidence systems. One calibrated decision.
            <br />
            Detect voice manipulation across Indic languages,
            <br />
            even over phone-quality audio.
          </p>
          <div className="hero-stats">
            <div>
              <strong>
                09<span>/09</span>
              </strong>
              <small>DETECTORS HEALTHY</small>
            </div>
            <div>
              <strong>23</strong>
              <small>LANGUAGES IN SCOPE</small>
            </div>
            <div>
              <strong>
                148<span>ms</span>
              </strong>
              <small>SIMULATED LATENCY</small>
            </div>
          </div>
          <div className="decision-key">
            <Chip tone="green">HUMAN</Chip>
            <Chip tone="red">SYNTHETIC</Chip>
            <Chip tone="amber">ABSTAIN</Chip>
          </div>
        </div>
        <div className="hero-orb">
          <VoxOrb />
          <div className="orb-legend">
            <span className="cyan">●</span> VOX INTELLIGENCE CORE{" "}
            <span className="mono">v2.4.1-demo</span>
          </div>
        </div>
      </section>
      <div className="section-label">
        <span>PERFORMANCE SNAPSHOT</span>
        <span>SUPPLIED RESEARCH VALUES · NOT INDEPENDENTLY VERIFIED</span>
      </div>
      <div className="metric-grid">
        {metrics.map((m, i) => (
          <Link to="/results" className="metric-card" key={m.label}>
            <div className="eyebrow">
              {m.label}
              <ArrowUpRight size={13} />
            </div>
            <div className="metric-value">
              {m.value}
              <span>{m.unit}</span>
            </div>
            <Sparkline seed={i} tone={m.tone} />
            <p>{m.note}</p>
          </Link>
        ))}
      </div>
      <div className="grid-two">
        <Panel
          title="Risk meets coverage"
          eyebrow="CALIBRATED ABSTENTION"
          action={
            <Link className="text-link" to="/results">
              Explore <ArrowUpRight size={13} />
            </Link>
          }
        >
          <div className="chart-key">
            <span className="cyan">— Selective risk</span>
            <span>Illustrative curve · AURC .0273 supplied</span>
          </div>
          <LineChart
            values={[0.5, 0.7, 0.8, 1.2, 1.5, 2.1, 3.1, 4.8, 7.4, 12.6]}
            max={15}
          />
        </Panel>
        <Panel
          title="Evidence in agreement"
          eyebrow="ENSEMBLE CONTRIBUTION"
          action={<Chip tone="cyan">DEMO</Chip>}
        >
          <div className="contributions">
            {detectors.slice(0, 6).map((d) => (
              <Bar
                key={d.name}
                label={d.name}
                value={d.score}
                tone={d.score > 85 ? "cyan" : "neutral"}
              />
            ))}
          </div>
          <Link className="panel-footer text-link" to="/evidence">
            Inspect all nine systems <ArrowRight size={15} />
          </Link>
        </Panel>
      </div>
      <div className="grid-main">
        <Panel
          title="Detection stream"
          eyebrow="LATEST SAMPLE CALLS"
          action={
            <Link className="text-link" to="/calls">
              All calls <ArrowUpRight size={13} />
            </Link>
          }
        >
          <DataTable
            headers={["CALL ID", "LANGUAGE", "VERDICT", "CONFIDENCE"]}
            rows={calls.slice(0, 5).map((c) => [
              <Link className="mono text-link" to={"/calls?call=" + c.id}>
                {c.id}
              </Link>,
              c.language,
              <Chip
                tone={
                  c.verdict === "SYNTHETIC"
                    ? "red"
                    : c.verdict === "HUMAN"
                      ? "green"
                      : "amber"
                }
              >
                {c.verdict}
              </Chip>,
              <span className="mono">{c.confidence}%</span>,
            ])}
          />
        </Panel>
        <Panel title="Channel resilience" eyebrow="SUPPLIED EER">
          <div className="channel-row">
            <span>Clean audio</span>
            <strong>
              9.24<small>%</small>
            </strong>
          </div>
          <div className="channel-row">
            <span>G.711 telephony</span>
            <strong>
              11.41<small>%</small>
            </strong>
          </div>
          <div className="notice">
            +2.17 pp across the supplied channel comparison.
          </div>
          <Link className="text-link panel-footer" to="/languages">
            Inspect language coverage <ArrowRight size={14} />
          </Link>
        </Panel>
      </div>
    </>
  );
}
