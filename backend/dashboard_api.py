"""
GodsEye Dashboard API Router
Exposes REST endpoints for the React dashboard to fetch real data from PostgreSQL
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, and_

from backend.db_storage import GodsEyeDatabase, MainLog, Threat, HoneypotCommandLog, MitreTechnique

logger = logging.getLogger(__name__)


def risk_score_to_severity(risk_score: int) -> str:
    """Map risk score to severity level"""
    if risk_score <= 3:
        return "INFO"
    elif risk_score <= 6:
        return "LOW"
    elif risk_score <= 8:
        return "MEDIUM"
    elif risk_score <= 10:
        return "HIGH"
    else:
        return "CRITICAL"


def create_dashboard_router(db: GodsEyeDatabase) -> APIRouter:
    """Create FastAPI router with dashboard endpoints"""
    router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

    # ========================================
    # GET /api/dashboard/stats
    # ========================================
    @router.get("/stats")
    async def get_stats():
        """
        Get dashboard KPIs
        Returns: active_threats, total_violations, events_per_minute, mitre_breakdown
        """
        try:
            session = db.get_session()

            # Count active threats
            active_threats = session.query(func.count(Threat.threat_id)).filter(
                Threat.status == 'ACTIVE'
            ).scalar() or 0

            # Count total violations (all main_logs)
            total_violations = session.query(func.count(MainLog.id)).scalar() or 0

            # Events per minute (last 60 minutes)
            sixty_min_ago = datetime.utcnow() - timedelta(minutes=60)
            events_last_60_min = session.query(func.count(MainLog.id)).filter(
                MainLog.created_at >= sixty_min_ago
            ).scalar() or 0
            events_per_minute = round(events_last_60_min / 60, 2) if events_last_60_min > 0 else 0

            # MITRE breakdown: count threats by mitre_id
            mitre_counts = session.query(
                MitreTechnique.technique_name,
                func.count(Threat.threat_id)
            ).outerjoin(Threat).group_by(MitreTechnique.technique_name).all()

            mitre_breakdown = {name: count for name, count in mitre_counts if name}

            session.close()

            return {
                "active_threats": active_threats,
                "total_violations": total_violations,
                "events_per_minute": events_per_minute,
                "mitre_breakdown": mitre_breakdown,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================
    # GET /api/dashboard/events
    # ========================================
    @router.get("/events")
    async def get_events(
        limit: int = Query(50, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        since: Optional[int] = None
    ):
        """
        Get merged event stream from main_logs
        Query params:
            - limit: max results (default 50, max 1000)
            - offset: pagination offset
            - since: unix timestamp, only fetch events after this time
        """
        try:
            session = db.get_session()

            query = session.query(MainLog)

            if since is not None:
                since_dt = datetime.fromtimestamp(since)
                query = query.filter(MainLog.created_at > since_dt)

            query = query.order_by(MainLog.created_at.desc()).offset(offset).limit(limit)
            logs = query.all()

            events = []
            for log in logs:
                events.append({
                    "event_id": f"main_{log.id}",
                    "source": "physical" if log.source == "PHYSICAL" else "digital",
                    "event_type": log.event_type,
                    "severity": log.severity.lower() if log.severity else "medium",
                    "user_id": log.user_id,
                    "resource_id": log.resource_id,
                    "event_time": log.event_time.isoformat() if log.event_time else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "description": f"{log.event_type} on {log.resource_id}"
                })

            session.close()
            return events
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================
    # GET /api/dashboard/alerts
    # ========================================
    @router.get("/alerts")
    async def get_alerts():
        """
        Get all ACTIVE threats as alerts
        Maps risk_score to severity level
        """
        try:
            session = db.get_session()

            threats = session.query(Threat).filter(Threat.status == 'ACTIVE').all()

            alerts = []
            for threat in threats:
                mitre_tech = None
                if threat.mitre_id:
                    mitre = session.query(MitreTechnique).filter(
                        MitreTechnique.technique_id == threat.mitre_id
                    ).first()
                    mitre_tech = mitre.technique_name if mitre else None

                alerts.append({
                    "alert_id": f"threat_{threat.threat_id}",
                    "threat_id": str(threat.threat_id),
                    "threat_pattern": threat.threat_pattern,
                    "risk_score": threat.risk_score,
                    "severity": risk_score_to_severity(threat.risk_score),
                    "mitre_technique": mitre_tech,
                    "first_seen": threat.first_seen.isoformat() if threat.first_seen else None,
                    "last_seen": threat.last_seen.isoformat() if threat.last_seen else None,
                    "event_count": threat.event_count,
                    "status": threat.status.lower() if threat.status else "active"
                })

            session.close()
            return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================
    # GET /api/dashboard/honeypot
    # ========================================
    @router.get("/honeypot")
    async def get_honeypot_events(
        limit: int = Query(50, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """
        Get honeypot-only event stream from honeypot_command_logs
        Query params:
            - limit: max results (default 50, max 1000)
            - offset: pagination offset
        """
        try:
            session = db.get_session()

            logs = session.query(HoneypotCommandLog).order_by(
                HoneypotCommandLog.created_at.desc()
            ).offset(offset).limit(limit).all()

            events = []
            for log in logs:
                events.append({
                    "event_id": f"honeypot_{log.id}",
                    "source": "digital",
                    "event_type": "honeypot_access",
                    "severity": "high",
                    "user_id": None,
                    "resource_id": None,
                    "event_time": log.event_time.isoformat() if log.event_time else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "description": f"Honeypot activity from {log.attacker_ip}:{log.target_port}"
                })

            session.close()
            return events
        except Exception as e:
            logger.error(f"Error fetching honeypot events: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================
    # PATCH /api/dashboard/alerts/{alert_id}/acknowledge
    # ========================================
    @router.patch("/alerts/{alert_id}/acknowledge")
    async def acknowledge_alert(alert_id: str):
        """
        Mark an alert as acknowledged
        alert_id format: "threat_123"
        """
        try:
            threat_id = int(alert_id.split("_")[1]) if "_" in alert_id else int(alert_id)

            success = db.update_threat_status(threat_id, "ACKNOWLEDGED")
            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")

            # Return updated threat
            session = db.get_session()
            threat = session.query(Threat).filter(Threat.threat_id == threat_id).first()

            if not threat:
                session.close()
                raise HTTPException(status_code=404, detail="Alert not found")

            result = {
                "alert_id": f"threat_{threat.threat_id}",
                "threat_id": str(threat.threat_id),
                "threat_pattern": threat.threat_pattern,
                "risk_score": threat.risk_score,
                "severity": risk_score_to_severity(threat.risk_score),
                "mitre_technique": None,
                "first_seen": threat.first_seen.isoformat() if threat.first_seen else None,
                "last_seen": threat.last_seen.isoformat() if threat.last_seen else None,
                "event_count": threat.event_count,
                "status": threat.status.lower() if threat.status else "acknowledged"
            }
            session.close()
            return result
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid alert ID format")
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================
    # PATCH /api/dashboard/alerts/{alert_id}/resolve
    # ========================================
    @router.patch("/alerts/{alert_id}/resolve")
    async def resolve_alert(alert_id: str):
        """
        Mark an alert as resolved
        alert_id format: "threat_123"
        """
        try:
            threat_id = int(alert_id.split("_")[1]) if "_" in alert_id else int(alert_id)

            success = db.update_threat_status(threat_id, "RESOLVED")
            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")

            # Return updated threat
            session = db.get_session()
            threat = session.query(Threat).filter(Threat.threat_id == threat_id).first()

            if not threat:
                session.close()
                raise HTTPException(status_code=404, detail="Alert not found")

            result = {
                "alert_id": f"threat_{threat.threat_id}",
                "threat_id": str(threat.threat_id),
                "threat_pattern": threat.threat_pattern,
                "risk_score": threat.risk_score,
                "severity": risk_score_to_severity(threat.risk_score),
                "mitre_technique": None,
                "first_seen": threat.first_seen.isoformat() if threat.first_seen else None,
                "last_seen": threat.last_seen.isoformat() if threat.last_seen else None,
                "event_count": threat.event_count,
                "status": threat.status.lower() if threat.status else "resolved"
            }
            session.close()
            return result
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid alert ID format")
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
