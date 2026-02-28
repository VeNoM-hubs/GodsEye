"""
GodsEye Database Demo
Quick demo showing database capabilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from backend.db_storage import get_db


def demo():
    """Quick database demo"""
    
    print("\n" + "="*80)
    print("👁️  GodsEye Database Demo")
    print("="*80)
    
    # Connect to database
    print("\n🔌 Connecting to PostgreSQL...")
    db = get_db()
    print("✅ Connected!")
    
    print("\n" + "-"*80)
    print("📊 Current Database Status")
    print("-"*80)
    
    stats = db.get_statistics()
    
    print(f"\n📦 Data Overview:")
    print(f"  • Users: {stats.get('users', {}).get('total', 0)}")
    print(f"  • Resources: {stats.get('resources', {}).get('total', 0)}")
    print(f"  • Physical Events: {stats.get('events', {}).get('physical_total', 0)}")
    print(f"  • Digital Events: {stats.get('events', {}).get('digital_total', 0)}")
    print(f"  • Unified Logs: {stats.get('events', {}).get('main_total', 0)}")
    print(f"  • Active Threats: {stats.get('threats', {}).get('active', 0)}")
    
    print(f"\n📈 Last 24 Hours:")
    recent = stats.get('recent_24h', {})
    print(f"  • Physical Events: {recent.get('physical_events', 0)}")
    print(f"  • Digital Events: {recent.get('digital_events', 0)}")
    print(f"  • HIGH Severity: {recent.get('high_severity', 0)}")
    
    print("\n" + "-"*80)
    print("🔥 High Severity Events (Last 24h)")
    print("-"*80)
    
    high_sev = db.get_high_severity_events(hours=24, limit=10)
    
    if high_sev:
        for event in high_sev:
            print(f"\n  ⚠️  {event['source']} Event ID: {event['id']}")
            print(f"     User: {event['user_id']}")
            print(f"     Resource: {event['resource_id']}")
            print(f"     Type: {event['event_type']}")
            print(f"     Time: {event['event_time']}")
            if event['correlation_flag']:
                print(f"     🔗 Correlated with threat detection")
    else:
        print("\n  ✅ No high severity events in last 24 hours")
    
    print("\n" + "-"*80)
    print("🎯 Active Threats")
    print("-"*80)
    
    threats = db.get_threats(status='ACTIVE', limit=10)
    
    if threats:
        for threat in threats:
            print(f"\n  🚨 Threat #{threat['threat_id']}")
            print(f"     User: {threat['user_id']}")
            print(f"     Pattern: {threat['threat_pattern']}")
            print(f"     MITRE: {threat['mitre_id']}")
            print(f"     Risk Score: {threat['risk_score']}")
            print(f"     Events: {threat['event_count']}")
            print(f"     Last Activity: {threat['last_seen']}")
    else:
        print("\n  ✅ No active threats detected")
    
    print("\n" + "-"*80)
    print("📊 Dashboard Summary")
    print("-"*80)
    
    dashboard = db.get_dashboard_summary()
    
    top_users = dashboard.get('top_users', [])
    if top_users:
        print(f"\n  👥 Most Active Users (last 7 days):")
        for user in top_users[:5]:
            print(f"     • {user['user_id']}: {user['event_count']} events")
    
    top_resources = dashboard.get('top_resources', [])
    if top_resources:
        print(f"\n  🎯 Most Accessed Resources (last 7 days):")
        for resource in top_resources[:5]:
            print(f"     • {resource['resource_id']}: {resource['access_count']} accesses")
    
    severity_dist = dashboard.get('severity_distribution', {})
    if severity_dist:
        print(f"\n  📈 Severity Distribution (last 24h):")
        for severity, count in severity_dist.items():
            print(f"     • {severity}: {count}")
    
    high_risk = dashboard.get('high_risk_threats', [])
    if high_risk:
        print(f"\n  ⚠️  High Risk Threats (Score >= 70):")
        for threat in high_risk[:5]:
            print(f"     • {threat['user_id']}: {threat['risk_score']} points")
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)
    print("\nGodsEye is monitoring your infrastructure 24/7")
    print("Run 'python tests/test_database.py' for comprehensive testing")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'godseye' exists")
        print("  3. Tables are created (run database/setup_postgres.sql)")
        print("  4. Some data exists (run tests/test_database.py first)")
