import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { d as events, i as api, x as trafficSeries } from "./api-D71CZkbx.mjs";
import { l as axisProps, n as PageHeader, o as SimTag, r as Panel, u as chartTooltip } from "./soc-DzyCmLi7.mjs";
import { t as EventsTable } from "./events-table-C2GxLDR-.mjs";
import { a as XAxis, d as ResponsiveContainer, f as Tooltip, i as YAxis, o as Area, s as CartesianGrid, t as AreaChart } from "../_libs/recharts+[...].mjs";
import { t as D } from "./traffic-DbRKwSsb.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/traffic-B-vF3Ibh.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function TrafficPage() {
	const [traffic, setTraffic] = (0, import_react.useState)(trafficSeries);
	const [events$1, setEvents] = (0, import_react.useState)(events);
	const [isLive, setIsLive] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		let mounted = true;
		Promise.all([api.trafficSeries(), api.events()]).then(([t, ev]) => {
			if (!mounted) return;
			setTraffic(t);
			setEvents(ev);
			setIsLive(true);
		}).catch(() => {
			if (mounted) setIsLive(false);
		});
		return () => {
			mounted = false;
		};
	}, []);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
				title: "Live Traffic",
				description: D,
				actions: isLive ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2 rounded-full bg-success" }), " Live stream active"]
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, {})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
				title: "Traffic volume (24h)",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "h-64",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
						data: traffic,
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
								strokeDasharray: "3 3",
								stroke: "var(--border)"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
								dataKey: "time",
								...axisProps
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, { ...axisProps }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
								dataKey: "total",
								stroke: "var(--primary)",
								fill: "var(--primary)",
								fillOpacity: .2
							})
						]
					}) })
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
				title: "Recent flows",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EventsTable, { data: events$1 })
			})
		]
	});
}
//#endregion
export { TrafficPage as component };
