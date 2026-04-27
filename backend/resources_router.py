from fastapi import APIRouter
from sqlalchemy import text

from backend.db_storage import GodsEyeDatabase


def create_resources_router(db: GodsEyeDatabase) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["resources"])

    @router.get("/resources")
    def get_resources():
        session = db.get_session()
        try:
            result = session.execute(
                text("""
                    SELECT resource_id, resource_name, resource_type,
                           required_access_level, is_sensitive
                    FROM resources
                    ORDER BY resource_type, resource_name
                """)
            )
            resources = [dict(row._mapping) for row in result.fetchall()]
            return {"resources": resources}
        finally:
            session.close()

    @router.get("/resources/with-activity")
    def get_resources_with_activity():
        session = db.get_session()
        try:
            result = session.execute(
                text("""
                    SELECT r.resource_id, r.resource_name, r.resource_type,
                           r.required_access_level, r.is_sensitive,
                           ml.severity      AS last_severity,
                           ml.event_time    AS last_event_time,
                           ml.event_type    AS last_event_type
                    FROM resources r
                    LEFT JOIN LATERAL (
                        SELECT severity, event_time, event_type
                        FROM main_logs
                        WHERE resource_id = r.resource_id
                        AND event_time >= NOW() - INTERVAL '5 minutes'
                        ORDER BY event_time DESC
                        LIMIT 1
                    ) ml ON true
                    ORDER BY r.resource_type, r.resource_name
                """)
            )
            resources = []
            for row in result.fetchall():
                resource = dict(row._mapping)
                # Convert datetime to ISO 8601
                if hasattr(resource.get('last_event_time'), 'isoformat'):
                    resource['last_event_time'] = resource['last_event_time'].isoformat()
                resources.append(resource)

            return {"resources": resources}
        finally:
            session.close()

    return router
