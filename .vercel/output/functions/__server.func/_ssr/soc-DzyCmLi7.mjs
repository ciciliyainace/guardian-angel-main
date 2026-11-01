import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { l as cn } from "./api-D71CZkbx.mjs";
import { N as FlaskConical, a as TrendingUp, o as TrendingDown } from "../_libs/lucide-react.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/soc-DzyCmLi7.js
var import_jsx_runtime = require_jsx_runtime();
var sevStyles = {
	critical: "bg-critical/15 text-critical border-critical/30",
	high: "bg-warning/15 text-warning border-warning/30",
	medium: "bg-info/15 text-info border-info/30",
	low: "bg-muted text-muted-foreground border-border"
};
function SeverityBadge({ severity }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: cn("inline-flex items-center rounded border px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide", sevStyles[severity]),
		children: severity
	});
}
var statusStyles = {
	new: "bg-primary/15 text-primary",
	acknowledged: "bg-info/15 text-info",
	investigating: "bg-warning/15 text-warning",
	resolved: "bg-success/15 text-success",
	pending: "bg-warning/15 text-warning",
	approved: "bg-success/15 text-success",
	rejected: "bg-critical/15 text-critical",
	expired: "bg-muted text-muted-foreground"
};
function StatusPill({ status }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: cn("inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize", statusStyles[status] ?? "bg-muted text-muted-foreground"),
		children: status
	});
}
var healthStyles = {
	Operational: "text-success",
	Degraded: "text-warning",
	Disconnected: "text-muted-foreground",
	Error: "text-critical",
	Unknown: "text-muted-foreground"
};
function HealthBadge({ status }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
		className: cn("inline-flex items-center gap-1.5 text-xs font-medium", healthStyles[status]),
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2 rounded-full bg-current" }), status]
	});
}
function RiskBar({ score }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex items-center gap-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "h-1.5 w-14 overflow-hidden rounded-full bg-muted",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: cn("h-full", score >= 85 ? "bg-critical" : score >= 65 ? "bg-warning" : score >= 40 ? "bg-info" : "bg-muted-foreground"),
				style: { width: `${score}%` }
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "font-mono text-xs tabular-nums",
			children: score
		})]
	});
}
function SimTag({ label = "Simulated" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
		className: "inline-flex items-center gap-1 rounded border border-warning/40 bg-warning/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-warning",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FlaskConical, { className: "size-3" }), label]
	});
}
function PageHeader({ title, description, actions }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mb-6 flex flex-wrap items-end justify-between gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
			className: "text-xl font-semibold tracking-tight",
			children: title
		}), description && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-1 text-sm text-muted-foreground",
			children: description
		})] }), actions && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex flex-wrap gap-2",
			children: actions
		})]
	});
}
function Panel({ title, action, children, className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: cn("soc-panel rounded-lg border bg-card text-card-foreground", className),
		children: [title && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "flex items-center justify-between gap-2 border-b px-4 py-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-sm font-semibold",
				children: title
			}), action]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "p-4",
			children
		})]
	});
}
function StatCard({ icon: Icon, label, value, delta, tone = "primary" }) {
	const toneCls = {
		primary: "text-primary bg-primary/10",
		critical: "text-critical bg-critical/10",
		warning: "text-warning bg-warning/10",
		success: "text-success bg-success/10",
		info: "text-info bg-info/10"
	}[tone];
	const valueCls = {
		primary: "text-value-primary",
		critical: "text-value-critical",
		warning: "text-value-warning",
		success: "text-value-success",
		info: "text-value-info"
	}[tone];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "soc-panel rounded-lg border bg-card p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-xs font-medium text-muted-foreground",
					children: label
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: cn("rounded-md p-1.5", toneCls),
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "size-4" })
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: cn("mt-3 text-2xl font-semibold tabular-nums", valueCls),
				children: value
			}),
			delta !== void 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: cn("mt-1 flex items-center gap-1 text-xs", delta >= 0 ? "text-critical" : "text-success"),
				children: [
					delta >= 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TrendingUp, { className: "size-3" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TrendingDown, { className: "size-3" }),
					Math.abs(delta),
					"% vs previous 24h"
				]
			})
		]
	});
}
var chartTooltip = {
	contentStyle: {
		background: "var(--popover)",
		border: "1px solid var(--border)",
		borderRadius: 8,
		color: "var(--popover-foreground)",
		boxShadow: "var(--shadow-tooltip)",
		fontSize: 12
	},
	itemStyle: { color: "var(--popover-foreground)" },
	cursor: { fill: "color-mix(in oklab, var(--muted) 60%, transparent)" }
};
var axisProps = {
	stroke: "var(--muted-foreground)",
	fontSize: 11,
	tickLine: false,
	axisLine: false
};
//#endregion
export { SeverityBadge as a, StatusPill as c, RiskBar as i, axisProps as l, PageHeader as n, SimTag as o, Panel as r, StatCard as s, HealthBadge as t, chartTooltip as u };
