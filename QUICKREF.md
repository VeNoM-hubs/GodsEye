# GodsEye Quick Reference

## 🚀 Quick Start (5 Minutes)

```powershell
# 1. Setup database
psql -U postgres -f database/setup_postgres.sql

# 2. Seed data
python tests/seed_database.py

# 3. Test system
python tests/test_database.py

# 4. View status
python tests/demo_database.py
```

## 📦 Python API Cheat Sheet

### Initialize
```python
from backend.db_storage import get_db
db = get_db()
```

### Physical Access Logging
```python
# RFID/Fingerprint/Door access
db.log_physical_event(
    user_id="john_doe",
    resource_id="door_server_room",
    access_status="GRANTED"  # or DENIED, FAILED
)
```

### Digital Activity Logging
```python
# Sysmon/Wazuh/Endpoint events
db.log_digital_event(
    user_id="alice_smith",
    resource_id="server_prod",
    action_type="FILE_ACCESS",
    raw_severity="LOW"  # or MEDIUM, HIGH
)
```

### Query Events
```python
# High severity events (last 24h)
events = db.get_high_severity_events(hours=24)

# User activity
events = db.get_main_logs(user_id="john_doe", limit=50)

# Recent physical access
logs = db.get_physical_logs(resource_id="door_server_room", limit=100)
```

### Threat Management
```python
# Active threats
threats = db.get_threats(status='ACTIVE')

# User threats
threats = db.get_threat_by_user('eve_blackhat')

# Resolve threat
db.update_threat_status(threat_id=1, status='RESOLVED')
```

### Analytics
```python
# Overall stats
stats = db.get_statistics()

# Dashboard data
dashboard = db.get_dashboard_summary()
```

## 🗄️ SQL Cheat Sheet

```sql
-- Recent HIGH severity events
SELECT * FROM main_logs 
WHERE severity = 'HIGH' 
  AND event_time >= NOW() - INTERVAL '24 hours'
ORDER BY event_time DESC;

-- Active threats by risk
SELECT * FROM threats 
WHERE status = 'ACTIVE'
ORDER BY risk_score DESC;

-- User activity summary
SELECT user_id, COUNT(*) as event_count
FROM main_logs
GROUP BY user_id
ORDER BY event_count DESC;

-- Failed access attempts
SELECT user_id, resource_id, COUNT(*) as attempts
FROM physical_logs
WHERE access_status = 'DENIED'
  AND event_time >= NOW() - INTERVAL '1 hour'
GROUP BY user_id, resource_id;
```

## 🎯 Access Levels

| Level | Role | Example |
|---|---|---|
| 10 | Admin | Root, Security Admin |
| 8-9 | IT Staff | Senior Engineers, IT Admins |
| 6-7 | Engineers | Software Engineers |
| 5 | Analysts | Data/Security Analysts |
| 3-4 | Staff | Regular Employees |
| 2-3 | Contractors | External Workers |
| 1 | Guest | Visitors, External |

## 🚨 Event Severity

| Severity | Trigger | Example |
|---|---|---|
| HIGH | Denied access, Insufficient level | Level 3 user → Level 8 resource |
| MEDIUM | Suspicious patterns | Multiple failed attempts |
| LOW | Normal operations | Successful access |

## 🔥 Threat Detection

Automatic threat creation when:
- **HIGH severity** event occurs
- **Risk score starts at 70**
- **+10 points** per additional violation
- **10-minute correlation window**
- **MITRE T1078** mapping (Valid Accounts)

## 📊 Database Tables

```
physical_logs  →  [TRIGGER 1]  →  main_logs  →  [TRIGGER 3]  →  threats
digital_logs   →  [TRIGGER 2]  →     ↑
                                     |
users ←──────────────────────────────┤
resources ←──────────────────────────┘
mitre_techniques ←───────────────────────────────────────────┘
```

## 🛠️ Common Tasks

### Add New User
```python
db.add_user("new_user", "New User", "employee", access_level=5)
```

### Add New Resource
```python
db.add_resource("door_lab", "Lab Door", "physical_door", 
                required_access_level=6, is_sensitive=False)
```

### Check User Status
```python
user = db.get_user("john_doe")
print(f"{user['full_name']}: Level {user['access_level']}")
```

### Get Resource Info
```python
resource = db.get_resource("door_server_room")
print(f"Required Level: {resource['required_access_level']}")
```

## 🔧 Maintenance

```powershell
# Backup database
pg_dump -U godseye godseye > backup.sql

# Restore database
psql -U godseye godseye < backup.sql

# Check database size
psql -U godseye -d godseye -c "\dt+"
```

## 📞 Files

| File | Purpose |
|---|---|
| `database/setup_postgres.sql` | Create tables & triggers |
| `database/README.md` | Full documentation |
| `backend/db_storage.py` | Python API |
| `tests/seed_database.py` | Initial data setup |
| `tests/test_database.py` | Comprehensive tests |
| `tests/demo_database.py` | Quick status view |

## 🎓 Learning Path

1. **Run seed_database.py** - Understand data structure
2. **Run test_database.py** - See events & triggers in action
3. **Run demo_database.py** - View system status
4. **Check database/README.md** - Deep dive
5. **Start logging real events!** - Production ready

---

**Need Help?** See `database/README.md` for detailed documentation
