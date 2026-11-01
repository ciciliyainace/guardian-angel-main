import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { i as api, l as cn, m as getAuthToken, r as Button } from "./api-D71CZkbx.mjs";
import { T as LoaderCircle } from "../_libs/lucide-react.mjs";
import { n as PageHeader, r as Panel } from "./soc-DzyCmLi7.mjs";
import { t as Input } from "./input-DF0EQrhe.mjs";
import { t as Textarea } from "./textarea-BastJrKb.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { x as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { a as useTheme, n as Route, r as TABS, t as D } from "./settings-7vnEbvYg.mjs";
import { i as TabsTrigger$1, n as TabsContent$1, r as TabsList$1, t as Tabs$1 } from "../_libs/radix-ui__react-tabs.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/settings-C5yGJL01.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Tabs = Tabs$1;
var TabsList = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsList$1, {
	ref,
	className: cn("inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground", className),
	...props
}));
TabsList.displayName = TabsList$1.displayName;
var TabsTrigger = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsTrigger$1, {
	ref,
	className: cn("inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background cursor-pointer transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow", className),
	...props
}));
TabsTrigger.displayName = TabsTrigger$1.displayName;
var TabsContent = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent$1, {
	ref,
	className: cn("mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2", className),
	...props
}));
TabsContent.displayName = TabsContent$1.displayName;
function Settings() {
	const { tab = "profile" } = Route.useSearch();
	const navigate = useNavigate({ from: "/settings" });
	const { theme, setTheme } = useTheme();
	const [profile, setProfile] = (0, import_react.useState)({
		displayName: "Ciciliya Inace",
		email: "analyst@sentinelai.local",
		role: "analyst",
		username: "ciciliya-inace",
		email_verified: true,
		auth_providers: ["password"]
	});
	const [loadingProfile, setLoadingProfile] = (0, import_react.useState)(false);
	const [resendingVerification, setResendingVerification] = (0, import_react.useState)(false);
	const [fbCategory, setFbCategory] = (0, import_react.useState)("False Positive");
	const [fbMessage, setFbMessage] = (0, import_react.useState)("");
	const [submittingFb, setSubmittingFb] = (0, import_react.useState)(false);
	const [loginUser, setLoginUser] = (0, import_react.useState)("admin");
	const [loginPass, setLoginPass] = (0, import_react.useState)("");
	const [loggingIn, setLoggingIn] = (0, import_react.useState)(false);
	const [hasToken, setHasToken] = (0, import_react.useState)(!!getAuthToken());
	(0, import_react.useEffect)(() => {
		let isMounted = true;
		setLoadingProfile(true);
		api.getProfile().then((p) => {
			if (isMounted && p) setProfile(p);
		}).catch(() => {}).finally(() => {
			if (isMounted) setLoadingProfile(false);
		});
		return () => {
			isMounted = false;
		};
	}, []);
	const handleLogin = async (e) => {
		e.preventDefault();
		setLoggingIn(true);
		try {
			await api.login(loginUser, loginPass);
			setHasToken(true);
			toast.success(`Authenticated as ${loginUser}`);
			const updatedProfile = await api.getProfile();
			setProfile(updatedProfile);
		} catch (err) {
			const msg = err instanceof Error ? err.message : "Authentication failed";
			toast.error(msg);
		} finally {
			setLoggingIn(false);
		}
	};
	const handleLogout = async () => {
		await api.logout();
		setHasToken(false);
		toast.info("Logged out");
	};
	const handleSendFeedback = async (e) => {
		e.preventDefault();
		if (!fbMessage.trim()) {
			toast.error("Please enter a feedback message");
			return;
		}
		setSubmittingFb(true);
		try {
			await api.submitFeedback(fbCategory, fbMessage);
			toast.success("Feedback submitted to SentinelAI security team");
			setFbMessage("");
		} catch (err) {
			const msg = err instanceof Error ? err.message : "Failed to submit feedback";
			toast.error(msg);
		} finally {
			setSubmittingFb(false);
		}
	};
	const handleResendVerification = async () => {
		if (!profile.email) return;
		setResendingVerification(true);
		try {
			const data = await (await fetch(`${api.isLive() ? "http://127.0.0.1:8000/api/v1" : "/api/v1"}/auth/resend-verification`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ email: profile.email })
			})).json();
			toast.info("Verification Request Dispatched", { description: data.message || "A verification link has been sent to your email." });
		} catch {
			toast.error("Failed to resend verification email.");
		} finally {
			setResendingVerification(false);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageHeader, {
			title: "Settings",
			description: D
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Tabs, {
			value: tab,
			onValueChange: (v) => navigate({ search: { tab: v } }),
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsList, {
					className: "flex-wrap",
					children: TABS.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsTrigger, {
						value: t,
						className: "capitalize",
						children: t
					}, t))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
					value: "profile",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "User Profile",
						children: loadingProfile ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex h-20 items-center text-sm text-muted-foreground",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-2 size-4 animate-spin" }), " Loading profile..."]
						}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-3 text-sm",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-medium text-foreground",
									children: "Name: "
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted-foreground",
									children: profile.displayName || profile.username
								})] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-medium text-foreground",
									children: "Username: "
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-xs text-muted-foreground",
									children: profile.username
								})] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-medium text-foreground",
										children: "Email: "
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono text-xs text-muted-foreground",
										children: profile.email
									}),
									profile.email_verified ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "ml-2 inline-flex items-center rounded bg-success/15 px-1.5 py-0.5 text-[10px] font-medium text-success",
										children: "✓ Verified"
									}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
										className: "ml-2 inline-flex items-center gap-1.5",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "rounded bg-warning/15 px-1.5 py-0.5 text-[10px] font-medium text-warning",
											children: "⚠ Unverified"
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											variant: "link",
											size: "sm",
											onClick: handleResendVerification,
											disabled: resendingVerification,
											className: "h-auto p-0 text-xs text-primary underline",
											children: resendingVerification ? "Sending..." : "Resend Link"
										})]
									})
								] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-medium text-foreground",
									children: "Assigned Role: "
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold capitalize text-foreground",
									children: profile.role
								})] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-medium text-foreground",
									children: "Authentication: "
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "inline-flex items-center gap-1",
									children: (profile.auth_providers || ["password"]).map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "rounded border bg-muted/50 px-1.5 py-0.5 font-mono text-[11px] text-muted-foreground capitalize",
										children: p
									}, p))
								})] })
							]
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
					value: "security",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Account & API Authentication",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "max-w-md space-y-4 text-sm",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center justify-between rounded-lg border p-3",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "font-medium",
									children: "Active Session Status"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "text-xs text-muted-foreground",
									children: hasToken ? "JWT Token Active" : "Unauthenticated (Operating in Guest/Demo Mode)"
								})] }), hasToken && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									variant: "outline",
									size: "sm",
									onClick: handleLogout,
									children: "Sign Out"
								})]
							}), !hasToken && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
								onSubmit: handleLogin,
								className: "space-y-3 rounded-lg border p-4",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "text-xs font-medium uppercase text-muted-foreground",
										children: "Sign In to Backend"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
										className: "text-xs text-muted-foreground",
										children: "Username"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										value: loginUser,
										onChange: (e) => setLoginUser(e.target.value),
										placeholder: "Username or email",
										required: true
									})] }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
										className: "text-xs text-muted-foreground",
										children: "Password"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										type: "password",
										value: loginPass,
										onChange: (e) => setLoginPass(e.target.value),
										placeholder: "••••••••",
										required: true
									})] }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
										type: "submit",
										size: "sm",
										disabled: loggingIn,
										className: "w-full",
										children: [loggingIn ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-2 size-3 animate-spin" }) : null, "Authenticate"]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
										className: "text-[11px] text-muted-foreground",
										children: [
											"Default analyst: ",
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
												className: "rounded bg-muted px-1",
												children: "ciciliya-inace"
											}),
											" / ",
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", {
												className: "rounded bg-muted px-1",
												children: "<configured password>"
											})
										]
									})
								]
							})]
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
					value: "appearance",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Theme",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "flex gap-2",
							children: [
								"dark",
								"light",
								"system"
							].map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: theme === t ? "default" : "outline",
								onClick: () => setTheme(t),
								className: "capitalize",
								children: t
							}, t))
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
					value: "help",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Help & Navigation",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-2 text-sm text-muted-foreground",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", { children: [
									"• Press ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("kbd", {
										className: "rounded border bg-muted px-1 font-mono text-xs",
										children: "⌘K"
									}),
									" or ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("kbd", {
										className: "rounded border bg-muted px-1 font-mono text-xs",
										children: "Ctrl+K"
									}),
									" to search pages, alerts, and block requests."
								] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "• Review and approve firewall block requests strictly from the Firewall Management tab." }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "• Detection models and rules operate on an alert-first principle: automated blocking is disabled by default." })
							]
						})
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
					value: "about",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Panel, {
						title: "About Sentinel AI",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm text-muted-foreground",
							children: "SentinelAI — AI-Powered Firewall Attack Detection System for Computer Networks."
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-xs text-muted-foreground",
							children: "Architecture: FastAPI Backend · Scikit-learn (Random Forest & Isolation Forest) · Suricata IDS Connector · Windows Defender Firewall Integration · React Frontend."
						})]
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
					value: "feedback",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Panel, {
						title: "Submit Feedback & False Positives",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
							onSubmit: handleSendFeedback,
							className: "max-w-lg space-y-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
									className: "text-xs font-medium text-muted-foreground",
									children: "Category"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
									value: fbCategory,
									onChange: (e) => setFbCategory(e.target.value),
									className: "mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
											value: "False Positive",
											children: "False Positive Report"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
											value: "Rule Suggestion",
											children: "Rule Suggestion"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
											value: "Bug Report",
											children: "System Bug Report"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
											value: "Feature Request",
											children: "Feature Request"
										})
									]
								})] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
									className: "text-xs font-medium text-muted-foreground",
									children: "Message / Explanation"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
									value: fbMessage,
									onChange: (e) => setFbMessage(e.target.value),
									placeholder: "Describe the issue, false positive event ID, or suggested rule parameter...",
									rows: 4,
									required: true
								})] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									type: "submit",
									size: "sm",
									disabled: submittingFb,
									children: [submittingFb && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mr-1.5 size-3.5 animate-spin" }), "Submit Feedback"]
								})
							]
						})
					})
				})
			]
		})]
	});
}
//#endregion
export { Settings as component };
