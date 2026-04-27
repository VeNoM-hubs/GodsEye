import type {
  MainLogRow, ThreatRow, ResourceRow,
  StatsResponse, AlertSeverity
} from "@shared/cyber-api";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status} on GET ${path}`);
  return res.json();
}

async function patch(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: "PATCH" });
  if (!res.ok) throw new Error(`HTTP ${res.status} on PATCH ${path}`);
}

export async function fetchEvents(params?: {
  limit?: number;
  offset?: number;
  severity?: AlertSeverity;
}): Promise<MainLogRow[]> {
  const q = new URLSearchParams();
  if (params?.limit)    q.set("limit",    String(params.limit));
  if (params?.offset)   q.set("offset",   String(params.offset));
  if (params?.severity) q.set("severity", params.severity);
  const qs = q.toString() ? `?${q}` : "";
  const data = await get<{ events: MainLogRow[] }>(`/api/events${qs}`);
  return data.events;
}

export async function fetchStats(): Promise<StatsResponse> {
  return get<StatsResponse>("/api/stats");
}

export async function fetchAlerts(): Promise<ThreatRow[]> {
  const data = await get<{ alerts: ThreatRow[] }>("/api/alerts");
  return data.alerts;
}

export async function acknowledgeAlert(threatId: number): Promise<void> {
  return patch(`/api/alerts/${threatId}/acknowledge`);
}

export async function resolveAlert(threatId: number): Promise<void> {
  return patch(`/api/alerts/${threatId}/resolve`);
}

export async function fetchResources(): Promise<ResourceRow[]> {
  const data = await get<{ resources: ResourceRow[] }>("/api/resources/with-activity");
  return data.resources;
}
