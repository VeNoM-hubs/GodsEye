import { useEffect, useRef, useState } from "react";
import type { HoneypotFeedEvent } from "@shared/cyber-api";
import { fetchHoneypotLogs } from "@/lib/api-client";

export type HoneypotEvent = HoneypotFeedEvent;
export type WsStatus = "connecting" | "connected" | "disconnected";

// Derive the WS URL from env: prefer explicit VITE_WS_URL, otherwise swap
// protocol on VITE_API_BASE_URL and append the honeypot path.
function resolveWsUrl(): string {
  const explicit = import.meta.env.VITE_WS_URL as string | undefined;
  if (explicit) return explicit;
  const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8080";
  return base.replace(/^http/, "ws") + "/ws/honeypot";
}

function isHoneypotEvent(v: unknown): v is HoneypotEvent {
  if (!v || typeof v !== "object") return false;
  const o = v as Record<string, unknown>;
  return (
    typeof o.id === "number" &&
    typeof o.attacker_ip === "string" &&
    typeof o.target_port === "number"
  );
}

export interface HoneypotFeedResult {
  events: HoneypotEvent[];
  wsStatus: WsStatus;
}

export function useHoneypotFeed(): HoneypotFeedResult {
  const [events,   setEvents]   = useState<HoneypotEvent[]>([]);
  const [wsStatus, setWsStatus] = useState<WsStatus>("connecting");

  const wsRef        = useRef<WebSocket | null>(null);
  const unmountedRef = useRef(false);
  const seenIds      = useRef(new Set<number>());

  // Seed from REST on mount
  useEffect(() => {
    fetchHoneypotLogs(100)
      .then((rows) => {
        rows.forEach((r) => seenIds.current.add(r.id));
        setEvents(rows);
      })
      .catch(() => {});
  }, []);

  // WebSocket live append
  useEffect(() => {
    unmountedRef.current = false;

    function connect() {
      if (unmountedRef.current) return;
      const wsUrl = resolveWsUrl();
      setWsStatus("connecting");

      let ws: WebSocket;
      try {
        ws = new WebSocket(wsUrl);
      } catch {
        // Invalid URL — don't retry forever
        setWsStatus("disconnected");
        return;
      }
      wsRef.current = ws;

      ws.onopen = () => {
        if (!unmountedRef.current) setWsStatus("connected");
      };

      ws.onmessage = (e) => {
        try {
          const payload: unknown = JSON.parse(e.data);
          if (!isHoneypotEvent(payload)) return;   // ignore batch or heartbeat frames
          if (seenIds.current.has(payload.id)) return;
          seenIds.current.add(payload.id);
          setEvents((prev) => [payload, ...prev].slice(0, 200));
        } catch {
          // malformed JSON — silently ignore
        }
      };

      ws.onerror = () => {
        if (!unmountedRef.current) setWsStatus("disconnected");
      };

      ws.onclose = () => {
        if (!unmountedRef.current) {
          setWsStatus("disconnected");
          setTimeout(connect, 3000);
        }
      };
    }

    connect();
    return () => {
      unmountedRef.current = true;
      wsRef.current?.close();
    };
  }, []);

  return { events, wsStatus };
}
