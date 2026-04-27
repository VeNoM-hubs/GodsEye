"""
Honeypot Webhook API
Receives POST requests from ESP32 honeypot and stores them in the database
"""

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from backend.db_storage import GodsEyeDatabase, HoneypotCommandLog

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================================
# Pydantic Models for API
# ================================

class HoneypotEventRequest(BaseModel):
    """Schema for simple honeypot payload: IP + Port + Command"""
    attacker_ip: Optional[str] = Field(None, description="Attacker's IP address", alias="ip")
    target_port: Optional[int] = Field(None, description="Honeypot target port (23 for telnet, 21 for FTP, etc)", alias="port")
    command_text: Optional[str] = Field(None, description="Single command text from simple payload", alias="command")
    timestamp: Optional[str] = Field(None, description="Event timestamp (ISO-8601)")
    # Extended ESP32 fields — accepted for broadcast, not persisted to DB
    honeypot_id: Optional[str] = Field(None, description="ESP32 honeypot identifier")
    threat_level: Optional[str] = Field(None, description="Threat classification: LOW/MEDIUM/HIGH/CRITICAL")
    commands_executed: Optional[List[str]] = Field(None, description="List of commands executed by attacker")
    auth_success: Optional[bool] = Field(None, description="Whether authentication succeeded")

    model_config = {
        "populate_by_name": True
    }


class HoneypotEventResponse(BaseModel):
    """Schema for API response"""
    success: bool
    message: str
    honeypot_command_log_id: Optional[int] = None
    error: Optional[str] = None


# ================================
# Honeypot API Router
# ================================

def create_honeypot_router(db: GodsEyeDatabase):
    """
    Create FastAPI router with honeypot webhook endpoints
    
    Args:
        db: GodsEyeDatabase instance for storing logs
    
    Returns:
        APIRouter with honeypot endpoints
    """
    from fastapi import APIRouter
    from backend.ws_manager import manager

    router = APIRouter(prefix="/honeypot", tags=["honeypot"])

    def store_honeypot_event(event: HoneypotEventRequest) -> tuple[int, datetime, str, int, Optional[str]]:
        attacker_ip = event.attacker_ip
        target_port = event.target_port

        if not attacker_ip or target_port is None:
            raise ValueError("Both attacker_ip (or ip) and target_port (or port) are required")

        # Parse timestamp
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

        return command_log_id, event_time, attacker_ip, target_port, normalized_command
    
    @router.post("/log", response_model=HoneypotEventResponse)
    async def log_honeypot_event(event: HoneypotEventRequest):
        """
        Receive and store simple honeypot event from ESP32.

        Supported payload examples:
        {"ip":"192.168.0.1","port":445,"command":"(no data)"}
        {"attacker_ip":"192.168.0.1","target_port":445,"command_text":"ls"}
        """
        try:
            command_log_id, event_time, attacker_ip, target_port, normalized_command = store_honeypot_event(event)

            # Broadcast to all connected WebSocket clients
            await manager.broadcast({
                "event": "honeypot_hit",
                "id": command_log_id,
                "honeypot_id": event.honeypot_id,
                "attacker_ip": attacker_ip,
                "target_port": target_port,
                "threat_level": event.threat_level,
                "commands_executed": event.commands_executed,
                "auth_success": event.auth_success,
                "timestamp": event_time.isoformat(),
            })
            
            logger.info(
                f"✅ Honeypot command logged [ID: {command_log_id}] - "
                f"IP: {attacker_ip} | Port: {target_port} | Command: {normalized_command or '(no data)'}"
            )
            
            return HoneypotEventResponse(
                success=True,
                message="Honeypot command stored successfully",
                honeypot_command_log_id=command_log_id,
                error=None
            )
        
        except ValueError as e:
            return HoneypotEventResponse(
                success=False,
                message="Failed to store honeypot event",
                error=str(e)
            )
        except Exception as e:
            error_msg = f"Failed to store honeypot event: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return HoneypotEventResponse(
                success=False,
                message="Failed to store honeypot event",
                error=error_msg
            )
    
    
    @router.get("/logs")
    async def get_honeypot_logs(
        limit: int = 100,
        offset: int = 0,
        attacker_ip: Optional[str] = None,
        target_port: Optional[int] = None
    ):
        """
        Retrieve simple honeypot command logs from database.
        
        Query parameters:
        - limit: Maximum number of logs to return (default: 100)
        - offset: Number of logs to skip (default: 0)
        - attacker_ip: Optional filter by attacker IP
        - target_port: Optional filter by target port
        """
        try:
            session = db.get_session()
            query = session.query(HoneypotCommandLog)

            if attacker_ip:
                query = query.filter(HoneypotCommandLog.attacker_ip == attacker_ip)
            if target_port is not None:
                query = query.filter(HoneypotCommandLog.target_port == target_port)
            
            total = query.count()
            logs = query.order_by(HoneypotCommandLog.event_time.desc())\
                        .limit(limit)\
                        .offset(offset)\
                        .all()
            
            session.close()
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "count": len(logs),
                "logs": [log.to_dict() for log in logs]
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve honeypot logs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve logs: {str(e)}"
            )
    
    
    @router.get("/logs/ip/{attacker_ip}")
    async def get_logs_by_attacker_ip(attacker_ip: str):
        """Get all command logs for a specific attacker IP."""
        try:
            session = db.get_session()
            logs = session.query(HoneypotCommandLog)\
                          .filter(HoneypotCommandLog.attacker_ip == attacker_ip)\
                          .order_by(HoneypotCommandLog.event_time.desc())\
                          .all()
            session.close()
            
            return {
                "attacker_ip": attacker_ip,
                "total": len(logs),
                "logs": [log.to_dict() for log in logs]
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve logs for IP {attacker_ip}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    
    @router.get("/stats")
    async def get_honeypot_stats():
        """Get simple honeypot command activity statistics."""
        try:
            session = db.get_session()
            
            total_events = session.query(HoneypotCommandLog).count()
            
            unique_attackers = session.query(HoneypotCommandLog.attacker_ip)\
                                      .distinct()\
                                      .count()
            
            ports_hit = session.query(HoneypotCommandLog.target_port)\
                               .distinct()\
                               .count()

            empty_command_count = session.query(HoneypotCommandLog)\
                                         .filter(HoneypotCommandLog.command_text.is_(None))\
                                         .count()
            
            session.close()
            
            return {
                "total_events": total_events,
                "unique_attackers": unique_attackers,
                "ports_exploited": ports_hit,
                "empty_command_count": empty_command_count
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve honeypot stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    
    @router.delete("/logs/{log_id}")
    async def delete_honeypot_log(log_id: int):
        """Delete a specific honeypot command log."""
        try:
            session = db.get_session()
            log = session.query(HoneypotCommandLog).filter(HoneypotCommandLog.id == log_id).first()
            
            if not log:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Log {log_id} not found"
                )
            
            session.delete(log)
            session.commit()
            session.close()
            
            logger.info(f"✅ Deleted honeypot log {log_id}")
            
            return {"success": True, "message": f"Log {log_id} deleted"}
        
        except Exception as e:
            logger.error(f"❌ Failed to delete log: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    return router
