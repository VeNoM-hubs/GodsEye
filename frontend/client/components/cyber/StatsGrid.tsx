import { Monitor, ShieldCheck, Activity, Cpu, Globe } from "lucide-react";
import { DashboardStats } from "@shared/cyber-api";
import { cn } from "@/lib/utils";

interface StatsGridProps {
  stats: DashboardStats;
}

export function StatsGrid({ stats }: StatsGridProps) {
  const cards = [
    {
      label: "Active Managed Nodes",
      value: stats.totalDevices,
      icon: Monitor,
      trend: "+2 this week",
      color: "text-blue-400",
      bg: "bg-blue-400/5",
      border: "border-blue-400/20",
    },
    {
      label: "Node Uptime Status",
      value: `${stats.onlineDevices}/${stats.totalDevices}`,
      icon: Cpu,
      trend: "94.2% Uptime",
      color: "text-emerald-400",
      bg: "bg-emerald-400/5",
      border: "border-emerald-400/20",
    },
    {
      label: "Total Incidents",
      value: stats.criticalAlerts,
      icon: ShieldCheck,
      trend: "No Critical Issues",
      color: "text-rose-400",
      bg: "bg-rose-400/5",
      border: "border-rose-400/20",
    },
    {
      label: "Network Health Score",
      value: `${100 - stats.threatLevel}%`,
      icon: Activity,
      trend: "Low Risk Profile",
      color: "text-amber-400",
      bg: "bg-amber-400/5",
      border: "border-amber-400/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
              <div className="flex items-baseline gap-2 mt-1">
                <h3 className="text-2xl font-bold tracking-tight text-foreground">{card.value}</h3>
              </div>
            </div>
          </div>
          
          <div className="mt-4 flex items-center justify-between">
            <span className={cn("text-[9px] font-bold px-2 py-0.5 rounded tracking-wider uppercase", card.bg, card.color)}>
              {card.trend}
            </span>
            <div className={cn("w-1.5 h-1.5 rounded-full", card.color.replace('text', 'bg'))} />
          </div>
        </div>
      ))}
    </div>
  );
}
