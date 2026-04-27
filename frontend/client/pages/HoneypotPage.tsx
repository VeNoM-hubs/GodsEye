import { useMemo, useState } from "react";
import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { HoneypotFeed } from "@/components/cyber/HoneypotFeed";
import { useHoneypotFeed } from "@/hooks/useHoneypotFeed";
import { motion } from "framer-motion";

export interface HoneypotFilters {
  ip: string;
  port: string;
  threat: string;   // "" | "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
  auth: string;     // "" | "success" | "fail"
  command: string;
}

const EMPTY_FILTERS: HoneypotFilters = { ip: "", port: "", threat: "", auth: "", command: "" };

function isActive(f: HoneypotFilters): boolean {
  return Object.values(f).some((v) => v !== "");
}

export default function HoneypotPage() {
  const { events, wsStatus } = useHoneypotFeed();
  const [filters, setFilters] = useState<HoneypotFilters>(EMPTY_FILTERS);

  const filtered = useMemo(() => {
    if (!isActive(filters)) return events;
    return events.filter((ev) => {
      if (filters.ip      && !ev.attacker_ip.includes(filters.ip)) return false;
      if (filters.port    && String(ev.target_port) !== filters.port.trim()) return false;
      if (filters.threat  && (ev.threat_level ?? "").toUpperCase() !== filters.threat) return false;
      if (filters.auth === "success" && !ev.auth_success)  return false;
      if (filters.auth === "fail"    &&  ev.auth_success)  return false;
      if (filters.command) {
        const cmds = ev.commands_executed?.join(" ") ?? "";
        if (!cmds.toLowerCase().includes(filters.command.toLowerCase())) return false;
      }
      return true;
    });
  }, [events, filters]);

  function setFilter<K extends keyof HoneypotFilters>(key: K, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div className="flex min-h-screen bg-background text-foreground subtle-grid overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto p-10 space-y-8 scrollbar-hide">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
              <span className="w-1 h-8 bg-primary rounded-full" />
              Threat Intelligence
            </h1>
            <p className="text-muted-foreground text-[11px] font-medium mt-1 uppercase tracking-widest opacity-80">
              Live Honeypot Ingestion —{" "}
              {isActive(filters)
                ? `${filtered.length} of ${events.length} Events`
                : `${events.length} Events Captured`}
            </p>
          </motion.div>

          <HoneypotFeed
            events={filtered}
            wsStatus={wsStatus}
            filters={filters}
            filtersActive={isActive(filters)}
            onFilterChange={setFilter}
            onClearFilters={() => setFilters(EMPTY_FILTERS)}
          />
        </div>
      </main>
    </div>
  );
}
