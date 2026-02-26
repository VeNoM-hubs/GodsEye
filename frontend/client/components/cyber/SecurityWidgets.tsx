import { ShieldAlert, Ban, UserX, Activity, Brain, Building2 } from "lucide-react";
import type {
    DashboardStats,
    MitreEntry,
    FlaggedUser,
    TargetedResource,
    AlertSeverity,
} from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

/* ── Severity colour helper ───────────────────────────────────────────── */
const SEV_DOT: Record<AlertSeverity, string> = {
    INFO: "bg-sky-400",
    LOW: "bg-emerald-400",
    MEDIUM: "bg-amber-400",
    HIGH: "bg-orange-500",
    CRITICAL: "bg-rose-500",
};

/* ── Main component ───────────────────────────────────────────────────── */
interface SecurityWidgetsProps {
    stats: DashboardStats;
}

export function SecurityWidgets({ stats }: SecurityWidgetsProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {/* 1 — Active Threats */}
            <Widget
                icon={ShieldAlert}
                label="Active Threats"
                color="rose"
                delay={0}
            >
                <div className="flex items-end gap-3">
                    <span className="text-4xl font-black tracking-tight text-rose-400">
                        {stats.active_threats}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-rose-400/60 mb-1.5">
                        unresolved
                    </span>
                </div>
            </Widget>

            {/* 2 — Access Violations */}
            <Widget
                icon={Ban}
                label="Access Violations"
                color="amber"
                delay={0.04}
            >
                <div className="flex items-end gap-3">
                    <span className="text-4xl font-black tracking-tight text-amber-400">
                        {stats.access_violations}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-amber-400/60 mb-1.5">
                        failed / denied
                    </span>
                </div>
            </Widget>

            {/* 3 — Events Per Minute */}
            <Widget
                icon={Activity}
                label="Events Per Minute"
                color="emerald"
                delay={0.08}
            >
                <div className="flex items-end gap-3">
                    <span className="text-4xl font-black tracking-tight text-emerald-400">
                        {stats.events_per_minute}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400/60 mb-1.5">
                        last 60 s
                    </span>
                </div>
            </Widget>

            {/* 4 — Top Flagged Users */}
            <Widget
                icon={UserX}
                label="Top Flagged Users"
                color="violet"
                delay={0.12}
            >
                {stats.top_flagged_users.length === 0 ? (
                    <span className="text-[11px] text-muted-foreground/50 italic">
                        No flagged users
                    </span>
                ) : (
                    <div className="space-y-1.5 mt-1">
                        {stats.top_flagged_users.slice(0, 4).map((u) => (
                            <UserRow key={u.user_id} user={u} />
                        ))}
                    </div>
                )}
            </Widget>

            {/* 5 — MITRE Technique Distribution */}
            <Widget
                icon={Brain}
                label="MITRE ATT&CK Map"
                color="sky"
                delay={0.16}
            >
                {stats.mitre_distribution.length === 0 ? (
                    <span className="text-[11px] text-muted-foreground/50 italic">
                        No data
                    </span>
                ) : (
                    <div className="space-y-1.5 mt-1">
                        {stats.mitre_distribution.slice(0, 4).map((m) => (
                            <MitreBar key={m.technique_id} entry={m} max={stats.mitre_distribution[0].count} />
                        ))}
                    </div>
                )}
            </Widget>

            {/* 6 — Most Targeted Resources */}
            <Widget
                icon={Building2}
                label="Targeted Resources"
                color="orange"
                delay={0.20}
            >
                {stats.targeted_resources.length === 0 ? (
                    <span className="text-[11px] text-muted-foreground/50 italic">
                        No data
                    </span>
                ) : (
                    <div className="space-y-1.5 mt-1">
                        {stats.targeted_resources.slice(0, 4).map((r) => (
                            <ResourceRow key={r.resource} entry={r} />
                        ))}
                    </div>
                )}
            </Widget>
        </div>
    );
}

/* ── Widget card shell ────────────────────────────────────────────────── */
const COLOR_MAP: Record<string, { bg: string; border: string; text: string; icon: string }> = {
    rose: { bg: "bg-rose-400/5", border: "border-rose-400/20", text: "text-rose-400", icon: "bg-rose-400/10" },
    amber: { bg: "bg-amber-400/5", border: "border-amber-400/20", text: "text-amber-400", icon: "bg-amber-400/10" },
    emerald: { bg: "bg-emerald-400/5", border: "border-emerald-400/20", text: "text-emerald-400", icon: "bg-emerald-400/10" },
    violet: { bg: "bg-violet-400/5", border: "border-violet-400/20", text: "text-violet-400", icon: "bg-violet-400/10" },
    sky: { bg: "bg-sky-400/5", border: "border-sky-400/20", text: "text-sky-400", icon: "bg-sky-400/10" },
    orange: { bg: "bg-orange-400/5", border: "border-orange-400/20", text: "text-orange-400", icon: "bg-orange-400/10" },
};

function Widget({
    icon: Icon,
    label,
    color,
    delay,
    children,
}: {
    icon: React.ElementType;
    label: string;
    color: string;
    delay: number;
    children: React.ReactNode;
}) {
    const c = COLOR_MAP[color] ?? COLOR_MAP.sky;
    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay }}
            className={cn(
                "p-4 rounded-xl border bg-card/40 backdrop-blur-sm relative overflow-hidden transition-all duration-300 hover:bg-card/60 hover:border-border/60 shadow-sm",
                c.border
            )}
        >
            <div className="flex items-center gap-2.5 mb-3">
                <div className={cn("p-1.5 rounded-lg border", c.icon, c.border)}>
                    <Icon className={cn("w-4 h-4", c.text)} />
                </div>
                <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-muted-foreground">
                    {label}
                </p>
            </div>
            {children}
        </motion.div>
    );
}

/* ── Sub-components ───────────────────────────────────────────────────── */

function UserRow({ user }: { user: FlaggedUser }) {
    return (
        <div className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-2">
                <span className={cn("w-1.5 h-1.5 rounded-full", SEV_DOT[user.highest_severity])} />
                <span className="font-mono font-semibold text-foreground/80 truncate max-w-[120px]">
                    {user.user_id}
                </span>
            </div>
            <span className="text-muted-foreground font-bold">{user.alert_count}</span>
        </div>
    );
}

function MitreBar({ entry, max }: { entry: MitreEntry; max: number }) {
    const pct = Math.max(12, (entry.count / max) * 100);
    return (
        <div className="space-y-0.5">
            <div className="flex items-center justify-between text-[10px]">
                <span className="font-mono text-sky-400/70 font-bold">{entry.technique_id}</span>
                <span className="text-muted-foreground">{entry.count}</span>
            </div>
            <div className="h-1 rounded-full bg-muted/20 overflow-hidden">
                <motion.div
                    className="h-full rounded-full bg-sky-400/60"
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.6 }}
                />
            </div>
        </div>
    );
}

function ResourceRow({ entry }: { entry: TargetedResource }) {
    return (
        <div className="flex items-center justify-between text-[11px]">
            <span className="text-foreground/70 font-semibold truncate max-w-[160px]">
                {entry.resource}
            </span>
            <span className="text-orange-400 font-bold font-mono">{entry.hit_count}</span>
        </div>
    );
}
