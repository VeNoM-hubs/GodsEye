import { useCallback, useEffect, useRef, useState } from "react";
import type {
  GodsEyeEvent, SecurityAlert, DashboardStats,
  FlaggedUser, MitreEntry, TargetedResource,
  AlertSeverity, MainLogRow, ThreatRow, WsMessage,
  ConnectionStatus,
} from "@shared/cyber-api";
import { fetchEvents, fetchStats, fetchAlerts } from "@/lib/api-client";

// ── DB row → GodsEyeEvent ────────────────────────────────────────────
function mapRowToEvent(row: MainLogRow): GodsEyeEvent {
  const source = row.source === "PHYSICAL" ? "physical" : "digital";

  // Determine event_type from DB source and event_type field
  let eventType: GodsEyeEvent["event"]["event_type"];
  if (row.source === "PHYSICAL") {
    eventType = "access";
  } else if (row.event_type.includes("honeypot")) {
    eventType = "honeypot";
  } else if (row.event_type.includes("teapot")) {
    eventType = "teapot";
  } else {
    eventType = "endpoint";
  }

  // Build the minimal RawEvent shape the components actually read.
  const base = {
    event_id:   `ml_${row.id}`,
    event_type: eventType as any,
    timestamp:  row.event_time,
  };

  if (eventType === "access") {
    return {
      source,
      event: {
        ...base,
        device_id:     row.resource_id,
        location:      row.resource_id,
        access_method: "rfid" as const,
        status:        mapEventTypeToStatus(row.event_type),
        user_id:       row.user_id,
      },
    };
  }

  // endpoint / digital fallback
  return {
    source,
    event: {
      ...base,
      event_type:          "endpoint" as const,
      hostname:            row.resource_id,
      endpoint_id:         `ep_${row.source_ref_id}`,
      operating_system:    "OT Workstation",
      endpoint_event_type: "process_creation" as const,
      user:                row.user_id,
      severity:            row.severity,
      description:         row.event_type,
    },
  };
}

function mapEventTypeToStatus(et: string): "success" | "failed" | "denied" | "anomaly" {
  if (et === "SUCCESS")  return "success";
  if (et === "DENIED")   return "denied";
  if (et === "ANOMALY")  return "anomaly";
  return "failed";
}

// ── ThreatRow → SecurityAlert ────────────────────────────────────────
function mapThreatToAlert(t: ThreatRow): SecurityAlert {
  return {
    alert_id:            String(t.threat_id),
    alert_type:          "access_anomaly",
    severity:            riskScoreToSeverity(t.risk_score),
    title:               t.threat_pattern,
    description:         t.threat_pattern,
    source_event_id:     `threat_${t.threat_id}`,
    timestamp:           t.last_seen,
    mitre_technique_id:  t.mitre_id ?? undefined,
    mitre_technique_name: t.mitre_id ?? undefined,
    risk_score:          t.risk_score,
    user_id:             t.user_id,
    acknowledged:        t.status === "ACKNOWLEDGED",
    resolved:            t.status === "RESOLVED",
  };
}

function riskScoreToSeverity(score: number): AlertSeverity {
  if (score >= 90) return "CRITICAL";
  if (score >= 70) return "HIGH";
  if (score >= 50) return "MEDIUM";
  if (score >= 30) return "LOW";
  return "INFO";
}

// ── Stats computation (identical logic to old mock hook) ─────────────
function computeStats(events: GodsEyeEvent[], alerts: SecurityAlert[]): DashboardStats {
  const unresolved = alerts.filter((a) => !a.resolved);
  const accessViolations = events.filter(
    (e) => e.event.event_type === "access" && (e.event as any).status !== "success"
  ).length;
  const oneMinAgo = Date.now() - 60_000;
  const eventsPerMinute = events.filter(
    (e) => new Date(e.event.timestamp).getTime() > oneMinAgo
  ).length;

  const userMap = new Map<string, { count: number; sev: AlertSeverity }>();
  for (const a of unresolved) {
    const uid = a.user_id ?? "unknown";
    const cur = userMap.get(uid);
    if (!cur) userMap.set(uid, { count: 1, sev: a.severity });
    else { cur.count++; if (sevRank(a.severity) > sevRank(cur.sev)) cur.sev = a.severity; }
  }
  const top_flagged_users: FlaggedUser[] = [...userMap.entries()]
    .map(([user_id, v]) => ({ user_id, alert_count: v.count, highest_severity: v.sev }))
    .sort((a, b) => b.alert_count - a.alert_count).slice(0, 5);

  const mitreMap = new Map<string, MitreEntry>();
  for (const a of unresolved) {
    if (!a.mitre_technique_id) continue;
    const cur = mitreMap.get(a.mitre_technique_id);
    if (!cur) mitreMap.set(a.mitre_technique_id, { technique_id: a.mitre_technique_id, technique_name: a.mitre_technique_name ?? a.mitre_technique_id, count: 1 });
    else cur.count++;
  }
  const mitre_distribution = [...mitreMap.values()].sort((a, b) => b.count - a.count);

  const resMap = new Map<string, number>();
  for (const a of unresolved) { const r = a.resource ?? "unknown"; resMap.set(r, (resMap.get(r) ?? 0) + 1); }
  const targeted_resources: TargetedResource[] = [...resMap.entries()]
    .map(([resource, hit_count]) => ({ resource, hit_count }))
    .sort((a, b) => b.hit_count - a.hit_count).slice(0, 6);

  return { active_threats: unresolved.length, access_violations: accessViolations, events_per_minute: eventsPerMinute, top_flagged_users, mitre_distribution, targeted_resources };
}

function sevRank(s: AlertSeverity) {
  return { INFO: 0, LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 }[s] ?? 0;
}

// ── Hook ─────────────────────────────────────────────────────────────
export function useGodsEye() {
  const [events, setEvents]               = useState<GodsEyeEvent[]>([]);
  const [alerts, setAlerts]               = useState<SecurityAlert[]>([]);
  const [ready,  setReady]                = useState(false);
  const [connectionStatus, setStatus]     = useState<ConnectionStatus>("connecting");
  const wsRef   = useRef<WebSocket | null>(null);
  const retryMs = useRef(3000);

  // ── Initial REST fetch ────────────────────────────────────────────
  useEffect(() => {
    Promise.all([fetchEvents({ limit: 50 }), fetchAlerts()])
      .then(([rows, threats]) => {
        setEvents(rows.map(mapRowToEvent));
        setAlerts(threats.map(mapThreatToAlert));
        setReady(true);
      })
      .catch((err) => {
        console.error("Initial fetch failed:", err);
        setReady(true);
      });
  }, []);

  // ── WebSocket connection ──────────────────────────────────────────
  const connect = useCallback(() => {
    const url = (import.meta as any).env?.VITE_WS_URL ?? "ws://localhost:8000/ws";
    const ws  = new WebSocket(url);
    wsRef.current = ws;
    setStatus("connecting");

    ws.onopen = () => {
      setStatus("connected");
      retryMs.current = 3000;
    };

    ws.onmessage = (e) => {
      try {
        const msg: WsMessage = JSON.parse(e.data);
        if (msg.type !== "batch") return;
        if (msg.events?.length) {
          setEvents((prev) => [...prev, ...msg.events!.map(mapRowToEvent)].slice(-100));
        }
        if (msg.threats?.length) {
          const incoming = msg.threats!.map(mapThreatToAlert);
          setAlerts((prev) => {
            const map = new Map(prev.map((a) => [a.alert_id, a]));
            incoming.forEach((a) => map.set(a.alert_id, a));
            return [...map.values()].slice(-50);
          });
        }
      } catch { }
    };

    ws.onerror = () => setStatus("disconnected");

    ws.onclose = () => {
      setStatus("disconnected");
      setTimeout(() => {
        retryMs.current = Math.min(retryMs.current * 2, 30_000);
        connect();
      }, retryMs.current);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => { wsRef.current?.close(); };
  }, [connect]);

  const stats = computeStats(events, alerts);

  return { events, alerts, stats, ready, connectionStatus };
}
