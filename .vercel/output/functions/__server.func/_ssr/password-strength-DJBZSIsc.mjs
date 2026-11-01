import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { K as Check, t as X } from "../_libs/lucide-react.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/password-strength-DJBZSIsc.js
var import_jsx_runtime = require_jsx_runtime();
function analyzePassword(password) {
	const hasMinLength = password.length >= 8;
	const hasUpper = /[A-Z]/.test(password);
	const hasLower = /[a-z]/.test(password);
	const hasNumberOrSymbol = /[0-9!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password);
	let score = 0;
	if (hasMinLength) score += 1;
	if (hasUpper) score += 1;
	if (hasLower) score += 1;
	if (hasNumberOrSymbol) score += 1;
	let label = "Very Weak";
	let colorClass = "bg-destructive text-destructive";
	if (score === 1) {
		label = "Weak";
		colorClass = "bg-destructive text-destructive";
	} else if (score === 2) {
		label = "Fair";
		colorClass = "bg-warning text-warning";
	} else if (score === 3) {
		label = "Good";
		colorClass = "bg-info text-info";
	} else if (score === 4) {
		label = "Strong";
		colorClass = "bg-success text-success";
	}
	return {
		score,
		label,
		colorClass,
		hasMinLength,
		hasUpper,
		hasLower,
		hasNumberOrSymbol
	};
}
function PasswordStrengthMeter({ password }) {
	if (!password) return null;
	const analysis = analyzePassword(password);
	const percent = analysis.score / 4 * 100;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-2.5 pt-1 text-xs",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-between font-mono text-[11px]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-muted-foreground",
					children: "Password Strength"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: `font-semibold ${analysis.colorClass.split(" ")[1]}`,
					children: analysis.label
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "h-1.5 w-full overflow-hidden rounded-full bg-muted",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: `h-full transition-all duration-300 ${analysis.colorClass.split(" ")[0]}`,
					style: { width: `${percent}%` }
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-2 gap-1.5 pt-1 text-[11px] text-muted-foreground",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-1.5",
						children: [analysis.hasMinLength ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3.5 text-success" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-3.5 text-muted-foreground/60" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "8+ characters" })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-1.5",
						children: [analysis.hasUpper ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3.5 text-success" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-3.5 text-muted-foreground/60" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Uppercase letter" })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-1.5",
						children: [analysis.hasLower ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3.5 text-success" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-3.5 text-muted-foreground/60" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Lowercase letter" })]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-1.5",
						children: [analysis.hasNumberOrSymbol ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3.5 text-success" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-3.5 text-muted-foreground/60" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Number or symbol" })]
					})
				]
			})
		]
	});
}
//#endregion
export { analyzePassword as n, PasswordStrengthMeter as t };
