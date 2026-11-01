import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { a as auditLogs, d as events, i as api, r as Button, u as downloadCSV } from "./api-D71CZkbx.mjs";
import { R as Download, T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { n as PageHeader, o as SimTag, r as Panel } from "./soc-DzyCmLi7.mjs";
import { t as D } from "./reports-C_ZL2z3W.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/reports-7tTY1bX1.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ReportsPage() {
	const [logs, setLogs] = (0, import_react.useState)(auditLogs);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [isDemo, setIsDemo] = (0, import_react.useState)(false);
	const loadLogs = async () => {
		setLoading(true);
		try {
			const data = await api.auditLogs();
			if (Array.isArray(data) && data.length > 0) setLogs(data);
			setIsDemo(api.isOffline());
		} catch {} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		loadLogs();
	}, []);
	const handleExportCSV = async () => {
		try {
			const liveEvents = await api.events();
			if (liveEvents && liveEvents.length > 0) {
				downloadCSV("events.csv", liveEvents);
				return;
			}
		} catch {}
		downloadCSV("events.csv", events);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "Reports & Logs",
			description: D,
			actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [
					isDemo && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, { label: "Demo Logs" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						variant: "outline",
						size: "sm",
						onClick: handleExportCSV,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "mr-1.5 size-3.5" }), "Events CSV"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "outline",
						size: "sm",
						onClick: () => window.print(),
						children: "Print"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						variant: "outline",
						size: "sm",
						onClick: loadLogs,
						disabled: loading,
						children: [loading && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-1.5 size-3.5 animate-spin" }), "Refresh"]
					})
				]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
			title: "Audit log",
			children: loading && logs.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex h-36 items-center justify-center text-sm text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-2 size-4 animate-spin" }), " Loading audit trail..."]
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "divide-y text-sm",
				children: logs.map((l, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
					className: "py-2 font-mono text-xs",
					children: typeof l === "object" && l !== null ? Object.values(l).map(String).join(" · ") : String(l)
				}, i))
			})
		})]
	});
}
//#endregion
export { ReportsPage as component };
