import { useState, useEffect, useCallback, useRef } from "react";
import {
  GodsEyeApiClient,
  WireEvent,
  WireAlert,
  WireDashboardStats,
} from "@shared/godseye-api-types";

export interface UseGodsEyeLiveReturn {
  events: WireEvent[];
  alerts: WireAlert[];
  stats: WireDashboardStats | null;
  ready: boolean;
  error: string | null;
  lastUpdated: number;
  paused: boolean;
  setPaused: (paused: boolean) => void;
}

const DEFAULT_STATS: WireDashboardStats = {
  active_threats: 0,
  total_violations: 0,
  events_per_minute: 0,
  mitre_breakdown: {},
  timestamp: new Date().toISOString(),
};

export function useGodsEyeLive(): UseGodsEyeLiveReturn {
  const [events, setEvents] = useState<WireEvent[]>([]);
  const [alerts, setAlerts] = useState<WireAlert[]>([]);
  const [stats, setStats] = useState<WireDashboardStats | null>(DEFAULT_STATS);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState(0);
  const [paused, setPaused] = useState(false);

  const lastTimestampRef = useRef<number>(0);
  const retryCountRef = useRef(0);
  const maxRetriesRef = useRef(3);

  // Initial load: fetch all data once
  const loadInitialData = useCallback(async () => {
    try {
      const [statsRes, eventsRes, alertsRes] = await Promise.all([
        GodsEyeApiClient.getStats(),
        GodsEyeApiClient.getEvents(100, 0),
        GodsEyeApiClient.getAlerts(),
      ]);

      setStats(statsRes);
      setEvents(eventsRes);
      setAlerts(alertsRes);
      setLastUpdated(Date.now());
      setReady(true);
      setError(null);
      retryCountRef.current = 0;

      // Set lastTimestamp to the most recent event's created_at timestamp
      if (eventsRes.length > 0) {
        const mostRecent = eventsRes[0];
        lastTimestampRef.current = new Date(mostRecent.created_at).getTime() / 1000;
      }
    } catch (err) {
      console.error("Failed to load initial data:", err);
      setReady(true);
      setError(err instanceof Error ? err.message : "Failed to load initial data");
    }
  }, []);

  // Polling: fetch new data every 3 seconds
  const pollData = useCallback(async () => {
    if (paused) return;

    try {
      const since = lastTimestampRef.current > 0 ? Math.floor(lastTimestampRef.current) : undefined;

      const [statsRes, eventsRes, alertsRes] = await Promise.all([
        GodsEyeApiClient.getStats(),
        GodsEyeApiClient.getEvents(100, 0, since),
        GodsEyeApiClient.getAlerts(),
      ]);

      // Update stats (replace entirely)
      setStats(statsRes);

      // Update alerts (replace entirely)
      setAlerts(alertsRes);

      // Append new events (deduplicate by event_id)
      setEvents((prev) => {
        const newEvents = eventsRes;
        const combined = [...newEvents, ...prev];

        // Deduplicate by event_id, keeping first occurrence
        const seen = new Set<string>();
        const deduped = combined.filter((event) => {
          if (seen.has(event.event_id)) {
            return false;
          }
          seen.add(event.event_id);
          return true;
        });

        // Limit to last 500 events to avoid memory bloat
        return deduped.slice(0, 500);
      });

      setLastUpdated(Date.now());
      setError(null);
      retryCountRef.current = 0;

      // Update lastTimestamp to most recent event's created_at
      if (eventsRes.length > 0) {
        const mostRecent = eventsRes[0];
        lastTimestampRef.current = new Date(mostRecent.created_at).getTime() / 1000;
      }
    } catch (err) {
      console.error("Polling error:", err);
      retryCountRef.current++;

      const errorMsg = err instanceof Error ? err.message : "API unreachable";
      setError(errorMsg);

      // Keep last known data, just show error
      // Don't clear events/alerts/stats on error
    }
  }, [paused]);

  // Handle acknowledge/resolve optimistically
  const optimisticAcknowledge = useCallback((alertId: string) => {
    setAlerts((prev) => prev.filter((a) => a.alert_id !== alertId));
    GodsEyeApiClient.acknowledgeAlert(alertId).catch(() => {
      // If fails, re-fetch to restore
      GodsEyeApiClient.getAlerts().then(setAlerts);
    });
  }, []);

  const optimisticResolve = useCallback((alertId: string) => {
    setAlerts((prev) => prev.filter((a) => a.alert_id !== alertId));
    GodsEyeApiClient.resolveAlert(alertId).catch(() => {
      // If fails, re-fetch to restore
      GodsEyeApiClient.getAlerts().then(setAlerts);
    });
  }, []);

  // Initial load effect
  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Polling effect
  useEffect(() => {
    if (!ready) return;

    const interval = setInterval(pollData, 3000);

    return () => clearInterval(interval);
  }, [ready, pollData]);

  return {
    events,
    alerts,
    stats,
    ready,
    error,
    lastUpdated,
    paused,
    setPaused,
  };
}
