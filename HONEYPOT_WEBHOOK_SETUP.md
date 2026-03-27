# Honeypot Webhook Integration Guide

## System Architecture

```
┌─────────────────────────────────────┐
│        ESP32 Honeypot               │
│   (honeypots/ESP32-Honeypot/)       │
│                                     │
│  - Port 23: Telnet Service          │
│  - Logs all commands/credentials    │
│  - Accepts attacker connections     │
└─────────────┬───────────────────────┘
              │
              │ POST /honeypot/log
              │ (JSON Event)
              ▼
┌─────────────────────────────────────┐
│  FastAPI Server (api_server.py)     │
│  Listens on: http://0.0.0.0:8000    │
│                                     │
│  Endpoint: POST /honeypot/log       │
│  - Validates JSON payload           │
│  - Stores in database               │
│  - Returns success/failure          │
└─────────────┬───────────────────────┘
              │
              │ INSERT INTO honeypot_logs
              ▼
┌─────────────────────────────────────┐
│    PostgreSQL Database              │
│    (localhost:5432/godseye)         │
│                                     │
│  Table: honeypot_logs               │
│  - Stores all honeypot interactions │
│  - Auto-triggers threat detection   │
└─────────────────────────────────────┘
```

---

## Setup Instructions

### Step 1: Start the Webhook Server

Run the FastAPI server to listen for honeypot events:

```bash
cd c:\Users\lukra_mj9bmma\GodsEye
python -m backend.api_server
```

Expected output:
```
🚀 Starting GodsEye Honeypot API Server
📍 Listening on http://0.0.0.0:8000
📖 Swagger UI: http://0.0.0.0:8000/docs
```

### Step 2: Configure ESP32 Honeypot with Webhook URL

The ESP32 honeypot reads configuration from a JSON file (`/config.json` on SPIFFS).

**Option A: Using Web UI (Recommended)**

1. Make sure the ESP32 is powered on
2. Connect to WiFi AP: `HoneypotConfig` (password: `HoneyPotConfig123`)
3. Open browser to: `http://192.168.4.1`
4. In the web form, set:
   - **SSID**: Your WiFi network
   - **Password**: Your WiFi password
   - **Webhook URL**: `http://192.168.0.7:8000/honeypot/log`
   - **Enabled Ports**: Check ports to monitor (23 for Telnet, 21 for FTP, etc)
5. Click "Save Configuration" and "Reboot"

**Option B: Manual Configuration**

Create a JSON config file for the ESP32:

```json
{
  "ssid": "YOUR_WIFI_SSID",
  "password": "YOUR_WIFI_PASSWORD",
  "webhook": "http://192.168.1.100:8000/honeypot/log",
  "ports": [21, 22, 23, 25, 53, 110, 143, 443, 445, 3306, 3389, 5900, 8080]
}
```

Upload this to the ESP32's SPIFFS storage.

### Step 3: Verify Webhook Connection

Check if server is receiving events:

```bash
# Watch server logs
python -m backend.api_server
```

You should see:
```
✅ Honeypot event logged [ID: 1] - Attacker: 192.168.1.5:54321 → Port: 23 | Threat: HIGH
```

---

## Webhook POST Format

When attackers connect to the ESP32 honeypot, events are sent as JSON POST requests:

### POST /honeypot/log

**Request Body:**
```json
{
  "honeypot_id": "ESP32-AABBCCDD",
  "honeypot_name": "Telnet Server",
  "honeypot_type": "multi-service",
  "attacker_ip": "192.168.1.5",
  "attacker_port": 54321,
  "target_port": 23,
  "username_attempted": "admin",
  "password_attempted": "password123",
  "commands_executed": ["ls", "whoami", "cat /etc/passwd"],
  "auth_success": false,
  "session_duration_ms": 5000,
  "threat_level": "HIGH",
  "timestamp": "2026-03-27T12:34:56"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Honeypot event stored successfully",
  "honeypot_log_id": 1,
  "error": null
}
```

---

## Database Schema

The `honeypot_logs` table stores all events:

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key (auto-increment) |
| honeypot_id | VARCHAR(100) | Unique honeypot identifier (e.g., MAC address) |
| honeypot_name | VARCHAR(100) | Service name (e.g., "Telnet Server") |
| honeypot_type | VARCHAR(50) | Type (e.g., "multi-service") |
| attacker_ip | VARCHAR(50) | Attacker's IP address |
| attacker_port | INT | Attacker's source port |
| target_port | INT | Honeypot port (23, 21, etc) |
| username_attempted | VARCHAR(200) | Username from login attempt |
| password_attempted | VARCHAR(200) | Password from login attempt |
| commands_executed | TEXT[] | Array of executed commands |
| auth_success | BOOLEAN | Whether authentication succeeded |
| session_duration_ms | INT | Duration in milliseconds |
| threat_level | VARCHAR(20) | LOW / MEDIUM / HIGH / CRITICAL |
| event_time | TIMESTAMP | When attack occurred |
| created_at | TIMESTAMP | When record was inserted |

---

## Automatic Threat Detection

When a honeypot event is inserted, the `escalate_honeypot_hit()` trigger automatically:

1. Creates a new threat record in the `threats` table
2. Sets risk_score based on threat_level:
   - CRITICAL: 95
   - HIGH: 80
   - MEDIUM: 60
   - LOW: 50
3. Links to MITRE technique T1595 (Active Scanning)

Example threat created:
```
threat_id: 100
user_id: HONEYPOT_ESP32-AABBCCDD
threat_pattern: Honeypot Interaction - multi-service on port 23
mitre_id: T1595
risk_score: 80
status: ACTIVE
```

---

## API Endpoints Reference

### 1. POST /honeypot/log
**Submit a honeypot event** (from ESP32)
```bash
curl -X POST http://localhost:8000/honeypot/log \
  -H "Content-Type: application/json" \
  -d '{
    "honeypot_id": "ESP32-12345678",
    "honeypot_name": "Telnet",
    "honeypot_type": "multi-service",
    "attacker_ip": "192.168.1.5",
    "attacker_port": 54321,
    "target_port": 23,
    "threat_level": "HIGH"
  }'
```

### 2. GET /honeypot/logs
**Retrieve all honeypot logs**
```bash
curl http://localhost:8000/honeypot/logs?limit=50&offset=0
```

Query parameters:
- `limit` (default: 100) - Max results
- `offset` (default: 0) - Pagination
- `threat_level` (optional) - Filter by LOW/MEDIUM/HIGH/CRITICAL

### 3. GET /honeypot/logs/{honeypot_id}
**Get logs for specific honeypot**
```bash
curl http://localhost:8000/honeypot/logs/ESP32-AABBCCDD
```

### 4. GET /honeypot/stats
**Get honeypot statistics**
```bash
curl http://localhost:8000/honeypot/stats
```

Response:
```json
{
  "total_events": 42,
  "high_threat_count": 12,
  "unique_attackers": 8,
  "ports_exploited": 5
}
```

### 5. DELETE /honeypot/logs/{log_id}
**Delete a specific log**
```bash
curl -X DELETE http://localhost:8000/honeypot/logs/1
```

### 6. GET /health
**Health check**
```bash
curl http://localhost:8000/health
```

### 7. GET /docs
**Interactive API documentation (Swagger UI)**
```
http://localhost:8000/docs
```

---

## Testing the Webhook

### Test 1: Manual Event Submission

```bash
curl -X POST http://localhost:8000/honeypot/log \
  -H "Content-Type: application/json" \
  -d '{
    "honeypot_id": "ESP32-TEST",
    "honeypot_name": "Telnet Server",
    "honeypot_type": "multi-service",
    "attacker_ip": "192.168.1.100",
    "attacker_port": 12345,
    "target_port": 23,
    "username_attempted": "testuser",
    "password_attempted": "testpass",
    "commands_executed": ["whoami", "id"],
    "auth_success": false,
    "session_duration_ms": 3000,
    "threat_level": "HIGH"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Honeypot event stored successfully",
  "honeypot_log_id": 1,
  "error": null
}
```

### Test 2: Verify Database Storage

```bash
psql -U postgres -d godseye -c \
  "SELECT id, attacker_ip, target_port, threat_level FROM honeypot_logs ORDER BY id DESC LIMIT 5;"
```

### Test 3: Check Automatic Threat Creation

```bash
psql -U postgres -d godseye -c \
  "SELECT threat_id, user_id, threat_pattern, risk_score, status FROM threats WHERE user_id LIKE 'HONEYPOT_%' ORDER BY threat_id DESC LIMIT 5;"
```

---

## ESP32 Configuration Update in Code

If manually updating ESP32-Honeypot.ino, find the webhook URL section and modify:

**Old (Discord webhook):**
```cpp
WebhookURL = "https://discord.com/api/webhooks/...";
```

**New (GodsEye API):**
```cpp
WebhookURL = "http://192.168.1.100:8000/honeypot/log";
```

The ESP32 code currently sends Discord-formatted messages. To send JSON events instead, update the `logCommand()` function to POST JSON:

**Update in honeypot_api.ino line ~360:**

```cpp
if (WiFi.status() == WL_CONNECTED && WebhookURL.length() > 0) {
    HTTPClient http;
    http.begin(WebhookURL);
    http.addHeader("Content-Type", "application/json");

    // Build JSON event (instead of Discord format)
    String msg = "{\"honeypot_id\":\"" + String(WiFi.macAddress()) +
                 "\",\"honeypot_name\":\"Telnet\",\"honeypot_type\":\"multi-service\"," +
                 "\"attacker_ip\":\"" + ip + "\",\"attacker_port\":0," +
                 "\"target_port\":23,\"commands_executed\":[\"" + escapeJSON(command) + "\"]," +
                 "\"auth_success\":false,\"session_duration_ms\":0,\"threat_level\":\"MEDIUM\"}";

    http.POST(msg);
    http.end();
}
```

---

## Troubleshooting

### Issue: ESP32 can't connect to webhook

**Solutions:**
1. Verify WiFi password is correct in config
2. Check firewall allows port 8000
3. Verify Flask server is running: `python -m backend.api_server`
4. Check IP address (use `ipconfig` to find your PC's IP)

### Issue: Events not appearing in database

**Solutions:**
1. Check server logs for errors
2. Verify honeypot_logs table exists: 
   ```bash
   psql -U postgres -d godseye -c "\d honeypot_logs"
   ```
3. Manually test webhook:
   ```bash
   curl -X POST http://localhost:8000/honeypot/log \
     -d '{"honeypot_id":"TEST"}' \
     -H "Content-Type: application/json"
   ```

### Issue: Database connection fails

**Solutions:**
1. Verify PostgreSQL is running
2. Check credentials in db_config.yaml
3. Test connection: 
   ```bash
   psql -U postgres -d godseye -c "SELECT 1;"
   ```

---

## Next Steps

1. ✅ Update ESP32 config with webhook URL
2. ✅ Start api_server.py
3. ✅ Monitor logs as attackers connect
4. Create dashboard to visualize honeypot data
5. Set up email/Slack alerts for HIGH/CRITICAL threats
6. Analyze attacker patterns using MITRE framework
