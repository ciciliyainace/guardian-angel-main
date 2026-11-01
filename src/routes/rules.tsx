import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { PageHeader, Panel, SeverityBadge, SimTag } from "@/components/soc";
import { api } from "@/lib/api";
import { DetectionRule } from "@/lib/mock-data";

const T = "Detection Rules — Sentinel AI";
const D = "Enable, disable and tune rule-based detections.";
export const Route = createFileRoute("/rules")({
  head: () => ({ meta: [{ title: T }, { name: "description", content: D }, { property: "og:title", content: T }, { property: "og:description", content: D }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: Rules,
});
function Rules() {
  const [rules, setRules] = useState<DetectionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadRules = async () => {
    setLoading(true);
    try {
      const data = await api.rules();
      setRules(data);
      setIsDemo(api.isOffline());
    } catch {
      toast.error("Failed to load detection rules from backend");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  const handleToggle = async (rule: DetectionRule, enabled: boolean) => {
    setUpdatingId(rule.id);
    // Optimistic update
    setRules((all) => all.map((x) => (x.id === rule.id ? { ...x, enabled } : x)));
    try {
      await api.toggleRule(rule.id, enabled);
      toast.success(`Rule ${rule.id} ${enabled ? "enabled" : "disabled"}`);
    } catch (err: unknown) {
      // Revert on failure
      setRules((all) => all.map((x) => (x.id === rule.id ? { ...x, enabled: !enabled } : x)));
      const msg = err instanceof Error ? err.message : "Failed to toggle rule";
      toast.error(msg);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Detection Rules"
        description={D}
        actions={
          <div className="flex items-center gap-2">
            {isDemo && <SimTag label="Demo Rules" />}
            <Button variant="outline" size="sm" onClick={loadRules} disabled={loading}>
              {loading && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
              Refresh
            </Button>
          </div>
        }
      />
      <div className="grid gap-3">
        {loading && rules.length === 0 ? (
          <div className="flex h-36 items-center justify-center text-sm text-muted-foreground">
            <Loader2 className="mr-2 size-4 animate-spin" /> Loading rules...
          </div>
        ) : rules.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No detection rules configured.
          </div>
        ) : (
          rules.map((r) => (
            <Panel key={r.id}>
              <div className="flex items-center gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 font-medium">
                    <span className="font-mono text-xs text-muted-foreground">{r.id}</span>
                    {r.name}
                    <SeverityBadge severity={r.severity} />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {r.description} · threshold {r.threshold} / {r.windowSec}s · {r.matches} matches
                  </p>
                </div>
                <Switch
                  aria-label={`Toggle ${r.name}`}
                  checked={r.enabled}
                  disabled={updatingId === r.id}
                  onCheckedChange={(v) => handleToggle(r, v)}
                />
              </div>
            </Panel>
          ))
        )}
      </div>
    </div>
  );
}

