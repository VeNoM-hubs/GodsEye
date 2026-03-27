"""
GodsEye Master Test Suite
Interactive CLI for testing all components:
- Database connectivity
- Honeypot API endpoints
- Event injection and storage
- Threat detection
- Log retrieval and analytics
"""

import sys
import os
import requests
import json
import time
import subprocess
import atexit
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.db_storage import GodsEyeDatabase, HoneypotLog, User, Resource, Threat
from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GodsEyeTestSuite:
    """Master test suite for GodsEye"""
    
    def __init__(self):
        self.db = None
        self.api_base_url = "http://localhost:8000"
        self.api_ready = False
        self.backend_process: Optional[subprocess.Popen] = None
        atexit.register(self._cleanup_background_process)
        print(f"\n{Colors.HEADER}{'='*70}")
        print("🔍 GodsEye Master Test Suite")
        print(f"{'='*70}{Colors.ENDC}\n")
    
    # ================================
    # Menu System
    # ================================
    
    def display_main_menu(self):
        """Display main menu options"""
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}Main Menu:{Colors.ENDC}")
        print("  1. Database Tests")
        print("  2. Honeypot API Tests")
        print("  3. Event Injection Tests")
        print("  4. Threat Detection Tests")
        print("  5. Log Retrieval & Analytics")
        print("  6. System Statistics")
        print("  7. Interactive Demo")
        print("  8. Exit")
        choice = input("\nSelect option (1-8): ").strip()
        return choice
    
    # ================================
    # 1. Database Tests
    # ================================
    
    def test_database(self):
        """Test database connectivity and schema"""
        print(f"\n{Colors.HEADER}🔌 Database Tests{Colors.ENDC}")
        
        while True:
            print("\n  1. Test Connection")
            print("  2. Verify Tables")
            print("  3. Check Table Row Counts")
            print("  4. Inspect honeypot_logs Schema")
            print("  5. Back to Main Menu")
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self._test_connection()
            elif choice == "2":
                self._verify_tables()
            elif choice == "3":
                self._check_row_counts()
            elif choice == "4":
                self._inspect_honeypot_schema()
            elif choice == "5":
                break
            else:
                print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
    
    def _test_connection(self):
        """Test PostgreSQL connection"""
        try:
            print("\n⏳ Testing PostgreSQL connection...")
            self.db = GodsEyeDatabase()
            session = self.db.get_session()
            result = session.execute(text("SELECT 1")).scalar()
            session.close()
            
            print(f"{Colors.OKGREEN}✅ Database connected successfully!{Colors.ENDC}")
            print("   Host: localhost")
            print("   Port: 5432")
            print("   Database: godseye")
            print("   User: postgres")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Connection failed: {str(e)}{Colors.ENDC}")
    
    def _verify_tables(self):
        """Verify all required tables exist"""
        try:
            print("\n⏳ Verifying tables...")
            session = self.db.get_session()
            
            required_tables = [
                'users', 'resources', 'physical_logs', 'digital_logs',
                'honeypot_logs', 'main_logs', 'mitre_techniques', 'threats'
            ]
            
            query = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            result = session.execute(text(query)).fetchall()
            existing_tables = [row[0] for row in result]
            session.close()
            
            missing = [t for t in required_tables if t not in existing_tables]
            
            print(f"\n{Colors.OKGREEN}Tables Found:{Colors.ENDC}")
            for table in required_tables:
                status = "✅" if table in existing_tables else "❌"
                print(f"  {status} {table}")
            
            if missing:
                print(f"\n{Colors.FAIL}Missing tables: {missing}{Colors.ENDC}")
            else:
                print(f"\n{Colors.OKGREEN}All required tables present!{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _check_row_counts(self):
        """Check row counts in each table"""
        try:
            print("\n⏳ Checking table row counts...")
            session = self.db.get_session()
            
            tables = [
                'users', 'resources', 'physical_logs', 'digital_logs',
                'honeypot_logs', 'main_logs', 'mitre_techniques', 'threats'
            ]
            
            print(f"\n{Colors.OKCYAN}Table Statistics:{Colors.ENDC}")
            for table in tables:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  {table:<20} {count:>5} rows")
            
            session.close()
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _inspect_honeypot_schema(self):
        """Show honeypot_logs table schema"""
        try:
            print("\n⏳ Inspecting honeypot_logs schema...")
            session = self.db.get_session()
            
            query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'honeypot_logs'
                ORDER BY ordinal_position
            """
            result = session.execute(text(query)).fetchall()
            session.close()
            
            print(f"\n{Colors.OKCYAN}honeypot_logs columns:{Colors.ENDC}")
            print(f"{'Column':<25} {'Type':<20} {'Nullable':<10}")
            print("-" * 55)
            for col, dtype, nullable in result:
                print(f"{col:<25} {dtype:<20} {nullable:<10}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # 2. Honeypot API Tests
    # ================================
    
    def test_honeypot_api(self):
        """Test honeypot API endpoints"""
        print(f"\n{Colors.HEADER}🔌 Honeypot API Tests{Colors.ENDC}")
        
        # Check API availability
        if not self._check_api_ready():
            return
        
        while True:
            print("\n  1. Test Health Endpoint")
            print("  2. Test POST /honeypot/log")
            print("  3. Test GET /honeypot/logs")
            print("  4. Test GET /honeypot/stats")
            print("  5. Submit Test Event")
            print("  6. Back to Main Menu")
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self._test_health()
            elif choice == "2":
                self._test_post_log()
            elif choice == "3":
                self._test_get_logs()
            elif choice == "4":
                self._test_stats()
            elif choice == "5":
                self._submit_test_event()
            elif choice == "6":
                break
            else:
                print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
    
    def _cleanup_background_process(self):
        """Stop auto-started backend process on exit."""
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
            except Exception:
                pass

    def _start_backend_main(self) -> bool:
        """Start backend.main in background (it also starts API server)."""
        if self.backend_process and self.backend_process.poll() is None:
            return True

        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", "backend.main"],
                cwd=PROJECT_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to auto-start backend.main: {str(e)}{Colors.ENDC}")
            return False

    def _check_api_ready(self, auto_start: bool = True) -> bool:
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"{Colors.OKGREEN}✅ API Server is running!{Colors.ENDC}")
                self.api_ready = True
                return True
            else:
                print(f"{Colors.FAIL}❌ API returned status {response.status_code}{Colors.ENDC}")
                return False
        except requests.exceptions.ConnectionError:
            if auto_start:
                print(f"{Colors.WARNING}⚠️  API not reachable, auto-starting backend.main...{Colors.ENDC}")
                if not self._start_backend_main():
                    return False

                for _ in range(20):
                    try:
                        response = requests.get(f"{self.api_base_url}/health", timeout=2)
                        if response.status_code == 200:
                            print(f"{Colors.OKGREEN}✅ API Server auto-started successfully!{Colors.ENDC}")
                            self.api_ready = True
                            return True
                    except Exception:
                        pass
                    time.sleep(1)

            print(f"{Colors.FAIL}❌ API Server not reachable at {self.api_base_url}{Colors.ENDC}")
            print(f"   Start it with: python -m backend.main")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
            return False
    
    def _test_health(self):
        """Test API health endpoint"""
        try:
            print("\n⏳ Testing GET /health...")
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            data = response.json()
            
            print(f"{Colors.OKGREEN}✅ Response:{Colors.ENDC}")
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _test_post_log(self):
        """Test posting a honeypot event"""
        try:
            print("\n⏳ Testing POST /honeypot/log...")
            
            payload = {
                "honeypot_id": "ESP32-TESTDEVICE",
                "honeypot_name": "Telnet Server",
                "honeypot_type": "multi-service",
                "attacker_ip": "192.168.1.50",
                "attacker_port": 12345,
                "target_port": 23,
                "username_attempted": "admin",
                "password_attempted": "password123",
                "commands_executed": ["ls", "whoami", "id"],
                "auth_success": False,
                "session_duration_ms": 5000,
                "threat_level": "HIGH"
            }
            
            print(f"\nPayload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.api_base_url}/honeypot/log",
                json=payload,
                timeout=5
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                print(f"\n{Colors.OKGREEN}✅ Event posted successfully!{Colors.ENDC}")
                print(f"   Log ID: {data.get('honeypot_log_id')}")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"{Colors.FAIL}❌ Failed: {data.get('error', 'Unknown error')}{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _test_get_logs(self):
        """Test retrieving logs from API"""
        try:
            print("\n⏳ Testing GET /honeypot/logs...")
            
            response = requests.get(
                f"{self.api_base_url}/honeypot/logs?limit=10",
                timeout=5
            )
            data = response.json()
            
            print(f"\n{Colors.OKGREEN}✅ Response:{Colors.ENDC}")
            print(f"Total events: {data.get('total')}")
            print(f"Returned: {data.get('count')} logs\n")
            
            logs = data.get('logs', [])
            if logs:
                for log in logs[:3]:  # Show first 3
                    print(f"[{log.get('id')}] {log.get('attacker_ip')}:{log.get('attacker_port')} "
                          f"→ Port {log.get('target_port')} | {log.get('threat_level')}")
                if len(logs) > 3:
                    print(f"... and {len(logs) - 3} more")
            else:
                print(f"{Colors.WARNING}No logs found (run 'Submit Test Event' first){Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _test_stats(self):
        """Test getting honeypot statistics"""
        try:
            print("\n⏳ Testing GET /honeypot/stats...")
            
            response = requests.get(
                f"{self.api_base_url}/honeypot/stats",
                timeout=5
            )
            data = response.json()
            
            print(f"\n{Colors.OKGREEN}✅ Honeypot Statistics:{Colors.ENDC}")
            print(f"  Total Events:      {data.get('total_events')}")
            print(f"  High Threat Count: {data.get('high_threat_count')}")
            print(f"  Unique Attackers:  {data.get('unique_attackers')}")
            print(f"  Ports Exploited:   {data.get('ports_exploited')}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _submit_test_event(self):
        """Submit a custom test event"""
        try:
            print("\n📝 Create Custom Honeypot Event")
            print("-" * 50)
            
            honeypot_id = input("Honeypot ID (ESP32-XXXXX): ").strip() or "ESP32-CUSTOM"
            attacker_ip = input("Attacker IP (e.g., 192.168.1.5): ").strip() or "192.168.1.5"
            target_port = input("Target Port (23 for Telnet): ").strip() or "23"
            command = input("Command/Username: ").strip() or "admin"
            threat_level = input("Threat Level (LOW/MEDIUM/HIGH/CRITICAL): ").strip() or "MEDIUM"
            
            payload = {
                "honeypot_id": honeypot_id,
                "honeypot_name": "Telnet Server",
                "honeypot_type": "multi-service",
                "attacker_ip": attacker_ip,
                "attacker_port": 12345,
                "target_port": int(target_port),
                "username_attempted": command,
                "password_attempted": "attempted",
                "commands_executed": [command],
                "auth_success": False,
                "session_duration_ms": 3000,
                "threat_level": threat_level
            }
            
            response = requests.post(
                f"{self.api_base_url}/honeypot/log",
                json=payload,
                timeout=5
            )
            data = response.json()
            
            if data.get('success'):
                print(f"\n{Colors.OKGREEN}✅ Event stored! ID: {data.get('honeypot_log_id')}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ Failed: {data.get('error')}{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # 3. Event Injection Tests
    # ================================
    
    def test_event_injection(self):
        """Test event injection into database"""
        print(f"\n{Colors.HEADER}💉 Event Injection Tests{Colors.ENDC}")
        
        while True:
            print("\n  1. Inject Honeypot Event (Direct DB)")
            print("  2. Inject Physical Access Event")
            print("  3. Inject Digital Event")
            print("  4. Verify Events in Database")
            print("  5. Back to Main Menu")
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self._inject_honeypot_event_db()
            elif choice == "2":
                self._inject_physical_event()
            elif choice == "3":
                self._inject_digital_event()
            elif choice == "4":
                self._verify_events()
            elif choice == "5":
                break
            else:
                print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
    
    def _inject_honeypot_event_db(self):
        """Inject honeypot event directly into database"""
        try:
            print("\n⏳ Injecting honeypot event...")
            session = self.db.get_session()
            
            log = HoneypotLog(
                honeypot_id="ESP32-DB-TEST",
                honeypot_name="Telnet Server",
                honeypot_type="multi-service",
                attacker_ip="10.0.0.1",
                attacker_port=54321,
                target_port=23,
                username_attempted="testuser",
                password_attempted="testpass",
                commands_executed=["whoami", "ls", "cat /etc/passwd"],
                auth_success=False,
                session_duration_ms=6000,
                threat_level="HIGH"
            )
            
            session.add(log)
            session.commit()
            log_id = log.id
            session.close()
            
            print(f"{Colors.OKGREEN}✅ Event injected! ID: {log_id}{Colors.ENDC}")
            print(f"   Attacker: 10.0.0.1:54321 → Port 23")
            print(f"   Threat Level: HIGH")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _inject_physical_event(self):
        """Inject physical access event"""
        try:
            print("\n⏳ Fetching users and resources for injection...")
            session = self.db.get_session()
            
            users = session.query(User).limit(5).all()
            resources = session.query(Resource).limit(5).all()
            
            if not users or not resources:
                print(f"{Colors.WARNING}⚠️  No users or resources found. Run seed_database.py first.{Colors.ENDC}")
                session.close()
                return
            
            from backend.db_storage import PhysicalLog
            
            user = users[0]
            resource = resources[0]
            
            phys_log = PhysicalLog(
                user_id=user.user_id,
                resource_id=resource.resource_id,
                access_status="DENIED"
            )
            
            session.add(phys_log)
            session.commit()
            log_id = phys_log.id
            session.close()
            
            print(f"{Colors.OKGREEN}✅ Physical event injected! ID: {log_id}{Colors.ENDC}")
            print(f"   User: {user.user_id} ({user.full_name})")
            print(f"   Resource: {resource.resource_id}")
            print(f"   Status: DENIED")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _inject_digital_event(self):
        """Inject digital event"""
        try:
            print("\n⏳ Fetching users and resources...")
            session = self.db.get_session()
            
            users = session.query(User).limit(5).all()
            resources = session.query(Resource).limit(5).all()
            
            if not users or not resources:
                print(f"{Colors.WARNING}⚠️  No users or resources found.{Colors.ENDC}")
                session.close()
                return
            
            from backend.db_storage import DigitalLog
            
            user = users[0]
            resource = resources[0]
            
            dig_log = DigitalLog(
                user_id=user.user_id,
                resource_id=resource.resource_id,
                action_type="FILE_ACCESS",
                raw_severity="HIGH"
            )
            
            session.add(dig_log)
            session.commit()
            log_id = dig_log.id
            session.close()
            
            print(f"{Colors.OKGREEN}✅ Digital event injected! ID: {log_id}{Colors.ENDC}")
            print(f"   User: {user.user_id}")
            print(f"   Resource: {resource.resource_id}")
            print(f"   Action: FILE_ACCESS (HIGH severity)")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _verify_events(self):
        """Show all recent events"""
        try:
            print("\n⏳ Retrieving recent events...")
            session = self.db.get_session()
            
            honeypot_count = session.query(HoneypotLog).count()
            physical_count = session.query(text("SELECT COUNT(*) FROM physical_logs")).scalar()
            digital_count = session.query(text("SELECT COUNT(*) FROM digital_logs")).scalar()
            
            print(f"\n{Colors.OKCYAN}Event Summary:{Colors.ENDC}")
            print(f"  Honeypot Events:  {honeypot_count}")
            print(f"  Physical Events:  {physical_count}")
            print(f"  Digital Events:   {digital_count}")
            
            # Show recent honeypot events
            recent = session.query(HoneypotLog).order_by(HoneypotLog.id.desc()).limit(5).all()
            if recent:
                print(f"\n{Colors.OKCYAN}Recent Honeypot Events:{Colors.ENDC}")
                for log in recent:
                    print(f"  [{log.id}] {log.attacker_ip}:{log.attacker_port} → "
                          f"Port {log.target_port} | {log.threat_level}")
            
            session.close()
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # 4. Threat Detection Tests
    # ================================
    
    def test_threat_detection(self):
        """Test threat detection system"""
        print(f"\n{Colors.HEADER}🚨 Threat Detection Tests{Colors.ENDC}")
        
        while True:
            print("\n  1. List Active Threats")
            print("  2. Check Threat Escalation")
            print("  3. View Threat Details")
            print("  4. Manually Create Threat")
            print("  5. Back to Main Menu")
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self._list_threats()
            elif choice == "2":
                self._check_escalation()
            elif choice == "3":
                self._view_threat_details()
            elif choice == "4":
                self._create_threat()
            elif choice == "5":
                break
            else:
                print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
    
    def _list_threats(self):
        """List all active threats"""
        try:
            print("\n⏳ Retrieving threats...")
            session = self.db.get_session()
            
            threats = session.query(Threat)\
                            .filter(Threat.status == 'ACTIVE')\
                            .order_by(Threat.risk_score.desc())\
                            .limit(10)\
                            .all()
            
            session.close()
            
            if not threats:
                print(f"{Colors.WARNING}No active threats found{Colors.ENDC}")
                return
            
            print(f"\n{Colors.OKGREEN}✅ Active Threats:{Colors.ENDC}")
            print(f"{'ID':<5} {'User':<20} {'Pattern':<40} {'Risk':<5}")
            print("-" * 70)
            for threat in threats:
                print(f"{threat.threat_id:<5} {threat.user_id:<20} "
                      f"{threat.threat_pattern:<40} {threat.risk_score:<5}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _check_escalation(self):
        """Check if HIGH severity events triggered threat creation"""
        try:
            print("\n⏳ Checking threat escalation...")
            session = self.db.get_session()
            
            # Check for threats from honeypot hits
            honeypot_threats = session.query(Threat)\
                                      .filter(Threat.user_id.like('HONEYPOT_%'))\
                                      .all()
            
            session.close()
            
            print(f"\n{Colors.OKCYAN}Threat Escalation Status:{Colors.ENDC}")
            print(f"  Honeypot-triggered threats: {len(honeypot_threats)}")
            
            if honeypot_threats:
                print(f"\n{Colors.OKGREEN}✅ Auto-escalation working!{Colors.ENDC}")
                for t in honeypot_threats[:3]:
                    print(f"  - {t.threat_pattern} (Risk: {t.risk_score})")
            else:
                print(f"{Colors.WARNING}ℹ️  No honeypot threats yet (inject events first){Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _view_threat_details(self):
        """Show detailed threat information"""
        try:
            session = self.db.get_session()
            threats = session.query(Threat).limit(10).all()
            session.close()
            
            if not threats:
                print(f"{Colors.WARNING}No threats found{Colors.ENDC}")
                return
            
            print("\nSelect threat to view:")
            for i, threat in enumerate(threats, 1):
                print(f"  {i}. ID {threat.threat_id} - {threat.threat_pattern} (Risk: {threat.risk_score})")
            
            choice = input("\nSelect (number): ").strip()
            try:
                idx = int(choice) - 1
                threat = threats[idx]
                
                print(f"\n{Colors.OKCYAN}Threat Details:{Colors.ENDC}")
                print(f"  ID:           {threat.threat_id}")
                print(f"  User:         {threat.user_id}")
                print(f"  Pattern:      {threat.threat_pattern}")
                print(f"  Risk Score:   {threat.risk_score}")
                print(f"  Event Count:  {threat.event_count}")
                print(f"  Status:       {threat.status}")
                print(f"  First Seen:   {threat.first_seen}")
                print(f"  Last Seen:    {threat.last_seen}")
                if threat.mitre_id:
                    print(f"  MITRE ID:     {threat.mitre_id}")
            except (ValueError, IndexError):
                print(f"{Colors.FAIL}Invalid selection{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _create_threat(self):
        """Manually create a threat for testing"""
        try:
            threat = Threat(
                user_id="TEST_ATTACKER",
                threat_pattern="Test Threat Pattern",
                mitre_id="T1595",
                risk_score=75,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                status="ACTIVE"
            )
            
            session = self.db.get_session()
            session.add(threat)
            session.commit()
            threat_id = threat.threat_id
            session.close()
            
            print(f"{Colors.OKGREEN}✅ Test threat created! ID: {threat_id}{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # 5. Log Retrieval & Analytics
    # ================================
    
    def test_log_analytics(self):
        """Test log retrieval and analytics"""
        print(f"\n{Colors.HEADER}📊 Log Retrieval & Analytics{Colors.ENDC}")
        
        while True:
            print("\n  1. Get All Honeypot Logs")
            print("  2. Filter by Threat Level")
            print("  3. Filter by Attacker IP")
            print("  4. Get Logs by Honeypot ID")
            print("  5. Top Attacked Ports")
            print("  6. Top Attacker IPs")
            print("  7. Back to Main Menu")
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self._get_all_logs()
            elif choice == "2":
                self._filter_by_threat()
            elif choice == "3":
                self._filter_by_attacker()
            elif choice == "4":
                self._filter_by_honeypot()
            elif choice == "5":
                self._top_ports()
            elif choice == "6":
                self._top_attackers()
            elif choice == "7":
                break
            else:
                print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
    
    def _get_all_logs(self):
        """Retrieve all honeypot logs"""
        try:
            print("\n⏳ Retrieving honeypot logs...")
            session = self.db.get_session()
            
            logs = session.query(HoneypotLog)\
                         .order_by(HoneypotLog.event_time.desc())\
                         .limit(20)\
                         .all()
            
            session.close()
            
            if not logs:
                print(f"{Colors.WARNING}No logs found{Colors.ENDC}")
                return
            
            print(f"\n{Colors.OKCYAN}Honeypot Logs (Latest 20):{Colors.ENDC}")
            print(f"{'ID':<5} {'Attacker':<20} {'Port':<6} {'Threat':<8} {'Time':<19}")
            print("-" * 60)
            for log in logs:
                time_str = log.event_time.strftime("%Y-%m-%d %H:%M:%S") if log.event_time else "N/A"
                print(f"{log.id:<5} {log.attacker_ip:<20} {log.target_port:<6} "
                      f"{log.threat_level:<8} {time_str:<19}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _filter_by_threat(self):
        """Filter logs by threat level"""
        try:
            threat_level = input("Threat Level (LOW/MEDIUM/HIGH/CRITICAL): ").strip().upper()
            
            if threat_level not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                print(f"{Colors.FAIL}Invalid threat level{Colors.ENDC}")
                return
            
            print(f"\n⏳ Filtering by {threat_level}...")
            session = self.db.get_session()
            
            logs = session.query(HoneypotLog)\
                         .filter(HoneypotLog.threat_level == threat_level)\
                         .order_by(HoneypotLog.event_time.desc())\
                         .limit(15)\
                         .all()
            
            session.close()
            
            print(f"\n{Colors.OKCYAN}Logs with {threat_level} Threat:{Colors.ENDC}")
            print(f"Found {len(logs)} events\n")
            for log in logs:
                print(f"[{log.id}] {log.attacker_ip}:{log.attacker_port} → Port {log.target_port}")
                if log.commands_executed:
                    print(f"      Commands: {', '.join(log.commands_executed[:3])}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _filter_by_attacker(self):
        """Filter logs by attacker IP"""
        try:
            attacker_ip = input("Attacker IP: ").strip()
            
            print(f"\n⏳ Filtering by {attacker_ip}...")
            session = self.db.get_session()
            
            logs = session.query(HoneypotLog)\
                         .filter(HoneypotLog.attacker_ip == attacker_ip)\
                         .order_by(HoneypotLog.event_time.desc())\
                         .all()
            
            session.close()
            
            print(f"\n{Colors.OKCYAN}Logs from {attacker_ip}:{Colors.ENDC}")
            print(f"Found {len(logs)} events\n")
            
            if logs:
                print(f"{'Port':<6} {'Threat':<8} {'Duration (ms)':<15}")
                print("-" * 30)
                for log in logs:
                    print(f"{log.target_port:<6} {log.threat_level:<8} {log.session_duration_ms:<15}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _filter_by_honeypot(self):
        """Filter logs by honeypot ID"""
        try:
            honeypot_id = input("Honeypot ID: ").strip()
            
            print(f"\n⏳ Filtering by {honeypot_id}...")
            session = self.db.get_session()
            
            logs = session.query(HoneypotLog)\
                         .filter(HoneypotLog.honeypot_id == honeypot_id)\
                         .order_by(HoneypotLog.event_time.desc())\
                         .all()
            
            session.close()
            
            print(f"\n{Colors.OKCYAN}Logs for {honeypot_id}:{Colors.ENDC}")
            print(f"Found {len(logs)} events\n")
            
            if logs:
                print(f"{'Attacker':<20} {'Port':<6} {'Threat':<8}")
                print("-" * 35)
                for log in logs:
                    print(f"{log.attacker_ip:<20} {log.target_port:<6} {log.threat_level:<8}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _top_ports(self):
        """Show top attacked ports"""
        try:
            print("\n⏳ Analyzing ports...")
            session = self.db.get_session()
            
            query = """
                SELECT target_port, COUNT(*) as count
                FROM honeypot_logs
                GROUP BY target_port
                ORDER BY count DESC
                LIMIT 10
            """
            result = session.execute(text(query)).fetchall()
            session.close()
            
            print(f"\n{Colors.OKCYAN}Top Attacked Ports:{Colors.ENDC}")
            print(f"{'Port':<10} {'Attacks':<10}")
            print("-" * 20)
            for port, count in result:
                service = {21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 
                          80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL'}.get(port, 'Other')
                print(f"{port:<10} {count:<10} ({service})")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    def _top_attackers(self):
        """Show top attacker IPs"""
        try:
            print("\n⏳ Analyzing attackers...")
            session = self.db.get_session()
            
            query = """
                SELECT attacker_ip, COUNT(*) as count
                FROM honeypot_logs
                GROUP BY attacker_ip
                ORDER BY count DESC
                LIMIT 10
            """
            result = session.execute(text(query)).fetchall()
            session.close()
            
            print(f"\n{Colors.OKCYAN}Top Attacker IPs:{Colors.ENDC}")
            print(f"{'IP':<20} {'Attacks':<10}")
            print("-" * 30)
            for ip, count in result:
                print(f"{ip:<20} {count:<10}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # 6. System Statistics
    # ================================
    
    def system_statistics(self):
        """Show overall system statistics"""
        print(f"\n{Colors.HEADER}📈 System Statistics{Colors.ENDC}")
        
        try:
            session = self.db.get_session()
            
            # Counts
            users_count = session.query(User).count()
            resources_count = session.query(Resource).count()
            honeypot_logs_count = session.query(HoneypotLog).count()
            threats_count = session.query(Threat).filter(Threat.status == 'ACTIVE').count()
            
            # High threat count
            high_threat = session.query(HoneypotLog)\
                                .filter(HoneypotLog.threat_level.in_(['HIGH', 'CRITICAL']))\
                                .count()
            
            # Unique attackers
            unique_attackers = session.query(HoneypotLog.attacker_ip)\
                                      .distinct()\
                                      .count()
            
            session.close()
            
            print(f"\n{Colors.OKCYAN}System Overview:{Colors.ENDC}")
            print(f"  Users:              {users_count}")
            print(f"  Resources:          {resources_count}")
            print(f"  Honeypot Events:    {honeypot_logs_count}")
            print(f"  High/Critical Hits: {high_threat}")
            print(f"  Active Threats:     {threats_count}")
            print(f"  Unique Attackers:   {unique_attackers}")
            
            if honeypot_logs_count > 0:
                danger_percent = (high_threat / honeypot_logs_count) * 100
                print(f"\n  {Colors.WARNING}⚠️  {danger_percent:.1f}% of events are HIGH/CRITICAL{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # 7. Interactive Demo
    # ================================
    
    def interactive_demo(self):
        """Run an interactive automated demo"""
        print(f"\n{Colors.HEADER}🎬 Interactive Demo{Colors.ENDC}")
        print("\nThis demo will:")
        print("  1. Create sample honeypot events")
        print("  2. Verify database storage")
        print("  3. List threats created")
        print("  4. Show statistics")
        
        if input("\nContinue? (y/n): ").lower() != 'y':
            return
        
        try:
            # Step 1: Create events
            print(f"\n{Colors.BOLD}Step 1: Creating 5 sample honeypot events...{Colors.ENDC}")
            session = self.db.get_session()
            
            events = [
                ("192.168.1.10", 23, "admin", "password", "HIGH"),
                ("10.0.0.5", 22, "root", "admin123", "CRITICAL"),
                ("172.16.0.20", 21, "user", "pass", "MEDIUM"),
                ("192.168.35.1", 3306, "mysql", "mysql", "HIGH"),
                ("203.0.113.5", 110, "mail", "pop3pass", "MEDIUM"),
            ]
            
            for ip, port, user, pwd, threat in events:
                log = HoneypotLog(
                    honeypot_id="ESP32-DEMO",
                    honeypot_name="Demo Server",
                    honeypot_type="multi-service",
                    attacker_ip=ip,
                    attacker_port=54321,
                    target_port=port,
                    username_attempted=user,
                    password_attempted=pwd,
                    commands_executed=[f"login as {user}"],
                    auth_success=False,
                    session_duration_ms=3000,
                    threat_level=threat
                )
                session.add(log)
                print(f"  ✓ {ip}:{port} ({threat})")
            
            session.commit()
            session.close()
            
            # Step 2: Show statistics
            print(f"\n{Colors.BOLD}Step 2: System Statistics{Colors.ENDC}")
            self.system_statistics()
            
            # Step 3: Show threats
            print(f"\n{Colors.BOLD}Step 3: Active Threats{Colors.ENDC}")
            self._list_threats()
            
            # Step 4: Show top attackers
            print(f"\n{Colors.BOLD}Step 4: Top Attacked Ports{Colors.ENDC}")
            self._top_ports()
            
            print(f"\n{Colors.OKGREEN}✅ Demo complete!{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
    
    # ================================
    # Main Event Loop
    # ================================
    
    def run(self):
        """Main test suite runner"""
        try:
            # Initialize database connection
            print("⏳ Initializing database...")
            self.db = GodsEyeDatabase()
            print(f"{Colors.OKGREEN}✅ Database initialized{Colors.ENDC}\n")

            # Explicit note: schema/trigger bootstrap runs during GodsEyeDatabase initialization
            print(f"{Colors.OKGREEN}✅ Schema/tables/triggers ready{Colors.ENDC}\n")

            # Ensure backend.main + API are running for full test suite
            self._check_api_ready(auto_start=True)
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to initialize database: {str(e)}{Colors.ENDC}")
            print("Make sure PostgreSQL is running and configured correctly.")
            return
        
        while True:
            try:
                choice = self.display_main_menu()
                
                if choice == "1":
                    self.test_database()
                elif choice == "2":
                    self.test_honeypot_api()
                elif choice == "3":
                    self.test_event_injection()
                elif choice == "4":
                    self.test_threat_detection()
                elif choice == "5":
                    self.test_log_analytics()
                elif choice == "6":
                    self.system_statistics()
                elif choice == "7":
                    self.interactive_demo()
                elif choice == "8":
                    print(f"\n{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}\n")
                    break
                else:
                    print(f"{Colors.FAIL}Invalid option{Colors.ENDC}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")

        self._cleanup_background_process()


if __name__ == "__main__":
    suite = GodsEyeTestSuite()
    suite.run()
