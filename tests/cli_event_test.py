"""
Interactive CLI Test for Database Event Injection
Allows manual entry of event data for testing with PostgreSQL database
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db_storage import get_db


class InteractiveCLI:
    """Interactive CLI for testing database event injection"""
    
    def __init__(self):
        print("\n🔌 Connecting to database...")
        print("📄 Using credentials from config/db_config.yaml")
        try:
            self.db = get_db()
            print("✅ Connected to PostgreSQL database!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nMake sure:")
            print("  1. PostgreSQL is running")
            print("  2. Database 'godseye' exists")
            print("  3. Credentials in config/db_config.yaml are correct")
            print("  4. Tables are created (run database/setup_postgres.sql)")
            print("  5. Test data exists (run: python tests/seed_database.py)")
            raise
        
        # Load users and resources for selection
        self.users = self.db.get_all_users()
        self.resources = self.db.get_all_resources()
        
        if not self.users or not self.resources:
            print("\n⚠️  Warning: No users or resources found in database!")
            print("Run 'python tests/seed_database.py' to create test data")
        
        self.events_logged = 0
        
        self.events_logged = 0
    
    def list_users(self) -> list:
        """Show available users"""
        print("\n👥 Available Users:")
        for i, user in enumerate(self.users[:10], 1):  # Show first 10
            print(f"  {i}. {user['user_id']} - {user['full_name']} (Level {user['access_level']})")
        if len(self.users) > 10:
            print(f"  ... and {len(self.users) - 10} more")
        return self.users
    
    def list_resources(self, resource_type: Optional[str] = None) -> list:
        """Show available resources"""
        resources = self.resources
        if resource_type:
            resources = [r for r in resources if r['resource_type'] == resource_type]
        
        print(f"\n🏢 Available Resources ({len(resources)}):")
        for i, res in enumerate(resources[:10], 1):  # Show first 10
            sensitive = " [SENSITIVE]" if res.get('is_sensitive') else ""
            print(f"  {i}. {res['resource_id']} - {res['resource_name']} (Level {res['required_access_level']}){sensitive}")
        if len(resources) > 10:
            print(f"  ... and {len(resources) - 10} more")
        return resources
    
    def register_handlers(self):
        """Legacy method - no longer needed"""
        pass
    
    def clear_screen(self):
        """Clear the console screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_input(self, prompt: str, default: Optional[str] = None, required: bool = True) -> Optional[str]:
        """Get user input with optional default"""
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        
        value = input(prompt).strip()
        
        if not value:
            if default:
                return default
            elif required:
                print("⚠️  This field is required!")
                return self.get_input(prompt.rstrip(": "), default, required)
            else:
                return None
        
        return value
    
    def get_choice(self, prompt: str, choices: list) -> str:
        """Get user choice from list"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                choice_num = int(input("\nSelect (number): "))
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print("⚠️  Please enter a valid number")
    
    
    def create_access_event(self) -> dict:
        """Interactive creation of physical access event"""
        print("\n" + "="*80)
        print("📝 Create Physical Access Event (RFID/Card Scan)")
        print("="*80)
        
        # Show physical doors
        doors = [r for r in self.resources if r['resource_type'] == 'physical_door']
        print("\n🚪 Available Doors:")
        for i, door in enumerate(doors, 1):
            print(f"  {i}. {door['resource_id']} - {door['resource_name']} (Level {door['required_access_level']} required)")
        
        # Select resource
        resource_choice = int(self.get_input(f"Select door (1-{len(doors)})", "1")) - 1
        if 0 <= resource_choice < len(doors):
            resource_id = doors[resource_choice]['resource_id']
        else:
            resource_id = self.get_input("Or enter resource_id manually", "door_server_room")
        
        # Show users
        self.list_users()
        user_choice = int(self.get_input(f"Select user (1-{min(10, len(self.users))})", "1")) - 1
        if 0 <= user_choice < len(self.users):
            user_id = self.users[user_choice]['user_id']
        else:
            user_id = self.get_input("Or enter user_id manually", "staff_frank")
        
        # Access Status
        print("\n✅ Access Status:")
        status = self.get_choice("Select status:", [
            "GRANTED",
            "DENIED",
            "FAILED"
        ])
        
        return {
            "user_id": user_id,
            "resource_id": resource_id,
            "access_status": status,
            "event_type": "physical"
        }
    
    
    def create_digital_event(self) -> dict:
        """Interactive creation of digital log event"""
        print("\n" + "="*80)
        print("💻 Create Digital Event (File Access, Process, Login)")
        print("="*80)
        
        # Show digital resources (databases, servers, file systems)
        digital_resources = [r for r in self.resources if r['resource_type'] in ['database', 'server', 'file_system', 'application']]
        print("\n📂 Available Digital Resources:")
        for i, res in enumerate(digital_resources[:15], 1):
            print(f"  {i}. {res['resource_id']} - {res['resource_name']} (Level {res['required_access_level']})")
        
        # Select resource
        resource_choice = int(self.get_input(f"Select resource (1-{min(15, len(digital_resources))})", "1")) - 1
        if 0 <= resource_choice < len(digital_resources):
            resource_id = digital_resources[resource_choice]['resource_id']
        else:
            resource_id = self.get_input("Or enter resource_id manually", "db_production")
        
        # Show users
        self.list_users()
        user_choice = int(self.get_input(f"Select user (1-{min(10, len(self.users))})", "1")) - 1
        if 0 <= user_choice < len(self.users):
            user_id = self.users[user_choice]['user_id']
        else:
            user_id = self.get_input("Or enter user_id manually", "staff_frank")
        
        # Action Type
        print("\n⚡ Action Type:")
        action = self.get_choice("Select action:", [
            "FILE_ACCESS",
            "FILE_WRITE",
            "FILE_DELETE",
            "PROCESS_CREATE",
            "NETWORK_CONNECTION",
            "LOGIN",
            "QUERY_EXECUTION",
            "DATA_EXPORT"
        ])
        
        # Severity
        print("\n🚨 Raw Severity:")
        severity = self.get_choice("Select severity:", [
            "LOW",
            "MEDIUM",
            "HIGH"
        ])
        
        return {
            "user_id": user_id,
            "resource_id": resource_id,
            "action_type": action,
            "raw_severity": severity,
            "event_type": "digital"
        }
    
    def create_honeypot_event(self) -> dict:
        """Create honeypot event (deprecated - kept for compatibility)"""
        print("\n⚠️  Honeypot events not yet implemented in database schema")
        print("Creating a HIGH severity digital event instead...")
        return self.create_digital_event()
    
    
    def create_network_event(self) -> dict:
        """Create network event (deprecated - kept for compatibility)"""
        print("\n⚠️  Network events - creating as digital event...")
        event = self.create_digital_event()
        event['action_type'] = 'NETWORK_CONNECTION'
        return event
    
    def create_endpoint_event(self) -> dict:
        """Create endpoint event (deprecated - kept for compatibility)"""
        print("\n⚠️  Endpoint events - creating as digital event...")
        event = self.create_digital_event()
        return event
    
    def create_teapot_event(self) -> dict:
        """Create teapot/decoy event (deprecated - kept for compatibility)"""
        print("\n⚠️  Teapot events - creating as HIGH severity physical access attempt...")
        event = self.create_access_event()
        event['access_status'] = 'DENIED'
        return event
    
    
    def process_event(self, event_data: dict):
        """Process the event and insert into database"""
        print("\n" + "="*80)
        print("🔄 Processing Event...")
        print("="*80)
        
        # Show event data
        print("\n📦 Event Data:")
        import json
        print(json.dumps(event_data, indent=2))
        
        try:
            # Insert based on event type
            event_id = None
            
            if event_data.get('event_type') == 'physical':
                # Physical access log
                event_id = self.db.log_physical_event(
                    user_id=event_data['user_id'],
                    resource_id=event_data['resource_id'],
                    access_status=event_data['access_status']
                )
                
                if event_id:
                    print(f"\n✅ Physical event logged successfully!")
                    print(f"   Event ID: {event_id}")
                    print(f"   User: {event_data['user_id']}")
                    print(f"   Resource: {event_data['resource_id']}")
                    print(f"   Status: {event_data['access_status']}")
                else:
                    print(f"\n❌ Failed to log physical event!")
                    print(f"   Check logs above for error details")
                    return False
                
            elif event_data.get('event_type') == 'digital':
                # Digital log
                event_id = self.db.log_digital_event(
                    user_id=event_data['user_id'],
                    resource_id=event_data['resource_id'],
                    action_type=event_data['action_type'],
                    raw_severity=event_data['raw_severity']
                )
                
                if event_id:
                    print(f"\n✅ Digital event logged successfully!")
                    print(f"   Event ID: {event_id}")
                    print(f"   User: {event_data['user_id']}")
                    print(f"   Resource: {event_data['resource_id']}")
                    print(f"   Action: {event_data['action_type']}")
                    print(f"   Severity: {event_data['raw_severity']}")
                else:
                    print(f"\n❌ Failed to log digital event!")
                    print(f"   Check logs above for error details")
                    return False
            
            else:
                print(f"\n❌ Unknown event type: {event_data.get('event_type')}")
                return False
            
            self.events_logged += 1
            
            # Check if triggers created threat
            if event_data.get('event_type') == 'physical' and event_data['access_status'] == 'DENIED':
                print("\n🚨 HIGH severity event - checking for threat detection...")
                threats = self.db.get_threat_by_user(event_data['user_id'], status='ACTIVE')
                if threats:
                    print(f"   ⚠️  ACTIVE threat detected!")
                    print(f"   Risk Score: {threats[0]['risk_score']}")
                    print(f"   Event Count: {threats[0]['event_count']}")
            
            elif event_data.get('event_type') == 'digital' and event_data['raw_severity'] == 'HIGH':
                print("\n🚨 HIGH severity event - checking for threat detection...")
                threats = self.db.get_threat_by_user(event_data['user_id'], status='ACTIVE')
                if threats:
                    print(f"   ⚠️  ACTIVE threat detected!")
                    print(f"   Risk Score: {threats[0]['risk_score']}")
                    print(f"   Event Count: {threats[0]['event_count']}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Event processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def main_menu(self):
        """Display main menu and handle user choice"""
        while True:
            print("\n" + "="*80)
            print("🔵 GodsEye Database Event Injection - Interactive CLI")
            print("="*80)
            print("\nSelect event type to create:")
            print("  1. 📱 Physical Access Event (RFID/Door)")
            print("  2. 💻 Digital Event (File/Process/Login)")
            print("  3. 🍯 Honeypot Event (creates digital)")
            print("  4. 🌐 Network Event (creates digital)")
            print("  5. 🖥️  Endpoint Event (creates digital)")
            print("  6. 🫖 Teapot Event (creates physical denied)")
            print("  7. 📊 Show Database Statistics")
            print("  8. 👥 List Users")
            print("  9. 🏢 List Resources")
            print("  0. 🚪 Exit")
            
            try:
                choice = input("\nEnter choice (0-9): ").strip()
                
                if choice == "1":
                    event = self.create_access_event()
                    self.process_event(event)
                
                elif choice == "2":
                    event = self.create_digital_event()
                    self.process_event(event)
                
                elif choice == "3":
                    event = self.create_honeypot_event()
                    self.process_event(event)
                
                elif choice == "4":
                    event = self.create_network_event()
                    self.process_event(event)
                
                elif choice == "5":
                    event = self.create_endpoint_event()
                    self.process_event(event)
                
                elif choice == "6":
                    event = self.create_teapot_event()
                    self.process_event(event)
                
                elif choice == "7":
                    self.show_statistics()
                
                elif choice == "8":
                    self.list_users()
                
                elif choice == "9":
                    self.list_resources()
                
                elif choice == "0":
                    print("\n👋 Goodbye!")
                    break
                
                else:
                    print("\n⚠️  Invalid choice. Please enter 0-9.")
                
                input("\nPress Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")
    
    
    def show_statistics(self):
        """Show database statistics"""
        print("\n" + "="*80)
        print("📊 GodsEye Database Statistics")
        print("="*80)
        
        try:
            stats = self.db.get_statistics()
            
            print(f"\n📦 Data Overview:")
            print(f"   Users: {stats.get('users', {}).get('total', 0)}")
            print(f"   Resources: {stats.get('resources', {}).get('total', 0)}")
            print(f"   Physical Events: {stats.get('events', {}).get('physical_total', 0)}")
            print(f"   Digital Events: {stats.get('events', {}).get('digital_total', 0)}")
            print(f"   Unified Logs: {stats.get('events', {}).get('main_total', 0)}")
            print(f"   Active Threats: {stats.get('threats', {}).get('active', 0)}")
            
            print(f"\n📈 Last 24 Hours:")
            print(f"   Physical Events: {stats.get('events', {}).get('physical_24h', 0)}")
            print(f"   Digital Events: {stats.get('events', {}).get('digital_24h', 0)}")
            print(f"   HIGH Severity: {stats.get('events', {}).get('high_severity_24h', 0)}")
            
            print(f"\n🔥 Active Threats:")
            threats = self.db.get_threats(status='ACTIVE', limit=5)
            if threats:
                for threat in threats:
                    print(f"   • {threat['user_id']}: Risk {threat['risk_score']} ({threat['event_count']} events)")
            else:
                print(f"   ✅ No active threats")
            
            print(f"\n📊 Session Statistics:")
            print(f"   Events Logged This Session: {self.events_logged}")
            
        except Exception as e:
            print(f"\n❌ Error getting statistics: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Entry point"""
    try:
        cli = InteractiveCLI()
        
        print("\n" + "="*80)
        print("🔵 Welcome to GodsEye Database Event Injection CLI")
        print("="*80)
        print("\nThis tool allows you to manually create and inject events into the database.")
        print("Events will trigger automated threat detection via PostgreSQL triggers.")
        print("\n✅ Database: Connected")
        print(f"✅ Users: {len(cli.users)} available")
        print(f"✅ Resources: {len(cli.resources)} available")
        print("\nPress Ctrl+C at any time to exit.")
        print("="*80)
        
        input("\nPress Enter to start...")
        
        cli.main_menu()
        
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'godseye' exists")
        print("  3. config/db_config.yaml has correct credentials")
        print("  4. Tables are created (run: psql -U postgres -f database/setup_postgres.sql)")
        print("  5. Test data exists (run: python tests/seed_database.py)")


if __name__ == "__main__":
    main()
