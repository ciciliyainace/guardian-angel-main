import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { _ as perClassRecall, h as models, i as api, r as Button, v as sampleMetrics } from "./api-D71CZkbx.mjs";
import { T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { l as axisProps, n as PageHeader, o as SimTag, r as Panel, u as chartTooltip } from "./soc-DzyCmLi7.mjs";
import { t as D } from "./analytics-BUQJ35Gr.mjs";
import { a as XAxis, c as Bar, d as ResponsiveContainer, f as Tooltip, i as YAxis, r as BarChart, s as CartesianGrid } from "../_libs/recharts+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/analytics-CBuyitgQ.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function AnalyticsPage() {
	const [metrics, setMetrics] = (0, import_react.useState)(sampleMetrics);
	const [recallData, setRecallData] = (0, import_react.useState)(perClassRecall);
	const [modelList, setModelList] = (0, import_react.useState)(models);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [isDemo, setIsDemo] = (0, import_react.useState)(false);
	const loadData = async () => {
		setLoading(true);
		try {
			const data = await api.modelMetrics();
			if (data.metrics) setMetrics(data.metrics);
			if (data.perClassRecall) setRecallData(data.perClassRecall);
			if (data.models) setModelList(data.models);
			setIsDemo(api.isOffline());
		} catch {} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		loadData();
	}, []);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
				title: "AI Analytics",
				description: D,
				actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-2",
					children: [isDemo && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, { label: "Sample metrics" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						variant: "outline",
						size: "sm",
						onClick: loadData,
						disabled: loading,
						children: [loading && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-1.5 size-3.5 animate-spin" }), "Refresh"]
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "grid gap-3 sm:grid-cols-3 lg:grid-cols-5",
				children: Object.entries(metrics).map(([k, v]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Panel, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "text-xs uppercase text-muted-foreground",
					children: k
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "font-mono text-2xl",
					children: v
				})] }, k))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
				title: "Per-class recall",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "h-64",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
						data: recallData,
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
								strokeDasharray: "3 3",
								stroke: "var(--border)"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
								dataKey: "cls",
								...axisProps
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
								...axisProps,
								domain: [0, 1]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { ...chartTooltip }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
								dataKey: "recall",
								fill: "var(--primary)",
								radius: 4
							})
						]
					}) })
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "grid gap-3 md:grid-cols-3",
				children: modelList.map((m) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Panel, {
					title: m.name,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-xs text-muted-foreground",
						children: [
							m.version,
							" · ",
							m.dataset
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-2 text-sm",
						children: [
							"Status: ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: m.status === "Loaded" || m.status === "Active" ? "font-medium text-success" : "text-warning",
								children: m.status
							}),
							" · ",
							m.features,
							" features"
						]
					})]
				}, m.name))
			})
		]
	});
}
//#endregion
export { AnalyticsPage as component };
