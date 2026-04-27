import { Bug } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import type { HoneypotEvent } from "@/hooks/useHoneypotFeed";

interface HoneypotFeedProps {
  events: HoneypotEvent[];
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
    const time = d.toTimeString().slice(0, 8);
    const date = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    return `${time} · ${date}`;
  } catch {
    return iso;
  }
}

export function HoneypotFeed({ events }: HoneypotFeedProps) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="p-5 border-b border-border flex items-center gap-2">
        <Bug className="w-5 h-5 text-muted-foreground" />
        <h2 className="text-lg font-semibold">Live Honeypot Feed</h2>
        <span className="ml-auto text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
          {events.length} captures
        </span>
      </div>

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
                Listening for honeypot events...
              </TableCell>
            </TableRow>
          ) : (
            events.map((ev) => (
              <TableRow
                key={ev.id}
                className={cn(
                  "border-border/30 hover:bg-muted/20 transition-colors",
                  ev.threat_level === "CRITICAL" &&
                    "bg-rose-500/5 border-l-2 border-l-rose-500/50"
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
                    <span
                      className={cn(
                        "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest",
                        threatBadge[ev.threat_level] ?? "text-muted-foreground bg-muted/20"
                      )}
                    >
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
                  {ev.auth_success ? (
                    <span className="text-emerald-500">✓</span>
                  ) : (
                    <span className="text-rose-500">✗</span>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
