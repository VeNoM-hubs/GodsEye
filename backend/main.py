"""
Main Backend Application
Integrates all components and provides event processing pipeline
"""

import logging
from datetime import datetime

from backend.event_receiver import get_event_receiver
from backend.anomaly_detection import get_anomaly_detector
from backend.alert_engine import get_alert_engine
from backend.storage import get_storage
from backend.config import get_config
from backend.schemas import (
    AccessEvent, 
    HoneypotEvent, 
    NetworkEvent, 
    EndpointEvent, 
    TeapotEvent,
    EventType
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GodsEyeBackend:
    """
    Main backend application for GodsEye
    """
    
    def __init__(self):
        logger.info("="*80)
        logger.info("Starting GodsEye Backend System")
        logger.info("="*80)
        
        # Initialize components
        self.config = get_config()
        self.event_receiver = get_event_receiver()
        self.anomaly_detector = get_anomaly_detector()
        self.alert_engine = get_alert_engine()
        self.storage = get_storage()
        
        # Register event handlers
        self._register_handlers()
        
        logger.info("GodsEye Backend initialized successfully")
    
    def _register_handlers(self):
        """Register event handlers for each event type"""
        
        self.event_receiver.register_handler(
            EventType.ACCESS, 
            self._handle_access_event
        )
        
        self.event_receiver.register_handler(
            EventType.HONEYPOT, 
            self._handle_honeypot_event
        )
        
        self.event_receiver.register_handler(
            EventType.NETWORK, 
            self._handle_network_event
        )
        
        self.event_receiver.register_handler(
            EventType.ENDPOINT, 
            self._handle_endpoint_event
        )
        
        self.event_receiver.register_handler(
            EventType.TEAPOT, 
            self._handle_teapot_event
        )
        
        logger.info("Event handlers registered")
    
    def _handle_access_event(self, event: AccessEvent):
        """Handle access control events"""
        logger.info(f"Processing access event: {event.event_id}")
        
        # Save event to storage
        self.storage.save_event(event)
        
        # Check for anomalies
        anomalies = self.anomaly_detector.analyze_event(event)
        
        # Generate alerts for detected anomalies
        for anomaly in anomalies:
            alert = self.alert_engine.create_alert_from_anomaly(anomaly)
            self.storage.save_alert(alert)
    
    def _handle_honeypot_event(self, event: HoneypotEvent):
        """Handle honeypot interaction events"""
        logger.warning(f"Honeypot interaction detected: {event.event_id}")
        
        # Save event
        self.storage.save_event(event)
        
        # Create CRITICAL alert
        alert = self.alert_engine.create_honeypot_alert(event)
        self.storage.save_alert(alert)
    
    def _handle_network_event(self, event: NetworkEvent):
        """Handle network anomaly events"""
        logger.info(f"Processing network event: {event.event_id}")
        
        # Save event
        self.storage.save_event(event)
        
        # Create alert if anomaly score is high
        if event.anomaly_score and event.anomaly_score >= self.config.alerts.alert_threshold:
            alert = self.alert_engine.create_network_alert(event)
            self.storage.save_alert(alert)
    
    def _handle_endpoint_event(self, event: EndpointEvent):
        """Handle endpoint monitoring events"""
        logger.info(f"Processing endpoint event: {event.event_id}")
        
        # Save event
        self.storage.save_event(event)
        
        # Create alert for high severity events
        if event.severity in ["WARNING", "ERROR", "CRITICAL"]:
            alert = self.alert_engine.create_endpoint_alert(event)
            self.storage.save_alert(alert)
    
    def _handle_teapot_event(self, event: TeapotEvent):
        """Handle teapot (decoy credential) events"""
        logger.critical(f"TEAPOT TRIGGERED: {event.event_id}")
        
        # Save event
        self.storage.save_event(event)
        
        # Create CRITICAL alert
        alert = self.alert_engine.create_teapot_alert(event)
        self.storage.save_alert(alert)
    
    def process_event(self, event_data: dict):
        """
        Process incoming event
        
        Args:
            event_data: Raw event data dictionary
        """
        return self.event_receiver.process_event(event_data)
    
    def get_system_status(self) -> dict:
        """Get overall system status"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "receiver_stats": self.event_receiver.get_statistics(),
            "alert_stats": self.alert_engine.get_statistics(),
            "storage_stats": self.storage.get_storage_stats(),
            "anomaly_detector_stats": self.anomaly_detector.get_statistics()
        }
    
    def shutdown(self):
        """Shutdown backend gracefully"""
        logger.info("Shutting down GodsEye Backend")
        
        # Cleanup old data
        self.storage.cleanup_old_data()
        
        logger.info("GodsEye Backend shutdown complete")


# Global backend instance
_backend: GodsEyeBackend = None

def get_backend() -> GodsEyeBackend:
    """Get global backend instance"""
    global _backend
    if _backend is None:
        _backend = GodsEyeBackend()
    return _backend


if __name__ == "__main__":
    # Initialize backend
    backend = get_backend()
    
    # Display system status
    status = backend.get_system_status()
    print("\n" + "="*80)
    print("GodsEye Backend System Status")
    print("="*80)
    print(f"System ready at: {status['timestamp']}")
    print("="*80 + "\n")
