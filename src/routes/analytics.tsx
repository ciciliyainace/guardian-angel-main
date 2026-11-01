import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Button } from "@/components/ui/button";
import { PageHeader, Panel, SimTag, axisProps, chartTooltip } from "@/components/soc";
import { api } from "@/lib/api";
import { models as defaultModels, perClassRecall as defaultRecall, sampleMetrics as defaultMetrics } from "@/lib/mock-data";

const T = "AI Analytics — Sentinel AI";
const D = "Model performance for the ML detection pipeline (sample evaluation).";
export const Route = createFileRoute("/analytics")({
  head: () => ({ meta: [{ title: T }, { name: "description", content: D }, { property: "og:title", content: T }, { property: "og:description", content: D }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const [metrics, setMetrics] = useState(defaultMetrics);
  const [recallData, setRecallData] = useState(defaultRecall);
  const [modelList, setModelList] = useState(defaultModels);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await api.modelMetrics();
      if (data.metrics) setMetrics(data.metrics);
      if (data.perClassRecall) setRecallData(data.perClassRecall);
      if (data.models) setModelList(data.models);
      setIsDemo(api.isOffline());
    } catch {
      // keep default values
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-4">
      <PageHeader
        title="AI Analytics"
        description={D}
        actions={
          <div className="flex items-center gap-2">
            {isDemo && <SimTag label="Sample metrics" />}
            <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
              {loading && <Loader2 className="mr-1.5 size-3.5 animate-spin" />}
              Refresh
            </Button>
          </div>
        }
      />
      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {Object.entries(metrics).map(([k, v]) => (
          <Panel key={k}>
            <div className="text-xs uppercase text-muted-foreground">{k}</div>
            <div className="font-mono text-2xl">{v}</div>
          </Panel>
        ))}
      </div>
      <Panel title="Per-class recall">
        <div className="h-64">
          <ResponsiveContainer>
            <BarChart data={recallData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="cls" {...axisProps} />
              <YAxis {...axisProps} domain={[0, 1]} />
              <Tooltip {...chartTooltip} />
              <Bar dataKey="recall" fill="var(--primary)" radius={4} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>
      <div className="grid gap-3 md:grid-cols-3">
        {modelList.map((m) => (
          <Panel key={m.name} title={m.name}>
            <p className="text-xs text-muted-foreground">
              {m.version} · {m.dataset}
            </p>
            <p className="mt-2 text-sm">
              Status: <span className={m.status === "Loaded" || m.status === "Active" ? "font-medium text-success" : "text-warning"}>{m.status}</span> · {m.features} features
            </p>
          </Panel>
        ))}
      </div>
    </div>
  );
}

