# SentinelAI Windows Sensor Agent

A lightweight host security telemetry agent for SentinelAI. It captures real-time host socket metadata and Suricata intrusion detection events, streams them safely to the SentinelAI backend over authenticated HTTPS/HTTP, and features offline spooling.

---

## Capabilities

1. **Active Windows Socket Collection**:
   - Gathers genuine TCP/UDP connections (`local_address`, `remote_address`, `ports`, `state`).
   - Resolves originating process identifiers (PIDs) and executable names.
   - Accurately categorized as `socket_metadata` without fabricating unmeasured packet flow features.

2. **Suricata EVE JSON Ingestion**:
   - Incrementally tails Suricata `eve.json` using byte-offset tracking.
   - Detects log rotations and file truncations safely without duplicate processing.
   - Parses `alert`, `flow`, `dns`, `http`, and `tls` records.

3. **Secure Heartbeat & State Synchronization**:
   - Authenticated via SHA-256 hashed API keys (`X-Sensor-Key`).
   - Reports CPU, memory, socket counts, and collector operational statuses every 30 seconds.

4. **Resilient Offline Spooling**:
   - If the SentinelAI cloud backend is temporarily unreachable, events are buffered in `.telemetry_spool.jsonl`.
   - Flushes automatically upon reconnection with exponential backoff.

---

## Installation & Setup

### Prerequisites
- Python 3.10+ installed on Windows.
- Administrator privileges on Windows host (recommended for process inspection).

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Enroll Sensor
Run `enroll.py` to register your sensor with the SentinelAI backend:
```bash
python enroll.py --backend-url https://<your-backend>.onrender.com/api/v1 --user admin --password Admin123!
```
Or for local testing:
```bash
python enroll.py --backend-url http://127.0.0.1:8000/api/v1
```

This generates `sensor_config.json` containing your unique sensor ID and `sen_live_...` API key.

### 3. Run the Sensor Agent
```bash
python sensor_agent.py
```
Or double-click `run_sensor.bat`.

