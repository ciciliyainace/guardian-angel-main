import { useState, useEffect } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, AlertTriangle, BellRing, Flame, Gauge, Network, FileText, HeartPulse, ShieldBan, Radio, ShieldCheck, Terminal } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { Button } from "@/components/ui/button";
import { EventsTable } from "@/components/events-table";
import { Panel, PageHeader, SeverityBadge, SimTag, StatCard, axisProps, chartTooltip } from "@/components/soc";
import { api, type OverviewData, type DetailedMonitoringHealth } from "@/lib/api";
import {
  blockRequests as mockBlockRequests,
  categoryCounts as mockCategoryCounts,
  events as mockEvents,
  firewallHistory as mockFirewallHistory,
  fmtTime,
  severityCounts as mockSeverityCounts,
  trafficSeries as mockTrafficSeries,
  type SecurityEvent,
} from "@/lib/mock-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Overview — Sentinel AI Security Center" },
      { name: "description", content: "Command-center overview of network events, alerts, threats and firewall blocks." },
      { property: "og:title", content: "Overview — Sentinel AI Security Center" },
      { property: "og:description", content: "Command-center overview of network events, alerts, threats and firewall blocks." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Overview,
});

const sevColor: Record<string, string> = {
  critical: "var(--chart-4)",
  high: "var(--chart-3)",
  medium: "var(--chart-5)",
  low: "var(--chart-2)",
};

function Overview() {
  const [dataOrigin, setDataOrigin] = useState<"live" | "simulated" | "all">("live");
  const [timeRange, setTimeRange] = useState<"15m" | "1h" | "24h" | "7d">("24h");
  const [health, setHealth] = useState<DetailedMonitoringHealth | null>(null);

  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [trafficSeries, setTrafficSeries] = useState<typeof mockTrafficSeries>([]);
  const [categoryCounts, setCategoryCounts] = useState<typeof mockCategoryCounts>([]);
  const [severityCounts, setSeverityCounts] = useState<typeof mockSeverityCounts>([]);
  const [firewallHistory, setFirewallHistory] = useState<typeof mockFirewallHistory>([]);
  const [summary, setSummary] = useState<OverviewData | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let mounted = true;
    // Check detailed system and sensor health
    api.detailedHealth()
      .then((h) => {
        if (mounted) setHealth(h);
      })
      .catch(() => {
        if (mounted) setHealth(null);
      });

    // Fetch metrics filtered by origin and timeRange
    Promise.all([
      api.overviewSummary(dataOrigin, timeRange),
      api.trafficSeries(dataOrigin, timeRange),
      api.categoryCounts(dataOrigin, timeRange),
      api.severityCounts(dataOrigin, timeRange),
      api.firewallHistory(),
      api.events(),
    ])
      .then(([s, t, c, sev, f, ev]) => {
        if (!mounted) return;
        setSummary(s);
        setTrafficSeries(t as typeof mockTrafficSeries);
        setCategoryCounts(c as typeof mockCategoryCounts);
        setSeverityCounts(sev as typeof mockSeverityCounts);
        setFirewallHistory(f as typeof mockFirewallHistory);

        // Filter events by origin if applicable
        if (dataOrigin === "live") {
          setEvents(ev.filter((e) => (e as any).data_origin === "live" || (e as any).dataOrigin === "live" || !e.id.startsWith("SIM-")));
        } else if (dataOrigin === "simulated") {
          setEvents(ev.filter((e) => (e as any).data_origin === "simulated" || e.id.startsWith("SIM-")));
        } else {
          setEvents(ev);
        }

        setIsLive(true);
      })
      .catch(() => {
        if (!mounted) return;
        setIsLive(false);
        if (dataOrigin === "simulated") {
          setEvents(mockEvents);
          setTrafficSeries(mockTrafficSeries);
          setCategoryCounts(mockCategoryCounts);
          setSeverityCounts(mockSeverityCounts);
          setFirewallHistory(mockFirewallHistory);
        } else {
          setEvents([]);
          setTrafficSeries([]);
          setCategoryCounts([]);
          setSeverityCounts([]);
          setFirewallHistory([]);
        }
      });

    return () => {
      mounted = false;
    };
  }, [dataOrigin, timeRange]);

  const total = summary ? summary.totalEvents : 0;
  const benign = trafficSeries.reduce((a, b) => a + b.benign, 0);
  const active = summary ? summary.activeAlerts : 0;
  const critical = summary ? summary.criticalThreats : 0;
  const suspicious = summary ? summary.suspiciousConnections : 0;
  const blocks = summary ? summary.managedBlocks : 0;

  const donut = [
    { name: "Benign", value: benign },
    { name: "Suspicious", value: Math.max(0, total - benign) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Security Overview</h1>
          <p className="text-sm text-muted-foreground">
            {dataOrigin === "live"
              ? `Real network telemetry captured over the last ${timeRange}.`
              : dataOrigin === "simulated"
              ? "Synthetically generated security events for testing and evaluation."
              : "Unified view of live telemetry and test scenarios."}
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Origin Switcher */}
          <div className="flex rounded-lg border bg-muted/30 p-0.5 text-xs font-medium">
            <button
              onClick={() => setDataOrigin("live")}
              className={`rounded px-2.5 py-1 transition-colors ${
                dataOrigin === "live"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Live Telemetry
            </button>
            <button
              onClick={() => setDataOrigin("simulated")}
              className={`rounded px-2.5 py-1 transition-colors ${
                dataOrigin === "simulated"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Simulation Mode
            </button>
            <button
              onClick={() => setDataOrigin("all")}
              className={`rounded px-2.5 py-1 transition-colors ${
                dataOrigin === "all"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              All
            </button>
          </div>

          {/* Time Range Switcher */}
          <div className="flex rounded-lg border bg-muted/30 p-0.5 text-xs font-medium">
            {(["15m", "1h", "24h", "7d"] as const).map((r) => (
              <button
                key={r}
                onClick={() => setTimeRange(r)}
                className={`rounded px-2 py-1 transition-colors ${
                  timeRange === r
                    ? "bg-primary text-primary-foreground font-semibold shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Live Monitoring Health Status Banner */}
      {dataOrigin === "live" && (
        <div className={`flex flex-col gap-2 rounded-lg border p-4 text-xs sm:flex-row sm:items-center sm:justify-between ${
          health?.overall_status === "LIVE"
            ? "border-success/40 bg-success/5 text-success-foreground"
            : health?.overall_status === "STANDBY"
            ? "border-primary/40 bg-primary/5 text-foreground"
            : "border-warning/40 bg-warning/5 text-foreground"
        }`}>
          <div className="flex items-center gap-3">
            <div className={`grid size-8 place-items-center rounded-full ${
              health?.overall_status === "LIVE"
                ? "bg-success/20 text-success"
                : health?.overall_status === "STANDBY"
                ? "bg-primary/20 text-primary"
                : "bg-warning/20 text-warning"
            }`}>
              {health?.overall_status === "LIVE" ? (
                <Radio className="size-4 animate-pulse text-success" />
              ) : health?.overall_status === "STANDBY" ? (
                <Activity className="size-4 text-primary" />
              ) : (
                <AlertTriangle className="size-4 text-warning" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 font-semibold">
                <span>
                  {health?.overall_status === "LIVE"
                    ? `Live Host Network Monitoring Active (${health.active_sensor_count} Sensor connected)`
                    : health?.overall_status === "STANDBY"
                    ? "Sensor Connected in Standby"
                    : "No Live Sensor Connected"}
                </span>
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                  health?.overall_status === "LIVE"
                    ? "bg-success/20 text-success"
                    : health?.overall_status === "STANDBY"
                    ? "bg-primary/20 text-primary"
                    : "bg-warning/20 text-warning"
                }`}>
                  {health?.overall_status || "OFFLINE"}
                </span>
              </div>
              <p className="text-muted-foreground text-[11px] mt-0.5">
                {health?.message || "Install and start the host sensor agent to begin genuine live telemetry collection."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 font-mono text-[11px]">
            <span className={`inline-flex items-center gap-1.5 ${health?.suricata_operational ? "text-success" : "text-muted-foreground"}`}>
              <span className={`size-1.5 rounded-full ${health?.suricata_operational ? "bg-success" : "bg-muted"}`} />
              Suricata IDS: {health?.suricata_operational ? "Operational" : "Standby"}
            </span>
            <span className={`inline-flex items-center gap-1.5 ${health?.windows_socket_operational ? "text-success" : "text-muted-foreground"}`}>
              <span className={`size-1.5 rounded-full ${health?.windows_socket_operational ? "bg-success" : "bg-muted"}`} />
              Winsock: {health?.windows_socket_operational ? "Active" : "Standby"}
            </span>
          </div>
        </div>
      )}

      {/* Empty State Banner when 0 Live Events */}
      {dataOrigin === "live" && total === 0 && (
        <div className="rounded-lg border border-dashed border-border bg-muted/10 p-6 text-center">
          <Terminal className="mx-auto size-8 text-muted-foreground" />
          <h3 className="mt-2 text-sm font-semibold">Waiting for Network Telemetry</h3>
          <p className="mx-auto mt-1 max-w-md text-xs text-muted-foreground">
            No live telemetry events have been received within the last {timeRange}.
            Run the SentinelAI Sensor Agent on your Windows machine to capture genuine socket connections and Suricata EVE records.
          </p>
          <div className="mx-auto mt-3 flex items-center justify-center gap-2">
            <code className="rounded border bg-muted px-3 py-1 font-mono text-xs">
              python sensor_agent/sensor_agent.py
            </code>
          </div>
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatCard icon={Network} label="Total network events" value={total.toLocaleString("en-US")} delta={summary?.eventsDelta ?? 0} />
        <StatCard icon={BellRing} label="Active alerts" value={String(active)} delta={summary?.alertsDelta ?? 0} tone="warning" />
        <StatCard icon={AlertTriangle} label="Critical threats" value={String(critical)} delta={summary?.threatsDelta ?? 0} tone="critical" />
        <StatCard icon={Activity} label="Suspicious connections" value={suspicious.toLocaleString("en-US")} delta={summary?.suspiciousDelta ?? 0} tone="info" />
        <StatCard icon={ShieldBan} label="Managed firewall blocks" value={String(blocks)} tone="success" />
        <StatCard icon={Gauge} label="Detection recall" value={summary?.detectionRecall ?? "--"} tone="primary" />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Network traffic over time" className="lg:col-span-2" action={dataOrigin === "simulated" ? <SimTag /> : undefined}>
          <div className="h-64">
            {trafficSeries.length > 0 ? (
              <ResponsiveContainer>
                <AreaChart data={trafficSeries}>
                  <defs>
                    <linearGradient id="gb" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="time" {...axisProps} />
                  <YAxis {...axisProps} width={40} />
                  <Tooltip {...chartTooltip} />
                  <Area type="monotone" dataKey="benign" stroke="var(--chart-1)" fill="url(#gb)" strokeWidth={2} />
                  <Area type="monotone" dataKey="suspicious" stroke="var(--chart-4)" fill="var(--chart-4)" fillOpacity={0.15} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center text-xs text-muted-foreground">
                No traffic timeseries for this time window
              </div>
            )}
          </div>
        </Panel>
        <Panel title="Benign vs suspicious">
          <div className="h-64">
            {total > 0 ? (
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={donut} dataKey="value" innerRadius={60} outerRadius={90} paddingAngle={2} stroke="none">
                    <Cell fill="var(--chart-1)" />
                    <Cell fill="var(--chart-4)" />
                  </Pie>
                  <Tooltip {...chartTooltip} />
                  <Legend wrapperStyle={{ fontSize: 12 }} formatter={(value) => <span className="text-muted-foreground">{value}</span>} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center text-xs text-muted-foreground">
                No active flows detected
              </div>
            )}
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Attack categories">
          <div className="h-60">
            {categoryCounts.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={categoryCounts} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" {...axisProps} />
                  <YAxis type="category" dataKey="category" {...axisProps} width={120} />
                  <Tooltip {...chartTooltip} />
                  <Bar dataKey="count" fill="var(--chart-1)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center text-xs text-muted-foreground">
                No category data recorded
              </div>
            )}
          </div>
        </Panel>
        <Panel title="Alert severity distribution">
          <div className="h-60">
            {severityCounts.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={severityCounts}>
                  <XAxis dataKey="severity" {...axisProps} />
                  <YAxis {...axisProps} width={30} />
                  <Tooltip {...chartTooltip} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {severityCounts.map((s) => (
                      <Cell key={s.severity} fill={sevColor[s.severity] || "var(--chart-1)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center text-xs text-muted-foreground">
                No severity counts recorded
              </div>
            )}
          </div>
        </Panel>
        <Panel title="Firewall action history">
          <div className="h-60">
            {firewallHistory.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={firewallHistory}>
                  <XAxis dataKey="day" {...axisProps} />
                  <YAxis {...axisProps} width={25} />
                  <Tooltip {...chartTooltip} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="approved" stackId="a" fill="var(--chart-2)" />
                  <Bar dataKey="rejected" stackId="a" fill="var(--chart-4)" />
                  <Bar dataKey="expired" stackId="a" fill="var(--chart-5)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center text-xs text-muted-foreground">
                No firewall history in this window
              </div>
            )}
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <Panel title="Recent threat activity" className="lg:col-span-1">
          {events.filter((e) => e.severity !== "low").length > 0 ? (
            <ol className="relative space-y-4 border-l pl-4">
              {events.filter((e) => e.severity !== "low").slice(0, 6).map((e) => (
                <li key={e.id} className="text-xs">
                  <span className="absolute -left-1 mt-1 size-2 rounded-full bg-primary" />
                  <div className="flex items-center gap-2 font-medium">
                    {e.category} <SeverityBadge severity={e.severity} />
                  </div>
                  <div className="font-mono text-muted-foreground">
                    {e.sourceIp} · {fmtTime(e.timestamp).slice(11)}
                  </div>
                </li>
              ))}
            </ol>
          ) : (
            <div className="py-6 text-center text-xs text-muted-foreground">
              No recent threats detected
            </div>
          )}
        </Panel>
        <Panel title="Quick actions" className="lg:col-span-3">
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            <Button asChild variant="outline" className="justify-start">
              <Link to="/alerts"><BellRing />View all alerts</Link>
            </Button>
            <Button asChild variant="outline" className="justify-start">
              <Link to="/firewall"><Flame />Review block requests</Link>
            </Button>
            <Button asChild variant="outline" className="justify-start">
              <Link to="/reports"><FileText />Generate report</Link>
            </Button>
            <Button asChild variant="outline" className="justify-start">
              <Link to="/health"><HeartPulse />Open system health</Link>
            </Button>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            The interface never executes security actions directly — all actions route through an authorized backend once connected.
          </p>
        </Panel>
      </div>

      <Panel title="Recent network events" action={dataOrigin === "simulated" ? <SimTag /> : undefined}>
        <EventsTable data={events} />
      </Panel>
    </div>
  );
}
