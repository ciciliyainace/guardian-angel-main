import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader, Panel, SimTag } from "@/components/soc";
import { api } from "@/lib/api";
import { auditLogs as defaultAuditLogs, downloadCSV, events as defaultEvents } from "@/lib/mock-data";

const T = "Reports & Logs — Sentinel AI";
const D = "Export events and review the audit trail.";
export const Route = createFileRoute("/reports")({
  head: () => ({ meta: [{ title: T }, { name: "description", content: D }, { property: "og:title", content: T }, { property: "og:description", content: D }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: ReportsPage,
});

function ReportsPage() {
  const [logs, setLogs] = useState(defaultAuditLogs);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.auditLogs();
      if (Array.isArray(data) && data.length > 0) {
        setLogs(data);
      }
      setIsDemo(api.isOffline());
    } catch {
      // keep default logs
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const handleExportCSV = async () => {
    try {
      const liveEvents = await api.events();
      if (liveEvents && liveEvents.length > 0) {
        downloadCSV("events.csv", liveEvents as unknown as Record<string, unknown>[]);
        return;
      }
    } catch {
      // fallback
    }
    downloadCSV("events.csv", defaultEvents as unknown as Record<string, unknown>[]);
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Reports & Logs"
        description={D}
        actions={
          <div className="flex items-center gap-2">
            {isDemo && <SimTag label="Demo Logs" />}
            <Button variant="outline" size="sm" onClick={handleExportCSV}>
              <Download className="mr-1.5 size-3.5" />
              Events CSV
            </Button>
            <Button variant="outline" size="sm" onClick={() => window.print()}>
              Print
            </Button>
            <Button variant="outline" size="sm" onClick={loadLogs} disabled={loading}>
              {loading && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
              Refresh
            </Button>
          </div>
        }
      />
      <Panel title="Audit log">
        {loading && logs.length === 0 ? (
          <div className="flex h-36 items-center justify-center text-sm text-muted-foreground">
            <Loader2 className="mr-2 size-4 animate-spin" /> Loading audit trail...
          </div>
        ) : (
          <ul className="divide-y text-sm">
            {logs.map((l, i) => (
              <li key={i} className="py-2 font-mono text-xs">
                {typeof l === "object" && l !== null
                  ? Object.values(l).map(String).join(" · ")
                  : String(l)}
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}

