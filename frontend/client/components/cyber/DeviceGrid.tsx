import { Monitor, Smartphone, Cpu, Router, ShieldCheck, ShieldAlert, ShieldX, MapPin, Activity, Clock } from "lucide-react";
import { Device, AccessLevel } from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface DeviceGridProps {
  devices: Device[];
}

const accessLevelIcons = {
  Admin: ShieldCheck,
  User: ShieldAlert,
  Restricted: ShieldAlert,
  Guest: ShieldX,
};

const accessLevelColors = {
  Admin: "text-emerald-500 bg-emerald-500/5 border-emerald-500/20",
  User: "text-blue-500 bg-blue-500/5 border-blue-500/20",
  Restricted: "text-amber-500 bg-amber-500/5 border-amber-500/20",
  Guest: "text-rose-500 bg-rose-500/5 border-rose-500/20",
};

const deviceIcons = {
  server: Cpu,
  workstation: Monitor,
  mobile: Smartphone,
  iot: Router,
};

export function DeviceGrid({ devices }: DeviceGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {devices.map((device, i) => {
        const DeviceIcon = deviceIcons[device.type];
        const AccessIcon = accessLevelIcons[device.accessLevel];
        
        return (
          <motion.div
            key={device.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className={cn(
              "group relative overflow-hidden rounded-xl border bg-card/40 p-5 transition-all duration-300 hover:bg-card/60 hover:border-border/60 hover:shadow-lg",
              device.status === "online" ? "border-emerald-500/10" : "border-border/50 opacity-60 grayscale-[0.5]"
            )}
          >
            <div className="flex items-start justify-between mb-5">
              <div className={cn(
                "p-2.5 rounded-lg border",
                device.status === "online" ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-500" : "bg-muted/40 border-border/40 text-muted-foreground"
              )}>
                <DeviceIcon className="w-5 h-5" />
              </div>
              <div className="flex flex-col items-end gap-2">
                <div className={cn(
                  "flex items-center gap-1.5 px-2 py-0.5 rounded border text-[9px] font-bold uppercase tracking-wider",
                  accessLevelColors[device.accessLevel]
                )}>
                  <AccessIcon className="w-3 h-3" />
                  {device.accessLevel}
                </div>
                <div className={cn(
                  "w-1.5 h-1.5 rounded-full",
                  device.status === "online" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-muted-foreground/30"
                )} />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors truncate">
                  {device.name}
                </h3>
                <p className="text-[10px] font-mono text-muted-foreground mt-1 opacity-80 uppercase tracking-widest">{device.ip}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 py-3 border-y border-border/20">
                <div className="flex items-center gap-2">
                  <MapPin className="w-3 h-3 text-muted-foreground opacity-60" />
                  <span className="text-[11px] font-medium text-foreground/80 truncate">{device.location.city.split(',')[0]}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-3 h-3 text-muted-foreground opacity-60" />
                  <span className="text-[11px] font-medium text-foreground/80 uppercase">{device.status}</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3 h-3 text-muted-foreground opacity-40" />
                  <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
                    Last Sync: {new Date(device.lastSeen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <button className="text-[10px] font-bold text-primary hover:underline uppercase tracking-widest">Manage</button>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
