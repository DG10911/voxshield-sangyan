import { Context } from "./store-context";
import { useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { AnalysisResult, AuditEvent, CallRecord, Mode } from "./types";
import { initialAudit, initialCalls } from "./services/mock";
import { api, config } from "./services/api";
export function usePreference<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      return (
        JSON.parse(localStorage.getItem("vox." + key) || "null") ?? initial
      );
    } catch {
      return initial;
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem("vox." + key, JSON.stringify(value));
    } catch {}
  }, [key, value]);
  return [value, setValue] as const;
}
function useStore() {
  const [calls, setCalls] = useState(initialCalls);
  const [audit, setAudit] = useState(initialAudit);
  const [mode, setMode] = useState<Mode>(
    config.demo ? "DEMO DATA" : "LIVE API",
  );
  const [toast, setToast] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [busy, setBusy] = useState(false);
  const notify = (s: string) => setToast(s);
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(""), 4500);
      return () => clearTimeout(t);
    }
  }, [toast]);
  const log = (event: string, call = "—", action = "Recorded") =>
    setAudit((a) => [
      {
        id: `AUD-${Date.now()}`,
        timestamp: new Date().toISOString(),
        actor: "demo-analyst",
        event,
        call,
        action,
        hash: "sim-" + Date.now().toString(16),
        source: "demo",
      },
      ...a,
    ]);
  const addResult = (r: AnalysisResult) => {
    setResult(r);
    setCalls((c) => [
      {
        ...r,
        analyst: "D. Goenka",
        status: "New",
        threat: r.verdict === "SYNTHETIC" ? "GEN-UNK-04" : "Unattributed",
      },
      ...c,
    ]);
    setAudit((a) => [
      {
        id: `AUD-${Date.now()}`,
        timestamp: r.timestamp,
        actor: r.source === "demo" ? "demo-analyst" : "analyst",
        event: "analysis.completed",
        call: r.id,
        action: r.verdict,
        hash: "sim-" + Date.now().toString(16),
        source: r.source,
      },
      ...a,
    ]);
    notify("Analysis complete · " + r.verdict);
  };
  const retry = async () => {
    if (config.demo) {
      notify("Demo mode is enabled in environment configuration.");
      return;
    }
    setBusy(true);
    try {
      await api.health();
      setMode("LIVE API");
      notify("API reconnected");
    } catch {
      setMode("OFFLINE DEMO");
      notify("API unavailable · deterministic demo is active");
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    if (!config.demo) void retry();
  }, []);
  return {
    calls,
    audit,
    mode,
    setMode,
    toast,
    notify,
    result,
    addResult,
    log,
    retry,
    busy,
    review: (id: string, status: CallRecord["status"]) => {
      setCalls((c) => c.map((x) => (x.id === id ? { ...x, status } : x)));
      log("review.updated", id, status);
    },
  };
}
export type AppStore = ReturnType<typeof useStore>;
export function StoreProvider({ children }: { children: ReactNode }) {
  const value = useStore();
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useApp() {
  const c = useContext(Context);
  if (!c) throw new Error("Store provider missing");
  return c;
}
