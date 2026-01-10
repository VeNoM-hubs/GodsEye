
"""
Rule-Based Access Anomaly Detection
Detects suspicious access patterns using predefined rules
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Optional

from backend.schemas import AccessEvent, AccessStatus, AccessMethod
from backend.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccessAnomaly:
    """Represents a detected access anomaly"""
    
    def __init__(
        self,
        event: AccessEvent,
        anomaly_type: str,
        severity: str,
        description: str,
        confidence: float = 1.0
    ):
        self.event = event
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.description = description
        self.confidence = confidence
        self.detected_at = datetime.utcnow()


class AccessAnomalyDetector:
    """
    Rule-based access anomaly detection engine
    """
    
    def __init__(self):
        self.config = get_config().access_control
        self.teapot_config = get_config().teapot
        
        # Track failed attempts per device/user
        self.failed_attempts = defaultdict(list)
        
        # Track access patterns
        self.access_history = defaultdict(list)
        
        logger.info("Access Anomaly Detector initialized")
    
    def analyze_event(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Analyze access event for anomalies
        
        Args:
            event: Access event to analyze
        
        Returns:
            List of detected anomalies (empty if none)
        """
        anomalies = []
        
        # Check all rule-based detection methods
        anomalies.extend(self._check_failed_attempts(event))
        anomalies.extend(self._check_abnormal_access_time(event))
        anomalies.extend(self._check_card_fingerprint_mismatch(event))
        anomalies.extend(self._check_unknown_location(event))
        anomalies.extend(self._check_missing_multi_factor(event))
        anomalies.extend(self._check_teapot_credentials(event))
        
        # Log detected anomalies
        if anomalies:
            logger.warning(
                f"Detected {len(anomalies)} anomalie(s) for event {event.event_id}"
            )
            for anomaly in anomalies:
                logger.warning(f"  - {anomaly.anomaly_type}: {anomaly.description}")
        
        return anomalies
    
    def _check_failed_attempts(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Check for repeated failed access attempts
        
        Rule: More than X failed attempts in Y seconds = anomaly
        """
        anomalies = []
        
        if event.status != AccessStatus.FAILED:
            return anomalies
        
        # Track this failed attempt
        key = f"{event.device_id}_{event.card_id or event.fingerprint_id}"
        self.failed_attempts[key].append(event.timestamp)
        
        # Clean old attempts outside the time window
        cutoff_time = datetime.utcnow() - timedelta(
            seconds=self.config.failed_attempt_window_seconds
        )
        self.failed_attempts[key] = [
            ts for ts in self.failed_attempts[key] if ts > cutoff_time
        ]
        
        # Check if threshold exceeded
        if len(self.failed_attempts[key]) >= self.config.max_failed_attempts:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="REPEATED_FAILED_ATTEMPTS",
                severity="HIGH",
                description=f"Multiple failed access attempts detected: "
                           f"{len(self.failed_attempts[key])} attempts in "
                           f"{self.config.failed_attempt_window_seconds}s",
                confidence=1.0
            ))
        
        return anomalies
    
    def _check_abnormal_access_time(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Check for access attempts outside normal hours
        
        Rule: Access outside configured hours = anomaly
        """
        anomalies = []
        
        hour = event.timestamp.hour
        
        # Check if outside normal hours
        start_hour = self.config.normal_access_hours_start
        end_hour = self.config.normal_access_hours_end
        
        is_abnormal = False
        if start_hour < end_hour:
            # Normal case: e.g., 6 AM to 10 PM
            is_abnormal = hour < start_hour or hour >= end_hour
        else:
            # Crosses midnight: e.g., 10 PM to 6 AM
            is_abnormal = hour >= end_hour and hour < start_hour
        
        if is_abnormal:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="ABNORMAL_ACCESS_TIME",
                severity="MEDIUM",
                description=f"Access attempt at abnormal hour: {hour:02d}:00 "
                           f"(normal hours: {start_hour:02d}:00-{end_hour:02d}:00)",
                confidence=0.8
            ))
        
        return anomalies
    
    def _check_card_fingerprint_mismatch(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Check for mismatched card and fingerprint
        
        Rule: Card ID and fingerprint ID don't match expected pairing
        """
        anomalies = []
        
        # Only check if both methods used
        if event.access_method != AccessMethod.RFID_FINGERPRINT:
            return anomalies
        
        if not event.card_id or not event.fingerprint_id:
            return anomalies
        
        # Check historical pairings
        # In real system, this would check against user database
        # For now, detect if user_id is None when both credentials provided
        if event.user_id is None and event.status == AccessStatus.SUCCESS:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="CARD_FINGERPRINT_MISMATCH",
                severity="HIGH",
                description=f"Card {event.card_id} and fingerprint {event.fingerprint_id} "
                           f"do not match any known user",
                confidence=0.9
            ))
        
        return anomalies
    
    def _check_unknown_location(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Check for access at unknown/unauthorized locations
        
        Rule: Location not in known locations list
        """
        anomalies = []
        
        if event.location not in self.config.known_locations:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="UNKNOWN_LOCATION",
                severity="MEDIUM",
                description=f"Access attempt at unknown location: {event.location}",
                confidence=0.7
            ))
        
        return anomalies
    
    def _check_missing_multi_factor(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Check for missing multi-factor authentication
        
        Rule: System requires both RFID and fingerprint
        """
        anomalies = []
        
        if not self.config.require_multi_factor:
            return anomalies
        
        if event.access_method != AccessMethod.RFID_FINGERPRINT:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="MISSING_MULTI_FACTOR",
                severity="MEDIUM",
                description=f"Multi-factor authentication required but only "
                           f"{event.access_method} was used",
                confidence=1.0
            ))
        
        return anomalies
    
    def _check_teapot_credentials(self, event: AccessEvent) -> List[AccessAnomaly]:
        """
        Check if decoy (teapot) credentials were used
        
        Rule: ANY use of decoy credentials = CRITICAL threat
        """
        anomalies = []
        
        if not self.teapot_config.enabled:
            return anomalies
        
        # Check if card is decoy
        if event.card_id in self.teapot_config.decoy_cards:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="TEAPOT_CARD_USED",
                severity="CRITICAL",
                description=f"DECOY CARD USED: {event.card_id} - Confirmed malicious activity",
                confidence=1.0
            ))
        
        # Check if fingerprint is decoy
        if event.fingerprint_id in self.teapot_config.decoy_fingerprints:
            anomalies.append(AccessAnomaly(
                event=event,
                anomaly_type="TEAPOT_FINGERPRINT_USED",
                severity="CRITICAL",
                description=f"DECOY FINGERPRINT USED: {event.fingerprint_id} - "
                           f"Confirmed malicious activity",
                confidence=1.0
            ))
        
        return anomalies
    
    def get_statistics(self) -> dict:
        """Get detector statistics"""
        return {
            "tracked_devices": len(self.failed_attempts),
            "total_failed_attempts": sum(len(v) for v in self.failed_attempts.values()),
            "access_history_entries": sum(len(v) for v in self.access_history.values())
        }
    
    def cleanup_old_data(self, days: int = 7):
        """Clean up tracking data older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Clean failed attempts
        for key in list(self.failed_attempts.keys()):
            self.failed_attempts[key] = [
                ts for ts in self.failed_attempts[key] if ts > cutoff
            ]
            if not self.failed_attempts[key]:
                del self.failed_attempts[key]
        
        logger.info(f"Cleaned up tracking data older than {days} days")


# Global detector instance
_anomaly_detector: Optional[AccessAnomalyDetector] = None

def get_anomaly_detector() -> AccessAnomalyDetector:
    """Get global anomaly detector instance"""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AccessAnomalyDetector()
    return _anomaly_detector
