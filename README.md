# GodsEye

**AI-Driven IoT Network for Cyber-Physical Threat, Access Anomaly, and Endpoint Activity Detection in Industrial Control Systems**

## Overview
GodsEye is a comprehensive security system that combines physical IoT sensors, network monitoring, endpoint telemetry, and AI analysis to protect industrial infrastructure from both cyber and physical threats.

## Sustainable Development Goals
- **SDG 9**: Industry, Innovation, and Infrastructure (primary)
- **SDG 11**: Sustainable Cities and Communities
- **SDG 16**: Peace, Justice, and Strong Institutions

## Key Features
- **Physical Access Control**: RFID + Fingerprint authentication
- **IoT Communication**: MQTT-based messaging
- **Deception Layer**: Honeypots & Teapots
- **Endpoint Monitoring**: Sysmon + Wazuh integration
- **AI Detection**: Rule-based + Machine Learning anomaly detection
- **Real-time Correlation**: Cross-source threat intelligence

## Technology Stack
- **Backend**: Python 3.10+
- **IoT Protocol**: MQTT (Mosquitto)
- **Hardware**: ESP32, RFID readers, Fingerprint sensors
- **Monitoring**: Sysmon, Wazuh
- **AI/ML**: scikit-learn, Isolation Forest
- **Storage**: JSON logs (PostgreSQL planned)

## Project Status
🚧 **In Development** - Following 45-day implementation roadmap

## Setup Instructions

### Prerequisites
- Python 3.10+
- Linux / WSL
- Git
- MQTT Broker (Mosquitto)

### Installation
```bash
# Clone repository
git clone https://github.com/VeNoM-hubs/GodsEye.git
cd GodsEye

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure
```
GodsEye/
├── backend/           # Python backend services
├── iot/              # IoT device code (ESP32, sensors)
├── monitoring/       # Sysmon & Wazuh configurations
├── honeypots/        # Honeypot implementations
├── ml_models/        # AI/ML anomaly detection
├── dashboard/        # Web dashboard
├── tests/            # Test suites
├── logs/             # System logs
└── config/           # Configuration files
```

## Implementation Roadmap
See [ROADMAP.md](ROADMAP.md) for detailed 45-day implementation plan.

## License
MIT License

## Contributors
- VeNoM-hubs (Project Lead)
