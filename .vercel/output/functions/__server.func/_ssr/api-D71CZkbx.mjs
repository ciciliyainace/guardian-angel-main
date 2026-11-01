import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { l as Slot, m as require_jsx_runtime } from "../_libs/@radix-ui/react-avatar+[...].mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/api-D71CZkbx.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium cursor-pointer transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0", {
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
			destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
			outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
			secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
			ghost: "hover:bg-accent hover:text-accent-foreground",
			link: "text-primary underline-offset-4 hover:underline"
		},
		size: {
			default: "h-9 px-4 py-2",
			sm: "h-8 rounded-md px-3 text-xs",
			lg: "h-10 rounded-md px-8",
			icon: "h-9 w-9"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "default"
	}
});
var Button = import_react.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		className: cn(buttonVariants({
			variant,
			size,
			className
		})),
		ref,
		...props
	});
});
Button.displayName = "Button";
var ATTACK_CATEGORIES = [
	"Port scanning",
	"DoS-like traffic",
	"Brute-force",
	"Suspicious connection",
	"Signature match",
	"Anomalous traffic"
];
var PROTOCOLS = [
	"TCP",
	"UDP",
	"ICMP",
	"Other"
];
var SOURCES = [
	"Rule engine",
	"Random Forest",
	"Isolation Forest",
	"Suricata"
];
function rng(seed) {
	let s = seed;
	return () => {
		s = s * 16807 % 2147483647;
		return (s - 1) / 2147483646;
	};
}
var r = rng(42);
var pick = (arr) => arr[Math.floor(r() * arr.length)];
var ip = (priv = false) => priv ? `192.168.${Math.floor(r() * 4)}.${Math.floor(r() * 254) + 1}` : `${Math.floor(r() * 200) + 20}.${Math.floor(r() * 255)}.${Math.floor(r() * 255)}.${Math.floor(r() * 254) + 1}`;
var BASE = Date.UTC(2026, 9, 10, 3, 0, 0);
var sevFromScore = (s) => s >= 85 ? "critical" : s >= 65 ? "high" : s >= 40 ? "medium" : "low";
var events = Array.from({ length: 120 }, (_, i) => {
	const riskScore = Math.round(r() * 100);
	return {
		id: `EVT-${(10240 + i).toString()}`,
		timestamp: BASE - i * 1e3 * 60 * Math.round(3 + r() * 20),
		sourceIp: ip(),
		destIp: ip(true),
		protocol: pick(PROTOCOLS),
		category: pick(ATTACK_CATEGORIES),
		source: pick(SOURCES),
		severity: sevFromScore(riskScore),
		riskScore,
		status: pick([
			"new",
			"new",
			"acknowledged",
			"investigating",
			"resolved"
		]),
		srcPort: Math.floor(r() * 6e4) + 1024,
		dstPort: pick([
			22,
			80,
			443,
			3389,
			445,
			53,
			8080,
			21
		]),
		duplicates: r() > .75 ? Math.floor(r() * 12) + 1 : 0
	};
});
var trafficSeries = Array.from({ length: 24 }, (_, h) => {
	const benign = Math.round(1800 + Math.sin(h / 3.5) * 600 + r() * 300);
	const suspicious = Math.round(40 + r() * 120 + (h === 14 || h === 15 ? 260 : 0));
	return {
		time: `${String(h).padStart(2, "0")}:00`,
		benign,
		suspicious,
		total: benign + suspicious
	};
});
var categoryCounts = ATTACK_CATEGORIES.map((c) => ({
	category: c,
	count: events.filter((e) => e.category === c).length
}));
var severityCounts = [
	"critical",
	"high",
	"medium",
	"low"
].map((s) => ({
	severity: s,
	count: events.filter((e) => e.severity === s).length
}));
var firewallHistory = Array.from({ length: 7 }, (_, d) => ({
	day: [
		"Mon",
		"Tue",
		"Wed",
		"Thu",
		"Fri",
		"Sat",
		"Sun"
	][d],
	approved: Math.round(2 + r() * 8),
	rejected: Math.round(r() * 4),
	expired: Math.round(r() * 5)
}));
var blockRequests = events.filter((e) => e.severity === "critical" || e.severity === "high").slice(0, 14).map((e, i) => ({
	id: `BLK-${2001 + i}`,
	sourceIp: e.sourceIp,
	reason: `${e.category} (risk ${e.riskScore})`,
	alertId: e.id,
	requestedBy: i % 3 === 0 ? "ciciliya-inace" : "risk-engine",
	requestedAt: e.timestamp,
	durationMin: pick([
		30,
		60,
		120,
		240
	]),
	status: pick([
		"pending",
		"pending",
		"approved",
		"rejected",
		"expired"
	]),
	direction: "Inbound"
}));
var defaultRules = [
	{
		id: "R-001",
		name: "Port scan detection",
		description: "Distinct destination ports contacted by one source",
		category: "Port scan detection",
		severity: "high",
		enabled: true,
		threshold: 25,
		windowSec: 60,
		lastTriggered: BASE - 6e5,
		matches: 142
	},
	{
		id: "R-002",
		name: "Connection-rate threshold",
		description: "New connections per source exceed threshold",
		category: "Connection-rate threshold",
		severity: "critical",
		enabled: true,
		threshold: 300,
		windowSec: 10,
		lastTriggered: BASE - 36e5,
		matches: 38
	},
	{
		id: "R-003",
		name: "Repeated auth failures",
		description: "Failed SSH/RDP logins from same source",
		category: "Repeated authentication failures",
		severity: "high",
		enabled: true,
		threshold: 8,
		windowSec: 120,
		lastTriggered: BASE - 9e5,
		matches: 76
	},
	{
		id: "R-004",
		name: "Suricata ET signatures",
		description: "Escalate Emerging Threats signature hits",
		category: "Known signature alerts",
		severity: "medium",
		enabled: true,
		threshold: 1,
		windowSec: 1,
		lastTriggered: BASE - 2e5,
		matches: 211
	},
	{
		id: "R-005",
		name: "Long low-volume flows",
		description: "Persistent flows with tiny payloads (beacon-like)",
		category: "Suspicious flow patterns",
		severity: "low",
		enabled: false,
		threshold: 600,
		windowSec: 3600,
		lastTriggered: BASE - 864e5,
		matches: 9
	}
];
var models = [
	{
		name: "Random Forest classifier",
		version: "rf-1.3.0",
		dataset: "CIC-IDS2017 (sample split)",
		evaluated: "2026-10-02",
		status: "Loaded",
		classes: [
			"Benign",
			"PortScan",
			"DoS",
			"BruteForce",
			"Bot"
		],
		features: 78
	},
	{
		name: "Isolation Forest anomaly detector",
		version: "if-0.9.2",
		dataset: "Benign baseline (local)",
		evaluated: "2026-10-01",
		status: "Loaded",
		classes: ["Normal", "Anomalous"],
		features: 24
	},
	{
		name: "Hybrid risk engine",
		version: "hre-0.5.0",
		dataset: "Rules + RF + IF outputs",
		evaluated: "2026-10-03",
		status: "Active",
		classes: ["Risk score 0–100"],
		features: 6
	}
];
var sampleMetrics = {
	precision: .94,
	recall: .91,
	f1: .925,
	fpr: .021,
	latencyMs: 3.8
};
var perClassRecall = [
	{
		cls: "Benign",
		recall: .98
	},
	{
		cls: "PortScan",
		recall: .95
	},
	{
		cls: "DoS",
		recall: .93
	},
	{
		cls: "BruteForce",
		recall: .84
	},
	{
		cls: "Bot",
		recall: .71
	}
];
var confusion = {
	labels: [
		"Benign",
		"PortScan",
		"DoS",
		"BruteForce",
		"Bot"
	],
	matrix: [
		[
			4890,
			22,
			31,
			12,
			45
		],
		[
			18,
			951,
			9,
			14,
			8
		],
		[
			27,
			6,
			1862,
			3,
			2
		],
		[
			21,
			30,
			4,
			412,
			23
		],
		[
			41,
			7,
			3,
			6,
			143
		]
	]
};
Array.from({ length: 20 }, (_, i) => ({
	bucket: (-.5 + i * .05).toFixed(2),
	normal: Math.round(Math.max(0, 400 * Math.exp(-((i - 13) ** 2) / 8))),
	anomalous: Math.round(Math.max(0, 60 * Math.exp(-((i - 4) ** 2) / 5)))
}));
var auditLogs = Array.from({ length: 30 }, (_, i) => ({
	id: `AUD-${5e3 + i}`,
	timestamp: BASE - i * 13e5,
	actor: pick([
		"ciciliya-inace",
		"admin",
		"risk-engine",
		"system"
	]),
	action: pick([
		"Approve block",
		"Reject block",
		"Edit rule",
		"Acknowledge alert",
		"Resolve alert",
		"Login",
		"Export CSV"
	]),
	target: pick([
		"BLK-2003",
		"R-002",
		"EVT-10251",
		"EVT-10260",
		"settings",
		"session"
	]),
	result: pick([
		"Success",
		"Success",
		"Success",
		"Denied"
	]),
	reason: pick([
		"Confirmed scan",
		"False positive",
		"Threshold tuning",
		"Routine review",
		"—"
	]),
	related: pick([
		"INC-301",
		"BLK-2005",
		"—",
		"INC-298"
	])
}));
var services = [
	{
		name: "Backend API (FastAPI)",
		status: "Disconnected",
		detail: "Not configured — frontend demo mode"
	},
	{
		name: "PostgreSQL database",
		status: "Unknown",
		detail: "Requires backend"
	},
	{
		name: "Network collector",
		status: "Operational",
		detail: "Simulated stream active"
	},
	{
		name: "Suricata IDS integration",
		status: "Degraded",
		detail: "Simulated: eve.json lag 42s",
		error: "WARN eve.json tail delayed > 30s (simulated)"
	},
	{
		name: "ML classifier",
		status: "Operational",
		detail: "rf-1.3.0 (simulated)"
	},
	{
		name: "Anomaly detector",
		status: "Operational",
		detail: "if-0.9.2 (simulated)"
	},
	{
		name: "Firewall integration",
		status: "Disconnected",
		detail: "Windows Defender helper not connected"
	},
	{
		name: "Event-processing queue",
		status: "Error",
		detail: "Simulated backlog",
		error: "ERR queue consumer timeout after 5000ms (simulated)\n  at worker.consume (queue.py:118)"
	}
];
var notificationsSeed = [
	{
		id: 1,
		title: "Critical: DoS-like traffic",
		body: "Source 103.44.12.9 exceeded connection-rate rule",
		time: BASE - 2e5,
		read: false,
		severity: "critical"
	},
	{
		id: 2,
		title: "Block request pending",
		body: "BLK-2003 awaits administrator approval",
		time: BASE - 9e5,
		read: false,
		severity: "high"
	},
	{
		id: 3,
		title: "Suricata feed degraded",
		body: "Event lag above 30s (simulated)",
		time: BASE - 36e5,
		read: false,
		severity: "medium"
	},
	{
		id: 4,
		title: "Model evaluated",
		body: "rf-1.3.0 sample evaluation completed",
		time: BASE - 86e5,
		read: true,
		severity: "low"
	}
];
var fmtTime = (t) => new Date(t).toISOString().replace("T", " ").slice(0, 16) + " UTC";
function toCSV(rows) {
	if (!rows.length) return "";
	const keys = Object.keys(rows[0] ?? {});
	const esc = (v) => `"${String(v).replace(/"/g, "\"\"")}"`;
	return [keys.join(","), ...rows.map((row) => keys.map((k) => esc(row[k])).join(","))].join("\n");
}
function downloadCSV(name, rows) {
	const blob = new Blob([toCSV(rows)], { type: "text/csv" });
	const a = document.createElement("a");
	a.href = URL.createObjectURL(blob);
	a.download = name;
	a.click();
	URL.revokeObjectURL(a.href);
}
var API_BASE_URL = {
	"BASE_URL": "/",
	"DEV": false,
	"MODE": "production",
	"PROD": true,
	"SSR": true,
	"TSS_DEV_SERVER": "false",
	"TSS_DEV_SSR_STYLES_BASEPATH": "/",
	"TSS_DEV_SSR_STYLES_ENABLED": "true",
	"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
	"TSS_INLINE_CSS_ENABLED": "false",
	"TSS_ROUTER_BASEPATH": "",
	"TSS_SERVER_FN_BASE": "/_serverFn/",
	"VITE_API_BASE_URL": "http://127.0.0.1:8000/api/v1"
}["VITE_API_BASE_URL"] ?? "http://127.0.0.1:8000/api/v1";
var TOKEN_KEY = "sentinelai_access_token";
function getAuthToken() {
	if (typeof window === "undefined") return null;
	return localStorage.getItem(TOKEN_KEY);
}
function setAuthToken(token) {
	if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, token);
}
function clearAuthToken() {
	if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
}
var lastRequestLive = false;
async function request(path, demo, init) {
	const token = getAuthToken();
	const headers = {
		"Content-Type": "application/json",
		...init?.headers || {}
	};
	if (token) headers["Authorization"] = `Bearer ${token}`;
	try {
		const res = await fetch(`${API_BASE_URL}${path}`, {
			...init,
			headers
		});
		if (!res.ok) {
			const errBody = await res.json().catch(() => null);
			throw new Error(errBody?.detail || errBody?.message || `API error ${res.status}: ${res.statusText}`);
		}
		const data = await res.json();
		lastRequestLive = true;
		return data;
	} catch (err) {
		lastRequestLive = false;
		console.warn(`[SentinelAI API] Request to ${path} failed (${err.message}). Falling back to local state.`);
		return demo();
	}
}
var api = {
	login: async (usernameOrEmail, password) => {
		const res = await fetch(`${API_BASE_URL}/auth/login`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				username_or_email: usernameOrEmail,
				password
			})
		});
		if (!res.ok) {
			const err = await res.json().catch(() => null);
			throw new Error(err?.detail || "Invalid username/email or password.");
		}
		const data = await res.json();
		setAuthToken(data.access_token);
		return data;
	},
	register: async (payload) => {
		const res = await fetch(`${API_BASE_URL}/auth/register`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(payload)
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
	getProfile: () => request("/auth/me", () => ({
		id: 1,
		email: "analyst@sentinelai.local",
		username: "ciciliya-inace",
		displayName: "Ciciliya Inace",
		role: "analyst",
		is_active: true,
		email_verified: true,
		auth_providers: ["password"]
	})),
	events: () => request("/events", () => events),
	getEvent: (id) => request(`/events/${id}`, () => {
		const found = events.find((e) => e.id === id);
		if (!found) throw new Error("Event not found");
		return found;
	}),
	trafficSeries: () => request("/analytics/traffic-series", () => trafficSeries),
	overviewSummary: () => request("/analytics/summary", () => {
		const total = trafficSeries.reduce((a, b) => a + b.total, 0);
		const benign = trafficSeries.reduce((a, b) => a + b.benign, 0);
		return {
			totalEvents: total,
			activeAlerts: events.filter((e) => e.status !== "resolved").length,
			criticalThreats: events.filter((e) => e.severity === "critical").length,
			suspiciousConnections: total - benign,
			managedBlocks: blockRequests.filter((b) => b.status === "approved").length,
			detectionRecall: "91%",
			eventsDelta: 6,
			alertsDelta: 12,
			threatsDelta: -4,
			suspiciousDelta: 9
		};
	}),
	categoryCounts: () => request("/analytics/categories", () => categoryCounts),
	severityCounts: () => request("/analytics/severity", () => severityCounts),
	firewallHistory: () => request("/analytics/firewall-history", () => firewallHistory),
	modelMetrics: () => request("/analytics/model-metrics", () => ({
		metrics: sampleMetrics,
		perClassRecall,
		confusion,
		models
	})),
	alerts: () => request("/events", () => events),
	updateAlertStatus: (id, status, notes) => request(`/alerts/${id}`, () => ({
		status,
		id
	}), {
		method: "PATCH",
		body: JSON.stringify({
			status,
			notes
		})
	}),
	blockRequests: () => request("/firewall/requests", () => blockRequests),
	approveBlock: (id, note) => request(`/firewall/requests/${id}/approve`, () => ({
		success: true,
		id,
		status: "approved"
	}), {
		method: "POST",
		body: JSON.stringify({ reviewer_note: note })
	}),
	rejectBlock: (id, reason) => request(`/firewall/requests/${id}/reject`, () => ({
		success: true,
		id,
		status: "rejected"
	}), {
		method: "POST",
		body: JSON.stringify({ reason })
	}),
	rollbackAction: (actionId) => request(`/firewall/actions/${actionId}/rollback`, () => ({
		success: true,
		actionId
	}), { method: "POST" }),
	rules: () => request("/rules", () => defaultRules),
	toggleRule: (id, enabled) => request(`/rules/${id}`, () => ({
		id,
		enabled
	}), {
		method: "PATCH",
		body: JSON.stringify({ enabled })
	}),
	updateRule: (id, updates) => request(`/rules/${id}`, () => ({
		id,
		...updates
	}), {
		method: "PATCH",
		body: JSON.stringify(updates)
	}),
	services: () => request("/health", () => services),
	testConnection: async () => {
		const res = await fetch(`${API_BASE_URL}/health/ping`);
		if (!res.ok) throw new Error(`Backend ping failed: HTTP ${res.status}`);
		return res.json();
	},
	auditLogs: () => request("/audit", () => auditLogs),
	reportSummary: () => request("/reports/summary", () => ({
		title: "Security Report",
		period: "Last 24 Hours"
	})),
	exportEventsCSVUrl: () => `${API_BASE_URL}/reports/export`,
	settings: () => request("/settings", () => []),
	updateSetting: (key, value) => request(`/settings/${key}`, () => ({
		key,
		value
	}), {
		method: "PATCH",
		body: JSON.stringify({ value })
	}),
	submitFeedback: (category, message) => request("/feedback", () => ({
		status: "received",
		category,
		message
	}), {
		method: "POST",
		body: JSON.stringify({
			category,
			message
		})
	}),
	isOffline: () => !lastRequestLive,
	isLive: () => lastRequestLive
};
//#endregion
export { perClassRecall as _, auditLogs as a, severityCounts as b, clearAuthToken as c, events as d, firewallHistory as f, notificationsSeed as g, models as h, api as i, cn as l, getAuthToken as m, ATTACK_CATEGORIES as n, blockRequests as o, fmtTime as p, Button as r, categoryCounts as s, API_BASE_URL as t, downloadCSV as u, sampleMetrics as v, trafficSeries as x, setAuthToken as y };
