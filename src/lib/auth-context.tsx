import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { API_BASE_URL, getAuthToken, setAuthToken, clearAuthToken } from "@/lib/api";

export interface AuthUser {
  id: number;
  email: string;
  username: string;
  display_name: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  auth_providers: string[];
  created_at?: string | null;
  first_login_at?: string | null;
  last_login_at?: string | null;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  display_name?: string;
  terms_accepted: boolean;
}

export interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<AuthUser>;
  register: (payload: RegisterPayload) => Promise<AuthUser>;
  loginWithGoogle: (params: { id_token?: string; code?: string; redirect_uri?: string }) => Promise<AuthUser>;
  getGoogleOAuthUrl: () => Promise<{ configured: boolean; url?: string; message?: string }>;
  verifyEmail: (token: string) => Promise<{ status: string; message: string }>;
  resendVerification: (email: string) => Promise<{ status: string; message: string; email_status?: string }>;
  forgotPassword: (email: string) => Promise<{ status: string; message: string; email_status?: string }>;
  resetPassword: (token: string, password: string, confirmPassword: string) => Promise<{ status: string; message: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<AuthUser | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(getAuthToken());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore authenticated session on load
  const refreshUser = useCallback(async (): Promise<AuthUser | null> => {
    const currentToken = getAuthToken();
    if (!currentToken) {
      setUser(null);
      setIsLoading(false);
      return null;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${currentToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) {
        // Token invalid or expired
        clearAuthToken();
        setToken(null);
        setUser(null);
        return null;
      }

      const userData = (await res.json()) as AuthUser;
      setUser(userData);
      return userData;
    } catch (err) {
      console.warn("[Auth] Failed to restore session from API:", err);
      // Don't wipe immediately on network errors to support offline resilience
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (usernameOrEmail: string, password: string): Promise<AuthUser> => {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username_or_email: usernameOrEmail.trim(),
        password,
      }),
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

  const register = async (payload: RegisterPayload): Promise<AuthUser> => {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Registration failed. Please check your information.");
    }

    const userData = (await res.json()) as AuthUser;
    return userData;
  };

  const getGoogleOAuthUrl = async () => {
    const res = await fetch(`${API_BASE_URL}/auth/google/url`);
    if (!res.ok) {
      throw new Error("Failed to retrieve Google OAuth status from backend.");
    }
    return res.json();
  };

  const loginWithGoogle = async (params: { id_token?: string; code?: string; redirect_uri?: string }): Promise<AuthUser> => {
    const res = await fetch(`${API_BASE_URL}/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
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

  const verifyEmail = async (token: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Email verification failed or token has expired.");
    }

    // Refresh active session profile if user is currently logged in
    await refreshUser();
    return res.json();
  };

  const resendVerification = async (email: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/resend-verification`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Failed to resend verification email.");
    }
    return res.json();
  };

  const forgotPassword = async (email: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Failed to process forgot password request.");
    }
    return res.json();
  };

  const resetPassword = async (token: string, password: string, confirmPassword: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token,
        password,
        confirm_password: confirmPassword,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Failed to reset password.");
    }
    return res.json();
  };

  const logout = async (): Promise<void> => {
    const currentToken = getAuthToken();
    try {
      if (currentToken) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${currentToken}`,
            "Content-Type": "application/json",
          },
        });
      }
    } catch {
      // Ignored during client logout
    } finally {
      clearAuthToken();
      setToken(null);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
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
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
