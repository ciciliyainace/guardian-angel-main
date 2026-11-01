import { useMemo, useState } from "react";
import { ArrowUpDown, Download, Eye, Search } from "lucide-react";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { ATTACK_CATEGORIES, downloadCSV, fmtTime, type AlertStatus, type SecurityEvent } from "@/lib/mock-data";
import { RiskBar, SeverityBadge, SimTag, StatusPill } from "@/components/soc";

type SortKey = "timestamp" | "riskScore" | "sourceIp";

export function EventsTable({
  data,
  pageSize = 10,
  selectable = false,
  onSelectionChange,
  selected,
  onStatusChange,
  showDuplicates = false,
}: {
  data: SecurityEvent[];
  pageSize?: number;
  selectable?: boolean;
  selected?: Set<string>;
  onSelectionChange?: (s: Set<string>) => void;
  onStatusChange?: (id: string, s: AlertStatus) => void;
  showDuplicates?: boolean;
}) {
  const [q, setQ] = useState("");
  const [sev, setSev] = useState("all");
  const [cat, setCat] = useState("all");
  const [status, setStatus] = useState("all");
  const [range, setRange] = useState("all");
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: "timestamp", dir: -1 });
  const [page, setPage] = useState(0);
  const [detail, setDetail] = useState<SecurityEvent | null>(null);

  const filtered = useMemo(() => {
    const newest = Math.max(...data.map((d) => d.timestamp));
    const hours = range === "1h" ? 1 : range === "6h" ? 6 : range === "24h" ? 24 : Infinity;
    return data
      .filter((e) => (q ? `${e.sourceIp} ${e.destIp} ${e.id}`.includes(q.trim()) : true))
      .filter((e) => sev === "all" || e.severity === sev)
      .filter((e) => cat === "all" || e.category === cat)
      .filter((e) => status === "all" || e.status === status)
      .filter((e) => newest - e.timestamp <= hours * 3.6e6)
      .sort((a, b) => (a[sort.key] > b[sort.key] ? 1 : -1) * sort.dir);
  }, [data, q, sev, cat, status, range, sort]);

  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const rows = filtered.slice(page * pageSize, page * pageSize + pageSize);
  const toggleSort = (key: SortKey) => setSort((s) => ({ key, dir: s.key === key ? (-s.dir as 1 | -1) : -1 }));
  const reset = () => setPage(0);

  const SortHead = ({ k, children }: { k: SortKey; children: string }) => (
    <button onClick={() => toggleSort(k)} className="inline-flex items-center gap-1 hover:text-foreground">
      {children} <ArrowUpDown className="size-3" />
    </button>
  );

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-48 flex-1">
          <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
          <Input value={q} onChange={(e) => { setQ(e.target.value); reset(); }} placeholder="Search IP or event ID…" className="pl-8" aria-label="Search events" />
        </div>
        <Select value={sev} onValueChange={(v) => { setSev(v); reset(); }}>
          <SelectTrigger className="w-32" aria-label="Severity"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All severity</SelectItem>
            {["critical", "high", "medium", "low"].map((s) => <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={cat} onValueChange={(v) => { setCat(v); reset(); }}>
          <SelectTrigger className="w-44" aria-label="Category"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {ATTACK_CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={(v) => { setStatus(v); reset(); }}>
          <SelectTrigger className="w-36" aria-label="Status"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All status</SelectItem>
            {["new", "acknowledged", "investigating", "resolved"].map((s) => <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={range} onValueChange={(v) => { setRange(v); reset(); }}>
          <SelectTrigger className="w-32" aria-label="Date range"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="1h">Last 1h</SelectItem>
            <SelectItem value="6h">Last 6h</SelectItem>
            <SelectItem value="24h">Last 24h</SelectItem>
            <SelectItem value="all">All time</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm" onClick={() => { downloadCSV("sentinel-ai-events.csv", filtered as unknown as Record<string, unknown>[]); toast.success(`Exported ${filtered.length} records (simulated data)`); }}>
          <Download className="size-4" /> CSV
        </Button>
      </div>

      <div className="overflow-x-auto rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {selectable && (
                <TableHead className="w-8">
                  <Checkbox
                    aria-label="Select page"
                    checked={rows.length > 0 && rows.every((r) => selected?.has(r.id))}
                    onCheckedChange={(c) => {
                      const s = new Set(selected);
                      rows.forEach((r) => (c ? s.add(r.id) : s.delete(r.id)));
                      onSelectionChange?.(s);
                    }}
                  />
                </TableHead>
              )}
              <TableHead><SortHead k="timestamp">Timestamp</SortHead></TableHead>
              <TableHead><SortHead k="sourceIp">Source IP</SortHead></TableHead>
              <TableHead>Destination</TableHead>
              <TableHead>Proto</TableHead>
              <TableHead>Detection</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead><SortHead k="riskScore">Risk</SortHead></TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={10} className="py-10 text-center text-sm text-muted-foreground">No events match these filters.</TableCell></TableRow>
            )}
            {rows.map((e) => (
              <TableRow key={e.id}>
                {selectable && (
                  <TableCell>
                    <Checkbox aria-label={`Select ${e.id}`} checked={selected?.has(e.id) ?? false} onCheckedChange={(c) => { const s = new Set(selected); c ? s.add(e.id) : s.delete(e.id); onSelectionChange?.(s); }} />
                  </TableCell>
                )}
                <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">{fmtTime(e.timestamp)}</TableCell>
                <TableCell className="font-mono text-xs">{e.sourceIp}</TableCell>
                <TableCell className="font-mono text-xs">{e.destIp}:{e.dstPort}</TableCell>
                <TableCell className="text-xs">{e.protocol}</TableCell>
                <TableCell className="whitespace-nowrap text-xs">
                  {e.category}
                  {showDuplicates && e.duplicates > 0 && <span className="ml-1.5 rounded bg-muted px-1 text-[10px] text-muted-foreground">×{e.duplicates + 1}</span>}
                </TableCell>
                <TableCell><SeverityBadge severity={e.severity} /></TableCell>
                <TableCell><RiskBar score={e.riskScore} /></TableCell>
                <TableCell><StatusPill status={e.status} /></TableCell>
                <TableCell className="text-right">
                  <Button size="icon" variant="ghost" aria-label="View details" onClick={() => setDetail(e)}><Eye className="size-4" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{filtered.length} records · page {page + 1} of {pages}</span>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>Previous</Button>
          <Button size="sm" variant="outline" disabled={page >= pages - 1} onClick={() => setPage((p) => p + 1)}>Next</Button>
        </div>
      </div>

      <Sheet open={!!detail} onOpenChange={(o) => !o && setDetail(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
          {detail && (
            <>
              <SheetHeader>
                <div className="flex items-center gap-2"><SimTag /><SeverityBadge severity={detail.severity} /></div>
                <SheetTitle className="font-mono">{detail.id}</SheetTitle>
                <SheetDescription>{detail.category} detected by {detail.source}</SheetDescription>
              </SheetHeader>
              <div className="space-y-5 px-4 pb-6 text-sm">
                <dl className="grid grid-cols-2 gap-3">
                  {[
                    ["Timestamp", fmtTime(detail.timestamp)],
                    ["Protocol", detail.protocol],
                    ["Source", `${detail.sourceIp}:${detail.srcPort}`],
                    ["Destination", `${detail.destIp}:${detail.dstPort}`],
                    ["Risk score (0–100, heuristic)", String(detail.riskScore)],
                    ["Detection source", detail.source],
                  ].map(([k, v]) => (
                    <div key={k}><dt className="text-xs text-muted-foreground">{k}</dt><dd className="font-mono text-xs">{v}</dd></div>
                  ))}
                </dl>
                <p className="rounded-md border border-dashed p-3 text-xs text-muted-foreground">
                  Risk score is a combined heuristic, not a calibrated probability. Classifier and anomaly scores are shown separately in Threat Detection.
                </p>
                {onStatusChange && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium">Status</label>
                    <Select value={detail.status} onValueChange={(v) => { onStatusChange(detail.id, v as AlertStatus); setDetail({ ...detail, status: v as AlertStatus }); toast.success(`Status set to ${v}`); }}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {["new", "acknowledged", "investigating", "resolved"].map((s) => <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                    <label className="text-xs font-medium">Investigation notes</label>
                    <Textarea placeholder="Add notes for this alert…" />
                    <Button size="sm" onClick={() => toast.success("Note saved locally (demo)")}>Save note</Button>
                  </div>
                )}
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
