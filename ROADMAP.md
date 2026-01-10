# GodsEye Implementation Roadmap

## 🎯 Scope
- RFID access cards
- Fingerprint scanners  
- MQTT communication
- Python backend
- Rules → AI detection
- Honeypots & Teapots
- Sysmon + Wazuh monitoring
- ❌ No environmental sensors

---

## 🟦 PHASE 0: PLANNING & FOUNDATION (Day 0–2)
- [x] Lock scope
- [x] Project structure
- [ ] System setup verification

---

## 🟦 PHASE 1: PYTHON BACKEND FOUNDATION (Day 3–7)
- [x] Modular backend folders
- [ ] Event schema design
- [ ] Event receiver
- [ ] Rule-based access anomaly detection
- [ ] Alert engine
- [ ] Storage layer
- [ ] Testing with fake data

---

## 🟦 PHASE 2: IoT COMMUNICATION (Day 8–11)
- [ ] MQTT Broker setup
- [ ] Simulated IoT devices
- [ ] Backend MQTT listener
- [ ] End-to-end test

---

## 🟦 PHASE 3: REAL IoT ACCESS DEVICES (Day 12–17)
- [ ] Hardware setup (ESP32)
- [ ] Firmware development
- [ ] ESP32 → MQTT integration
- [ ] Physical integration test

---

## 🟦 PHASE 4: HONEYPOTS (Day 18–21)
- [ ] IoT honeypot devices
- [ ] Interaction logging
- [ ] Alert generation

---

## 🟦 PHASE 5: TEAPOTS (Day 22–24)
- [ ] Decoy credentials
- [ ] Detection logic

---

## 🟦 PHASE 6: NETWORK MONITORING (Day 25–27)
- [ ] Traffic observation
- [ ] Network anomaly rules

---

## 🟦 PHASE 7: SYSMON & WAZUH (Day 28–32)
- [ ] Sysmon setup
- [ ] Wazuh setup
- [ ] Python integration

---

## 🟦 PHASE 8: AI ANOMALY DETECTION (Day 33–37)
- [ ] Data preparation
- [ ] ML models (Isolation Forest)
- [ ] Threat scoring

---

## 🟦 PHASE 9: CORRELATION ENGINE (Day 38–40)
- [ ] Cross-source correlation
- [ ] Incident classification

---

## 🟦 PHASE 10: DASHBOARD & DEMO (Day 41–45)
- [ ] Live dashboard
- [ ] Final demo scenarios
