# Database Configuration

## Overview

The `db_config.yaml` file contains PostgreSQL database credentials used by all GodsEye modules.

## Configuration File

**Location:** `config/db_config.yaml`

```yaml
database:
  host: localhost          # PostgreSQL server hostname
  port: 5432              # PostgreSQL server port
  name: godseye           # Database name
  username: postgres      # Database username
  password: "1234"        # Database password
```

## Usage

### Automatic Configuration

All database modules automatically load credentials from `db_config.yaml`:

```python
from backend.db_storage import get_db

# Automatically uses config/db_config.yaml
db = get_db()
```

### Override Configuration

You can override config file values programmatically:

```python
from backend.db_storage import get_db

# Override specific values
db = get_db(
    db_host="production-db.example.com",
    db_port=5433,
    db_password="production_password"
)
```

### Custom Config Path

Use a different config file:

```python
from backend.db_storage import get_db

# Use custom config file
db = get_db(config_path="/path/to/custom_config.yaml")
```

## Security Notes

⚠️ **Important:** Never commit database passwords to version control!

### Best Practices

1. **Development:** Use `db_config.yaml` with local credentials (already in `.gitignore`)
2. **Production:** Use environment variables or secure credential management
3. **Team sharing:** Share credentials via secure channels (not Git)

### Environment Variables (Alternative)

For production environments, consider using environment variables:

```python
import os
from backend.db_storage import get_db

db = get_db(
    db_host=os.getenv('DB_HOST', 'localhost'),
    db_port=int(os.getenv('DB_PORT', 5432)),
    db_name=os.getenv('DB_NAME', 'godseye'),
    db_user=os.getenv('DB_USER', 'postgres'),
    db_password=os.getenv('DB_PASSWORD')
)
```

## Testing

Test database connection:

```bash
# Seed database with test data
python tests/seed_database.py

# Run database tests
python tests/test_database.py

# View database status
python tests/demo_database.py

# Test RFID event injection
python tests/test_rfid_injection.py
```

All test scripts now use `db_config.yaml` automatically.

## Troubleshooting

### Connection Failed

If you see "Connection failed" errors:

1. Verify PostgreSQL is running:
   ```bash
   psql -U postgres -c "SELECT version();"
   ```

2. Check credentials in `db_config.yaml` are correct

3. Ensure database exists:
   ```bash
   psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='godseye';"
   ```

4. Verify tables are created:
   ```bash
   psql -U postgres -d godseye -c "\dt"
   ```

### Create Database

If database doesn't exist:

```bash
# Using setup script (recommended)
psql -U postgres -f database/setup_postgres.sql

# Or manually
psql -U postgres -c "CREATE DATABASE godseye;"
psql -U postgres -d godseye -f database/schema.sql
```

## Files Using Database Config

- `backend/db_storage.py` - Main database module
- `tests/seed_database.py` - Database seeding
- `tests/test_database.py` - Database tests
- `tests/demo_database.py` - Database demo
- `tests/test_rfid_injection.py` - RFID event testing

All automatically use `config/db_config.yaml`.
