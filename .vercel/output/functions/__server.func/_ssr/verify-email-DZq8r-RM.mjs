import { _ as lazyRouteComponent, v as createFileRoute } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/verify-email-DZq8r-RM.js
var $$splitComponentImporter = () => import("./verify-email-Cs0DhtUP.mjs");
var Route = createFileRoute("/verify-email")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: (search) => ({ token: search.token || "" })
});
//#endregion
export { Route as t };
