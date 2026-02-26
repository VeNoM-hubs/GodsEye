import { Monitor, Smartphone, Cpu, Router, ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";
import { Device } from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Link } from "react-router-dom";

interface DeviceListProps {
  devices: Device[];
}

const accessLevelIcons = {
  Admin: ShieldCheck,
  User: ShieldAlert,
  Restricted: ShieldAlert,
  Guest: ShieldX,
};

const accessLevelColors = {
  Admin: "text-emerald-500 bg-emerald-500/5",
  User: "text-blue-500 bg-blue-500/5",
  Restricted: "text-amber-500 bg-amber-500/5",
  Guest: "text-rose-500 bg-rose-500/5",
};

const deviceIcons = {
  server: Cpu,
  workstation: Monitor,
  mobile: Smartphone,
  iot: Router,
};

export function DeviceList({ devices }: DeviceListProps) {
  return (
    <div className="rounded-xl border border-border/40 bg-card/40 backdrop-blur-md overflow-hidden shadow-sm relative transition-all duration-300 hover:border-border/60">
      <div className="p-5 border-b border-border/40 bg-muted/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-muted/20 border border-border/40 text-muted-foreground">
              <Monitor className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-[11px] tracking-[0.2em] uppercase text-muted-foreground">Network Infrastructure</h3>
          </div>
          <Link to="/devices" className="text-[10px] font-bold text-primary hover:underline uppercase tracking-widest transition-all">
            Manage Assets
          </Link>
        </div>
      </div>

      <Table>
        <TableHeader className="bg-muted/5">
          <TableRow className="border-border/20 hover:bg-transparent">
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground px-6 py-4">Node Identity</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground text-center">Status</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Permission Profile</TableHead>
            <TableHead className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground text-right px-6">Operational Control</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {devices.map((device) => {
            const DeviceIcon = deviceIcons[device.type];
            const AccessIcon = accessLevelIcons[device.accessLevel];
            return (
              <TableRow key={device.id} className="border-border/10 hover:bg-muted/10 transition-all group cursor-pointer">
                <TableCell className="px-6 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded bg-muted/40 group-hover:text-primary transition-colors">
                      <DeviceIcon className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">{device.name}</p>
                      <p className="text-[9px] font-mono text-muted-foreground mt-0.5">{device.ip}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex items-center justify-center">
                    <div className={cn("w-1.5 h-1.5 rounded-full", device.status === "online" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]" : "bg-muted-foreground/20")} />
                  </div>
                </TableCell>
                <TableCell>
                  <div className={cn("inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider", accessLevelColors[device.accessLevel])}>
                    <AccessIcon className="w-2.5 h-2.5" />
                    {device.accessLevel}
                  </div>
                </TableCell>
                <TableCell className="text-right px-6">
                  <button className="text-[9px] font-bold text-primary opacity-0 group-hover:opacity-100 transition-all hover:underline uppercase tracking-widest">
                    Details
                  </button>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
