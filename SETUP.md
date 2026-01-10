# Setup Instructions for GodsEye

## Phase 0 & 1: Backend Foundation Setup

### Prerequisites
1. **Python 3.10+** installed
2. **Git** installed
3. **Linux / WSL** (recommended) or Windows PowerShell

### Installation Steps

#### 1. Clone Repository (if not already done)
```bash
git clone https://github.com/VeNoM-hubs/GodsEye.git
cd GodsEye
```

#### 2. Create Virtual Environment
```bash
# On Linux/WSL/Mac
python3 -m venv venv
source venv/bin/activate

# On Windows PowerShell
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation
```bash
python -c "import pydantic, paho.mqtt, sklearn; print('✓ All dependencies installed')"
```

### Running the Backend

#### Option 1: Run Demo Scenarios
```bash
python tests/test_backend.py
```

This will run 6 demo scenarios:
- Scenario 1: Multiple failed access attempts (brute force)
- Scenario 2: Attacker interaction with honeypot
- Scenario 3: Decoy credential used (teapot)
- Scenario 4: Access attempt at abnormal hour
- Scenario 5: Network anomaly with high score
- Scenario 6: Suspicious endpoint activity

#### Option 2: Run Unit Tests
```bash
pytest tests/test_backend.py -v
```

#### Option 3: Start Backend Service
```bash
python backend/main.py
```

### Verify Setup

After running the demo scenarios, you should see:
- ✅ Console alerts for detected threats
- ✅ Log files created in `logs/` directory
- ✅ Events stored in `logs/events/`
- ✅ Alerts stored in `logs/alerts/`

### Project Structure Created
```
GodsEye/
├── backend/
│   ├── __init__.py
│   ├── schemas.py          # Event schemas (NEVER changes)
│   ├── config.py           # Configuration management
│   ├── event_receiver.py   # Event validation & routing
│   ├── anomaly_detection.py # Rule-based detection
│   ├── alert_engine.py     # Alert generation
│   ├── storage.py          # Event/alert storage
│   └── main.py            # Main application
├── config/
│   └── config.yaml        # System configuration
├── logs/                  # Storage directory (auto-created)
├── tests/
│   └── test_backend.py    # Test suite with fake data
├── requirements.txt
├── README.md
└── ROADMAP.md

```

### Configuration

Edit `config/config.yaml` to customize:
- MQTT broker settings
- Alert thresholds
- Access control rules
- Decoy credentials (teapots)
- Storage settings

### Next Steps (Phase 2)

Once backend is verified:
1. Install Mosquitto MQTT broker
2. Create simulated IoT devices
3. Implement MQTT communication

See ROADMAP.md for detailed implementation plan.

### Troubleshooting

**ImportError: No module named 'pydantic'**
```bash
pip install -r requirements.txt
```

**Permission denied errors**
```bash
chmod +x tests/test_backend.py
```

**YAML parsing errors**
```bash
pip install pyyaml --upgrade
```

### Development Tips

- Use `pytest` for testing during development
- Check logs in `logs/` directory for debugging
- Modify `config/config.yaml` for different scenarios
- Add custom rules in `backend/anomaly_detection.py`
