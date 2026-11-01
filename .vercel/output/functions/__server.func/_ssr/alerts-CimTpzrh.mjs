import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { d as events, i as api } from "./api-D71CZkbx.mjs";
import { n as PageHeader, o as SimTag, r as Panel } from "./soc-DzyCmLi7.mjs";
import { t as D } from "./alerts-CPikK1x6.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { t as EventsTable } from "./events-table-C2GxLDR-.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/alerts-CimTpzrh.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Alerts() {
	const [data, setData] = (0, import_react.useState)(events);
	const [selected, setSelected] = (0, import_react.useState)(/* @__PURE__ */ new Set());
	const [isLive, setIsLive] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		let mounted = true;
		api.events().then((res) => {
			if (!mounted) return;
			setData(res);
			setIsLive(true);
		}).catch(() => {
			if (mounted) setIsLive(false);
		});
		return () => {
			mounted = false;
		};
	}, []);
	const handleStatusChange = (id, s) => {
		setData((d) => d.map((e) => e.id === id ? {
			...e,
			status: s
		} : e));
		api.updateAlertStatus(id, s).then(() => toast.success(`Alert ${id} status updated to ${s}`)).catch((err) => toast.error(`Failed to update status: ${err.message}`));
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "Security Alerts",
			description: D,
			actions: isLive ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2 rounded-full bg-success" }), " Live alerts"]
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, {})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EventsTable, {
			data,
			selectable: true,
			selected,
			onSelectionChange: setSelected,
			onStatusChange: handleStatusChange
		}) })]
	});
}
//#endregion
export { Alerts as component };
