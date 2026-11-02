// SIMULATED DATA — all values below are generated demo data, not real network activity.
export type Severity = "critical" | "high" | "medium" | "low";
export type AlertStatus = "new" | "acknowledged" | "investigating" | "resolved";

export const ATTACK_CATEGORIES = [
  "Port scanning",
  "DoS-like traffic",
  "Brute-force",
  "Suspicious connection",
  "Signature match",
  "Anomalous traffic",
] as const;
export type AttackCategory = (typeof ATTACK_CATEGORIES)[number];

const PROTOCOLS = ["TCP", "UDP", "ICMP", "Other"] as const;
const SOURCES = ["Rule engine", "Random Forest", "Isolation Forest", "Suricata"] as const;

// deterministic PRNG so SSR and client match
function rng(seed: number) {
  let s = seed;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}
const r = rng(42);
const pick = <T,>(arr: readonly T[]): T => arr[Math.floor(r() * arr.length)] as T;
const ip = (priv = false) =>
  priv
    ? `192.168.${Math.floor(r() * 4)}.${Math.floor(r() * 254) + 1}`
    : `${Math.floor(r() * 200) + 20}.${Math.floor(r() * 255)}.${Math.floor(r() * 255)}.${Math.floor(r() * 254) + 1}`;
const BASE = Date.UTC(2026, 9, 10, 3, 0, 0);
const sevFromScore = (s: number): Severity =>
  s >= 85 ? "critical" : s >= 65 ? "high" : s >= 40 ? "medium" : "low";

export interface SecurityEvent {
  id: string;
  timestamp: number;
  sourceIp: string;
  destIp: string;
  protocol: (typeof PROTOCOLS)[number];
  category: AttackCategory;
  source: (typeof SOURCES)[number];
  severity: Severity;
  riskScore: number;
  status: AlertStatus;
  srcPort: number;
  dstPort: number;
  duplicates: number;
}

export const events: SecurityEvent[] = Array.from({ length: 120 }, (_, i) => {
  const riskScore = Math.round(r() * 100);
  return {
    id: `EVT-${(10240 + i).toString()}`,
    timestamp: BASE - i * 1000 * 60 * Math.round(3 + r() * 20),
    sourceIp: ip(),
    destIp: ip(true),
    protocol: pick(PROTOCOLS),
    category: pick(ATTACK_CATEGORIES),
    source: pick(SOURCES),
    severity: sevFromScore(riskScore),
    riskScore,
    status: pick(["new", "new", "acknowledged", "investigating", "resolved"] as const),
    srcPort: Math.floor(r() * 60000) + 1024,
    dstPort: pick([22, 80, 443, 3389, 445, 53, 8080, 21]),
    duplicates: r() > 0.75 ? Math.floor(r() * 12) + 1 : 0,
  };
});

export const trafficSeries = Array.from({ length: 24 }, (_, h) => {
  const benign = Math.round(1800 + Math.sin(h / 3.5) * 600 + r() * 300);
  const suspicious = Math.round(40 + r() * 120 + (h === 14 || h === 15 ? 260 : 0));
  return { time: `${String(h).padStart(2, "0")}:00`, benign, suspicious, total: benign + suspicious };
});

export const categoryCounts = ATTACK_CATEGORIES.map((c) => ({
  category: c,
  count: events.filter((e) => e.category === c).length,
}));

export const severityCounts = (["critical", "high", "medium", "low"] as Severity[]).map((s) => ({
  severity: s,
  count: events.filter((e) => e.severity === s).length,
}));

export const firewallHistory = Array.from({ length: 7 }, (_, d) => ({
  day: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d],
  approved: Math.round(2 + r() * 8),
  rejected: Math.round(r() * 4),
  expired: Math.round(r() * 5),
}));

export interface BlockRequest {
  id: string;
  sourceIp: string;
  reason: string;
  alertId: string;
  requestedBy: string;
  requestedAt: number;
  durationMin: number;
  status: "pending" | "approved" | "rejected" | "expired";
  direction: "Inbound" | "Outbound";
}

export const blockRequests: BlockRequest[] = events
  .filter((e) => e.severity === "critical" || e.severity === "high")
  .slice(0, 14)
  .map((e, i) => ({
    id: `BLK-${2001 + i}`,
    sourceIp: e.sourceIp,
    reason: `${e.category} (risk ${e.riskScore})`,
    alertId: e.id,
    requestedBy: i % 3 === 0 ? "ciciliya-inace" : "risk-engine",
    requestedAt: e.timestamp,
    durationMin: pick([30, 60, 120, 240]),
    status: pick(["pending", "pending", "approved", "rejected", "expired"] as const),
    direction: "Inbound",
  }));

export interface DetectionRule {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: Severity;
  enabled: boolean;
  threshold: number;
  windowSec: number;
  lastTriggered: number;
  matches: number;
}

export const defaultRules: DetectionRule[] = [
  { id: "R-001", name: "Port scan detection", description: "Distinct destination ports contacted by one source", category: "Port scan detection", severity: "high", enabled: true, threshold: 25, windowSec: 60, lastTriggered: BASE - 6e5, matches: 142 },
  { id: "R-002", name: "Connection-rate threshold", description: "New connections per source exceed threshold", category: "Connection-rate threshold", severity: "critical", enabled: true, threshold: 300, windowSec: 10, lastTriggered: BASE - 3.6e6, matches: 38 },
  { id: "R-003", name: "Repeated auth failures", description: "Failed SSH/RDP logins from same source", category: "Repeated authentication failures", severity: "high", enabled: true, threshold: 8, windowSec: 120, lastTriggered: BASE - 9e5, matches: 76 },
  { id: "R-004", name: "Suricata ET signatures", description: "Escalate Emerging Threats signature hits", category: "Known signature alerts", severity: "medium", enabled: true, threshold: 1, windowSec: 1, lastTriggered: BASE - 2e5, matches: 211 },
  { id: "R-005", name: "Long low-volume flows", description: "Persistent flows with tiny payloads (beacon-like)", category: "Suspicious flow patterns", severity: "low", enabled: false, threshold: 600, windowSec: 3600, lastTriggered: BASE - 8.64e7, matches: 9 },
];

export const models = [
  { name: "Random Forest classifier", version: "rf-1.3.0", dataset: "CIC-IDS2017 (sample split)", evaluated: "2026-10-02", status: "Loaded", classes: ["Benign", "PortScan", "DoS", "BruteForce", "Bot"], features: 78 },
  { name: "Isolation Forest anomaly detector", version: "if-0.9.2", dataset: "Benign baseline (local)", evaluated: "2026-10-01", status: "Loaded", classes: ["Normal", "Anomalous"], features: 24 },
  { name: "Hybrid risk engine", version: "hre-0.5.0", dataset: "Rules + RF + IF outputs", evaluated: "2026-10-03", status: "Active", classes: ["Risk score 0–100"], features: 6 },
];

export const sampleMetrics = { precision: 0.94, recall: 0.91, f1: 0.925, fpr: 0.021, latencyMs: 3.8 };
export const perClassRecall = [
  { cls: "Benign", recall: 0.98 }, { cls: "PortScan", recall: 0.95 }, { cls: "DoS", recall: 0.93 },
  { cls: "BruteForce", recall: 0.84 }, { cls: "Bot", recall: 0.71 },
];
export const confusion = {
  labels: ["Benign", "PortScan", "DoS", "BruteForce", "Bot"],
  matrix: [
    [4890, 22, 31, 12, 45],
    [18, 951, 9, 14, 8],
    [27, 6, 1862, 3, 2],
    [21, 30, 4, 412, 23],
    [41, 7, 3, 6, 143],
  ],
};
export const anomalyDistribution = Array.from({ length: 20 }, (_, i) => ({
  bucket: (-0.5 + i * 0.05).toFixed(2),
  normal: Math.round(Math.max(0, 400 * Math.exp(-((i - 13) ** 2) / 8))),
  anomalous: Math.round(Math.max(0, 60 * Math.exp(-((i - 4) ** 2) / 5))),
}));

export const auditLogs = Array.from({ length: 30 }, (_, i) => ({
  id: `AUD-${5000 + i}`,
  timestamp: BASE - i * 1.3e6,
  actor: pick(["ciciliya-inace", "admin", "risk-engine", "system"]),
  action: pick(["Approve block", "Reject block", "Edit rule", "Acknowledge alert", "Resolve alert", "Login", "Export CSV"]),
  target: pick(["BLK-2003", "R-002", "EVT-10251", "EVT-10260", "settings", "session"]),
  result: pick(["Success", "Success", "Success", "Denied"]),
  reason: pick(["Confirmed scan", "False positive", "Threshold tuning", "Routine review", "—"]),
  related: pick(["INC-301", "BLK-2005", "—", "INC-298"]),
}));

export type HealthStatus = "Operational" | "Degraded" | "Disconnected" | "Error" | "Unknown";
export const services: { name: string; status: HealthStatus; detail: string; error?: string }[] = [
  { name: "Backend API (FastAPI)", status: "Disconnected", detail: "Not configured — frontend demo mode" },
  { name: "PostgreSQL database", status: "Unknown", detail: "Requires backend" },
  { name: "Network collector", status: "Operational", detail: "Simulated stream active" },
  { name: "Suricata IDS integration", status: "Degraded", detail: "Simulated: eve.json lag 42s", error: "WARN eve.json tail delayed > 30s (simulated)" },
  { name: "ML classifier", status: "Operational", detail: "rf-1.3.0 (simulated)" },
  { name: "Anomaly detector", status: "Operational", detail: "if-0.9.2 (simulated)" },
  { name: "Firewall integration", status: "Disconnected", detail: "Windows Defender helper not connected" },
  { name: "Event-processing queue", status: "Error", detail: "Simulated backlog", error: "ERR queue consumer timeout after 5000ms (simulated)\n  at worker.consume (queue.py:118)" },
];

export const notificationsSeed = [
  { id: 1, title: "Critical: DoS-like traffic", body: "Source 103.44.12.9 exceeded connection-rate rule", time: BASE - 2e5, read: false, severity: "critical" as Severity },
  { id: 2, title: "Block request pending", body: "BLK-2003 awaits administrator approval", time: BASE - 9e5, read: false, severity: "high" as Severity },
  { id: 3, title: "Suricata feed degraded", body: "Event lag above 30s (simulated)", time: BASE - 3.6e6, read: false, severity: "medium" as Severity },
  { id: 4, title: "Model evaluated", body: "rf-1.3.0 sample evaluation completed", time: BASE - 8.6e6, read: true, severity: "low" as Severity },
];

export const fmtTime = (t: number) =>
  new Date(t).toISOString().replace("T", " ").slice(0, 16) + " UTC";

export function toCSV(rows: Record<string, unknown>[]) {
  if (!rows.length) return "";
  const keys = Object.keys(rows[0] ?? {});
  const esc = (v: unknown) => `"${String(v).replace(/"/g, '""')}"`;
  return [keys.join(","), ...rows.map((row) => keys.map((k) => esc(row[k])).join(","))].join("\n");
}

export function downloadCSV(name: string, rows: Record<string, unknown>[]) {
  const blob = new Blob([toCSV(rows)], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}
