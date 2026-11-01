import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { i as api, r as Button } from "./api-D71CZkbx.mjs";
import { T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { n as PageHeader, o as SimTag, r as Panel, t as HealthBadge } from "./soc-DzyCmLi7.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { t as D } from "./health-BHIOTu6C.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/health-BCG10ccJ.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function HealthPage() {
	const [servicesList, setServicesList] = (0, import_react.useState)([]);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [testing, setTesting] = (0, import_react.useState)(false);
	const [isDemo, setIsDemo] = (0, import_react.useState)(false);
	const loadHealth = async () => {
		setLoading(true);
		try {
			const data = await api.services();
			setServicesList(data);
			setIsDemo(api.isOffline());
		} catch {
			toast.error("Failed to load health status from backend");
		} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		loadHealth();
	}, []);
	const handleTestConnection = async () => {
		setTesting(true);
		try {
			await api.testConnection();
			toast.success("Backend connection verified");
			await loadHealth();
		} catch (e) {
			const msg = e instanceof Error ? e.message : "Connection failed";
			toast.error(msg);
		} finally {
			setTesting(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "System Health",
			description: D,
			actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [isDemo && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, { label: "Demo Health" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "outline",
					disabled: testing || loading,
					onClick: handleTestConnection,
					children: [testing ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-1.5 size-3.5 animate-spin" }) : null, "Test connection"]
				})]
			})
		}), loading && servicesList.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex h-48 items-center justify-center text-sm text-muted-foreground",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-2 size-4 animate-spin" }), " Checking system services..."]
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "grid gap-3 md:grid-cols-2",
			children: servicesList.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Panel, {
				title: s.name,
				action: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HealthBadge, { status: s.status }),
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-sm text-muted-foreground",
					children: s.detail
				}), s.error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-1 font-mono text-xs text-critical",
					children: s.error
				})]
			}, s.name))
		})]
	});
}
//#endregion
export { HealthPage as component };
