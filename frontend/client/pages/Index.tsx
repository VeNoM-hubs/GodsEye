import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { SecurityWidgets } from "@/components/cyber/SecurityWidgets";
import { LogViewer } from "@/components/cyber/LogViewer";
import { DeviceList } from "@/components/cyber/DeviceList";
import { CliTerminal } from "@/components/cyber/CliTerminal";
import { AttackGraph } from "@/components/cyber/OrgEventsChart";
import { ConnectionBadge } from "@/components/cyber/ConnectionBadge";
import { useGodsEyeLive } from "@/hooks/useGodsEyeLive";
import { motion } from "framer-motion";

export default function Index() {
  const { events, alerts, stats, ready, error, lastUpdated, setPaused, paused } = useGodsEyeLive();

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

          {/* ── Attack Graph ── */}
          <AttackGraph alerts={alerts} />

          {/* ── CLI Terminal + Structured Logs ── */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 h-fit lg:h-[600px] pb-12">
            <div className="xl:col-span-2 h-full flex flex-col gap-8">
              <div className="flex-1 min-h-[420px]">
                <CliTerminal events={events} />
              </div>
            </div>
            <div className="h-full min-h-[500px] xl:min-h-0 flex flex-col">
              <LogViewer events={events} />
            </div>
          </div>
        </div>

        <ConnectionBadge status={ready && !error ? "connected" : "disconnected"} />
      </main>
    </div>
  );
}
