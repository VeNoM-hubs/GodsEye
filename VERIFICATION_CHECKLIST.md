# GodsEye Dashboard - Verification & Deployment Checklist

## ✅ All Files Successfully Committed to GitHub

**Branch:** `feature/honeypot-live-feed-page`

### New Files Created:
- ✅ `backend/dashboard_api.py` — 6 REST endpoints for dashboard
- ✅ `frontend/server/routes/godseye-proxy.ts` — Express proxy middleware
- ✅ `frontend/shared/godseye-api-types.ts` — TypeScript types & API client
- ✅ `frontend/client/hooks/useGodsEyeLive.ts` — React polling hook
- ✅ `DEPLOYMENT_GUIDE.md` — Comprehensive multi-PC setup
- ✅ `QUICK_START_MULTIPC.md` — 5-minute quick start

### Files Modified:
- ✅ `backend/api_server.py` — Registered dashboard router (2 lines)
- ✅ `frontend/server/index.ts` — Added proxy + health check
- ✅ `frontend/client/pages/Index.tsx` — Uses useGodsEyeLive hook

---

## 🎯 Running on Another PC - Complete Steps

### Prerequisites:
- [ ] Backend PC (Python 3.10+, access to PostgreSQL)
- [ ] Frontend PC (Node.js 16+, pnpm or npm)
- [ ] Both PCs connected to same network
- [ ] PostgreSQL database running (any location)

---

## Step 1: Backend PC Setup (FastAPI)

### 1.1 Clone Latest Code
```cmd
cd C:\GodsEye
git clone https://github.com/VeNoM-hubs/GodsEye.git
cd GodsEye
git checkout feature/honeypot-live-feed-page
```

Or if already cloned:
```cmd
cd C:\GodsEye\GodsEye
git pull origin feature/honeypot-live-feed-page
```

### 1.2 Create Database Configuration
```cmd
REM Copy template to actual config
copy config\db_config.yaml.template config\db_config.yaml

REM Edit config\db_config.yaml with your database details
REM CRITICAL: Change "host: localhost" to actual PostgreSQL IP
```

**Edit `config/db_config.yaml`:**
```yaml
database:
  host: 192.168.1.100        # ← CHANGE THIS to PostgreSQL server IP
  port: 5432
  name: godseye
  username: postgres
  password: "your_password"   # ← CHANGE THIS
```

**How to find PostgreSQL IP:**
- Open Command Prompt on PostgreSQL server PC: `ipconfig`
- Look for "IPv4 Address" (e.g., `192.168.1.100`)

### 1.3 Setup Python Environment
```cmd
REM Activate virtual environment
venv\Scripts\activate.bat

REM Install dependencies (if first time)
pip install -r requirements.txt
```

### 1.4 Start Backend Server
```cmd
python backend/api_server.py
```

**Expected Output:**
```
INFO: GodsEye ICS Security Platform API running on http://0.0.0.0:8000
INFO: ✅ Database connected
```

**✅ Backend is ready!** Keep terminal open.

---

## Step 2: Frontend PC Setup (React)

### 2.1 Clone Latest Code
```cmd
cd C:\GodsEye
git clone https://github.com/VeNoM-hubs/GodsEye.git
cd GodsEye
git checkout feature/honeypot-live-feed-page
```

Or if already cloned:
```cmd
cd C:\GodsEye\GodsEye
git pull origin feature/honeypot-live-feed-page
```

### 2.2 Install Dependencies
```cmd
cd frontend
pnpm install
```

If `pnpm` not installed:
```cmd
npm install -g pnpm
pnpm install
```

### 2.3 Create Environment Configuration
**Create file:** `frontend/.env.local`

**Content:**
```
GODSEYE_API_URL=http://192.168.1.100:8000
```

**Replace `192.168.1.100` with Backend PC's IP address**

**How to find Backend PC IP:**
- On Backend PC: Open Command Prompt: `ipconfig`
- Look for "IPv4 Address" (e.g., `192.168.1.200`)

### 2.4 Start Frontend Server
```cmd
cd frontend
pnpm dev
```

**Expected Output:**
```
 > Frontend server running at http://localhost:8080
```

**✅ Frontend is ready!** Keep terminal open.

---

## Step 3: Verify Connection & Dashboard

### 3.1 Open Dashboard
On Frontend PC, open web browser:
```
http://localhost:8080
```

### 3.2 Verify Connection Indicators

**You should see:**
- ✅ Dashboard page loads without errors
- ✅ **NO red error banner** at top
- ✅ Stats cards show numbers (not zeros):
  - Active Threats: N
  - Total Violations: M
  - Events/min: X.XX
- ✅ Event list populated with data
- ✅ Alerts showing if threats exist
- ✅ **Bottom right badge:** Green "Live · PostgreSQL Connected"

### 3.3 Connection Status Badge
The bottom-right corner shows:
```
🟢 Live · PostgreSQL Connected
   Last updated: 2 seconds ago
```

This means:
- ✅ Frontend successfully connected to backend
- ✅ Backend successfully connected to PostgreSQL
- ✅ Data is being fetched and updated

---

## Troubleshooting Guide

### Issue: Red Banner - "API Unreachable"

**Check 1: Backend is running**
```cmd
REM On any PC, test backend health:
curl http://<BACKEND_PC_IP>:8000/health
```

Expected: `{"status": "healthy", ...}`

**Check 2: .env.local has correct IP**
```cmd
REM On Frontend PC, verify file:
type frontend\.env.local
```

Should show: `GODSEYE_API_URL=http://<BACKEND_PC_IP>:8000`

**Check 3: Network connectivity**
```cmd
REM On Frontend PC:
ping <BACKEND_PC_IP>
```

Should respond successfully

**Check 4: Firewall allows port 8000**
```cmd
REM On Backend PC:
netstat -ano | findstr :8000
```

Should show Python process listening on port 8000

If not open, add firewall rule:
```cmd
netsh advfirewall firewall add rule name="GodsEye" dir=in action=allow protocol=tcp localport=8000
```

### Issue: Dashboard Shows No Data (Zeros)

**Check 1: PostgreSQL has data**
```cmd
REM On any PC with psql access:
psql -h <POSTGRES_IP> -U postgres -d godseye
SELECT COUNT(*) FROM main_logs;
SELECT COUNT(*) FROM threats;
```

Should return numbers > 0

**Check 2: Database config is correct**
```cmd
REM On Backend PC, verify:
type config\db_config.yaml
```

- host: should NOT be localhost (should be PostgreSQL IP)
- username: should be correct
- password: should be correct

**Check 3: Backend can reach database**
```cmd
REM On Backend PC terminal output, look for:
"✅ Database connected"
```

If you see error about database, check credentials

### Issue: Frontend Won't Start

**Check 1: Dependencies installed**
```cmd
cd frontend
pnpm list fastapi
```

Should show packages

**Check 2: .env.local exists**
```cmd
dir frontend\.env.local
```

Should exist. If not, create it with correct API URL

**Check 3: Port 8080 not in use**
```cmd
netstat -ano | findstr :8080
```

If something is using it, either:
- Close that app, OR
- Change port in package.json dev script

---

## Network Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│ Frontend PC (e.g., 192.168.1.200)               │
│ ┌───────────────────────────────────────────┐   │
│ │ Browser                                   │   │
│ │ http://localhost:8080                     │   │
│ │ React Dashboard                           │   │
│ └───────────────────────────────────────────┘   │
│ ┌───────────────────────────────────────────┐   │
│ │ Express Proxy Server (Node.js)            │   │
│ │ Port 8080                                 │   │
│ │ Routes /api/dashboard/* to backend        │   │
│ └─────────────────┬───────────────────────┘   │
└─────────────────┼─────────────────────────────┘
                  │
                  │ GODSEYE_API_URL
                  │ http://192.168.1.100:8000
                  │
┌─────────────────▼───────────────────────────────┐
│ Backend PC (e.g., 192.168.1.100)                │
│ ┌───────────────────────────────────────────┐   │
│ │ FastAPI Server (Python)                   │   │
│ │ Port 8000                                 │   │
│ │ Endpoints: /api/dashboard/*               │   │
│ └─────────────────┬───────────────────────┘   │
└─────────────────┼─────────────────────────────┘
                  │
                  │ PostgreSQL connection
                  │ Host from db_config.yaml
                  │ Port 5432
                  │
┌─────────────────▼───────────────────────────────┐
│ PostgreSQL Database                             │
│ (Any PC: same, Backend PC, or remote server)    │
│ Tables: main_logs, threats, honeypot_logs...    │
└─────────────────────────────────────────────────┘
```

---

## Configuration Reference

### Backend PC Configuration
**File: `config/db_config.yaml`**
```yaml
database:
  host: 192.168.1.100        # PostgreSQL server IP
  port: 5432                 # PostgreSQL port (default)
  name: godseye              # Database name
  username: postgres         # DB username
  password: "password123"    # DB password
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600
```

### Frontend PC Configuration
**File: `frontend/.env.local`**
```
GODSEYE_API_URL=http://192.168.1.100:8000
```

---

## Testing Each Layer

### Layer 1: PostgreSQL Connection
```cmd
REM On any PC with psql installed:
psql -h 192.168.1.100 -U postgres -d godseye -c "SELECT count(*) FROM main_logs;"
```

Expected: Returns a number

### Layer 2: Backend API
```cmd
REM On any PC with curl:
curl http://192.168.1.100:8000/health
```

Expected: `{"status":"healthy",...}`

### Layer 3: Backend Health Check
```cmd
REM On Backend PC:
curl http://localhost:8000/health
```

Expected: Same as Layer 2

### Layer 4: Frontend Health Check
```cmd
REM On Frontend PC:
curl http://localhost:8080/api/godseye/health
```

Expected: `{"status":"healthy","backend":"http://192.168.1.100:8000"}`

### Layer 5: Dashboard
```
Browser on Frontend PC: http://localhost:8080
```

Expected: Dashboard loads with data from PostgreSQL

---

## Security Notes for Deployment

⚠️ **Important for Production:**

1. **Never commit credentials:**
   - Add `config/db_config.yaml` to `.gitignore`
   - Add `frontend/.env.local` to `.gitignore`

2. **Use environment variables:**
   ```cmd
   set GODSEYE_API_URL=http://backend.company.com:8000
   ```

3. **Enable HTTPS:**
   - Use nginx reverse proxy
   - Get SSL certificate
   - Forward HTTPS to HTTP internally

4. **Add authentication:**
   - JWT tokens in API requests
   - Session management in frontend

5. **Firewall rules:**
   - Only allow ports 8000, 8080 from trusted IPs
   - Block public internet access initially

6. **PostgreSQL security:**
   - Use strong passwords
   - Limit connections by IP
   - Run backups regularly

---

## Dashboard Features

✅ **Real-Time Data:**
- Stats updated every 3 seconds
- Event stream with incremental fetching
- Alerts with severity levels (INFO, LOW, MEDIUM, HIGH, CRITICAL)
- Honeypot activity feed

✅ **User Actions:**
- Acknowledge alerts (mark as acknowledged)
- Resolve alerts (mark as resolved)
- Pause/resume live updates

✅ **Error Handling:**
- Connection loss shows red banner
- Auto-reconnect with backoff
- Keeps showing last known data
- Health check endpoint for monitoring

---

## Support & Debugging

**Check these in order if something breaks:**

1. ✅ Both terminals show "running" messages
2. ✅ Network connectivity: `ping <ip>`
3. ✅ Port availability: `netstat -ano | findstr :8000`
4. ✅ Configuration files exist and have correct IPs
5. ✅ Firewall allows ports 8000, 8080
6. ✅ PostgreSQL accepts remote connections
7. ✅ Database credentials are correct

**For detailed troubleshooting, see:**
- `DEPLOYMENT_GUIDE.md` — Full setup guide
- `QUICK_START_MULTIPC.md` — Quick reference

---

## Files Overview

```
backend/
├── dashboard_api.py         [NEW] - 6 endpoints (stats, events, alerts, etc.)
├── api_server.py            [MODIFIED] - Registered dashboard router
└── ...other files...

frontend/
├── server/
│   ├── index.ts             [MODIFIED] - Proxy + health check
│   └── routes/
│       └── godseye-proxy.ts [NEW] - Request proxy middleware
├── shared/
│   └── godseye-api-types.ts [NEW] - TypeScript types + API client
├── client/
│   ├── hooks/
│   │   └── useGodsEyeLive.ts [NEW] - React hook (polling)
│   └── pages/
│       └── Index.tsx        [MODIFIED] - Uses useGodsEyeLive
├── .env.local               [CREATE] - API URL config
└── ...other files...

config/
├── db_config.yaml           [CREATE from template] - Database credentials
└── db_config.yaml.template  - Template file

Documentation/
├── DEPLOYMENT_GUIDE.md          - Complete setup guide
├── QUICK_START_MULTIPC.md       - 5-minute quick start
└── VERIFICATION_CHECKLIST.md    - This file
```

---

## Summary

✅ **All code is ready for multi-PC deployment**
✅ **Database config is configurable for remote PostgreSQL**
✅ **Frontend API URL is configurable via environment variables**
✅ **Error handling and auto-reconnect built in**
✅ **Comprehensive guides provided**

**Next: Follow Steps 1-3 above to deploy on your PCs!**

---

**For any issues, refer to the troubleshooting guide above or check DEPLOYMENT_GUIDE.md**
