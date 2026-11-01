import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { H as CircleAlert, Q as ArrowRight, T as LoaderCircle, V as CircleCheck, x as MailCheck } from "../_libs/lucide-react.mjs";
import { t as Input } from "./input-DF0EQrhe.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
import { b as Link, x as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as AuthLayout } from "./auth-layout-0M7xX-2G.mjs";
import { t as Label } from "./label-C3qa2Vlq.mjs";
import { t as Route } from "./verify-email-DZq8r-RM.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/verify-email-Cs0DhtUP.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function VerifyEmailPage() {
	const { verifyEmail, resendVerification } = useAuth();
	const search = Route.useSearch();
	const navigate = useNavigate();
	const [token, setToken] = (0, import_react.useState)(search.token || "");
	const [resendEmail, setResendEmail] = (0, import_react.useState)("");
	const [isVerifying, setIsVerifying] = (0, import_react.useState)(false);
	const [isSuccess, setIsSuccess] = (0, import_react.useState)(false);
	const [errorMessage, setErrorMessage] = (0, import_react.useState)(null);
	const [resendStatus, setResendStatus] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		if (search.token && !isSuccess && !isVerifying && !errorMessage) handleAutoVerify(search.token);
	}, [search.token]);
	const handleAutoVerify = async (tok) => {
		try {
			setIsVerifying(true);
			setErrorMessage(null);
			await verifyEmail(tok);
			setIsSuccess(true);
			toast.success("Email Verified", { description: "Your email address has been verified successfully." });
		} catch (err) {
			setErrorMessage(err.message || "Invalid or expired verification token.");
		} finally {
			setIsVerifying(false);
		}
	};
	const handleManualSubmit = (e) => {
		e.preventDefault();
		if (!token.trim()) return;
		handleAutoVerify(token.trim());
	};
	const handleResend = async (e) => {
		e.preventDefault();
		if (!resendEmail.trim()) return;
		try {
			setResendStatus("sending");
			const res = await resendVerification(resendEmail.trim());
			setResendStatus("sent");
			toast.info("Verification Dispatched", { description: res.message || "Verification email has been sent." });
		} catch (err) {
			const e = err;
			setResendStatus(null);
			toast.error("Resend Failed", { description: e.message || "Could not resend verification email." });
		}
	};
	if (isVerifying) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Verifying Email",
		subtitle: "Cryptographically validating your verification token with SentinelAI",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col items-center justify-center py-8 text-center space-y-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-10 animate-spin text-primary" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-xs text-muted-foreground font-mono",
				children: "Validating single-use token in MongoDB Atlas..."
			})]
		})
	});
	if (isSuccess) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Email Verified Successfully",
		subtitle: "Your SentinelAI account identity has been confirmed",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-5 text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-8" })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "text-base font-semibold text-foreground",
						children: "Identity Confirmed"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-muted-foreground leading-relaxed",
						children: "Your email address is now verified. You have full access to network defense analytics, alert reviews, and firewall management."
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					type: "button",
					onClick: () => navigate({ to: "/" }),
					className: "w-full gap-2 font-semibold",
					children: ["Enter Security Operations Center ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowRight, { className: "size-4" })]
				})
			]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Verify Email Address",
		subtitle: "Complete your SentinelAI account verification",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-5",
			children: [
				errorMessage && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-start gap-2.5 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "mt-0.5 size-4 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "leading-relaxed",
						children: errorMessage
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
					onSubmit: handleManualSubmit,
					className: "space-y-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-1.5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "token",
							className: "text-xs font-medium",
							children: "Verification Token"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "token",
							type: "text",
							placeholder: "Paste verification token here",
							value: token,
							onChange: (e) => setToken(e.target.value),
							className: "font-mono text-xs",
							required: true
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						type: "submit",
						disabled: !token.trim(),
						className: "w-full gap-2 font-semibold",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MailCheck, { className: "size-4" }), " Verify Account"]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-lg border border-border/70 bg-muted/20 p-4 space-y-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "text-xs font-medium text-foreground",
							children: "Need a new verification link?"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-[11px] text-muted-foreground leading-relaxed",
							children: "If your token expired or you didn't receive the original email, enter your email below to request a new link."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
							onSubmit: handleResend,
							className: "flex gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
								type: "email",
								placeholder: "user@sentinelai.local",
								value: resendEmail,
								onChange: (e) => setResendEmail(e.target.value),
								className: "text-xs flex-1",
								required: true
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "submit",
								variant: "secondary",
								size: "sm",
								disabled: resendStatus === "sending" || !resendEmail.trim(),
								className: "text-xs",
								children: resendStatus === "sending" ? "Sending..." : resendStatus === "sent" ? "Sent ✓" : "Resend"
							})]
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "text-center text-xs",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/login",
						className: "text-muted-foreground transition-colors hover:text-foreground hover:underline",
						children: "Return to Login"
					})
				})
			]
		})
	});
}
//#endregion
export { VerifyEmailPage as component };
