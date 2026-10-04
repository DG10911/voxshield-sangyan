import type {
  AnalysisResult,
  HealthStatus,
  Verdict,
  AuditEvent,
  Threat,
  IntelNode,
  IntelEdge,
  ProductRisk,
  SpeakerVerification,
  DeploymentProfile,
} from "../types";
import { mockAnalysis } from "./mock";
export const config = {
  api:
    import.meta.env.VITE_API_BASE_URL ??
    (import.meta.env.DEV ? "http://localhost:8000" : ""),
  ws: import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000",
  demo: import.meta.env.VITE_DEMO_MODE !== "false",
  three: import.meta.env.VITE_ENABLE_3D !== "false",
  motion: import.meta.env.VITE_ENABLE_ADVANCED_MOTION !== "false",
};
export const endpoints = {
  health: "/api/health",
  analyze: "/api/analyze?bhashini=true",
  stream: "/api/stream-analyze",
  audit: "/api/audit",
  threats: "/api/threats",
  intel: "/api/intel",
  risk: "/api/risk/score",
  search: "/api/threat/search?q=",
  gateway: "/api/gateway/decide",
  consumer: "/api/consumer/check",
  deployment: "/api/deployment/profile",
  warroom: "/api/warroom",
  verify: "/api/speaker/verify",
};
export async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(config.api + path, {
    ...init,
    signal: init.signal ?? AbortSignal.timeout(8000),
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}
export const api = {
  health: () => request<HealthStatus>(endpoints.health),
  audit: () => request<AuditEvent[]>(endpoints.audit),
  threats: () => request<Threat[]>(endpoints.threats),
  intel: () =>
    request<{ nodes: IntelNode[]; edges: IntelEdge[] }>(endpoints.intel),
  searchThreats: (query: string) =>
    request<Threat[]>(endpoints.search + encodeURIComponent(query)),
  deployment: () =>
    request<{ profile: DeploymentProfile }>(endpoints.deployment),
  warroom: () => request<{ threats: Threat[] }>(endpoints.warroom),
  risk: (input: Record<string, unknown>) =>
    request<ProductRisk>(endpoints.risk, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }),
  gateway: (input: Record<string, unknown>) =>
    request<ProductRisk>(endpoints.gateway, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }),
  consumer: (body: FormData) =>
    request<AnalysisResult>(endpoints.consumer, { method: "POST", body }),
  verifySpeaker: (body: FormData) =>
    request<SpeakerVerification>(endpoints.verify, { method: "POST", body }),
  streamWindow: (body: FormData) =>
    request<AnalysisResult>(endpoints.stream, { method: "POST", body }),
  analyze: async (
    file: File | null,
    scenario: Verdict,
    id: string,
  ): Promise<AnalysisResult> => {
    if (config.demo) return mockAnalysis(scenario, file?.name, id);
    if (!file) throw new Error("Select an audio file for live analysis.");
    const body = new FormData();
    body.append("file", file);
    const result = await request<AnalysisResult>(endpoints.analyze, {
      method: "POST",
      body,
    });
    if (
      !["HUMAN", "SYNTHETIC", "ABSTAIN"].includes(result.verdict) ||
      !Array.isArray(result.detectors) ||
      !Array.isArray(result.reasons) ||
      !Number.isFinite(result.confidence) ||
      result.confidence < 0 ||
      result.confidence > 100 ||
      !Number.isFinite(result.duration) ||
      result.duration <= 0 ||
      ![
        "id",
        "filename",
        "language",
        "channel",
        "timestamp",
        "transcript",
      ].every(
        (k) =>
          typeof (result as unknown as Record<string, unknown>)[k] === "string",
      ) ||
      result.detectors.some(
        (d) =>
          !d ||
          typeof d.name !== "string" ||
          !Number.isFinite(d.score) ||
          typeof d.detail !== "string",
      ) ||
      result.reasons.some((r) => typeof r !== "string")
    )
      throw new Error(
        "Unexpected analysis response. Check the backend contract.",
      );
    return { ...result, source: "live" };
  },
};
export function download(name: string, content: string, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function csv(rows: Record<string, unknown>[]) {
  if (!rows.length) return "";
  const keys = Object.keys(rows[0]);
  const quote = (v: unknown) =>
    '"' + String(v ?? "").replaceAll('"', '""') + '"';
  return [
    keys.map(quote).join(","),
    ...rows.map((r) => keys.map((k) => quote(r[k])).join(",")),
  ].join("\n");
}
