import { _ as lazyRouteComponent, v as createFileRoute } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/login-D1_IvoKn.js
var $$splitComponentImporter = () => import("./login-Cq6BD0AN.mjs");
var Route = createFileRoute("/login")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: (search) => ({ redirect: search.redirect || "/" })
});
//#endregion
export { Route as t };
