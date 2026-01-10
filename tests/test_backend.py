"""
Test Suite for GodsEye Backend
Tests all components with simulated data
"""

import pytest
from datetime import datetime, timedelta
from faker import Faker

from backend.main import get_backend
from backend.schemas import (
    AccessEvent,
    HoneypotEvent,
    NetworkEvent,
    EndpointEvent,
    TeapotEvent,
    AccessMethod,
    AccessStatus,
    EventType,
    HoneypotInteractionType,
    NetworkEventType,
    EndpointEventType
)

fake = Faker()


class TestDataGenerator:
    """Generate fake test data for all event types"""
    
    @staticmethod
    def generate_access_event(
        status: AccessStatus = AccessStatus.SUCCESS,
        use_decoy: bool = False,
        abnormal_hour: bool = False
    ) -> dict:
        """Generate fake access event"""
        
        timestamp = datetime.utcnow()
        if abnormal_hour:
            # Set to 3 AM (outside normal hours)
            timestamp = timestamp.replace(hour=3, minute=0, second=0)
        
        card_id = "FAKE_CARD_001" if use_decoy else f"CARD_{fake.random_int(10000, 99999)}"
        
        return {
            "event_id": f"acc_test_{fake.uuid4()[:8]}",
            "event_type": "access",
            "timestamp": timestamp.isoformat(),
            "device_id": fake.random_element(["access_door_01", "access_door_02", "access_door_03"]),
            "location": fake.random_element(["Server Room A", "Control Room", "Main Entrance"]),
            "access_method": "rfid_fingerprint",
            "card_id": card_id,
            "fingerprint_id": f"FP_USER_{fake.random_int(1, 100)}",
            "user_id": f"USER_{fake.random_int(1, 100)}" if status == AccessStatus.SUCCESS else None,
            "status": status,
            "failure_reason": "Invalid credentials" if status == AccessStatus.FAILED else None,
            "metadata": {}
        }
    
    @staticmethod
    def generate_honeypot_event() -> dict:
        """Generate fake honeypot interaction event"""
        
        return {
            "event_id": f"hp_test_{fake.uuid4()[:8]}",
            "event_type": "honeypot",
            "timestamp": datetime.utcnow().isoformat(),
            "honeypot_id": f"hp_plc_{fake.random_int(1, 5)}",
            "honeypot_type": fake.random_element(["fake_plc", "fake_access", "fake_iot"]),
            "source_ip": fake.ipv4(),
            "source_port": fake.random_int(40000, 60000),
            "interaction_type": "command",
            "payload": "MODBUS_READ_COILS",
            "protocol": "modbus",
            "threat_level": "HIGH",
            "metadata": {}
        }
    
    @staticmethod
    def generate_network_event(anomaly_score: float = 0.8) -> dict:
        """Generate fake network event"""
        
        return {
            "event_id": f"net_test_{fake.uuid4()[:8]}",
            "event_type": "network",
            "timestamp": datetime.utcnow().isoformat(),
            "network_event_type": "suspicious_connection",
            "source_ip": fake.ipv4_private(),
            "destination_ip": fake.ipv4_private(),
            "source_port": fake.random_int(40000, 60000),
            "destination_port": 502,
            "protocol": "modbus",
            "packet_count": fake.random_int(100, 1000),
            "byte_count": fake.random_int(10000, 100000),
            "anomaly_score": anomaly_score,
            "description": "Unusual traffic pattern detected",
            "metadata": {}
        }
    
    @staticmethod
    def generate_endpoint_event(severity: str = "WARNING") -> dict:
        """Generate fake endpoint event"""
        
        return {
            "event_id": f"ep_test_{fake.uuid4()[:8]}",
            "event_type": "endpoint",
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": f"ICS-WORKSTATION-{fake.random_int(1, 10)}",
            "endpoint_id": f"endpoint_{fake.random_int(1, 100)}",
            "operating_system": "Windows 10",
            "endpoint_event_type": "process_creation",
            "process_name": fake.random_element(["powershell.exe", "cmd.exe", "python.exe"]),
            "process_id": fake.random_int(1000, 9999),
            "parent_process": "explorer.exe",
            "command_line": fake.file_path(),
            "user": f"operator_{fake.random_int(1, 20)}",
            "severity": severity,
            "description": "Suspicious process execution detected",
            "metadata": {}
        }
    
    @staticmethod
    def generate_teapot_event() -> dict:
        """Generate fake teapot event"""
        
        return {
            "event_id": f"tea_test_{fake.uuid4()[:8]}",
            "event_type": "teapot",
            "timestamp": datetime.utcnow().isoformat(),
            "decoy_type": "fake_card",
            "decoy_id": "FAKE_CARD_001",
            "device_id": "access_door_01",
            "source_ip": None,
            "location": "Server Room A",
            "threat_level": "CRITICAL",
            "description": "Decoy credential used - confirmed malicious activity",
            "metadata": {}
        }


class TestEventProcessing:
    """Test event processing pipeline"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend = get_backend()
        self.generator = TestDataGenerator()
    
    def test_normal_access_event(self):
        """Test processing of normal access event"""
        event_data = self.generator.generate_access_event(status=AccessStatus.SUCCESS)
        result = self.backend.process_event(event_data)
        assert result == True
    
    def test_failed_access_event(self):
        """Test failed access detection"""
        # Generate multiple failed attempts
        for i in range(5):
            event_data = self.generator.generate_access_event(status=AccessStatus.FAILED)
            self.backend.process_event(event_data)
        
        # Should generate anomaly alerts
        alerts = self.backend.alert_engine.get_alerts(severity="HIGH")
        assert len(alerts) > 0
    
    def test_decoy_credential_detection(self):
        """Test teapot (decoy credential) detection"""
        event_data = self.generator.generate_access_event(use_decoy=True)
        self.backend.process_event(event_data)
        
        # Should generate CRITICAL alert
        critical_alerts = self.backend.alert_engine.get_alerts(severity="CRITICAL")
        assert len(critical_alerts) > 0
    
    def test_abnormal_time_detection(self):
        """Test abnormal access time detection"""
        event_data = self.generator.generate_access_event(abnormal_hour=True)
        self.backend.process_event(event_data)
        
        # Should detect abnormal time
        alerts = self.backend.alert_engine.get_alerts(severity="MEDIUM")
        assert len(alerts) > 0
    
    def test_honeypot_interaction(self):
        """Test honeypot event processing"""
        event_data = self.generator.generate_honeypot_event()
        result = self.backend.process_event(event_data)
        assert result == True
        
        # Should create CRITICAL alert
        critical_alerts = self.backend.alert_engine.get_alerts(severity="CRITICAL")
        assert len(critical_alerts) > 0
    
    def test_network_anomaly(self):
        """Test network anomaly detection"""
        event_data = self.generator.generate_network_event(anomaly_score=0.9)
        result = self.backend.process_event(event_data)
        assert result == True
        
        # Should create alert for high anomaly score
        alerts = self.backend.alert_engine.get_alerts(severity="HIGH")
        assert len(alerts) > 0
    
    def test_endpoint_threat(self):
        """Test endpoint threat detection"""
        event_data = self.generator.generate_endpoint_event(severity="CRITICAL")
        result = self.backend.process_event(event_data)
        assert result == True
        
        # Should create alert
        alerts = self.backend.alert_engine.get_alerts(severity="CRITICAL")
        assert len(alerts) > 0
    
    def test_teapot_event(self):
        """Test teapot event processing"""
        event_data = self.generator.generate_teapot_event()
        result = self.backend.process_event(event_data)
        assert result == True
        
        # Should create CRITICAL alert
        critical_alerts = self.backend.alert_engine.get_alerts(severity="CRITICAL")
        assert len(critical_alerts) > 0
    
    def test_system_status(self):
        """Test system status reporting"""
        status = self.backend.get_system_status()
        assert "timestamp" in status
        assert "receiver_stats" in status
        assert "alert_stats" in status
        assert "storage_stats" in status


def run_demo_scenarios():
    """
    Run demonstration scenarios showing different attack types
    """
    print("\n" + "="*80)
    print("GodsEye Backend - Demo Scenarios")
    print("="*80 + "\n")
    
    backend = get_backend()
    generator = TestDataGenerator()
    
    # Scenario 1: Wrong Card Attack
    print("\n📌 Scenario 1: Multiple Failed Access Attempts (Brute Force)")
    print("-" * 80)
    for i in range(5):
        event_data = generator.generate_access_event(status=AccessStatus.FAILED)
        backend.process_event(event_data)
    print("✓ Processed 5 failed access attempts")
    
    # Scenario 2: Honeypot Hit
    print("\n📌 Scenario 2: Attacker Interaction with Honeypot")
    print("-" * 80)
    event_data = generator.generate_honeypot_event()
    backend.process_event(event_data)
    print("✓ Processed honeypot interaction")
    
    # Scenario 3: Decoy Credential Used
    print("\n📌 Scenario 3: Decoy Credential Used (Teapot Triggered)")
    print("-" * 80)
    event_data = generator.generate_teapot_event()
    backend.process_event(event_data)
    print("✓ Processed teapot event")
    
    # Scenario 4: Abnormal Access Time
    print("\n📌 Scenario 4: Access Attempt at Abnormal Hour")
    print("-" * 80)
    event_data = generator.generate_access_event(abnormal_hour=True)
    backend.process_event(event_data)
    print("✓ Processed abnormal time access")
    
    # Scenario 5: Network Anomaly
    print("\n📌 Scenario 5: High Anomaly Score Network Traffic")
    print("-" * 80)
    event_data = generator.generate_network_event(anomaly_score=0.95)
    backend.process_event(event_data)
    print("✓ Processed network anomaly")
    
    # Scenario 6: Endpoint Threat
    print("\n📌 Scenario 6: Suspicious Endpoint Activity")
    print("-" * 80)
    event_data = generator.generate_endpoint_event(severity="CRITICAL")
    backend.process_event(event_data)
    print("✓ Processed endpoint threat")
    
    # Display final statistics
    print("\n" + "="*80)
    print("System Statistics")
    print("="*80)
    status = backend.get_system_status()
    print(f"\nTotal Events Received: {status['receiver_stats']['total_received']}")
    print(f"Total Events Processed: {status['receiver_stats']['total_processed']}")
    print(f"Total Alerts Generated: {status['alert_stats']['total_generated']}")
    print(f"\nAlerts by Severity:")
    for severity, count in status['alert_stats']['by_severity'].items():
        print(f"  {severity}: {count}")
    
    print("\n" + "="*80)
    print("Demo Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run demo scenarios
    run_demo_scenarios()
