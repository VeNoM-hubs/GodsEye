import { LayoutDashboard, ShieldCheck, Monitor, Settings, Activity, Lock, Bell } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "Overview", path: "/" },
  { icon: Monitor, label: "Assets", path: "/devices" },
  { icon: ShieldCheck, label: "Threat Intel", path: "/threats" },
  { icon: Activity, label: "Activity Logs", path: "/logs" },
  { icon: Lock, label: "Identity & Access", path: "/access" },
  { icon: Settings, label: "System Config", path: "/settings" },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r border-border/60 bg-sidebar-background flex flex-col h-screen sticky top-0 shrink-0">
      <div className="p-8 pb-10 flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
          <ShieldCheck className="w-5 h-5 text-primary-foreground" />
        </div>
        <div className="flex flex-row items-baseline gap-1.5">
          <h1 className="font-bold text-lg tracking-tight text-foreground whitespace-nowrap">
            God'sEye <span className="text-primary/90 font-medium">Dashboard</span>
          </h1>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        <p className="px-4 mb-4 text-[10px] font-semibold text-muted-foreground uppercase tracking-[0.15em]">Security Operations</p>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-4 py-2.5 rounded-md transition-all duration-200 group",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
              )}
            >
              <item.icon className={cn("w-4.5 h-4.5", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground/80")} />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-border/40">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/20 border border-border/40">
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
              <Activity className="w-4 h-4 text-primary" />
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-sidebar-background" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-foreground leading-none">Cloud Sentinel</p>
            <p className="text-[9px] text-muted-foreground mt-1">Status: Operational</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
