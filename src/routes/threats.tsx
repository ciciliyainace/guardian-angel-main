import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { EventsTable } from "@/components/events-table";
import { PageHeader, Panel, SimTag } from "@/components/soc";
import { events as seedEvents, type SecurityEvent } from "@/lib/mock-data";
import { api } from "@/lib/api";

const T = "Threat Detection — Sentinel AI";
const D = "High-risk detections from rules and ML models.";
export const Route = createFileRoute("/threats")({
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
  component: ThreatsPage,
});

function ThreatsPage() {
  const [events, setEvents] = useState<SecurityEvent[]>(seedEvents);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let mounted = true;
    api
      .events()
      .then((res) => {
        if (!mounted) return;
        setEvents(res);
        setIsLive(true);
      })
      .catch(() => {
        if (mounted) setIsLive(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const threats = events.filter((e) => e.severity === "critical" || e.severity === "high");

  return (
    <div className="space-y-4">
      <PageHeader
        title="Threat Detection"
        description={D}
        actions={isLive ? <span className="inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success"><span className="size-2 rounded-full bg-success" /> Live detections</span> : <SimTag />}
      />
      <Panel title="Critical & high detections">
        <EventsTable data={threats} showDuplicates />
      </Panel>
    </div>
  );
}
