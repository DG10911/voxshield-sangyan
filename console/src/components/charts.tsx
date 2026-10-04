import { useEffect, useRef, useState } from "react";
import type { DetectorScore } from "../types";
import { Pause, Play, ZoomIn, ZoomOut } from "lucide-react";
export function Sparkline({
  seed = 0,
  tone = "cyan",
}: {
  seed?: number;
  tone?: string;
}) {
  const vals = Array.from(
    { length: 28 },
    (_, i) =>
      18 + Math.sin(i * 0.7 + seed) * 7 + Math.cos(i * 0.31 + seed) * 10,
  );
  return (
    <svg
      className={"sparkline " + tone}
      viewBox="0 0 150 45"
      aria-hidden="true"
    >
      <path
        d={vals.map((v, i) => `${i ? "L" : "M"}${i * 5.5},${v}`).join(" ")}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}
export function LineChart({
  values = [2, 3, 5, 6, 9, 12, 19, 28, 45, 68],
  label = "Selective risk",
  color = "cyan",
  unit = "%",
  xLabel = "Coverage",
  max = 100,
  xMax = 100,
  xUnit = "%",
}: {
  values?: number[];
  label?: string;
  color?: string;
  unit?: string;
  xLabel?: string;
  max?: number;
  xMax?: number;
  xUnit?: string;
}) {
  const [hover, setHover] = useState<number | null>(null);
  const coords = values.map((v, i) => [
    48 + (i * 600) / (values.length - 1),
    180 - (v / max) * 150,
  ]);
  const path = coords.map(([x, y], i) => `${i ? "L" : "M"}${x},${y}`).join(" ");
  return (
    <div className={"chart " + color}>
      <svg
        viewBox="0 0 680 235"
        role="img"
        aria-label={`${label}: ${values.join(", ")}${unit}`}
      >
        <defs>
          <linearGradient
            id={"fill-" + label.replaceAll(" ", "")}
            x1="0"
            y1="0"
            x2="0"
            y2="1"
          >
            <stop stopColor="currentColor" stopOpacity=".16" />
            <stop offset="1" stopColor="currentColor" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0, 1, 2, 3].map((i) => (
          <g key={i}>
            <line
              x1="48"
              x2="650"
              y1={30 + i * 50}
              y2={30 + i * 50}
              stroke="#223047"
              strokeDasharray="3 5"
            />
            <text x="3" y={34 + i * 50}>
              {max < 1
                ? (max - (i * max) / 3).toFixed(3)
                : max <= 1
                  ? (max - (i * max) / 3).toFixed(2)
                  : Math.round(max - (i * max) / 3)}
              {unit}
            </text>
          </g>
        ))}
        <path
          d={path + " L648,180 L48,180 Z"}
          fill={`url(#fill-${label.replaceAll(" ", "")})`}
        />
        <path d={path} fill="none" stroke="currentColor" strokeWidth="2" />
        {coords.map(([x, y], i) => (
          <g
            key={i}
            tabIndex={0}
            onFocus={() => setHover(i)}
            onBlur={() => setHover(null)}
            onMouseEnter={() => setHover(i)}
            onMouseLeave={() => setHover(null)}
            aria-label={`${xLabel} ${((i * xMax) / (values.length - 1)).toFixed(1)} ${xUnit}, ${label} ${values[i]}${unit}`}
          >
            <circle cx={x} cy={y} r="14" fill="transparent" />
            <circle cx={x} cy={y} r={hover === i ? 5 : 2} fill="currentColor" />
            <title>{`${label}: ${values[i]}${unit}`}</title>
          </g>
        ))}
        {[0, 25, 50, 75, 100].map((v) => (
          <text key={v} x={48 + v * 6} y="204" textAnchor="middle">
            {Math.round((v / 100) * xMax)}
            {xUnit}
          </text>
        ))}
        <text x="350" y="230" textAnchor="middle">
          {xLabel}
        </text>
        {hover !== null && (
          <g>
            <rect
              x="230"
              y="10"
              width="270"
              height="28"
              rx="4"
              fill="#182536"
            />
            <text x="245" y="29" className="chart-tooltip">
              {label} · {values[hover]}
              {unit}
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}
export function Waveform({
  url,
  duration = 18,
  suspicious = false,
  onTime,
  caption = "Deterministic sample envelope",
}: {
  url?: string;
  duration?: number;
  suspicious?: boolean;
  onTime?: (t: number) => void;
  caption?: string;
}) {
  const audio = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [envelope, setEnvelope] = useState<number[] | null>(null);
  const [decodedDuration, setDecodedDuration] = useState(duration);
  const [decodeStatus, setDecodeStatus] = useState("");
  useEffect(() => {
    let cancelled = false;
    let context: AudioContext | undefined;
    setEnvelope(null);
    setDecodedDuration(duration);
    setDecodeStatus("");
    if (url) {
      setDecodeStatus("Decoding audio…");
      void fetch(url)
        .then((r) => r.arrayBuffer())
        .then(async (buffer) => {
          context = new AudioContext();
          const decoded = await context.decodeAudioData(buffer);
          if (cancelled) return;
          const channel = decoded.getChannelData(0);
          const points = Array.from({ length: 160 }, (_, i) => {
            const start = Math.floor((i * channel.length) / 160),
              end = Math.floor(((i + 1) * channel.length) / 160);
            let peak = 0;
            for (
              let j = start;
              j < end;
              j += Math.max(1, Math.floor((end - start) / 200))
            )
              peak = Math.max(peak, Math.abs(channel[j]));
            return peak;
          });
          setEnvelope(points);
          setDecodedDuration(decoded.duration);
          setDecodeStatus(
            `${decoded.sampleRate.toLocaleString()} Hz · ${decoded.duration.toFixed(1)}s · decoded envelope`,
          );
        })
        .catch(() => {
          if (!cancelled)
            setDecodeStatus("Envelope unavailable · illustrative fallback");
        })
        .finally(() => {
          void context?.close();
        });
    }
    return () => {
      cancelled = true;
    };
  }, [url, duration]);
  const total = decodedDuration;
  useEffect(() => {
    setTime(0);
    setPlaying(false);
  }, [url]);
  useEffect(() => {
    if (!playing || url) return;
    const t = setInterval(
      () =>
        setTime((v) => {
          if (v >= total) {
            setPlaying(false);
            return 0;
          }
          return v + 0.1;
        }),
      100,
    );
    return () => clearInterval(t);
  }, [playing, url, total]);
  useEffect(() => onTime?.(time), [time]);
  const seek = (v: number) => {
    setTime(v);
    if (audio.current) audio.current.currentTime = v;
  };
  return (
    <div className="waveform">
      <div className="wave-meta">
        <span className="eyebrow">AUDIO SIGNAL</span>
        <span>{decodeStatus || caption}</span>
        <div className="actions">
          <button
            className="icon-button"
            aria-label="Zoom waveform out"
            onClick={() => setZoom(Math.max(1, zoom - 1))}
          >
            <ZoomOut size={14} />
          </button>
          <span>{zoom}×</span>
          <button
            className="icon-button"
            aria-label="Zoom waveform in"
            onClick={() => setZoom(Math.min(4, zoom + 1))}
          >
            <ZoomIn size={14} />
          </button>
        </div>
      </div>
      <div className="wave-scroll">
        <svg
          viewBox="0 0 800 115"
          style={{ width: `${zoom * 100}%` }}
          role="img"
          aria-label="Audio waveform; use seek slider below"
        >
          <line x1="0" x2="800" y1="57" y2="57" stroke="#223047" />
          {suspicious && (
            <rect
              x="185"
              y="6"
              width="160"
              height="100"
              fill="#ff4d6a"
              opacity=".07"
            />
          )}
          {Array.from({ length: 160 }, (_, i) => {
            const amp = envelope
              ? Math.max(1, envelope[i] * 48)
              : 6 + Math.abs(Math.sin(i * 0.47) * Math.cos(i * 0.13)) * 40;
            return (
              <line
                key={i}
                x1={i * 5}
                x2={i * 5}
                y1={57 - amp}
                y2={57 + amp}
                stroke={suspicious && i > 37 && i < 69 ? "#ff4d6a" : "#22d3ee"}
                strokeWidth="2"
                opacity={i / 160 < time / total ? 1 : 0.42}
              >
                <title>{((i / 160) * total).toFixed(1)}s</title>
              </line>
            );
          })}
          <line
            x1={(time / total) * 800}
            x2={(time / total) * 800}
            y1="0"
            y2="115"
            stroke="white"
          />
        </svg>
      </div>
      <input
        aria-label="Seek audio"
        type="range"
        min="0"
        max={total}
        step=".1"
        value={time}
        onChange={(e) => seek(+e.target.value)}
      />
      <div className="between">
        <button
          onClick={() => {
            if (url && audio.current) {
              if (playing) audio.current.pause();
              else void audio.current.play().catch(() => setPlaying(false));
            }
            setPlaying(!playing);
          }}
        >
          {playing ? <Pause size={14} /> : <Play size={14} />}{" "}
          {url ? "Playback" : "Preview timeline"}
        </button>
        <span className="mono">
          {time.toFixed(1)}s / {total.toFixed(1)}s
        </span>
        {suspicious && <span className="red small">Anomaly · 04.2–07.8s</span>}
      </div>
      {url && (
        <audio
          ref={audio}
          src={url}
          onTimeUpdate={() => setTime(audio.current?.currentTime || 0)}
          onEnded={() => setPlaying(false)}
        />
      )}
    </div>
  );
}
export function EvidenceGraph({
  items,
  onSelect,
  verdict = "EVIDENCE",
}: {
  items: DetectorScore[];
  onSelect: (d: DetectorScore) => void;
  verdict?: string;
}) {
  return (
    <div className="evidence-graph">
      <svg
        viewBox="0 0 600 350"
        role="img"
        aria-label="Evidence contribution graph; select a detector in the accompanying list"
      >
        <circle
          cx="300"
          cy="175"
          r="105"
          fill="none"
          stroke="#223047"
          strokeDasharray="3 7"
        />
        <circle cx="300" cy="175" r="62" fill="#101a28" stroke="#365069" />
        <text x="300" y="172" textAnchor="middle" fill="#eef3fb" fontSize="12">
          {verdict}
        </text>
        <text x="300" y="191" textAnchor="middle" fill="#8fa0ba" fontSize="9">
          CALIBRATED FUSION
        </text>
        {items.map((d, i) => {
          const a = (i / items.length) * Math.PI * 2 - Math.PI / 2;
          const x = 300 + Math.cos(a) * 200,
            y = 175 + Math.sin(a) * 140;
          return (
            <g
              key={d.name}
              role="button"
              tabIndex={0}
              aria-label={`Inspect ${d.name}: ${d.score}% synthetic likelihood`}
              onClick={() => onSelect(d)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(d);
                }
              }}
              style={{ cursor: "pointer" }}
            >
              <title>
                {d.name}: {d.score}% · fusion weight {d.weight}%
              </title>
              <line
                x1={300 + Math.cos(a) * 64}
                y1={175 + Math.sin(a) * 64}
                x2={x}
                y2={y}
                stroke={d.score > 80 ? "#ff4d6a" : "#365069"}
                opacity=".5"
              />
              <circle
                cx={x}
                cy={y}
                r="7"
                fill={d.score > 80 ? "#ff4d6a" : "#22d3ee"}
              />
              <text
                x={x}
                y={y + 23}
                textAnchor="middle"
                fill="#8fa0ba"
                fontSize="10"
              >
                {d.name.split(" /")[0]}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="evidence-list">
        {items.map((d) => (
          <button key={d.name} onClick={() => onSelect(d)}>
            <span>{d.name}</span>
            <span className="mono">
              {d.score}% <span className="muted">↗</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
