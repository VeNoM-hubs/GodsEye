import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { ShieldCheck, Info } from "lucide-react";

interface PlaceholderPageProps {
  title: string;
}

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <div className="flex min-h-screen bg-background text-foreground subtle-grid overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />
        <div className="flex-1 p-10 flex flex-col items-center justify-center space-y-10 animate-in fade-in zoom-in duration-500">
          <div className="w-16 h-16 rounded-xl bg-muted/20 border border-border/40 flex items-center justify-center shadow-sm">
            <ShieldCheck className="w-8 h-8 text-primary" />
          </div>
          
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight text-foreground">
              {title} <span className="text-primary/60">—</span> Under Maintenance
            </h1>
            <p className="max-w-md text-muted-foreground text-sm leading-relaxed mx-auto font-medium opacity-80">
              The requested security module is currently in development or undergoing a protocol update.
            </p>
          </div>

          <div className="max-w-md w-full p-6 rounded-lg bg-muted/5 border border-border/40 font-mono text-[11px] space-y-3 opacity-80 shadow-sm backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-3.5 h-3.5 text-primary" />
              <p className="text-primary font-bold uppercase tracking-widest text-[10px]"># Asset Controller Protocol</p>
            </div>
            <p className="text-muted-foreground">Module: {title.toUpperCase()}</p>
            <p className="text-amber-500 font-bold uppercase tracking-[0.15em]">Status: Pending Deployment</p>
            <div className="h-px bg-border/40 my-2" />
            <div className="flex items-center gap-2 text-[10px] text-muted-foreground font-bold tracking-widest uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]" />
              Relay Link Stable: Node_0x221..A1
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
