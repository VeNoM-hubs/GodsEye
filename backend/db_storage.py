"""
Database Storage for GodsEye
PostgreSQL database with automated threat detection
"""

import os
import json
import yaml
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, BigInteger, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

from backend.schemas import AccessEvent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()


# ================================
# Configuration Loader
# ================================

def load_db_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load database configuration from YAML file
    
    Args:
        config_path: Path to db_config.yaml file. If None, uses default location.
    
    Returns:
        Dictionary with database configuration
    """
    if config_path is None:
        # Default path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(current_dir), 'config', 'db_config.yaml')
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('database', {})
    except FileNotFoundError:
        logger.warning(f"Database config file not found: {config_path}. Using default values.")
        return {}
    except Exception as e:
        logger.error(f"Error loading database config: {e}. Using default values.")
        return {}


# ================================
# SQLAlchemy Models
# ================================

class User(Base):
    """Users table - stores user information"""
    __tablename__ = 'users'
    
    user_id = Column(String(50), primary_key=True)
    full_name = Column(String(120), nullable=False)
    role = Column(String(50), nullable=False)
    access_level = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'full_name': self.full_name,
            'role': self.role,
            'access_level': self.access_level,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Resource(Base):
    """Resources table - stores protected resources"""
    __tablename__ = 'resources'
    
    resource_id = Column(String(50), primary_key=True)
    resource_name = Column(String(120), nullable=False)
    resource_type = Column(String(30), nullable=False)
    required_access_level = Column(Integer, nullable=False)
    is_sensitive = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'resource_type': self.resource_type,
            'required_access_level': self.required_access_level,
            'is_sensitive': self.is_sensitive
        }


class PhysicalLog(Base):
    """Physical logs - RFID, biometric, card reader events"""
    __tablename__ = 'physical_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    resource_id = Column(String(50), ForeignKey('resources.resource_id', ondelete='RESTRICT'), nullable=False)
    access_status = Column(String(20), nullable=False)  # GRANTED, DENIED, FAILED
    event_time = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'access_status': self.access_status,
            'event_time': self.event_time.isoformat() if self.event_time else None
        }


class DigitalLog(Base):
    """Digital logs - Sysmon, Wazuh, endpoint events"""
    __tablename__ = 'digital_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    resource_id = Column(String(50), ForeignKey('resources.resource_id', ondelete='RESTRICT'), nullable=False)
    action_type = Column(String(50), nullable=False)  # FILE_ACCESS, PROCESS_CREATE, etc
    raw_severity = Column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    event_time = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'action_type': self.action_type,
            'raw_severity': self.raw_severity,
            'event_time': self.event_time.isoformat() if self.event_time else None
        }


class MainLog(Base):
    """Unified main logs - aggregates physical and digital"""
    __tablename__ = 'main_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source = Column(String(20), nullable=False)  # PHYSICAL or DIGITAL
    source_ref_id = Column(BigInteger, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    resource_id = Column(String(50), ForeignKey('resources.resource_id'), nullable=False)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    event_time = Column(DateTime, nullable=False)
    correlation_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'source_ref_id': self.source_ref_id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'event_time': self.event_time.isoformat() if self.event_time else None,
            'correlation_flag': self.correlation_flag,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MitreTechnique(Base):
    """MITRE ATT&CK techniques"""
    __tablename__ = 'mitre_techniques'
    
    technique_id = Column(String(20), primary_key=True)
    technique_name = Column(String(200), nullable=False)
    tactic = Column(String(100), nullable=False)
    
    def to_dict(self):
        return {
            'technique_id': self.technique_id,
            'technique_name': self.technique_name,
            'tactic': self.tactic
        }


class Threat(Base):
    """Detected threats with risk scoring"""
    __tablename__ = 'threats'
    
    threat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    threat_pattern = Column(String(120), nullable=False)
    mitre_id = Column(String(20), ForeignKey('mitre_techniques.technique_id'))
    risk_score = Column(Integer, nullable=False)
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    event_count = Column(Integer, default=1)
    status = Column(String(20), default='ACTIVE')  # ACTIVE, RESOLVED, IGNORED
    
    def to_dict(self):
        return {
            'threat_id': self.threat_id,
            'user_id': self.user_id,
            'threat_pattern': self.threat_pattern,
            'mitre_id': self.mitre_id,
            'risk_score': self.risk_score,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'event_count': self.event_count,
            'status': self.status
        }


# ================================
# Database Manager
# ================================

class GodsEyeDatabase:
    """
    GodsEye PostgreSQL database manager
    Handles all database operations with automated threat detection
    """
    
    def __init__(
        self, 
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize PostgreSQL database connection
        
        Args:
            db_host: PostgreSQL host (overrides config file)
            db_port: PostgreSQL port (overrides config file)
            db_name: Database name (overrides config file)
            db_user: Database user (overrides config file)
            db_password: Database password (overrides config file)
            config_path: Path to db_config.yaml file
        """
        # Load config from file
        config = load_db_config(config_path)
        
        # Use parameters if provided, otherwise use config file, otherwise use defaults
        db_host = db_host or config.get('host', 'localhost')
        db_port = db_port or config.get('port', 5432)
        db_name = db_name or config.get('name', 'godseye')
        db_user = db_user or config.get('username', 'godseye')
        db_password = db_password or config.get('password', 'godseye_secure_password')
        
        # PostgreSQL connection string
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}")
        
        # Create engine
        self.engine = create_engine(connection_string, echo=False, pool_pre_ping=True)
        
        # Note: Tables are created via setup_postgres.sql
        # We don't call Base.metadata.create_all() to avoid conflicts with triggers
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"GodsEye PostgreSQL Database initialized successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    # ================================
    # User Management
    # ================================
    
    def add_user(self, user_id: str, full_name: str, role: str, access_level: int) -> bool:
        """
        Add a new user
        
        Args:
            user_id: Unique user identifier
            full_name: User's full name
            role: User role (e.g., admin, employee, contractor)
            access_level: Access level (1-10, higher = more access)
        
        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            user = User(
                user_id=user_id,
                full_name=full_name,
                role=role,
                access_level=access_level,
                is_active=True
            )
            session.add(user)
            session.commit()
            logger.info(f"Added user: {user_id} ({full_name})")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding user {user_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        session = self.get_session()
        try:
            users = session.query(User).all()
            return [user.to_dict() for user in users]
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
        finally:
            session.close()
    
    # ================================
    # Resource Management
    # ================================
    
    def add_resource(self, resource_id: str, resource_name: str, resource_type: str, 
                    required_access_level: int, is_sensitive: bool = False) -> bool:
        """
        Add a new resource
        
        Args:
            resource_id: Unique resource identifier
            resource_name: Resource name
            resource_type: Type (e.g., door, file, database, server)
            required_access_level: Minimum access level required
            is_sensitive: Whether resource contains sensitive data
        
        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            resource = Resource(
                resource_id=resource_id,
                resource_name=resource_name,
                resource_type=resource_type,
                required_access_level=required_access_level,
                is_sensitive=is_sensitive
            )
            session.add(resource)
            session.commit()
            logger.info(f"Added resource: {resource_id} ({resource_name})")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding resource {resource_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_resource(self, resource_id: str) -> Optional[Dict]:
        """Get resource by ID"""
        session = self.get_session()
        try:
            resource = session.query(Resource).filter(Resource.resource_id == resource_id).first()
            return resource.to_dict() if resource else None
        except Exception as e:
            logger.error(f"Error getting resource {resource_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_all_resources(self) -> List[Dict]:
        """Get all resources"""
        session = self.get_session()
        try:
            resources = session.query(Resource).all()
            return [resource.to_dict() for resource in resources]
        except Exception as e:
            logger.error(f"Error getting resources: {e}")
            return []
        finally:
            session.close()
    
    # ================================
    # Physical Event Logging
    # ================================
    
    def log_physical_event(self, user_id: str, resource_id: str, access_status: str, 
                          event_time: Optional[datetime] = None) -> Optional[int]:
        """
        Log a physical access event (RFID, fingerprint, card reader)
        
        Triggers will automatically:
        - Insert into main_logs
        - Detect threats if HIGH severity
        
        Args:
            user_id: User attempting access
            resource_id: Resource being accessed
            access_status: GRANTED, DENIED, or FAILED
            event_time: Time of event (defaults to now)
        
        Returns:
            Event ID if successful, None otherwise
        """
        session = self.get_session()
        try:
            log = PhysicalLog(
                user_id=user_id,
                resource_id=resource_id,
                access_status=access_status,
                event_time=event_time or datetime.utcnow()
            )
            session.add(log)
            session.commit()
            
            event_id = log.id
            logger.info(f"Logged physical event: {event_id} - {user_id} -> {resource_id} [{access_status}]")
            return event_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging physical event: {e}")
            return None
        finally:
            session.close()
    
    def get_physical_logs(self, user_id: Optional[str] = None, resource_id: Optional[str] = None,
                         start_time: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """Get physical logs with filters"""
        session = self.get_session()
        try:
            query = session.query(PhysicalLog)
            
            if user_id:
                query = query.filter(PhysicalLog.user_id == user_id)
            if resource_id:
                query = query.filter(PhysicalLog.resource_id == resource_id)
            if start_time:
                query = query.filter(PhysicalLog.event_time >= start_time)
            
            query = query.order_by(PhysicalLog.event_time.desc()).limit(limit)
            
            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting physical logs: {e}")
            return []
        finally:
            session.close()
    
    # ================================
    # Digital Event Logging
    # ================================
    
    def log_digital_event(self, user_id: str, resource_id: str, action_type: str,
                         raw_severity: str, event_time: Optional[datetime] = None) -> Optional[int]:
        """
        Log a digital event (Sysmon, Wazuh, endpoint activity)
        
        Triggers will automatically:
        - Insert into main_logs
        - Detect threats if HIGH severity
        
        Args:
            user_id: User performing action
            resource_id: Resource being accessed
            action_type: Type of action (FILE_ACCESS, PROCESS_CREATE, etc)
            raw_severity: HIGH, MEDIUM, or LOW
            event_time: Time of event (defaults to now)
        
        Returns:
            Event ID if successful, None otherwise
        """
        session = self.get_session()
        try:
            log = DigitalLog(
                user_id=user_id,
                resource_id=resource_id,
                action_type=action_type,
                raw_severity=raw_severity,
                event_time=event_time or datetime.utcnow()
            )
            session.add(log)
            session.commit()
            
            event_id = log.id
            logger.info(f"Logged digital event: {event_id} - {user_id} -> {resource_id} [{action_type}] [{raw_severity}]")
            return event_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging digital event: {e}")
            return None
        finally:
            session.close()
    
    def get_digital_logs(self, user_id: Optional[str] = None, resource_id: Optional[str] = None,
                        start_time: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """Get digital logs with filters"""
        session = self.get_session()
        try:
            query = session.query(DigitalLog)
            
            if user_id:
                query = query.filter(DigitalLog.user_id == user_id)
            if resource_id:
                query = query.filter(DigitalLog.resource_id == resource_id)
            if start_time:
                query = query.filter(DigitalLog.event_time >= start_time)
            
            query = query.order_by(DigitalLog.event_time.desc()).limit(limit)
            
            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting digital logs: {e}")
            return []
        finally:
            session.close()
    
    # ================================
    # Main Logs (Unified View)
    # ================================
    
    def get_main_logs(self, user_id: Optional[str] = None, severity: Optional[str] = None,
                     start_time: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """
        Get unified main logs
        
        Args:
            user_id: Filter by user
            severity: Filter by severity (HIGH, MEDIUM, LOW)
            start_time: Filter by time
            limit: Maximum results
        
        Returns:
            List of main log entries
        """
        session = self.get_session()
        try:
            query = session.query(MainLog)
            
            if user_id:
                query = query.filter(MainLog.user_id == user_id)
            if severity:
                query = query.filter(MainLog.severity == severity)
            if start_time:
                query = query.filter(MainLog.event_time >= start_time)
            
            query = query.order_by(MainLog.event_time.desc()).limit(limit)
            
            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting main logs: {e}")
            return []
        finally:
            session.close()
    
    def get_high_severity_events(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get HIGH severity events from recent hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return self.get_main_logs(severity='HIGH', start_time=start_time, limit=limit)
    
    # ================================
    # Threat Management
    # ================================
    
    def get_threats(self, status: str = 'ACTIVE', limit: int = 100) -> List[Dict]:
        """
        Get detected threats
        
        Args:
            status: ACTIVE, RESOLVED, or IGNORED
            limit: Maximum results
        
        Returns:
            List of threats
        """
        session = self.get_session()
        try:
            query = session.query(Threat)
            
            if status:
                query = query.filter(Threat.status == status)
            
            query = query.order_by(Threat.risk_score.desc(), Threat.last_seen.desc()).limit(limit)
            
            threats = query.all()
            return [threat.to_dict() for threat in threats]
        except Exception as e:
            logger.error(f"Error getting threats: {e}")
            return []
        finally:
            session.close()
    
    def get_threat_by_user(self, user_id: str, status: str = 'ACTIVE') -> List[Dict]:
        """Get threats for specific user"""
        session = self.get_session()
        try:
            query = session.query(Threat).filter(Threat.user_id == user_id)
            
            if status:
                query = query.filter(Threat.status == status)
            
            query = query.order_by(Threat.last_seen.desc())
            
            threats = query.all()
            return [threat.to_dict() for threat in threats]
        except Exception as e:
            logger.error(f"Error getting threats for user {user_id}: {e}")
            return []
        finally:
            session.close()
    
    def update_threat_status(self, threat_id: int, status: str) -> bool:
        """
        Update threat status
        
        Args:
            threat_id: Threat ID
            status: ACTIVE, RESOLVED, or IGNORED
        
        Returns:
            True if successful
        """
        session = self.get_session()
        try:
            threat = session.query(Threat).filter(Threat.threat_id == threat_id).first()
            if threat:
                threat.status = status
                session.commit()
                logger.info(f"Updated threat {threat_id} status to {status}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating threat {threat_id}: {e}")
            return False
        finally:
            session.close()
    
    # ================================
    # MITRE ATT&CK Management
    # ================================
    
    def add_mitre_technique(self, technique_id: str, technique_name: str, tactic: str) -> bool:
        """Add MITRE ATT&CK technique"""
        session = self.get_session()
        try:
            technique = MitreTechnique(
                technique_id=technique_id,
                technique_name=technique_name,
                tactic=tactic
            )
            session.add(technique)
            session.commit()
            logger.info(f"Added MITRE technique: {technique_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding MITRE technique {technique_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_mitre_techniques(self) -> List[Dict]:
        """Get all MITRE techniques"""
        session = self.get_session()
        try:
            techniques = session.query(MitreTechnique).all()
            return [tech.to_dict() for tech in techniques]
        except Exception as e:
            logger.error(f"Error getting MITRE techniques: {e}")
            return []
        finally:
            session.close()
    
    # ================================
    # Statistics & Analytics
    # ================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        session = self.get_session()
        try:
            stats = {
                'users': {
                    'total': session.query(User).count(),
                    'active': session.query(User).filter(User.is_active == True).count()
                },
                'resources': {
                    'total': session.query(Resource).count(),
                    'sensitive': session.query(Resource).filter(Resource.is_sensitive == True).count()
                },
                'events': {
                    'physical_total': session.query(PhysicalLog).count(),
                    'digital_total': session.query(DigitalLog).count(),
                    'main_total': session.query(MainLog).count()
                },
                'threats': {
                    'active': session.query(Threat).filter(Threat.status == 'ACTIVE').count(),
                    'resolved': session.query(Threat).filter(Threat.status == 'RESOLVED').count(),
                    'total': session.query(Threat).count()
                }
            }
            
            # Recent activity (last 24 hours)
            last_24h = datetime.utcnow() - timedelta(hours=24)
            stats['recent_24h'] = {
                'physical_events': session.query(PhysicalLog).filter(
                    PhysicalLog.event_time >= last_24h
                ).count(),
                'digital_events': session.query(DigitalLog).filter(
                    DigitalLog.event_time >= last_24h
                ).count(),
                'high_severity': session.query(MainLog).filter(
                    MainLog.event_time >= last_24h,
                    MainLog.severity == 'HIGH'
                ).count()
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            session.close()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary for visualization"""
        session = self.get_session()
        try:
            # Top 5 users with most events
            top_users = session.execute(text("""
                SELECT user_id, COUNT(*) as event_count
                FROM main_logs
                WHERE event_time >= NOW() - INTERVAL '7 days'
                GROUP BY user_id
                ORDER BY event_count DESC
                LIMIT 5
            """)).fetchall()
            
            # Top 5 targeted resources
            top_resources = session.execute(text("""
                SELECT resource_id, COUNT(*) as access_count
                FROM main_logs
                WHERE event_time >= NOW() - INTERVAL '7 days'
                GROUP BY resource_id
                ORDER BY access_count DESC
                LIMIT 5
            """)).fetchall()
            
            # Severity distribution (last 24h)
            severity_dist = session.execute(text("""
                SELECT severity, COUNT(*) as count
                FROM main_logs
                WHERE event_time >= NOW() - INTERVAL '24 hours'
                GROUP BY severity
            """)).fetchall()
            
            # Active threats by risk score
            high_risk_threats = session.query(Threat).filter(
                Threat.status == 'ACTIVE',
                Threat.risk_score >= 70
            ).order_by(Threat.risk_score.desc()).limit(10).all()
            
            return {
                'top_users': [{'user_id': row[0], 'event_count': row[1]} for row in top_users],
                'top_resources': [{'resource_id': row[0], 'access_count': row[1]} for row in top_resources],
                'severity_distribution': {row[0]: row[1] for row in severity_dist},
                'high_risk_threats': [threat.to_dict() for threat in high_risk_threats]
            }
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {}
        finally:
            session.close()


# ================================
# Global Database Instance
# ================================

_db: Optional[GodsEyeDatabase] = None

def get_db(
    db_host: Optional[str] = None,
    db_port: Optional[int] = None,
    db_name: Optional[str] = None,
    db_user: Optional[str] = None,
    db_password: Optional[str] = None,
    config_path: Optional[str] = None
) -> GodsEyeDatabase:
    """
    Get global PostgreSQL database instance
    Reads credentials from config/db_config.yaml by default
    
    Args:
        db_host: PostgreSQL host (overrides config file)
        db_port: PostgreSQL port (overrides config file)
        db_name: Database name (overrides config file)
        db_user: Database username (overrides config file)
        db_password: Database password (overrides config file)
        config_path: Path to db_config.yaml file
    
    Returns:
        GodsEyeDatabase instance
    """
    global _db
    if _db is None:
        _db = GodsEyeDatabase(
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            config_path=config_path
        )
    return _db
