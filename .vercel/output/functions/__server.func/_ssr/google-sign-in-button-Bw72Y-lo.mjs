import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/google-sign-in-button-Bw72Y-lo.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function GoogleSignInButton({ label = "Continue with Google", disabled = false }) {
	const { getGoogleOAuthUrl } = useAuth();
	const [loading, setLoading] = (0, import_react.useState)(false);
	const handleClick = async () => {
		try {
			setLoading(true);
			const res = await getGoogleOAuthUrl();
			if (res.configured && res.url) window.location.href = res.url;
			else toast.info("Google OAuth Configuration Required", {
				description: res.message || "Please configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env to activate Google OAuth.",
				duration: 6e3
			});
		} catch (err) {
			const e = err;
			toast.error("Google Sign-In Error", { description: e.message || "Failed to initiate Google authentication." });
		} finally {
			setLoading(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
		type: "button",
		variant: "outline",
		onClick: handleClick,
		disabled: disabled || loading,
		className: "relative flex h-10 w-full items-center justify-center gap-2.5 border-border/80 bg-background/50 hover:bg-muted/80 transition-all font-medium text-xs sm:text-sm",
		children: [loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-4 animate-spin text-muted-foreground" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
			className: "size-4 shrink-0",
			viewBox: "0 0 24 24",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
					fill: "#4285F4",
					d: "M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
					fill: "#34A853",
					d: "M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
					fill: "#FBBC05",
					d: "M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
					fill: "#EA4335",
					d: "M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: label })]
	});
}
//#endregion
export { GoogleSignInButton as t };
