import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { H as CircleAlert, I as Eye, L as EyeOff, O as KeySquare, V as CircleCheck, w as Lock } from "../_libs/lucide-react.mjs";
import { t as Input } from "./input-DF0EQrhe.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
import { b as Link, x as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as AuthLayout } from "./auth-layout-0M7xX-2G.mjs";
import { t as Label } from "./label-C3qa2Vlq.mjs";
import { n as analyzePassword, t as PasswordStrengthMeter } from "./password-strength-DJBZSIsc.mjs";
import { t as Route } from "./reset-password-MyvPk9U6.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/reset-password-DG7qa6Bu.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function ResetPasswordPage() {
	const { resetPassword } = useAuth();
	const navigate = useNavigate();
	const search = Route.useSearch();
	const [token, setToken] = (0, import_react.useState)(search.token || "");
	const [password, setPassword] = (0, import_react.useState)("");
	const [confirmPassword, setConfirmPassword] = (0, import_react.useState)("");
	const [showPassword, setShowPassword] = (0, import_react.useState)(false);
	const [showConfirmPassword, setShowConfirmPassword] = (0, import_react.useState)(false);
	const [isLoading, setIsLoading] = (0, import_react.useState)(false);
	const [isSuccess, setIsSuccess] = (0, import_react.useState)(false);
	const [errorMessage, setErrorMessage] = (0, import_react.useState)(null);
	const passwordAnalysis = analyzePassword(password);
	const passwordsMatch = password.length > 0 && password === confirmPassword;
	const handleSubmit = async (e) => {
		e.preventDefault();
		setErrorMessage(null);
		if (!token.trim()) {
			setErrorMessage("Password reset token is missing. Please use the link provided in your email.");
			return;
		}
		if (password !== confirmPassword) {
			setErrorMessage("Passwords do not match.");
			return;
		}
		if (passwordAnalysis.score < 2) {
			setErrorMessage("Please choose a stronger password meeting security requirements.");
			return;
		}
		try {
			setIsLoading(true);
			await resetPassword(token.trim(), password, confirmPassword);
			setIsSuccess(true);
			toast.success("Password Updated", { description: "Your password has been changed. You may now log in with your new credentials." });
		} catch (err) {
			setErrorMessage(err.message || "Failed to reset password. Link may be invalid or expired.");
		} finally {
			setIsLoading(false);
		}
	};
	if (isSuccess) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Password Successfully Updated",
		subtitle: "Your SentinelAI account credentials have been secured",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-5 text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-8" })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "text-base font-semibold text-foreground",
						children: "New Password Active"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-muted-foreground leading-relaxed",
						children: "Your password has been updated in MongoDB Atlas. Previous authentication sessions have been invalidated for security."
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "button",
					onClick: () => navigate({ to: "/login" }),
					className: "w-full font-semibold",
					children: "Sign In with New Password"
				})
			]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Create New Password",
		subtitle: "Establish a new secure password for your SentinelAI account",
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
				!search.token && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
						htmlFor: "token",
						className: "text-xs font-medium",
						children: "Reset Token"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KeySquare, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "token",
							type: "text",
							placeholder: "Paste reset token from email",
							value: token,
							onChange: (e) => setToken(e.target.value),
							className: "pl-9 text-xs font-mono",
							required: true
						})]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "new-password",
							className: "text-xs font-medium",
							children: "New Password"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "new-password",
									type: showPassword ? "text" : "password",
									autoComplete: "new-password",
									placeholder: "Min. 8 characters",
									value: password,
									onChange: (e) => setPassword(e.target.value),
									className: "pl-9 pr-10 text-sm",
									disabled: isLoading,
									required: true
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => setShowPassword(!showPassword),
									className: "absolute right-3 top-2.5 text-muted-foreground transition-colors hover:text-foreground",
									"aria-label": showPassword ? "Hide password" : "Show password",
									children: showPassword ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "size-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "size-4" })
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PasswordStrengthMeter, { password })
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "confirm-reset-password",
							className: "text-xs font-medium",
							children: "Confirm New Password"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "confirm-reset-password",
									type: showConfirmPassword ? "text" : "password",
									autoComplete: "new-password",
									placeholder: "Re-enter new password",
									value: confirmPassword,
									onChange: (e) => setConfirmPassword(e.target.value),
									className: "pl-9 pr-10 text-sm",
									disabled: isLoading,
									required: true
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => setShowConfirmPassword(!showConfirmPassword),
									className: "absolute right-3 top-2.5 text-muted-foreground transition-colors hover:text-foreground",
									"aria-label": showConfirmPassword ? "Hide password" : "Show password",
									children: showConfirmPassword ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EyeOff, { className: "size-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Eye, { className: "size-4" })
								})
							]
						}),
						confirmPassword.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "text-[11px] font-mono",
							children: passwordsMatch ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-success flex items-center gap-1",
								children: "✓ Passwords match"
							}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-destructive flex items-center gap-1",
								children: "✕ Passwords do not match"
							})
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "submit",
					disabled: isLoading,
					className: "w-full gap-2 font-semibold shadow-sm transition-all",
					children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" }), "Securing Account..."]
					}) : "Update Password"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "pt-2 text-center text-xs",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/login",
						className: "text-muted-foreground transition-colors hover:text-foreground hover:underline",
						children: "Cancel and Return to Login"
					})
				})
			]
		})
	});
}
//#endregion
export { ResetPasswordPage as component };
