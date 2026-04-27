import { useEffect, useMemo, useState } from "react";
import { Bell, Loader2, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { AlertSeverity } from "@shared/cyber-api";
import { useAlertNotifications, type AlertNotificationItem, type WsStatus } from "@/hooks/useAlertNotifications";

const SEV_STYLES: Record<AlertSeverity, string> = {
  CRITICAL: "text-rose-400 bg-rose-900/30 border-rose-700/50",
  HIGH: "text-orange-400 bg-orange-900/30 border-orange-700/50",
  MEDIUM: "text-amber-400 bg-amber-900/30 border-amber-700/50",
  LOW: "text-cyan-400 bg-cyan-900/30 border-cyan-700/50",
  INFO: "text-muted-foreground bg-muted/30 border-border/40",
};

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

function WsBadge({ status }: { status: WsStatus }) {
  if (status === "connected") {
    return (
      <span className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-widest text-emerald-400">
        <Wifi className="w-3 h-3" />
        Live
      </span>
    );
  }
  if (status === "connecting") {
    return (
      <span className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-widest text-amber-400">
        <Loader2 className="w-3 h-3 animate-spin" />
        Connecting
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-widest text-muted-foreground">
      <WifiOff className="w-3 h-3" />
      Offline
    </span>
  );
}

function NotificationRow({ item }: { item: AlertNotificationItem }) {
  return (
    <div
      className={cn(
        "px-4 py-3 border-b border-border/30",
        item.unread && "bg-muted/20"
      )}
    >
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border",
            SEV_STYLES[item.severity]
          )}
        >
          {item.severity}
        </span>
        <span className="text-[10px] text-muted-foreground">Risk {item.risk_score}</span>
        <span className="ml-auto text-[10px] text-muted-foreground">{formatTime(item.last_seen)}</span>
      </div>
      <p className="text-[12px] font-semibold text-foreground mt-1 truncate">
        {item.threat_pattern}
      </p>
      <p className="text-[10px] text-muted-foreground mt-0.5">
        User: {item.user_id || "unknown"}  ·  Events: {item.event_count}
      </p>
    </div>
  );
}

export function NotificationBell() {
  const { notifications, unreadCount, wsStatus, markAllRead, clearAll } = useAlertNotifications();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (open) markAllRead();
  }, [open, markAllRead]);

  const badgeText = useMemo(() => (unreadCount > 9 ? "9+" : String(unreadCount)), [unreadCount]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="w-9 h-9 relative hover:bg-muted/40">
          <Bell className="w-4.5 h-4.5 text-muted-foreground" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-primary text-[9px] font-bold text-primary-foreground flex items-center justify-center">
              {badgeText}
            </span>
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent align="end" className="w-96 p-0">
        <div className="flex items-center justify-between px-4 py-3 border-b border-border/40">
          <div className="flex items-center gap-2">
            <span className="text-[12px] font-bold text-foreground">Notifications</span>
            <WsBadge status={wsStatus} />
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={markAllRead}
              className="text-[9px] uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors"
            >
              Mark read
            </button>
            <button
              onClick={clearAll}
              className="text-[9px] uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="max-h-80 overflow-y-auto scrollbar-hide">
          {notifications.length === 0 ? (
            <div className="px-4 py-8 text-center text-[11px] text-muted-foreground">
              No high-risk alerts yet.
            </div>
          ) : (
            notifications.slice(0, 8).map((item) => (
              <NotificationRow key={item.threat_id} item={item} />
            ))
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
