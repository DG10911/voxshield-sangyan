import { useEffect, useRef, useState, useId } from "react";
import type { ReactNode } from "react";
import { X, ArrowUpRight, Download, Copy, Check } from "lucide-react";
import { csv, download } from "../services/api";
export function Chip({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return (
    <span className={"chip " + tone}>
      <span className="status-dot" />
      {children}
    </span>
  );
}
export function Panel({
  title,
  eyebrow,
  action,
  children,
  className = "",
}: {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={"panel " + className}>
      {(title || action) && (
        <header className="panel-head">
          <div>
            {eyebrow && <span className="eyebrow">{eyebrow}</span>}
            <h2>{title}</h2>
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}
export function PageHeader({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <header className="page-head">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>
          {title.replace(/\.$/, "")}
          <span className="title-dot">.</span>
        </h1>
        <p>{description}</p>
      </div>
      <div className="actions">{children}</div>
    </header>
  );
}
export function ExportButton({
  rows,
  name = "voxshield-export",
}: {
  rows: object[];
  name?: string;
}) {
  return (
    <button
      onClick={() =>
        download(
          name + ".csv",
          csv(rows as Record<string, unknown>[]),
          "text/csv",
        )
      }
    >
      <Download size={15} /> Export CSV
    </button>
  );
}
export function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        } catch {
          setCopied(false);
        }
      }}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}{" "}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}
export function Empty({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="empty">
      <span className="empty-signal">∿</span>
      <h3>{title}</h3>
      <p>{detail}</p>
    </div>
  );
}
export function Modal({
  title,
  children,
  onClose,
  drawer = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  drawer?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    ref.current?.showModal();
    return () => previous?.focus();
  }, []);
  return (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      className={drawer ? "drawer" : "modal"}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="modal-head">
        <div>
          <span className="eyebrow">VOXSHIELD / INSPECTOR</span>
          <h2 id={titleId}>{title}</h2>
        </div>
        <button
          className="icon-button"
          aria-label="Close dialog"
          onClick={onClose}
        >
          <X size={20} />
        </button>
      </div>
      <div className="modal-body">{children}</div>
    </dialog>
  );
}
export function Tabs({
  items,
  value,
  onChange,
}: {
  items: string[];
  value: string;
  onChange: (s: string) => void;
}) {
  return (
    <div className="tabs" aria-label="View">
      {items.map((s) => (
        <button
          key={s}
          aria-pressed={s === value}
          className={s === value ? "active" : ""}
          onClick={() => onChange(s)}
        >
          {s}
        </button>
      ))}
    </div>
  );
}
export function DataTable({
  headers,
  rows,
  onRow,
}: {
  headers: string[];
  rows: ReactNode[][];
  onRow?: (i: number) => void;
}) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((v, j) => (
                <td key={j}>
                  {j === 0 && onRow ? (
                    <button className="table-link" onClick={() => onRow(i)}>
                      {v}
                      <ArrowUpRight size={12} />
                    </button>
                  ) : (
                    v
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length && (
        <Empty
          title="No matching records"
          detail="Adjust the current filters to broaden your search."
        />
      )}
    </div>
  );
}
export function DetailList({ items }: { items: [string, ReactNode][] }) {
  return (
    <dl className="detail-list">
      {items.map(([k, v]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd>{v}</dd>
        </div>
      ))}
    </dl>
  );
}
export function Bar({
  value,
  tone = "cyan",
  label,
}: {
  value: number;
  tone?: string;
  label?: string;
}) {
  return (
    <div className="bar-block">
      {label && (
        <div className="between">
          <span>{label}</span>
          <span className="mono">{value}%</span>
        </div>
      )}
      <div className="bar-track">
        <div className={"bar-fill " + tone} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
