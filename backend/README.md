# SentinelAI — AI-Powered Firewall Attack Detection System
## Backend Architecture & MongoDB Atlas Deployment Guide

**SentinelAI** is an AI-powered firewall attack detection system for computer networks. The backend integrates rule-based IDS/IPS inspections with supervised and unsupervised machine learning models (Random Forest, Decision Tree baseline, Isolation Forest anomaly detector), safe firewall response orchestration, and **MongoDB Atlas** as the primary persistent database.

---

## 1. Operating Principles & Safety Architecture

1. **Alert-First Principle**: All detected threats generate persistent alerts, evidence records, and risk scores. Automated OS-level firewall blocking is **disabled by default** (`ALLOW_FIREWALL_BLOCKING=false`).
2. **Safe Firewall Isolation**: The system defaults to simulation mode (`FIREWALL_MODE=simulation`). Simulated blocks record lifecycle states, expirations, and audit entries without modifying the operating system firewall.
3. **Protected Infrastructure Targets**: The system strictly forbids blocking loopback addresses (`127.0.0.1`, `::1`), private gateways, broadcast/multicast ranges (`224.0.0.0/4`), DNS resolvers (`8.8.8.8`, `1.1.1.1`), or administrator-configured management subnets.
4. **Parameterized OS Execution**: The Windows Defender adapter does not execute untrusted shell strings or dynamic PowerShell scripts from user input. All firewall commands use strict, fixed argument lists via `netsh advfirewall`.
5. **Two-Tier Role-Based Access Control**:
   - `analyst`: Can monitor traffic, view alerts, update investigation states, and request IP blocks.
   - `administrator`: Can approve or reject block requests, toggle and edit detection rules, modify system settings, and rollback firewall actions.
6. **No Silent Fallback & Zero Credential Leaks**: MongoDB connection issues are reported transparently via health endpoints without leaking passwords or connection credentials in logs, API responses, or git commits.

---

## 2. Technology Stack

- **Operating System**: Windows 11 (PowerShell 7 / Windows PowerShell 5.1).
- **Runtime**: Python 3.12 (via virtual environment `.venv`).
- **Primary Database**: **MongoDB Atlas** (Cluster0) via official `pymongo` driver (v4.9+) with DNS SRV resolution (`dnspython`).
- **Web API**: FastAPI 0.115+, Pydantic v2 (with field aliases and contract validation), Uvicorn ASGI.
- **Machine Learning**: Scikit-Learn 1.6+, NumPy 2.2+, Pandas 2.2+, Joblib.
- **Security & Cryptography**: PyJWT (HS256 access tokens), Bcrypt password hashing.
- **Testing**: Pytest, Pytest-asyncio, Mongomock, HTTPX.

---

## 3. MongoDB Atlas Collections & Indexes

SentinelAI utilizes 10 collections with automatic index initialization on startup:

| Collection | Key Fields | Indexes |
| :--- | :--- | :--- |
| `users` | `id`, `username`, `email`, `role`, `hashed_password` | `username` (unique), `email` (unique), `id` (unique) |
| `network_events` | `id`, `timestamp`, `source_ip`, `dest_ip`, `category`, `severity`, `risk_score` | `id` (unique), `timestamp` (-1), `category`, `(severity, timestamp)`, `(source_ip, dest_ip)` |
| `alerts` | `id`, `timestamp`, `status`, `severity`, `risk_score`, `related_event_id` | `id` (unique), `timestamp` (-1), `(status, severity)`, `related_event_id` |
| `detection_rules` | `id`, `name`, `category`, `severity`, `enabled`, `threshold`, `window_sec` | `id` (unique), `enabled` |
| `firewall_requests`| `id`, `source_ip`, `status`, `requested_by`, `requested_at`, `duration_min` | `id` (unique), `(status, requested_at)`, `source_ip` |
| `firewall_actions` | `id`, `managed_rule_name`, `status`, `expires_at`, `verification_status` | `id` (unique), `managed_rule_name` (unique), `(status, expires_at)` |
| `model_registry` | `version`, `model_type`, `accuracy`, `precision`, `recall`, `f1_score` | `version` (unique) |
| `audit_logs` | `id`, `timestamp`, `actor`, `action`, `target`, `result` | `id` (unique), `timestamp` (-1), `(actor, timestamp)` |
| `system_settings` | `key`, `value`, `category`, `description`, `updated_by` | `key` (unique) |
| `feedback` | `event_id`, `analyst`, `feedback_type`, `comments`, `created_at` | `created_at` (-1) |

---

## 4. Step-by-Step Windows 11 Setup Guide

### Step 1: Open PowerShell in Project Root
```powershell
cd "d:\project\unexpected\New folder\guardian-angel-main\guardian-angel-main"
```

### Step 2: Activate Python Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell blocks execution of scripts, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

### Step 3: Configure Environment Variables
Verify or update `backend\.env`:
```ini
DATABASE_TYPE=mongodb
MONGODB_URI=mongodb+srv://<db_username>:<db_password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=sentinelai
SECRET_KEY=<generate_secure_random_key_for_production>
FIREWALL_MODE=simulation
ALLOW_FIREWALL_BLOCKING=false
```

> [!IMPORTANT]
> Replace `<db_username>` and `<db_password>` with your actual MongoDB Atlas database user credentials.
> In MongoDB Atlas console (**Security -> Network Access**), ensure your current public IP is allowed to connect to Cluster0.

### Step 4: Install / Verify Python Dependencies
```powershell
pip install -r backend\requirements.txt
```

### Step 5: Initialize MongoDB Collections & Default Seed Data
```powershell
# Optionally customize initial passwords before running:
# $Env:INITIAL_ADMIN_PASSWORD="<YourSecureAdminPassword>"
# $Env:INITIAL_ANALYST_PASSWORD="<YourSecureAnalystPassword>"

python backend\scripts\initialize_database.py
```
This script creates all required indexes idempotently and seeds:
- **Default Administrator**: username: `admin` (password configured via environment or initial setup)
- **Default SOC Analyst**: username: `ciciliya-inace` (password configured via environment or initial setup)
- **Default Detection Rules**: Port scanning, Connection-rate threshold, Repeated auth failures, Suricata signatures, Long low-volume flows
- **Default System Settings**: Simulation mode, alert-only master toggle, retention windows

### Step 6: (Optional) Migrate Existing SQLite Data to MongoDB Atlas
If you have records in a local SQLite file (`sentinelai.db`), run the migration utility:
```powershell
# Dry run simulation (does not modify MongoDB):
python backend\scripts\migrate_sqlite_to_mongodb.py --dry-run

# Execute migration:
python backend\scripts\migrate_sqlite_to_mongodb.py --sqlite-path sentinelai.db
```

### Step 7: Train or Verify ML Models
Train the Random Forest, Decision Tree baseline, and Isolation Forest models:
```powershell
python backend\scripts\run_training.py
```
This generates:
- `artifacts/random_forest.joblib`
- `artifacts/decision_tree.joblib`
- `artifacts/isolation_forest.joblib`

### Step 8: Start the SentinelAI Backend
```powershell
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Or run the batch helper:
```powershell
.\backend\run_backend.bat
```

### Step 9: Verify Health & Database Connectivity
Open your browser or run:
- Interactive API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Readiness Check: [http://127.0.0.1:8000/health/ready](http://127.0.0.1:8000/health/ready)

Expected `/health/ready` output:
```json
{
  "status": "ready",
  "database": "connected",
  "database_type": "mongodb",
  "database_name": "sentinelai",
  "cluster": "mongodb+srv://<username>:******@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
  "models_loaded": true,
  "firewall_mode": "simulation",
  "blocking_enabled": false
}
```

### Step 10: Run the Test Suite
```powershell
python -m pytest backend\tests -v
```
All 39 automated tests (including MongoDB Atlas connection, Suricata EVE log tailing, Windows socket telemetry, masking, and contract tests) execute with 100% pass rate.

### Step 11: Launch Frontend
In a separate terminal:
```powershell
npm run dev
```
Open [http://localhost:8080](http://localhost:8080). The frontend connects directly to the FastAPI backend with MongoDB Atlas persistence.

---

## 5. Suricata IDS Integration & Windows Configuration Guide

SentinelAI features an integrated Suricata EVE JSON log tailing collector (`SuricataCollector`) that ingests live signature alerts and flow summaries.

### 5.1 Collector States
The collector reports one of 4 explicit states:
- `Not Configured`: `SURICATA_EVE_PATH` is empty. Suricata monitoring is omitted from background polling.
- `Disconnected`: `SURICATA_EVE_PATH` is configured, but the `eve.json` file is absent (Suricata service is stopped or not writing).
- `Operational`: File exists, is readable, and new events are tailing via safe byte offsets.
- `Error`: Filesystem permission or format error encountered.

### 5.2 Windows Suricata Installation Steps
1. **Install Npcap**: Download and install Npcap from [https://npcap.com/#download](https://npcap.com/#download). During installation, select "Install Npcap in WinPcap API-compatible Mode".
2. **Download Suricata for Windows**: Download the MSI installer for Windows (64-bit) from [https://suricata.io/download/](https://suricata.io/download/) and install to `C:\Program Files\Suricata`.
3. **List Network Interfaces**: Open PowerShell as Administrator and run:
   ```powershell
   & "C:\Program Files\Suricata\suricata.exe" --list-interfaces
   ```
   Note the GUID or adapter name (e.g., `\Device\NPF_{...}`).
4. **Configure `suricata.yaml`**: Open `C:\Program Files\Suricata\suricata.yaml` and verify:
   ```yaml
   default-log-dir: "C:\\Program Files\\Suricata\\log"
   outputs:
     - eve-log:
         enabled: yes
         filetype: regular
         filename: eve.json
         types:
           - alert:
               payload: yes
           - flow
   ```
5. **Update `backend/.env`**:
   ```ini
   SURICATA_EVE_PATH=C:/Program Files/Suricata/log/eve.json
   ```
6. **Run Suricata**:
   ```powershell
   & "C:\Program Files\Suricata\suricata.exe" -c "C:\Program Files\Suricata\suricata.yaml" -i "\Device\NPF_{YOUR_INTERFACE_GUID}"
   ```
SentinelAI will automatically transition from `Disconnected` to `Operational` and parse live signature matches without duplicates.

---

## 6. MongoDB Atlas Security & Production Whitelist Transition

During local development across cellular or dynamic ISP connections (which frequently rotate dynamic IPv4/IPv6 addresses), `0.0.0.0/0` is used temporarily.

### Transitioning to Strict Production IP Whitelisting:
1. **Static Cloud Backend (AWS / GCP / Azure)**:
   - Identify your backend's Elastic IP or NAT Gateway public IP (e.g., `52.14.88.12/32`).
   - In MongoDB Atlas Console -> **Network Access** -> **Edit**, remove `0.0.0.0/0` and add the specific `/32` IP address.
2. **VPC Peering or AWS PrivateLink**:
   - For enterprise deployments, configure VPC Peering or PrivateLink under Atlas **Network Access -> Private Endpoints**.
   - Traffic travels entirely over private cloud interconnects without traversing the public internet.
3. **Zero Credential Leaking**:
   - Credentials are stored strictly in `backend/.env`.
   - All logs, error messages, and health endpoints mask connection credentials automatically via regex.

---

## 7. Security & Masking Architecture

1. **Credential Sanitization**: The connection string password is automatically stripped from logs and API error responses using regex masking (`get_masked_mongodb_uri()`, `sanitize_error_message()`).
2. **Environment Protection**: `.env` is registered in `.gitignore`. `backend/.env.example` contains only safe placeholders.
3. **No Plaintext Passwords**: All user passwords are encrypted using Bcrypt (`bcrypt.hashpw`).
4. **Token Expiry**: JWT access tokens are signed with HS256 and configured with 24-hour expiration.

