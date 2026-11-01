import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader, Panel, SimTag, StatusPill } from "@/components/soc";
import { api } from "@/lib/api";
import { BlockRequest, fmtTime } from "@/lib/mock-data";

const T = "Firewall Management — Sentinel AI";
const D = "Review and approve block requests (simulation only).";
export const Route = createFileRoute("/firewall")({
  head: () => ({ meta: [{ title: T }, { name: "description", content: D }, { property: "og:title", content: T }, { property: "og:description", content: D }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: Firewall,
});
function Firewall() {
  const [reqs, setReqs] = useState<BlockRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const data = await api.blockRequests();
      setReqs(data);
      setIsDemo(api.isOffline());
    } catch {
      toast.error("Failed to load block requests from backend");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const set = async (id: string, status: "approved" | "rejected") => {
    setSubmittingId(id);
    try {
      if (status === "approved") {
        await api.approveBlock(id, "Approved via SentinelAI console");
        toast.success(`${id} approved successfully`);
      } else {
        await api.rejectBlock(id, "Rejected via SentinelAI console");
        toast.info(`${id} rejected`);
      }
      setReqs((r) => r.map((x) => (x.id === id ? { ...x, status } : x)));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update block request";
      toast.error(msg);
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Firewall Management"
        description={D}
        actions={
          <div className="flex items-center gap-2">
            {isDemo && <SimTag label="Demo Data" />}
            <Button variant="outline" size="sm" onClick={loadRequests} disabled={loading}>
              {loading && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
              Refresh
            </Button>
          </div>
        }
      />
      <Panel>
        {loading && reqs.length === 0 ? (
          <div className="flex h-36 items-center justify-center text-sm text-muted-foreground">
            <Loader2 className="mr-2 size-4 animate-spin" /> Loading block requests...
          </div>
        ) : reqs.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No block requests found. All incoming traffic normal.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-muted-foreground">
                <tr>
                  <th className="p-2">ID</th>
                  <th>Source IP</th>
                  <th>Reason</th>
                  <th>Requested</th>
                  <th>Status</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {reqs.map((r) => (
                  <tr key={r.id} className="border-t">
                    <td className="p-2 font-mono text-xs">{r.id}</td>
                    <td className="font-mono">{r.sourceIp}</td>
                    <td>{r.reason}</td>
                    <td className="font-mono text-xs">{fmtTime(r.requestedAt)}</td>
                    <td><StatusPill status={r.status} /></td>
                    <td className="space-x-1 text-right">
                      {r.status === "pending" && (
                        <>
                          <Button
                            size="sm"
                            disabled={submittingId === r.id}
                            onClick={() => set(r.id, "approved")}
                          >
                            {submittingId === r.id ? <Loader2 className="size-3 animate-spin" /> : "Approve"}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={submittingId === r.id}
                            onClick={() => set(r.id, "rejected")}
                          >
                            Reject
                          </Button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}

