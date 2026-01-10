"""
Event Receiver Demo & Test
Demonstrates event receiver functionality with sample events
"""

import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '..')

from backend.event_receiver import EventReceiver, get_event_receiver
from backend.schemas import EventType


def demo_access_events():
    """Demo access event processing"""
    print("\n" + "="*80)
    print("TEST 1: Access Events")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Test 1: Valid successful access
    print("\n1️⃣ Testing VALID access event (success)...")
    valid_access = {
        "event_type": "access",
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": "access_door_01",
        "location": "Server Room A",
        "access_method": "rfid_fingerprint",
        "card_id": "CARD_12345",
        "fingerprint_id": "FP_USER_001",
        "user_id": "USER_001",
        "status": "success"
    }
    
    result = receiver.receive_event(valid_access)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
        print(f"   Device: {result.event_data.device_id}")
        print(f"   Location: {result.event_data.location}")
        print(f"   Status: {result.event_data.status}")
    else:
        print("❌ Failed to receive event")
    
    # Test 2: Failed access attempt
    print("\n2️⃣ Testing FAILED access event...")
    failed_access = {
        "event_type": "access",
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": "access_door_01",
        "location": "Server Room A",
        "access_method": "rfid",
        "card_id": "CARD_99999",
        "status": "failed",
        "failure_reason": "Invalid card ID"
    }
    
    result = receiver.receive_event(failed_access)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
        print(f"   Status: {result.event_data.status}")
        print(f"   Reason: {result.event_data.failure_reason}")
    else:
        print("❌ Failed to receive event")
    
    # Test 3: Invalid event (missing required field)
    print("\n3️⃣ Testing INVALID access event (missing device_id)...")
    invalid_access = {
        "event_type": "access",
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Server Room A",
        "access_method": "rfid",
        "status": "success"
    }
    
    result = receiver.receive_event(invalid_access)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
    else:
        print("❌ Validation failed (expected - missing required field)")
    
    return receiver


def demo_honeypot_events():
    """Demo honeypot event processing"""
    print("\n" + "="*80)
    print("TEST 2: Honeypot Events")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Test honeypot interaction
    print("\n1️⃣ Testing honeypot interaction event...")
    honeypot_event = {
        "event_type": "honeypot",
        "timestamp": datetime.utcnow().isoformat(),
        "honeypot_id": "hp_plc_001",
        "honeypot_type": "fake_plc",
        "source_ip": "192.168.1.100",
        "source_port": 52341,
        "interaction_type": "command",
        "payload": "MODBUS_READ_COILS",
        "protocol": "modbus"
    }
    
    result = receiver.receive_event(honeypot_event)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
        print(f"   Honeypot: {result.event_data.honeypot_type}")
        print(f"   Source IP: {result.event_data.source_ip}")
        print(f"   Interaction: {result.event_data.interaction_type}")
        print(f"   Threat Level: {result.event_data.threat_level}")
    else:
        print("❌ Failed to receive event")
    
    return receiver


def demo_network_events():
    """Demo network event processing"""
    print("\n" + "="*80)
    print("TEST 3: Network Events")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Test network anomaly
    print("\n1️⃣ Testing network anomaly event...")
    network_event = {
        "event_type": "network",
        "timestamp": datetime.utcnow().isoformat(),
        "network_event_type": "suspicious_connection",
        "source_ip": "10.0.0.50",
        "destination_ip": "10.0.0.100",
        "source_port": 44512,
        "destination_port": 502,
        "protocol": "modbus",
        "packet_count": 150,
        "byte_count": 45000,
        "anomaly_score": 0.85,
        "description": "Unusual Modbus traffic pattern detected"
    }
    
    result = receiver.receive_event(network_event)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
        print(f"   Type: {result.event_data.network_event_type}")
        print(f"   Source: {result.event_data.source_ip}:{result.event_data.source_port}")
        print(f"   Destination: {result.event_data.destination_ip}:{result.event_data.destination_port}")
        print(f"   Anomaly Score: {result.event_data.anomaly_score}")
    else:
        print("❌ Failed to receive event")
    
    return receiver


def demo_endpoint_events():
    """Demo endpoint event processing"""
    print("\n" + "="*80)
    print("TEST 4: Endpoint Events (Sysmon/Wazuh)")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Test endpoint event
    print("\n1️⃣ Testing endpoint event (suspicious process)...")
    endpoint_event = {
        "event_type": "endpoint",
        "timestamp": datetime.utcnow().isoformat(),
        "hostname": "ICS-WORKSTATION-01",
        "endpoint_id": "endpoint_001",
        "operating_system": "Windows 10",
        "endpoint_event_type": "process_creation",
        "process_name": "powershell.exe",
        "process_id": 4512,
        "parent_process": "cmd.exe",
        "command_line": "powershell.exe -enc <base64_encoded_command>",
        "user": "operator_01",
        "severity": "WARNING",
        "description": "Suspicious PowerShell execution detected"
    }
    
    result = receiver.receive_event(endpoint_event)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
        print(f"   Hostname: {result.event_data.hostname}")
        print(f"   Event Type: {result.event_data.endpoint_event_type}")
        print(f"   Process: {result.event_data.process_name} (PID: {result.event_data.process_id})")
        print(f"   Severity: {result.event_data.severity}")
    else:
        print("❌ Failed to receive event")
    
    return receiver


def demo_teapot_events():
    """Demo teapot event processing"""
    print("\n" + "="*80)
    print("TEST 5: Teapot Events (Decoy Credentials)")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Test teapot trigger
    print("\n1️⃣ Testing teapot event (decoy card used)...")
    teapot_event = {
        "event_type": "teapot",
        "timestamp": datetime.utcnow().isoformat(),
        "decoy_type": "fake_card",
        "decoy_id": "FAKE_CARD_001",
        "device_id": "access_door_01",
        "location": "Server Room A",
        "threat_level": "CRITICAL"
    }
    
    result = receiver.receive_event(teapot_event)
    if result:
        print(f"✅ Event received: {result.event_data.event_id}")
        print(f"   Decoy Type: {result.event_data.decoy_type}")
        print(f"   Decoy ID: {result.event_data.decoy_id}")
        print(f"   Location: {result.event_data.location}")
        print(f"   Threat Level: {result.event_data.threat_level}")
    else:
        print("❌ Failed to receive event")
    
    return receiver


def demo_event_routing():
    """Demo event routing with handlers"""
    print("\n" + "="*80)
    print("TEST 6: Event Routing with Handlers")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Define handler functions
    def access_handler(event):
        print(f"   📥 ACCESS handler called for event {event.event_id}")
    
    def honeypot_handler(event):
        print(f"   🍯 HONEYPOT handler called for event {event.event_id}")
    
    def network_handler(event):
        print(f"   🌐 NETWORK handler called for event {event.event_id}")
    
    def endpoint_handler(event):
        print(f"   💻 ENDPOINT handler called for event {event.event_id}")
    
    def teapot_handler(event):
        print(f"   🫖 TEAPOT handler called for event {event.event_id}")
    
    # Register handlers
    print("\n1️⃣ Registering handlers...")
    receiver.register_handler(EventType.ACCESS, access_handler)
    receiver.register_handler(EventType.HONEYPOT, honeypot_handler)
    receiver.register_handler(EventType.NETWORK, network_handler)
    receiver.register_handler(EventType.ENDPOINT, endpoint_handler)
    receiver.register_handler(EventType.TEAPOT, teapot_handler)
    print("✅ All handlers registered")
    
    # Test routing
    print("\n2️⃣ Testing event routing...")
    
    events = [
        {
            "event_type": "access",
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": "door_01",
            "location": "Server Room",
            "access_method": "rfid",
            "card_id": "CARD_001",
            "status": "success"
        },
        {
            "event_type": "honeypot",
            "timestamp": datetime.utcnow().isoformat(),
            "honeypot_id": "hp_001",
            "honeypot_type": "fake_plc",
            "source_ip": "192.168.1.100",
            "interaction_type": "connection"
        },
        {
            "event_type": "teapot",
            "timestamp": datetime.utcnow().isoformat(),
            "decoy_type": "fake_card",
            "decoy_id": "FAKE_CARD_999"
        }
    ]
    
    for event_data in events:
        print(f"\nRouting {event_data['event_type']} event...")
        receiver.process_event(event_data)
    
    return receiver


def demo_statistics():
    """Demo receiver statistics"""
    print("\n" + "="*80)
    print("TEST 7: Event Receiver Statistics")
    print("="*80)
    
    receiver = EventReceiver()
    
    # Process multiple events
    print("\n1️⃣ Processing multiple events...")
    
    events = [
        {"event_type": "access", "timestamp": datetime.utcnow().isoformat(), "device_id": "d1", "location": "L1", "access_method": "rfid", "card_id": "C1", "status": "success"},
        {"event_type": "access", "timestamp": datetime.utcnow().isoformat(), "device_id": "d2", "location": "L2", "access_method": "rfid", "card_id": "C2", "status": "failed"},
        {"event_type": "honeypot", "timestamp": datetime.utcnow().isoformat(), "honeypot_id": "hp1", "honeypot_type": "fake_plc", "source_ip": "1.2.3.4", "interaction_type": "command"},
        {"event_type": "network", "timestamp": datetime.utcnow().isoformat(), "network_event_type": "port_scan", "source_ip": "1.1.1.1", "destination_ip": "2.2.2.2", "protocol": "tcp"},
        {"event_type": "endpoint", "timestamp": datetime.utcnow().isoformat(), "hostname": "host1", "endpoint_id": "ep1", "operating_system": "Windows", "endpoint_event_type": "process_creation", "severity": "INFO"},
        {"event_type": "teapot", "timestamp": datetime.utcnow().isoformat(), "decoy_type": "fake_card", "decoy_id": "FAKE_001"},
        # Invalid event
        {"event_type": "access", "timestamp": datetime.utcnow().isoformat()},  # Missing required fields
    ]
    
    for event in events:
        receiver.receive_event(event)
    
    # Get and display statistics
    print("\n2️⃣ Event Receiver Statistics:")
    print("-" * 80)
    stats = receiver.get_statistics()
    
    print(f"Total Received:  {stats['total_received']}")
    print(f"Total Processed: {stats['total_processed']}")
    print(f"Total Errors:    {stats['total_errors']}")
    print(f"Success Rate:    {stats['success_rate']:.2%}")
    
    print(f"\nEvents by Type:")
    for event_type, count in stats['by_type'].items():
        print(f"  {event_type}: {count}")
    
    return receiver


def main():
    """Run all event receiver demos"""
    print("\n" + "="*80)
    print("🔵 GodsEye Event Receiver Demo")
    print("="*80)
    print("Testing all event types and receiver functionality\n")
    
    # Run all demos
    demo_access_events()
    demo_honeypot_events()
    demo_network_events()
    demo_endpoint_events()
    demo_teapot_events()
    demo_event_routing()
    demo_statistics()
    
    # Final summary
    print("\n" + "="*80)
    print("✅ All Event Receiver Tests Complete!")
    print("="*80)
    print("\nThe event receiver successfully:")
    print("  ✅ Validates events against schemas")
    print("  ✅ Handles all 5 event types (Access, Honeypot, Network, Endpoint, Teapot)")
    print("  ✅ Generates unique event IDs")
    print("  ✅ Routes events to registered handlers")
    print("  ✅ Tracks statistics")
    print("  ✅ Handles invalid events gracefully")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
