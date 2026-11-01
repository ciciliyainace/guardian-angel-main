import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { C as LogIn, H as CircleAlert, I as Eye, L as EyeOff, n as User, w as Lock } from "../_libs/lucide-react.mjs";
import { t as Input } from "./input-DF0EQrhe.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
import { b as Link, x as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as AuthLayout } from "./auth-layout-0M7xX-2G.mjs";
import { t as Label } from "./label-C3qa2Vlq.mjs";
import { t as Route } from "./login-D1_IvoKn.mjs";
import { t as GoogleSignInButton } from "./google-sign-in-button-Bw72Y-lo.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/login-Cq6BD0AN.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function LoginPage() {
	const { login } = useAuth();
	const navigate = useNavigate();
	const redirectTarget = Route.useSearch().redirect || "/";
	const [usernameOrEmail, setUsernameOrEmail] = (0, import_react.useState)("");
	const [password, setPassword] = (0, import_react.useState)("");
	const [showPassword, setShowPassword] = (0, import_react.useState)(false);
	const [isLoading, setIsLoading] = (0, import_react.useState)(false);
	const [errorMessage, setErrorMessage] = (0, import_react.useState)(null);
	const handleSubmit = async (e) => {
		e.preventDefault();
		setErrorMessage(null);
		if (!usernameOrEmail.trim() || !password) {
			setErrorMessage("Please enter both username/email and password.");
			return;
		}
		try {
			setIsLoading(true);
			const user = await login(usernameOrEmail.trim(), password);
			toast.success("Authentication Successful", { description: `Welcome back, ${user.displayName || user.username}.` });
			navigate({ to: redirectTarget });
		} catch (err) {
			const e = err;
			setErrorMessage(e.message || "Invalid username/email or password.");
			toast.error("Login Failed", { description: e.message || "Invalid username/email or password." });
		} finally {
			setIsLoading(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "SOC Access Portal",
		subtitle: "Enter your verified credentials to access SentinelAI Defense System",
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
						htmlFor: "identifier",
						className: "text-xs font-medium",
						children: "Username or Email Address"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(User, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "identifier",
							type: "text",
							autoComplete: "username",
							placeholder: "e.g. analyst or user@corp.net",
							value: usernameOrEmail,
							onChange: (e) => setUsernameOrEmail(e.target.value),
							className: "pl-9 text-sm",
							disabled: isLoading,
							required: true
						})]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "password",
							className: "text-xs font-medium",
							children: "Password"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/forgot-password",
							className: "text-xs text-primary transition-colors hover:text-primary/80 hover:underline",
							children: "Forgot password?"
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
								id: "password",
								type: showPassword ? "text" : "password",
								autoComplete: "current-password",
								placeholder: "••••••••••••",
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
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "submit",
					disabled: isLoading,
					className: "w-full gap-2 font-semibold shadow-sm transition-all",
					children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" }), "Verifying Credentials..."]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogIn, { className: "size-4" }), " Sign In"] })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative my-4 flex items-center justify-center",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-full border-t border-border/80" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "absolute bg-card px-3 font-mono text-[11px] text-muted-foreground uppercase",
						children: "Or"
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GoogleSignInButton, {
					label: "Continue with Google",
					disabled: isLoading
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "pt-2 text-center text-xs text-muted-foreground",
					children: [
						"Don't have an account yet?",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/register",
							className: "font-semibold text-primary transition-colors hover:text-primary/80 hover:underline",
							children: "Create an account"
						})
					]
				})
			]
		})
	});
}
//#endregion
export { LoginPage as component };
