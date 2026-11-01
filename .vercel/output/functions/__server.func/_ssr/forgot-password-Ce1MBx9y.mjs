import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { $ as ArrowLeft, H as CircleAlert, V as CircleCheck, b as Mail, k as KeyRound } from "../_libs/lucide-react.mjs";
import { t as Input } from "./input-DF0EQrhe.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
import { b as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as AuthLayout } from "./auth-layout-0M7xX-2G.mjs";
import { t as Label } from "./label-C3qa2Vlq.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/forgot-password-Ce1MBx9y.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ForgotPasswordPage() {
	const { forgotPassword } = useAuth();
	const [email, setEmail] = (0, import_react.useState)("");
	const [isLoading, setIsLoading] = (0, import_react.useState)(false);
	const [isSubmitted, setIsSubmitted] = (0, import_react.useState)(false);
	const [errorMessage, setErrorMessage] = (0, import_react.useState)(null);
	const handleSubmit = async (e) => {
		e.preventDefault();
		setErrorMessage(null);
		if (!email.trim()) {
			setErrorMessage("Please enter your registered email address.");
			return;
		}
		try {
			setIsLoading(true);
			await forgotPassword(email.trim().toLowerCase());
			setIsSubmitted(true);
			toast.success("Reset Request Dispatched", { description: "If an account with that email exists, reset instructions have been dispatched." });
		} catch (err) {
			setErrorMessage(err.message || "Failed to submit password reset request.");
		} finally {
			setIsLoading(false);
		}
	};
	if (isSubmitted) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Check Your Email",
		subtitle: "Password reset instructions have been dispatched",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-5 text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mx-auto flex size-14 items-center justify-center rounded-full bg-primary/15 text-primary",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-8" })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "text-base font-semibold text-foreground",
						children: "Reset Instructions Dispatched"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "text-xs text-muted-foreground leading-relaxed",
						children: [
							"If an active account exists for ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono font-semibold text-primary",
								children: email
							}),
							", a secure single-use reset link has been dispatched."
						]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-lg border border-border/70 bg-muted/30 p-3.5 text-left text-xs text-muted-foreground space-y-1.5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "• The reset link is single-use and will expire in 30 minutes." }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "• If you don't receive an email within 5 minutes, verify your spam folder." }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "• Never share password reset links with anyone." })
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "pt-2",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
						to: "/login",
						className: "inline-flex w-full items-center justify-center gap-2 rounded-md bg-secondary py-2 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "size-3.5" }), " Return to Login"]
					})
				})
			]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Reset Account Password",
		subtitle: "Enter your email to receive a secure password recovery link",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
			onSubmit: handleSubmit,
			className: "space-y-4",
			children: [
				errorMessage && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "mt-0.5 size-4 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "leading-relaxed",
						children: errorMessage
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
						htmlFor: "reset-email",
						className: "text-xs font-medium",
						children: "Account Email Address"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Mail, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "reset-email",
							type: "email",
							autoComplete: "email",
							placeholder: "e.g. analyst@sentinelai.local",
							value: email,
							onChange: (e) => setEmail(e.target.value),
							className: "pl-9 text-sm",
							disabled: isLoading,
							required: true
						})]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "submit",
					disabled: isLoading,
					className: "w-full gap-2 font-semibold shadow-sm transition-all",
					children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" }), "Dispatching Instructions..."]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KeyRound, { className: "size-4" }), " Send Recovery Link"] })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "pt-2 text-center text-xs",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
						to: "/login",
						className: "inline-flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-foreground",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "size-3.5" }), " Back to Login"]
					})
				})
			]
		})
	});
}
//#endregion
export { ForgotPasswordPage as component };
