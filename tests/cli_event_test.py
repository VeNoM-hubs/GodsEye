"""
Interactive CLI Test for Event Receiver
Allows manual entry of event data for testing
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.event_receiver import EventReceiver


class InteractiveCLI:
    """Interactive CLI for testing event receiver"""
    
    def __init__(self):
        self.receiver = EventReceiver()
        self.register_handlers()
    
    def register_handlers(self):
        """Register simple handlers for demonstration"""
        def handler(event):
            print(f"\n✅ Event processed successfully!")
            print(f"   Event ID: {event.event_id}")
            print(f"   Type: {event.event_type}")
        
        from backend.schemas import EventType
        for event_type in EventType:
            self.receiver.register_handler(event_type, handler)
    
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
        """Interactive creation of access event"""
        print("\n" + "="*80)
        print("📝 Create Access Event")
        print("="*80)
        
        event = {
            "event_type": "access",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Device Information
        print("\n🔧 Device Information:")
        event["device_id"] = self.get_input("Device ID", "access_door_01")
        event["location"] = self.get_input("Location", "Server Room A")
        
        # Access Method
        print("\n🔐 Access Method:")
        method = self.get_choice("Select access method:", [
            "rfid",
            "fingerprint",
            "rfid_fingerprint"
        ])
        event["access_method"] = method
        
        # Credentials
        print("\n🎫 Credentials:")
        if method in ["rfid", "rfid_fingerprint"]:
            event["card_id"] = self.get_input("Card ID", "CARD_12345")
        
        if method in ["fingerprint", "rfid_fingerprint"]:
            event["fingerprint_id"] = self.get_input("Fingerprint ID", "FP_USER_001")
        
        # User ID (optional)
        user_id = self.get_input("User ID (optional, press Enter to skip)", required=False)
        if user_id:
            event["user_id"] = user_id
        
        # Status
        print("\n✅ Access Status:")
        status = self.get_choice("Select status:", [
            "success",
            "failed",
            "denied",
            "anomaly"
        ])
        event["status"] = status
        
        # Failure reason (if failed/denied)
        if status in ["failed", "denied"]:
            reason = self.get_input("Failure reason", "Invalid credentials", required=False)
            if reason:
                event["failure_reason"] = reason
        
        return event
    
    def create_honeypot_event(self) -> dict:
        """Interactive creation of honeypot event"""
        print("\n" + "="*80)
        print("🍯 Create Honeypot Event")
        print("="*80)
        
        event = {
            "event_type": "honeypot",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Honeypot Information
        print("\n🎯 Honeypot Information:")
        event["honeypot_id"] = self.get_input("Honeypot ID", "hp_plc_001")
        
        honeypot_type = self.get_choice("Select honeypot type:", [
            "fake_plc",
            "fake_access",
            "fake_iot"
        ])
        event["honeypot_type"] = honeypot_type
        
        # Attacker Information
        print("\n👤 Attacker Information:")
        event["source_ip"] = self.get_input("Source IP", "192.168.1.100")
        
        port = self.get_input("Source Port (optional, press Enter to skip)", required=False)
        if port:
            event["source_port"] = int(port)
        
        # Interaction Details
        print("\n⚡ Interaction Details:")
        interaction = self.get_choice("Select interaction type:", [
            "connection",
            "authentication",
            "command",
            "data_access"
        ])
        event["interaction_type"] = interaction
        
        payload = self.get_input("Payload/Command (optional)", "MODBUS_READ_COILS", required=False)
        if payload:
            event["payload"] = payload
        
        protocol = self.get_input("Protocol (optional)", "modbus", required=False)
        if protocol:
            event["protocol"] = protocol
        
        return event
    
    def create_network_event(self) -> dict:
        """Interactive creation of network event"""
        print("\n" + "="*80)
        print("🌐 Create Network Event")
        print("="*80)
        
        event = {
            "event_type": "network",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Network Event Type
        print("\n📊 Event Type:")
        net_type = self.get_choice("Select network event type:", [
            "suspicious_connection",
            "port_scan",
            "traffic_spike",
            "unknown_device",
            "protocol_anomaly"
        ])
        event["network_event_type"] = net_type
        
        # Network Details
        print("\n🔌 Network Details:")
        event["source_ip"] = self.get_input("Source IP", "10.0.0.50")
        event["destination_ip"] = self.get_input("Destination IP", "10.0.0.100")
        event["protocol"] = self.get_input("Protocol", "modbus")
        
        # Ports (optional)
        src_port = self.get_input("Source Port (optional)", "44512", required=False)
        if src_port:
            event["source_port"] = int(src_port)
        
        dst_port = self.get_input("Destination Port (optional)", "502", required=False)
        if dst_port:
            event["destination_port"] = int(dst_port)
        
        # Traffic Information (optional)
        print("\n📈 Traffic Information (optional, press Enter to skip):")
        packets = self.get_input("Packet count", required=False)
        if packets:
            event["packet_count"] = int(packets)
        
        bytes_count = self.get_input("Byte count", required=False)
        if bytes_count:
            event["byte_count"] = int(bytes_count)
        
        # Anomaly Score
        score = self.get_input("Anomaly score (0.0-1.0)", "0.85", required=False)
        if score:
            event["anomaly_score"] = float(score)
        
        description = self.get_input("Description (optional)", required=False)
        if description:
            event["description"] = description
        
        return event
    
    def create_endpoint_event(self) -> dict:
        """Interactive creation of endpoint event"""
        print("\n" + "="*80)
        print("💻 Create Endpoint Event")
        print("="*80)
        
        event = {
            "event_type": "endpoint",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Endpoint Information
        print("\n🖥️  Endpoint Information:")
        event["hostname"] = self.get_input("Hostname", "ICS-WORKSTATION-01")
        event["endpoint_id"] = self.get_input("Endpoint ID", "endpoint_001")
        event["operating_system"] = self.get_input("Operating System", "Windows 10")
        
        # Event Type
        print("\n📋 Event Type:")
        ep_type = self.get_choice("Select endpoint event type:", [
            "process_creation",
            "network_connection",
            "file_creation",
            "registry_modification",
            "privilege_escalation"
        ])
        event["endpoint_event_type"] = ep_type
        
        # Process Information (optional)
        print("\n⚙️  Process Information (optional, press Enter to skip):")
        process = self.get_input("Process name", "powershell.exe", required=False)
        if process:
            event["process_name"] = process
        
        pid = self.get_input("Process ID", required=False)
        if pid:
            event["process_id"] = int(pid)
        
        parent = self.get_input("Parent process", required=False)
        if parent:
            event["parent_process"] = parent
        
        cmdline = self.get_input("Command line", required=False)
        if cmdline:
            event["command_line"] = cmdline
        
        user = self.get_input("User", required=False)
        if user:
            event["user"] = user
        
        # Severity
        print("\n🚨 Severity:")
        severity = self.get_choice("Select severity:", [
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL"
        ])
        event["severity"] = severity
        
        description = self.get_input("Description (optional)", required=False)
        if description:
            event["description"] = description
        
        return event
    
    def create_teapot_event(self) -> dict:
        """Interactive creation of teapot event"""
        print("\n" + "="*80)
        print("🫖 Create Teapot Event (Decoy Credential)")
        print("="*80)
        
        event = {
            "event_type": "teapot",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Decoy Information
        print("\n🎭 Decoy Information:")
        decoy_type = self.get_choice("Select decoy type:", [
            "fake_card",
            "fake_fingerprint",
            "fake_user"
        ])
        event["decoy_type"] = decoy_type
        
        event["decoy_id"] = self.get_input("Decoy ID", "FAKE_CARD_001")
        
        # Usage Information (optional)
        print("\n📍 Usage Information (optional, press Enter to skip):")
        device = self.get_input("Device ID", required=False)
        if device:
            event["device_id"] = device
        
        ip = self.get_input("Source IP", required=False)
        if ip:
            event["source_ip"] = ip
        
        location = self.get_input("Location", required=False)
        if location:
            event["location"] = location
        
        return event
    
    def process_event(self, event_data: dict):
        """Process the event and show results"""
        print("\n" + "="*80)
        print("🔄 Processing Event...")
        print("="*80)
        
        # Show event data
        print("\n📦 Event Data:")
        import json
        print(json.dumps(event_data, indent=2))
        
        # Process event
        result = self.receiver.process_event(event_data)
        
        if not result:
            print("\n❌ Event processing failed!")
        
        # Show statistics
        print("\n📊 Receiver Statistics:")
        stats = self.receiver.get_statistics()
        print(f"   Total Received: {stats['total_received']}")
        print(f"   Total Processed: {stats['total_processed']}")
        print(f"   Total Errors: {stats['total_errors']}")
        print(f"   Success Rate: {stats['success_rate']:.2%}")
    
    def main_menu(self):
        """Display main menu and handle user choice"""
        while True:
            print("\n" + "="*80)
            print("🔵 GodsEye Event Receiver - Interactive CLI")
            print("="*80)
            print("\nSelect event type to create:")
            print("  1. 📱 Access Event (RFID/Fingerprint)")
            print("  2. 🍯 Honeypot Event")
            print("  3. 🌐 Network Event")
            print("  4. 💻 Endpoint Event (Sysmon/Wazuh)")
            print("  5. 🫖 Teapot Event (Decoy Credential)")
            print("  6. 📊 Show Statistics")
            print("  7. 🔄 Reset Statistics")
            print("  8. 🚪 Exit")
            
            try:
                choice = input("\nEnter choice (1-8): ").strip()
                
                if choice == "1":
                    event = self.create_access_event()
                    self.process_event(event)
                
                elif choice == "2":
                    event = self.create_honeypot_event()
                    self.process_event(event)
                
                elif choice == "3":
                    event = self.create_network_event()
                    self.process_event(event)
                
                elif choice == "4":
                    event = self.create_endpoint_event()
                    self.process_event(event)
                
                elif choice == "5":
                    event = self.create_teapot_event()
                    self.process_event(event)
                
                elif choice == "6":
                    self.show_statistics()
                
                elif choice == "7":
                    self.receiver.reset_statistics()
                    print("\n✅ Statistics reset successfully!")
                
                elif choice == "8":
                    print("\n👋 Goodbye!")
                    break
                
                else:
                    print("\n⚠️  Invalid choice. Please enter 1-8.")
                
                input("\nPress Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
    
    def show_statistics(self):
        """Show detailed statistics"""
        print("\n" + "="*80)
        print("📊 Event Receiver Statistics")
        print("="*80)
        
        stats = self.receiver.get_statistics()
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Received:  {stats['total_received']}")
        print(f"   Total Processed: {stats['total_processed']}")
        print(f"   Total Errors:    {stats['total_errors']}")
        print(f"   Success Rate:    {stats['success_rate']:.2%}")
        
        if stats['by_type']:
            print(f"\n📋 Events by Type:")
            for event_type, count in stats['by_type'].items():
                print(f"   {event_type}: {count}")


def main():
    """Entry point"""
    cli = InteractiveCLI()
    
    print("\n" + "="*80)
    print("🔵 Welcome to GodsEye Event Receiver Interactive CLI")
    print("="*80)
    print("\nThis tool allows you to manually create and test events.")
    print("You'll be prompted for each field required by the event type.")
    print("\nPress Ctrl+C at any time to exit.")
    print("="*80)
    
    input("\nPress Enter to start...")
    
    cli.main_menu()


if __name__ == "__main__":
    main()
