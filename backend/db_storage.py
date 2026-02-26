"""
Database Storage for Access Events
Simple SQLite database for logging access control events
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from backend.schemas import AccessEvent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()


class AccessEventLog(Base):
    """
    Access Event Log Table
    Stores all RFID/Fingerprint access attempts
    """
    __tablename__ = 'access_event_logs'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Event Identification
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Device Information
    device_id = Column(String(100), nullable=False, index=True)
    location = Column(String(200), nullable=False, index=True)
    
    # Access Method
    access_method = Column(String(20), nullable=False)  # rfid, fingerprint, rfid_fingerprint
    
    # Credentials
    card_id = Column(String(100), index=True)
    fingerprint_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    
    # Status
    status = Column(String(20), nullable=False, index=True)  # success, failed, denied, anomaly
    failure_reason = Column(Text)
    
    # Metadata (stored as JSON string)
    metadata = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AccessEventLog(event_id='{self.event_id}', device='{self.device_id}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'device_id': self.device_id,
            'location': self.location,
            'access_method': self.access_method,
            'card_id': self.card_id,
            'fingerprint_id': self.fingerprint_id,
            'user_id': self.user_id,
            'status': self.status,
            'failure_reason': self.failure_reason,
            'metadata': json.loads(self.metadata) if self.metadata else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AccessEventDatabase:
    """
    PostgreSQL database manager for access event logging
    """
    
    def __init__(
        self, 
        db_host: str = "localhost",
        db_port: int = 5432,
        db_name: str = "godseye",
        db_user: str = "godseye",
        db_password: str = "godseye_secure_password"
    ):
        """
        Initialize PostgreSQL database connection
        
        Args:
            db_host: PostgreSQL host
            db_port: PostgreSQL port
            db_name: Database name
            db_user: Database user
            db_password: Database password
        """
        # PostgreSQL connection string
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}")
        
        # Create engine
        self.engine = create_engine(connection_string, echo=False)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"PostgreSQL Access Event Database initialized successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def save_access_event(self, event: AccessEvent) -> bool:
        """
        Save an access event to the database
        
        Args:
            event: AccessEvent object to save
        
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            # Create database record
            db_event = AccessEventLog(
                event_id=event.event_id,
                timestamp=event.timestamp,
                device_id=event.device_id,
                location=event.location,
                access_method=event.access_method,
                card_id=event.card_id,
                fingerprint_id=event.fingerprint_id,
                user_id=event.user_id,
                status=event.status,
                failure_reason=event.failure_reason,
                metadata=json.dumps(event.metadata) if event.metadata else None
            )
            
            session.add(db_event)
            session.commit()
            
            logger.info(f"Saved access event to database: {event.event_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving access event {event.event_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_access_events(
        self,
        device_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query access events with filters
        
        Args:
            device_id: Filter by device ID
            user_id: Filter by user ID
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
        
        Returns:
            List of access events as dictionaries
        """
        session = self.get_session()
        try:
            query = session.query(AccessEventLog)
            
            # Apply filters
            if device_id:
                query = query.filter(AccessEventLog.device_id == device_id)
            if user_id:
                query = query.filter(AccessEventLog.user_id == user_id)
            if status:
                query = query.filter(AccessEventLog.status == status)
            if start_date:
                query = query.filter(AccessEventLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AccessEventLog.timestamp <= end_date)
            
            # Order by timestamp descending (newest first)
            query = query.order_by(AccessEventLog.timestamp.desc())
            
            # Limit results
            query = query.limit(limit)
            
            # Execute and convert to dictionaries
            events = query.all()
            return [event.to_dict() for event in events]
            
        except Exception as e:
            logger.error(f"Error querying access events: {e}")
            return []
        finally:
            session.close()
    
    def get_failed_attempts(
        self,
        device_id: Optional[str] = None,
        card_id: Optional[str] = None,
        minutes: int = 5,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent failed access attempts
        
        Args:
            device_id: Filter by device ID
            card_id: Filter by card ID
            minutes: Look back this many minutes
            limit: Maximum results
        
        Returns:
            List of failed access events
        """
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(minutes=minutes)
        
        session = self.get_session()
        try:
            query = session.query(AccessEventLog)
            query = query.filter(AccessEventLog.status == 'failed')
            query = query.filter(AccessEventLog.timestamp >= start_date)
            
            if device_id:
                query = query.filter(AccessEventLog.device_id == device_id)
            if card_id:
                query = query.filter(AccessEventLog.card_id == card_id)
            
            query = query.order_by(AccessEventLog.timestamp.desc())
            query = query.limit(limit)
            
            events = query.all()
            return [event.to_dict() for event in events]
            
        except Exception as e:
            logger.error(f"Error querying failed attempts: {e}")
            return []
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        session = self.get_session()
        try:
            total_events = session.query(AccessEventLog).count()
            
            success_count = session.query(AccessEventLog).filter(
                AccessEventLog.status == 'success'
            ).count()
            
            failed_count = session.query(AccessEventLog).filter(
                AccessEventLog.status == 'failed'
            ).count()
            
            denied_count = session.query(AccessEventLog).filter(
                AccessEventLog.status == 'denied'
            ).count()
            
            unique_devices = session.query(AccessEventLog.device_id).distinct().count()
            unique_users = session.query(AccessEventLog.user_id).filter(
                AccessEventLog.user_id.isnot(None)
            ).distinct().count()
            
            return {
                'total_events': total_events,
                'success_count': success_count,
                'failed_count': failed_count,
                'denied_count': denied_count,
                'unique_devices': unique_devices,
                'unique_users': unique_users,
                'success_rate': (success_count / total_events * 100) if total_events > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            session.close()
    
    def clear_old_logs(self, days: int = 90) -> int:
        """
        Delete logs older than specified days
        
        Args:
            days: Delete logs older than this many days
        
        Returns:
            Number of records deleted
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        session = self.get_session()
        try:
            deleted = session.query(AccessEventLog).filter(
                AccessEventLog.timestamp < cutoff_date
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {deleted} old access event logs")
            return deleted
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing old logs: {e}")
            return 0
        finally:
            session.close()


# Global database instance
_db: Optional[AccessEventDatabase] = None

def get_access_db(
    db_host: str = "localhost",
    db_port: int = 5432,
    db_name: str = "godseye",
    db_user: str = "godseye",
    db_password: str = "godseye_secure_password"
) -> AccessEventDatabase:
    """
    Get global PostgreSQL database instance
    
    Args:
        db_host: PostgreSQL host
        db_port: PostgreSQL port
        db_name: Database name
        db_user: Database username
        db_password: Database password
    
    Returns:
        AccessEventDatabase instance
    """
    global _db
    if _db is None:
        _db = AccessEventDatabase(
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password
        )
    return _db
