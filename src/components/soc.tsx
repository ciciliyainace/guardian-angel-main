import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp, FlaskConical } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Severity, HealthStatus } from "@/lib/mock-data";

const sevStyles: Record<Severity, string> = {
  critical: "bg-critical/15 text-critical border-critical/30",
  high: "bg-warning/15 text-warning border-warning/30",
  medium: "bg-info/15 text-info border-info/30",
  low: "bg-muted text-muted-foreground border-border",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={cn("inline-flex items-center rounded border px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide", sevStyles[severity])}>
      {severity}
    </span>
  );
}

const statusStyles: Record<string, string> = {
  new: "bg-primary/15 text-primary",
  acknowledged: "bg-info/15 text-info",
  investigating: "bg-warning/15 text-warning",
  resolved: "bg-success/15 text-success",
  pending: "bg-warning/15 text-warning",
  approved: "bg-success/15 text-success",
  rejected: "bg-critical/15 text-critical",
  expired: "bg-muted text-muted-foreground",
};

export function StatusPill({ status }: { status: string }) {
  return (
    <span className={cn("inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize", statusStyles[status] ?? "bg-muted text-muted-foreground")}>
      {status}
    </span>
  );
}

const healthStyles: Record<HealthStatus, string> = {
  Operational: "text-success",
  Degraded: "text-warning",
  Disconnected: "text-muted-foreground",
  Error: "text-critical",
  Unknown: "text-muted-foreground",
};
export function HealthBadge({ status }: { status: HealthStatus }) {
  return (
    <span className={cn("inline-flex items-center gap-1.5 text-xs font-medium", healthStyles[status])}>
      <span className="size-2 rounded-full bg-current" />
      {status}
    </span>
  );
}

export function RiskBar({ score }: { score: number }) {
  const color = score >= 85 ? "bg-critical" : score >= 65 ? "bg-warning" : score >= 40 ? "bg-info" : "bg-muted-foreground";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-14 overflow-hidden rounded-full bg-muted">
        <div className={cn("h-full", color)} style={{ width: `${score}%` }} />
      </div>
      <span className="font-mono text-xs tabular-nums">{score}</span>
    </div>
  );
}

export function SimTag({ label = "Simulated" }: { label?: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded border border-warning/40 bg-warning/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-warning">
      <FlaskConical className="size-3" />
      {label}
    </span>
  );
}

export function PageHeader({ title, description, actions }: { title: string; description?: string; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function Panel({ title, action, children, className }: { title?: ReactNode; action?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={cn("soc-panel rounded-lg border bg-card text-card-foreground", className)}>
      {title && (
        <header className="flex items-center justify-between gap-2 border-b px-4 py-3">
          <h2 className="text-sm font-semibold">{title}</h2>
          {action}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}

export function StatCard({ icon: Icon, label, value, delta, tone = "primary" }: { icon: LucideIcon; label: string; value: string; delta?: number; tone?: "primary" | "critical" | "warning" | "success" | "info" }) {
  const toneCls = { primary: "text-primary bg-primary/10", critical: "text-critical bg-critical/10", warning: "text-warning bg-warning/10", success: "text-success bg-success/10", info: "text-info bg-info/10" }[tone];
  const valueCls = { primary: "text-value-primary", critical: "text-value-critical", warning: "text-value-warning", success: "text-value-success", info: "text-value-info" }[tone];
  return (
    <div className="soc-panel rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span className={cn("rounded-md p-1.5", toneCls)}><Icon className="size-4" /></span>
      </div>
      <div className={cn("mt-3 text-2xl font-semibold tabular-nums", valueCls)}>{value}</div>
      {delta !== undefined && (
        <div className={cn("mt-1 flex items-center gap-1 text-xs", delta >= 0 ? "text-critical" : "text-success")}>
          {delta >= 0 ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
          {Math.abs(delta)}% vs previous 24h
        </div>
      )}
    </div>
  );
}

export const chartTooltip = {
  contentStyle: {
    background: "var(--popover)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    color: "var(--popover-foreground)",
    boxShadow: "var(--shadow-tooltip)",
    fontSize: 12,
  },
  itemStyle: { color: "var(--popover-foreground)" },
  cursor: { fill: "color-mix(in oklab, var(--muted) 60%, transparent)" },
};
export const axisProps = { stroke: "var(--muted-foreground)", fontSize: 11, tickLine: false, axisLine: false } as const;
