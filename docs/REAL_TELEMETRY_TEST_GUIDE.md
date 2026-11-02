# SentinelAI Real Telemetry Verification & Testing Guide

This guide describes how to prove end-to-end data flow: from genuine host telemetry on Windows into the FastAPI backend, through MongoDB Atlas persistence, and onto the live Vercel frontend.

---

## 1. Verifying System Health & Sensor State

Query the live health endpoint:

```bash
curl -X GET "https://<your-render-app>.onrender.com/api/v1/health/detailed"
```

Expected Response:
```json
{
  "overall_status": "LIVE",
  "is_live": true,
  "active_sensor_count": 1,
  "active_sensors": ["win-sec-host-01"],
  "suricata_operational": false,
  "windows_socket_operational": true,
  "message": "Live network monitoring active across 1 host sensor(s).",
  "database": "connected",
  "models_loaded": true,
  "timestamp": 1793610000000,
  "version": "1.2.0"
}
```

---

## 2. Generating Genuine Host Traffic

Open a web browser or run network commands on your Windows machine:
```powershell
# Open outbound HTTPS connections
curl -I https://www.google.com
curl -I https://github.com
```

The sensor agent running in `sensor_agent/sensor_agent.py` will capture these active TCP connections (`remote_address`, `remote_port=443`, `process_name="curl.exe"` or `"chrome.exe"`) and ship them to `/api/v1/sensors/telemetry`.

---

## 3. Verifying Ingestion in MongoDB Atlas

Inspect the `network_events` collection in MongoDB Atlas:

```javascript
db.network_events.find({ data_origin: "live" }).sort({ timestamp: -1 }).limit(5).pretty()
```

Sample Stored Document:
```json
{
  "id": "EVT-LIVE-7A39B1E40F22",
  "timestamp": 1793610234500,
  "source_ip": "192.168.1.50",
  "dest_ip": "142.250.190.46",
  "src_port": 53210,
  "dst_port": 443,
  "protocol": "TCP",
  "category": "Benign",
  "severity": "low",
  "risk_score": 0,
  "data_origin": "live",
  "is_simulated": false,
  "sensor_id": "win-sec-host-01",
  "collector_metadata": {
    "collector": "windows_sockets",
    "pid": 9412,
    "process_name": "chrome.exe",
    "connection_status": "ESTABLISHED"
  }
}
```

---

## 4. Verifying on the Frontend Dashboard

1. Navigate to your live frontend: `https://guardian-angel-main.vercel.app/`
2. Look at the top navigation bar:
   - Green indicator: `REAL TELEMETRY ACTIVE (1 Host Sensor)`
3. Under the **Security Overview** header:
   - Ensure `Live Telemetry` tab is selected.
   - Total network events displays genuine database count (e.g. `42`, matching MongoDB Atlas).
   - Switch between `15m`, `1h`, `24h`, and `7d` to verify time-sliced queries.
4. Switch to `Simulation Mode`:
   - Visualizes synthetic benchmark scenarios with clear amber tags without polluting live database statistics.
