import { useEffect, useRef, useState, useCallback } from "react";
import { Terminal, Copy, Check, WifiOff } from "lucide-react";
import type { GodsEyeEvent, AlertSeverity } from "@shared/cyber-api";
import { getEventUser, getEventResource, getEventSeverity, getEventDescription } from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

/* ── severity → label ─────────────────────────────────────────────────── */
const SEV_LABEL: Record<AlertSeverity, string> = {
    INFO: "INFO",
    LOW: "LOW ",
    MEDIUM: "WARN",
    HIGH: "ERR ",
    CRITICAL: "CRIT",
};

const SEV_COLOR: Record<AlertSeverity, string> = {
    INFO: "text-sky-400",
    LOW: "text-emerald-400",
    MEDIUM: "text-amber-400",
    HIGH: "text-orange-400",
    CRITICAL: "text-rose-500",
};

const SEV_DIM: Record<AlertSeverity, string> = {
    INFO: "text-sky-400/70",
    LOW: "text-emerald-400/70",
    MEDIUM: "text-amber-400/70",
    HIGH: "text-orange-400/70",
    CRITICAL: "text-rose-500/70",
};

const SOURCE_COLOR: Record<string, string> = {
    physical: "text-cyan-400",
    digital: "text-violet-400",
};

/* ── facility codes for realism ──────────────────────────────────────── */
const FACILITIES = ["kernel", "auth", "sshd", "nginx", "systemd", "firewalld", "auditd", "cron"];
const DEFAULT_WAZUH_WS_URL = "ws://10.188.231.155:8765";

function resolveWazuhWsUrl(): string {
    const raw = (import.meta as any).env?.VITE_WAZUH_WS_URL ?? DEFAULT_WAZUH_WS_URL;
    if (typeof window !== "undefined" && window.location.protocol === "https:" && raw.startsWith("ws://")) {
        return raw.replace(/^ws:\/\//, "wss://");
    }
    return raw;
}

function formatLogLine(ge: GodsEyeEvent) {
    const e = ge.event;
    const d = new Date(e.timestamp);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const timestamp = `${months[d.getMonth()]} ${String(d.getDate()).padStart(2, " ")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
    const host = getEventResource(e).toLowerCase().replace(/[\s/]+/g, "-").slice(0, 24);
    const facility = FACILITIES[Math.abs(e.event_id.charCodeAt(4)) % FACILITIES.length];
    const pid = String(1000 + (e.event_id.charCodeAt(5) % 9000));
    const user = getEventUser(e);
    const severity = getEventSeverity(e);
    const message = getEventDescription(e);
    const source = ge.source;

    return { timestamp, host, facility, pid, user, severity, message, source };
}

/* ── boot lines ───────────────────────────────────────────────────────── */
const BOOT_LINES = [
    "gods-eye-soc kernel: Initializing security event bus v2.4.1 …",
    "gods-eye-soc systemd[1]: Started GodsEye Security Operations Daemon.",
    "gods-eye-soc auditd[812]: audit daemon started with pid 812",
    "gods-eye-soc nginx[1024]: event-stream relay bound to 0.0.0.0:8443",
    "gods-eye-soc firewalld[932]: Loaded firewalld config; 47 active rules",
    "gods-eye-soc sshd[1101]: Server listening on 0.0.0.0 port 22",
    "gods-eye-soc kernel: cluster-west-02 uplink established (RTT 4ms)",
    "──────────────────────── LIVE FEED ──────────────────────────",
];

interface CliLine {
    id: string;
    isRaw?: boolean;
    content?: string;
    parts?: ReturnType<typeof formatLogLine>;
    kind?: "boot" | "ws";
}

interface CliTerminalProps {
    events: GodsEyeEvent[];
}

export function CliTerminal({ events }: CliTerminalProps) {
    const [lines, setLines] = useState<CliLine[]>(() =>
        BOOT_LINES.map((b, i) => ({ id: `boot-${i}`, isRaw: true, content: b, kind: "boot" }))
    );
    const [copied, setCopied] = useState(false);
    const [paused, setPaused] = useState(false);
    const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
    const bottomRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const processedIds = useRef<Set<string>>(new Set());

    const appendRawLine = useCallback((content: string, kind: "boot" | "ws") => {
        const id = `${kind}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        setLines((prev) => [...prev, { id, isRaw: true, content, kind }].slice(-200));
    }, []);

    const autoScroll = useCallback(() => {
        if (paused) return;
        const el = containerRef.current;
        if (el) el.scrollTop = el.scrollHeight;
    }, [paused]);

    useEffect(() => {
        let changed = false;
        const newLines: CliLine[] = [];
        for (const ge of [...events].reverse()) {
            if (!processedIds.current.has(ge.event.event_id)) {
                processedIds.current.add(ge.event.event_id);
                newLines.push({
                    id: ge.event.event_id,
                    parts: formatLogLine(ge),
                });
                changed = true;
            }
        }
        if (changed) setLines((prev) => [...prev, ...newLines].slice(-200));
    }, [events]);

    useEffect(() => {
        let ws: WebSocket | null = null;
        let reconnectTimer: number | undefined;
        let alive = true;

        function connect() {
            if (!alive) return;
            setWsStatus("connecting");
            try {
                ws = new WebSocket(resolveWazuhWsUrl());
            } catch {
                setWsStatus("disconnected");
                return;
            }

            ws.onopen = () => {
                setWsStatus("connected");
                appendRawLine("[wazuh] websocket connected", "ws");
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as {
                        time?: string;
                        agent?: string;
                        rule?: string;
                        severity?: number | string;
                    };
                    const time = data.time ?? new Date().toISOString();
                    const agent = data.agent ?? "unknown";
                    const rule = data.rule ?? "unknown";
                    const severity = data.severity ?? "n/a";
                    const line = `[${time}] ${agent} -> ${rule} (lvl:${severity})`;
                    appendRawLine(line, "ws");
                } catch {
                    // ignore malformed messages
                }
            };

            ws.onerror = () => {
                setWsStatus("disconnected");
                appendRawLine("[wazuh] websocket error", "ws");
            };

            ws.onclose = () => {
                if (!alive) return;
                setWsStatus("disconnected");
                appendRawLine("[wazuh] websocket disconnected", "ws");
                reconnectTimer = window.setTimeout(connect, 4000);
            };
        }

        connect();

        return () => {
            alive = false;
            if (reconnectTimer) window.clearTimeout(reconnectTimer);
            ws?.close();
        };
    }, [appendRawLine]);

    useEffect(() => { autoScroll(); }, [lines, autoScroll]);

    function handleScroll() {
        const el = containerRef.current;
        if (!el) return;
        setPaused(el.scrollHeight - el.scrollTop - el.clientHeight > 40);
    }

    async function handleCopy() {
        const text = lines.map((l) => {
            if (l.isRaw) return l.content;
            const p = l.parts!;
            return `${p.timestamp} [${p.source.toUpperCase()}] ${p.host} ${p.facility}[${p.pid}] ${p.user}: [${SEV_LABEL[p.severity]}] ${p.message}`;
        }).join("\n");
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1800);
    }

    return (
        <div className="rounded-xl border border-border/40 bg-[#0a0c12] overflow-hidden shadow-2xl relative flex flex-col h-full min-h-[420px] font-mono">
            {/* title bar */}
            <div className="flex items-center gap-0 px-4 py-2.5 border-b border-white/5 bg-[#111318] shrink-0">
                <div className="flex items-center gap-1.5 mr-4">
                    <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                    <div className="w-3 h-3 rounded-full bg-amber-400/80" />
                    <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="flex items-center gap-2 flex-1">
                    <Terminal className="w-3.5 h-3.5 text-primary/70" />
                    <span className="text-[11px] text-muted-foreground/60 tracking-widest uppercase select-none">
                        gods-eye — /var/log/security/live-stream
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    {paused && (
                        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-[9px] text-amber-400/80 font-bold uppercase tracking-widest flex items-center gap-1">
                            <WifiOff className="w-3 h-3" /> PAUSED
                        </motion.span>
                    )}
                    <button onClick={handleCopy} title="Copy all" className="p-1 rounded hover:bg-white/5 text-muted-foreground/50 hover:text-primary transition-colors">
                        {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                </div>
            </div>

            {/* info bar */}
            <div className="flex items-center justify-between px-4 py-1.5 bg-[#0d0f15] border-b border-white/5 shrink-0 text-[9px] font-mono text-muted-foreground/50 uppercase tracking-widest">
                <div className="flex items-center gap-4">
                    <span className="text-emerald-400/70 flex items-center gap-1">
                        <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> LIVE
                    </span>
                    <span>{lines.length} lines</span>
                    <span>enc: AES-256-GCM</span>
                </div>
                <span>
                    wazuh: {wsStatus} · relay: cluster-west-02 · pid 1
                </span>
            </div>

            {/* log body */}
            <div ref={containerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto px-4 py-3 space-y-px scrollbar-hide" style={{ scrollbarWidth: "none" }}>
                <AnimatePresence initial={false}>
                    {lines.map((line) => (
                        <motion.div
                            key={line.id}
                            initial={{ opacity: 0, x: -6 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.18 }}
                            className="leading-[1.7] text-[11px] whitespace-pre-wrap break-all"
                        >
                            {line.isRaw ? (
                                <span className={line.kind === "ws" ? "text-emerald-400/80" : "text-muted-foreground/30 italic"}>
                                    {line.content}
                                </span>
                            ) : (
                                <LogLine parts={line.parts!} />
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>

                <div className="flex items-center gap-1 mt-2">
                    <span className="text-primary/60 text-[11px]">root@gods-eye:~#</span>
                    <span className="inline-block w-2 h-3.5 bg-primary/80 animate-pulse ml-1" />
                </div>
                <div ref={bottomRef} />
            </div>
        </div>
    );
}

/* ── Individual formatted log line ──────────────────────────────────── */
function LogLine({ parts }: { parts: ReturnType<typeof formatLogLine> }) {
    return (
        <span>
            <span className="text-muted-foreground/50">{parts.timestamp} </span>
            {/* Source badge */}
            <span className={cn("font-bold", SOURCE_COLOR[parts.source])}>
                [{parts.source === "physical" ? "PHY" : "DIG"}]
            </span>{" "}
            {/* hostname/resource */}
            <span className="text-sky-400/80">{parts.host} </span>
            {/* facility[pid] */}
            <span className="text-violet-400/70">{parts.facility}</span>
            <span className="text-muted-foreground/40">[{parts.pid}]</span>{" "}
            {/* user */}
            <span className="text-teal-400/70">{parts.user}</span>
            <span className="text-muted-foreground/40">: </span>
            {/* severity */}
            <span className={cn("font-bold", SEV_COLOR[parts.severity])}>
                [{SEV_LABEL[parts.severity]}]
            </span>{" "}
            {/* message */}
            <span className={cn(SEV_DIM[parts.severity])}>{parts.message}</span>
        </span>
    );
}
