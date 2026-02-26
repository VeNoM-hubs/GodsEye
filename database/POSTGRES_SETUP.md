# PostgreSQL Setup for GodsEye

**Note:** GodsEye uses PostgreSQL exclusively for production-grade reliability and performance.

## Step 1: Install PostgreSQL

### Windows
Download and install from: https://www.postgresql.org/download/windows/

**During installation:**
- Set a password for the `postgres` superuser (remember this!)
- Default port: 5432
- Remember the installation path

### Using Chocolatey (Windows)
```powershell
choco install postgresql
```

### Verify Installation
```powershell
psql --version
```

---

## Step 2: Create Database

### Option A: Using pgAdmin (GUI)
1. Open pgAdmin
2. Connect to PostgreSQL server
3. Right-click "Databases" → Create → Database
4. Name: `godseye`
5. Owner: `postgres`

### Option B: Using Command Line (Recommended)
```powershell
# Login as postgres user
psql -U postgres

# Then run:
CREATE DATABASE godseye;
CREATE USER godseye WITH PASSWORD 'godseye_secure_password';
GRANT ALL PRIVILEGES ON DATABASE godseye TO godseye;
\q
```

### Option C: Run SQL Script
```powershell
psql -U postgres -f database\setup_postgres.sql
```

---

## Step 3: Update Configuration

Edit `config/config.yaml`:
```yaml
storage:
  storage_type: postgresql
  db_host: localhost
  db_port: 5432
  db_name: godseye
  db_user: godseye
  db_password: godseye_secure_password
```

**⚠️ IMPORTANT**: Change the password to something secure!

---

## Step 4: Install Python Driver

```powershell
pip install psycopg2-binary
```

---

## Step 5: Test Connection

```powershell
python tests\test_database.py
```

---

## Connection String

```
postgresql://godseye:godseye_secure_password@localhost:5432/godseye
```

---

## Troubleshooting

### Error: "psql is not recognized"
Add PostgreSQL bin directory to PATH:
```
C:\Program Files\PostgreSQL\16\bin
```

### Error: "password authentication failed"
Check your password and username are correct.

### Error: "connection refused"
Make sure PostgreSQL service is running:
```powershell
# Check status
Get-Service postgresql*

# Start service
Start-Service postgresql-x64-16
```

### Error: "database does not exist"
Create the database first using Step 2.

---

## Security Best Practices

1. **Change default password** immediately
2. **Use environment variables** for credentials:
   ```powershell
   $env:GODSEYE_DB_PASSWORD="your_secure_password"
   ```
3. **Restrict network access** in `pg_hba.conf`
4. **Use SSL connections** for production

---

## Quick Commands

```powershell
# Connect to database
psql -U godseye -d godseye

# List tables
\dt

# View table structure
\d access_event_logs

# Count records
SELECT COUNT(*) FROM access_event_logs;

# View recent events
SELECT event_id, device_id, status, timestamp 
FROM access_event_logs 
ORDER BY timestamp DESC 
LIMIT 10;

# Exit
\q
```

---

## Next Steps

After setup is complete:
1. Run `python tests\test_database.py` to create tables
2. Run `python tests\cli_event_test.py` to add events
3. Events will be stored in PostgreSQL!
