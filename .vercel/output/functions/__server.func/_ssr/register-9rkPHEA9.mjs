import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { r as Button } from "./api-D71CZkbx.mjs";
import { H as CircleAlert, I as Eye, L as EyeOff, V as CircleCheck, b as Mail, d as Send, n as User, r as UserCheck, w as Lock } from "../_libs/lucide-react.mjs";
import { t as Input } from "./input-DF0EQrhe.mjs";
import { t as Checkbox } from "./checkbox-CKIHdpWX.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { n as useAuth } from "./auth-context-DgLrqJiR.mjs";
import { b as Link, x as useNavigate } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as AuthLayout } from "./auth-layout-0M7xX-2G.mjs";
import { t as Label } from "./label-C3qa2Vlq.mjs";
import { t as GoogleSignInButton } from "./google-sign-in-button-Bw72Y-lo.mjs";
import { n as analyzePassword, t as PasswordStrengthMeter } from "./password-strength-DJBZSIsc.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/register-9rkPHEA9.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function RegisterPage() {
	const { register } = useAuth();
	const navigate = useNavigate();
	const [username, setUsername] = (0, import_react.useState)("");
	const [email, setEmail] = (0, import_react.useState)("");
	const [password, setPassword] = (0, import_react.useState)("");
	const [confirmPassword, setConfirmPassword] = (0, import_react.useState)("");
	const [termsAccepted, setTermsAccepted] = (0, import_react.useState)(false);
	const [showPassword, setShowPassword] = (0, import_react.useState)(false);
	const [showConfirmPassword, setShowConfirmPassword] = (0, import_react.useState)(false);
	const [isLoading, setIsLoading] = (0, import_react.useState)(false);
	const [errorMessage, setErrorMessage] = (0, import_react.useState)(null);
	const [registeredUser, setRegisteredUser] = (0, import_react.useState)(null);
	const passwordAnalysis = analyzePassword(password);
	const passwordsMatch = password.length > 0 && password === confirmPassword;
	const handleSubmit = async (e) => {
		e.preventDefault();
		setErrorMessage(null);
		if (!username.trim() || !email.trim() || !password || !confirmPassword) {
			setErrorMessage("Please fill in all required registration fields.");
			return;
		}
		if (username.trim().length < 3) {
			setErrorMessage("Username must be at least 3 characters in length.");
			return;
		}
		if (!/^[a-zA-Z0-9_\-\.]+$/.test(username.trim())) {
			setErrorMessage("Username may only contain letters, numbers, hyphens, and underscores.");
			return;
		}
		if (password !== confirmPassword) {
			setErrorMessage("Password and confirmation password do not match.");
			return;
		}
		if (passwordAnalysis.score < 2) {
			setErrorMessage("Please choose a stronger password meeting security requirements.");
			return;
		}
		if (!termsAccepted) {
			setErrorMessage("You must acknowledge the Security Operations & Terms policy to proceed.");
			return;
		}
		try {
			setIsLoading(true);
			const user = await register({
				username: username.trim(),
				email: email.trim().toLowerCase(),
				password,
				confirm_password: confirmPassword,
				terms_accepted: termsAccepted
			});
			setRegisteredUser({
				username: user.username,
				email: user.email
			});
			toast.success("Account Created", { description: `Account for ${user.username} successfully registered. Welcome email sent.` });
		} catch (err) {
			const e = err;
			setErrorMessage(e.message || "Failed to create account. Please verify your details.");
			toast.error("Registration Error", { description: e.message || "Failed to create account." });
		} finally {
			setIsLoading(false);
		}
	};
	if (registeredUser) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Account Provisioned",
		subtitle: "Your SentinelAI SOC analyst credentials have been created",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-5 text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mx-auto flex size-14 items-center justify-center rounded-full bg-success/15 text-success",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-8" })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h3", {
							className: "text-lg font-semibold text-foreground",
							children: [
								"Welcome to the Defense Team, ",
								registeredUser.username,
								"!"
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-xs text-muted-foreground leading-relaxed",
							children: "Your account has been saved in MongoDB Atlas. We have dispatched a confirmation email with account details to:"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "rounded-md border border-primary/30 bg-primary/10 py-2 px-3 font-mono text-xs font-semibold text-primary",
							children: registeredUser.email
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-lg border border-border/70 bg-muted/30 p-3.5 text-left text-xs text-muted-foreground space-y-1.5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2 font-medium text-foreground",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Send, { className: "size-3.5 text-primary" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Next Steps:" })]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "1. Check your inbox for the SentinelAI welcome notification." }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "2. If verification is enabled, click the verification link in the email." }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "3. Sign in to your dashboard to monitor live firewall and ML events." })
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "button",
					onClick: () => navigate({ to: "/login" }),
					className: "w-full font-semibold",
					children: "Proceed to Login"
				})
			]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthLayout, {
		title: "Create SOC Account",
		subtitle: "Register an analyst account on SentinelAI Defense System",
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
						htmlFor: "username",
						className: "text-xs font-medium",
						children: "Username"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(User, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "username",
							type: "text",
							autoComplete: "username",
							placeholder: "e.g. analyst_john",
							value: username,
							onChange: (e) => setUsername(e.target.value),
							className: "pl-9 text-sm",
							disabled: isLoading,
							required: true
						})]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
						htmlFor: "email",
						className: "text-xs font-medium",
						children: "Email Address"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Mail, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
							id: "email",
							type: "email",
							autoComplete: "email",
							placeholder: "e.g. analyst@sentinelai.local",
							value: email,
							onChange: (e) => setEmail(e.target.value),
							className: "pl-9 text-sm",
							disabled: isLoading,
							required: true
						})]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "space-y-1.5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
							htmlFor: "reg-password",
							className: "text-xs font-medium",
							children: "Password"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "reg-password",
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
							htmlFor: "confirm-password",
							className: "text-xs font-medium",
							children: "Confirm Password"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, { className: "absolute left-3 top-2.5 size-4 text-muted-foreground" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									id: "confirm-password",
									type: showConfirmPassword ? "text" : "password",
									autoComplete: "new-password",
									placeholder: "Re-enter your password",
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
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-start gap-2.5 pt-1",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Checkbox, {
						id: "terms",
						checked: termsAccepted,
						onCheckedChange: (checked) => setTermsAccepted(checked === true),
						className: "mt-0.5"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
						htmlFor: "terms",
						className: "text-xs text-muted-foreground leading-snug cursor-pointer",
						children: "I acknowledge SentinelAI's Security & Compliance Policies, and agree to keep authentication credentials confidential."
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					type: "submit",
					disabled: isLoading || !termsAccepted,
					className: "w-full gap-2 font-semibold shadow-sm transition-all",
					children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "flex items-center gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-3.5 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" }), "Provisioning Account..."]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserCheck, { className: "size-4" }), " Create Account"] })
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative my-4 flex items-center justify-center",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-full border-t border-border/80" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "absolute bg-card px-3 font-mono text-[11px] text-muted-foreground uppercase",
						children: "Or"
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GoogleSignInButton, {
					label: "Register with Google",
					disabled: isLoading
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "pt-2 text-center text-xs text-muted-foreground",
					children: [
						"Already registered?",
						" ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/login",
							className: "font-semibold text-primary transition-colors hover:text-primary/80 hover:underline",
							children: "Sign in to existing account"
						})
					]
				})
			]
		})
	});
}
//#endregion
export { RegisterPage as component };
