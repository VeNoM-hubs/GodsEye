import { Bug, Wifi, WifiOff, Loader2, X } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { HoneypotEvent, WsStatus } from "@/hooks/useHoneypotFeed";
import type { HoneypotFilters } from "@/pages/HoneypotPage";

interface HoneypotFeedProps {
  events: HoneypotEvent[];
  wsStatus: WsStatus;
  filters: HoneypotFilters;
  filtersActive: boolean;
  onFilterChange: <K extends keyof HoneypotFilters>(key: K, value: string) => void;
  onClearFilters: () => void;
}

const threatBadge: Record<string, string> = {
  CRITICAL: "text-rose-400 bg-rose-500/10 border border-rose-500/20",
  HIGH:     "text-orange-400 bg-orange-500/10 border border-orange-500/20",
  MEDIUM:   "text-amber-400 bg-amber-500/10 border border-amber-500/20",
  LOW:      "text-cyan-400 bg-cyan-500/10 border border-cyan-500/20",
};

function formatTs(iso: string): string {
  try {
    const d = new Date(iso);
    return `${d.toTimeString().slice(0, 8)} · ${d.toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;
  } catch {
    return iso;
  }
}

function WsIndicator({ status }: { status: WsStatus }) {
  if (status === "connected") {
    return (
      <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-emerald-400">
        <Wifi className="w-3 h-3" />
        Live
      </span>
    );
  }
  if (status === "connecting") {
    return (
      <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-amber-400">
        <Loader2 className="w-3 h-3 animate-spin" />
        Connecting
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
      <WifiOff className="w-3 h-3" />
      Offline
    </span>
  );
}

const inputCls = "h-8 text-[11px] bg-muted/20 border-border/40 focus:border-primary/40 focus:ring-0 rounded-md placeholder:text-muted-foreground/50";
const selectTriggerCls = "h-8 text-[11px] bg-muted/20 border-border/40 focus:ring-0 rounded-md";

export function HoneypotFeed({
  events, wsStatus, filters, filtersActive, onFilterChange, onClearFilters,
}: HoneypotFeedProps) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="p-5 border-b border-border flex items-center gap-3 flex-wrap">
        <Bug className="w-5 h-5 text-muted-foreground flex-shrink-0" />
        <h2 className="text-lg font-semibold flex-shrink-0">Live Honeypot Feed</h2>
        <div className="ml-auto flex items-center gap-4">
          <WsIndicator status={wsStatus} />
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
            {events.length} captures
          </span>
        </div>
      </div>

      {/* ── Filter bar ────────────────────────────────────────────────────── */}
      <div className="px-5 py-3 border-b border-border/50 bg-muted/5 flex flex-wrap items-center gap-2">
        <Input
          value={filters.ip}
          onChange={(e) => onFilterChange("ip", e.target.value)}
          placeholder="Attacker IP"
          className={cn(inputCls, "w-36")}
        />
        <Input
          value={filters.port}
          onChange={(e) => onFilterChange("port", e.target.value)}
          placeholder="Port"
          className={cn(inputCls, "w-24")}
          type="number"
          min={0}
          max={65535}
        />
        <Select
          value={filters.threat || "all"}
          onValueChange={(v) => onFilterChange("threat", v === "all" ? "" : v)}
        >
          <SelectTrigger className={cn(selectTriggerCls, "w-36")}>
            <SelectValue placeholder="Threat Level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Threats</SelectItem>
            <SelectItem value="CRITICAL">Critical</SelectItem>
            <SelectItem value="HIGH">High</SelectItem>
            <SelectItem value="MEDIUM">Medium</SelectItem>
            <SelectItem value="LOW">Low</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={filters.auth || "all"}
          onValueChange={(v) => onFilterChange("auth", v === "all" ? "" : v)}
        >
          <SelectTrigger className={cn(selectTriggerCls, "w-32")}>
            <SelectValue placeholder="Auth" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Auth</SelectItem>
            <SelectItem value="success">Auth Success</SelectItem>
            <SelectItem value="fail">Auth Fail</SelectItem>
          </SelectContent>
        </Select>
        <Input
          value={filters.command}
          onChange={(e) => onFilterChange("command", e.target.value)}
          placeholder="Command…"
          className={cn(inputCls, "w-40")}
        />
        {filtersActive && (
          <button
            onClick={onClearFilters}
            className="flex items-center gap-1 px-2.5 py-1 h-8 rounded-md bg-muted/40 border border-border/40 text-[10px] font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all ml-auto"
          >
            <X className="w-3 h-3" />
            Clear
          </button>
        )}
      </div>

      {/* ── Table ─────────────────────────────────────────────────────────── */}
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent border-border/50">
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Timestamp</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Attacker IP</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Port</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Threat Level</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Commands</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Auth</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-muted-foreground py-12 text-sm">
                {filtersActive
                  ? "No events match the current filters."
                  : "Listening for honeypot events…"}
              </TableCell>
            </TableRow>
          ) : (
            events.map((ev) => (
              <TableRow
                key={ev.id}
                className={cn(
                  "border-border/30 hover:bg-muted/20 transition-colors",
                  ev.threat_level === "CRITICAL" && "bg-rose-500/5 border-l-2 border-l-rose-500/50"
                )}
              >
                <TableCell className="font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                  {formatTs(ev.timestamp)}
                </TableCell>
                <TableCell className="font-mono text-[12px]">
                  {ev.attacker_ip}
                </TableCell>
                <TableCell className="font-mono text-[12px] text-muted-foreground">
                  {ev.target_port}
                </TableCell>
                <TableCell>
                  {ev.threat_level ? (
                    <span className={cn(
                      "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest",
                      threatBadge[ev.threat_level] ?? "text-muted-foreground bg-muted/20"
                    )}>
                      {ev.threat_level}
                    </span>
                  ) : (
                    <span className="text-muted-foreground text-[11px]">—</span>
                  )}
                </TableCell>
                <TableCell className="text-[11px] text-muted-foreground max-w-[200px] truncate">
                  {ev.commands_executed?.join(", ").slice(0, 40) ?? "—"}
                </TableCell>
                <TableCell className="text-[13px] font-bold">
                  {ev.auth_success
                    ? <span className="text-emerald-500">✓</span>
                    : <span className="text-rose-500">✗</span>}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
