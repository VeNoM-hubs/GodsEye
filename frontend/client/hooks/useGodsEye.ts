import { useCallback, useEffect, useRef, useState } from "react";
import type {
    GodsEyeEvent,
    SecurityAlert,
    DashboardStats,
    FlaggedUser,
    MitreEntry,
    TargetedResource,
    AlertSeverity,
} from "@shared/cyber-api";
import { getEventUser, getEventSeverity } from "@shared/cyber-api";
import {
    INITIAL_EVENTS,
    INITIAL_ALERTS,
    generateRandomEvent,
    generateAlert,
} from "@/lib/mock-data";

/* ── Aggregate helpers ────────────────────────────────────────────────── */

function computeStats(
    events: GodsEyeEvent[],
    alerts: SecurityAlert[]
): DashboardStats {
    const unresolvedAlerts = alerts.filter((a) => !a.resolved);

    // Access violations
    const accessViolations = events.filter(
        (e) =>
            e.event.event_type === "access" &&
            (e.event as any).status !== "success"
    ).length;

    // Events per minute (count events in last 60s)
    const oneMinAgo = Date.now() - 60_000;
    const recentCount = events.filter(
        (e) => new Date(e.event.timestamp).getTime() > oneMinAgo
    ).length;

    // Top flagged users
    const userMap = new Map<string, { count: number; sev: AlertSeverity }>();
    for (const a of unresolvedAlerts) {
        const uid = a.user_id ?? "unknown";
        const cur = userMap.get(uid);
        if (!cur) {
            userMap.set(uid, { count: 1, sev: a.severity });
        } else {
            cur.count++;
            if (sevRank(a.severity) > sevRank(cur.sev)) cur.sev = a.severity;
        }
    }
    const topFlaggedUsers: FlaggedUser[] = [...userMap.entries()]
        .map(([user_id, v]) => ({
            user_id,
            alert_count: v.count,
            highest_severity: v.sev,
        }))
        .sort((a, b) => b.alert_count - a.alert_count)
        .slice(0, 5);

    // MITRE distribution
    const mitreMap = new Map<string, MitreEntry>();
    for (const a of unresolvedAlerts) {
        if (!a.mitre_technique_id) continue;
        const cur = mitreMap.get(a.mitre_technique_id);
        if (!cur) {
            mitreMap.set(a.mitre_technique_id, {
                technique_id: a.mitre_technique_id,
                technique_name: a.mitre_technique_name ?? a.mitre_technique_id,
                count: 1,
            });
        } else {
            cur.count++;
        }
    }
    const mitreDistribution = [...mitreMap.values()].sort(
        (a, b) => b.count - a.count
    );

    // Targeted resources
    const resMap = new Map<string, number>();
    for (const a of unresolvedAlerts) {
        const r = a.resource ?? "unknown";
        resMap.set(r, (resMap.get(r) ?? 0) + 1);
    }
    const targetedResources: TargetedResource[] = [...resMap.entries()]
        .map(([resource, hit_count]) => ({ resource, hit_count }))
        .sort((a, b) => b.hit_count - a.hit_count)
        .slice(0, 6);

    return {
        active_threats: unresolvedAlerts.length,
        access_violations: accessViolations,
        events_per_minute: recentCount,
        top_flagged_users: topFlaggedUsers,
        mitre_distribution: mitreDistribution,
        targeted_resources: targetedResources,
    };
}

function sevRank(s: AlertSeverity): number {
    return { INFO: 0, LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 }[s] ?? 0;
}

/* ── Hook ─────────────────────────────────────────────────────────────── */

export function useGodsEye() {
    const [events, setEvents] = useState<GodsEyeEvent[]>(INITIAL_EVENTS);
    const [alerts, setAlerts] = useState<SecurityAlert[]>(INITIAL_ALERTS);
    const [paused, setPaused] = useState(false);
    const intervalRef = useRef<ReturnType<typeof setInterval>>();

    /** Generate one tick of data */
    const tick = useCallback(() => {
        const newEvent = generateRandomEvent();
        setEvents((prev) => [...prev.slice(-99), newEvent]);

        // ~40% chance to create a correlated alert
        if (Math.random() < 0.4) {
            const newAlert = generateAlert(newEvent.event.event_id);
            setAlerts((prev) => [...prev.slice(-49), newAlert]);
        }
    }, []);

    useEffect(() => {
        if (paused) return;
        intervalRef.current = setInterval(tick, 3000 + Math.random() * 2000);
        return () => clearInterval(intervalRef.current);
    }, [paused, tick]);

    const stats = computeStats(events, alerts);

    return {
        events,
        alerts,
        stats,
        paused,
        setPaused,
        ready: true, // future: false until WS handshake
    };
}
