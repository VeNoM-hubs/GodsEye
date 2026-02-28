# GodsEye Database Documentation

## Overview

GodsEye uses **PostgreSQL** with automated threat detection via database triggers. Events flow through three layers:

1. **Physical/Digital Logs** → Raw events from RFID, biometrics, Sysmon, Wazuh
2. **Main Logs** → Unified view with severity scoring (automatically populated by triggers)
3. **Threats** → Detected attack patterns with risk scores (automatically created by triggers)

## Database Schema

### Core Tables

#### `users`
User account information with access levels (1-10)
```sql
user_id (PK) | full_name | role | access_level | is_active
```

#### `resources`
Protected resources (doors, servers, databases, files)
```sql
resource_id (PK) | resource_name | resource_type | required_access_level | is_sensitive
```

#### `physical_logs`
Physical access events (RFID cards, fingerprints, door sensors)
```sql
id (PK) | user_id (FK) | resource_id (FK) | access_status | event_time
```

#### `digital_logs`
Digital events (Sysmon, Wazuh, endpoint activity)
```sql
id (PK) | user_id (FK) | resource_id (FK) | action_type | raw_severity | event_time
```

#### `main_logs`
Unified log view (auto-populated by triggers)
```sql
id (PK) | source | source_ref_id | user_id (FK) | resource_id (FK) | 
event_type | severity | event_time | correlation_flag
```

#### `threats`
Detected threats (auto-created by triggers)
```sql
threat_id (PK) | user_id (FK) | threat_pattern | mitre_id (FK) | 
risk_score | first_seen | last_seen | event_count | status
```

#### `mitre_techniques`
MITRE ATT&CK framework mapping
```sql
technique_id (PK) | technique_name | tactic
```

## Automated Detection

### Trigger 1: Physical → Main
When you insert into `physical_logs`:
- **Calculates severity** based on user access level vs. resource requirements
- **AUTO inserts** into `main_logs`
- **HIGH severity** if denied or insufficient access level

### Trigger 2: Digital → Main
When you insert into `digital_logs`:
- **Maps severity** from raw_severity (HIGH/MEDIUM/LOW)
- **AUTO inserts** into `main_logs`

### Trigger 3: Main → Threat
When HIGH severity event is inserted into `main_logs`:
- **Checks for existing threats** for that user (last 10 minutes)
- **Updates existing threat**: increments risk_score +10, event_count +1
- **Creates new threat**: risk_score=70, MITRE T1078 (Valid Accounts)
- **Sets correlation_flag** = TRUE in main_logs

## Quick Start

### 1. Setup Database
```powershell
# Connect to PostgreSQL
psql -U postgres

# Run setup script
\i database/setup_postgres.sql

# Exit
\q
```

### 2. Seed Initial Data
```powershell
python tests/seed_database.py
```
This creates:
- 20 MITRE ATT&CK techniques
- 17 users (admins, engineers, analysts, contractors)
- 31 resources (doors, databases, servers, files)

### 3. Test System
```powershell
python tests/test_database.py
```
Runs comprehensive tests:
- Logs physical access events
- Logs digital activity
- Verifies threat detection
- Tests analytics

### 4. View Status
```powershell
python tests/demo_database.py
```
Shows:
- Current statistics
- Active threats
- High severity events
- Top users/resources

## Python API Usage

### Connect to Database
```python
from backend.db_storage import get_db

db = get_db(
    db_host="localhost",
    db_port=5432,
    db_name="godseye",
    db_user="godseye",
    db_password="your_password"
)
```

### Add Users
```python
db.add_user(
    user_id="john_doe",
    full_name="John Doe",
    role="admin",
    access_level=10
)
```

### Add Resources
```python
db.add_resource(
    resource_id="door_server_room",
    resource_name="Server Room Door",
    resource_type="physical_door",
    required_access_level=8,
    is_sensitive=True
)
```

### Log Physical Access
```python
# Triggers will automatically:
# 1. Calculate severity
# 2. Insert to main_logs
# 3. Detect threats if HIGH severity

event_id = db.log_physical_event(
    user_id="john_doe",
    resource_id="door_server_room",
    access_status="GRANTED"  # or DENIED, FAILED
)
```

### Log Digital Activity
```python
event_id = db.log_digital_event(
    user_id="alice_smith",
    resource_id="db_production",
    action_type="UNAUTHORIZED_ACCESS",
    raw_severity="HIGH"  # or MEDIUM, LOW
)
```

### Query Main Logs
```python
# Get all HIGH severity events
high_sev = db.get_high_severity_events(hours=24, limit=100)

# Filter by user
user_logs = db.get_main_logs(user_id="john_doe", limit=50)

# Filter by severity and time
from datetime import datetime, timedelta
start = datetime.utcnow() - timedelta(hours=1)
recent = db.get_main_logs(severity="HIGH", start_time=start)
```

### Check Threats
```python
# Get active threats
threats = db.get_threats(status='ACTIVE', limit=100)

# Get threats for specific user
user_threats = db.get_threat_by_user('eve_blackhat', status='ACTIVE')

# Update threat status
db.update_threat_status(threat_id=1, status='RESOLVED')
```

### Analytics
```python
# Overall statistics
stats = db.get_statistics()
print(f"Active threats: {stats['threats']['active']}")

# Dashboard summary
dashboard = db.get_dashboard_summary()
print(f"Top users: {dashboard['top_users']}")
print(f"Top resources: {dashboard['top_resources']}")
print(f"Severity distribution: {dashboard['severity_distribution']}")
```

## Event Flow Example

```
1. RFID scan: User "bob_miller" (Level 3) attempts to access "door_server_room" (Level 8 required)

2. Your code logs event:
   db.log_physical_event('bob_miller', 'door_server_room', 'DENIED')

3. Trigger #1 (physical → main):
   - Checks: user level (3) < required (8)
   - Inserts to main_logs with severity='HIGH'

4. Trigger #3 (main → threat):
   - Detects HIGH severity
   - Checks for existing threat for bob_miller (last 10 min)
   - Creates new threat:
     * threat_pattern: 'Unauthorized Access Pattern'
     * mitre_id: 'T1078' (Valid Accounts)
     * risk_score: 70
   - Sets correlation_flag=TRUE

5. Result:
   - physical_logs: 1 row
   - main_logs: 1 row (auto)
   - threats: 1 row (auto)
   - Ready for dashboard/alerts!
```

## Database Maintenance

### View Recent Events
```sql
SELECT * FROM main_logs 
WHERE event_time >= NOW() - INTERVAL '1 hour'
ORDER BY event_time DESC;
```

### Check Active Threats
```sql
SELECT * FROM threats 
WHERE status = 'ACTIVE'
ORDER BY risk_score DESC;
```

### Cleanup Old Logs
```sql
DELETE FROM physical_logs 
WHERE event_time < NOW() - INTERVAL '90 days';
```

### Reset Database
```sql
TRUNCATE TABLE physical_logs CASCADE;
TRUNCATE TABLE digital_logs CASCADE;
TRUNCATE TABLE main_logs CASCADE;
TRUNCATE TABLE threats CASCADE;
```

## Performance Indexes

The schema includes indexes on:
- `main_logs.event_time` - Fast time-based queries
- `main_logs.severity` - Fast severity filtering
- `threats.user_id` - Fast user threat lookup
- `physical_logs.user_id` - Fast user event lookup
- `digital_logs.user_id` - Fast user event lookup

## MITRE ATT&CK Mapping

The system maps threats to MITRE ATT&CK framework:

| Threat Pattern | MITRE ID | Tactic |
|---|---|---|
| Unauthorized Access Pattern | T1078 | Initial Access |
| Brute Force Attempts | T1110 | Credential Access |
| Privilege Escalation | T1068 | Privilege Escalation |
| Lateral Movement | T1021 | Lateral Movement |

## Security Considerations

1. **Change default password** in config/config.yaml
2. **Use environment variables** for credentials
3. **Enable SSL** for PostgreSQL connections
4. **Restrict network access** in pg_hba.conf
5. **Regular backups** of godseye database
6. **Monitor database performance** with pg_stat_statements

## Troubleshooting

### Connection Refused
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Start service
Start-Service postgresql-x64-16
```

### Tables Don't Exist
```powershell
# Run setup script
psql -U postgres -d godseye -f database/setup_postgres.sql
```

### Triggers Not Working
```sql
-- Verify triggers exist
SELECT * FROM pg_trigger WHERE tgname LIKE '%godseye%';

-- Manually re-run setup
\i database/setup_postgres.sql
```

## Next Steps

1. ✅ Database operational
2. 🔄 Integrate with IoT devices (MQTT)
3. 🔄 Connect Sysmon/Wazuh for digital events
4. 🔄 Build dashboard (React/Flask)
5. 🔄 Add email/SMS alerts
6. 🔄 ML-based anomaly detection

---

**Documentation Version:** 1.0  
**Last Updated:** February 27, 2026  
**Database Version:** PostgreSQL 16+
