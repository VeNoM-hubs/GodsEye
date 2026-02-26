import { Bell, Search, Globe, Activity, Terminal, Shield } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="h-16 border-b border-border/40 bg-background/50 backdrop-blur-xl sticky top-0 z-50 flex items-center justify-between px-8">
      <div className="flex items-center gap-6 flex-1">
        <div className="relative w-full max-w-sm group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <Input
            placeholder="Search assets, logs, or IPs..."
            className="pl-10 h-9 bg-muted/20 border-border/40 focus:border-primary/40 focus:ring-0 transition-all rounded-md text-sm"
          />
        </div>

        <div className="hidden lg:flex items-center gap-6 text-[11px] font-semibold border-l border-border/40 pl-6 h-6 uppercase tracking-wider text-muted-foreground">
          <div className="flex items-center gap-2">
            <Globe className="w-3.5 h-3.5" />
            <span>Node Clusters: 12</span>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="w-3.5 h-3.5" />
            <span>Risk Score: 24</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 mr-2 bg-muted/30 border border-border/40 rounded px-2.5 py-1">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Connected</span>
        </div>

        <Button variant="ghost" size="icon" className="w-9 h-9 relative hover:bg-muted/40">
          <Bell className="w-4.5 h-4.5 text-muted-foreground" />
          <span className="absolute top-2.5 right-2.5 w-1.5 h-1.5 rounded-full bg-primary" />
        </Button>

        <div className="w-px h-4 bg-border/40 mx-2" />

        <div className="flex items-center gap-3 pl-2 group cursor-pointer">
          <div className="text-right hidden sm:block">
            <p className="text-[13px] font-semibold text-foreground leading-none">Garvit Maheshwari</p>
            <p className="text-[10px] text-muted-foreground mt-1">Systems Admin</p>
          </div>
          <div className="w-8 h-8 rounded-full border border-border/60 bg-muted/40 p-0.5 overflow-hidden ring-offset-background group-hover:border-primary/60 transition-all">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Garvit" alt="Avatar" className="w-full h-full rounded-full" />
          </div>
        </div>
      </div>
    </header>
  );
}
