/**
 * @deprecated — Replaced by SecurityWidgets.tsx for the GodsEye dashboard.
 * Kept for backward compatibility; not rendered on any active page.
 */
import { Monitor, ShieldCheck, Activity, Cpu } from "lucide-react";
import { DashboardStats } from "@shared/cyber-api";
import { cn } from "@/lib/utils";

interface StatsGridProps {
  stats: DashboardStats;
}

export function StatsGrid({ stats }: StatsGridProps) {
  const cards = [
    {
      label: "Active Threats",
      value: stats.active_threats,
      icon: ShieldCheck,
      trend: `${stats.access_violations} access violations`,
      color: "text-rose-400",
      bg: "bg-rose-400/5",
      border: "border-rose-400/20",
    },
    {
      label: "Events Per Minute",
      value: stats.events_per_minute,
      icon: Activity,
      trend: "last 60s",
      color: "text-emerald-400",
      bg: "bg-emerald-400/5",
      border: "border-emerald-400/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {cards.map((card, i) => (
        <div
          key={i}
          className={cn(
            "p-5 rounded-xl border bg-card/40 backdrop-blur-sm relative overflow-hidden transition-all duration-300 hover:bg-card/60 hover:border-border/60 shadow-sm",
            card.border
          )}
        >
          <div className="flex items-center gap-4">
            <div className={cn("p-2 rounded-lg border", card.bg, card.border)}>
              <card.icon className={cn("w-4.5 h-4.5", card.color)} />
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-muted-foreground">{card.label}</p>
              <h3 className="text-2xl font-bold tracking-tight text-foreground mt-1">{card.value}</h3>
            </div>
          </div>
          <div className="mt-4">
            <span className={cn("text-[9px] font-bold px-2 py-0.5 rounded tracking-wider uppercase", card.bg, card.color)}>
              {card.trend}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
