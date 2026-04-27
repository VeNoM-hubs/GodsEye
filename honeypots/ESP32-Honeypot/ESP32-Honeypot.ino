#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <vector>

String ssid, password, WebhookURL;
const char* configPath = "/config.json";
const char* logPath = "/honeypot_logs.txt";
const char* indexPath = "/index.html";

// Serial input buffer for config command detection
String serialBuffer = "";
unsigned long lastSerialInput = 0;
const unsigned long SERIAL_TIMEOUT = 1000; // 1 second timeout for detecting command without line ending

WiFiServer ftpServer(21);
WiFiServer sshServer(22);
WiFiServer honeypotServer(23);
WiFiServer smtpServer(25);
WiFiServer dnsServer(53);
WiFiServer pop3Server(110);
WiFiServer imapServer(143);
WiFiServer httpServer(443);
WiFiServer smbServer(445);
WiFiServer mysqlServer(3306);
WiFiServer rdpServer(3389);
WiFiServer vncServer(5900);
WiFiServer ahttpServer(8080);

std::vector<uint16_t> enabledPorts;

WebServer webServer(80);
bool honeypotServersStarted = false;
bool configPortalActive = false;


void createFileIfMissing(const char* path, const char* content) {
  if (!SPIFFS.exists(path)) {
    File f = SPIFFS.open(path, FILE_WRITE);
    if (f) {
      f.print(content);
      f.close();
      Serial.println(String("[+] Create : ") + path);
    } else {
      Serial.println(String("[!] Fail to create : ") + path);
    }
  }
}

void initSPIFFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("[!] Error SPIFFS");
    return;
  }

  // Création automatique des fichiers de base
  createFileIfMissing(configPath, "{\"ssid\":\"\",\"password\":\"\",\"webhook\":\"\",\"ports\":[21,22,23,25,53,110,143,443,445,3306,3389,5900,8080]}");
  createFileIfMissing(logPath, "");
  createFileIfMissing(indexPath,
                      "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Honeypot Config</title>"
                      "<style>"
                      "body{font-family:sans-serif;background:#f4f4f4;padding:20px;margin:0;}"
                      "h2{text-align:center;color:#333;}"
                      ".container{max-width:500px;margin:auto;}"
                      "form, .actions{background:#fff;padding:20px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);margin-bottom:20px;}"
                      "label{display:block;margin-top:10px;font-weight:bold;}"
                      "input:not([type=checkbox]){width:100%;padding:10px;margin-top:5px;box-sizing:border-box;border:1px solid #ccc;border-radius:5px;font-family:inherit;}"
                      "input[type=checkbox]{width:auto;height:auto;padding:0;margin-right:8px;vertical-align:middle;}"
                      "button{margin-top:10px;width:100%;padding:12px;border:none;border-radius:5px;cursor:pointer;font-size:16px;}"
                      "#save{background:#28a745;color:white;}#save:hover{background:#218838;}"
                      "#reboot{background:#007bff;color:white;}#reboot:hover{background:#0069d9;}"
                      "#reset{background:#dc3545;color:white;}#reset:hover{background:#c82333;}"
                      "#showlog,#showconfig{background:#6c757d;color:white;}#showlog:hover,#showconfig:hover{background:#5a6268;}"
                      "#output{white-space:pre-wrap;background:#000;color:#0f0;padding:10px;border-radius:5px;max-height:300px;overflow:auto;margin-top:10px;display:none;}"
                      "</style></head><body>"
                      "<div class='container'>"
                      "<h2>Honeypot Configuration</h2>"
                      "<form id='form'>"
                      "<label>Wi-Fi SSID</label><input name='ssid' required>"
                      "<label>Wi-Fi Password</label><input name='password' type='password' required>"
                      "<label>Webhook URL</label><input name='webhook'>"
                      "<label>Ports to enable</label>"
                      "<div style='max-height:200px;overflow:auto;border:1px solid #ccc;padding:10px;border-radius:5px;'>"
                      "<label><input type='checkbox' name='ports' value='21'> FTP (21)</label>"
                      "<label><input type='checkbox' name='ports' value='22'> SSH (22)</label>"
                      "<label><input type='checkbox' name='ports' value='23'> Telnet (23)</label>"
                      "<label><input type='checkbox' name='ports' value='25'> SMTP (25)</label>"
                      "<label><input type='checkbox' name='ports' value='53'> DNS (53)</label>"
                      "<label><input type='checkbox' name='ports' value='110'> POP3 (110)</label>"
                      "<label><input type='checkbox' name='ports' value='143'> IMAP (143)</label>"
                      "<label><input type='checkbox' name='ports' value='443'> HTTPS (443)</label>"
                      "<label><input type='checkbox' name='ports' value='445'> SMB (445)</label>"
                      "<label><input type='checkbox' name='ports' value='3306'> MySQL (3306)</label>"
                      "<label><input type='checkbox' name='ports' value='3389'> RDP (3389)</label>"
                      "<label><input type='checkbox' name='ports' value='5900'> VNC (5900)</label>"
                      "<label><input type='checkbox' name='ports' value='8080'> AHTTP (8080)</label>"
                      "</div>"
                      "<button id='save' type='submit'>Save Configuration</button>"
                      "</form>"
                      "<div class='actions'>"
                      "<button id='reboot'>Reboot Device</button>"
                      "<button id='reset'>Reset Configuration</button>"
                      "<button id='showconfig'>Show Config</button>"
                      "<button id='showlog'>Show Logs</button>"
                      "<pre id='output'></pre>"
                      "</div></div>"
                      "<script>"
                      "fetch('/config').then(r=>r.json()).then(c=>{"
                      "for(let k in c){"
                      "  if(k==='ports'){"
                      "    c[k].forEach(p=>{"
                      "      let cb=document.querySelector(`input[name=ports][value='${p}']`);"
                      "      if(cb)cb.checked=true;"
                      "    });"
                      "  }else{"
                      "    let el=document.querySelector(`[name=${k}]`);"
                      "    if(el)el.value=c[k];"
                      "  }"
                      "}});"
                      "document.getElementById('form').onsubmit=e=>{"
                      "e.preventDefault();"
                      "let form=e.target;"
                      "let data=new FormData(form);"
                      "let ports=[];"
                      "form.querySelectorAll('input[name=ports]:checked').forEach(cb=>ports.push(parseInt(cb.value)));"
                      "let obj=Object.fromEntries(Array.from(data.entries()).filter(([k])=>k!=='ports'));"
                      "obj.ports=ports;"
                      "fetch('/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}).then(()=>alert('Configuration saved.'));"
                      "};"
                      "document.getElementById('reboot').onclick=()=>{"
                      "fetch('/reboot',{method:'POST'}).then(()=>alert('Rebooting...'));};"
                      "document.getElementById('reset').onclick=()=>{"
                      "if(confirm('Reset configuration?')){"
                      "fetch('/reset',{method:'POST'}).then(()=>alert('Config reset.'));}};"
                      "document.getElementById('showlog').onclick=()=>{"
                      "fetch('/log').then(r=>r.text()).then(t=>{let o=document.getElementById('output');o.style.display='block';o.textContent=t;});};"
                      "document.getElementById('showconfig').onclick=()=>{"
                      "fetch('/config').then(r=>r.json()).then(c=>{let o=document.getElementById('output');o.style.display='block';o.textContent=JSON.stringify(c,null,2);});};"
                      "</script></body></html>");


}

bool loadConfig() {
  File file = SPIFFS.open(configPath, "r");
  if (!file || file.size() == 0) return false;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, file);
  file.close();
  if (err) return false;

  ssid = doc["ssid"].as<String>();
  password = doc["password"].as<String>();
  WebhookURL = doc["webhook"].as<String>();

  enabledPorts.clear();
  for (JsonVariant port : doc["ports"].as<JsonArray>()) {
    enabledPorts.push_back(port.as<uint16_t>());
  }

  return ssid.length() > 0 && password.length() > 0;
}

void startHoneypot() {
  Serial.println("\n[*] Starting honeypot servers...");
  
  auto tryBegin = [](uint16_t port, WiFiServer & srv) {
    if (std::find(enabledPorts.begin(), enabledPorts.end(), port) != enabledPorts.end()) {
      srv.begin();
      Serial.println("[+] Honeypot port LISTENING: " + String(port));
      return true;
    } else {
      Serial.println("[-] Port " + String(port) + " disabled in config");
      return false;
    }
  };
  
  int boundPorts = 0;
  if (tryBegin(21,  ftpServer)) boundPorts++;
  if (tryBegin(22,  sshServer)) boundPorts++;
  if (tryBegin(23,  honeypotServer)) boundPorts++;
  if (tryBegin(25,  smtpServer)) boundPorts++;
  if (tryBegin(53,  dnsServer)) boundPorts++;
  if (tryBegin(110, pop3Server)) boundPorts++;
  if (tryBegin(143, imapServer)) boundPorts++;
  if (tryBegin(443, httpServer)) boundPorts++;
  if (tryBegin(445, smbServer)) boundPorts++;
  if (tryBegin(3306, mysqlServer)) boundPorts++;
  if (tryBegin(3389, rdpServer)) boundPorts++;
  if (tryBegin(5900, vncServer)) boundPorts++;
  if (tryBegin(8080, ahttpServer)) boundPorts++;
  
  if (enabledPorts.size() == 0) {
    Serial.println("[!] WARNING: No ports enabled! Check config file at /config.json");
    Serial.println("[*] Add port 23 to enable Telnet honeypot");
    } else if (boundPorts == 0) {
      Serial.println("[!] ERROR: No ports could be bound! Possible causes:");
      Serial.println("    - Ports already in use");
      Serial.println("    - WiFi not connected");
      Serial.println("    - Out of memory");
  }
  
  honeypotServersStarted = true;
  Serial.println("[+] Honeypot mode active. " + String(boundPorts) + "/" + String(enabledPorts.size()) + " ports successfully bound.");
  Serial.println("[*] Type 'status' in serial monitor for diagnostics");
}


void setupWebUI() {
  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_AP);

  // --- GET / : serve config page ---
  webServer.on("/", HTTP_GET, []() {
    File file = SPIFFS.open(indexPath, "r");
    if (!file) {
      webServer.send(500, "text/plain", "Unable to open index.html");
      return;
    }

    webServer.streamFile(file, "text/html");
    file.close();
  });

  // --- GET /config : return JSON config file ---
  webServer.on("/config", HTTP_GET, []() {
    File file = SPIFFS.open(configPath, "r");
    if (!file) {
      webServer.send(500, "application/json", "{\"error\":\"Unable to open config file\"}");
      return;
    }

    String json = file.readString();
    file.close();

    webServer.sendHeader("Cache-Control", "no-store");
    webServer.send(200, "application/json", json);
  });

  // --- POST /config : overwrite JSON config ---
  webServer.on("/config", HTTP_POST, []() {
    if (!webServer.hasArg("plain")) {
      webServer.send(400, "application/json", "{\"error\":\"Missing JSON body\"}");
      return;
    }

    String body = webServer.arg("plain");
    File file = SPIFFS.open(configPath, "w");
    if (!file) {
      webServer.send(500, "text/plain", "Error: Cannot write config file");
      return;
    }
    file.print(body);
    file.close();
    webServer.send(200, "application/json", "{\"status\":\"OK\"}");
  });

  // --- GET /log : return the content of the log file ---
  webServer.on("/log", HTTP_GET, []() {
    File file = SPIFFS.open(logPath, "r");
    if (!file) {
      webServer.send(500, "text/plain", "Cannot open log file");
      return;
    }

    String logContent = file.readString();
    file.close();

    webServer.sendHeader("Cache-Control", "no-store");
    webServer.send(200, "text/plain", logContent);
  });

  // --- POST /reboot : restart the ESP32 ---
  webServer.on("/reboot", HTTP_POST, []() {
    webServer.send(200, "text/plain", "Rebooting...");
    delay(500);
    ESP.restart();
  });

  // --- POST /reset : delete config and reboot ---
  webServer.on("/reset", HTTP_POST, []() {
    SPIFFS.remove(configPath);
    webServer.send(200, "text/plain", "Configuration reset...");
    delay(500);
  });

  // Enable AP mode for initial setup
  WiFi.softAP("HoneypotConfig", "HoneyPotConfig123");
  Serial.println("\n╔════════════════════════════════════════════════╗");
  Serial.println("║    CONFIGURATION MODE - Access Point Active    ║");
  Serial.println("╚════════════════════════════════════════════════╝");
  Serial.println("[*] Configuration Mode Enabled");
  Serial.println("[+] Connect to Wi-Fi SSID: HoneypotConfig");
  Serial.println("[+] Password             : HoneyPotConfig123");
  Serial.println("[+] Web Interface        : http://" + WiFi.softAPIP().toString());
  Serial.println("\n[HINT] Type 'config' in serial monitor to re-enter config mode anytime\n");

  webServer.begin();
  configPortalActive = true;

}


String escapeJSON(String s) {
  String result = "";

  for (unsigned int i = 0; i < s.length(); i++) {
    char c = s[i];
    // Autoriser seulement les caractères imprimables + retour chariot et saut de ligne
    if (c >= 32 || c == '\n' || c == '\r') {
      switch (c) {
        case '\\': result += "\\\\"; break;
        case '"': result += "\\\""; break;
        case '\n': result += "\\n"; break;
        case '\r': result += "\\r"; break;
        default: result += c; break;
      }
    }
  }

  return result;
}

void logCommand(String ip, uint16_t port, String command) {
  File logFile = SPIFFS.open(logPath, FILE_APPEND);
  if (!logFile) return;

  logFile.println("[" + String(millis()) + "] IP: " + ip + " - Port: " + String(port) + " - Command: " + command);
  logFile.close();

  Serial.println("IP: " + ip + " | Port: " + String(port) + " | CMD: " + command + "|Escaped " + escapeJSON(command));

  if (WiFi.status() == WL_CONNECTED && WebhookURL.length() > 0) {
    HTTPClient http;
    http.begin(WebhookURL);
    http.addHeader("Content-Type", "application/json");

    String msg = "{\"content\":\"📡 **Honeypot**\\n🔍 IP: " + ip +
                 "\\n📌 Port: " + String(port) +
                 "\\n💻 Command: " + escapeJSON(command) +
                 "\\n__________________________\"}";

    http.POST(msg);
    http.end();
  }
}


// Handle serial input to detect "config" command
// Works with any line ending (CR, LF, CRLF, or no line ending after timeout)
void handleSerialInput() {
  while (Serial.available()) {
    char c = Serial.read();
    lastSerialInput = millis();
    
    // Handle different line endings
    if (c == '\n' || c == '\r') {
      // Command received with line ending
      serialBuffer.trim();
      serialBuffer.toLowerCase();
      
      if (serialBuffer == "config") {
        Serial.println("\n[*] Config command detected - Entering configuration mode...");
        // Disconnect from WiFi and reset config mode
        WiFi.disconnect(true);
        delay(100);
        configPortalActive = false;
        honeypotServersStarted = false;
        setupWebUI();
      }
      else if (serialBuffer == "status" || serialBuffer == "info") {
        // Print diagnostic information
        printDiagnostics();
      }
      serialBuffer = ""; // Reset buffer
    } else if (c >= 32) {
      // Printable character - add to buffer (max 20 chars to prevent overflow)
      if (serialBuffer.length() < 20) {
        serialBuffer += c;
        Serial.print(c); // Echo the character
      }
    }
  }
  
  // Check for timeout (user typed "config" without line ending and waited)
  if (serialBuffer.length() > 0 && (millis() - lastSerialInput > SERIAL_TIMEOUT)) {
    serialBuffer.trim();
    serialBuffer.toLowerCase();
    
    if (serialBuffer == "config") {
      Serial.println("\n[*] Config command detected (no line ending) - Entering configuration mode...");
      // Disconnect from WiFi and reset config mode
      WiFi.disconnect(true);
      delay(100);
      configPortalActive = false;
      honeypotServersStarted = false;
      setupWebUI();
    }
    serialBuffer = ""; // Reset buffer
  }
}

// Print diagnostic information to serial
void printDiagnostics() {
  Serial.println("\n╔════════════════════════════════════════════════╗");
  Serial.println("║           HONEYPOT DIAGNOSTICS                 ║");
  Serial.println("╚════════════════════════════════════════════════╝");
  
  Serial.println("\n[WiFi Status]");
  Serial.println("  WiFi Status: " + String(WiFi.status() == WL_CONNECTED ? "CONNECTED" : "DISCONNECTED"));
  Serial.println("  Local IP: " + WiFi.localIP().toString());
  Serial.println("  Gateway: " + WiFi.gatewayIP().toString());
  Serial.println("  SSID: " + String(WiFi.SSID()));
  Serial.println("  RSSI: " + String(WiFi.RSSI()) + " dBm");
  Serial.println("  MAC: " + WiFi.macAddress());
  
  Serial.println("\n[Server Status]");
  Serial.println("  Config Portal Active: " + String(configPortalActive ? "YES" : "NO"));
  Serial.println("  Honeypot Started: " + String(honeypotServersStarted ? "YES" : "NO"));
  
  Serial.println("\n[Enabled Ports] (" + String(enabledPorts.size()) + " total)");
  for (uint16_t port : enabledPorts) {
    Serial.println("  - Port " + String(port));
  }
  
  Serial.println("\n[Memory Info]");
  Serial.println("  Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
  Serial.println("  Max Alloc Heap: " + String(ESP.getMaxAllocHeap()) + " bytes");
  
  Serial.println("\n[Commands]");
  Serial.println("  'config' - Enter configuration mode");
  Serial.println("  'status' - Show this diagnostic info");
  Serial.println("\n");
}

String dumpBytes(WiFiClient &c, size_t maxLen = 256, uint32_t timeout = 250) {
  String s;
  unsigned long t0 = millis();
  while (millis() - t0 < timeout && s.length() < maxLen && c.connected()) {
    while (c.available() && s.length() < maxLen) {
      uint8_t b = c.read();
      if (isprint(b) || b == '\r' || b == '\n')
        s += (char)b;
      else {
        char buf[5];
        sprintf(buf, "\\x%02X", b);
        s += buf;
      }
    }
    delay(1);
  }
  return s.length() ? s : "(no data)";
}


void handleBannerGrab(WiFiClient client, uint16_t port, const char* banner) {
  if (!client.connected()) return;
  String ip = client.remoteIP().toString();
  String payload = dumpBytes(client);
  client.write((const uint8_t*)banner, strlen(banner));
  delay(50);
  client.stop();
  logCommand(ip, port, payload);
}


void handleBannerGrab(WiFiClient client, uint16_t port, const uint8_t* banner, size_t len) {
  if (!client.connected()) return;
  String ip = client.remoteIP().toString();
  String payload = dumpBytes(client);
  client.write(banner, len);
  delay(50);
  client.stop();
  logCommand(ip, port, payload);
}



String readLine(WiFiClient &client, bool echo = false) {
  String line = "";
  unsigned long timeout = millis() + 30000; // 30 second timeout
  
  while (client.connected() && millis() < timeout) {
    if (client.available()) {
      char c = client.read();
      if (c == '\r') continue;
      if (c == '\n') break;
      line += c;
      if (echo) client.print(c);
    }
    delay(10); // Small delay to prevent CPU spinning
  }
  
  if (millis() >= timeout) {
    Serial.println("[!] Telnet timeout on readLine()");
  }
  
  return line;
}

// -- Handle interaction with a single Telnet client --
void handleHoneypotClient(WiFiClient client) {
  String ip = client.remoteIP().toString();
  
  if (!client.connected()) {
    Serial.println("[!] Client already disconnected");
    return;
  }

  // Prompt pour le login
  client.print("\r\nlogin: ");
  client.flush();
  String username = readLine(client, false);  // pas d'écho
  username.trim();
  
  if (!client.connected()) {
    Serial.println("[!] Client disconnected during login");
    return;
  }
  
  logCommand(ip, 23, "LOGIN username: " + username);

  // Prompt pour le password
  client.print("Password: ");
  client.flush();
  String password = readLine(client, false);
  password.trim();
  
  if (!client.connected()) {
    Serial.println("[!] Client disconnected during password entry");
    return;
  }
  
  logCommand(ip, 23, "LOGIN password: " + password);

  // Simulation d’un login réussi (peu importe les identifiants)
  client.println("\r\nWelcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-109-generic x86_64)");
  client.println(" * Documentation:  https://help.ubuntu.com");
  client.println(" * Management:     https://landscape.canonical.com");
  client.println(" * Support:        https://ubuntu.com/advantage\r\n");

  // Émulation d’un shell
  String currentDirectory = "/home/pi";
  String prompt = "pi@ubuntu:~$ ";

  while (client.connected()) {
    client.print(prompt);
    String command = readLine(client, false); // on ne renvoie jamais les caractères
    command.trim();

    // Log de la commande
    logCommand(client.remoteIP().toString(), 23, command);

    //------------------------------------------------
    // 1. Commandes de sortie
    //------------------------------------------------
    if (command.equalsIgnoreCase("exit") || command.equalsIgnoreCase("logout")) {
      client.println("Goodbye.");
      break;
    }

    //------------------------------------------------
    // 2. Commandes classiques
    //------------------------------------------------
    else if (command.equals("pwd")) {
      client.println(currentDirectory);
    }
    else if (command.equals("whoami")) {
      client.println("pi");
    }
    else if (command.equals("uname -a")) {
      client.println("Linux ubuntu 5.4.0-109-generic #123-Ubuntu SMP x86_64 GNU/Linux");
    }
    else if (command.equals("hostname")) {
      client.println("ubuntu");
    }
    else if (command.equals("uptime")) {
      client.println(" 12:15:01 up 1:15,  2 users,  load average: 0.00, 0.03, 0.00");
    }
    else if (command.equals("free -h")) {
      client.println("              total        used        free      shared  buff/cache   available");
      client.println("Mem:          1000M        200M        600M         10M        200M        700M");
      client.println("Swap:         1024M          0B       1024M");
    }
    else if (command.equals("df -h")) {
      client.println("Filesystem      Size  Used Avail Use% Mounted on");
      client.println("/dev/sda1        50G   15G   33G  31% /");
      client.println("tmpfs           100M  1.2M   99M   2% /run");
      client.println("tmpfs           500M     0  500M   0% /dev/shm");
    }
    else if (command.equals("ps aux")) {
      client.println("USER       PID  %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND");
      client.println("root         1   0.0  0.1  22564  1124 ?        Ss   12:00   0:01 /sbin/init");
      client.println("root       539   0.0  0.3  46896  3452 ?        Ss   12:00   0:00 /lib/systemd/systemd-journald");
      client.println("pi        1303   0.0  0.2  10820  2220 pts/0    Ss+  12:05   0:00 bash");
      client.println("pi        1304   0.0  0.2  10820  2152 pts/1    Ss+  12:06   0:00 bash");
    }
    else if (command.equals("top")) {
      client.println("top - 12:10:11 up  1:10,  2 users,  load average: 0.01, 0.05, 0.00");
      client.println("Tasks:  93 total,   1 running,  92 sleeping,   0 stopped,   0 zombie");
      client.println("%Cpu(s):  0.0 us,  0.2 sy,  0.0 ni, 99.7 id,  0.1 wa,  0.0 hi,  0.0 si,  0.0 st");
      client.println("MiB Mem :   1000.0 total,    600.0 free,    200.0 used,    200.0 buff/cache");
      client.println("MiB Swap:   1024.0 total,   1024.0 free,      0.0 used.    700.0 avail Mem");
      client.println("");
      client.println("  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND");
      client.println(" 1303 pi        20   0   10820   2220   2168 S   0.0  0.2   0:00.03 bash");
      client.println(" 1304 pi        20   0   10820   2152   2096 S   0.0  0.2   0:00.01 bash");
    }

    //------------------------------------------------
    // 3. Navigation et gestion de fichiers
    //------------------------------------------------
    else if (command.startsWith("ls")) {
      // On affiche des fichiers différents selon currentDirectory
      bool longListing = (command.indexOf("-l") >= 0);

      // /home/pi
      if (currentDirectory.equals("/home/pi")) {
        if (longListing) {
          client.println("total 20");
          client.println("drwxr-xr-x  2 pi  pi  4096 Jan  1 12:00 Documents");
          client.println("drwxr-xr-x  2 pi  pi  4096 Jan  1 12:00 Downloads");
          client.println("-rw-r--r--  1 pi  pi   220 Jan  1 12:00 .bashrc");
          client.println("-rw-r--r--  1 pi  pi  3523 Jan  1 12:00 .profile");
          client.println("-rw-r--r--  1 pi  pi    50 Jan  1 12:00 secrets.txt");
        } else {
          client.println("Documents  Downloads  .bashrc  .profile  secrets.txt");
        }
      }
      // /home/pi/Documents
      else if (currentDirectory.equals("/home/pi/Documents")) {
        if (longListing) {
          client.println("total 16");
          client.println("-rw-r--r--  1 pi  pi   80 Jan  1 12:00 mysql_credentials.txt");
          client.println("-rw-r--r--  1 pi  pi  120 Jan  1 12:00 password_list.txt");
          client.println("-rw-r--r--  1 pi  pi  600 Jan  1 12:00 financial_report_2023.xlsx");
          client.println("-rw-r--r--  1 pi  pi   20 Jan  1 12:00 readme.md");
        } else {
          client.println("mysql_credentials.txt  password_list.txt  financial_report_2023.xlsx  readme.md");
        }
      }
      // /home/pi/Downloads
      else if (currentDirectory.equals("/home/pi/Downloads")) {
        if (longListing) {
          client.println("total 8");
          client.println("-rw-r--r--  1 pi  pi  102 Jan  1 12:00 malware.sh");
          client.println("-rw-r--r--  1 pi  pi  250 Jan  1 12:00 helpful_script.py");
        } else {
          client.println("malware.sh  helpful_script.py");
        }
      }
      else if (currentDirectory.equals("/home")) {
        if (longListing) {
          client.println("total 8");
          client.println("drw-r--r--  1 pi  pi  102 Jan  1 12:00 pi");
        } else {
          client.println("pi");
        }
      }
      else if (currentDirectory.equals("/")) {
        if (longListing) {
          client.println("total 8");
          client.println("drw-r--r--  1 pi  pi  102 Jan  1 12:00 home");
        } else {
          client.println("home");
        }
      }
      // Autres répertoires
      else {
        // Par défaut, on met un ls vide ou un message
        client.println("No files found.");
      }
    }
    else if (command.startsWith("cd ")) {
      String newDir = command.substring(3);
      newDir.trim();

      // Simulation du changement de répertoire
      if (newDir.equals("..")) {
        // Retour en arrière dans l'arborescence
        if (currentDirectory.equals("/home/pi")) {
          currentDirectory = "/home";
          prompt = "pi@ubuntu:/home$ ";
        }
        else if (currentDirectory.equals("/home")) {
          currentDirectory = "/";
          prompt = "pi@ubuntu:/$ ";
        }
        else if (currentDirectory.equals("/")) {
          client.println("bash: cd: ..: No such file or directory");
        }
        else {
          client.println("bash: cd: ..: No such file or directory");
        }
      }
      else if (newDir.equals("/") || newDir.equals("~")) {
        // Aller à la racine ou au répertoire utilisateur
        currentDirectory = (newDir.equals("~")) ? "/home/pi" : "/";
        prompt = (newDir.equals("~")) ? "pi@ubuntu:~$ " : "pi@ubuntu:/$ ";
      }
      else if (newDir.equals("home") && currentDirectory.equals("/")) {
        // Aller explicitement à /home depuis /
        currentDirectory = "/home";
        prompt = "pi@ubuntu:/home$ ";
      }
      else if (newDir.equals("pi") && currentDirectory.equals("/home")) {
        // Aller explicitement à /home/pi depuis /home
        currentDirectory = "/home/pi";
        prompt = "pi@ubuntu:~$ ";
      }
      else if (newDir.equals("Documents") && currentDirectory.equals("/home/pi")) {
        // Aller à Documents uniquement si on est dans /home/pi
        currentDirectory = "/home/pi/Documents";
        prompt = "pi@ubuntu:~/Documents$ ";
      }
      else if (newDir.equals("Downloads") && currentDirectory.equals("/home/pi")) {
        // Aller à Downloads uniquement si on est dans /home/pi
        currentDirectory = "/home/pi/Downloads";
        prompt = "pi@ubuntu:~/Downloads$ ";
      }
      else {
        // Gestion des chemins absolus ou chemins non valides
        if (newDir.startsWith("/home/pi/")) {
          if (newDir.equals("/home/pi/Documents")) {
            currentDirectory = "/home/pi/Documents";
            prompt = "pi@ubuntu:~/Documents$ ";
          } else if (newDir.equals("/home/pi/Downloads")) {
            currentDirectory = "/home/pi/Downloads";
            prompt = "pi@ubuntu:~/Downloads$ ";
          } else {
            client.println("bash: cd: " + newDir + ": No such file or directory");
          }
        } else if (newDir.startsWith("/home/")) {
          currentDirectory = "/home";
          prompt = "pi@ubuntu:/home$ ";
        } else {
          client.println("bash: cd: " + newDir + ": No such file or directory");
        }
      }
    }
    else if (command.startsWith("mkdir ")) {
      String dirName = command.substring(6);
      dirName.trim();
      client.println("Directory '" + dirName + "' created.");
    }
    else if (command.startsWith("rmdir ")) {
      String dirName = command.substring(6);
      dirName.trim();
      client.println("Directory '" + dirName + "' removed.");
    }
    else if (command.startsWith("rm ")) {
      client.println("File removed successfully.");
    }
    else if (command.startsWith("mv ") || command.startsWith("cp ")) {
      client.println("Operation completed successfully.");
    }
    else if (command.startsWith("chmod ")) {
      client.println("Permissions changed.");
    }
    else if (command.startsWith("chown ")) {
      client.println("Ownership changed.");
    }
    else if (command.startsWith("touch ")) {
      String fileName = command.substring(6);
      fileName.trim();
      client.println("File '" + fileName + "' created or timestamp updated.");
    }

    //------------------------------------------------
    // 4. Lecture de fichiers (cat)
    //------------------------------------------------
    else if (command.startsWith("cat ")) {
      String fileName = command.substring(4);
      fileName.trim();

      // Gestion de cas particuliers absolus
      if (fileName == "/etc/passwd") {
        client.println("root:x:0:0:root:/root:/bin/bash");
        client.println("daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin");
        client.println("bin:x:2:2:bin:/bin:/usr/sbin/nologin");
        client.println("sys:x:3:3:sys:/dev:/usr/sbin/nologin");
        client.println("pi:x:1000:1000:,,,:/home/pi:/bin/bash");
      }
      else if (fileName == "/etc/shadow") {
        client.println("root:*:18948:0:99999:7:::");
        client.println("daemon:*:18948:0:99999:7:::");
        client.println("bin:*:18948:0:99999:7:::");
        client.println("sys:*:18948:0:99999:7:::");
        client.println("pi:$6$randomsalt$somehashedpassword:18948:0:99999:7:::");
      }
      else {
        // On gère les chemins relatifs ou absolus (simples) en tenant compte du currentDirectory
        // Pour simplifier, on traite les fichiers "connus" en fonction du répertoire courant

        // Normaliser si besoin (ex: cat /home/pi/Documents/...).
        // On peut faire un check direct, ou reconstituer le "fullPath".
        String fullPath = fileName;
        if (!fileName.startsWith("/")) {
          // c'est un chemin relatif => on le rattache au currentDirectory
          fullPath = currentDirectory + "/" + fileName;
        }

        // /home/pi/secrets.txt
        if (fullPath == "/home/pi/secrets.txt") {
          client.println("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7NGGYUNGGYD");
          client.println("AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYNGGYUNGGYD");
        }
        // /home/pi/Documents/mysql_credentials.txt
        else if (fullPath == "/home/pi/Documents/mysql_credentials.txt") {
          client.println("host=localhost");
          client.println("user=admin");
          client.println("password=My5up3rP@ss");
          client.println("database=production_db");
        }
        // /home/pi/Documents/password_list.txt
        else if (fullPath == "/home/pi/Documents/password_list.txt") {
          client.println("facebook:  fbpass123");
          client.println("gmail:     gmPass!0");
          client.println("twitter:   tw_pass_2025");
        }
        // /home/pi/Documents/financial_report_2023.xlsx (fichier binaire, on simule)
        else if (fullPath == "/home/pi/Documents/financial_report_2023.xlsx") {
          client.println("This appears to be a binary file (Excel).");
          client.println("�PK\003\004... (truncated) ...");
        }
        // /home/pi/Documents/readme.md
        else if (fullPath == "/home/pi/Documents/readme.md") {
          client.println("# README");
          client.println("This is a sample markdown file. Nothing special here.");
        }
        // /home/pi/Downloads/malware.sh
        else if (fullPath == "/home/pi/Downloads/malware.sh") {
          client.println("#!/bin/bash");
          client.println("echo 'Running malware...'");
          client.println("rm -rf / --no-preserve-root");
        }
        // /home/pi/Downloads/helpful_script.py
        else if (fullPath == "/home/pi/Downloads/helpful_script.py") {
          client.println("#!/usr/bin/env python3");
          client.println("print('Just a helpful script.')");
        }
        // Sinon, fichier inconnu
        else {
          client.println("cat: " + fileName + ": No such file or directory");
        }
      }
    }

    //------------------------------------------------
    // 5. Commandes réseau souvent utilisées
    //------------------------------------------------
    else if (command.equals("ifconfig")) {
      client.println("eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500");
      client.println("        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255");
      client.println("        inet6 fe80::d6be:d9ff:fe1b:220c  prefixlen 64  scopeid 0x20<link>");
      client.println("        RX packets 1243  bytes 234567 (234.5 KB)");
      client.println("        TX packets 981   bytes 123456 (123.4 KB)");
    }
    else if (command.equals("ip addr")) {
      client.println("1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000");
      client.println("    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00");
      client.println("    inet 127.0.0.1/8 scope host lo");
      client.println("    inet6 ::1/128 scope host ");
      client.println("2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000");
      client.println("    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff");
      client.println("    inet 192.168.1.10/24 brd 192.168.1.255 scope global eth0");
    }
    else if (command.startsWith("ping ")) {
      String target = command.substring(5);
      client.println("PING " + target + " (1.2.3.4) 56(84) bytes of data.");
      client.println("64 bytes from 1.2.3.4: icmp_seq=1 ttl=64 time=0.042 ms");
      client.println("64 bytes from 1.2.3.4: icmp_seq=2 ttl=64 time=0.043 ms");
      client.println("--- " + target + " ping statistics ---");
      client.println("2 packets transmitted, 2 received, 0% packet loss, time 1ms");
    }
    else if (command.equals("netstat -an")) {
      client.println("Active Internet connections (servers and established)");
      client.println("Proto Recv-Q Send-Q Local Address           Foreign Address         State");
      client.println("tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN");
      client.println("tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN");
      client.println("tcp        0      0 192.168.1.10:23         192.168.1.100:54321     ESTABLISHED");
    }
    else if (command.startsWith("wget ") || command.startsWith("curl ")) {
      String url = command.substring(command.indexOf(" ") + 1);
      client.println("Connecting to " + url + "...");
      client.println("HTTP request sent, awaiting response... 200 OK");
      client.println("Length: 1024 (1.0K) [text/html]");
      client.println("Saving to: ‘index.html’");
      client.println("index.html         100%[==========>]  1.00K  --.-KB/s    in 0s");
      client.println("Download completed.");
    }

    //------------------------------------------------
    // 6. Commandes de services et de packages
    //------------------------------------------------
    else if (command.startsWith("apt-get ")) {
      if (command.indexOf("update") >= 0) {
        client.println("Get:1 http://archive.ubuntu.com/ubuntu focal InRelease [265 kB]");
        client.println("Get:2 http://archive.ubuntu.com/ubuntu focal-updates InRelease [114 kB]");
        client.println("Reading package lists... Done");
      }
      else if (command.indexOf("install") >= 0) {
        client.println("Reading package lists... Done");
        client.println("Building dependency tree");
        client.println("Reading state information... Done");
        client.println("The following NEW packages will be installed:");
        client.println("  <some-package>");
        client.println("0 upgraded, 1 newly installed, 0 to remove and 5 not upgraded.");
        client.println("Need to get 0 B/123 kB of archives.");
        client.println("After this operation, 345 kB of additional disk space will be used.");
        client.println("Selecting previously unselected package <some-package>.");
        client.println("(Reading database ... 45% )");
        client.println("Unpacking <some-package> (from <some-package>.deb) ...");
        client.println("Setting up <some-package> ...");
        client.println("Processing triggers for man-db (2.9.1-1) ...");
      }
      else {
        client.println("E: Invalid operation " + command.substring(7));
      }
    }
    else if (command.startsWith("service ")) {
      // service <nom> start/stop/status/restart
      if (command.indexOf("start") >= 0) {
        client.println("Starting service " + command.substring(8) + "...");
        client.println("Service started.");
      }
      else if (command.indexOf("stop") >= 0) {
        client.println("Stopping service " + command.substring(8) + "...");
        client.println("Service stopped.");
      }
      else if (command.indexOf("restart") >= 0) {
        client.println("Restarting service " + command.substring(8) + "...");
        client.println("Service restarted.");
      }
      else if (command.indexOf("status") >= 0) {
        client.println(command.substring(8) + " is running.");
      }
      else {
        client.println("Usage: service <service> {start|stop|restart|status}");
      }
    }
    else if (command.startsWith("systemctl ")) {
      // ex: systemctl status ssh
      if (command.indexOf("start") >= 0) {
        client.println("Systemd: Starting service...");
        client.println("Done.");
      }
      else if (command.indexOf("stop") >= 0) {
        client.println("Systemd: Stopping service...");
        client.println("Done.");
      }
      else if (command.indexOf("restart") >= 0) {
        client.println("Systemd: Restarting service...");
        client.println("Done.");
      }
      else if (command.indexOf("status") >= 0) {
        client.println("● ssh.service - OpenBSD Secure Shell server");
        client.println("   Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)");
        client.println("   Active: active (running) since Wed 2025-01-23 12:00:00 UTC; 1h 4min ago");
        client.println(" Main PID: 600 (sshd)");
        client.println("    Tasks: 1 (limit: 4915)");
        client.println("   CGroup: /system.slice/ssh.service");
      }
      else {
        client.println("systemctl: command not recognized or incomplete arguments.");
      }
    }

    //------------------------------------------------
    // 7. Commandes d’élévation de privilèges
    //------------------------------------------------
    else if (command.startsWith("sudo ")) {
      client.println("[sudo] password for pi: ");
      delay(1000);
      client.println("pi is not in the sudoers file.  This incident will be reported.");
    }

    //------------------------------------------------
    // 8. Commandes diverses
    //------------------------------------------------
    else if (command.equals("env")) {
      client.println("SHELL=/bin/bash");
      client.println("PWD=" + currentDirectory);
      client.println("LOGNAME=pi");
      client.println("HOME=/home/pi");
      client.println("LANG=C.UTF-8");
    }
    else if (command.equals("set")) {
      client.println("BASH=/bin/bash");
      client.println("BASHOPTS=cmdhist:complete_fullquote:expand_aliases:extquote:force_fignore:histappend:interactive_comments:progcomp");
      client.println("PWD=" + currentDirectory);
      client.println("HOME=/home/pi");
      client.println("LANG=C.UTF-8");
    }
    else if (command.equals("alias")) {
      client.println("alias ls='ls --color=auto'");
      client.println("alias ll='ls -alF'");
      client.println("alias l='ls -CF'");
    }
    else if (command.equals("history")) {
      // Petite simulation d’historique
      client.println("    1  pwd");
      client.println("    2  ls -l");
      client.println("    3  whoami");
      client.println("    4  cat /etc/passwd");
      client.println("    5  sudo su");
    }
    else if (command.equals("iptables")) {
      client.println("Chain INPUT (policy ACCEPT)");
      client.println("target     prot opt source               destination         ");
      client.println("Chain FORWARD (policy ACCEPT)");
      client.println("target     prot opt source               destination         ");
      client.println("Chain OUTPUT (policy ACCEPT)");
      client.println("target     prot opt source               destination         ");
    }
    //------------------------------------------------
    // 9. Commande supplémentaire.
    //------------------------------------------------
    else if (command.equals("id")) {
      client.println("uid=1000(pi) gid=1000(pi) groups=1000(pi)");
    }
    else if (command.equals("lsb_release -a")) {
      client.println("Distributor ID: Ubuntu");
      client.println("Description:    Ubuntu 20.04.5 LTS");
      client.println("Release:        20.04");
      client.println("Codename:       focal");
    }
    else if (command.equals("cat /etc/issue")) {
      client.println("Ubuntu 20.04.5 LTS \\n+ \\l");
    }
    else if (command.equals("cat /proc/version")) {
      client.println("Linux version 5.4.0-109-generic (buildd@lgw01-amd64-039) (gcc version 9.3.0, GNU ld version 2.34) #123-Ubuntu SMP");
    }
    else if (command.equals("cat /proc/cpuinfo")) {
      client.println("processor   : 0");
      client.println("vendor_id   : GenuineIntel");
      client.println("cpu family  : 6");
      client.println("model       : 158");
      client.println("model name  : Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz");
      client.println("stepping    : 10");
      client.println("microcode   : 0xca");
      client.println("cpu MHz     : 1992.000");
      client.println("cache size  : 8192 KB");
    }
    else if (command.equals("lscpu")) {
      client.println("Architecture:        x86_64");
      client.println("CPU op-mode(s):      32-bit, 64-bit");
      client.println("Byte Order:          Little Endian");
      client.println("CPU(s):              4");
      client.println("Vendor ID:           GenuineIntel");
      client.println("Model name:          Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz");
      client.println("CPU MHz:             1992.000");
    }
    else if (command.equals("dmesg")) {
      client.println("[    0.000000] Booting Linux on physical CPU 0");
      client.println("[    0.123456] Linux version 5.4.0-109-generic (buildd@lgw01-amd64-039) (gcc version 9.3.0, GNU ld version 2.34) #123-Ubuntu SMP");
    }
    else if (command.equals("last")) {
      client.println("pi     pts/0        192.168.1.10    Wed Feb  3 12:00   still logged in");
      client.println("reboot system boot  5.4.0-109-generic Wed Feb  3 11:55   still running");
    }
    else if (command.equals("finger pi")) {
      client.println("Login: pi");
      client.println("Name:  ");
      client.println("Directory: /home/pi");
      client.println("Shell: /bin/bash");
    }
    //------------------------------------------------
    // 10. Commande vide (juste Entrée)
    //------------------------------------------------
    else if (command.length() == 0) {
      // Ne rien faire
    }

    //------------------------------------------------
    // 11. Commande non reconnue
    //------------------------------------------------
    else {
      client.println("bash: " + command + ": command not found");
    }
  }

  // Déconnexion
  client.stop();
  Serial.println("Client disconnected.");
}


/* ===================================================================== */
/*  Main honeypot loop – Nmap‑friendly banners (almost working on it)     */
/* ===================================================================== */
void honeypotLoop() {
  /* ---------- Helper lambdas ---------------------------------------- */
  auto nowMs   = []() {
    return (uint32_t)millis();
  };
  auto nbWrite = [](WiFiClient & c, const uint8_t* p, size_t n) {
    size_t w = c.write(p, n); c.flush(); return w;
  };
  if (WiFiClient c = honeypotServer.available()) {
    String ip = c.remoteIP().toString();
    Serial.println("[*] >>> Telnet connection from: " + ip);
    
    const uint8_t telnetNegotiation[] = {255, 251, 1, 255, 251, 3, 255, 253, 3}; // IAC WILL ECHO, IAC WILL SGA, IAC DO SGA
    c.write(telnetNegotiation, sizeof(telnetNegotiation));
    c.flush();
    delay(10);
    
    handleHoneypotClient(c);
    Serial.println("[*] <<< Telnet client disconnected: " + ip);
  }

  /* ---------- FTP : ProFTPD 1.3.7c ---------- */
  if (WiFiClient c = ftpServer.available())
    handleBannerGrab(c, 21, "220 ProFTPD 1.3.7c Server (Debian) [::ffff:192.168.1.10]\r\n");

  /* ---------- SSH : OpenSSH 8.5p1 ----------- */
  if (WiFiClient c = sshServer.available()) {
    if (!c) return;
    String ip = c.remoteIP().toString();
    c.print("SSH-2.0-OpenSSH_8.5p1 Debian-1");
    logCommand(ip, 22, dumpBytes(c));
    /* keep the channel open a bit so nmap --script ssh-hostkey can
       finish the key‑exchange probe                           */
    unsigned long t0 = millis();
    while (c.connected() && millis() - t0 < 3000) delay(1);
    c.stop();
  }

  /* ---------- SMTP : Exim 4.94.2 ------------ */
  if (WiFiClient c = smtpServer.available())
    handleBannerGrab(c, 25, "220 mail.local ESMTP Exim 4.94.2\r\n");

  /* ---------- POP3 / IMAP  ------------------ */
  if (WiFiClient c = pop3Server.available())
    handleBannerGrab(c, 110, "+OK Dovecot ready.\r\n");

  if (WiFiClient c = imapServer.available())
    handleBannerGrab(c, 143, "* OK [CAPABILITY IMAP4rev1 LITERAL+ SASL-IR LOGIN-REFERRALS ID ENABLE IDLE] Dovecot ready.\r\n");

  /* ---------- HTTP on 443 (no TLS) ---------- */
  if (WiFiClient c = httpServer.available())
    handleBannerGrab(
      c, 443,
      "HTTP/1.1 200 OK\r\n"
      "Server: Apache/2.4.52 (Debian)\r\n"
      "Content-Type: text/html\r\n"
      "Content-Length: 44\r\n\r\n"
      "<html><body><h1>It works!</h1></body></html>");

  /* ---------- VNC 5900 ---------------------- */
  if (WiFiClient c = vncServer.available())
    handleBannerGrab(c, 5900, "RFB 003.008\n");


  /* ---------- DNS over TCP : proper CHAOS TXT version.bind ------------ */
  if (WiFiClient c = dnsServer.available()) {
    uint8_t query[514];
    int n = c.read(query, sizeof(query));
    if (n < 14) {
      c.stop();
      return;
    }

    uint16_t id = (query[2] << 8) | query[3];
    static uint8_t dnsResp[] = {
      0x00, 0x00, 0x81, 0x80, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
      0x07, 'v', 'e', 'r', 's', 'i', 'o', 'n', 0x04, 'b', 'i', 'n', 'd', 0x00,
      0x00, 0x10, 0x00, 0x03, 0xC0, 0x0C, 0x00, 0x10, 0x00, 0x03, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x07, 0x06, '9', '.', '1', '6', '.', '3'
    };
    dnsResp[0] = id >> 8;
    dnsResp[1] = id & 0xFF;

    uint16_t dnsLen = sizeof(dnsResp);
    uint8_t tcp[dnsLen + 2];
    tcp[0] = dnsLen >> 8; tcp[1] = dnsLen & 0xFF;
    memcpy(tcp + 2, dnsResp, dnsLen);

    handleBannerGrab(c, 53, tcp, dnsLen + 2);
  }



  /* ---------- SMB / microsoft‑ds : length now correct --------------- */
  if (WiFiClient c = smbServer.available()) {
    static const uint8_t SMB_CORE[] = {
      0xFF, 0x53, 0x4D, 0x42, 0x72, 0x00, 0x00, 0x00,
      0x88, 0x07, 0xC8, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x11, 0x02, 0x00, 0x01, 0x00, 0x20,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 'W', 'i', 'n', '7', ' ', 'L', 'M', ' ', '0', '.', '1', '2', 0x00
    };
    uint32_t len = sizeof(SMB_CORE);
    uint8_t pkt[len + 4];
    pkt[0] = 0x00; pkt[1] = (len >> 16) & 0xFF; pkt[2] = (len >> 8) & 0xFF; pkt[3] = len & 0xFF;
    memcpy(pkt + 4, SMB_CORE, len);
    handleBannerGrab(c, 445, pkt, len + 4);
  }


  /* ---------- MySQL 5.7 greeting – length fields fixed -------------- */
  if (WiFiClient c = mysqlServer.available()) {
    static const uint8_t MYSQL_PAY[] = {
      0x0A, '5', '.', '7', '.', '3', '3', 0x00,
      0x08, 0x00, 0x00, 0x00,
      'r', 'a', 'n', 'd', 's', 'a', 'l', 't', 0x00,
      0xFF, 0xF7, 0x08, 0x02, 0x00, 0xFF, 0xC7, 0x15,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      'r', 'a', 'n', 'd', 's', 'a', 'l', 't', '2', 0x00,
      'm', 'y', 's', 'q', 'l', '_', 'n', 'a', 't', 'i', 'v', 'e', '_', 'p', 'a', 's', 's', 'w', 'o', 'r', 'd', 0x00
    };
    uint8_t pkt[sizeof(MYSQL_PAY) + 4];
    pkt[0] = sizeof(MYSQL_PAY) & 0xFF;       // 3‑byte little‑endian length
    pkt[1] = (sizeof(MYSQL_PAY) >> 8) & 0xFF;
    pkt[2] = (sizeof(MYSQL_PAY) >> 16) & 0xFF;
    pkt[3] = 0x00;                           // sequence‑id
    memcpy(pkt + 4, MYSQL_PAY, sizeof(MYSQL_PAY));
    handleBannerGrab(c, 3306, pkt, sizeof(pkt));
  }

  /* ---------- RDP Connection‑Confirm ------------------------------- */
  if (WiFiClient c = rdpServer.available()) {
    static const uint8_t RDP_CC[] = {
      0x03, 0x00, 0x00, 0x13,
      0x0E, 0xD0, 0x00, 0x00,
      0x12, 0x34, 0x00, 0x02,
      0x00, 0x08, 0x00
    };
    handleBannerGrab(c, 3389, RDP_CC, sizeof(RDP_CC));
  }

  /* ---------- HTTP alternative (no TLS) ---------- */
  if (WiFiClient c = ahttpServer.available())
    handleBannerGrab(
      c, 8080,
      "HTTP/1.1 200 OK\r\n"
      "Server: Apache/2.4.52 (Debian)\r\n"
      "Content-Type: text/html\r\n"
      "Content-Length: 44\r\n\r\n"
      "<html><body><h1>It works!</h1></body></html>");

  /* ---------- short pause to yield CPU ----- */
  delay(10);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n\n╔═══════════════════════════════════════╗");
  Serial.println("║  ESP32 Honeypot Starting             ║");
  Serial.println("╚═══════════════════════════════════════╝\n");
  
  initSPIFFS();

  if (!loadConfig()) {
    Serial.println("[!] No configuration found or invalid config");
    Serial.println("[*] Entering Configuration Mode (Access Point)");
    Serial.println("[*] To exit and retry config, type 'config' in serial monitor");
    setupWebUI();
    return;
  }

  Serial.println("[+] Configuration loaded successfully");
  Serial.println("[+] SSID: " + ssid);
  
  WiFi.begin(ssid.c_str(), password.c_str());
  Serial.print("[~] Connecting to Wi-Fi: " + ssid + " ");

  unsigned long startTime = millis();
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 5000) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n[!] Wi-Fi connection failed after " + String(attempts) + " attempts");
    Serial.println("[*] Entering Configuration Mode (Access Point)");
    Serial.println("[*] To try connecting again, type 'config' in serial monitor");
    setupWebUI();
    return;
  }

  Serial.println("\n[+] Connected to WiFi!");
  Serial.println("[+] Device IP: " + WiFi.localIP().toString());
  Serial.println("[+] RSSI: " + String(WiFi.RSSI()) + " dBm");
  startHoneypot();
}


void loop() {
  // Always check for serial input to detect config command
  handleSerialInput();
  
  if (configPortalActive) {
    webServer.handleClient();
  }

  if (honeypotServersStarted) {
    honeypotLoop();
  }
}
