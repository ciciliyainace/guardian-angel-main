import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { b as severityCounts, d as events, f as firewallHistory, i as api, o as blockRequests, p as fmtTime, r as Button, s as categoryCounts, x as trafficSeries } from "./api-D71CZkbx.mjs";
import { F as FileText, M as Gauge, P as Flame, X as BellRing, et as Activity, g as Network, i as TriangleAlert, j as HeartPulse, l as ShieldBan } from "../_libs/lucide-react.mjs";
import { a as SeverityBadge, l as axisProps, n as PageHeader, o as SimTag, r as Panel, s as StatCard, u as chartTooltip } from "./soc-DzyCmLi7.mjs";
import { t as EventsTable } from "./events-table-C2GxLDR-.mjs";
import { a as XAxis, c as Bar, d as ResponsiveContainer, f as Tooltip, i as YAxis, l as Pie, n as PieChart, o as Area, p as Legend, r as BarChart, s as CartesianGrid, t as AreaChart, u as Cell } from "../_libs/recharts+[...].mjs";
import { b as Link } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-Dy8MHKDB.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var sevColor = {
	critical: "var(--chart-4)",
	high: "var(--chart-3)",
	medium: "var(--chart-5)",
	low: "var(--chart-2)"
};
function Overview() {
	const [events$1, setEvents] = (0, import_react.useState)(events);
	const [trafficSeries$1, setTrafficSeries] = (0, import_react.useState)(trafficSeries);
	const [categoryCounts$1, setCategoryCounts] = (0, import_react.useState)(categoryCounts);
	const [severityCounts$1, setSeverityCounts] = (0, import_react.useState)(severityCounts);
	const [firewallHistory$1, setFirewallHistory] = (0, import_react.useState)(firewallHistory);
	const [summary, setSummary] = (0, import_react.useState)(null);
	const [isLive, setIsLive] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		let mounted = true;
		Promise.all([
			api.overviewSummary(),
			api.trafficSeries(),
			api.categoryCounts(),
			api.severityCounts(),
			api.firewallHistory(),
			api.events()
		]).then(([s, t, c, sev, f, ev]) => {
			if (!mounted) return;
			setSummary(s);
			setTrafficSeries(t);
			setCategoryCounts(c);
			setSeverityCounts(sev);
			setFirewallHistory(f);
			setEvents(ev);
			setIsLive(true);
		}).catch(() => {
			if (mounted) setIsLive(false);
		});
		return () => {
			mounted = false;
		};
	}, []);
	const total = summary ? summary.totalEvents : trafficSeries$1.reduce((a, b) => a + b.total, 0);
	const benign = trafficSeries$1.reduce((a, b) => a + b.benign, 0);
	const active = summary ? summary.activeAlerts : events$1.filter((e) => e.status !== "resolved").length;
	const critical = summary ? summary.criticalThreats : events$1.filter((e) => e.severity === "critical").length;
	const suspicious = summary ? summary.suspiciousConnections : total - benign;
	const blocks = summary ? summary.managedBlocks : blockRequests.filter((b) => b.status === "approved").length;
	const donut = [{
		name: "Benign",
		value: benign
	}, {
		name: "Suspicious",
		value: Math.max(0, total - benign)
	}];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
				title: "Security Overview",
				description: "Last 24 hours across monitored network segments.",
				actions: isLive ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2 rounded-full bg-success" }), " Live backend connected"]
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, { label: "Simulated data" })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						icon: Network,
						label: "Total network events",
						value: total.toLocaleString("en-US"),
						delta: summary?.eventsDelta ?? 6
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						icon: BellRing,
						label: "Active alerts",
						value: String(active),
						delta: summary?.alertsDelta ?? 12,
						tone: "warning"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						icon: TriangleAlert,
						label: "Critical threats",
						value: String(critical),
						delta: summary?.threatsDelta ?? -4,
						tone: "critical"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						icon: Activity,
						label: "Suspicious connections",
						value: suspicious.toLocaleString("en-US"),
						delta: summary?.suspiciousDelta ?? 9,
						tone: "info"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						icon: ShieldBan,
						label: "Managed firewall blocks",
						value: String(blocks),
						tone: "success"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatCard, {
						icon: Gauge,
						label: "Detection recall (sample eval)",
						value: summary?.detectionRecall ?? "91%",
						tone: "primary"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-4 lg:grid-cols-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
					title: "Network traffic over time",
					className: "lg:col-span-2",
					action: !isLive ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, {}) : void 0,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-64",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
							data: trafficSeries$1,
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("defs", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
									id: "gb",
									x1: "0",
									y1: "0",
									x2: "0",
									y2: "1",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
										offset: "0%",
										stopColor: "var(--chart-1)",
										stopOpacity: .35
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
										offset: "100%",
										stopColor: "var(--chart-1)",
										stopOpacity: 0
									})]
								}) }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
									stroke: "var(--border)",
									vertical: false
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
									dataKey: "time",
									...axisProps
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
									...axisProps,
									width: 40
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
									type: "monotone",
									dataKey: "benign",
									stroke: "var(--chart-1)",
									fill: "url(#gb)",
									strokeWidth: 2
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
									type: "monotone",
									dataKey: "suspicious",
									stroke: "var(--chart-4)",
									fill: "var(--chart-4)",
									fillOpacity: .15,
									strokeWidth: 2
								})
							]
						}) })
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
					title: "Benign vs suspicious",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-64",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(PieChart, { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Pie, {
								data: donut,
								dataKey: "value",
								innerRadius: 60,
								outerRadius: 90,
								paddingAngle: 2,
								stroke: "none",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, { fill: "var(--chart-1)" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, { fill: "var(--chart-4)" })]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, {
								wrapperStyle: { fontSize: 12 },
								formatter: (value) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted-foreground",
									children: value
								})
							})
						] }) })
					})
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-4 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Attack categories",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-60",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
								data: categoryCounts$1,
								layout: "vertical",
								margin: { left: 20 },
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										type: "number",
										...axisProps
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										type: "category",
										dataKey: "category",
										...axisProps,
										width: 120
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
										dataKey: "count",
										fill: "var(--chart-1)",
										radius: [
											0,
											4,
											4,
											0
										]
									})
								]
							}) })
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Alert severity distribution",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-60",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
								data: severityCounts$1,
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										dataKey: "severity",
										...axisProps
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										...axisProps,
										width: 30
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
										dataKey: "count",
										radius: [
											4,
											4,
											0,
											0
										],
										children: severityCounts$1.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, { fill: sevColor[s.severity] || "var(--chart-1)" }, s.severity))
									})
								]
							}) })
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Firewall action history",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-60",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
								data: firewallHistory$1,
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										dataKey: "day",
										...axisProps
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										...axisProps,
										width: 25
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, { wrapperStyle: { fontSize: 11 } }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
										dataKey: "approved",
										stackId: "a",
										fill: "var(--chart-2)"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
										dataKey: "rejected",
										stackId: "a",
										fill: "var(--chart-4)"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
										dataKey: "expired",
										stackId: "a",
										fill: "var(--chart-5)",
										radius: [
											4,
											4,
											0,
											0
										]
									})
								]
							}) })
						})
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-4 lg:grid-cols-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
					title: "Recent threat activity",
					className: "lg:col-span-1",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
						className: "relative space-y-4 border-l pl-4",
						children: events$1.filter((e) => e.severity !== "low").slice(0, 6).map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "text-xs",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "absolute -left-1 mt-1 size-2 rounded-full bg-primary" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-2 font-medium",
									children: [
										e.category,
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SeverityBadge, { severity: e.severity })
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "font-mono text-muted-foreground",
									children: [
										e.sourceIp,
										" · ",
										fmtTime(e.timestamp).slice(11)
									]
								})
							]
						}, e.id))
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Panel, {
					title: "Quick actions",
					className: "lg:col-span-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "grid gap-2 sm:grid-cols-2 lg:grid-cols-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								asChild: true,
								variant: "outline",
								className: "justify-start",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
									to: "/alerts",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BellRing, {}), "View all alerts"]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								asChild: true,
								variant: "outline",
								className: "justify-start",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
									to: "/firewall",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Flame, {}), "Review block requests"]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								asChild: true,
								variant: "outline",
								className: "justify-start",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
									to: "/reports",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FileText, {}), "Generate report"]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								asChild: true,
								variant: "outline",
								className: "justify-start",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
									to: "/health",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(HeartPulse, {}), "Open system health"]
								})
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 text-xs text-muted-foreground",
						children: "The interface never executes security actions directly — all actions route through an authorized backend once connected."
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
				title: "Recent security events",
				action: !isLive ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, {}) : void 0,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EventsTable, { data: events$1 })
			})
		]
	});
}
//#endregion
export { Overview as component };
