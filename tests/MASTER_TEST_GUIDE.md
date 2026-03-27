# Master Test Suite - Quick Start Guide

## Overview

The master test suite provides an interactive CLI for testing all GodsEye components:
- ✅ Database connectivity and schema
- ✅ Honeypot API endpoints
- ✅ Event injection (honeypot, physical, digital)
- ✅ Automatic threat detection
- ✅ Log retrieval and analytics
- ✅ System statistics
- ✅ Automated demo mode

## Prerequisites

1. **PostgreSQL running** with GodsEye database
2. **FastAPI server running** (for API tests):
   ```bash
   python -m backend.api_server
   ```
3. **Python dependencies installed** (already have from project setup)

## Running the Test Suite

### Start the Master Test Suite

```bash
cd c:\Users\lukra_mj9bmma\GodsEye
python tests/master_test.py
```

### Expected Output

```
======================================================================
🔍 GodsEye Master Test Suite
======================================================================

Main Menu:
  1. Database Tests
  2. Honeypot API Tests
  3. Event Injection Tests
  4. Threat Detection Tests
  5. Log Retrieval & Analytics
  6. System Statistics
  7. Interactive Demo
  8. Exit

Select option (1-8):
```

## Test Sections

### 1. Database Tests
- **Test Connection** - Verify PostgreSQL connectivity
- **Verify Tables** - Check all 8 tables exist
- **Check Row Counts** - See how many records in each table
- **Inspect Schema** - Show honeypot_logs column definitions

**What to expect:**
```
✅ Database connected successfully!
   Host: localhost
   Port: 5432
   Database: godseye
   User: postgres
```

### 2. Honeypot API Tests
- **Test Health Endpoint** - Verify API server is running
- **Test POST /honeypot/log** - Submit honeypot event
- **Test GET /honeypot/logs** - Retrieve stored logs
- **Test GET /honeypot/stats** - Get honeypot statistics
- **Submit Test Event** - Create custom honeypot event

**Requirements:**
- FastAPI server must be running on `http://localhost:8000`

**Example event submission:**
```json
{
  "honeypot_id": "ESP32-ABC123",
  "honeypot_name": "Telnet Server",
  "honeypot_type": "multi-service",
  "attacker_ip": "192.168.1.5",
  "attacker_port": 54321,
  "target_port": 23,
  "threat_level": "HIGH"
}
```

### 3. Event Injection Tests
- **Inject Honeypot Event (Direct DB)** - Write directly to honeypot_logs table
- **Inject Physical Access Event** - Create door/RFID access log
- **Inject Digital Event** - Create file/process access log
- **Verify Events** - Show recent events from all tables

**What happens:**
1. Honeypot event injected → stored in `honeypot_logs`
2. Database trigger → creates automatic threat in `threats` table
3. Threat escalation → risk_score calculated

### 4. Threat Detection Tests
- **List Active Threats** - Show all ACTIVE threats
- **Check Threat Escalation** - Verify auto-escalation working
- **View Threat Details** - Select threat to see full info
- **Manually Create Threat** - Create test threat

**What to expect:**
```
Active Threats:
ID   User                Pattern                              Risk
100  HONEYPOT_ESP32-ABC  Honeypot Interaction on port 23     80
101  TEST_ATTACKER       Test Threat Pattern                 75
```

### 5. Log Retrieval & Analytics
- **Get All Honeypot Logs** - Show latest 20 events
- **Filter by Threat Level** - Query by LOW/MEDIUM/HIGH/CRITICAL
- **Filter by Attacker IP** - See all attacks from one IP
- **Get Logs by Honeypot ID** - Query by honeypot device
- **Top Attacked Ports** - Show port statistics (FTP, SSH, etc)
- **Top Attacker IPs** - Show which IPs attacked most

**Example output:**
```
Top Attacked Ports:
Port       Attacks
23         5           (Telnet)
22         3           (SSH)
3306       2           (MySQL)

Top Attacker IPs:
IP                   Attacks
192.168.1.5          5
10.0.0.1             3
172.16.0.20          2
```

### 6. System Statistics
Shows overall system health:
```
Users:              17
Resources:          31
Honeypot Events:    42
High/Critical Hits: 12
Active Threats:     8
Unique Attackers:   6

⚠️  28.6% of events are HIGH/CRITICAL
```

### 7. Interactive Demo
Automated full-cycle test that:
1. Creates 5 sample honeypot events (different attackers/ports)
2. Shows system statistics
3. Lists created threats
4. Displays top attacked ports
5. Verifies everything integrated

**Perfect for seeing the full system in action!**

## Test Workflow Recommendations

### First Time Setup
```
1. Database Tests → Test Connection
2. Database Tests → Verify Tables
3. Database Tests → Check Row Counts
4. Honeypot API Tests → Test Health Endpoint
5. Event Injection Tests → Inject Honeypot Event
6. Threat Detection Tests → List Active Threats
7. System Statistics
```

### API Integration Testing
```
1. Start FastAPI server in terminal
2. Honeypot API Tests → Test POST /honeypot/log
3. Honeypot API Tests → Submit Test Event
4. Honeypot API Tests → Test GET /honeypot/logs
5. Log Retrieval → Get All Honeypot Logs
```

### End-to-End Testing
```
1. Event Injection → Inject Honeypot Event
2. Threat Detection → Check Threat Escalation
3. Threat Detection → List Active Threats
4. Log Retrieval → Filter by Threat Level (HIGH)
5. System Statistics
```

### Full Demo
```
1. Interactive Demo
   (Runs all steps automatically)
```

## Troubleshooting

### Database Connection Error
```
❌ Connection failed: could not connect to server
```
**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1;"

# If failed, start PostgreSQL
# Windows: Use Services app or pgAdmin
```

### API Server Not Found
```
❌ API Server not reachable at http://localhost:8000
```
**Solution:**
```bash
# Start API server in another terminal
python -m backend.api_server
```

### No Honeypot Logs Table
```
❌ Error: relation "honeypot_logs" does not exist
```
**Solution:**
```bash
# Re-run database setup
psql -U postgres -d godseye -f database/setup_postgres.sql
```

### No Users/Resources Found
```
⚠️  No users or resources found. Run seed_database.py first.
```
**Solution:**
```bash
# Seed database with test data
python tests/seed_database.py
```

## Color Key

- 🟢 **GREEN** `✅` - Success/Working
- 🔵 **BLUE** - Information/Menu
- 🟡 **YELLOW** `⚠️` - Warning/Info
- 🔴 **RED** `❌` - Error/Failed

## Sample Test Session Transcript

```
======================================================================
🔍 GodsEye Master Test Suite
======================================================================

Main Menu:
  1. Database Tests
  ...
  8. Exit

Select option (1-8): 1

🔌 Database Tests

  1. Test Connection
  ...

Select option (1-5): 1

⏳ Testing PostgreSQL connection...
✅ Database connected successfully!
   Host: localhost
   Port: 5432
   Database: godseye
   User: postgres

Main Menu:
  ...

Select option (1-8): 7

🎬 Interactive Demo

This demo will:
  1. Create sample honeypot events
  2. Verify database storage
  3. List threats created
  4. Show statistics

Continue? (y/n): y

Step 1: Creating 5 sample honeypot events...
  ✓ 192.168.1.10:23 (HIGH)
  ✓ 10.0.0.5:22 (CRITICAL)
  ✓ 172.16.0.20:21 (MEDIUM)
  ✓ 192.168.35.1:3306 (HIGH)
  ✓ 203.0.113.5:110 (MEDIUM)

Step 2: System Statistics
Users:              17
Resources:          31
Honeypot Events:    10
...

✅ Demo complete!
```

## Advanced Usage

### Testing API Payload Validation

The test suite validates all incoming honeypot events. You can test:
- Missing required fields
- Invalid threat levels
- Malformed JSON
- Connection timeouts

### Batch Event Injection

For load testing:
```python
# Modify master_test.py to create 100+ events in a loop
# Good for testing performance and scalability
```

### Custom SQL Queries

The test suite gives you SQL query capabilities:
```
Database Tests → (You can add custom queries here)
```

## Integration with CI/CD

The test suite can be run non-interactively:
```bash
# Future: Add pytest integration
# Currently interactive only, but easily adaptable
```

## Next Steps

After successful testing:
1. ✅ Deploy ESP32 honeypot with webhook URL
2. ✅ Monitor attacks in real-time
3. ✅ Create Grafana dashboard for visualization
4. ✅ Set up email alerts for HIGH/CRITICAL threats
5. ✅ Analyze attacker patterns with MITRE framework

## Support

For issues or questions:
1. Check error messages in test output
2. Verify prerequisites (PostgreSQL, API server)
3. Review database schema: `\d honeypot_logs`
4. Check API health: `curl http://localhost:8000/health`
