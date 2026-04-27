import { useState, useCallback } from "react";
import { fetchEvents, fetchAlerts, fetchResources, fetchHoneypotLogs } from "@/lib/api-client";
import type { AlertSeverity } from "@shared/cyber-api";

export type SearchResultType = "event" | "alert" | "resource" | "honeypot";

export interface SearchResult {
  id: string;
  type: SearchResultType;
  title: string;
  subtitle: string;
  timestamp: string;
  severity?: AlertSeverity;
  route: string;
  score: number;
}

function normalize(s: string): string {
  return s.toLowerCase().trim();
}

function scoreMatch(query: string, ...fields: (string | undefined | null)[]): number {
  const q = normalize(query);
  let best = 0;
  for (const raw of fields) {
    if (!raw) continue;
    const f = normalize(raw);
    if (f === q) { best = Math.max(best, 100); continue; }
    if (f.startsWith(q)) { best = Math.max(best, 70); continue; }
    if (f.includes(q)) { best = Math.max(best, 40); }
  }
  return best;
}

function severityFromString(s: string | null | undefined): AlertSeverity | undefined {
  if (!s) return undefined;
  const up = s.toUpperCase();
  if (["INFO","LOW","MEDIUM","HIGH","CRITICAL"].includes(up)) return up as AlertSeverity;
  return undefined;
}

export function useGlobalSearch() {
  const [results, setResults]   = useState<SearchResult[]>([]);
  const [loading, setLoading]   = useState(false);
  const [searched, setSearched] = useState(false);

  const runSearch = useCallback(async (query: string) => {
    const q = query.trim();
    if (!q) return;
    setLoading(true);
    setSearched(true);

    try {
      const [events, alerts, resources, honeypots] = await Promise.allSettled([
        fetchEvents({ limit: 200 }),
        fetchAlerts(),
        fetchResources(),
        fetchHoneypotLogs(200),
      ]);

      const out: SearchResult[] = [];

      // ── Events ────────────────────────────────────────────────────────────
      if (events.status === "fulfilled") {
        for (const e of events.value) {
          const score = scoreMatch(
            q,
            e.user_id, e.resource_id, e.event_type, e.severity, String(e.id)
          );
          if (score > 0) {
            out.push({
              id:        `event-${e.id}`,
              type:      "event",
              title:     `${e.event_type.toUpperCase()} — ${e.resource_id}`,
              subtitle:  `User: ${e.user_id ?? "—"}  ·  Severity: ${e.severity}`,
              timestamp: e.event_time,
              severity:  e.severity,
              route:     "/",
              score,
            });
          }
        }
      }

      // ── Alerts ────────────────────────────────────────────────────────────
      if (alerts.status === "fulfilled") {
        for (const a of alerts.value) {
          const score = scoreMatch(
            q,
            a.threat_pattern, a.user_id, a.mitre_id, String(a.threat_id), a.status
          );
          if (score > 0) {
            out.push({
              id:        `alert-${a.threat_id}`,
              type:      "alert",
              title:     a.threat_pattern,
              subtitle:  `Risk: ${a.risk_score}  ·  Status: ${a.status}${a.mitre_id ? `  ·  MITRE: ${a.mitre_id}` : ""}`,
              timestamp: a.last_seen,
              severity:  a.risk_score >= 90 ? "CRITICAL" : a.risk_score >= 70 ? "HIGH" : a.risk_score >= 50 ? "MEDIUM" : "LOW",
              route:     "/threats",
              score,
            });
          }
        }
      }

      // ── Resources ─────────────────────────────────────────────────────────
      if (resources.status === "fulfilled") {
        for (const r of resources.value) {
          const score = scoreMatch(
            q,
            r.resource_id, r.resource_name, r.resource_type, r.last_severity
          );
          if (score > 0) {
            out.push({
              id:        `resource-${r.resource_id}`,
              type:      "resource",
              title:     r.resource_name,
              subtitle:  `ID: ${r.resource_id}  ·  Type: ${r.resource_type}`,
              timestamp: r.last_event_time ?? new Date().toISOString(),
              severity:  severityFromString(r.last_severity),
              route:     "/devices",
              score,
            });
          }
        }
      }

      // ── Honeypot logs ─────────────────────────────────────────────────────
      if (honeypots.status === "fulfilled") {
        for (const h of honeypots.value) {
          const score = scoreMatch(
            q,
            h.attacker_ip, String(h.target_port), String(h.id),
            ...(h.commands_executed ?? [])
          );
          if (score > 0) {
            out.push({
              id:        `honeypot-${h.id}`,
              type:      "honeypot",
              title:     `Honeypot Hit — ${h.attacker_ip}`,
              subtitle:  `Port: ${h.target_port}${h.commands_executed?.length ? `  ·  Cmd: ${h.commands_executed[0]}` : ""}`,
              timestamp: h.timestamp,
              severity:  "HIGH",
              route:     "/threats",
              score,
            });
          }
        }
      }

      // Sort: score desc, then recency desc
      out.sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      });

      setResults(out);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSearch = useCallback(() => {
    setResults([]);
    setSearched(false);
  }, []);

  return { results, loading, searched, runSearch, clearSearch };
}
