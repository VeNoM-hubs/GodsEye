"""
Alert Engine
Generates, manages, and dispatches security alerts
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import uuid4

from backend.schemas import AccessEvent, HoneypotEvent, NetworkEvent, EndpointEvent, TeapotEvent
from backend.anomaly_detection import AccessAnomaly
from backend.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    """Types of alerts"""
    ACCESS_ANOMALY = "access_anomaly"
    HONEYPOT_INTERACTION = "honeypot_interaction"
    NETWORK_ANOMALY = "network_anomaly"
    ENDPOINT_THREAT = "endpoint_threat"
    TEAPOT_TRIGGERED = "teapot_triggered"
    CORRELATION = "correlation"


class Alert:
    """
    Security alert object
    """
    
    def __init__(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        source_event_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.alert_id = self._generate_alert_id()
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.description = description
        self.source_event_id = source_event_id
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}
        self.acknowledged = False
        self.resolved = False
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid4())[:8]
        return f"alert_{timestamp}_{unique_id}"
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "source_event_id": self.source_event_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved
        }
    
    def acknowledge(self):
        """Mark alert as acknowledged"""
        self.acknowledged = True
        logger.info(f"Alert {self.alert_id} acknowledged")
    
    def resolve(self):
        """Mark alert as resolved"""
        self.resolved = True
        logger.info(f"Alert {self.alert_id} resolved")


class AlertEngine:
    """
    Alert generation and management engine
    """
    
    def __init__(self):
        self.config = get_config().alerts
        self.alerts: List[Alert] = []
        self.alert_stats = {
            "total_generated": 0,
            "by_severity": {sev: 0 for sev in AlertSeverity},
            "by_type": {atype: 0 for atype in AlertType}
        }
        logger.info("Alert Engine initialized")
    
    def create_alert_from_anomaly(
        self, 
        anomaly: AccessAnomaly
    ) -> Alert:
        """
        Create alert from detected access anomaly
        
        Args:
            anomaly: Detected access anomaly
        
        Returns:
            Generated alert
        """
        # Map anomaly severity to alert severity
        severity = AlertSeverity(anomaly.severity)
        
        alert = Alert(
            alert_type=AlertType.ACCESS_ANOMALY,
            severity=severity,
            title=f"Access Anomaly: {anomaly.anomaly_type}",
            description=anomaly.description,
            source_event_id=anomaly.event.event_id,
            metadata={
                "anomaly_type": anomaly.anomaly_type,
                "confidence": anomaly.confidence,
                "device_id": anomaly.event.device_id,
                "location": anomaly.event.location,
                "card_id": anomaly.event.card_id,
                "fingerprint_id": anomaly.event.fingerprint_id,
                "user_id": anomaly.event.user_id
            }
        )
        
        self._process_alert(alert)
        return alert
    
    def create_honeypot_alert(
        self, 
        honeypot_event: HoneypotEvent
    ) -> Alert:
        """
        Create CRITICAL alert from honeypot interaction
        
        Args:
            honeypot_event: Honeypot interaction event
        
        Returns:
            Generated alert
        """
        alert = Alert(
            alert_type=AlertType.HONEYPOT_INTERACTION,
            severity=AlertSeverity.CRITICAL,
            title=f"Honeypot Interaction Detected: {honeypot_event.honeypot_type}",
            description=f"Attacker interaction with {honeypot_event.honeypot_type} "
                       f"from {honeypot_event.source_ip}",
            source_event_id=honeypot_event.event_id,
            metadata={
                "honeypot_id": honeypot_event.honeypot_id,
                "honeypot_type": honeypot_event.honeypot_type,
                "source_ip": honeypot_event.source_ip,
                "source_port": honeypot_event.source_port,
                "interaction_type": honeypot_event.interaction_type,
                "payload": honeypot_event.payload,
                "protocol": honeypot_event.protocol
            }
        )
        
        self._process_alert(alert)
        return alert
    
    def create_teapot_alert(
        self, 
        teapot_event: TeapotEvent
    ) -> Alert:
        """
        Create CRITICAL alert from teapot (decoy credential) usage
        
        Args:
            teapot_event: Teapot event
        
        Returns:
            Generated alert
        """
        alert = Alert(
            alert_type=AlertType.TEAPOT_TRIGGERED,
            severity=AlertSeverity.CRITICAL,
            title=f"DECOY CREDENTIAL USED: {teapot_event.decoy_type}",
            description=teapot_event.description,
            source_event_id=teapot_event.event_id,
            metadata={
                "decoy_type": teapot_event.decoy_type,
                "decoy_id": teapot_event.decoy_id,
                "device_id": teapot_event.device_id,
                "source_ip": teapot_event.source_ip,
                "location": teapot_event.location
            }
        )
        
        self._process_alert(alert)
        return alert
    
    def create_network_alert(
        self, 
        network_event: NetworkEvent
    ) -> Alert:
        """
        Create alert from network anomaly
        
        Args:
            network_event: Network event
        
        Returns:
            Generated alert
        """
        # Determine severity based on anomaly score
        if network_event.anomaly_score and network_event.anomaly_score >= 0.8:
            severity = AlertSeverity.HIGH
        elif network_event.anomaly_score and network_event.anomaly_score >= 0.6:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        alert = Alert(
            alert_type=AlertType.NETWORK_ANOMALY,
            severity=severity,
            title=f"Network Anomaly: {network_event.network_event_type}",
            description=network_event.description or "Network anomaly detected",
            source_event_id=network_event.event_id,
            metadata={
                "network_event_type": network_event.network_event_type,
                "source_ip": network_event.source_ip,
                "destination_ip": network_event.destination_ip,
                "source_port": network_event.source_port,
                "destination_port": network_event.destination_port,
                "protocol": network_event.protocol,
                "anomaly_score": network_event.anomaly_score
            }
        )
        
        self._process_alert(alert)
        return alert
    
    def create_endpoint_alert(
        self, 
        endpoint_event: EndpointEvent
    ) -> Alert:
        """
        Create alert from endpoint event
        
        Args:
            endpoint_event: Endpoint event
        
        Returns:
            Generated alert
        """
        # Map endpoint severity to alert severity
        severity_map = {
            "INFO": AlertSeverity.INFO,
            "WARNING": AlertSeverity.MEDIUM,
            "ERROR": AlertSeverity.HIGH,
            "CRITICAL": AlertSeverity.CRITICAL
        }
        severity = severity_map.get(endpoint_event.severity, AlertSeverity.MEDIUM)
        
        alert = Alert(
            alert_type=AlertType.ENDPOINT_THREAT,
            severity=severity,
            title=f"Endpoint Threat: {endpoint_event.endpoint_event_type}",
            description=endpoint_event.description or "Endpoint anomaly detected",
            source_event_id=endpoint_event.event_id,
            metadata={
                "hostname": endpoint_event.hostname,
                "endpoint_id": endpoint_event.endpoint_id,
                "endpoint_event_type": endpoint_event.endpoint_event_type,
                "process_name": endpoint_event.process_name,
                "process_id": endpoint_event.process_id,
                "user": endpoint_event.user,
                "command_line": endpoint_event.command_line
            }
        )
        
        self._process_alert(alert)
        return alert
    
    def _process_alert(self, alert: Alert):
        """
        Process and dispatch alert
        
        Args:
            alert: Alert to process
        """
        # Store alert
        self.alerts.append(alert)
        
        # Update statistics
        self.alert_stats["total_generated"] += 1
        self.alert_stats["by_severity"][alert.severity] += 1
        self.alert_stats["by_type"][alert.alert_type] += 1
        
        # Dispatch based on severity
        if self._should_dispatch(alert):
            self._dispatch_alert(alert)
    
    def _should_dispatch(self, alert: Alert) -> bool:
        """
        Determine if alert should be dispatched
        
        Args:
            alert: Alert to check
        
        Returns:
            True if should dispatch
        """
        # Check if notifications enabled
        if not self.config.enable_notifications:
            return False
        
        # Get severity level threshold
        severity_levels = self.config.severity_levels
        alert_level = severity_levels.get(alert.severity.value, 0)
        
        # Always dispatch CRITICAL and HIGH
        return alert_level >= severity_levels.get("MEDIUM", 3)
    
    def _dispatch_alert(self, alert: Alert):
        """
        Dispatch alert through configured channels
        
        Args:
            alert: Alert to dispatch
        """
        channels = self.config.notification_channels
        
        for channel in channels:
            if channel == "console":
                self._dispatch_console(alert)
            elif channel == "log":
                self._dispatch_log(alert)
            # Future: email, sms, webhook, etc.
    
    def _dispatch_console(self, alert: Alert):
        """Print alert to console"""
        print("\n" + "="*80)
        print(f"🚨 SECURITY ALERT [{alert.severity}]")
        print("="*80)
        print(f"Alert ID: {alert.alert_id}")
        print(f"Type: {alert.alert_type}")
        print(f"Time: {alert.timestamp}")
        print(f"Title: {alert.title}")
        print(f"Description: {alert.description}")
        print(f"Source Event: {alert.source_event_id}")
        if alert.metadata:
            print(f"Metadata: {json.dumps(alert.metadata, indent=2)}")
        print("="*80 + "\n")
    
    def _dispatch_log(self, alert: Alert):
        """Log alert to file"""
        logger.warning(
            f"ALERT [{alert.severity}] {alert.title} - {alert.description} "
            f"(ID: {alert.alert_id})"
        )
    
    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        unacknowledged_only: bool = False,
        unresolved_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Alert]:
        """
        Query alerts with filters
        
        Args:
            severity: Filter by severity
            alert_type: Filter by type
            unacknowledged_only: Only unacknowledged alerts
            unresolved_only: Only unresolved alerts
            limit: Maximum number of alerts to return
        
        Returns:
            List of filtered alerts
        """
        filtered = self.alerts
        
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]
        
        if unacknowledged_only:
            filtered = [a for a in filtered if not a.acknowledged]
        
        if unresolved_only:
            filtered = [a for a in filtered if not a.resolved]
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_statistics(self) -> dict:
        """Get alert statistics"""
        return {
            **self.alert_stats,
            "total_active": len(self.alerts),
            "unacknowledged": len([a for a in self.alerts if not a.acknowledged]),
            "unresolved": len([a for a in self.alerts if not a.resolved])
        }


# Global alert engine instance
_alert_engine: Optional[AlertEngine] = None

def get_alert_engine() -> AlertEngine:
    """Get global alert engine instance"""
    global _alert_engine
    if _alert_engine is None:
        _alert_engine = AlertEngine()
    return _alert_engine
