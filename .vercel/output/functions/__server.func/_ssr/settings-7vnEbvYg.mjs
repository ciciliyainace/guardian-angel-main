import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { _ as lazyRouteComponent, v as createFileRoute } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/settings-7vnEbvYg.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var KEY = "sentinel-ai-theme";
var Ctx = (0, import_react.createContext)({
	theme: "dark",
	setTheme: () => {}
});
function apply(t) {
	const dark = t === "dark" || t === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches;
	document.documentElement.classList.toggle("dark", dark);
}
function ThemeProvider({ children }) {
	const [theme, setThemeState] = (0, import_react.useState)("dark");
	(0, import_react.useEffect)(() => {
		const saved = localStorage.getItem(KEY) ?? localStorage.getItem("protecto-theme") ?? "dark";
		localStorage.setItem(KEY, saved);
		setThemeState(saved);
		apply(saved);
		const mq = window.matchMedia("(prefers-color-scheme: dark)");
		const onChange = () => {
			if ((localStorage.getItem(KEY) ?? "dark") === "system") apply("system");
		};
		mq.addEventListener("change", onChange);
		return () => mq.removeEventListener("change", onChange);
	}, []);
	const setTheme = (t) => {
		localStorage.setItem(KEY, t);
		setThemeState(t);
		apply(t);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Ctx.Provider, {
		value: {
			theme,
			setTheme
		},
		children
	});
}
var useTheme = () => (0, import_react.useContext)(Ctx);
var TABS = [
	"profile",
	"security",
	"appearance",
	"help",
	"about",
	"feedback"
];
var D = "Profile, appearance and application settings.";
var $$splitComponentImporter = () => import("./settings-C5yGJL01.mjs");
var T = "Settings — Sentinel AI";
var Route = createFileRoute("/settings")({
	validateSearch: (s) => TABS.includes(s["tab"]) ? { tab: s["tab"] } : {},
	head: () => ({ meta: [
		{ title: T },
		{
			name: "description",
			content: D
		},
		{
			property: "og:title",
			content: T
		},
		{
			property: "og:description",
			content: D
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter, "component")
});
//#endregion
export { useTheme as a, ThemeProvider as i, Route as n, TABS as r, D as t };
