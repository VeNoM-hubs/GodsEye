import { cn } from "@/lib/utils";
import type { ConnectionStatus } from "@shared/cyber-api";

interface ConnectionBadgeProps {
  status: ConnectionStatus;
}

export function ConnectionBadge({ status }: ConnectionBadgeProps) {
  const label = {
    connecting:    "Connecting...",
    connected:     "Gateway Connected: Cluster-West-02",
    disconnected:  "Backend Disconnected — Retrying",
  }[status];

  const dotClass = {
    connecting:   "bg-amber-400 animate-pulse",
    connected:    "bg-emerald-500 animate-pulse",
    disconnected: "bg-rose-500",
  }[status];

  return (
    <div className="absolute bottom-6 right-8 pointer-events-none z-50">
      <div className={cn(
        "flex items-center gap-3 bg-card/60 backdrop-blur-md px-4 py-1.5 rounded-full border border-border/40 shadow-sm",
        status === "disconnected" && "border-rose-500/30"
      )}>
        <div className={cn("w-1.5 h-1.5 rounded-full", dotClass)} />
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
          {label}
        </span>
      </div>
    </div>
  );
}
