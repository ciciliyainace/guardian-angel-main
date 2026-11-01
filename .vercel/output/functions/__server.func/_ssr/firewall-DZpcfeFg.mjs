import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { i as api, p as fmtTime, r as Button } from "./api-D71CZkbx.mjs";
import { T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { c as StatusPill, n as PageHeader, o as SimTag, r as Panel } from "./soc-DzyCmLi7.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { t as D } from "./firewall-ABLH8dZq.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/firewall-DZpcfeFg.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function Firewall() {
	const [reqs, setReqs] = (0, import_react.useState)([]);
	const [loading, setLoading] = (0, import_react.useState)(true);
	const [isDemo, setIsDemo] = (0, import_react.useState)(false);
	const [submittingId, setSubmittingId] = (0, import_react.useState)(null);
	const loadRequests = async () => {
		setLoading(true);
		try {
			const data = await api.blockRequests();
			setReqs(data);
			setIsDemo(api.isOffline());
		} catch {
			toast.error("Failed to load block requests from backend");
		} finally {
			setLoading(false);
		}
	};
	(0, import_react.useEffect)(() => {
		loadRequests();
	}, []);
	const set = async (id, status) => {
		setSubmittingId(id);
		try {
			if (status === "approved") {
				await api.approveBlock(id, "Approved via SentinelAI console");
				toast.success(`${id} approved successfully`);
			} else {
				await api.rejectBlock(id, "Rejected via SentinelAI console");
				toast.info(`${id} rejected`);
			}
			setReqs((r) => r.map((x) => x.id === id ? {
				...x,
				status
			} : x));
		} catch (err) {
			const msg = err instanceof Error ? err.message : "Failed to update block request";
			toast.error(msg);
		} finally {
			setSubmittingId(null);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "Firewall Management",
			description: D,
			actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [isDemo && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SimTag, { label: "Demo Data" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "outline",
					size: "sm",
					onClick: loadRequests,
					disabled: loading,
					children: [loading && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-1.5 size-3.5 animate-spin" }), "Refresh"]
				})]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, { children: loading && reqs.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex h-36 items-center justify-center text-sm text-muted-foreground",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-2 size-4 animate-spin" }), " Loading block requests..."]
		}) : reqs.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "py-8 text-center text-sm text-muted-foreground",
			children: "No block requests found. All incoming traffic normal."
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "overflow-x-auto",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
				className: "w-full text-sm",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
					className: "text-left text-xs text-muted-foreground",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							className: "p-2",
							children: "ID"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", { children: "Source IP" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", { children: "Reason" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", { children: "Requested" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", { children: "Status" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {})
					] })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: reqs.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
					className: "border-t",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "p-2 font-mono text-xs",
							children: r.id
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "font-mono",
							children: r.sourceIp
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", { children: r.reason }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "font-mono text-xs",
							children: fmtTime(r.requestedAt)
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusPill, { status: r.status }) }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "space-x-1 text-right",
							children: r.status === "pending" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								disabled: submittingId === r.id,
								onClick: () => set(r.id, "approved"),
								children: submittingId === r.id ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-3 animate-spin" }) : "Approve"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								variant: "outline",
								disabled: submittingId === r.id,
								onClick: () => set(r.id, "rejected"),
								children: "Reject"
							})] })
						})
					]
				}, r.id)) })]
			})
		}) })]
	});
}
//#endregion
export { Firewall as component };
