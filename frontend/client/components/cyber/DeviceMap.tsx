import { Globe, MapPin, Activity, ShieldAlert, Wifi, Server, Smartphone, Monitor } from "lucide-react";
import { Device } from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface DeviceMapProps {
  devices: Device[];
}

export function DeviceMap({ devices }: DeviceMapProps) {
  return (
    <div className="rounded-xl border border-border/40 bg-card/40 backdrop-blur-md overflow-hidden shadow-sm relative h-full flex flex-col min-h-[400px]">
      <div className="p-4 border-b border-border/40 flex items-center justify-between bg-muted/5 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-500/10">
            <Globe className="w-4 h-4 text-blue-500" />
          </div>
          <h3 className="font-bold text-[11px] tracking-[0.2em] uppercase text-muted-foreground">Geographic Distribution</h3>
        </div>
        <div className="flex items-center gap-2">
          <div className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground bg-muted/20 px-2 py-1 rounded">Real-time Telemetry</div>
        </div>
      </div>

      <div className="flex-1 relative bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=2072')] bg-cover bg-center grayscale opacity-[0.03] subtle-grid" />

      <div className="absolute inset-0 p-8 flex flex-col justify-center pointer-events-none">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-10">
          {devices.map((device, i) => (
            <motion.div
              key={device.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className={cn(
                "pointer-events-auto flex flex-col gap-2 p-2.5 rounded-lg border bg-background/90 backdrop-blur-sm shadow-sm hover:border-primary/40 transition-all duration-300 relative group cursor-pointer",
                device.status === "online" ? "border-emerald-500/20" : "border-border/50 opacity-40 grayscale"
              )}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2.5">
                  <div className={cn("p-1.5 rounded bg-muted/40", device.status === "online" ? "text-emerald-500" : "text-muted-foreground")}>
                    {device.type === "server" && <Server className="w-3 h-3" />}
                    {device.type === "mobile" && <Smartphone className="w-3 h-3" />}
                    {device.type === "workstation" && <Monitor className="w-3 h-3" />}
                    {device.type === "iot" && <Wifi className="w-3 h-3" />}
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-foreground">{device.name.split("-")[0]}</span>
                    <span className="text-[8px] font-mono text-muted-foreground mt-0.5">{device.ip}</span>
                  </div>
                </div>
                <div className={cn("w-1.5 h-1.5 rounded-full", device.status === "online" ? "bg-emerald-500" : "bg-muted-foreground/30")} />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-muted/5 backdrop-blur-md border-t border-border/40 z-10">
        <div className="flex items-center justify-between text-[9px] font-mono text-muted-foreground">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 uppercase font-bold tracking-widest">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Active: {devices.filter(d => d.status === "online").length}
            </span>
            <span className="flex items-center gap-1.5 uppercase font-bold tracking-widest">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> Issues: 3
            </span>
          </div>
          <span className="text-muted-foreground uppercase tracking-widest opacity-60">Fleet Tracking System v4.2</span>
        </div>
      </div>
    </div>
  );
}
