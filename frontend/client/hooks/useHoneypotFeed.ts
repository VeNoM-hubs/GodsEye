import { useEffect, useRef, useState } from "react";
import type { HoneypotFeedEvent } from "@shared/cyber-api";
import { fetchHoneypotLogs } from "@/lib/api-client";

// Re-export canonical type under the legacy name so existing imports don't break
export type HoneypotEvent = HoneypotFeedEvent;

export function useHoneypotFeed(): HoneypotEvent[] {
  const [events, setEvents] = useState<HoneypotEvent[]>([]);
  const wsRef        = useRef<WebSocket | null>(null);
  const unmountedRef = useRef(false);
  const seenIds      = useRef(new Set<number>());

  // Seed from REST on mount
  useEffect(() => {
    fetchHoneypotLogs(50)
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
      const ws = new WebSocket("ws://localhost:8000/ws/honeypot");
      wsRef.current = ws;

      ws.onmessage = (e) => {
        try {
          const event: HoneypotEvent = JSON.parse(e.data);
          if (seenIds.current.has(event.id)) return;
          seenIds.current.add(event.id);
          setEvents((prev) => [event, ...prev].slice(0, 200));
        } catch {}
      };

      ws.onclose = () => {
        if (!unmountedRef.current) setTimeout(connect, 3000);
      };
    }

    connect();
    return () => {
      unmountedRef.current = true;
      wsRef.current?.close();
    };
  }, []);

  return events;
}
