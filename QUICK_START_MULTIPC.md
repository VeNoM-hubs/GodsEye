# Quick Start: Running GodsEye Dashboard on Another PC

## Summary
- ✅ All files pushed to GitHub (`feature/honeypot-live-feed-page` branch)
- ✅ Backend supports remote PostgreSQL connection
- ✅ Frontend can connect to backend on different PC
- ✅ Complete deployment guide available in `DEPLOYMENT_GUIDE.md`

---

## Quick Setup (5 minutes)

### PC 1: Backend (Python FastAPI)

```cmd
REM 1. Clone/pull code
cd C:\Users\YourName\GodsEye
git pull origin feature/honeypot-live-feed-page

REM 2. Setup database config (CRITICAL!)
copy config\db_config.yaml.template config\db_config.yaml
REM   Edit config\db_config.yaml:
REM   - Change host: from "localhost" to PostgreSQL server IP
REM   - e.g., host: 192.168.1.100
REM   - Set correct password

REM 3. Activate venv and start backend
venv\Scripts\activate.bat
python backend/api_server.py

REM EXPECTED: "INFO: GodsEye ICS Security Platform API running on http://0.0.0.0:8000"
```

**Keep this terminal OPEN.**

---

### PC 2: Frontend (Node.js React)

```cmd
REM 1. Clone/pull code
cd C:\Users\YourName\GodsEye
git pull origin feature/honeypot-live-feed-page

REM 2. Install dependencies
cd frontend
pnpm install
REM    (or: npm install if pnpm not available)

REM 3. Create .env.local with backend address
REM    Create file: frontend\.env.local
REM    Content:
REM    GODSEYE_API_URL=http://192.168.1.100:8000
REM    (Replace 192.168.1.100 with Backend PC's IP address)

REM 4. Start frontend
pnpm dev

REM EXPECTED: " > Frontend server running at http://localhost:8080"
```

---

### PC 2: Open Dashboard

```
Browser: http://localhost:8080
```

**You should see:**
- ✅ Dashboard loads without errors
- ✅ No red error banner
- ✅ Stats showing numbers (threats, violations, events)
- ✅ Events/alerts populated from database
- ✅ Green badge at bottom: "Live · PostgreSQL Connected"

---

## Critical Configuration Files

### PC 1: Backend Database Config
**File:** `config/db_config.yaml`

```yaml
database:
  host: 192.168.1.100        # ← Change to PostgreSQL IP (NOT localhost)
  port: 5432
  name: godseye
  username: postgres
  password: "your_db_password"
```

**How to find PostgreSQL IP:**
- On PostgreSQL PC: `ipconfig` → look for IPv4 Address
- Example: `192.168.1.100`

### PC 2: Frontend API Config
**File:** `frontend/.env.local`

```
GODSEYE_API_URL=http://192.168.1.100:8000
```

**Replace `192.168.1.100` with Backend PC IP address**

---

## Architecture Verification

```
┌─────────────────────────────┐
│ PC 2: Frontend              │
│ Browser: localhost:8080     │
│ React Dashboard             │
└────────────┬────────────────┘
             │
             │ GODSEYE_API_URL=
             │ http://192.168.1.100:8000
             │
┌────────────▼────────────────┐
│ PC 2: Express Proxy         │
│ Port 8080 (Node.js)         │
└────────────┬────────────────┘
             │
             │ Proxy to
             │ http://192.168.1.100:8000
             │
┌────────────▼────────────────┐
│ PC 1: FastAPI Backend       │
│ Port 8000 (Python)          │
└────────────┬────────────────┘
             │
             │ Query
             │
┌────────────▼────────────────┐
│ PostgreSQL (any location)   │
│ IP from db_config.yaml      │
│ Port 5432                   │
└─────────────────────────────┘
```

---

## Verify Each Layer

### Layer 1: PostgreSQL Connection
```cmd
REM On PC 1 (Backend):
psql -h 192.168.1.100 -U postgres -d godseye
REM Should succeed with correct password
```

### Layer 2: FastAPI Backend
```cmd
REM On any PC, Browser or Terminal:
curl http://192.168.1.100:8000/health
REM Should return: {"status": "healthy", ...}
```

### Layer 3: Express Proxy
```cmd
REM On PC 2 (Frontend):
curl http://localhost:8080/api/godseye/health
REM Should return: {"status": "healthy", "backend": "http://192.168.1.100:8000"}
```

### Layer 4: React Dashboard
```cmd
REM Open browser:
http://localhost:8080
REM Should show dashboard with data from PostgreSQL
```

---

## Troubleshooting Checklist

| Issue | Check |
|-------|-------|
| **Red "API unreachable" banner** | 1. Is backend running on PC 1? 2. Is firewall allowing port 8000? 3. Is .env.local correct IP? |
| **Backend won't start** | 1. Is config/db_config.yaml created? 2. Is PostgreSQL IP correct (not localhost)? 3. Can you ping that IP? |
| **Frontend won't start** | 1. Is pnpm installed? 2. Did you run `pnpm install`? 3. Is .env.local in frontend/ directory? |
| **No data showing** | 1. Does PostgreSQL have data? 2. Can backend reach database? 3. Check dashboard_api.py queries |
| **Connection timeout** | 1. Check firewall on PC 1 allows port 8000 2. Check firewall on PC 2 allows outbound to port 8000 3. Ping Backend PC IP |

---

## Network Requirements

### From Frontend PC to Backend PC:
- **Port:** 8000 (TCP)
- **Protocol:** HTTP
- **Check:** `ping <backend-ip>` should work

### From Backend PC to PostgreSQL:
- **Port:** 5432 (TCP)
- **Protocol:** PostgreSQL wire protocol
- **Check:** `telnet <postgres-ip> 5432` should connect

### Windows Firewall Rules:
```cmd
REM On Backend PC (allow incoming):
netsh advfirewall firewall add rule name="GodsEye Backend" dir=in action=allow protocol=tcp localport=8000

REM Verify:
netsh advfirewall firewall show rule name="GodsEye Backend"
```

---

## Files Modified (Summary)

```
✅ ADDED:
   backend/dashboard_api.py
   frontend/server/routes/godseye-proxy.ts
   frontend/shared/godseye-api-types.ts
   frontend/client/hooks/useGodsEyeLive.ts
   DEPLOYMENT_GUIDE.md
   QUICK_START_MULTIPC.md (this file)

✅ MODIFIED:
   backend/api_server.py
   frontend/server/index.ts
   frontend/client/pages/Index.tsx

✅ CREATE (manually):
   config/db_config.yaml (from template)
   frontend/.env.local (with API URL)
```

---

## API Endpoints (Backend)

All served on `http://<backend-ip>:8000/api/dashboard/`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/stats` | GET | KPIs (threats, violations, events/min) |
| `/events` | GET | Event stream (paginated, with `?since=` support) |
| `/alerts` | GET | Active threats/alerts |
| `/honeypot` | GET | Honeypot-only events |
| `/alerts/{id}/acknowledge` | PATCH | Mark alert acknowledged |
| `/alerts/{id}/resolve` | PATCH | Mark alert resolved |

---

## Environment Variables

### Backend (config/db_config.yaml)
```yaml
database:
  host: <POSTGRES_SERVER_IP>
  port: 5432
  name: godseye
  username: postgres
  password: <PASSWORD>
```

### Frontend (frontend/.env.local)
```
GODSEYE_API_URL=http://<BACKEND_PC_IP>:8000
```

---

## Support

**If dashboard shows "API unreachable":**

1. ✅ Check both servers are running (see terminal output)
2. ✅ Check .env.local has correct Backend PC IP
3. ✅ Test connectivity: `curl http://<backend-ip>:8000/health`
4. ✅ Check Windows Firewall allows port 8000
5. ✅ Check backend PC IP address with `ipconfig` on Backend PC

**See full troubleshooting in:** `DEPLOYMENT_GUIDE.md`

---

## Next Steps

1. ✅ Pull latest code: `git pull origin feature/honeypot-live-feed-page`
2. ✅ Follow Backend PC setup above
3. ✅ Follow Frontend PC setup above  
4. ✅ Open http://localhost:8080 and verify data shows
5. ✅ Read DEPLOYMENT_GUIDE.md for production setup

---

**Dashboard shows real PostgreSQL data with automatic reconnection logic! 🚀**
