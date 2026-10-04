import { Suspense, lazy, useEffect, useRef, useState } from "react";
import {
  HashRouter,
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  Activity,
  AudioLines,
  Radio,
  Phone,
  Languages as LanguagesIcon,
  BrainCircuit,
  Database,
  ChartNoAxesCombined,
  Radar,
  Fingerprint,
  Layers,
  Network,
  HardDrive,
  Cpu,
  ShieldCheck,
  Settings2,
  GitBranch,
  Search,
  PanelLeftClose,
  Menu,
  ChevronRight,
  Bell,
  CheckCircle2,
} from "lucide-react";
const iconMap: Record<string, LucideIcon> = {
  Activity,
  AudioLines,
  Radio,
  Phone,
  Languages: LanguagesIcon,
  BrainCircuit,
  Database,
  ChartNoAxesCombined,
  Radar,
  Fingerprint,
  Layers,
  Network,
  HardDrive,
  Cpu,
  ShieldCheck,
  Settings2,
  GitBranch,
};
import type { LucideIcon } from "lucide-react";
import { navigation, pages, languages, generators } from "./data/catalog";
import { Chip, Modal, DetailList } from "./components/ui";
import { StoreProvider, useApp, usePreference } from "./store";
const Overview = lazy(() => import("./features/Overview"));
const Analyze = lazy(() => import("./features/Analyze"));
const Live = lazy(() =>
  import("./features/Monitoring").then((m) => ({ default: m.Live })),
);
const Calls = lazy(() =>
  import("./features/Monitoring").then((m) => ({ default: m.Calls })),
);
const Languages = lazy(() =>
  import("./features/Intelligence").then((m) => ({ default: m.Languages })),
);
const Evidence = lazy(() =>
  import("./features/Intelligence").then((m) => ({ default: m.Evidence })),
);
const Registries = lazy(() =>
  import("./features/Intelligence").then((m) => ({ default: m.Registries })),
);
const Results = lazy(() =>
  import("./features/Intelligence").then((m) => ({ default: m.Results })),
);
const Threats = lazy(() =>
  import("./features/Intelligence").then((m) => ({ default: m.Threats })),
);
const Speakers = lazy(() =>
  import("./features/Intelligence").then((m) => ({ default: m.Speakers })),
);
const Products = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Products })),
);
const Integrations = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Integrations })),
);
const Corpus = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Corpus })),
);
const Training = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Training })),
);
const Ops = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Ops })),
);
const Deployment = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Deployment })),
);
const Roadmap = lazy(() =>
  import("./features/Platform").then((m) => ({ default: m.Roadmap })),
);
function CommandPalette({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState(0);
  const navigate = useNavigate();
  const { calls } = useApp();
  const items = [
    ...pages.map(([id, label]) => ({ label, type: "SCREEN", path: "/" + id })),
    ...calls.map((c) => ({
      label: c.id + " · " + c.language,
      type: "CALL",
      path: "/calls?call=" + c.id,
    })),
    ...languages.map((l) => ({
      label: l.name + " model",
      type: "LANGUAGE",
      path: "/languages",
    })),
    ...generators.map((g) => ({
      label: g.name,
      type: "GENERATOR",
      path: "/registries",
    })),
    { label: "Analyze new call", type: "ACTION", path: "/analyze" },
    { label: "Check DGX training", type: "ACTION", path: "/training" },
    { label: "Open deployment profile", type: "ACTION", path: "/deployment" },
    { label: "Search datasets", type: "ACTION", path: "/corpus" },
    { label: "SPK-A941", type: "SPEAKER", path: "/speakers" },
  ]
    .filter((i) => i.label.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 12);
  const run = (path: string) => {
    navigate(path);
    onClose();
  };
  return (
    <Modal title="Where should we look?" onClose={onClose}>
      <div className="command-input">
        <Search size={20} />
        <input
          autoFocus
          role="combobox"
          aria-label="Search commands"
          aria-expanded="true"
          aria-controls="command-results"
          aria-activedescendant={items.length ? "command-" + index : undefined}
          placeholder="Search screens, calls, languages, actions…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIndex(0);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") {
              e.preventDefault();
              setIndex((i) => (i + 1) % Math.max(items.length, 1));
            }
            if (e.key === "ArrowUp") {
              e.preventDefault();
              setIndex(
                (i) => (i - 1 + items.length) % Math.max(items.length, 1),
              );
            }
            if (e.key === "Enter" && items[index]) run(items[index].path);
          }}
        />
      </div>
      <div id="command-results" role="listbox" className="command-results">
        {items.map((item, i) => (
          <button
            id={"command-" + i}
            role="option"
            aria-selected={i === index}
            className={i === index ? "active" : ""}
            key={item.type + item.label}
            onClick={() => run(item.path)}
          >
            <span>{item.label}</span>
            <span className="eyebrow">{item.type} ↵</span>
          </button>
        ))}
        {!items.length && <p>No matching commands.</p>}
      </div>
      <div className="command-help">
        ↑ ↓ Navigate <span>↵ Open</span>
        <span>Esc Close</span>
      </div>
    </Modal>
  );
}
function Shell() {
  const [collapsed, setCollapsed] = usePreference("sidebar-collapsed", false);
  const [motion] = usePreference("reduced-motion", false);
  const [palette, setPalette] = useState(false);
  const [info, setInfo] = useState("");
  const [mobile, setMobile] = useState(false);
  const { mode, toast, calls, retry, busy } = useApp();
  const location = useLocation();
  const navigate = useNavigate();
  const prev = useRef("");
  const page = pages.find((p) => location.pathname === "/" + p[0]) || pages[0];
  const group = navigation.find((g) =>
    g.items.some((p) => p[0] === page[0]),
  )?.group;
  useEffect(() => {
    document.documentElement.classList.toggle("reduce-motion", motion);
  }, [motion]);
  useEffect(() => {
    document.title = page[1] + " — VoxShield";
    setMobile(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement).tagName;
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setPalette((p) => !p);
        return;
      }
      if (
        ["INPUT", "TEXTAREA", "SELECT"].includes(tag) ||
        document.querySelector("dialog[open]")
      )
        return;
      const targets: Record<string, string> = {
        o: "overview",
        a: "analyze",
        l: "live",
        t: "threats",
      };
      if (prev.current === "g" && targets[e.key]) {
        navigate("/" + targets[e.key]);
        prev.current = "";
      } else prev.current = e.key;
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [navigate]);
  return (
    <div
      className={
        "app " + (collapsed ? "collapsed " : "") + (mobile ? "mobile-open" : "")
      }
    >
      <a
        className="skip-link"
        href="#main"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main")?.focus();
        }}
      >
        Skip to content
      </a>
      <aside className="sidebar">
        <Link to="/overview" className="brand">
          <img src="/shield.svg" alt="" />
          <div>
            VOXSHIELD<span>VOICE FRAUD INTELLIGENCE</span>
          </div>
        </Link>
        <div className="workspace">
          <div className="workspace-avatar">VS</div>
          <div>
            <strong>Intelligence workspace</strong>
            <span>Enterprise / Demo environment</span>
          </div>
        </div>
        <nav aria-label="Main navigation">
          {navigation.map((g) => (
            <div className="nav-group" key={g.group}>
              <div className="nav-label">{g.group}</div>
              {g.items.map(([id, label, icon]) => {
                const Icon = iconMap[icon];
                return (
                  <NavLink
                    to={"/" + id}
                    key={id}
                    title={collapsed ? label : undefined}
                  >
                    <Icon size={17} />
                    <span>{label}</span>
                    {id === "live" && <i className="live-dot" />}
                    {id === "threats" && <small>03</small>}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="between">
            <span className="health-light" />
            <span>DGX cluster · simulated</span>
            <span className="mono">4/4</span>
          </div>
          <div className="footer-build">
            <span>DEMO / v0.1.0</span>
            <button
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              onClick={() => setCollapsed(!collapsed)}
            >
              <PanelLeftClose size={16} />
            </button>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <button
            className="mobile-menu icon-button"
            aria-label="Toggle navigation"
            onClick={() => setMobile(!mobile)}
          >
            <Menu size={20} />
          </button>
          <div className="breadcrumb">
            <span>{group}</span>
            <ChevronRight size={12} />
            <strong>{page[1]}</strong>
          </div>
          <button
            className="global-search"
            aria-label="Search intelligence"
            onClick={() => setPalette(true)}
          >
            <Search size={15} />
            <span>Search intelligence</span>
            <kbd>⌘ K</kbd>
          </button>
          <div className="top-status">
            <button
              className="demo-button"
              onClick={() => setInfo("Demo data")}
            >
              <span className="status-dot" />
              {mode}
            </button>
            <span className="api-status">
              <span className="health-light" />
              {mode === "LIVE API"
                ? "API online"
                : mode === "OFFLINE DEMO"
                  ? "API offline"
                  : "9 / 9 detectors"}
            </span>
          </div>
          <button
            className="icon-button notification-button"
            aria-label="Notifications"
            onClick={() => setInfo("Notifications")}
          >
            <Bell size={18} />
            <i />
          </button>
          <button
            className="avatar"
            aria-label="Analyst profile"
            onClick={() => setInfo("Analyst profile")}
          >
            DG
          </button>
        </header>
        {mode === "OFFLINE DEMO" && (
          <div className="offline-banner">
            API offline. Showing labeled sample data.{" "}
            <button disabled={busy} onClick={() => void retry()}>
              {busy ? "Retrying…" : "Retry connection"}
            </button>
          </div>
        )}
        <main id="main" tabIndex={-1} key={location.pathname}>
          <Suspense
            fallback={
              <div className="skeleton-page" aria-label="Loading screen">
                <div />
                <div />
                <div />
              </div>
            }
          >
            <Routes>
              <Route path="/overview" element={<Overview />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/live" element={<Live />} />
              <Route path="/calls" element={<Calls key={location.search} />} />
              <Route path="/languages" element={<Languages />} />
              <Route path="/evidence" element={<Evidence />} />
              <Route path="/registries" element={<Registries />} />
              <Route path="/results" element={<Results />} />
              <Route path="/threats" element={<Threats />} />
              <Route path="/speakers" element={<Speakers />} />
              <Route path="/products" element={<Products />} />
              <Route path="/integrations" element={<Integrations />} />
              <Route path="/corpus" element={<Corpus />} />
              <Route path="/training" element={<Training />} />
              <Route path="/ops" element={<Ops />} />
              <Route path="/deployment" element={<Deployment />} />
              <Route path="/roadmap" element={<Roadmap />} />
              <Route path="*" element={<Navigate to="/overview" replace />} />
            </Routes>
          </Suspense>
          <footer className="main-footer">
            <span>
              <img src="/shield.svg" alt="" /> VOXSHIELD INTELLIGENCE PLATFORM
            </span>
            <span>Evidence first. Certainty earned.</span>
            <span>PROTOTYPE / DEMO TELEMETRY</span>
          </footer>
        </main>
      </div>
      {palette && <CommandPalette onClose={() => setPalette(false)} />}
      <div className={"toast " + (toast ? "visible" : "")} role="status">
        {toast && (
          <>
            <CheckCircle2 size={17} />
            {toast}
          </>
        )}
      </div>
      {info && (
        <Modal title={info} onClose={() => setInfo("")}>
          {info === "Demo data" ? (
            <>
              <Chip tone="cyan">{mode}</Chip>
              <p>
                Demo mode uses deterministic sample data. Uploaded audio is not
                classified in demo mode. Benchmark values marked “supplied” come
                from your specification and are not independently verified.
              </p>
              <p>
                Even with the live API enabled, infrastructure, corpus,
                training, and intelligence pages remain labeled sample surfaces
                until their backend adapters are connected.
              </p>
              <DetailList
                items={[
                  ["Audio retention", "In-memory only"],
                  ["History and audit", "Session only"],
                  ["Preferences", "Local browser storage"],
                ]}
              />
            </>
          ) : info === "Notifications" ? (
            <div className="notifications">
              <p>
                <Chip tone="cyan">SIMULATED</Chip> Nine evidence systems
                available.
              </p>
              <p>
                <Chip tone="amber">REVIEW</Chip>{" "}
                {calls.filter((c) => c.verdict === "ABSTAIN").length} sample
                calls require human review.
              </p>
              <Link to="/calls" className="button" onClick={() => setInfo("")}>
                Open investigation queue
              </Link>
            </div>
          ) : (
            <>
              <div className="profile-avatar">DG</div>
              <h3>D. Goenka</h3>
              <p>Demo analyst · Intelligence workspace</p>
              <DetailList
                items={[
                  ["Role", "Analyst · simulated"],
                  ["Environment", "Local prototype"],
                  ["Authentication", "No production session"],
                ]}
              />
              <Link
                className="button"
                to="/deployment"
                onClick={() => setInfo("")}
              >
                Workspace settings
              </Link>
            </>
          )}
        </Modal>
      )}
    </div>
  );
}
export default function App() {
  return (
    <StoreProvider>
      <HashRouter>
        <Shell />
      </HashRouter>
    </StoreProvider>
  );
}
