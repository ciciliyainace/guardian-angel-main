import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { EventsTable } from "@/components/events-table";
import { PageHeader, Panel, SimTag } from "@/components/soc";
import { events as seed, type AlertStatus, type SecurityEvent } from "@/lib/mock-data";
import { api } from "@/lib/api";
import { toast } from "sonner";

const T = "Security Alerts — Sentinel AI";
const D = "Triage, acknowledge and resolve security alerts.";
export const Route = createFileRoute("/alerts")({
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
  component: Alerts,
});

function Alerts() {
  const [data, setData] = useState<SecurityEvent[]>(seed);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let mounted = true;
    api
      .events()
      .then((res) => {
        if (!mounted) return;
        setData(res);
        setIsLive(true);
      })
      .catch(() => {
        if (mounted) setIsLive(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const handleStatusChange = (id: string, s: AlertStatus) => {
    setData((d) => d.map((e) => (e.id === id ? { ...e, status: s } : e)));
    api
      .updateAlertStatus(id, s)
      .then(() => toast.success(`Alert ${id} status updated to ${s}`))
      .catch((err: Error) => toast.error(`Failed to update status: ${err.message}`));
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Security Alerts"
        description={D}
        actions={isLive ? <span className="inline-flex items-center gap-1.5 rounded border border-success/40 bg-success/10 px-2 py-0.5 text-xs font-medium text-success"><span className="size-2 rounded-full bg-success" /> Live alerts</span> : <SimTag />}
      />
      <Panel>
        <EventsTable
          data={data}
          selectable
          selected={selected}
          onSelectionChange={setSelected}
          onStatusChange={handleStatusChange}
        />
      </Panel>
    </div>
  );
}
