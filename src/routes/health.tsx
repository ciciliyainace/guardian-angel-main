import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { HealthBadge, PageHeader, Panel, SimTag } from "@/components/soc";
import { api } from "@/lib/api";
import { HealthStatus } from "@/lib/mock-data";

interface ServiceHealth {
  name: string;
  status: HealthStatus;
  detail: string;
  error?: string;
}

const T = "System Health — Sentinel AI";
const D = "Status of sensors, models and backend services.";
export const Route = createFileRoute("/health")({
  head: () => ({ meta: [{ title: T }, { name: "description", content: D }, { property: "og:title", content: T }, { property: "og:description", content: D }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: HealthPage,
});

function HealthPage() {
  const [servicesList, setServicesList] = useState<ServiceHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [isDemo, setIsDemo] = useState(false);

  const loadHealth = async () => {
    setLoading(true);
    try {
      const data = await api.services();
      setServicesList(data);
      setIsDemo(api.isOffline());
    } catch {
      toast.error("Failed to load health status from backend");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
  }, []);

  const handleTestConnection = async () => {
    setTesting(true);
    try {
      await api.testConnection();
      toast.success("Backend connection verified");
      await loadHealth();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Connection failed";
      toast.error(msg);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="System Health"
        description={D}
        actions={
          <div className="flex items-center gap-2">
            {isDemo && <SimTag label="Demo Health" />}
            <Button
              variant="outline"
              disabled={testing || loading}
              onClick={handleTestConnection}
            >
              {testing ? <Loader2 className="mr-1.5 size-3.5 animate-spin" /> : null}
              Test connection
            </Button>
          </div>
        }
      />
      {loading && servicesList.length === 0 ? (
        <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
          <Loader2 className="mr-2 size-4 animate-spin" /> Checking system services...
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {servicesList.map((s) => (
            <Panel key={s.name} title={s.name} action={<HealthBadge status={s.status} />}>
              <p className="text-sm text-muted-foreground">{s.detail}</p>
              {s.error && <p className="mt-1 font-mono text-xs text-critical">{s.error}</p>}
            </Panel>
          ))}
        </div>
      )}
    </div>
  );
}

