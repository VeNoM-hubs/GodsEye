import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { AlertSeverity, ThreatRow, WsMessage } from "@shared/cyber-api";
import { fetchAlerts } from "@/lib/api-client";

export type WsStatus = "connecting" | "connected" | "disconnected";

export interface AlertNotification {
  threat_id: number;
  threat_pattern: string;
  risk_score: number;
  severity: AlertSeverity;
  status: ThreatRow["status"];
  last_seen: string;
  first_seen: string;
  user_id: string;
  mitre_id: string | null;
  event_count: number;
}

export interface AlertNotificationItem extends AlertNotification {
  unread: boolean;
}

export interface UseAlertNotificationsResult {
  notifications: AlertNotificationItem[];
  unreadCount: number;
  wsStatus: WsStatus;
  markAllRead: () => void;
  clearAll: () => void;
}

function resolveAlertsWsUrl(): string {
  const explicit = import.meta.env.VITE_WS_ALERTS_URL as string | undefined;
  if (explicit) return explicit;
  const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8080";
  return base.replace(/^http/, "ws") + "/ws";
}

function scoreToSeverity(score: number): AlertSeverity {
  if (score <= 10) {
    if (score <= 3) return "INFO";
    if (score <= 6) return "LOW";
    if (score <= 8) return "MEDIUM";
    if (score <= 10) return "HIGH";
    return "CRITICAL";
  }
  if (score >= 90) return "CRITICAL";
  if (score >= 70) return "HIGH";
  if (score >= 50) return "MEDIUM";
  if (score >= 30) return "LOW";
  return "INFO";
}

function isHighRisk(severity: AlertSeverity): boolean {
  return severity === "HIGH" || severity === "CRITICAL";
}

function normalizeThreat(threat: ThreatRow): AlertNotification | null {
  const severity = scoreToSeverity(threat.risk_score);
  if (!isHighRisk(severity)) return null;
  if (threat.status === "RESOLVED") return null;

  return {
    threat_id: threat.threat_id,
    threat_pattern: threat.threat_pattern,
    risk_score: threat.risk_score,
    severity,
    status: threat.status,
    last_seen: threat.last_seen,
    first_seen: threat.first_seen,
    user_id: threat.user_id,
    mitre_id: threat.mitre_id,
    event_count: threat.event_count,
  };
}

function sortByLastSeen(a: AlertNotification, b: AlertNotification): number {
  return new Date(b.last_seen).getTime() - new Date(a.last_seen).getTime();
}

export function useAlertNotifications(): UseAlertNotificationsResult {
  const [items, setItems] = useState<AlertNotification[]>([]);
  const [wsStatus, setWsStatus] = useState<WsStatus>("connecting");
  const [lastReadAt, setLastReadAt] = useState<number>(() => Date.now());

  const wsRef = useRef<WebSocket | null>(null);
  const unmountedRef = useRef(false);

  const upsertThreats = useCallback((threats: ThreatRow[]) => {
    setItems((prev) => {
      const map = new Map(prev.map((item) => [item.threat_id, item]));
      for (const threat of threats) {
        const normalized = normalizeThreat(threat);
        if (!normalized) {
          map.delete(threat.threat_id);
          continue;
        }
        map.set(normalized.threat_id, normalized);
      }
      return [...map.values()].sort(sortByLastSeen).slice(0, 20);
    });
  }, []);

  useEffect(() => {
    fetchAlerts()
      .then((alerts) => {
        upsertThreats(alerts);
      })
      .catch(() => {});
  }, [upsertThreats]);

  useEffect(() => {
    unmountedRef.current = false;

    function connect() {
      if (unmountedRef.current) return;
      const wsUrl = resolveAlertsWsUrl();
      setWsStatus("connecting");

      let ws: WebSocket;
      try {
        ws = new WebSocket(wsUrl);
      } catch {
        setWsStatus("disconnected");
        return;
      }

      wsRef.current = ws;

      ws.onopen = () => {
        if (!unmountedRef.current) setWsStatus("connected");
      };

      ws.onmessage = (e) => {
        try {
          const msg: WsMessage = JSON.parse(e.data);
          if (msg.type !== "batch" || !msg.threats?.length) return;
          upsertThreats(msg.threats);
        } catch {
          // ignore malformed frames
        }
      };

      ws.onerror = () => {
        if (!unmountedRef.current) setWsStatus("disconnected");
      };

      ws.onclose = () => {
        if (!unmountedRef.current) {
          setWsStatus("disconnected");
          setTimeout(connect, 4000);
        }
      };
    }

    connect();
    return () => {
      unmountedRef.current = true;
      wsRef.current?.close();
    };
  }, [upsertThreats]);

  const notifications = useMemo<AlertNotificationItem[]>(() => {
    return items.map((item) => ({
      ...item,
      unread: new Date(item.last_seen).getTime() > lastReadAt,
    }));
  }, [items, lastReadAt]);

  const unreadCount = useMemo(() => notifications.filter((n) => n.unread).length, [notifications]);

  const markAllRead = useCallback(() => {
    setLastReadAt(Date.now());
  }, []);

  const clearAll = useCallback(() => {
    setItems([]);
  }, []);

  return {
    notifications,
    unreadCount,
    wsStatus,
    markAllRead,
    clearAll,
  };
}
