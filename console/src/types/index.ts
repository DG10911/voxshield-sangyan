export type Verdict = "HUMAN" | "SYNTHETIC" | "ABSTAIN";
export type Mode = "DEMO DATA" | "LIVE API" | "OFFLINE DEMO";
export interface DetectorScore {
  name: string;
  score: number;
  weight: number;
  detail: string;
  version: string;
}
export interface AnalysisResult {
  id: string;
  filename: string;
  verdict: Verdict;
  confidence: number;
  language: string;
  channel: string;
  duration: number;
  timestamp: string;
  detectors: DetectorScore[];
  reasons: string[];
  transcript: string;
  source: "demo" | "live";
  spectrogram?: string;
}
export interface CallRecord extends AnalysisResult {
  analyst: string;
  status: "New" | "In review" | "Resolved";
  threat: string;
}
export interface LanguageMetric {
  name: string;
  native: string;
  iso: string;
  clean: number | null;
  phone: number | null;
  status: "Supplied" | "Pending";
}
export interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  event: string;
  call: string;
  action: string;
  hash: string;
  source: "demo" | "live";
}
export interface Generator {
  id: string;
  name: string;
  family: string;
  seen: boolean;
  risk: string;
  samples: number;
}
export interface Threat {
  id: string;
  generator: string;
  language: string;
  novelty: number;
  confidence: number;
  source: string;
}
export interface Speaker {
  id: string;
  name: string;
  quality: number;
}
export interface SpeakerVerification {
  similarity: number;
  result: "SAME" | "DIFFERENT";
  source: "demo" | "live";
}
export interface TrainingRound {
  id: string;
  language: string;
  epoch: number;
  progress: number;
  status: string;
  gpu: string;
}
export interface Dataset {
  name: string;
  language: string;
  hours: number;
  samples: number;
  license: string;
  storage: string;
  status: string;
}
export type DeploymentProfile =
  "Cloud" | "Enterprise" | "Indic On-Prem" | "Edge";
export interface HealthStatus {
  status: string;
  model: string;
}
export interface IntelNode {
  id: string;
  label: string;
  kind: string;
  x: number;
  y: number;
}
export interface IntelEdge {
  source: string;
  target: string;
}
export interface ProductRisk {
  score: number;
  decision: "ALLOW" | "REVIEW" | "BLOCK";
  source: "demo" | "live";
}
