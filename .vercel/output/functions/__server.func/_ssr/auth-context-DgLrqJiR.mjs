import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { c as clearAuthToken, m as getAuthToken, t as API_BASE_URL, y as setAuthToken } from "./api-D71CZkbx.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/auth-context-DgLrqJiR.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var AuthContext = (0, import_react.createContext)(void 0);
function AuthProvider({ children }) {
	const [user, setUser] = (0, import_react.useState)(null);
	const [token, setToken] = (0, import_react.useState)(getAuthToken());
	const [isLoading, setIsLoading] = (0, import_react.useState)(true);
	const refreshUser = (0, import_react.useCallback)(async () => {
		const currentToken = getAuthToken();
		if (!currentToken) {
			setUser(null);
			setIsLoading(false);
			return null;
		}
		try {
			const res = await fetch(`${API_BASE_URL}/auth/me`, { headers: {
				Authorization: `Bearer ${currentToken}`,
				"Content-Type": "application/json"
			} });
			if (!res.ok) {
				clearAuthToken();
				setToken(null);
				setUser(null);
				return null;
			}
			const userData = await res.json();
			setUser(userData);
			return userData;
		} catch (err) {
			console.warn("[Auth] Failed to restore session from API:", err);
			return null;
		} finally {
			setIsLoading(false);
		}
	}, []);
	(0, import_react.useEffect)(() => {
		refreshUser();
	}, [refreshUser]);
	const login = async (usernameOrEmail, password) => {
		const res = await fetch(`${API_BASE_URL}/auth/login`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				username_or_email: usernameOrEmail.trim(),
				password
			})
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Invalid username/email or password.");
		}
		const data = await res.json();
		setAuthToken(data.access_token);
		setToken(data.access_token);
		setUser(data.user);
		return data.user;
	};
	const register = async (payload) => {
		const res = await fetch(`${API_BASE_URL}/auth/register`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(payload)
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Registration failed. Please check your information.");
		}
		return await res.json();
	};
	const getGoogleOAuthUrl = async () => {
		const res = await fetch(`${API_BASE_URL}/auth/google/url`);
		if (!res.ok) throw new Error("Failed to retrieve Google OAuth status from backend.");
		return res.json();
	};
	const loginWithGoogle = async (params) => {
		const res = await fetch(`${API_BASE_URL}/auth/google`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(params)
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Google authentication failed.");
		}
		const data = await res.json();
		setAuthToken(data.access_token);
		setToken(data.access_token);
		setUser(data.user);
		return data.user;
	};
	const verifyEmail = async (token) => {
		const res = await fetch(`${API_BASE_URL}/auth/verify-email`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token })
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Email verification failed or token has expired.");
		}
		await refreshUser();
		return res.json();
	};
	const resendVerification = async (email) => {
		const res = await fetch(`${API_BASE_URL}/auth/resend-verification`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ email })
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Failed to resend verification email.");
		}
		return res.json();
	};
	const forgotPassword = async (email) => {
		const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ email })
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Failed to process forgot password request.");
		}
		return res.json();
	};
	const resetPassword = async (token, password, confirmPassword) => {
		const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				token,
				password,
				confirm_password: confirmPassword
			})
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Failed to reset password.");
		}
		return res.json();
	};
	const logout = async () => {
		const currentToken = getAuthToken();
		try {
			if (currentToken) await fetch(`${API_BASE_URL}/auth/logout`, {
				method: "POST",
				headers: {
					Authorization: `Bearer ${currentToken}`,
					"Content-Type": "application/json"
				}
			});
		} catch {} finally {
			clearAuthToken();
			setToken(null);
			setUser(null);
		}
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthContext.Provider, {
		value: {
			user,
			token,
			isAuthenticated: !!user && !!token,
			isLoading,
			login,
			register,
			loginWithGoogle,
			getGoogleOAuthUrl,
			verifyEmail,
			resendVerification,
			forgotPassword,
			resetPassword,
			logout,
			refreshUser
		},
		children
	});
}
function useAuth() {
	const context = (0, import_react.useContext)(AuthContext);
	if (!context) throw new Error("useAuth must be used within an AuthProvider");
	return context;
}
//#endregion
export { useAuth as n, AuthProvider as t };
