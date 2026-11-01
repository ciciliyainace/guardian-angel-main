import { useState, useEffect } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, AlertTriangle, BellRing, Flame, Gauge, Network, FileText, HeartPulse, ShieldBan } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { Button } from "@/components/ui/button";
import { EventsTable } from "@/components/events-table";
import { Panel, PageHeader, SeverityBadge, SimTag, StatCard, axisProps, chartTooltip } from "@/components/soc";
import { api, type OverviewData } from "@/lib/api";
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
  const [events, setEvents] = useState<SecurityEvent[]>(mockEvents);
  const [trafficSeries, setTrafficSeries] = useState(mockTrafficSeries);
  const [categoryCounts, setCategoryCounts] = useState(mockCategoryCounts);
  const [severityCounts, setSeverityCounts] = useState(mockSeverityCounts);
  const [firewallHistory, setFirewallHistory] = useState(mockFirewallHistory);
  const [summary, setSummary] = useState<OverviewData | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      api.overviewSummary(),
      api.trafficSeries(),
      api.categoryCounts(),
      api.severityCounts(),
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
        setEvents(ev);
        setIsLive(true);
      })
      .catch(() => {
        if (mounted) setIsLive(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const total = summary ? summary.totalEvents : trafficSeries.reduce((a, b) => a + b.total, 0);
  const benign = trafficSeries.reduce((a, b) => a + b.benign, 0);
  const active = summary ? summary.activeAlerts : events.filter((e) => e.status !== "resolved").length;
  const critical = summary ? summary.criticalThreats : events.filter((e) => e.severity === "critical").length;
  const suspicious = summary ? summary.suspiciousConnections : total - benign;
  const blocks = summary ? summary.managedBlocks : mockBlockRequests.filter((b) => b.status === "approved").length;

  const donut = [
    { name: "Benign", value: benign },
    { name: "Suspicious", value: Math.max(0, total - benign) },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Overview"
        description="Last 24 hours across monitored network segments."
        actions={isLive ? <span className="inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success"><span className="size-2 rounded-full bg-success" /> Live backend connected</span> : <SimTag label="Simulated data" />}
      />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatCard icon={Network} label="Total network events" value={total.toLocaleString("en-US")} delta={summary?.eventsDelta ?? 6} />
        <StatCard icon={BellRing} label="Active alerts" value={String(active)} delta={summary?.alertsDelta ?? 12} tone="warning" />
        <StatCard icon={AlertTriangle} label="Critical threats" value={String(critical)} delta={summary?.threatsDelta ?? -4} tone="critical" />
        <StatCard icon={Activity} label="Suspicious connections" value={suspicious.toLocaleString("en-US")} delta={summary?.suspiciousDelta ?? 9} tone="info" />
        <StatCard icon={ShieldBan} label="Managed firewall blocks" value={String(blocks)} tone="success" />
        <StatCard icon={Gauge} label="Detection recall (sample eval)" value={summary?.detectionRecall ?? "91%"} tone="primary" />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Network traffic over time" className="lg:col-span-2" action={!isLive ? <SimTag /> : undefined}>
          <div className="h-64">
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
          </div>
        </Panel>
        <Panel title="Benign vs suspicious">
          <div className="h-64">
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
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Attack categories">
          <div className="h-60">
            <ResponsiveContainer>
              <BarChart data={categoryCounts} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" {...axisProps} />
                <YAxis type="category" dataKey="category" {...axisProps} width={120} />
                <Tooltip {...chartTooltip} />
                <Bar dataKey="count" fill="var(--chart-1)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Alert severity distribution">
          <div className="h-60">
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
          </div>
        </Panel>
        <Panel title="Firewall action history">
          <div className="h-60">
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
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <Panel title="Recent threat activity" className="lg:col-span-1">
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

      <Panel title="Recent security events" action={!isLive ? <SimTag /> : undefined}>
        <EventsTable data={events} />
      </Panel>
    </div>
  );
}
