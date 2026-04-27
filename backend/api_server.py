"""
FastAPI Server for GodsEye Honeypot Webhook
Provides webhook endpoints for receiving honeypot events from ESP32
"""

import os
import sys
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.db_storage import GodsEyeDatabase, HoneypotCommandLog
from backend.honeypot_api import create_honeypot_router, HoneypotEventRequest
from backend.ws_broadcaster import get_ws_router
from backend.events_router import create_events_router
from backend.resources_router import create_resources_router
from backend.dashboard_api import create_dashboard_router
from backend.ws_manager import manager as honeypot_ws_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: nothing to do, WS broadcaster is per-connection
    yield
    # shutdown: nothing to do


def create_app():
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="GodsEye Honeypot API",
        description="Webhook API for receiving events from ESP32 honeypot",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    db = GodsEyeDatabase()
    logger.info("✅ Database connected")
    
    # Include honeypot router
    honeypot_router = create_honeypot_router(db)
    app.include_router(honeypot_router)

    # Include new routers
    app.include_router(create_events_router(db))
    app.include_router(create_resources_router(db))
    app.include_router(create_dashboard_router(db))
    app.include_router(get_ws_router(db))

    @app.websocket("/ws/honeypot")
    async def honeypot_ws_endpoint(websocket: WebSocket):
        await honeypot_ws_manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await honeypot_ws_manager.disconnect(websocket)

    @app.websocket("/ws/ingest")
    async def honeypot_ws_ingest(websocket: WebSocket):
        await websocket.accept()
        while True:
            try:
                payload = await websocket.receive_json()
                event = HoneypotEventRequest.model_validate(payload)

                # Store event (mirror POST /honeypot/log)
                command_log_id = None
                try:
                    # Reuse DB logic via the honeypot router helper
                    # Use a minimal local implementation to avoid circular imports
                    attacker_ip = event.attacker_ip
                    target_port = event.target_port
                    if not attacker_ip or target_port is None:
                        raise ValueError("Both attacker_ip (or ip) and target_port (or port) are required")

                    if event.timestamp:
                        try:
                            event_time = datetime.fromisoformat(event.timestamp)
                        except ValueError:
                            event_time = datetime.utcnow()
                    else:
                        event_time = datetime.utcnow()

                    normalized_command = (event.command_text or "").strip() if event.command_text else None
                    if normalized_command and normalized_command.lower() == "(no data)":
                        normalized_command = None

                    command_log = HoneypotCommandLog(
                        attacker_ip=attacker_ip,
                        target_port=target_port,
                        command_text=normalized_command,
                        event_time=event_time
                    )

                    session = db.get_session()
                    try:
                        session.add(command_log)
                        session.commit()
                        command_log_id = command_log.id
                    except Exception:
                        session.rollback()
                        raise
                    finally:
                        session.close()

                    await websocket.send_json({
                        "ok": True,
                        "id": command_log_id,
                        "timestamp": event_time.isoformat(),
                    })
                except Exception as exc:
                    await websocket.send_json({"ok": False, "error": str(exc)})
            except WebSocketDisconnect:
                break
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Check API health status"""
        return {
            "status": "healthy",
            "service": "GodsEye Honeypot Webhook API",
            "database": "connected"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """API root - shows available endpoints"""
        return {
            "service": "GodsEye Honeypot Webhook API",
            "version": "1.0.0",
            "endpoints": {
                "POST /honeypot/log": "Submit honeypot event",
                "GET /honeypot/logs": "Retrieve all honeypot logs",
                "GET /honeypot/logs/{honeypot_id}": "Get logs for specific honeypot",
                "GET /honeypot/stats": "Get honeypot statistics",
                "DELETE /honeypot/logs/{log_id}": "Delete specific log",
                "GET /health": "Health check",
                "GET /docs": "API documentation (Swagger UI)",
                "GET /redoc": "API documentation (ReDoc)"
            }
        }
    
    return app


# Module-level app for uvicorn: uvicorn backend.api_server:app
app = create_app()


if __name__ == "__main__":
    # Run server
    logger.info("🚀 Starting GodsEye Honeypot API Server")
    logger.info("📍 Listening on http://0.0.0.0:8000")
    logger.info("📖 Swagger UI: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
