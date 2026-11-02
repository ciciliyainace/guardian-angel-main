// Centralized API service layer connecting to the SentinelAI FastAPI backend.
// In demo mode or when backend is unavailable, provides graceful fallback.
import * as mock from "./mock-data";
import type { SecurityEvent, BlockRequest, DetectionRule, AlertStatus, Severity } from "./mock-data";

export const API_BASE_URL = (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? "http://127.0.0.1:8000/api/v1";
export const DEMO_MODE = false;

const TOKEN_KEY = "sentinelai_access_token";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

let lastRequestLive = false;

export function isBackendLive(): boolean {
  return lastRequestLive;
}

async function request<T>(path: string, demo: () => T, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      throw new Error(errBody?.detail || errBody?.message || `API error ${res.status}: ${res.statusText}`);
    }

    const data = (await res.json()) as T;
    lastRequestLive = true;
    return data;
  } catch (err: unknown) {
    lastRequestLive = false;
    const e = err as Error;
    // If backend is not running or network failed, fallback to mock data with a console notice
    console.warn(`[SentinelAI API] Request to ${path} failed (${e.message}). Falling back to local state.`);
    return demo();
  }
}

export interface OverviewData {
  totalEvents: number;
  activeAlerts: number;
  criticalThreats: number;
  suspiciousConnections: number;
  managedBlocks: number;
  detectionRecall: string;
  eventsDelta?: number;
  alertsDelta?: number;
  threatsDelta?: number;
  suspiciousDelta?: number;
}

export const api = {
  // Authentication
  login: async (usernameOrEmail: string, password: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email: usernameOrEmail, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Invalid username/email or password.");
    }
    const data = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  register: async (payload: {
    username: string;
    email: string;
    password: string;
    confirm_password: string;
    display_name?: string;
    terms_accepted: boolean;
  }) => {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Registration failed.");
    }
    return res.json();
  },

  logout: async () => {
    try {
      await request("/auth/logout", () => ({ status: "success" }), { method: "POST" });
    } finally {
      clearAuthToken();
    }
  },

  getProfile: () =>
    request("/auth/me", () => ({
      id: 1,
      email: "analyst@sentinelai.local",
      username: "ciciliya-inace",
      displayName: "Ciciliya Inace",
      role: "analyst",
      is_active: true,
      email_verified: true,
      auth_providers: ["password"],
    })),

  // Events & Traffic
  events: () => request<SecurityEvent[]>("/events", () => mock.events),
  getEvent: (id: string) =>
    request<SecurityEvent>(`/events/${id}`, () => {
      const found = mock.events.find((e) => e.id === id);
      if (!found) throw new Error("Event not found");
      return found;
    }),
  trafficSeries: () => request("/analytics/traffic-series", () => mock.trafficSeries),
  overviewSummary: () =>
    request<OverviewData>("/analytics/summary", () => {
      const total = mock.trafficSeries.reduce((a, b) => a + b.total, 0);
      const benign = mock.trafficSeries.reduce((a, b) => a + b.benign, 0);
      const active = mock.events.filter((e) => e.status !== "resolved").length;
      const critical = mock.events.filter((e) => e.severity === "critical").length;
      return {
        totalEvents: total,
        activeAlerts: active,
        criticalThreats: critical,
        suspiciousConnections: total - benign,
        managedBlocks: mock.blockRequests.filter((b) => b.status === "approved").length,
        detectionRecall: "91%",
        eventsDelta: 6,
        alertsDelta: 12,
        threatsDelta: -4,
        suspiciousDelta: 9,
      };
    }),
  categoryCounts: () => request("/analytics/categories", () => mock.categoryCounts),
  severityCounts: () => request("/analytics/severity", () => mock.severityCounts),
  firewallHistory: () => request("/analytics/firewall-history", () => mock.firewallHistory),
  modelMetrics: () =>
    request("/analytics/model-metrics", () => ({
      metrics: mock.sampleMetrics,
      perClassRecall: mock.perClassRecall,
      confusion: mock.confusion,
      models: mock.models,
    })),

  // Alerts
  alerts: () => request<SecurityEvent[]>("/events", () => mock.events),
  updateAlertStatus: (id: string, status: AlertStatus, notes?: string) =>
    request(
      `/alerts/${id}`,
      () => ({ status, id }),
      {
        method: "PATCH",
        body: JSON.stringify({ status, notes }),
      }
    ),

  // Firewall Management
  blockRequests: () => request<BlockRequest[]>("/firewall/requests", () => mock.blockRequests),
  approveBlock: (id: string, note?: string) =>
    request(
      `/firewall/requests/${id}/approve`,
      () => ({ success: true, id, status: "approved" }),
      {
        method: "POST",
        body: JSON.stringify({ reviewer_note: note }),
      }
    ),
  rejectBlock: (id: string, reason?: string) =>
    request(
      `/firewall/requests/${id}/reject`,
      () => ({ success: true, id, status: "rejected" }),
      {
        method: "POST",
        body: JSON.stringify({ reason }),
      }
    ),
  rollbackAction: (actionId: string) =>
    request(
      `/firewall/actions/${actionId}/rollback`,
      () => ({ success: true, actionId }),
      { method: "POST" }
    ),

  // Rules
  rules: () => request<DetectionRule[]>("/rules", () => mock.defaultRules),
  toggleRule: (id: string, enabled: boolean) =>
    request(
      `/rules/${id}`,
      () => ({ id, enabled }),
      {
        method: "PATCH",
        body: JSON.stringify({ enabled }),
      }
    ),
  updateRule: (id: string, updates: Partial<DetectionRule>) =>
    request(
      `/rules/${id}`,
      () => ({ id, ...updates }),
      {
        method: "PATCH",
        body: JSON.stringify(updates),
      }
    ),

  // System Health & Sensors
  services: () => request("/health", () => mock.services),
  testConnection: async () => {
    const res = await fetch(`${API_BASE_URL}/health/ping`);
    if (!res.ok) throw new Error(`Backend ping failed: HTTP ${res.status}`);
    return res.json();
  },

  // Audit Logs & Reports
  auditLogs: () => request("/audit", () => mock.auditLogs),
  reportSummary: () => request("/reports/summary", () => ({ title: "Security Report", period: "Last 24 Hours" })),
  exportEventsCSVUrl: () => `${API_BASE_URL}/reports/export`,

  // Settings & Feedback
  settings: () => request("/settings", () => []),
  updateSetting: (key: string, value: unknown) =>
    request(`/settings/${key}`, () => ({ key, value }), {
      method: "PATCH",
      body: JSON.stringify({ value }),
    }),
  submitFeedback: (category: string, message: string) =>
    request("/feedback", () => ({ status: "received", category, message }), {
      method: "POST",
      body: JSON.stringify({ category, message }),
    }),

  // State checks
  isOffline: () => !lastRequestLive,
  isLive: () => lastRequestLive,
};
