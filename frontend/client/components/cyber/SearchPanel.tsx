import { X, Search, AlertTriangle, Server, Shield, Bug, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import type { SearchResult, SearchResultType } from "@/hooks/useGlobalSearch";
import type { AlertSeverity } from "@shared/cyber-api";

interface SearchPanelProps {
  open: boolean;
  query: string;
  loading: boolean;
  searched: boolean;
  results: SearchResult[];
  onClose: () => void;
  onNavigate: (route: string) => void;
}

const TYPE_LABELS: Record<SearchResultType, string> = {
  event:    "Events",
  alert:    "Alerts",
  resource: "Devices / Resources",
  honeypot: "Honeypot Logs",
};

const TYPE_ICON: Record<SearchResultType, React.ElementType> = {
  event:    AlertTriangle,
  alert:    Shield,
  resource: Server,
  honeypot: Bug,
};

const SEV_COLOR: Record<AlertSeverity, string> = {
  CRITICAL: "text-rose-400   bg-rose-900/30  border-rose-700/50",
  HIGH:     "text-orange-400 bg-orange-900/30 border-orange-700/50",
  MEDIUM:   "text-yellow-400 bg-yellow-900/30 border-yellow-700/50",
  LOW:      "text-blue-400   bg-blue-900/30  border-blue-700/50",
  INFO:     "text-muted-foreground bg-muted/30 border-border/40",
};

function SeverityBadge({ sev }: { sev?: AlertSeverity }) {
  if (!sev) return null;
  return (
    <span className={cn("px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border", SEV_COLOR[sev])}>
      {sev}
    </span>
  );
}

function ResultRow({ result, onNavigate }: { result: SearchResult; onNavigate: (r: string) => void }) {
  const Icon = TYPE_ICON[result.type];
  return (
    <button
      onClick={() => onNavigate(result.route)}
      className="w-full flex items-start gap-3 px-4 py-3 rounded-lg hover:bg-muted/30 border border-transparent hover:border-border/40 transition-all text-left group"
    >
      <div className="mt-0.5 w-7 h-7 flex-shrink-0 flex items-center justify-center rounded-md bg-muted/30 border border-border/40 group-hover:border-primary/40 transition-colors">
        <Icon className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary transition-colors" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[13px] font-semibold text-foreground truncate">{result.title}</span>
          <SeverityBadge sev={result.severity} />
        </div>
        <p className="text-[11px] text-muted-foreground mt-0.5 truncate">{result.subtitle}</p>
      </div>
      <time className="text-[10px] text-muted-foreground/60 flex-shrink-0 mt-1">
        {new Date(result.timestamp).toLocaleString()}
      </time>
    </button>
  );
}

export function SearchPanel({ open, query, loading, searched, results, onClose, onNavigate }: SearchPanelProps) {
  const grouped = results.reduce<Partial<Record<SearchResultType, SearchResult[]>>>((acc, r) => {
    (acc[r.type] ??= []).push(r);
    return acc;
  }, {});

  const order: SearchResultType[] = ["alert", "event", "honeypot", "resource"];
  const hasResults = results.length > 0;

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) onClose(); }}>
      <DialogContent className="max-w-3xl w-full max-h-[85vh] flex flex-col p-0 border-border/60 bg-background/95 backdrop-blur-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-border/40 flex-shrink-0">
          <Search className="w-4 h-4 text-muted-foreground flex-shrink-0" />
          <DialogTitle className="flex-1 text-[13px] font-medium text-foreground">
            {loading ? (
              <span className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Searching across all data sources…
              </span>
            ) : searched ? (
              <span>
                {hasResults
                  ? <><span className="text-primary font-bold">{results.length}</span> results for <span className="text-primary font-bold">"{query}"</span></>
                  : <>No results for <span className="text-muted-foreground font-bold">"{query}"</span></>}
              </span>
            ) : (
              <span className="text-muted-foreground">Search results</span>
            )}
          </DialogTitle>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-muted/40 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto scrollbar-hide px-3 py-3 space-y-5">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <Loader2 className="w-8 h-8 animate-spin mb-3 opacity-50" />
              <p className="text-sm">Fetching events, alerts, resources, and honeypot logs…</p>
            </div>
          )}

          {!loading && searched && !hasResults && (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <Search className="w-10 h-10 mb-4 opacity-20" />
              <p className="text-sm font-medium">No matching results</p>
              <p className="text-[11px] mt-1 opacity-60">Try a different IP, user ID, resource name, or severity</p>
            </div>
          )}

          {!loading && hasResults && order.map((type) => {
            const group = grouped[type];
            if (!group?.length) return null;
            const Icon = TYPE_ICON[type];
            return (
              <div key={type}>
                <div className="flex items-center gap-2 px-1 mb-2">
                  <Icon className="w-3 h-3 text-muted-foreground/60" />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                    {TYPE_LABELS[type]}
                  </span>
                  <span className="text-[10px] text-muted-foreground/40">({group.length})</span>
                </div>
                <div className="space-y-0.5">
                  {group.slice(0, 8).map((r) => (
                    <ResultRow key={r.id} result={r} onNavigate={onNavigate} />
                  ))}
                  {group.length > 8 && (
                    <p className="text-[10px] text-muted-foreground/50 px-4 py-1">
                      +{group.length - 8} more — refine your query to narrow results
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        {hasResults && !loading && (
          <div className="border-t border-border/40 px-5 py-2.5 flex items-center justify-between flex-shrink-0">
            <span className="text-[10px] text-muted-foreground/50 uppercase tracking-widest">
              Click a result to navigate · Exact matches rank first
            </span>
            <button
              onClick={onClose}
              className="text-[10px] text-muted-foreground/60 hover:text-muted-foreground transition-colors uppercase tracking-widest font-bold"
            >
              Close
            </button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
