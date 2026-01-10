"""
Event Schema Definitions for GodsEye
Defines JSON structure for all event types
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Event type enumeration"""
    ACCESS = "access"
    HONEYPOT = "honeypot"
    NETWORK = "network"
    ENDPOINT = "endpoint"
    TEAPOT = "teapot"


class AccessMethod(str, Enum):
    """Access authentication methods"""
    RFID = "rfid"
    FINGERPRINT = "fingerprint"
    RFID_FINGERPRINT = "rfid_fingerprint"


class AccessStatus(str, Enum):
    """Access attempt status"""
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"
    ANOMALY = "anomaly"


# ============================================
# ACCESS EVENT SCHEMA
# ============================================
class AccessEvent(BaseModel):
    """
    Access control event schema
    Captures RFID and fingerprint authentication attempts
    """
    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(default=EventType.ACCESS)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Device Information
    device_id: str = Field(..., description="Access device identifier")
    location: str = Field(..., description="Physical location of device")
    
    # Access Attempt Details
    access_method: AccessMethod
    card_id: Optional[str] = Field(None, description="RFID card ID if used")
    fingerprint_id: Optional[str] = Field(None, description="Fingerprint template ID if used")
    user_id: Optional[str] = Field(None, description="Associated user ID if known")
    
    # Status
    status: AccessStatus
    failure_reason: Optional[str] = Field(None, description="Reason for failure if applicable")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "acc_20260110_001",
                "event_type": "access",
                "timestamp": "2026-01-10T14:30:00Z",
                "device_id": "access_door_01",
                "location": "Server Room A",
                "access_method": "rfid_fingerprint",
                "card_id": "CARD_12345",
                "fingerprint_id": "FP_USER_001",
                "user_id": "USER_001",
                "status": "success",
                "failure_reason": None,
                "metadata": {}
            }
        }


# ============================================
# HONEYPOT EVENT SCHEMA
# ============================================
class HoneypotInteractionType(str, Enum):
    """Types of honeypot interactions"""
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    COMMAND = "command"
    DATA_ACCESS = "data_access"


class HoneypotEvent(BaseModel):
    """
    Honeypot interaction event schema
    Captures all interactions with decoy systems
    """
    event_id: str
    event_type: EventType = Field(default=EventType.HONEYPOT)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Honeypot Information
    honeypot_id: str = Field(..., description="Honeypot device/service identifier")
    honeypot_type: str = Field(..., description="Type: fake_plc, fake_access, fake_iot")
    
    # Attacker Information
    source_ip: str
    source_port: Optional[int] = None
    
    # Interaction Details
    interaction_type: HoneypotInteractionType
    payload: Optional[str] = Field(None, description="Captured payload/command")
    protocol: Optional[str] = Field(None, description="Protocol used")
    
    # Analysis
    threat_level: str = Field(default="HIGH", description="Always HIGH for honeypots")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "hp_20260110_001",
                "event_type": "honeypot",
                "timestamp": "2026-01-10T15:45:00Z",
                "honeypot_id": "hp_plc_001",
                "honeypot_type": "fake_plc",
                "source_ip": "192.168.1.100",
                "source_port": 52341,
                "interaction_type": "command",
                "payload": "MODBUS_READ_COILS",
                "protocol": "modbus",
                "threat_level": "HIGH",
                "metadata": {}
            }
        }


# ============================================
# NETWORK EVENT SCHEMA
# ============================================
class NetworkEventType(str, Enum):
    """Network event types"""
    SUSPICIOUS_CONNECTION = "suspicious_connection"
    PORT_SCAN = "port_scan"
    TRAFFIC_SPIKE = "traffic_spike"
    UNKNOWN_DEVICE = "unknown_device"
    PROTOCOL_ANOMALY = "protocol_anomaly"


class NetworkEvent(BaseModel):
    """
    Network monitoring event schema
    Captures network traffic anomalies
    """
    event_id: str
    event_type: EventType = Field(default=EventType.NETWORK)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Network Details
    network_event_type: NetworkEventType
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str
    
    # Traffic Information
    packet_count: Optional[int] = None
    byte_count: Optional[int] = None
    
    # Detection
    anomaly_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "net_20260110_001",
                "event_type": "network",
                "timestamp": "2026-01-10T16:00:00Z",
                "network_event_type": "suspicious_connection",
                "source_ip": "10.0.0.50",
                "destination_ip": "10.0.0.100",
                "source_port": 44512,
                "destination_port": 502,
                "protocol": "modbus",
                "packet_count": 150,
                "byte_count": 45000,
                "anomaly_score": 0.85,
                "description": "Unusual Modbus traffic pattern detected",
                "metadata": {}
            }
        }


# ============================================
# ENDPOINT EVENT SCHEMA
# ============================================
class EndpointEventType(str, Enum):
    """Endpoint event types from Sysmon/Wazuh"""
    PROCESS_CREATION = "process_creation"
    NETWORK_CONNECTION = "network_connection"
    FILE_CREATION = "file_creation"
    REGISTRY_MODIFICATION = "registry_modification"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class EndpointEvent(BaseModel):
    """
    Endpoint monitoring event schema
    Captures Sysmon and Wazuh telemetry
    """
    event_id: str
    event_type: EventType = Field(default=EventType.ENDPOINT)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Endpoint Information
    hostname: str
    endpoint_id: str
    operating_system: str
    
    # Event Details
    endpoint_event_type: EndpointEventType
    process_name: Optional[str] = None
    process_id: Optional[int] = None
    parent_process: Optional[str] = None
    command_line: Optional[str] = None
    user: Optional[str] = None
    
    # Network (if applicable)
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None
    
    # File (if applicable)
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Detection
    severity: str = Field(default="INFO")
    description: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "ep_20260110_001",
                "event_type": "endpoint",
                "timestamp": "2026-01-10T17:30:00Z",
                "hostname": "ICS-WORKSTATION-01",
                "endpoint_id": "endpoint_001",
                "operating_system": "Windows 10",
                "endpoint_event_type": "process_creation",
                "process_name": "powershell.exe",
                "process_id": 4512,
                "parent_process": "cmd.exe",
                "command_line": "powershell.exe -enc <base64>",
                "user": "operator_01",
                "severity": "WARNING",
                "description": "Suspicious PowerShell execution detected",
                "metadata": {}
            }
        }


# ============================================
# TEAPOT EVENT SCHEMA
# ============================================
class TeapotEvent(BaseModel):
    """
    Teapot (decoy credential) event schema
    Any use of decoy credentials = confirmed malicious
    """
    event_id: str
    event_type: EventType = Field(default=EventType.TEAPOT)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Decoy Information
    decoy_type: str = Field(..., description="Type: fake_card, fake_fingerprint, fake_user")
    decoy_id: str = Field(..., description="Decoy credential identifier")
    
    # Usage Information
    device_id: Optional[str] = None
    source_ip: Optional[str] = None
    location: Optional[str] = None
    
    # Detection
    threat_level: str = Field(default="CRITICAL", description="Always CRITICAL")
    description: str = Field(default="Decoy credential used - confirmed malicious activity")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "tea_20260110_001",
                "event_type": "teapot",
                "timestamp": "2026-01-10T18:00:00Z",
                "decoy_type": "fake_card",
                "decoy_id": "FAKE_CARD_999",
                "device_id": "access_door_01",
                "source_ip": None,
                "location": "Server Room A",
                "threat_level": "CRITICAL",
                "description": "Decoy credential used - confirmed malicious activity",
                "metadata": {}
            }
        }


# ============================================
# UNIFIED EVENT CONTAINER
# ============================================
class UnifiedEvent(BaseModel):
    """
    Unified event container for all event types
    Used for routing and storage
    """
    event_data: AccessEvent | HoneypotEvent | NetworkEvent | EndpointEvent | TeapotEvent
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = Field(default=False)
