import { useEffect, useState } from "react";
import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { StatsGrid } from "@/components/cyber/StatsGrid";
import { LogViewer } from "@/components/cyber/LogViewer";
import { DeviceList } from "@/components/cyber/DeviceList";
import { DeviceMap } from "@/components/cyber/DeviceMap";
import { MOCK_DEVICES, MOCK_LOGS, MOCK_STATS } from "@/lib/mock-data";
import { CyberLog, Device } from "@shared/cyber-api";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

export default function Index() {
  const [logs, setLogs] = useState<CyberLog[]>(MOCK_LOGS);
  const [devices, setDevices] = useState<Device[]>(MOCK_DEVICES);
  const [stats, setStats] = useState(MOCK_STATS);

  // Real-time simulation
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate new log
      const randomDevice = devices[Math.floor(Math.random() * devices.length)];
      const eventTypes = [
        { event: "Login Attempt", severity: "low" as const, details: "Attempt from 192.168.1.50" },
        { event: "Unauthorized Access", severity: "high" as const, details: "Multiple failed attempts on port 22" },
        { event: "Update Completed", severity: "low" as const, details: "System patch 1.2.4 applied" },
        { event: "Network Congestion", severity: "medium" as const, details: "High latency on uplink SYD-02" },
        { event: "Critical Failure", severity: "critical" as const, details: "Storage node beta timeout" },
      ];
      const randomEvent = eventTypes[Math.floor(Math.random() * eventTypes.length)];

      const newLog: CyberLog = {
        id: `log-${Date.now()}`,
        timestamp: new Date().toISOString(),
        deviceId: randomDevice.id,
        deviceName: randomDevice.name,
        ...randomEvent,
      };

      setLogs((prev) => [newLog, ...prev.slice(0, 19)]); // Keep last 20

      // Randomly toggle device status
      if (Math.random() > 0.8) {
        setDevices((prev) =>
          prev.map((d) =>
            d.id === randomDevice.id ? { ...d, status: d.status === "online" ? "offline" : "online" } : d
          )
        );
      }

      // Randomly update stats
      setStats((prev) => ({
        ...prev,
        onlineDevices: devices.filter((d) => d.status === "online").length,
        threatLevel: Math.min(100, Math.max(0, prev.threatLevel + (Math.random() > 0.5 ? 1 : -1))),
      }));
    }, 4000);

    return () => clearInterval(interval);
  }, [devices]);

  return (
    <div className="flex min-h-screen bg-background text-foreground selection:bg-primary/20 font-sans subtle-grid overflow-hidden">
      <Sidebar />

      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-hide">
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
                  Global Fleet Overview & Infrastructure Telemetry
                </p>
              </div>
              <div className="flex items-center gap-4 bg-muted/20 backdrop-blur-md px-5 py-2.5 rounded-lg border border-border/40 shadow-sm transition-all hover:bg-muted/30">
                <div className="flex flex-col text-right">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Active Monitoring</span>
                  <span className="text-xs font-semibold text-foreground flex items-center gap-1.5 mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                    Fleet Healthy
                  </span>
                </div>
                <div className="w-px h-8 bg-border/40 mx-1" />
                <div className="flex flex-col text-right">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Risk Index</span>
                  <span className="text-xs font-semibold text-primary">Status: Nominal</span>
                </div>
              </div>
            </div>
          </motion.div>

          <StatsGrid stats={stats} />

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 h-fit lg:h-[600px] pb-12">
            <div className="xl:col-span-2 h-full flex flex-col gap-8">
              <div className="flex-1 min-h-[400px]">
                <DeviceMap devices={devices} />
              </div>
              <div className="h-fit">
                <DeviceList devices={devices} />
              </div>
            </div>
            <div className="h-full min-h-[500px] xl:min-h-0 flex flex-col">
              <LogViewer logs={logs} />
            </div>
          </div>
        </div>

        {/* System Uplink Badge */}
        <div className="absolute bottom-6 right-8 pointer-events-none z-50">
          <div className="flex items-center gap-3 bg-card/60 backdrop-blur-md px-4 py-1.5 rounded-full border border-border/40 shadow-sm">
             <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
             <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Gateway Connected: Cluster-West-02</span>
          </div>
        </div>
      </main>
    </div>
  );
}
