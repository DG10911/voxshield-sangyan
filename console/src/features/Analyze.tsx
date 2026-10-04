import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  Upload,
  Mic,
  Square,
  ArrowRight,
  FileAudio,
  Download,
} from "lucide-react";
import type { AnalysisResult, DetectorScore, Verdict } from "../types";
import {
  Panel,
  PageHeader,
  Chip,
  Modal,
  DetailList,
  Tabs,
  Bar,
} from "../components/ui";
import { EvidenceGraph, Waveform } from "../components/charts";
import VoxOrb from "../components/VoxOrb";
import { api, download } from "../services/api";
import { mockAnalysis } from "../services/mock";
import { detectors } from "../data/catalog";
import { useApp } from "../store";
export function DetectorInspector({
  detector,
  onClose,
  source = "demo",
}: {
  detector: DetectorScore;
  source?: "demo" | "live";
  onClose: () => void;
}) {
  return (
    <Modal title={detector.name} onClose={onClose} drawer>
      <Chip tone="cyan">
        {source === "demo" ? "DETERMINISTIC DEMO EVIDENCE" : "BACKEND EVIDENCE"}
      </Chip>
      <h3>{detector.detail}</h3>
      <Bar
        value={detector.score}
        label="Synthetic likelihood"
        tone={detector.score > 80 ? "red" : "cyan"}
      />
      <DetailList
        items={[
          ["Fusion weight", detector.weight + "%"],
          ["Model version", detector.version],
          ["Window", source === "demo" ? "04.2–07.8 seconds" : "Not supplied"],
          [
            "Health",
            source === "demo" ? "Available · simulated" : "Not supplied",
          ],
          [
            "Calibration",
            source === "demo"
              ? "ECE .058 · supplied aggregate"
              : "Not supplied",
          ],
        ]}
      />
      <div className="notice">
        A model score is one signal, not proof of fraud. Corroborate with other
        evidence and analyst review.
      </div>
    </Modal>
  );
}
export function VerdictView({ result }: { result: AnalysisResult }) {
  const [tab, setTab] = useState("Evidence");
  const [selected, setSelected] = useState<DetectorScore | null>(null);
  const [time, setTime] = useState(0);
  const tone =
    result.verdict === "SYNTHETIC"
      ? "red"
      : result.verdict === "HUMAN"
        ? "green"
        : "amber";
  return (
    <>
      <div className={"verdict-panel " + tone}>
        <div>
          <span className="eyebrow">
            CALIBRATED DECISION · {result.source.toUpperCase()}
          </span>
          <h2>{result.verdict}</h2>
          <p>
            {result.verdict === "ABSTAIN"
              ? "Insufficient evidence for a reliable binary decision."
              : result.verdict === "SYNTHETIC"
                ? "High-risk voice manipulation detected."
                : "Evidence is consistent with natural speech."}
          </p>
        </div>
        <div className="verdict-score">
          {result.confidence}
          <span>%</span>
          <small>MODEL CONFIDENCE</small>
        </div>
      </div>
      <div className="notice">
        {result.verdict === "ABSTAIN"
          ? "Recommended action: human review. Poor channel quality and model disagreement prevent a reliable decision."
          : result.verdict === "SYNTHETIC"
            ? "Recommended action: pause the transaction and verify through an independent trusted channel."
            : "Recommended action: continue normal checks. A HUMAN result does not establish identity or intent."}
      </div>
      <div className="reason-codes">
        {result.reasons.map((r) => (
          <code key={r}>{r}</code>
        ))}
      </div>
      <Tabs
        items={["Evidence", "Transcript", "Metadata"]}
        value={tab}
        onChange={setTab}
      />
      {tab === "Evidence" ? (
        <EvidenceGraph
          items={result.detectors}
          verdict={result.verdict}
          onSelect={setSelected}
        />
      ) : tab === "Transcript" ? (
        <>
          <Waveform
            suspicious={result.verdict === "SYNTHETIC"}
            onTime={setTime}
          />
          <div
            className={
              "transcript " + (time > 4 && time < 8 ? "highlight" : "")
            }
          >
            <span className="mono">04.2 — 07.8</span>
            <p>{result.transcript}</p>
            <small>
              {result.source === "demo"
                ? "Demo transcript · not transcribed from uploaded audio."
                : "Transcript supplied by the configured backend."}
            </small>
          </div>
        </>
      ) : (
        <DetailList
          items={[
            ["Call ID", result.id],
            ["Language", result.language],
            ["Channel", result.channel],
            ["Duration", result.duration + "s"],
            [
              "Model",
              result.source === "demo"
                ? "vox-fusion-2.4.1-demo"
                : "See detector versions",
            ],
            [
              "Confidence calibration",
              result.source === "demo"
                ? "ECE .058 · reference"
                : "Backend-provided score; protocol not supplied",
            ],
            ["Source", result.source],
            ["Filename", result.filename],
          ]}
        />
      )}
      <div className="actions panel-footer">
        <button
          onClick={() =>
            download(
              result.id + ".json",
              JSON.stringify(result, null, 2),
              "application/json",
            )
          }
        >
          <Download size={15} /> Export report
        </button>
        <Link className="button" to="/threats?focus=g">
          Related intelligence <ArrowRight size={14} />
        </Link>
      </div>
      {selected && (
        <DetectorInspector
          detector={selected}
          source={result.source}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
export default function Analyze() {
  const { addResult, result, mode, setMode, notify } = useApp();
  const [file, setFile] = useState<File | null>(null);
  const [scenario, setScenario] = useState<Verdict>("SYNTHETIC");
  const [selected, setSelected] = useState(false);
  const [stage, setStage] = useState(-1);
  const [error, setError] = useState("");
  const [url, setUrl] = useState("");
  const [recording, setRecording] = useState(false);
  const recorder = useRef<MediaRecorder | null>(null);
  const media = useRef<MediaStream | null>(null);
  const picker = useRef<HTMLInputElement>(null);
  const active = useRef(true);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
      media.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);
  useEffect(() => {
    if (!file) {
      setUrl("");
      return;
    }
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);
  const selectFile = (f?: File) => {
    if (!f) return;
    if (!/\.(wav|mp3|ogg|webm|m4a|flac)$/i.test(f.name)) {
      setError("Unsupported audio. Choose WAV, MP3, OGG, WebM, M4A or FLAC.");
      return;
    }
    if (f.size > 50 * 1024 * 1024) {
      setError("Audio exceeds 50 MB. Select a shorter recording.");
      return;
    }
    setFile(f);
    setSelected(true);
    setStage(-1);
    setError("");
  };
  const record = async () => {
    if (recording) {
      recorder.current?.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      media.current = stream;
      const rec = new MediaRecorder(stream);
      recorder.current = rec;
      const chunks: BlobPart[] = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = () => {
        if (active.current)
          selectFile(
            new File(chunks, "microphone.webm", { type: rec.mimeType }),
          );
        stream.getTracks().forEach((t) => t.stop());
      };
      rec.start();
      setRecording(true);
    } catch {
      setError(
        "Microphone unavailable or permission denied. Use the file picker or a sample scenario.",
      );
    }
  };
  const start = async () => {
    if (mode === "LIVE API" && !file) {
      setError(
        "Choose an audio file for live analysis. Sample scenarios require demo mode.",
      );
      return;
    }
    setError("");
    setStage(0);
    for (let i = 1; i <= 4; i++) {
      await new Promise((r) => setTimeout(r, 700));
      if (!active.current) return;
      setStage(i);
    }
    let r: AnalysisResult;
    const id = "VX-" + Date.now().toString(16).slice(-6).toUpperCase();
    try {
      r =
        mode === "LIVE API"
          ? await api.analyze(file, scenario, id)
          : mockAnalysis(scenario, file?.name, id);
    } catch {
      setMode("OFFLINE DEMO");
      notify("API unavailable · result is a demo scenario");
      r = mockAnalysis(scenario, file?.name, id);
    }
    if (active.current) {
      addResult(r);
      setStage(5);
    }
  };
  const working = stage >= 0 && stage < 5;
  return (
    <>
      <PageHeader
        eyebrow="MONITOR / ANALYZE CALL"
        title="Follow the evidence"
        description="From an unknown voice to a calibrated, explainable decision."
      >
        <Chip tone="cyan">{mode}</Chip>
      </PageHeader>
      <div className="grid-main">
        <Panel title="Signal intake" eyebrow="01 / INPUT">
          <div
            className="dropzone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              if (!working) selectFile(e.dataTransfer.files[0]);
            }}
          >
            <div className="upload-symbol">
              <Upload size={27} />
            </div>
            <h3>
              {selected
                ? file?.name || scenario.toLowerCase() + "_demo_hi.wav"
                : "A voice worth a closer look"}
            </h3>
            <p>Drop an audio file here, or choose from your device.</p>
            <div className="actions">
              <button
                className="primary"
                disabled={working || recording}
                onClick={() => picker.current?.click()}
              >
                <FileAudio size={15} /> Choose audio
              </button>
              <button disabled={working} onClick={() => void record()}>
                {recording ? <Square size={15} /> : <Mic size={15} />}{" "}
                {recording ? "Stop recording" : "Record"}
              </button>
            </div>
            <small>
              WAV, MP3, OGG, WebM, M4A, FLAC · up to 50 MB
              <br />
              Audio stays in memory in demo mode.
            </small>
            <input
              ref={picker}
              type="file"
              accept="audio/*"
              hidden
              onChange={(e) => selectFile(e.target.files?.[0])}
            />
          </div>
          <div className="sample-header">
            <span className="eyebrow">EXPLORE A DEMO SCENARIO</span>
            <span>Deterministic outcomes</span>
          </div>
          <div className="scenario-grid">
            {(["SYNTHETIC", "HUMAN", "ABSTAIN"] as Verdict[]).map((s, i) => (
              <button
                disabled={working}
                key={s}
                className={scenario === s && selected ? "selected" : ""}
                onClick={() => {
                  setScenario(s);
                  setFile(null);
                  setSelected(true);
                  setStage(-1);
                  setError("");
                }}
              >
                <Chip tone={i === 0 ? "red" : i === 1 ? "green" : "amber"}>
                  {s}
                </Chip>
                <small>
                  {
                    [
                      "Investment voice clone",
                      "Natural support call",
                      "Degraded ambiguous audio",
                    ][i]
                  }
                </small>
              </button>
            ))}
          </div>
          {selected && (
            <>
              <Waveform
                url={url}
                suspicious={stage === 5 && scenario === "SYNTHETIC"}
                caption={
                  file
                    ? "Illustrative envelope · playback uses your file"
                    : "Demo signal · 8 kHz · G.711 · Hindi"
                }
              />
              <div className="analysis-steps">
                {[
                  "Preprocessing",
                  "Language & codec",
                  "Evidence systems",
                  "Arbitration",
                  "Calibration",
                ].map((s, i) => (
                  <div key={s} className={stage >= i ? "complete" : ""}>
                    <span>
                      {stage > i ? "✓" : String(i + 1).padStart(2, "0")}
                    </span>
                    {s}
                  </div>
                ))}
              </div>
              <button
                className="primary wide"
                disabled={working || recording}
                onClick={() => void start()}
              >
                {working ? "Evidence converging…" : "Analyze signal"}
                <ArrowRight size={15} />
              </button>
            </>
          )}
          {error && (
            <div role="alert" className="error">
              {error}
            </div>
          )}
        </Panel>
        <Panel title="Intelligence state" eyebrow="02 / SIGNAL FIELD">
          <VoxOrb
            state={
              working
                ? "ANALYZING"
                : stage === 5 && result
                  ? result.verdict
                  : selected
                    ? "LISTENING"
                    : "IDLE"
            }
            confidence={stage === 5 && result ? result.confidence : 0}
          />
          <div className="intake-info">
            <p>
              Nine independent perspectives.
              <br />
              One accountable decision.
            </p>
            <div className="mini-modules">
              {detectors.map((d, i) => (
                <span
                  key={d.name}
                  className={stage >= 2 || stage === 5 ? "cyan" : ""}
                >
                  <span className="mono">0{i + 1}</span> {d.name}
                </span>
              ))}
            </div>
            <div className="notice">
              Demo mode does not classify your recording. It previews the
              selected scenario using sample evidence.
            </div>
          </div>
        </Panel>
      </div>
      {stage === 5 && result && (
        <Panel title="Analysis report" eyebrow={"03 / " + result.id}>
          <div className="padded" aria-live="polite">
            <VerdictView result={result} />
          </div>
        </Panel>
      )}
    </>
  );
}
