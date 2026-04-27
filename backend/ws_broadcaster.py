import asyncio
import json
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from backend.db_storage import GodsEyeDatabase

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for ws in list(self.active_connections):
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                self.disconnect(ws)


manager = ConnectionManager()


def get_ws_router(db: GodsEyeDatabase) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        last_event_id = 0
        last_threat_check = datetime.utcnow()

        try:
            while True:
                try:
                    # Update cursor before query to avoid missing events
                    last_threat_check = datetime.utcnow()

                    session = db.get_session()
                    try:
                        # Query 1: new main_logs rows
                        result = session.execute(
                            text("""
                                SELECT id, source, source_ref_id, user_id, resource_id,
                                       event_type, severity, event_time, correlation_flag
                                FROM main_logs
                                WHERE id > :last_id
                                ORDER BY id ASC
                                LIMIT 100
                            """),
                            {"last_id": last_event_id}
                        )
                        events = result.fetchall()
                        if events:
                            last_event_id = events[-1][0]

                        # Query 2: updated threats
                        result = session.execute(
                            text("""
                                SELECT threat_id, user_id, threat_pattern, mitre_id,
                                       risk_score, first_seen, last_seen, event_count, status
                                FROM threats
                                WHERE last_seen >= :since
                                ORDER BY last_seen ASC
                            """),
                            {"since": last_threat_check}
                        )
                        threats = result.fetchall()

                        # Serialize results
                        events_list = [dict(row._mapping) for row in events]
                        threats_list = [dict(row._mapping) for row in threats]

                        # Convert datetimes to ISO 8601
                        for event in events_list:
                            if hasattr(event.get('event_time'), 'isoformat'):
                                event['event_time'] = event['event_time'].isoformat()

                        for threat in threats_list:
                            if hasattr(threat.get('first_seen'), 'isoformat'):
                                threat['first_seen'] = threat['first_seen'].isoformat()
                            if hasattr(threat.get('last_seen'), 'isoformat'):
                                threat['last_seen'] = threat['last_seen'].isoformat()

                        # Build payload
                        if events_list or threats_list:
                            payload = {
                                "type": "batch",
                                "events": events_list,
                                "threats": threats_list
                            }
                        else:
                            payload = {
                                "type": "heartbeat",
                                "ts": datetime.utcnow().isoformat()
                            }

                        await manager.broadcast(json.dumps(payload))
                    finally:
                        session.close()

                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    manager.disconnect(websocket)
                    break

        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)

    return router
