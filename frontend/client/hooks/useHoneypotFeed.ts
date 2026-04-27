import { useEffect, useRef, useState } from "react";

export interface HoneypotEvent {
  id: number;
  honeypot_id: string | null;
  attacker_ip: string;
  target_port: number;
  threat_level: string | null;
  commands_executed: string[] | null;
  auth_success: boolean;
  timestamp: string; // ISO 8601
}

export function useHoneypotFeed(): HoneypotEvent[] {
  const [events, setEvents] = useState<HoneypotEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const unmountedRef = useRef(false);

  useEffect(() => {
    unmountedRef.current = false;

    function connect() {
      if (unmountedRef.current) return;

      const ws = new WebSocket("ws://localhost:8000/ws/honeypot");
      wsRef.current = ws;

      ws.onmessage = (e) => {
        try {
          const event: HoneypotEvent = JSON.parse(e.data);
          setEvents((prev) => [event, ...prev].slice(0, 200));
        } catch {}
      };

      ws.onclose = () => {
        if (!unmountedRef.current) {
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

  return events;
}
