import { useMemo } from "react";
import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { SecurityWidgets } from "@/components/cyber/SecurityWidgets";
import { LogViewer } from "@/components/cyber/LogViewer";
import { CliTerminal } from "@/components/cyber/CliTerminal";
import { OverviewTrendsChart } from "@/components/cyber/OverviewTrendsChart";
import { ConnectionBadge } from "@/components/cyber/ConnectionBadge";
import { useGodsEyeLive } from "@/hooks/useGodsEyeLive";
import { motion } from "framer-motion";
import type { GodsEyeEvent, DashboardStats } from "@shared/cyber-api";
import type { WireEvent, WireDashboardStats } from "@shared/godseye-api-types";

function adaptEvents(wireEvents: WireEvent[]): GodsEyeEvent[] {
  return wireEvents.map((e) => ({
    source: e.source,
    event: {
      event_id: e.event_id,
      event_type: e.event_type as any,
      timestamp: e.event_time,
      // Fill required fields with sensible defaults based on event_type
      ...(e.event_type === "access" ? {
        device_id: e.resource_id ?? "unknown",
        location: e.resource_id ?? "unknown",
        access_method: "rfid" as const,
        status: (e.severity === "HIGH" ? "anomaly" : e.severity === "MEDIUM" ? "denied" : "success") as any,
        user_id: e.user_id ?? undefined,
      } : e.event_type === "honeypot" ? {
        honeypot_id: e.resource_id ?? "honeypot-1",
        honeypot_type: "ssh",
        source_ip: e.user_id ?? "0.0.0.0",
        interaction_type: "connection" as const,
        threat_level: e.severity,
      } : e.event_type === "network" ? {
        network_event_type: "suspicious_connection" as const,
        source_ip: e.user_id ?? "0.0.0.0",
        destination_ip: e.resource_id ?? "0.0.0.0",
        protocol: "TCP",
        anomaly_score: e.severity === "HIGH" ? 0.9 : e.severity === "MEDIUM" ? 0.6 : 0.3,
        description: e.description,
      } : e.event_type === "endpoint" ? {
        hostname: e.resource_id ?? "unknown",
        endpoint_id: e.resource_id ?? "ep-1",
        operating_system: "Linux",
        endpoint_event_type: "process_creation" as const,
        severity: (e.severity as any) || "LOW",
        description: e.description,
      } : {
        decoy_type: "teapot",
        decoy_id: e.resource_id ?? "teapot-1",
        threat_level: e.severity,
        description: e.description ?? "Teapot triggered",
      }),
    } as any,
  }));
}

function adaptStats(wireStats: WireDashboardStats): DashboardStats {
  const mitre_distribution = Object.entries(wireStats.mitre_breakdown ?? {}).map(
    ([technique_id, count]) => ({ technique_id, technique_name: technique_id, count: count as number })
  );
  return {
    active_threats: wireStats.active_threats,
    access_violations: wireStats.total_violations,
    events_per_minute: wireStats.events_per_minute,
    top_flagged_users: [],
    mitre_distribution,
    targeted_resources: [],
  };
}

export default function Index() {
  const { events: wireEvents, stats: wireStats, ready, error, lastUpdated } = useGodsEyeLive();

  const events = useMemo(() => adaptEvents(wireEvents), [wireEvents]);
  const stats = useMemo(() => wireStats ? adaptStats(wireStats) : null, [wireStats]);

  const activeUsers = useMemo(() => {
    const cutoff = Date.now() - 10 * 60 * 1000;
    const unique = new Set<string>();
    for (const ev of wireEvents) {
      if (!ev.user_id) continue;
      const ts = ev.event_time ? new Date(ev.event_time).getTime() : 0;
      if (ts && ts < cutoff) continue;
      unique.add(ev.user_id);
    }
    return unique.size;
  }, [wireEvents]);

  return (
    <div className="flex min-h-screen bg-background text-foreground selection:bg-primary/20 font-sans subtle-grid overflow-hidden">
      <Sidebar />

      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-hide">
          {error && (
            <div className="bg-red-900/80 border-l-4 border-red-600 p-3 mb-4 rounded">
              <p className="text-red-100 text-sm">
                ⚠️ GodsEye API unreachable — showing last known data. {error}
              </p>
            </div>
          )}

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div className="flex items-center justify-between mb-2">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-3">
                  <span className="w-1 h-6 bg-primary rounded-full" />
                  Security Operations Center
                </h2>
                <p className="text-muted-foreground text-[11px] font-medium mt-1 uppercase tracking-widest opacity-80">
                  GodsEye — Unified Physical &amp; Digital Security Monitoring
                </p>
              </div>
              <div className="flex items-center gap-4 bg-muted/20 backdrop-blur-md px-5 py-2.5 rounded-lg border border-border/40 shadow-sm transition-all hover:bg-muted/30">
                <div className="flex flex-col text-right">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Active Monitoring</span>
                  <span className="text-xs font-semibold text-foreground flex items-center gap-1.5 mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                    System Nominal
                  </span>
                </div>
                <div className="w-px h-8 bg-border/40 mx-1" />
                <div className="flex flex-col text-right">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Threats</span>
                  <span className="text-xs font-semibold text-rose-400">{stats?.active_threats ?? 0} Active</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* ── Security Widgets ── */}
          {stats && <SecurityWidgets stats={stats} />}

          {/* ── Operational Trends ── */}
          <OverviewTrendsChart
            eventsPerMinute={wireStats?.events_per_minute ?? 0}
            activeUsers={activeUsers}
            accessViolations={wireStats?.total_violations ?? 0}
            updatedAt={lastUpdated}
          />

          {/* ── CLI Terminal + Structured Logs ── */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 h-fit lg:h-[640px] pb-12">
            <div className="xl:col-span-2 h-full min-h-[560px] flex flex-col">
              <LogViewer events={events} />
            </div>
            <div className="h-full min-h-[360px] xl:min-h-0 flex flex-col">
              <CliTerminal events={events} />
            </div>
          </div>
        </div>

        <ConnectionBadge status={ready && !error ? "connected" : "disconnected"} />
      </main>
    </div>
  );
}
