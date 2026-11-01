import { _ as lazyRouteComponent, v as createFileRoute } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/reset-password-MyvPk9U6.js
var $$splitComponentImporter = () => import("./reset-password-DG7qa6Bu.mjs");
var Route = createFileRoute("/reset-password")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: (search) => ({ token: search.token || "" })
});
//#endregion
export { Route as t };
