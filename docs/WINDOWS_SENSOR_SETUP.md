# SentinelAI Windows Sensor Setup & Operation Guide

This guide walks you through setting up, enrolling, and running the SentinelAI host network sensor agent on a Windows machine.

---

## 1. Prerequisites

- **Python 3.10+** (64-bit recommended) installed on Windows.
- **Administrator Privileges** (recommended to allow reading process names and ports).
- *(Optional)* **Suricata IDS for Windows**:
  - Download from: `https://suricata.io/download/`
  - Default eve log directory: `C:\Program Files\Suricata\log\eve.json`

---

## 2. Sensor Agent Installation

Open PowerShell as Administrator and navigate to the `sensor_agent/` directory:

```powershell
cd "d:\project\unexpected\New folder\guardian-angel-main\guardian-angel-main\sensor_agent"
```

Install the lightweight sensor dependencies:

```powershell
pip install -r requirements.txt
```

---

## 3. Sensor Enrollment

Enroll your Windows machine against the SentinelAI backend. You can connect to either your deployed Render backend or your local backend.

### For Deployed Render Backend:
```powershell
python enroll.py --backend-url "https://<your-render-app>.onrender.com/api/v1" --user "admin" --password "Admin123!" --sensor-id "win-sec-host-01" --name "Primary Windows Host"
```

### For Local Backend:
```powershell
python enroll.py --backend-url "http://127.0.0.1:8000/api/v1" --user "admin" --password "Admin123!" --sensor-id "win-sec-host-01" --name "Primary Windows Host"
```

This generates `sensor_config.json`:
```json
{
  "backend_url": "https://<your-render-app>.onrender.com/api/v1",
  "sensor_id": "win-sec-host-01",
  "sensor_key": "sen_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "name": "Primary Windows Host",
  "hostname": "MY-PC",
  "suricata_eve_path": "C:\\Program Files\\Suricata\\log\\eve.json",
  "poll_interval_sec": 5.0,
  "heartbeat_interval_sec": 30.0,
  "batch_size": 50
}
```

---

## 4. Running the Sensor Agent

To begin streaming genuine telemetry:

```powershell
python sensor_agent.py
```
Or double-click:
```powershell
run_sensor.bat
```

### Sensor Agent Output Log Example:
```
2026-11-02 12:00:00 [INFO] (SensorAgent) Starting SentinelAI Sensor Agent [ID: win-sec-host-01]
2026-11-02 12:00:00 [INFO] (SensorAgent) Target Backend: https://<your-render-app>.onrender.com/api/v1
2026-11-02 12:00:00 [INFO] (SensorAgent) Windows psutil available: True
2026-11-02 12:00:01 [INFO] (SensorAgent) Heartbeat acknowledged by backend (suricata: standby, winsock: operational)
2026-11-02 12:00:06 [INFO] (SensorAgent) Shipped 38 events: ingested=38, duplicates=0, alerts=0
```

---

## 5. Offline Spooling & Recovery

If your internet connection drops or the backend restarts:
1. The sensor agent automatically buffers unsent events in `.telemetry_spool.jsonl`.
2. Heartbeats retry with backoff.
3. Once the backend is reachable, spooled events are drained and forwarded without data loss.

