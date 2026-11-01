import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { i as api, l as cn, r as Button } from "./api-D71CZkbx.mjs";
import { T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { a as SeverityBadge, n as PageHeader, o as SimTag, r as Panel } from "./soc-DzyCmLi7.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { t as D } from "./rules-DcqoKzuQ.mjs";
import { n as SwitchThumb, t as Switch$1 } from "../_libs/radix-ui__react-switch.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/rules-7wzeVpUG.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Switch = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Switch$1, {
	className: cn("peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input", className),
	...props,
	ref,
	children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SwitchThumb, { className: cn("pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0") })
}));
Switch.displayName = Switch$1.displayName;
function Rules() {
	const [rules, setRules] = (0, import_react.useState)([]);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [isDemo, setIsDemo] = (0, import_react.useState)(false);
	const [updatingId, setUpdatingId] = (0, import_react.useState)(null);
	const loadRules = async () => {
		setLoading(true);
		try {
			const data = await api.rules();
			setRules(data);
			setIsDemo(api.isOffline());
		} catch {
			toast.error("Failed to load detection rules from backend");
		} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		loadRules();
	}, []);
	const handleToggle = async (rule, enabled) => {
		setUpdatingId(rule.id);
		setRules((all) => all.map((x) => x.id === rule.id ? {
			...x,
			enabled
		} : x));
		try {
			await api.toggleRule(rule.id, enabled);
			toast.success(`Rule ${rule.id} ${enabled ? "enabled" : "disabled"}`);
		} catch (err) {
			setRules((all) => all.map((x) => x.id === rule.id ? {
				...x,
				enabled: !enabled
			} : x));
			const msg = err instanceof Error ? err.message : "Failed to toggle rule";
			toast.error(msg);
		} finally {
			setUpdatingId(null);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "Detection Rules",
			description: D,
			actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [isDemo && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, { label: "Demo Rules" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "outline",
					size: "sm",
					onClick: loadRules,
					disabled: loading,
					children: [loading && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-1.5 size-3.5 animate-spin" }), "Refresh"]
				})]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "grid gap-3",
			children: loading && rules.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex h-36 items-center justify-center text-sm text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-2 size-4 animate-spin" }), " Loading rules..."]
			}) : rules.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "py-8 text-center text-sm text-muted-foreground",
				children: "No detection rules configured."
			}) : rules.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-0 flex-1",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-2 font-medium",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs text-muted-foreground",
								children: r.id
							}),
							r.name,
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SeverityBadge, { severity: r.severity })
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-sm text-muted-foreground",
						children: [
							r.description,
							" · threshold ",
							r.threshold,
							" / ",
							r.windowSec,
							"s · ",
							r.matches,
							" matches"
						]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Switch, {
					"aria-label": `Toggle ${r.name}`,
					checked: r.enabled,
					disabled: updatingId === r.id,
					onCheckedChange: (v) => handleToggle(r, v)
				})]
			}) }, r.id))
		})]
	});
}
//#endregion
export { Rules as component };
