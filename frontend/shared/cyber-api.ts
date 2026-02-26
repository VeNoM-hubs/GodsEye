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

export type LogSeverity = "low" | "medium" | "high" | "critical";

export interface CyberLog {
  id: string;
  timestamp: string;
  deviceId: string;
  deviceName: string;
  event: string;
  severity: LogSeverity;
  details: string;
}

export interface DashboardStats {
  totalDevices: number;
  onlineDevices: number;
  criticalAlerts: number;
  threatLevel: number; // 0-100
}
