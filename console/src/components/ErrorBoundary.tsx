import { Component } from "react";
import type { ReactNode, ErrorInfo } from "react";
export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("VoxShield view error", error, info.componentStack);
  }
  render() {
    if (this.state.failed)
      return (
        <main>
          <div className="panel padded" role="alert">
            <span className="eyebrow">VIEW UNAVAILABLE</span>
            <h1>The console needs a fresh start.</h1>
            <p>
              Local preferences are preserved. Session-only analysis results
              will reset when you reload.
            </p>
            <button
              className="primary"
              onClick={() => window.location.reload()}
            >
              Reload console
            </button>
          </div>
        </main>
      );
    return this.props.children;
  }
}
