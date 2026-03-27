# ESP32 Honeypot Index

## Overview
- **File**: [honeypots/ESP32-Honeypot/ESP32-Honeypot.ino](honeypots/ESP32-Honeypot/ESP32-Honeypot.ino)
- **Platform**: ESP32 microcontroller
- **Type**: Multi-service honeypot with fake Telnet shell emulation
- **Lines**: 1256 total
- **Purpose**: Simulate vulnerable services to detect and log attacker behavior

---

## Configuration & Initialization

### Global Configuration (Lines 1-50)
- **WiFi Credentials**: SSID and password loaded from SPIFFS JSON config
- **Webhook URL**: For external logging/alerting
- **Enabled Ports**: Configurable list of ports to activate
- **Log Storage**: SPIFFS-based file storage with configurable paths

### Variables & Libraries
- `WiFiServer`: 13 separate server instances (one per port)
- `AsyncWebServer webServer`: Web UI for configuration management
- File paths: `/config.json`, `/honeypot.log`

---

## Web Interface (Lines 60-200)

### HTML UI Features
- Form-based configuration
- Port selection checkboxes (FTP, SSH, Telnet, SMTP, DNS, POP3, IMAP, HTTPS, SMB, MySQL, RDP, VNC, HTTP-alt)
- Reboot button
- Reset configuration button
- Show logs button
- Show configuration button

### REST Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/config` | GET | Return JSON configuration |
| `/config` | POST | Update JSON configuration |
| `/log` | GET | Retrieve honeypot log file |
| `/reboot` | POST | Restart ESP32 |
| `/reset` | POST | Delete config and reboot |

### SPIFFS Management
- `loadConfig()` - Load WiFi and service settings from JSON file
- `escapeJSON()` - Sanitize strings for JSON output
- File operations use SPIFFS (SPI Flash File System)

---

## Logging & Webhook System (Lines 360-420)

### Log Structure
```
[timestamp] IP: x.x.x.x - Port: xxxx - Command: <command>
```

### Logging Functions
- `logCommand(ip, port, command)` - Appends to SPIFFS log file
- **Webhook Integration**: Sends Discord-formatted webhook POST to configured URL when WiFi is connected
- **Webhook Format**: 
  ```json
  {
    "content": "📡 **Honeypot**\n🔍 IP: {ip}\n📌 Port: {port}\n💻 Command: {command}\n__________________________"
  }
  ```

### Key Detail
- **NO Direct Database Integration**: Currently only logs to SPIFFS file and Discord webhook
- **Need for Database**: Requires API endpoint for POST events to database

---

## Port Handlers & Service Emulation (Lines 200-350 & Lines 900-1150)

### Banner Grab Services (Simple banners, close connection)
| Port | Service | Banner Response |
|------|---------|-----------------|
| 21 | FTP | `220 ProFTPD 1.3.7c Server (Debian) [::ffff:192.168.1.10]` |
| 22 | SSH | `SSH-2.0-OpenSSH_8.5p1 Debian-1` (keeps open 3 seconds for nmap probes) |
| 25 | SMTP | `220 mail.local ESMTP Exim 4.94.2` |
| 53 | DNS | TCP DNS response to version.bind CHAOS TXT query |
| 110 | POP3 | `+OK Dovecot ready.` |
| 143 | IMAP | `* OK [CAPABILITY IMAP4rev1...] Dovecot ready.` |
| 443 | HTTPS | HTTP/1.1 200 OK (Apache 2.4.52 fake page) |
| 445 | SMB | SMB Core Negotiate Response (Win7 LM 0.12) |
| 3306 | MySQL | MySQL 5.7.33 greeting with handshake protocol |
| 3389 | RDP | RDP Connection-Confirm packet |
| 5900 | VNC | `RFB 003.008` |
| 8080 | HTTP-Alt | HTTP/1.1 200 OK (Apache 2.4.52 fake page) |

### Interactive Telnet Service (Port 23)
- **Full shell emulation** with command interpretation
- **File structure simulation**: `/home`, `/home/pi`, `/home/pi/Documents`, `/home/pi/Downloads`
- **Credential simulation**: Fake AWS keys, MySQL credentials, password lists
- **Process simulation**: Fake `ps aux`, `top`, network stats

---

## Telnet Command Support (Lines 500-1050)

### Authentication Emulation (Lines 500-530)
```
Login: [captures username and logs]
Password: [captures password and logs]
→ Displays fake Ubuntu 20.04.5 LTS welcome banner
→ Drops into shell with pi@ubuntu prompt
```

### Group 1: Exit Commands
- `exit` / `logout` - Disconnect and close connection

### Group 2: System Information (Lines 540-610)
| Command | Output |
|---------|--------|
| `pwd` | Current directory |
| `whoami` | `pi` |
| `uname -a` | Linux Ubuntu kernel info |
| `hostname` | `ubuntu` |
| `uptime` | 1:15 uptime, 2 users, load average |
| `free -h` | 1000M total RAM, 200M used, 600M free |
| `df -h` | 50G filesystem, 31% used |
| `ps aux` | Fake process list (init, systemd, bash) |
| `top` | Interactive-style top output with CPU/memory stats |

### Group 3: File System Navigation (Lines 625-780)
- `ls` / `ls -l` - List files with context-aware output
- `cd ..` / `cd /` / `cd ~` - Navigate directories
- `cd Documents` / `cd Downloads` - Subdirectory navigation
- `mkdir`, `rmdir`, `rm`, `mv`, `cp`, `chmod`, `chown`, `touch` - File operations (simulated)

### Group 4: File Reading (Lines 785-850)
Special files with fake secrets:

**System files:**
- `/etc/passwd` - Fake user database
- `/etc/shadow` - Fake password hashes

**Credentials (honeypot targets):**
- `/home/pi/secrets.txt` - AWS access keys and secrets
- `/home/pi/Documents/mysql_credentials.txt` - MySQL connection details
- `/home/pi/Documents/password_list.txt` - Facebook/Gmail/Twitter passwords
- `/home/pi/Documents/financial_report_2023.xlsx` - Binary file simulation
- `/home/pi/Documents/readme.md` - Markdown file
- `/home/pi/Downloads/malware.sh` - Fake `rm -rf /` script
- `/home/pi/Downloads/helpful_script.py` - Python script stub

### Group 5: Network Commands (Lines 855-900)
| Command | Behavior |
|---------|----------|
| `ifconfig` | Fake eth0 config with 192.168.1.10 |
| `ip addr` | iproute2 style output |
| `ping <target>` | Simulates successful ping |
| `netstat -an` | Shows LISTEN and ESTABLISHED connections |
| `wget` / `curl` | Simulates HTTP download |

### Group 6: Package Management (Lines 905-960)
- `apt-get update` - Simulates apt repository fetching
- `apt-get install` - Simulates package installation

### Group 7: Service Management (Lines 962-1010)
- `service <name> {start|stop|restart|status}` - Simulates systemd service commands
- `systemctl {start|stop|restart|status}` - Alternative systemctl simulation

### Group 8: Privilege Escalation (Lines 1012-1020)
- `sudo` - Always responds with "pi is not in the sudoers file. This incident will be reported."

### Group 9: System Metadata (Lines 1025-1090)
| Command | Output |
|---------|--------|
| `env` | Shell environment variables |
| `set` | Bash set options |
| `alias` | Common shell aliases |
| `history` | Fake command history |
| `iptables` | Firewall rules simulation |
| `id` | User ID output |
| `lsb_release -a` | Ubuntu 20.04.5 LTS info |
| `cat /etc/issue` | Ubuntu release info |
| `cat /proc/version` | Kernel version |
| `cat /proc/cpuinfo` | Intel i7-8565U fake CPU info |
| `lscpu` | CPU architecture details |
| `dmesg` | Boot messages |
| `last` | Login history |
| `finger pi` | User information |

### Group 10: Empty Command Handling
- No response for return-only input

### Group 11: Unknown Command Response
- `bash: <command>: command not found`

---

## Port Startup Logic (Lines 300-350)

Function: `startHoneypot()`
- Iterates through `enabledPorts` vector
- Only starts servers for enabled ports
- Listens for serial "config" command to switch to config mode
- Main event loop accepts connections and routes to appropriate handlers

---

## Serial Configuration Mode (Lines 160-190)

- Serial input monitoring for debugging
- "config" command switches ESP32 to Wi-Fi AP mode for web UI configuration
- AP SSID: `HoneypotConfig`
- AP Password: `HoneyPotConfig123`
- Accessible at: `http://192.168.4.1` (or varies by ESP32 IP)

---

## Initialization Flow

### `setup()` (Lines 1200-1240)
1. Initialize Serial at 115,200 baud
2. Initialize SPIFFS file system
3. Load config from `/config.json`
4. If no config: Enter Web UI configuration mode (AP mode)
5. If config exists:
   - Switch to WiFi Station mode
   - Connect to configured SSID
   - If connection fails: Enter Web UI mode
   - If successful: Start honeypot servers

### `loop()` (Lines 1242-1243)
- **Empty** - main work done in `startHoneypot()` which runs once before loop starts

---

## Connection Handling

### Generic Banner Grab (Lines 430-470)
- `handleBannerGrab(client, port, banner_string)` - Send banner and close
- `handleBannerGrab(client, port, binary_banner, length)` - Binary version for protocols like DNS/SMB/RDP

### Telnet Interactive Session (Lines 500-1100)
- `handleHoneypotClient(client)` - Full telnet shell emulation
- Maintains current directory state per client
- Logs every command typed
- Responds with simulated command output

---

## Files Structure in SPIFFS

```
/config.json          - WiFi SSID, password, webhook URL, enabled ports
/honeypot.log         - Append-only log of all connections and commands
/www/*                - Static web assets for configuration UI
```

---

## Current Limitations & Issues

1. **Database Integration**: 
   - ❌ NO direct database logging
   - ❌ Only logs to SPIFFS file and Discord webhook
   - 🔧 **Need**: API endpoint for POST requests

2. **Telnet Emulation**:
   - No actual file content reading (all hardcoded)
   - No real command execution
   - No persistence across sessions

3. **Banner Accuracy**:
   - Good signatures but simplified (nmap may detect as honeypot)
   - Telnet negotiation strings present for Nmap-friendliness

4. **Logging Granularity**:
   - Per-port per-command only
   - No session tracking (IP + port + full command sequence)

---

## Integration Points for GodsEye Database

### Required Changes

1. **Create API Endpoint** (in Python/FastAPI):
   ```
   POST /honeypot/log
   {
     "honeypot_id": "ESP32-{MAC}",
     "honeypot_name": "Telnet Server",
     "honeypot_type": "multi-service",
     "attacker_ip": "x.x.x.x",
     "attacker_port": xxxx,
     "target_port": xxxx,
     "username_attempted": "string",
     "password_attempted": "string",
     "commands_executed": ["cmd1", "cmd2", ...],
     "auth_success": false,
     "session_duration_ms": xxxx,
     "timestamp": "ISO-8601"
   }
   ```

2. **Update honeypot.ino**:
   - Replace Discord webhook with GodsEye API endpoint
   - POST JSON events instead of Discord messages
   - Track session start/end for duration

3. **Database Schema**:
   - Create `honeypot_logs` table
   - Create auto-alerting trigger for honeypot hits
   - Link to existing `threats` table

---

## Performance Characteristics

- **Memory**: ~200KB free RAM (ESP32 has 520KB SRAM)
- **Storage**: SPIFFS log file grows ~1KB per session
- **Network**: Handles multiple simultaneous connections
- **Latency**: Sub-100ms responses to commands (sufficient for tricking attackers)

---

## Security Considerations

- **No authentication** - Accepts any username/password
- **No command validation** - Accepts any input string
- **No resource limits** - Can be exhausted with large log files
- **Plain text config** - WiFi password visible in `/config.json`
- **Discord webhook URL** - Exposed in config (potential information leak)

---

## Summary of Commands Supported

**Total Command Categories**: 11 groups
- System info: 11 commands
- File navigation: 5 commands
- File operations: 5 commands
- File reading: 8 special files
- Network: 6 commands
- Package management: 2 commands
- Service management: 2 command families
- Privilege escalation: 1 command
- System metadata: 11 commands
- Unknown commands: caught with not-found message

**Total: 60+ command variants**

---

## Next Steps for Integration

1. ✅ Analyze ESP32 honeypot ← Current
2. 🔧 Create honeypot_logs table in database
3. 🔧 Create POST endpoint for honeypot events
4. 🔧 Update ESP32 firmware to POST to new endpoint
5. 🔧 Create honeypot_threat trigger for automatic alert escalation
6. 🔧 Add CLI tool support for honeypot event injection
7. 🔧 Test end-to-end: SSH to ESP32 → Event stored in database → Threat detected
