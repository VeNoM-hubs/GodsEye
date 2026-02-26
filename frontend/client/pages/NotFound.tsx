import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { ShieldAlert, Terminal, ArrowLeft, Lock } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: Resource not found:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground subtle-grid relative overflow-hidden">
      <div className="relative z-10 text-center space-y-10 p-16 rounded-2xl border border-border/40 bg-card/40 backdrop-blur-2xl shadow-sm max-w-2xl w-full">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20 shadow-sm">
            <Lock className="w-8 h-8 text-primary" />
          </div>
        </div>
        
        <div className="space-y-4">
          <h1 className="text-6xl font-bold tracking-tight text-foreground">
            404
          </h1>
          <h2 className="text-xl font-semibold uppercase tracking-[0.2em] text-muted-foreground opacity-80">
            Resource Not Found
          </h2>
          <p className="text-muted-foreground max-w-sm mx-auto text-sm leading-relaxed">
            The requested endpoint or asset does not exist in the current security perimeter.
          </p>
        </div>

        <div className="bg-muted/10 p-5 rounded-lg border border-border/40 font-mono text-left text-[11px] space-y-2.5 opacity-80">
          <p className="text-emerald-500 font-bold uppercase tracking-widest text-[10px]"># System Diagnostics</p>
          <div className="grid grid-cols-[80px_1fr] gap-x-4">
            <span className="text-muted-foreground">Path:</span>
            <span className="text-foreground truncate">{location.pathname}</span>
            <span className="text-muted-foreground">Context:</span>
            <span className="text-foreground">Global_Fleet_SOC</span>
            <span className="text-muted-foreground">Status:</span>
            <span className="text-rose-500 font-bold">ERR_NOT_FOUND</span>
          </div>
        </div>

        <Link
          to="/"
          className="inline-flex items-center gap-2 px-8 py-3 rounded-md bg-primary text-primary-foreground font-bold uppercase tracking-widest text-[11px] hover:bg-primary/90 transition-all shadow-sm active:scale-95 group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Return to Overview
        </Link>
      </div>

      <div className="absolute bottom-8 left-8 opacity-40 flex items-center gap-3">
        <ShieldAlert className="w-4 h-4 text-muted-foreground" />
        <span className="text-[10px] font-mono font-bold tracking-[0.3em] text-muted-foreground uppercase">Sentinel Security Protocol v4.2.1</span>
      </div>
    </div>
  );
};

export default NotFound;
