from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from backend.db_storage import GodsEyeDatabase


def create_events_router(db: GodsEyeDatabase) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["events"])

    @router.get("/events")
    def get_events(
        limit: int = Query(default=50, le=200),
        offset: int = Query(default=0, ge=0),
        severity: str = Query(default=None)
    ):
        session = db.get_session()
        try:
            # Get events with optional severity filter
            result = session.execute(
                text("""
                    SELECT id, source, source_ref_id, user_id, resource_id,
                           event_type, severity, event_time, correlation_flag
                    FROM main_logs
                    WHERE (:severity IS NULL OR severity = :severity)
                    ORDER BY event_time DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"severity": severity, "limit": limit, "offset": offset}
            )
            events = [dict(row._mapping) for row in result.fetchall()]

            # Convert datetimes to ISO 8601
            for event in events:
                if hasattr(event.get('event_time'), 'isoformat'):
                    event['event_time'] = event['event_time'].isoformat()

            # Get total count
            count_result = session.execute(
                text("""
                    SELECT COUNT(*) FROM main_logs
                    WHERE (:severity IS NULL OR severity = :severity)
                """),
                {"severity": severity}
            )
            total = count_result.scalar()

            return {"events": events, "total": total}
        finally:
            session.close()

    @router.get("/stats")
    def get_stats():
        session = db.get_session()
        try:
            # Query A: active threats count
            result = session.execute(text("SELECT COUNT(*) FROM threats WHERE status = 'ACTIVE'"))
            active_threats = result.scalar()

            # Query B: access violations (last 24h)
            result = session.execute(
                text("""
                    SELECT COUNT(*) FROM main_logs
                    WHERE event_type IN ('DENIED','FAILED','ANOMALY')
                    AND event_time >= NOW() - INTERVAL '24 hours'
                """)
            )
            access_violations = result.scalar()

            # Query C: events per minute
            result = session.execute(
                text("""
                    SELECT COUNT(*) FROM main_logs
                    WHERE event_time >= NOW() - INTERVAL '60 seconds'
                """)
            )
            events_per_minute = result.scalar()

            # Query D: severity distribution (last 24h)
            result = session.execute(
                text("""
                    SELECT severity, COUNT(*) as count FROM main_logs
                    WHERE event_time >= NOW() - INTERVAL '24 hours'
                    GROUP BY severity
                """)
            )
            severity_dist = {}
            for row in result.fetchall():
                severity_dist[row[0]] = row[1]

            # Query E: top users by event count (last 24h)
            result = session.execute(
                text("""
                    SELECT user_id, COUNT(*) as event_count FROM main_logs
                    WHERE event_time >= NOW() - INTERVAL '24 hours'
                    GROUP BY user_id ORDER BY event_count DESC LIMIT 5
                """)
            )
            top_users = [{"user_id": row[0], "event_count": row[1]} for row in result.fetchall()]

            # Query F: high risk threats
            result = session.execute(
                text("""
                    SELECT threat_id, user_id, threat_pattern, mitre_id,
                           risk_score, first_seen, last_seen, event_count, status
                    FROM threats WHERE status = 'ACTIVE'
                    ORDER BY risk_score DESC LIMIT 10
                """)
            )
            high_risk_threats = [dict(row._mapping) for row in result.fetchall()]

            # Convert datetimes in threats
            for threat in high_risk_threats:
                if hasattr(threat.get('first_seen'), 'isoformat'):
                    threat['first_seen'] = threat['first_seen'].isoformat()
                if hasattr(threat.get('last_seen'), 'isoformat'):
                    threat['last_seen'] = threat['last_seen'].isoformat()

            return {
                "active_threats": active_threats,
                "access_violations": access_violations,
                "events_per_minute": events_per_minute,
                "severity_distribution": severity_dist,
                "top_users": top_users,
                "high_risk_threats": high_risk_threats
            }
        finally:
            session.close()

    @router.get("/alerts")
    def get_alerts():
        session = db.get_session()
        try:
            result = session.execute(
                text("""
                    SELECT threat_id, user_id, threat_pattern, mitre_id,
                           risk_score, first_seen, last_seen, event_count, status
                    FROM threats
                    WHERE status IN ('ACTIVE', 'ACKNOWLEDGED')
                    ORDER BY risk_score DESC
                """)
            )
            alerts = [dict(row._mapping) for row in result.fetchall()]

            # Convert datetimes
            for alert in alerts:
                if hasattr(alert.get('first_seen'), 'isoformat'):
                    alert['first_seen'] = alert['first_seen'].isoformat()
                if hasattr(alert.get('last_seen'), 'isoformat'):
                    alert['last_seen'] = alert['last_seen'].isoformat()

            return {"alerts": alerts}
        finally:
            session.close()

    @router.patch("/alerts/{threat_id}/acknowledge")
    def acknowledge_alert(threat_id: int):
        session = db.get_session()
        try:
            result = session.execute(
                text("UPDATE threats SET status = 'ACKNOWLEDGED' WHERE threat_id = :id"),
                {"id": threat_id}
            )
            session.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Threat not found")

            return {"success": True, "threat_id": threat_id, "status": "ACKNOWLEDGED"}
        finally:
            session.close()

    @router.patch("/alerts/{threat_id}/resolve")
    def resolve_alert(threat_id: int):
        session = db.get_session()
        try:
            result = session.execute(
                text("UPDATE threats SET status = 'RESOLVED' WHERE threat_id = :id"),
                {"id": threat_id}
            )
            session.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Threat not found")

            return {"success": True, "threat_id": threat_id, "status": "RESOLVED"}
        finally:
            session.close()

    return router
