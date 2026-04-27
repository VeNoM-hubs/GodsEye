import { useResources } from "@/hooks/useResources";
import { cn } from "@/lib/utils";
import type { AlertSeverity, ResourceRow } from "@shared/cyber-api";
import { DoorOpen, Server, Database, File, Shield, ShieldAlert, Monitor } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const resourceTypeIcons: Record<string, React.ReactNode> = {
  door: <DoorOpen className="w-4 h-4" />,
  server: <Server className="w-4 h-4" />,
  database: <Database className="w-4 h-4" />,
  file: <File className="w-4 h-4" />,
};

const typeLabels: Record<string, string> = {
  door: "Door",
  server: "Server",
  database: "Database",
  file: "File",
};

function getAccessLevelColor(level: number): string {
  if (level <= 3) return "bg-emerald-500/20 text-emerald-700";
  if (level <= 6) return "bg-amber-500/20 text-amber-700";
  return "bg-rose-500/20 text-rose-700";
}

function getSeverityColor(severity: AlertSeverity | null | undefined): string {
  if (!severity) return "bg-muted text-muted-foreground";
  const colors: Record<AlertSeverity, string> = {
    INFO: "bg-blue-500/20 text-blue-700",
    LOW: "bg-cyan-500/20 text-cyan-700",
    MEDIUM: "bg-amber-500/20 text-amber-700",
    HIGH: "bg-orange-500/20 text-orange-700",
    CRITICAL: "bg-rose-500/20 text-rose-700",
  };
  return colors[severity] || "bg-muted text-muted-foreground";
}

function getRelativeTime(isoString: string | null | undefined): string {
  if (!isoString) return "No recent events";
  const then = new Date(isoString).getTime();
  const now = Date.now();
  const mins = Math.floor((now - then) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function DeviceMap() {
  const { resources, loading } = useResources();

  const isRecentHighRisk = (resource: ResourceRow): boolean => {
    if (!resource.last_severity || !resource.last_event_time) return false;
    if (!["HIGH", "CRITICAL"].includes(resource.last_severity)) return false;
    const then = new Date(resource.last_event_time).getTime();
    const now = Date.now();
    return (now - then) < 5 * 60 * 1000; // within 5 minutes
  };

  return (
    <div className="w-full h-full bg-background rounded-lg border border-border">
      {/* Header */}
      <div className="p-5 border-b border-border flex items-center gap-2">
        <Monitor className="w-5 h-5 text-muted-foreground" />
        <h2 className="text-lg font-semibold">ICS Resource Inventory</h2>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Resource</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Access Level</TableHead>
              <TableHead>Sensitive</TableHead>
              <TableHead>Recent Activity</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              // Loading skeleton
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 5 }).map((_, j) => (
                    <TableCell key={j}>
                      <div className="h-4 bg-muted/40 rounded animate-pulse" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : resources.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                  No resources found
                </TableCell>
              </TableRow>
            ) : (
              resources.map((resource) => (
                <TableRow
                  key={resource.resource_id}
                  className={cn(
                    isRecentHighRisk(resource) &&
                      "bg-rose-500/5 border-l-2 border-l-rose-500/60"
                  )}
                >
                  {/* Resource: name + id */}
                  <TableCell>
                    <div>
                      <div className="font-medium">{resource.resource_name}</div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {resource.resource_id}
                      </div>
                    </div>
                  </TableCell>

                  {/* Type: icon + label */}
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {resourceTypeIcons[resource.resource_type]}
                      <span className="text-sm">
                        {typeLabels[resource.resource_type] || resource.resource_type}
                      </span>
                    </div>
                  </TableCell>

                  {/* Access Level: numeric badge */}
                  <TableCell>
                    <span
                      className={cn(
                        "inline-block px-2 py-1 rounded text-xs font-semibold",
                        getAccessLevelColor(resource.required_access_level)
                      )}
                    >
                      {resource.required_access_level}
                    </span>
                  </TableCell>

                  {/* Sensitive: check or dash */}
                  <TableCell className="text-center">
                    {resource.is_sensitive ? (
                      <Shield className="w-4 h-4 text-emerald-500 mx-auto" />
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>

                  {/* Recent Activity: severity + time or "No recent" */}
                  <TableCell>
                    {resource.last_severity && resource.last_event_time ? (
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            "inline-block px-2 py-1 rounded text-xs font-semibold",
                            getSeverityColor(resource.last_severity)
                          )}
                        >
                          {resource.last_severity}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {getRelativeTime(resource.last_event_time)}
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">
                        No recent events
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
