import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Activity, Users, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface TrendPoint {
  ts: number;
  time: string;
  events_per_minute: number;
  active_users: number;
  access_violations: number;
}

interface OverviewTrendsChartProps {
  eventsPerMinute: number;
  activeUsers: number;
  accessViolations: number;
  updatedAt: number;
}

function formatTime(ts: number): string {
  try {
    return new Date(ts).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card/95 backdrop-blur-xl border border-border/60 rounded-xl px-4 py-3 shadow-2xl text-xs font-mono min-w-[200px]">
      <p className="text-muted-foreground mb-2 font-bold uppercase tracking-widest">{label}</p>
      {payload.map((item: any) => (
        <div key={item.dataKey} className="flex items-center justify-between text-[11px]">
          <span className="text-muted-foreground">{item.name}</span>
          <span className="font-bold" style={{ color: item.color }}>{item.value}</span>
        </div>
      ))}
    </div>
  );
};

export function OverviewTrendsChart({
  eventsPerMinute,
  activeUsers,
  accessViolations,
  updatedAt,
}: OverviewTrendsChartProps) {
  const [series, setSeries] = useState<TrendPoint[]>([]);

  useEffect(() => {
    if (!updatedAt) return;

    setSeries((prev) => {
      const last = prev[prev.length - 1];
      if (last?.ts === updatedAt) return prev;
      const next: TrendPoint = {
        ts: updatedAt,
        time: formatTime(updatedAt),
        events_per_minute: eventsPerMinute,
        active_users: activeUsers,
        access_violations: accessViolations,
      };
      return [...prev, next].slice(-30);
    });
  }, [updatedAt, eventsPerMinute, activeUsers, accessViolations]);

  const latest = series[series.length - 1];
  const hasData = series.length > 0;

  const pills = useMemo(() => ([
    {
      label: "Events / Min",
      value: latest?.events_per_minute ?? 0,
      icon: <Activity className="w-3 h-3" />,
      color: "text-violet-400",
      bg: "bg-violet-400/10",
      border: "border-violet-400/20",
    },
    {
      label: "Active Users",
      value: latest?.active_users ?? 0,
      icon: <Users className="w-3 h-3" />,
      color: "text-emerald-400",
      bg: "bg-emerald-400/10",
      border: "border-emerald-400/20",
    },
    {
      label: "Access Violations",
      value: latest?.access_violations ?? 0,
      icon: <ShieldAlert className="w-3 h-3" />,
      color: "text-rose-400",
      bg: "bg-rose-400/10",
      border: "border-rose-400/20",
    },
  ]), [latest]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="rounded-2xl border border-border/50 bg-card/30 backdrop-blur-md overflow-hidden shadow-2xl relative"
    >
      <div className="scanline opacity-5 absolute inset-0 pointer-events-none z-0" />

      <div className="p-5 border-b border-border/50 flex items-center justify-between bg-muted/20 backdrop-blur-sm z-10 relative">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-violet-500/10 border border-violet-500/20">
            <Activity className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h3 className="font-bold text-lg tracking-tight">Operational Trends</h3>
            <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
              Live · security telemetry
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {pills.map((pill) => (
            <div key={pill.label} className={cn("flex flex-col items-end px-3 py-1.5 rounded-lg border", pill.bg, pill.border)}>
              <span className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground">{pill.label}</span>
              <span className={cn("text-sm font-bold flex items-center gap-1", pill.color)}>
                {pill.icon}
                {pill.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-5 z-10 relative">
        {hasData ? (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={series} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis
                dataKey="time"
                tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 10, fontFamily: "monospace" }}
                axisLine={{ stroke: "rgba(255,255,255,0.08)" }}
                tickLine={false}
                interval="preserveStartEnd"
                label={{ value: "Time", position: "insideBottomRight", offset: -4, fill: "rgba(255,255,255,0.25)", fontSize: 9, fontFamily: "monospace" }}
              />
              <YAxis
                tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 10, fontFamily: "monospace" }}
                axisLine={false}
                tickLine={false}
                width={40}
                allowDecimals={false}
                label={{ value: "Count", angle: -90, position: "insideLeft", offset: 12, fill: "rgba(255,255,255,0.25)", fontSize: 9, fontFamily: "monospace" }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="top"
                height={30}
                wrapperStyle={{ color: "rgba(255,255,255,0.45)", fontSize: 10, fontFamily: "monospace" }}
              />

              <Line
                type="monotone"
                dataKey="events_per_minute"
                name="Events / Min"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="active_users"
                name="Active Users"
                stroke="#34d399"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="access_violations"
                name="Access Violations"
                stroke="#f43f5e"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="px-4 py-12 text-center text-[11px] text-muted-foreground">
            Waiting for live telemetry…
          </div>
        )}
      </div>

      <div className="px-5 pb-4 border-t border-border/30 pt-3 bg-muted/10 text-[10px] font-mono text-muted-foreground flex justify-between uppercase z-10 relative">
        <span>events/min · active users · access violations</span>
        <span>source: gods-eye / dashboard stats</span>
      </div>
    </motion.div>
  );
}
