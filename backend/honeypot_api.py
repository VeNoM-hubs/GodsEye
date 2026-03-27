"""
Honeypot Webhook API
Receives POST requests from ESP32 honeypot and stores them in the database
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from backend.db_storage import GodsEyeDatabase, HoneypotLog

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================================
# Pydantic Models for API
# ================================

class HoneypotEventRequest(BaseModel):
    """Schema for honeypot event POST requests from ESP32"""
    honeypot_id: str = Field(..., description="Unique honeypot identifier (e.g., ESP32-MAC)")
    honeypot_name: str = Field(..., description="Honeypot service name (e.g., 'Telnet Server')")
    honeypot_type: str = Field(..., description="Honeypot type (e.g., 'multi-service', 'telnet')")
    attacker_ip: str = Field(..., description="Attacker's IP address")
    attacker_port: int = Field(..., description="Attacker's source port")
    target_port: int = Field(..., description="Honeypot target port (23 for telnet, 21 for FTP, etc)")
    username_attempted: Optional[str] = Field(None, description="Username used in login attempt")
    password_attempted: Optional[str] = Field(None, description="Password used in login attempt")
    commands_executed: Optional[List[str]] = Field(None, description="List of commands executed")
    auth_success: bool = Field(False, description="Whether authentication was successful")
    session_duration_ms: int = Field(0, description="Session duration in milliseconds")
    threat_level: str = Field("MEDIUM", description="Threat level (LOW, MEDIUM, HIGH, CRITICAL)")
    timestamp: Optional[str] = Field(None, description="Event timestamp (ISO-8601)")


class HoneypotEventResponse(BaseModel):
    """Schema for API response"""
    success: bool
    message: str
    honeypot_log_id: Optional[int] = None
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
    
    router = APIRouter(prefix="/honeypot", tags=["honeypot"])
    
    @router.post("/log", response_model=HoneypotEventResponse)
    async def log_honeypot_event(event: HoneypotEventRequest):
        """
        Receive and store honeypot event from ESP32
        
        This endpoint accepts POST requests from the ESP32 honeypot
        and stores them in the honeypot_logs table.
        
        Example POST request:
        ```json
        {
            "honeypot_id": "ESP32-AABBCCDD",
            "honeypot_name": "Telnet Server",
            "honeypot_type": "multi-service",
            "attacker_ip": "192.168.1.5",
            "attacker_port": 54321,
            "target_port": 23,
            "username_attempted": "admin",
            "password_attempted": "password123",
            "commands_executed": ["ls", "whoami", "cat /etc/passwd"],
            "auth_success": false,
            "session_duration_ms": 5000,
            "threat_level": "HIGH"
        }
        ```
        """
        try:
            # Parse timestamp
            event_time = None
            if event.timestamp:
                try:
                    event_time = datetime.fromisoformat(event.timestamp)
                except ValueError:
                    event_time = datetime.utcnow()
            else:
                event_time = datetime.utcnow()
            
            # Create HoneypotLog record
            honeypot_log = HoneypotLog(
                honeypot_id=event.honeypot_id,
                honeypot_name=event.honeypot_name,
                honeypot_type=event.honeypot_type,
                attacker_ip=event.attacker_ip,
                attacker_port=event.attacker_port,
                target_port=event.target_port,
                username_attempted=event.username_attempted,
                password_attempted=event.password_attempted,
                commands_executed=event.commands_executed or [],
                auth_success=event.auth_success,
                session_duration_ms=event.session_duration_ms,
                threat_level=event.threat_level,
                event_time=event_time
            )
            
            # Insert into database
            session = db.get_session()
            session.add(honeypot_log)
            session.commit()
            log_id = honeypot_log.id
            session.close()
            
            logger.info(
                f"✅ Honeypot event logged [ID: {log_id}] - "
                f"Attacker: {event.attacker_ip}:{event.attacker_port} → "
                f"Port: {event.target_port} | Threat: {event.threat_level}"
            )
            
            return HoneypotEventResponse(
                success=True,
                message=f"Honeypot event stored successfully",
                honeypot_log_id=log_id,
                error=None
            )
        
        except Exception as e:
            error_msg = f"Failed to store honeypot event: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return HoneypotEventResponse(
                success=False,
                message="Failed to store honeypot event",
                honeypot_log_id=None,
                error=error_msg
            )
    
    
    @router.get("/logs")
    async def get_honeypot_logs(
        limit: int = 100,
        offset: int = 0,
        threat_level: Optional[str] = None
    ):
        """
        Retrieve honeypot logs from database
        
        Query parameters:
        - limit: Maximum number of logs to return (default: 100)
        - offset: Number of logs to skip (default: 0)
        - threat_level: Filter by threat level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        try:
            session = db.get_session()
            query = session.query(HoneypotLog)
            
            if threat_level:
                query = query.filter(HoneypotLog.threat_level == threat_level)
            
            total = query.count()
            logs = query.order_by(HoneypotLog.event_time.desc())\
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
    
    
    @router.get("/logs/{honeypot_id}")
    async def get_logs_by_honeypot(honeypot_id: str):
        """Get all logs for a specific honeypot"""
        try:
            session = db.get_session()
            logs = session.query(HoneypotLog)\
                          .filter(HoneypotLog.honeypot_id == honeypot_id)\
                          .order_by(HoneypotLog.event_time.desc())\
                          .all()
            session.close()
            
            return {
                "honeypot_id": honeypot_id,
                "total": len(logs),
                "logs": [log.to_dict() for log in logs]
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve logs for {honeypot_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    
    @router.get("/stats")
    async def get_honeypot_stats():
        """Get honeypot activity statistics"""
        try:
            session = db.get_session()
            
            total_events = session.query(HoneypotLog).count()
            high_threat_count = session.query(HoneypotLog)\
                                       .filter(HoneypotLog.threat_level.in_(['HIGH', 'CRITICAL']))\
                                       .count()
            
            unique_attackers = session.query(HoneypotLog.attacker_ip)\
                                      .distinct()\
                                      .count()
            
            ports_hit = session.query(HoneypotLog.target_port)\
                               .distinct()\
                               .count()
            
            session.close()
            
            return {
                "total_events": total_events,
                "high_threat_count": high_threat_count,
                "unique_attackers": unique_attackers,
                "ports_exploited": ports_hit
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve honeypot stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    
    @router.delete("/logs/{log_id}")
    async def delete_honeypot_log(log_id: int):
        """Delete a specific honeypot log"""
        try:
            session = db.get_session()
            log = session.query(HoneypotLog).filter(HoneypotLog.id == log_id).first()
            
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
