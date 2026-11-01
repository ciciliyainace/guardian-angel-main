import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EventsTable } from "@/components/events-table";
import { PageHeader, Panel, SimTag, axisProps, chartTooltip } from "@/components/soc";
import { events as seedEvents, trafficSeries as seedTraffic, type SecurityEvent } from "@/lib/mock-data";
import { api } from "@/lib/api";

const T = "Live Traffic — Sentinel AI";
const D = "Real-time network flow monitoring and volumetric inspection.";
export const Route = createFileRoute("/traffic")({
  head: () => ({
    meta: [
      { title: T },
      { name: "description", content: D },
      { property: "og:title", content: T },
      { property: "og:description", content: D },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: TrafficPage,
});

function TrafficPage() {
  const [traffic, setTraffic] = useState(seedTraffic);
  const [events, setEvents] = useState<SecurityEvent[]>(seedEvents);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let mounted = true;
    Promise.all([api.trafficSeries(), api.events()])
      .then(([t, ev]) => {
        if (!mounted) return;
        setTraffic(t as typeof seedTraffic);
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

  return (
    <div className="space-y-4">
      <PageHeader
        title="Live Traffic"
        description={D}
        actions={isLive ? <span className="inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success"><span className="size-2 rounded-full bg-success" /> Live stream active</span> : <SimTag />}
      />
      <Panel title="Traffic volume (24h)">
        <div className="h-64">
          <ResponsiveContainer>
            <AreaChart data={traffic}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="time" {...axisProps} />
              <YAxis {...axisProps} />
              <Tooltip {...chartTooltip} />
              <Area dataKey="total" stroke="var(--primary)" fill="var(--primary)" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Panel>
      <Panel title="Recent flows">
        <EventsTable data={events} />
      </Panel>
    </div>
  );
}
