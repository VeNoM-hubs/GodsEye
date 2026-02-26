import { Terminal, ShieldAlert, Info, AlertTriangle, Radio, Skull } from "lucide-react";
import type { GodsEyeEvent, AlertSeverity } from "@shared/cyber-api";
import { getEventUser, getEventResource, getEventSeverity, getEventDescription } from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { motion, AnimatePresence } from "framer-motion";

interface LogViewerProps {
  events: GodsEyeEvent[];
}

const severityMeta: Record<AlertSeverity, { color: string; Icon: React.ElementType }> = {
  INFO: { color: "text-sky-400 bg-sky-400/10 border-sky-400/20", Icon: Info },
  LOW: { color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20", Icon: Info },
  MEDIUM: { color: "text-amber-400 bg-amber-400/10 border-amber-400/20", Icon: Radio },
  HIGH: { color: "text-orange-500 bg-orange-500/10 border-orange-500/20", Icon: AlertTriangle },
  CRITICAL: { color: "text-rose-500 bg-rose-500/10 border-rose-500/20", Icon: Skull },
};

const sourceLabel: Record<string, { label: string; color: string }> = {
  physical: { label: "PHY", color: "text-cyan-400 bg-cyan-400/10 border-cyan-400/20" },
  digital: { label: "DIG", color: "text-violet-400 bg-violet-400/10 border-violet-400/20" },
};

export function LogViewer({ events }: LogViewerProps) {
  return (
    <div className="flex flex-col h-full rounded-2xl border border-border/50 bg-card/30 backdrop-blur-md overflow-hidden relative shadow-2xl">
      <div className="scanline opacity-5" />
      <div className="p-4 border-b border-border/50 flex items-center justify-between bg-muted/20 backdrop-blur-sm z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Terminal className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-lg tracking-tight">System Events Stream</h3>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Live — {events.length} events
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {["All", "Critical", "Physical"].map((filter) => (
            <button
              key={filter}
              className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded bg-muted/30 border border-border/50 hover:bg-muted/50 transition-colors"
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      <ScrollArea className="flex-1 p-4 h-[400px]">
        <div className="space-y-3">
          <AnimatePresence initial={false}>
            {events.map((ge) => {
              const e = ge.event;
              const severity = getEventSeverity(e);
              const { color, Icon } = severityMeta[severity] ?? severityMeta.INFO;
              const src = sourceLabel[ge.source] ?? sourceLabel.digital;
              return (
                <motion.div
                  key={e.event_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="group flex flex-col gap-2 p-3 rounded-xl border border-transparent hover:border-border/30 hover:bg-muted/5 transition-all duration-300 relative overflow-hidden"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={cn("p-1.5 rounded-lg border", color)}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={cn("text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase", src.color)}>
                          {src.label}
                        </span>
                        <span className="text-xs font-mono text-muted-foreground">
                          [{new Date(e.timestamp).toLocaleTimeString()}]
                        </span>
                        <span className="text-xs font-bold text-foreground">
                          {getEventUser(e)}
                        </span>
                      </div>
                    </div>
                    <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded uppercase", color)}>
                      {severity}
                    </span>
                  </div>
                  <div className="pl-11">
                    <p className="text-sm font-semibold text-foreground leading-tight">
                      {e.event_type.toUpperCase()}: {getEventDescription(e)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1 font-mono">
                      Resource: {getEventResource(e)}
                    </p>
                  </div>
                  <div className="absolute right-2 bottom-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="text-[10px] font-bold text-primary underline">INSPECT</button>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </ScrollArea>

      <div className="p-3 border-t border-border/50 bg-muted/10 text-[10px] font-mono text-muted-foreground flex justify-between uppercase">
        <span>RELAY NODE: SYD-02</span>
        <span>ENCRYPTION: AES-256-GCM</span>
      </div>
    </div>
  );
}
