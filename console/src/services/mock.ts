import { detectors } from "../data/catalog";
import type { AnalysisResult, AuditEvent, CallRecord, Verdict } from "../types";
export const reasons: Record<Verdict, string[]> = {
  SYNTHETIC: [
    "HARMONIC_DISCONTINUITY",
    "TEMPORAL_REPETITION",
    "PROSODY_MISMATCH",
  ],
  HUMAN: ["COHERENT_ACOUSTICS", "NATURAL_TIMING", "MODEL_AGREEMENT"],
  ABSTAIN: ["LOW_CHANNEL_QUALITY", "MODEL_DISAGREEMENT", "BOUNDARY_CONFIDENCE"],
};
export function mockAnalysis(
  verdict: Verdict = "SYNTHETIC",
  filename = "investment_call_hi.wav",
  id = "VX-8A91F",
): AnalysisResult {
  return {
    id,
    filename,
    verdict,
    confidence:
      verdict === "SYNTHETIC" ? 91.4 : verdict === "HUMAN" ? 94.8 : 52.1,
    language: "Hindi",
    channel: "G.711 μ-law",
    duration: 18,
    timestamp: new Date().toISOString(),
    detectors: detectors.map((d, i) => ({
      ...d,
      score:
        verdict === "HUMAN"
          ? 8 + i * 2
          : verdict === "ABSTAIN"
            ? 34 + ((i * 13) % 41)
            : d.score,
    })),
    reasons: reasons[verdict],
    transcript:
      verdict === "HUMAN"
        ? "नमस्ते, मैं अपनी पिछली शिकायत की स्थिति जानना चाहता हूँ। / Hello, I would like to check the status of my previous request."
        : "नमस्ते, आपके लिए एक विशेष निवेश अवसर है। आज ही ट्रांसफ़र करें। / Hello, there is a special investment opportunity for you. Transfer today.",
    source: "demo",
  };
}
export const initialCalls: CallRecord[] = Array.from(
  { length: 32 },
  (_, i) => ({
    ...mockAnalysis(
      (["SYNTHETIC", "HUMAN", "ABSTAIN", "HUMAN"] as Verdict[])[i % 4],
      `call_${4127 + i}.wav`,
      i === 0
        ? "VX-8A91F"
        : `VX-${(41270 + i * 17).toString(16).toUpperCase()}`,
    ),
    language: ["Hindi", "Tamil", "Punjabi", "Bengali"][i % 4],
    timestamp: new Date(Date.UTC(2026, 9, 4, 13, 42 - i * 7)).toISOString(),
    channel: i % 3 ? "G.711 μ-law" : "PCM 16-bit",
    analyst: i % 2 ? "A. Rao" : "D. Goenka",
    status: i % 3 ? "New" : "In review",
    threat: i % 4 === 0 ? "GEN-UNK-04" : "Unattributed",
  }),
);
export const initialAudit: AuditEvent[] = initialCalls
  .slice(0, 7)
  .map((c, i) => ({
    id: `AUD-${100 + i}`,
    timestamp: c.timestamp,
    actor: "demo-analyst",
    event: "analysis.completed",
    call: c.id,
    action: c.verdict,
    hash: `sim-${(917283 + i * 18379).toString(16)}`,
    source: "demo",
  }));
export function liveConfidence(t: number) {
  return t < 4
    ? Math.min(79, Math.round(18 + t * 15))
    : Math.min(94, Math.round(18 + t * 15 + 7));
}
