"""
Seed GodsEye Database with Initial Data
Sets up MITRE techniques, users, and resources
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db_storage import get_db


def seed_database():
    """Seed database with initial data"""
    
    print("\n" + "="*80)
    print("🌱 GodsEye Database Seeding")
    print("="*80)
    
    # Connect
    print("\n🔌 Connecting to PostgreSQL...")
    db = get_db()
    print("✅ Connected!")
    
    # ================================
    # MITRE ATT&CK Techniques
    # ================================
    print("\n" + "-"*80)
    print("📚 Adding MITRE ATT&CK Techniques...")
    print("-"*80)
    
    mitre_techniques = [
        # Initial Access
        ('T1078', 'Valid Accounts', 'Initial Access'),
        ('T1133', 'External Remote Services', 'Initial Access'),
        ('T1190', 'Exploit Public-Facing Application', 'Initial Access'),
        
        # Execution
        ('T1059', 'Command and Scripting Interpreter', 'Execution'),
        ('T1203', 'Exploitation for Client Execution', 'Execution'),
        
        # Persistence
        ('T1053', 'Scheduled Task/Job', 'Persistence'),
        ('T1136', 'Create Account', 'Persistence'),
        
        # Privilege Escalation
        ('T1068', 'Exploitation for Privilege Escalation', 'Privilege Escalation'),
        ('T1134', 'Access Token Manipulation', 'Privilege Escalation'),
        
        # Credential Access
        ('T1110', 'Brute Force', 'Credential Access'),
        ('T1003', 'OS Credential Dumping', 'Credential Access'),
        ('T1040', 'Network Sniffing', 'Credential Access'),
        
        # Lateral Movement
        ('T1021', 'Remote Services', 'Lateral Movement'),
        ('T1080', 'Taint Shared Content', 'Lateral Movement'),
        
        # Collection
        ('T1005', 'Data from Local System', 'Collection'),
        ('T1039', 'Data from Network Shared Drive', 'Collection'),
        
        # Exfiltration
        ('T1041', 'Exfiltration Over C2 Channel', 'Exfiltration'),
        ('T1048', 'Exfiltration Over Alternative Protocol', 'Exfiltration'),
        
        # Command and Control
        ('T1071', 'Application Layer Protocol', 'Command and Control'),
        ('T1095', 'Non-Application Layer Protocol', 'Command and Control')
    ]
    
    for tech_id, name, tactic in mitre_techniques:
        success = db.add_mitre_technique(tech_id, name, tactic)
        if success:
            print(f"  ✅ {tech_id}: {name}")
    
    print(f"\n📊 Added {len(mitre_techniques)} MITRE techniques")
    
    # ================================
    # Users
    # ================================
    print("\n" + "-"*80)
    print("👥 Adding Users...")
    print("-"*80)
    
    users = [
        # Admins - Level 10
        ('admin_root', 'Root Administrator', 'admin', 10),
        ('admin_security', 'Security Admin', 'admin', 10),
        
        # IT Staff - Level 8-9
        ('it_john', 'John Stevens', 'it_admin', 9),
        ('it_sarah', 'Sarah Connor', 'it_engineer', 8),
        
        # Engineers - Level 6-7
        ('eng_alice', 'Alice Johnson', 'senior_engineer', 7),
        ('eng_bob', 'Bob Williams', 'engineer', 6),
        ('eng_charlie', 'Charlie Brown', 'engineer', 6),
        
        # Analysts - Level 5
        ('analyst_dave', 'Dave Miller', 'data_analyst', 5),
        ('analyst_eve', 'Eve Davis', 'security_analyst', 5),
        
        # Regular Staff - Level 3-4
        ('staff_frank', 'Frank Wilson', 'employee', 4),
        ('staff_grace', 'Grace Lee', 'employee', 4),
        ('staff_henry', 'Henry Martinez', 'employee', 3),
        
        # Contractors - Level 2-3
        ('contractor_ivan', 'Ivan Petrov', 'contractor', 3),
        ('contractor_julia', 'Julia Anderson', 'contractor', 2),
        
        # Guests - Level 1
        ('guest_kevin', 'Kevin Guest', 'guest', 1),
        
        # Test/Suspicious Users
        ('test_attacker', 'Test Attacker', 'external', 1),
        ('honeypot_user', 'Honeypot Account', 'decoy', 1)
    ]
    
    for user_id, full_name, role, level in users:
        success = db.add_user(user_id, full_name, role, level)
        if success:
            print(f"  ✅ {full_name} ({role}, Level {level})")
    
    print(f"\n📊 Added {len(users)} users")
    
    # ================================
    # Resources
    # ================================
    print("\n" + "-"*80)
    print("🏢 Adding Resources...")
    print("-"*80)
    
    resources = [
        # Physical Doors - Level 8-10 (HIGH SECURITY)
        ('door_datacenter', 'Data Center Main Entry', 'physical_door', 10, True),
        ('door_server_room', 'Server Room', 'physical_door', 8, True),
        ('door_network_ops', 'Network Operations Center', 'physical_door', 8, True),
        
        # Physical Doors - Level 5-7 (MEDIUM SECURITY)
        ('door_it_lab', 'IT Lab', 'physical_door', 7, False),
        ('door_dev_area', 'Development Area', 'physical_door', 5, False),
        
        # Physical Doors - Level 1-3 (LOW SECURITY)
        ('door_main_lobby', 'Main Lobby', 'physical_door', 1, False),
        ('door_cafeteria', 'Cafeteria', 'physical_door', 1, False),
        ('door_conference', 'Conference Room', 'physical_door', 3, False),
        
        # Databases - Level 8-10
        ('db_production', 'Production Database', 'database', 10, True),
        ('db_payroll', 'Payroll Database', 'database', 9, True),
        ('db_customer', 'Customer Data', 'database', 9, True),
        ('db_analytics', 'Analytics Database', 'database', 7, False),
        ('db_staging', 'Staging Database', 'database', 6, False),
        ('db_development', 'Development Database', 'database', 4, False),
        
        # Servers - Level 7-10
        ('server_prod_web', 'Production Web Server', 'server', 9, True),
        ('server_prod_api', 'Production API Server', 'server', 9, True),
        ('server_backup', 'Backup Server', 'server', 10, True),
        ('server_monitoring', 'Monitoring Server', 'server', 7, False),
        ('server_dev', 'Development Server', 'server', 5, False),
        
        # File Systems - Level 5-10
        ('fs_financial', 'Financial Records', 'file_system', 10, True),
        ('fs_hr', 'HR Documents', 'file_system', 9, True),
        ('fs_legal', 'Legal Documents', 'file_system', 8, True),
        ('fs_projects', 'Project Files', 'file_system', 5, False),
        ('fs_public', 'Public Documents', 'file_system', 1, False),
        
        # Network Equipment - Level 8-10
        ('net_core_router', 'Core Router', 'network', 10, True),
        ('net_firewall', 'Main Firewall', 'network', 10, True),
        ('net_switch', 'Core Switch', 'network', 8, True),
        
        # Applications - Various Levels
        ('app_erp', 'ERP System', 'application', 7, True),
        ('app_crm', 'CRM System', 'application', 6, False),
        ('app_wiki', 'Internal Wiki', 'application', 3, False)
    ]
    
    for res_id, name, res_type, level, sensitive in resources:
        success = db.add_resource(res_id, name, res_type, level, sensitive)
        if success:
            sensitive_flag = " [SENSITIVE]" if sensitive else ""
            print(f"  ✅ {name} ({res_type}, Level {level}){sensitive_flag}")
    
    print(f"\n📊 Added {len(resources)} resources")
    
    # ================================
    # Summary
    # ================================
    print("\n" + "="*80)
    print("✅ Database Seeding Complete!")
    print("="*80)
    
    stats = db.get_statistics()
    print(f"\n📊 Current Database State:")
    print(f"  • MITRE Techniques: {len(mitre_techniques)}")
    print(f"  • Users: {stats['users']['total']}")
    print(f"  • Resources: {stats['resources']['total']}")
    print(f"    - Sensitive Resources: {stats['resources']['sensitive']}")
    
    print("\n" + "="*80)
    print("🎯 Next Steps:")
    print("="*80)
    print("  1. Run: python tests/test_database.py")
    print("     (Generates test events and threats)")
    print("")
    print("  2. Run: python tests/demo_database.py")
    print("     (View current system status)")
    print("")
    print("  3. Start logging real events!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'godseye' exists")
        print("  3. Tables are created (run database/setup_postgres.sql)")
        print("\nSome errors might occur if data already exists (that's OK!)")
