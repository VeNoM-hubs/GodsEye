// ── GodsEye Type Definitions ─────────────────────────────────────────────
// Mirrors backend/schemas.py — 5 event types + alerts + MITRE mappings

/* ── Enums ─────────────────────────────────────────────────────────────── */

export type EventType = "access" | "honeypot" | "network" | "endpoint" | "teapot";
export type EventSource = "physical" | "digital";
export type AccessMethod = "rfid" | "fingerprint" | "rfid_fingerprint";
export type AccessStatus = "success" | "failed" | "denied" | "anomaly";

export type AlertSeverity = "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AlertType =
  | "access_anomaly"
  | "honeypot_interaction"
  | "network_anomaly"
  | "endpoint_threat"
  | "teapot_triggered"
  | "correlation";

export type EndpointEventType =
  | "process_creation"
  | "network_connection"
  | "file_creation"
  | "registry_modification"
  | "privilege_escalation";

export type NetworkEventType =
  | "suspicious_connection"
  | "port_scan"
  | "traffic_spike"
  | "unknown_device"
  | "protocol_anomaly";

export type HoneypotInteractionType =
  | "connection"
  | "authentication"
  | "command"
  | "data_access";

/* ── Event Schemas ─────────────────────────────────────────────────────── */

export interface AccessEvent {
  event_id: string;
  event_type: "access";
  timestamp: string;
  device_id: string;
  location: string;
  access_method: AccessMethod;
  card_id?: string;
  fingerprint_id?: string;
  user_id?: string;
  status: AccessStatus;
  failure_reason?: string;
}

export interface HoneypotEvent {
  event_id: string;
  event_type: "honeypot";
  timestamp: string;
  honeypot_id: string;
  honeypot_type: string;
  source_ip: string;
  source_port?: number;
  interaction_type: HoneypotInteractionType;
  payload?: string;
  protocol?: string;
  threat_level: string;
}

export interface NetworkEvent {
  event_id: string;
  event_type: "network";
  timestamp: string;
  network_event_type: NetworkEventType;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  packet_count?: number;
  byte_count?: number;
  anomaly_score?: number;
  description?: string;
}

export interface EndpointEvent {
  event_id: string;
  event_type: "endpoint";
  timestamp: string;
  hostname: string;
  endpoint_id: string;
  operating_system: string;
  endpoint_event_type: EndpointEventType;
  process_name?: string;
  process_id?: number;
  parent_process?: string;
  command_line?: string;
  user?: string;
  source_ip?: string;
  destination_ip?: string;
  destination_port?: number;
  file_path?: string;
  file_hash?: string;
  severity: AlertSeverity;
  description?: string;
}

export interface TeapotEvent {
  event_id: string;
  event_type: "teapot";
  timestamp: string;
  decoy_type: string;
  decoy_id: string;
  device_id?: string;
  source_ip?: string;
  location?: string;
  threat_level: string;
  description: string;
}

/* ── Unified Event (discriminated union) ──────────────────────────────── */

export type RawEvent =
  | AccessEvent
  | HoneypotEvent
  | NetworkEvent
  | EndpointEvent
  | TeapotEvent;

export interface GodsEyeEvent {
  /** Wrapper discriminator */
  source: EventSource;
  event: RawEvent;
}

/* ── Security Alerts ──────────────────────────────────────────────────── */

export interface SecurityAlert {
  alert_id: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  description: string;
  source_event_id: string;
  timestamp: string;
  mitre_technique_id?: string;
  mitre_technique_name?: string;
  risk_score: number; // 0-100
  user_id?: string;
  resource?: string;
  acknowledged: boolean;
  resolved: boolean;
}

/* ── Dashboard Aggregates ─────────────────────────────────────────────── */

export interface FlaggedUser {
  user_id: string;
  alert_count: number;
  highest_severity: AlertSeverity;
}

export interface MitreEntry {
  technique_id: string;
  technique_name: string;
  count: number;
}

export interface TargetedResource {
  resource: string;
  hit_count: number;
}

export interface DashboardStats {
  active_threats: number;
  access_violations: number;
  events_per_minute: number;
  top_flagged_users: FlaggedUser[];
  mitre_distribution: MitreEntry[];
  targeted_resources: TargetedResource[];
}

/* ── Helper: extract common fields from any event ─────────────────────── */

export function getEventUser(e: RawEvent): string {
  if (e.event_type === "access") return e.user_id ?? "unknown";
  if (e.event_type === "endpoint") return e.user ?? "SYSTEM";
  return "—";
}

export function getEventResource(e: RawEvent): string {
  if (e.event_type === "access") return e.location;
  if (e.event_type === "endpoint") return e.hostname;
  if (e.event_type === "network") return `${e.destination_ip}:${e.destination_port ?? "—"}`;
  if (e.event_type === "honeypot") return e.honeypot_id;
  if (e.event_type === "teapot") return e.location ?? e.device_id ?? "unknown";
  return "—";
}

export function getEventSeverity(e: RawEvent): AlertSeverity {
  if (e.event_type === "endpoint") return e.severity;
  if (e.event_type === "access") {
    if (e.status === "anomaly") return "HIGH";
    if (e.status === "denied") return "MEDIUM";
    if (e.status === "failed") return "LOW";
    return "INFO";
  }
  if (e.event_type === "honeypot") return "HIGH";
  if (e.event_type === "teapot") return "CRITICAL";
  if (e.event_type === "network") {
    if ((e.anomaly_score ?? 0) >= 0.8) return "HIGH";
    if ((e.anomaly_score ?? 0) >= 0.5) return "MEDIUM";
    return "LOW";
  }
  return "INFO";
}

export function getEventDescription(e: RawEvent): string {
  if (e.event_type === "access")
    return `${e.access_method.toUpperCase()} ${e.status} at ${e.location}${e.failure_reason ? ` — ${e.failure_reason}` : ""}`;
  if (e.event_type === "endpoint") return e.description ?? `${e.endpoint_event_type} on ${e.hostname}`;
  if (e.event_type === "network") return e.description ?? `${e.network_event_type} ${e.source_ip}→${e.destination_ip}`;
  if (e.event_type === "honeypot") return `${e.interaction_type} on ${e.honeypot_type} from ${e.source_ip}`;
  if (e.event_type === "teapot") return e.description;
  return "";
}

/* ── Legacy Device types (used by Infrastructure pages) ───────────────── */

export type DeviceStatus = "online" | "offline";
export type AccessLevel = "Admin" | "User" | "Restricted" | "Guest";
export type DeviceType = "server" | "workstation" | "mobile" | "iot";

export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  location: {
    city: string;
    lat: number;
    lng: number;
  };
  accessLevel: AccessLevel;
  lastSeen: string;
  ip: string;
}

// ── Real DB row types (from PostgreSQL) ───────────────────────────────

export interface MainLogRow {
  id: number;
  source: "PHYSICAL" | "DIGITAL";
  source_ref_id: number;
  user_id: string;
  resource_id: string;
  event_type: string;
  severity: AlertSeverity;
  event_time: string;          // ISO 8601
  correlation_flag: boolean;
}

export interface ThreatRow {
  threat_id: number;
  user_id: string;
  threat_pattern: string;
  mitre_id: string | null;
  risk_score: number;
  first_seen: string;          // ISO 8601
  last_seen: string;           // ISO 8601
  event_count: number;
  status: "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED";
}

export interface ResourceRow {
  resource_id: string;
  resource_name: string;
  resource_type: "door" | "server" | "database" | "file";
  required_access_level: number;
  is_sensitive: boolean;
  // from /api/resources/with-activity join (nullable when no recent events)
  last_severity?: AlertSeverity | null;
  last_event_time?: string | null;
  last_event_type?: string | null;
}

export interface WsMessage {
  type: "batch" | "heartbeat";
  events?: MainLogRow[];
  threats?: ThreatRow[];
  ts?: string;
}

export interface StatsResponse {
  active_threats: number;
  access_violations: number;
  events_per_minute: number;
  severity_distribution: Partial<Record<AlertSeverity, number>>;
  top_users: Array<{ user_id: string; event_count: number }>;
  high_risk_threats: ThreatRow[];
}

export type ConnectionStatus = "connecting" | "connected" | "disconnected";

// ── ESP32 Honeypot Feed types ─────────────────────────────────────────────

export interface HoneypotFeedEvent {
  id: number;
  honeypot_id: string | null;
  attacker_ip: string;
  target_port: number;
  threat_level: string | null;
  commands_executed: string[] | null;
  auth_success: boolean;
  timestamp: string; // ISO 8601
}

export interface HoneypotLogRow {
  id: number;
  attacker_ip: string;
  target_port: number;
  command_text: string | null;
  event_time: string | null;  // ISO 8601
  created_at: string | null;
}
