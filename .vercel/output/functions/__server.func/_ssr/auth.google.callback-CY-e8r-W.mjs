import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { H as CircleAlert, T as LoaderCircle, V as CircleCheck } from "../_libs/lucide-react.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
import { x as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Route } from "./auth.google.callback-33JQybTA.mjs";
import { t as AuthLayout } from "./auth-layout-0M7xX-2G.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/auth.google.callback-CY-e8r-W.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function GoogleCallbackPage() {
	const { loginWithGoogle } = useAuth();
	const navigate = useNavigate();
	const search = Route.useSearch();
	const [isLoading, setIsLoading] = (0, import_react.useState)(true);
	const [errorMessage, setErrorMessage] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		if (search.error) {
			setIsLoading(false);
			setErrorMessage(`Google authentication error: ${search.error}`);
			return;
		}
		if (!search.code) {
			setIsLoading(false);
			setErrorMessage("No authorization code was received from Google.");
			return;
		}
		handleCodeExchange(search.code);
	}, [search.code, search.error]);
	const handleCodeExchange = async (code) => {
		try {
			setIsLoading(true);
			const redirectUri = `${window.location.origin}/auth/google/callback`;
			const user = await loginWithGoogle({
				code,
				redirect_uri: redirectUri
			});
			toast.success("Google Authentication Successful", { description: `Welcome to SentinelAI, ${user.displayName || user.username}.` });
			navigate({ to: "/" });
		} catch (err) {
			setErrorMessage(err.message || "Failed to complete Google authentication.");
		} finally {
			setIsLoading(false);
		}
	};
	if (isLoading) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Authenticating with Google",
		subtitle: "Verifying OpenID Connect identity with SentinelAI backend",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col items-center justify-center py-8 text-center space-y-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-10 animate-spin text-primary" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-xs text-muted-foreground font-mono",
				children: "Exchanging cryptographic tokens and restoring session..."
			})]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Google Sign-In Status",
		subtitle: "Google OAuth authorization callback",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-5 text-center",
			children: [errorMessage ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mx-auto flex size-14 items-center justify-center rounded-full bg-destructive/15 text-destructive",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "size-8" })
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "space-y-1.5",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
					className: "text-base font-semibold text-foreground",
					children: "Authentication Could Not Be Completed"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs text-destructive leading-relaxed",
					children: errorMessage
				})]
			})] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-8" })
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "space-y-1.5",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
					className: "text-base font-semibold text-foreground",
					children: "Authentication Verified"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs text-muted-foreground leading-relaxed",
					children: "Redirecting to SentinelAI dashboard..."
				})]
			})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				type: "button",
				onClick: () => navigate({ to: "/login" }),
				className: "w-full font-semibold",
				children: "Return to Login"
			})]
		})
	});
}
//#endregion
export { GoogleCallbackPage as component };
