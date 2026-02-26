import { useMemo } from "react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    ComposedChart,
    Line,
} from "recharts";
import { Activity, TrendingUp, Target } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { SecurityAlert, AlertSeverity } from "@shared/cyber-api";

/* ── Bucket alerts into time windows ──────────────────────────────────── */

interface BucketPoint {
    time: string;
    threats: number;
    critical: number;
    high: number;
    medium: number;
    /** Individual alerts in this bucket for tooltip */
    _alerts: SecurityAlert[];
}

function bucketise(alerts: SecurityAlert[], bucketCount = 20): BucketPoint[] {
    if (alerts.length === 0) return [];

    const sorted = [...alerts].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    const minT = new Date(sorted[0].timestamp).getTime();
    const maxT = Math.max(new Date(sorted[sorted.length - 1].timestamp).getTime(), minT + 60_000);
    const span = (maxT - minT) / bucketCount;

    const buckets: BucketPoint[] = [];
    for (let i = 0; i < bucketCount; i++) {
        const tStart = minT + i * span;
        const tEnd = tStart + span;
        const d = new Date(tStart);
        const hh = String(d.getHours()).padStart(2, "0");
        const mm = String(d.getMinutes()).padStart(2, "0");

        const inBucket = sorted.filter((a) => {
            const t = new Date(a.timestamp).getTime();
            return t >= tStart && t < tEnd;
        });

        buckets.push({
            time: `${hh}:${mm}`,
            threats: inBucket.length,
            critical: inBucket.filter((a) => a.severity === "CRITICAL").length,
            high: inBucket.filter((a) => a.severity === "HIGH").length,
            medium: inBucket.filter((a) => a.severity === "MEDIUM" || a.severity === "LOW").length,
            _alerts: inBucket,
        });
    }
    return buckets;
}

/* ── Custom tooltip ───────────────────────────────────────────────────── */

const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const bucket: BucketPoint = payload[0]?.payload;
    if (!bucket) return null;

    return (
        <div className="bg-card/95 backdrop-blur-xl border border-border/60 rounded-xl px-4 py-3 shadow-2xl text-xs font-mono min-w-[200px] max-w-[280px]">
            <p className="text-muted-foreground mb-2 font-bold uppercase tracking-widest">{label}</p>
            <div className="flex items-center gap-4 mb-2.5">
                <Stat label="Total" value={bucket.threats} color="text-violet-400" />
                <Stat label="Critical" value={bucket.critical} color="text-rose-400" />
                <Stat label="High" value={bucket.high} color="text-orange-400" />
            </div>
            {bucket._alerts.slice(0, 3).map((a) => (
                <div key={a.alert_id} className="border-t border-border/30 pt-1.5 mt-1.5 space-y-0.5">
                    <div className="flex items-center justify-between">
                        <span className="text-sky-400/80 font-bold">{a.mitre_technique_id ?? "—"}</span>
                        <span className={cn("font-bold", sevColor(a.severity))}>{a.severity}</span>
                    </div>
                    <div className="text-muted-foreground/60 text-[10px]">
                        User: <span className="text-foreground/70">{a.user_id ?? "—"}</span> · Risk: <span className="text-foreground/70">{a.risk_score}</span>
                    </div>
                </div>
            ))}
            {bucket._alerts.length > 3 && (
                <p className="text-muted-foreground/40 text-[9px] mt-1.5 text-center">
                    +{bucket._alerts.length - 3} more
                </p>
            )}
        </div>
    );
};

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
    return (
        <div className="text-center">
            <div className={cn("text-base font-black", color)}>{value}</div>
            <div className="text-[8px] text-muted-foreground/50 uppercase tracking-widest">{label}</div>
        </div>
    );
}

function sevColor(s: AlertSeverity) {
    return { INFO: "text-sky-400", LOW: "text-emerald-400", MEDIUM: "text-amber-400", HIGH: "text-orange-400", CRITICAL: "text-rose-500" }[s];
}

/* ── Component ──────────────────────────────────────────────────────────── */

interface AttackGraphProps {
    alerts: SecurityAlert[];
}

export function AttackGraph({ alerts }: AttackGraphProps) {
    const data = useMemo(() => bucketise(alerts, 20), [alerts]);

    const totalThreats = alerts.filter((a) => !a.resolved).length;
    const critCount = alerts.filter((a) => a.severity === "CRITICAL" && !a.resolved).length;

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="rounded-2xl border border-border/50 bg-card/30 backdrop-blur-md overflow-hidden shadow-2xl relative"
        >
            <div className="scanline opacity-5 absolute inset-0 pointer-events-none z-0" />

            {/* Header */}
            <div className="p-5 border-b border-border/50 flex items-center justify-between bg-muted/20 backdrop-blur-sm z-10 relative">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-violet-500/10 border border-violet-500/20">
                        <Target className="w-5 h-5 text-violet-400" />
                    </div>
                    <div>
                        <h3 className="font-bold text-lg tracking-tight">Attack Graph — Correlated Threats</h3>
                        <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5">
                            <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
                            Live · MITRE ATT&CK correlation
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <Pill label="Threats" value={totalThreats} color="text-violet-400" bg="bg-violet-400/10" border="border-violet-400/20" icon={<TrendingUp className="w-3 h-3" />} />
                    <Pill label="Critical" value={critCount} color="text-rose-400" bg="bg-rose-400/10" border="border-rose-400/20" />
                </div>
            </div>

            {/* Chart */}
            <div className="p-5 z-10 relative">
                <ResponsiveContainer width="100%" height={260}>
                    <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="gradThreats" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="gradCrit" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.25} />
                                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />

                        <XAxis
                            dataKey="time"
                            tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 10, fontFamily: "monospace" }}
                            axisLine={{ stroke: "rgba(255,255,255,0.08)" }}
                            tickLine={false}
                            interval="preserveStartEnd"
                            label={{ value: "Time (HH:MM)", position: "insideBottomRight", offset: -4, fill: "rgba(255,255,255,0.25)", fontSize: 9, fontFamily: "monospace" }}
                        />

                        <YAxis
                            tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 10, fontFamily: "monospace" }}
                            axisLine={false}
                            tickLine={false}
                            width={40}
                            allowDecimals={false}
                            label={{ value: "Threat Count", angle: -90, position: "insideLeft", offset: 12, fill: "rgba(255,255,255,0.25)", fontSize: 9, fontFamily: "monospace" }}
                        />

                        <Tooltip content={<CustomTooltip />} />

                        {/* Total threats area */}
                        <Area type="monotone" dataKey="threats" stroke="#8b5cf6" strokeWidth={2} fill="url(#gradThreats)" dot={false} activeDot={{ r: 5, strokeWidth: 0, fill: "#8b5cf6" }} isAnimationActive={false} />

                        {/* Critical line */}
                        <Line type="monotone" dataKey="critical" stroke="#f43f5e" strokeWidth={1.5} strokeDasharray="4 3" dot={{ r: 3, fill: "#f43f5e", strokeWidth: 0 }} isAnimationActive={false} />

                        {/* High line */}
                        <Line type="monotone" dataKey="high" stroke="#f97316" strokeWidth={1} dot={false} isAnimationActive={false} />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            {/* Footer */}
            <div className="px-5 pb-4 border-t border-border/30 pt-3 bg-muted/10 text-[10px] font-mono text-muted-foreground flex justify-between uppercase z-10 relative">
                <span>correlated threats · mitre att&ck mapped</span>
                <span>source: gods-eye / alert-engine</span>
            </div>
        </motion.div>
    );
}

/* ── Pill helper ────────────────────────────────────────────────────────── */
function Pill({ label, value, color, bg, border, icon }: { label: string; value: string | number; color: string; bg: string; border: string; icon?: React.ReactNode }) {
    return (
        <div className={cn("flex flex-col items-end px-3 py-1.5 rounded-lg border", bg, border)}>
            <span className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground">{label}</span>
            <span className={cn("text-sm font-bold flex items-center gap-1", color)}>{icon}{value}</span>
        </div>
    );
}
