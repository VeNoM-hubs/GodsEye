/**
 * GodsEye API Types
 * TypeScript interfaces matching FastAPI response types
 * + Typed API client for frontend use
 */

// ================================
// Wire Types (what FastAPI returns)
// ================================

export interface WireEvent {
  event_id: string;
  source: "physical" | "digital";
  event_type: string;
  severity: string;
  user_id: string | null;
  resource_id: string | null;
  event_time: string; // ISO 8601
  created_at: string;
  description?: string;
}

export interface WireAlert {
  alert_id: string;
  threat_id: string;
  threat_pattern: string;
  risk_score: number;
  severity: "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  mitre_technique: string | null;
  first_seen: string;
  last_seen: string;
  event_count: number;
  status: "active" | "acknowledged" | "resolved";
}

export interface WireDashboardStats {
  active_threats: number;
  total_violations: number;
  events_per_minute: number;
  mitre_breakdown: { [technique: string]: number };
  timestamp: string;
}

// ================================
// API Client
// ================================

class GodsEyeApiClientImpl {
  private baseUrl: string;

  constructor(baseUrl: string = "/api") {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  async getStats(): Promise<WireDashboardStats> {
    return this.fetch<WireDashboardStats>("/dashboard/stats");
  }

  async getEvents(
    limit?: number,
    offset?: number,
    since?: number
  ): Promise<WireEvent[]> {
    const params = new URLSearchParams();
    if (limit !== undefined) params.append("limit", String(limit));
    if (offset !== undefined) params.append("offset", String(offset));
    if (since !== undefined) params.append("since", String(since));

    const queryString = params.toString();
    const path = `/dashboard/events${queryString ? `?${queryString}` : ""}`;
    return this.fetch<WireEvent[]>(path);
  }

  async getAlerts(): Promise<WireAlert[]> {
    return this.fetch<WireAlert[]>("/dashboard/alerts");
  }

  async getHoneypot(limit?: number, offset?: number): Promise<WireEvent[]> {
    const params = new URLSearchParams();
    if (limit !== undefined) params.append("limit", String(limit));
    if (offset !== undefined) params.append("offset", String(offset));

    const queryString = params.toString();
    const path = `/dashboard/honeypot${queryString ? `?${queryString}` : ""}`;
    return this.fetch<WireEvent[]>(path);
  }

  async acknowledgeAlert(alertId: string): Promise<WireAlert> {
    const [, threatId] = alertId.split("_");
    return this.fetch<WireAlert>(`/dashboard/alerts/${threatId}/acknowledge`, {
      method: "PATCH",
      body: JSON.stringify({}),
    });
  }

  async resolveAlert(alertId: string): Promise<WireAlert> {
    const [, threatId] = alertId.split("_");
    return this.fetch<WireAlert>(`/dashboard/alerts/${threatId}/resolve`, {
      method: "PATCH",
      body: JSON.stringify({}),
    });
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch("/api/godseye/health");
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Singleton instance
export const GodsEyeApiClient = new GodsEyeApiClientImpl();
