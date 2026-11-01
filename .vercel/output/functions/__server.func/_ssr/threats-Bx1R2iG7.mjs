import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { d as events, i as api } from "./api-D71CZkbx.mjs";
import { n as PageHeader, o as SimTag, r as Panel } from "./soc-DzyCmLi7.mjs";
import { t as EventsTable } from "./events-table-C2GxLDR-.mjs";
import { t as D } from "./threats-B9brEqXQ.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/threats-Bx1R2iG7.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ThreatsPage() {
	const [events$1, setEvents] = (0, import_react.useState)(events);
	const [isLive, setIsLive] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		let mounted = true;
		api.events().then((res) => {
			if (!mounted) return;
			setEvents(res);
			setIsLive(true);
		}).catch(() => {
			if (mounted) setIsLive(false);
		});
		return () => {
			mounted = false;
		};
	}, []);
	const threats = events$1.filter((e) => e.severity === "critical" || e.severity === "high");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "Threat Detection",
			description: D,
			actions: isLive ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2 rounded-full bg-success" }), " Live detections"]
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, {})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
			title: "Critical & high detections",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EventsTable, {
				data: threats,
				showDuplicates: true
			})
		})]
	});
}
//#endregion
export { ThreatsPage as component };
