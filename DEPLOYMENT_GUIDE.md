# GodsEye Dashboard - Deployment & Setup Guide

## Overview
The GodsEye Dashboard now includes:
- **FastAPI Backend** (port 8000) — Real-time data from PostgreSQL
- **Express Proxy** (port 8080) — Routes frontend requests to backend
- **React Frontend** (port 8080) — Interactive cybersecurity dashboard

This guide covers setup for **distributed deployment** where PostgreSQL is on a different PC.

---

## Architecture

```
┌─────────────────────┐
│  Browser (8080)     │
│  React Dashboard    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Express Proxy      │
│  (8080)             │
│  Node.js            │
└──────────┬──────────┘
           │ GODSEYE_API_URL
           │ (e.g., http://backend-pc:8000)
┌──────────▼──────────┐
│  FastAPI Backend    │
│  (8000)             │
│  Python             │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  PostgreSQL         │
│  (different PC)     │
│  Database           │
└─────────────────────┘
```

---

## Prerequisites

### Backend PC (where FastAPI + PostgreSQL access is)
- Python 3.10+
- PostgreSQL client access (or PostgreSQL server itself)
- 2GB+ RAM
- Network access to PostgreSQL port 5432

### Frontend PC (where React dashboard runs)
- Node.js 16+
- pnpm or npm
- 1GB+ RAM
- Network access to Backend PC port 8000

---

## Step 1: Setup Backend (on Backend PC)

### 1.1 Clone/Pull Latest Code
```cmd
cd "E:\Dowloads main\GodsEye"
git pull origin main
```

### 1.2 Create Database Config
Copy and modify the template:

```cmd
copy config\db_config.yaml.template config\db_config.yaml
```

Edit `config/db_config.yaml` with your PostgreSQL credentials:

```yaml
database:
  host: <POSTGRES_PC_IP>      # e.g., 192.168.1.100 or postgres-server.local
  port: 5432
  name: godseye
  username: postgres
  password: "your_password"
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600
```

**Important:** Replace `<POSTGRES_PC_IP>` with:
- IP address of PostgreSQL server PC (e.g., `192.168.1.100`)
- OR hostname (e.g., `postgres-server.local`)
- NOT `localhost` (that only works on same machine)

### 1.3 Activate Virtual Environment
```cmd
cd "E:\Dowloads main\GodsEye"
venv\Scripts\activate.bat
```

### 1.4 Start FastAPI Backend
```cmd
python backend/api_server.py
```

**Expected Output:**
```
INFO: GodsEye ICS Security Platform API running on http://0.0.0.0:8000
INFO: ✅ Database connected
```

**Note:** Leave this terminal open.

---

## Step 2: Setup Frontend (on Frontend PC)

### 2.1 Clone/Pull Latest Code
```cmd
cd "E:\Dowloads main\GodsEye"
git pull origin main
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

### 2.3 Create Environment File
Create `.env.local` in the `frontend/` directory:

```env
GODSEYE_API_URL=http://<BACKEND_PC_IP>:8000
```

Replace `<BACKEND_PC_IP>` with:
- IP address of Backend PC (e.g., `192.168.1.200`)
- OR hostname (e.g., `godseye-backend.local`)
- Use `http://localhost:8000` only if on same machine

### 2.4 Start React Frontend
```cmd
cd frontend
pnpm dev
```

**Expected Output:**
```
 > Frontend server running at http://localhost:8080
```

---

## Step 3: Verify Connection

### On Frontend PC, open browser:
```
http://localhost:8080
```

### You should see:
✅ Dashboard loads  
✅ No red error banner  
✅ Stats show numbers (not zeros)  
✅ Events/alerts populated from PostgreSQL  
✅ Bottom badge shows "Live · PostgreSQL Connected"

### Debug Connection:
If you see **red error banner** "API unreachable":

**Check 1: Backend is running**
```cmd
curl http://<BACKEND_PC_IP>:8000/health
```

Should return:
```json
{"status": "healthy", "service": "GodsEye Honeypot Webhook API", "database": "connected"}
```

**Check 2: Frontend proxy can reach backend**
```cmd
curl http://localhost:8080/api/godseye/health
```

Should return:
```json
{"status": "healthy", "backend": "http://<BACKEND_PC_IP>:8000"}
```

**Check 3: Database connection**
On Backend PC, check `db_config.yaml`:
- Is `host:` set to PostgreSQL server IP (not localhost)?
- Is password correct?
- Is PostgreSQL accepting remote connections?

---

## Step 4: Network Configuration

### If Backend and Frontend are on Different PCs:

**Firewall Rules:**
- **Backend PC:** Allow incoming TCP port 8000
- **Frontend PC:** Allow outgoing TCP to Backend PC port 8000

**Windows Firewall Example:**
```cmd
# On Backend PC:
netsh advfirewall firewall add rule name="GodsEye Backend" dir=in action=allow protocol=tcp localport=8000
```

**Local Network Discovery:**
- Use IP addresses (e.g., `192.168.1.100`) or
- Use hostnames if mDNS/DNS is configured (e.g., `backend-pc.local`)

---

## Environment Variables Summary

### Backend (Python)
No additional env vars needed — uses `config/db_config.yaml`

### Frontend (Node.js)
Create `frontend/.env.local`:
```env
GODSEYE_API_URL=http://<BACKEND_PC_IP>:8000
VITE_API_BASE_URL=http://<BACKEND_PC_IP>:8000     # Alternative
```

---

## File Structure

```
GodsEye/
├── backend/
│   ├── api_server.py              [UPDATED] - Registers dashboard router
│   ├── dashboard_api.py            [NEW] - 6 dashboard endpoints
│   ├── db_storage.py               - Database operations
│   └── ...
├── frontend/
│   ├── server/
│   │   ├── index.ts                [UPDATED] - Express server + proxy
│   │   └── routes/
│   │       └── godseye-proxy.ts    [NEW] - Proxy middleware
│   ├── shared/
│   │   └── godseye-api-types.ts   [NEW] - TypeScript types + API client
│   ├── client/
│   │   ├── hooks/
│   │   │   └── useGodsEyeLive.ts  [NEW] - React hook (real data polling)
│   │   └── pages/
│   │       └── Index.tsx           [UPDATED] - Uses useGodsEyeLive
│   └── .env.local                  [CREATE] - Backend API URL
├── config/
│   ├── db_config.yaml.template     - Database config template
│   └── db_config.yaml              [CREATE] - Your database credentials
└── ...
```

---

## Dashboard Features

### Real-Time Data:
- **Stats Dashboard** — Active threats, violations, events/min, MITRE breakdown
- **Event Stream** — Live physical & digital access events from PostgreSQL
- **Alerts** — Active threats with severity levels
- **Honeypot Feed** — Attacker interactions captured by honeypot
- **Alert Management** — Acknowledge/resolve threats

### Connection Monitoring:
- Green badge when connected to PostgreSQL
- Red banner if API unreachable
- Auto-reconnect with exponential backoff
- Incremental data fetching (only new events)

---

## Troubleshooting

### "API Unreachable" Error

**1. Check backend is running:**
```cmd
netstat -ano | findstr :8000
```

**2. Check connectivity:**
```cmd
ping <BACKEND_PC_IP>
curl http://<BACKEND_PC_IP>:8000/health
```

**3. Check .env.local has correct IP:**
```
GODSEYE_API_URL=http://<BACKEND_PC_IP>:8000
```

**4. Check firewall:**
- Backend PC: Allow port 8000 inbound
- Frontend PC: Allow outbound to port 8000

---

### "Database Connection Failed"

**1. Check db_config.yaml:**
```yaml
host: <POSTGRES_IP>    # NOT localhost
port: 5432
name: godseye
username: postgres
password: correct_password
```

**2. Test PostgreSQL connection:**
```cmd
psql -h <POSTGRES_IP> -U postgres -d godseye
```

**3. Verify PostgreSQL allows remote connections:**
- Check `postgresql.conf`: `listen_addresses = '*'`
- Check `pg_hba.conf`: Allow host connections

---

### "Ports Already in Use"

If port 8000 or 8080 is already in use:

**Find process using port 8000:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Or use different port:**
```cmd
# Backend: Change uvicorn port in api_server.py line 124
# Frontend: Change pnpm dev script in package.json
```

---

## Production Deployment

For production deployment:

1. **Use environment variables** (not hardcoded)
2. **Enable HTTPS** (use nginx reverse proxy)
3. **Add authentication** (JWT tokens)
4. **Set up monitoring** (logs, metrics)
5. **Use systemd** (Linux) or Task Scheduler (Windows) for auto-restart
6. **Configure CORS** properly in `api_server.py`

---

## Support

For issues:
1. Check logs from both backend and frontend terminals
2. Run health checks: `/api/godseye/health`
3. Verify network connectivity between PCs
4. Check database config and credentials
5. Review `.env.local` in frontend directory

---

## Files Modified/Created

- ✅ `backend/dashboard_api.py` — NEW
- ✅ `backend/api_server.py` — UPDATED (added dashboard router)
- ✅ `frontend/server/routes/godseye-proxy.ts` — NEW
- ✅ `frontend/server/index.ts` — UPDATED (added proxy + health check)
- ✅ `frontend/shared/godseye-api-types.ts` — NEW
- ✅ `frontend/client/hooks/useGodsEyeLive.ts` — NEW
- ✅ `frontend/client/pages/Index.tsx` — UPDATED (uses useGodsEyeLive)
- ✅ `config/db_config.yaml` — CREATE (from template)
- ✅ `frontend/.env.local` — CREATE (with backend API URL)
