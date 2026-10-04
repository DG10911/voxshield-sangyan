import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Play, Pause, Square, Search, Bookmark } from "lucide-react";
import {
  PageHeader,
  Panel,
  Chip,
  DataTable,
  Modal,
  DetailList,
  ExportButton,
  Bar,
} from "../components/ui";
import { LineChart, Waveform } from "../components/charts";
import { VerdictView, DetectorInspector } from "./Analyze";
import { detectors } from "../data/catalog";
import { liveConfidence } from "../services/mock";
import { useApp, usePreference } from "../store";
import type { CallRecord, DetectorScore } from "../types";
export function Live() {
  const [running, setRunning] = useState(false);
  const [time, setTime] = useState(0);
  const [selected, setSelected] = useState<DetectorScore | null>(null);
  const { log } = useApp();
  const score = liveConfidence(time);
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(
      () => setTime((t) => Math.min(120, t + 0.25)),
      250,
    );
    return () => clearInterval(timer);
  }, [running]);
  useEffect(() => {
    if (time === 4) log("stream.threshold_crossed", "LIVE-DEMO", "REVIEW");
    if (time === 120) setRunning(false);
  }, [time]);
  return (
    <>
      <PageHeader
        eyebrow="MONITOR / LIVE STREAM"
        title="Intelligence, in real time"
        description="A deterministic stream demonstrates how evidence develops across rolling windows."
      >
        <Chip tone={running ? "cyan" : "neutral"}>
          {running ? "SIMULATED STREAM" : time ? "PAUSED" : "DISCONNECTED"}
        </Chip>
      </PageHeader>
      <div className="stream-toolbar">
        <div className="actions">
          <button
            className="primary"
            disabled={running}
            onClick={() => {
              if (time >= 120) setTime(0);
              setRunning(true);
            }}
          >
            <Play size={15} /> {time ? "Resume" : "Start simulation"}
          </button>
          <button disabled={!running} onClick={() => setRunning(false)}>
            <Pause size={15} /> Pause
          </button>
          <button
            disabled={!time && !running}
            onClick={() => {
              setRunning(false);
              setTime(0);
            }}
          >
            <Square size={15} /> Stop
          </button>
        </div>
        <span className="mono">SESSION / LIVE-DEMO · NO AUDIO TRANSMITTED</span>
      </div>
      <div className="metric-grid">
        {[
          ["DURATION", time.toFixed(1) + "s"],
          ["SYNTHETIC LIKELIHOOD", score + "%"],
          ["TIME TO FLAG", time >= 4 ? "4.0s" : "Awaiting"],
          [
            "WINDOW / LATENCY",
            "2s / " + (148 + Math.round(Math.sin(time) * 8)) + "ms",
          ],
        ].map(([k, v]) => (
          <div className="metric-card" key={k}>
            <span className="eyebrow">{k}</span>
            <strong className="metric-value compact">{v}</strong>
          </div>
        ))}
      </div>
      <div className="grid-main">
        <Panel
          title="Rolling decision field"
          eyebrow="SIMULATED / 80% THRESHOLD"
          action={
            <Chip tone={time >= 4 ? "red" : "cyan"}>
              {time >= 4 ? "FLAGGED FOR REVIEW" : "OBSERVING"}
            </Chip>
          }
        >
          <LineChart
            values={Array.from(
              { length: Math.max(2, Math.ceil(time) + 1) },
              (_, i) => liveConfidence(i),
            )}
            label="Synthetic likelihood"
            color={time >= 4 ? "red" : "cyan"}
            xLabel="Elapsed time"
            xMax={Math.max(1, Math.ceil(time))}
            xUnit="s"
          />
          <div className="live-timeline">
            {Array.from({ length: 12 }, (_, i) => {
              const sec = Math.max(0, Math.floor(time) - 9) + i;
              return (
                <div
                  key={sec}
                  className={
                    sec === 4 && time >= 4
                      ? "flag"
                      : sec <= time
                        ? "passed"
                        : ""
                  }
                >
                  <span>{sec === 4 && time >= 4 ? "⚑ FLAG" : sec + "s"}</span>
                  <i />
                </div>
              );
            })}
          </div>
          <Waveform suspicious={time >= 4} />
          <div className="padded">
            <DetailList
              items={[
                [
                  "Language",
                  time > 1 ? "Hindi · stabilized at 1.5s" : "Detecting",
                ],
                ["Channel", "G.711 μ-law · simulated"],
                [
                  "Decision",
                  time >= 4
                    ? "SYNTHETIC · analyst review recommended"
                    : "Insufficient evidence",
                ],
                ["Transport", "Local simulation · WebSocket not connected"],
              ]}
            />
          </div>
        </Panel>
        <Panel title="Detector signals" eyebrow="ROLLING CONTRIBUTION">
          <div className="contributions">
            {detectors.map((d, i) => (
              <button
                className="detector-button"
                key={d.name}
                onClick={() =>
                  setSelected({
                    ...d,
                    score: Math.max(5, Math.min(d.score, score + i * 2)),
                  })
                }
              >
                <Bar
                  label={d.name}
                  value={Math.max(5, Math.min(d.score, score + i * 2))}
                  tone={time >= 4 && d.score > 80 ? "red" : "cyan"}
                />
              </button>
            ))}
          </div>
        </Panel>
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
export function Calls() {
  const { calls, review, notify } = useApp();
  const [params] = useSearchParams();
  const [search, setSearch] = useState("");
  const [verdict, setVerdict] = useState("All verdicts");
  const [language, setLanguage] = useState("All languages");
  const [channel, setChannel] = useState("All channels");
  const [status, setStatus] = useState("All statuses");
  const [confidence, setConfidence] = useState(0);
  const [date, setDate] = useState("");
  const [threat, setThreat] = useState("All threats");
  const [sort, setSort] = useState("Newest");
  const [page, setPage] = useState(0);
  const [saved, setSaved] = usePreference<Record<
    string,
    string | number
  > | null>("saved-filter", null);
  const [selected, setSelected] = useState<CallRecord | null>(
    calls.find((c) => c.id === params.get("call")) || null,
  );
  const filtered = calls
    .filter(
      (c) =>
        (c.id + " " + c.filename)
          .toLowerCase()
          .includes(search.toLowerCase()) &&
        (verdict === "All verdicts" || c.verdict === verdict) &&
        (language === "All languages" || c.language === language) &&
        (channel === "All channels" || c.channel === channel) &&
        (status === "All statuses" || c.status === status) &&
        c.confidence >= confidence &&
        (!date || c.timestamp.slice(0, 10) === date) &&
        (threat === "All threats" || c.threat === threat),
    )
    .sort((a, b) =>
      sort === "Confidence"
        ? b.confidence - a.confidence
        : sort === "Oldest"
          ? a.timestamp.localeCompare(b.timestamp)
          : b.timestamp.localeCompare(a.timestamp),
    );
  useEffect(
    () => setPage(0),
    [search, verdict, language, channel, status, confidence, date, threat],
  );
  const visible = filtered.slice(page * 10, page * 10 + 10);
  return (
    <>
      <PageHeader
        eyebrow="MONITOR / CALL HISTORY"
        title="The investigation record"
        description="Inspect decisions, follow evidence, and preserve the analyst review trail."
      >
        <ExportButton
          rows={filtered.map(({ detectors, reasons, ...c }) => c)}
          name="voxshield-calls"
        />
      </PageHeader>
      <Panel>
        <div className="filter-bar">
          <label className="search-input">
            <Search size={16} />
            <input
              aria-label="Search calls"
              placeholder="Search call ID or filename"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
          {[
            [
              verdict,
              setVerdict,
              ["All verdicts", "SYNTHETIC", "HUMAN", "ABSTAIN"],
            ],
            [
              language,
              setLanguage,
              ["All languages", ...new Set(calls.map((c) => c.language))],
            ],
            [
              channel,
              setChannel,
              ["All channels", "G.711 μ-law", "PCM 16-bit"],
            ],
            [
              status,
              setStatus,
              ["All statuses", "New", "In review", "Resolved"],
            ],
          ].map(([v, set, options], i) => (
            <select
              key={i}
              aria-label={
                [
                  "Verdict filter",
                  "Language filter",
                  "Channel filter",
                  "Status filter",
                ][i]
              }
              value={v as string}
              onChange={(e) => (set as (s: string) => void)(e.target.value)}
            >
              {(options as string[]).map((o) => (
                <option key={o}>{o}</option>
              ))}
            </select>
          ))}
        </div>
        <div className="filter-bar secondary">
          <label>
            Min confidence{" "}
            <input
              className="number-input"
              aria-label="Minimum confidence"
              type="number"
              min="0"
              max="100"
              value={confidence}
              onChange={(e) => setConfidence(+e.target.value)}
            />
            %
          </label>
          <input
            aria-label="Call date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
          <select
            aria-label="Threat filter"
            value={threat}
            onChange={(e) => setThreat(e.target.value)}
          >
            {["All threats", "GEN-UNK-04", "Unattributed"].map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <select
            aria-label="Sort calls"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
          >
            {["Newest", "Oldest", "Confidence"].map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
          <button
            onClick={() => {
              setSaved({
                verdict,
                language,
                channel,
                status,
                confidence,
                date,
                threat,
              });
              notify("Current view saved locally");
            }}
          >
            <Bookmark size={14} /> Save view
          </button>
          {saved && (
            <button
              onClick={() => {
                setVerdict(String(saved.verdict));
                setLanguage(String(saved.language));
                setChannel(String(saved.channel));
                setStatus(String(saved.status));
                setConfidence(Number(saved.confidence));
                setDate(String(saved.date));
                setThreat(String(saved.threat));
              }}
            >
              Load saved
            </button>
          )}
        </div>
        <DataTable
          headers={[
            "CALL ID",
            "TIME (LOCAL)",
            "LANGUAGE",
            "CHANNEL",
            "DURATION",
            "VERDICT",
            "CONF.",
            "THREAT",
            "ANALYST",
            "STATUS",
          ]}
          rows={visible.map((c) => [
            <span className="mono">{c.id}</span>,
            new Date(c.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            c.language,
            c.channel,
            c.duration + "s",
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
            c.confidence + "%",
            c.threat,
            c.analyst,
            c.status,
          ])}
          onRow={(i) => setSelected(visible[i])}
        />
        <div className="pagination">
          <span>
            {filtered.length} calls · Page {page + 1} /{" "}
            {Math.max(1, Math.ceil(filtered.length / 10))}
          </span>
          <div className="actions">
            <button disabled={page === 0} onClick={() => setPage(page - 1)}>
              Previous
            </button>
            <button
              disabled={(page + 1) * 10 >= filtered.length}
              onClick={() => setPage(page + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </Panel>
      {selected && (
        <Modal title={selected.id} onClose={() => setSelected(null)} drawer>
          <VerdictView result={selected} />
          <label className="field">
            Review status
            <select
              value={calls.find((c) => c.id === selected.id)?.status}
              onChange={(e) =>
                review(selected.id, e.target.value as CallRecord["status"])
              }
            >
              {["New", "In review", "Resolved"].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <DetailList
            items={[
              ["Audit", "analysis.completed → " + selected.verdict],
              ["Timestamp", new Date(selected.timestamp).toLocaleString()],
              ["Source", selected.source],
              [
                "Model",
                selected.source === "demo"
                  ? "vox-fusion-2.4.1-demo"
                  : "See detector versions",
              ],
            ]}
          />
        </Modal>
      )}
    </>
  );
}
