import { useRef, useState, useEffect } from "react";
import { Globe, Server, Smartphone, Monitor, Wifi } from "lucide-react";
import { Device } from "@shared/cyber-api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

/* ─────────────────────────────────────────────────────────────────────────
   Tiny equirectangular land-mask
   Source: hand-coded coarse polygon set – continents only, good enough
   for a decorative dotted globe.  Each entry is [lng, lat] pairs tracing
   a closed polygon in degrees.
──────────────────────────────────────────────────────────────────────────*/
const LAND_POLYGONS: Array<[number, number][]> = [
  // North America (coarse)
  [[-168, 72], [-140, 72], [-120, 76], [-83, 74], [-65, 68], [-53, 55], [-56, 47], [-66, 44], [-70, 41], [-75, 35], [-80, 25], [-87, 16], [-92, 16], [-90, 10], [-83, 8], [-77, 8], [-75, 10], [-76, 18], [-73, 20], [-72, 18], [-67, 18], [-62, 10], [-60, 7], [-62, 4], [-80, 4], [-82, 10], [-84, 9], [-86, 11], [-87, 16], [-90, 20], [-97, 20], [-100, 25], [-110, 25], [-117, 32], [-120, 35], [-124, 38], [-125, 48], [-130, 54], [-134, 58], [-140, 60], [-148, 60], [-152, 58], [-158, 56], [-160, 58], [-162, 63], [-165, 65], [-168, 68], [-168, 72]],
  // Greenland
  [[-44, 84], [-17, 77], [-18, 70], [-25, 68], [-35, 66], [-44, 66], [-52, 68], [-55, 72], [-50, 78], [-44, 84]],
  // South America
  [[-82, 8], [-75, 10], [-63, 10], [-60, 5], [-52, 4], [-50, 0], [-48, -2], [-42, -3], [-38, -8], [-35, -8], [-35, -15], [-39, -20], [-40, -22], [-42, -22], [-44, -24], [-48, -28], [-52, -32], [-53, -34], [-55, -35], [-58, -38], [-62, -38], [-65, -42], [-66, -46], [-67, -50], [-68, -54], [-70, -55], [-72, -50], [-74, -48], [-72, -42], [-70, -38], [-70, -34], [-72, -28], [-70, -18], [-76, -14], [-76, -8], [-78, -2], [-82, 2], [-82, 8]],
  // Europe (simplified)
  [[-10, 36], [0, 36], [8, 36], [12, 38], [16, 37], [18, 40], [20, 38], [26, 38], [28, 40], [30, 42], [30, 46], [24, 50], [20, 54], [18, 58], [16, 62], [12, 62], [8, 58], [5, 52], [0, 50], [-5, 48], [-10, 44], [-10, 36]],
  // Scandinavia + Finland
  [[5, 58], [8, 58], [12, 62], [18, 68], [20, 70], [25, 70], [28, 72], [30, 70], [28, 65], [30, 62], [26, 60], [22, 60], [20, 58], [18, 58], [12, 58], [10, 57], [5, 58]],
  // Africa
  [[-18, 16], [-16, 12], [-15, 8], [-15, 4], [-10, 4], [-5, 5], [0, 5], [5, 4], [10, 0], [12, -4], [14, -8], [16, -12], [18, -20], [20, -26], [22, -30], [24, -34], [26, -34], [30, -32], [32, -28], [36, -22], [40, -12], [42, -2], [42, 4], [40, 10], [42, 12], [44, 12], [44, 14], [38, 12], [36, 14], [34, 16], [36, 20], [36, 22], [34, 24], [32, 24], [30, 22], [24, 20], [18, 18], [12, 14], [8, 12], [4, 6], [0, 6], [-4, 6], [-8, 4], [-14, 10], [-18, 14], [-18, 16]],
  // Asia (very coarse)
  [[28, 42], [36, 42], [42, 42], [50, 42], [60, 44], [70, 44], [80, 44], [90, 44], [100, 44], [105, 52], [110, 52], [120, 48], [128, 44], [132, 42], [136, 54], [142, 56], [140, 62], [138, 68], [132, 70], [120, 72], [100, 76], [80, 76], [60, 72], [50, 70], [42, 68], [38, 64], [32, 66], [28, 62], [24, 58], [24, 54], [28, 50], [30, 46], [28, 42]],
  // Indian subcontinent
  [[62, 24], [68, 22], [72, 18], [76, 14], [78, 8], [80, 8], [82, 14], [84, 20], [80, 24], [76, 28], [70, 28], [64, 24], [62, 24]],
  // Southeast Asia peninsula
  [[98, 20], [100, 14], [100, 2], [103, 1], [106, 1], [108, 10], [104, 12], [98, 18], [98, 20]],
  // Australia
  [[114, -22], [118, -18], [122, -14], [130, -14], [136, -12], [142, -10], [148, -10], [152, -24], [154, -28], [152, -32], [148, -38], [144, -38], [140, -36], [136, -34], [134, -32], [130, -30], [116, -26], [114, -22]],
  // Japan (Honshu approx)
  [[130, 34], [134, 34], [138, 36], [140, 38], [142, 40], [142, 42], [140, 44], [136, 40], [132, 36], [130, 34]],
  // UK & Ireland (coarse)
  [[-6, 50], [-2, 50], [2, 52], [2, 56], [-2, 58], [-6, 58], [-8, 54], [-6, 50]],
];

/* ─────────────────────────────────────────────────────────────────────────
   Point-in-polygon (ray-casting)
──────────────────────────────────────────────────────────────────────────*/
function pip(px: number, py: number, poly: [number, number][]): boolean {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const xi = poly[i][0], yi = poly[i][1];
    const xj = poly[j][0], yj = poly[j][1];
    const intersect =
      yi > py !== yj > py &&
      px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

/* ─────────────────────────────────────────────────────────────────────────
   Project lat/lng → SVG x/y  (equirectangular)
──────────────────────────────────────────────────────────────────────────*/
const MAP_W = 960;
const MAP_H = 480;

function project(lat: number, lng: number): [number, number] {
  const x = ((lng + 180) / 360) * MAP_W;
  const y = ((90 - lat) / 180) * MAP_H;
  return [x, y];
}

/* ─────────────────────────────────────────────────────────────────────────
   Pre-compute dot positions once (outside component)
──────────────────────────────────────────────────────────────────────────*/
const STEP = 10; // dot spacing px
const DOTS: { x: number; y: number }[] = [];
for (let gy = STEP / 2; gy < MAP_H; gy += STEP) {
  for (let gx = STEP / 2; gx < MAP_W; gx += STEP) {
    const lng = (gx / MAP_W) * 360 - 180;
    const lat = 90 - (gy / MAP_H) * 180;
    for (const poly of LAND_POLYGONS) {
      if (pip(lng, lat, poly)) {
        DOTS.push({ x: gx, y: gy });
        break;
      }
    }
  }
}

/* ─────────────────────────────────────────────────────────────────────────
   Device type → icon
──────────────────────────────────────────────────────────────────────────*/
function DeviceIcon({ type, className }: { type: Device["type"]; className?: string }) {
  if (type === "server") return <Server className={className} />;
  if (type === "mobile") return <Smartphone className={className} />;
  if (type === "workstation") return <Monitor className={className} />;
  return <Wifi className={className} />;
}

interface DeviceMapProps {
  devices: Device[];
}

export function DeviceMap({ devices }: DeviceMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; device: Device } | null>(null);

  // Resolve pin positions
  const pins = devices.map((d) => {
    const [px, py] = project(d.location.lat, d.location.lng);
    return { device: d, px, py };
  });

  function handlePinEnter(
    e: React.MouseEvent<SVGGElement>,
    d: Device,
    px: number,
    py: number
  ) {
    setHovered(d.id);
    const rect = svgRef.current?.getBoundingClientRect();
    if (!rect) return;
    // convert SVG coords to container-relative
    const scaleX = rect.width / MAP_W;
    const scaleY = rect.height / MAP_H;
    setTooltip({ x: px * scaleX, y: py * scaleY, device: d });
  }

  function handlePinLeave() {
    setHovered(null);
    setTooltip(null);
  }

  return (
    <div className="rounded-xl border border-border/40 bg-card/40 backdrop-blur-md overflow-hidden shadow-sm relative h-full flex flex-col min-h-[400px]">
      {/* ── Header ── */}
      <div className="p-4 border-b border-border/40 flex items-center justify-between bg-muted/5 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-500/10">
            <Globe className="w-4 h-4 text-blue-500" />
          </div>
          <div>
            <h3 className="font-bold text-[11px] tracking-[0.2em] uppercase text-muted-foreground">
              Geographic Distribution
            </h3>
            <p className="text-[9px] font-mono text-muted-foreground/60 mt-0.5">
              IP-resolved device locations · live telemetry
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-widest text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            {devices.filter((d) => d.status === "online").length} Online
          </span>
          <span className="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-widest text-rose-400">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            {devices.filter((d) => d.status === "offline").length} Offline
          </span>
        </div>
      </div>

      {/* ── Map area ── */}
      <div className="flex-1 relative overflow-hidden bg-[#08090d]">
        {/* Subtle radial glow */}
        <div
          className="absolute inset-0 pointer-events-none z-0"
          style={{
            background:
              "radial-gradient(ellipse 70% 60% at 50% 50%, rgba(59,130,246,0.04) 0%, transparent 70%)",
          }}
        />

        <svg
          ref={svgRef}
          viewBox={`0 0 ${MAP_W} ${MAP_H}`}
          preserveAspectRatio="xMidYMid meet"
          className="w-full h-full z-10 relative"
          style={{ maxHeight: "320px" }}
        >
          {/* ── Land dots ── */}
          {DOTS.map((dot, i) => (
            <circle
              key={i}
              cx={dot.x}
              cy={dot.y}
              r={1.6}
              fill="rgba(99,130,190,0.22)"
            />
          ))}

          {/* ── Arc lines between online devices and first device (HQ) ── */}
          {pins
            .filter((p) => p.device.status === "online" && pins[0] && p.device.id !== pins[0].device.id)
            .map(({ device, px, py }) => {
              const hq = pins[0];
              const mx = (hq.px + px) / 2;
              const my = Math.min(hq.py, py) - 60;
              return (
                <path
                  key={`arc-${device.id}`}
                  d={`M ${hq.px} ${hq.py} Q ${mx} ${my} ${px} ${py}`}
                  stroke="rgba(99,130,246,0.18)"
                  strokeWidth={0.8}
                  fill="none"
                  strokeDasharray="3 4"
                />
              );
            })}

          {/* ── Device pins ── */}
          {pins.map(({ device, px, py }) => {
            const isOnline = device.status === "online";
            const isHovered = hovered === device.id;
            const color = isOnline ? "#10b981" : "#6b7280";
            const glowColor = isOnline ? "rgba(16,185,129,0.35)" : "rgba(107, 114, 128, 0.2)";

            return (
              <g
                key={device.id}
                transform={`translate(${px},${py})`}
                style={{ cursor: "pointer" }}
                onMouseEnter={(e) => handlePinEnter(e, device, px, py)}
                onMouseLeave={handlePinLeave}
              >
                {/* Outer pulse ring */}
                {isOnline && (
                  <>
                    <circle r={14} fill="none" stroke={color} strokeWidth={0.6} opacity={0.25}>
                      <animate attributeName="r" values="8;18" dur="2s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.4;0" dur="2s" repeatCount="indefinite" />
                    </circle>
                    <circle r={9} fill="none" stroke={color} strokeWidth={0.8} opacity={0.4}>
                      <animate attributeName="r" values="5;12" dur="2s" begin="0.5s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.5;0" dur="2s" begin="0.5s" repeatCount="indefinite" />
                    </circle>
                  </>
                )}

                {/* Glow disc */}
                <circle r={7} fill={glowColor} />

                {/* Core dot */}
                <circle
                  r={isHovered ? 5 : 4}
                  fill={color}
                  style={{ transition: "r 0.15s ease" }}
                />

                {/* Cross-hair lines */}
                <line x1={-8} y1={0} x2={-5} y2={0} stroke={color} strokeWidth={0.7} opacity={0.7} />
                <line x1={5} y1={0} x2={8} y2={0} stroke={color} strokeWidth={0.7} opacity={0.7} />
                <line x1={0} y1={-8} x2={0} y2={-5} stroke={color} strokeWidth={0.7} opacity={0.7} />
                <line x1={0} y1={5} x2={0} y2={8} stroke={color} strokeWidth={0.7} opacity={0.7} />

                {/* IP label (always visible) */}
                <text
                  y={-12}
                  textAnchor="middle"
                  fontSize={6}
                  fontFamily="monospace"
                  fill={color}
                  opacity={0.8}
                >
                  {device.ip}
                </text>
              </g>
            );
          })}
        </svg>

        {/* ── Tooltip ── */}
        <AnimatePresence>
          {tooltip && (
            <motion.div
              key={tooltip.device.id}
              initial={{ opacity: 0, scale: 0.92, y: 4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 4 }}
              transition={{ duration: 0.15 }}
              className="absolute z-30 pointer-events-none"
              style={{
                left: Math.min(tooltip.x + 16, 700),
                top: Math.max(tooltip.y - 70, 4),
              }}
            >
              <div className="bg-card/95 backdrop-blur-xl border border-border/60 rounded-xl px-3 py-2.5 shadow-2xl min-w-[180px]">
                {/* Header row */}
                <div className="flex items-center gap-2 mb-1.5">
                  <div
                    className={cn(
                      "p-1 rounded",
                      tooltip.device.status === "online"
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-muted/30 text-muted-foreground"
                    )}
                  >
                    <DeviceIcon type={tooltip.device.type} className="w-3 h-3" />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-foreground truncate max-w-[130px]">
                    {tooltip.device.name}
                  </span>
                </div>

                <div className="space-y-1">
                  <Row label="IP" value={tooltip.device.ip} mono />
                  <Row label="City" value={tooltip.device.location.city} />
                  <Row
                    label="Status"
                    value={tooltip.device.status.toUpperCase()}
                    valueClass={
                      tooltip.device.status === "online"
                        ? "text-emerald-400"
                        : "text-rose-400"
                    }
                  />
                  <Row label="Access" value={tooltip.device.accessLevel} />
                  <Row
                    label="Coords"
                    value={`${tooltip.device.location.lat.toFixed(2)}° / ${tooltip.device.location.lng.toFixed(2)}°`}
                    mono
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ── Footer ── */}
      <div className="p-3 bg-muted/5 backdrop-blur-md border-t border-border/40 z-10">
        <div className="flex items-center justify-between text-[9px] font-mono text-muted-foreground">
          <div className="flex items-center gap-6">
            {pins.map(({ device, px, py }) => (
              <span
                key={device.id}
                className={cn(
                  "flex items-center gap-1 uppercase font-bold tracking-widest transition-colors",
                  device.status === "online" ? "text-emerald-400" : "text-muted-foreground/40"
                )}
              >
                <span
                  className={cn(
                    "w-1.5 h-1.5 rounded-full",
                    device.status === "online" ? "bg-emerald-500" : "bg-muted-foreground/30"
                  )}
                />
                {device.ip}
              </span>
            ))}
          </div>
          <span className="opacity-50 uppercase tracking-widest">Fleet Tracking System v4.2</span>
        </div>
      </div>
    </div>
  );
}

/* ── Small helper component ─────────────────────────────────────────────── */
function Row({
  label,
  value,
  mono,
  valueClass,
}: {
  label: string;
  value: string;
  mono?: boolean;
  valueClass?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-[9px] uppercase tracking-widest text-muted-foreground/60 font-bold">
        {label}
      </span>
      <span
        className={cn(
          "text-[9px] font-semibold text-foreground",
          mono && "font-mono",
          valueClass
        )}
      >
        {value}
      </span>
    </div>
  );
}
