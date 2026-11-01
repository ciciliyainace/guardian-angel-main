import { _ as lazyRouteComponent, v as createFileRoute } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/auth.google.callback-33JQybTA.js
var $$splitComponentImporter = () => import("./auth.google.callback-CY-e8r-W.mjs");
var Route = createFileRoute("/auth/google/callback")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: (search) => ({
		code: search.code || "",
		state: search.state || "",
		error: search.error || ""
	})
});
//#endregion
export { Route as t };
