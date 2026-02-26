"""
Database Test Script
Test the access event database functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db_storage import get_access_db
from backend.schemas import AccessEvent, AccessMethod, AccessStatus


def test_database():
    """Test database operations"""
    
    print("\n" + "="*80)
    print("🗄️  GodsEye PostgreSQL Access Event Database Test")
    print("="*80)
    
    # PostgreSQL connection
    print("\n📝 PostgreSQL Connection Details:")
    host = input("Host [localhost]: ").strip() or "localhost"
    port = input("Port [5432]: ").strip() or "5432"
    dbname = input("Database name [godseye]: ").strip() or "godseye"
    user = input("Username [godseye]: ").strip() or "godseye"
    password = input("Password [godseye_secure_password]: ").strip() or "godseye_secure_password"
    
    print("\n🔌 Connecting to PostgreSQL...")
    try:
        db = get_access_db(
            db_host=host,
            db_port=int(port),
            db_name=dbname,
            db_user=user,
            db_password=password
        )
        print(f"✅ Connected to PostgreSQL: {host}:{port}/{dbname}")
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database 'godseye' exists")
        print("  3. User credentials are correct")
        print("\nSee database/POSTGRES_SETUP.md for setup instructions")
        return
    
    # Test 1: Save successful access event
    print("\n" + "-"*80)
    print("TEST 1: Saving successful access event")
    print("-"*80)
    
    success_event = AccessEvent(
        event_id="test_acc_001",
        timestamp=datetime.utcnow(),
        device_id="access_door_01",
        location="Server Room A",
        access_method=AccessMethod.RFID_FINGERPRINT,
        card_id="CARD_12345",
        fingerprint_id="FP_USER_001",
        user_id="USER_001",
        status=AccessStatus.SUCCESS
    )
    
    result = db.save_access_event(success_event)
    print(f"✅ Event saved: {result}")
    
    # Test 2: Save failed access events
    print("\n" + "-"*80)
    print("TEST 2: Saving multiple failed access events")
    print("-"*80)
    
    for i in range(1, 4):
        failed_event = AccessEvent(
            event_id=f"test_acc_fail_{i:03d}",
            timestamp=datetime.utcnow(),
            device_id="access_door_01",
            location="Server Room A",
            access_method=AccessMethod.RFID,
            card_id="CARD_WRONG",
            status=AccessStatus.FAILED,
            failure_reason="Invalid card ID"
        )
        db.save_access_event(failed_event)
        print(f"✅ Failed event {i} saved")
    
    # Test 3: Query all events
    print("\n" + "-"*80)
    print("TEST 3: Querying all access events")
    print("-"*80)
    
    all_events = db.get_access_events(limit=10)
    print(f"\nFound {len(all_events)} events:")
    for event in all_events:
        print(f"  • {event['event_id']} - {event['status']} - {event['device_id']} - {event['timestamp']}")
    
    # Test 4: Query failed attempts
    print("\n" + "-"*80)
    print("TEST 4: Querying failed access attempts")
    print("-"*80)
    
    failed_events = db.get_failed_attempts(device_id="access_door_01", minutes=10)
    print(f"\nFound {len(failed_events)} failed attempts in last 10 minutes:")
    for event in failed_events:
        print(f"  • {event['event_id']} - {event['card_id']} - {event['failure_reason']}")
    
    # Test 5: Query by device
    print("\n" + "-"*80)
    print("TEST 5: Querying events by device ID")
    print("-"*80)
    
    device_events = db.get_access_events(device_id="access_door_01", limit=10)
    print(f"\nFound {len(device_events)} events for device 'access_door_01'")
    
    # Test 6: Query by status
    print("\n" + "-"*80)
    print("TEST 6: Querying events by status")
    print("-"*80)
    
    success_events = db.get_access_events(status="success", limit=10)
    print(f"\nFound {len(success_events)} successful access events")
    
    # Test 7: Get statistics
    print("\n" + "-"*80)
    print("TEST 7: Database Statistics")
    print("-"*80)
    
    stats = db.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total Events:     {stats.get('total_events', 0)}")
    print(f"  Successful:       {stats.get('success_count', 0)}")
    print(f"  Failed:           {stats.get('failed_count', 0)}")
    print(f"  Denied:           {stats.get('denied_count', 0)}")
    print(f"  Unique Devices:   {stats.get('unique_devices', 0)}")
    print(f"  Unique Users:     {stats.get('unique_users', 0)}")
    print(f"  Success Rate:     {stats.get('success_rate', 0):.2f}%")
    
    # Test 8: Add event with metadata
    print("\n" + "-"*80)
    print("TEST 8: Saving event with metadata")
    print("-"*80)
    
    metadata_event = AccessEvent(
        event_id="test_acc_metadata",
        timestamp=datetime.utcnow(),
        device_id="access_door_02",
        location="Control Room",
        access_method=AccessMethod.FINGERPRINT,
        fingerprint_id="FP_ADMIN_001",
        user_id="ADMIN_001",
        status=AccessStatus.SUCCESS,
        metadata={
            "ip_address": "192.168.1.100",
            "session_id": "sess_12345",
            "custom_field": "test_value"
        }
    )
    
    db.save_access_event(metadata_event)
    print("✅ Event with metadata saved")
    
    # Retrieve and display
    retrieved = db.get_access_events(limit=1)
    if retrieved:
        print(f"\nMetadata stored: {retrieved[0].get('metadata', {})}")
    
    print("\n" + "="*80)
    print("✅ All database tests completed successfully!")
    print("="*80)
    print(f"\n💾 Database: PostgreSQL - {host}:{port}/{dbname}")
    print(f"📊 Total events in database: {stats.get('total_events', 0)}")
    print("\n")


if __name__ == "__main__":
    test_database()
