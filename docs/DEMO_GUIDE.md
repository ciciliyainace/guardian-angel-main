# SentinelAI — System Demonstration & Verification Guide

This guide provides end-to-end instructions for running and evaluating the **SentinelAI AI-Powered Firewall Attack Detection System** on a Windows workstation using Windows PowerShell.

---

## 1. Safety and Operational Guidelines

> [!IMPORTANT]
> **Safety First — Simulation Mode Active**
> - SentinelAI operates by default with `FIREWALL_MODE=simulation`. Approved firewall rules log actions and execute non-destructive diagnostic commands rather than altering system firewall rules.
> - **Never perform real denial-of-service, brute force, or intrusive scanning attacks against live production networks or external hosts.**
> - All demonstration events utilize reserved testing subnets (RFC 5737: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and private subnets (`192.168.1.0/24`).
> - Loopback addresses (`127.0.0.1`, `::1`), default gateways, and critical DNS resolvers (`8.8.8.8`, `1.1.1.1`) are hardcoded as protected targets and cannot be blocked under any circumstances.
> - Never commit or expose MongoDB Atlas connection strings or JWT secret keys. Keep sensitive parameters in `backend/.env`.

---

## 2. Environment Prerequisites

Before starting, ensure the following prerequisites are installed on your Windows workstation:

1. **Python 3.12+**: Configured in local virtual environment `.\.venv\`.
2. **Node.js (v18+ or v20+) and npm**: For running the React + Vite frontend.
3. **MongoDB Atlas Account / Cluster**: Connection string configured in `backend/.env`.
4. **Windows PowerShell**: Default terminal shell on Windows 10/11.

---

## 3. Starting the Application Services

Open two separate Windows PowerShell windows (one for the backend and one for the frontend) in the project root directory: `d:\project\unexpected\New folder\guardian-angel-main\guardian-angel-main`.

### Step 3.1: Start the FastAPI Backend

In the **first PowerShell window**, activate the virtual environment and start the Uvicorn server:

```powershell
# Navigate to the project root
cd "d:\project\unexpected\New folder\guardian-angel-main\guardian-angel-main"

# Launch the FastAPI backend on port 8000
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

**Expected Startup Output:**
```text
INFO:     Initializing SentinelAI Backend Defense System...
INFO:     Connected to MongoDB Atlas cluster0.kramxzk.mongodb.net
INFO:     MongoDB collections and indexes initialized successfully.
INFO:     Loaded ML model artifacts: Random Forest, Decision Tree, Isolation Forest, Scaler.
INFO:     Background workers started (IngestionWorker, ExpiryWorker, DetectionWorker).
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 3.2: Start the React SOC Dashboard

In the **second PowerShell window**, launch the frontend Vite development server:

```powershell
# Navigate to the project root
cd "d:\project\unexpected\New folder\guardian-angel-main\guardian-angel-main"

# Launch the React + Vite frontend
npm run dev
```

**Expected Startup Output:**
```text
  VITE v5.4.19  ready in 480 ms

  ➜  Local:   http://localhost:8080/
  ➜  Network: use --host to expose
```

---

## 4. Service Health and Database Verification

Verify that both the FastAPI API and MongoDB Atlas connection are operational using PowerShell:

```powershell
# 1. Check Root Health Check
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get | ConvertTo-Json

# 2. Check Detailed Database Readiness
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health/ready" -Method Get | ConvertTo-Json
```

**Expected JSON Response:**
```json
{
  "status": "ready",
  "database": {
    "status": "connected",
    "ping_ms": 42.5,
    "database_name": "sentinel_ai",
    "collections": ["events", "alerts", "rules", "firewall_actions", "block_requests", "audit_logs", "users"]
  },
  "models": {
    "random_forest": "loaded",
    "decision_tree": "loaded",
    "isolation_forest": "loaded",
    "scaler": "loaded"
  },
  "firewall_mode": "simulation"
}
```

---

## 5. User Roles and Authentication

SentinelAI enforces Role-Based Access Control (RBAC) via JSON Web Tokens (JWT). Two default seeded user accounts are available:

| Role | Username | Email | Password | Allowed Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Security Analyst** | `ciciliya-inace` | `analyst@sentinelai.local` | `<CONFIGURED_ANALYST_PASSWORD>` | View dashboard, inspect events & alerts, submit block requests |
| **Administrator** | `admin` | `admin@sentinelai.local` | `<CONFIGURED_ADMIN_PASSWORD>` | Full access, rule modifications, approve/reject/rollback firewall actions |

> [!NOTE]
> Passwords can be passed via environment variables `$Env:SENTINEL_ANALYST_PASSWORD` and `$Env:SENTINEL_ADMIN_PASSWORD` or replaced directly with your initialized credentials.

### Authenticate via PowerShell to Obtain JWT Tokens

```powershell
# Set or read passwords securely from environment variables (or replace placeholders)
$analystPassword = if ($Env:SENTINEL_ANALYST_PASSWORD) { $Env:SENTINEL_ANALYST_PASSWORD } else { "AnalystPass2026!" } # Replace with your configured analyst password
$adminPassword = if ($Env:SENTINEL_ADMIN_PASSWORD) { $Env:SENTINEL_ADMIN_PASSWORD } else { "SentinelAdmin2026!" } # Replace with your configured admin password

# Authenticate as Security Analyst
$analystAuth = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" -Method Post -ContentType "application/json" -Body (@{
    username_or_email = "ciciliya-inace"
    password = $analystPassword
} | ConvertTo-Json)

$analystToken = $analystAuth.access_token
Write-Host "Analyst JWT Token acquired: $($analystToken.Substring(0, 20))..." -ForegroundColor Green

# Authenticate as Administrator
$adminAuth = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" -Method Post -ContentType "application/json" -Body (@{
    username_or_email = "admin"
    password = $adminPassword
} | ConvertTo-Json)

$adminToken = $adminAuth.access_token
Write-Host "Administrator JWT Token acquired: $($adminToken.Substring(0, 20))..." -ForegroundColor Cyan
```

---

## 6. Demonstration Step-by-Step

### Scenario A: Benign Traffic Flow (Normal Web Browsing)

Demonstrate that legitimate user traffic flows through the preprocessor, ML models, and rule engine without triggering false alerts.

**Command:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=benign_web&count=3" -Method Post | ConvertTo-Json -Depth 4
```

**Observation in SOC Dashboard:**
1. Navigate to **Network Traffic** (`http://localhost:8080/traffic`).
2. Three new TCP port 443 flow records appear from source IP `192.0.2.15`.
3. Notice that `severity` is `low` / `info`, risk score is `10`, and **0 alerts** are generated.
4. Navigate to **Threats** (`http://localhost:8080/threats`) — verify that no new security incident was raised.

---

### Scenario B: Suspicious Attack Scenarios

Demonstrate real-time detection across diverse threat vectors.

#### 1. DoS SYN Flood Attack
Simulates asymmetrical packet floods with high SYN flags and negligible ACK packets.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=dos_syn_flood&count=5" -Method Post | ConvertTo-Json -Depth 4
```
- **Rule Triggered**: `R-002: DoS SYN Flood Detection`
- **ML Classification**: `dos` (Confidence: > 99%)
- **Alert Created**: Severity `critical`, Risk Score `92`.

#### 2. Port Scan Reconnaissance
Simulates rapid multi-port TCP probes across standard service ports.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=port_scan&count=5" -Method Post | ConvertTo-Json -Depth 4
```
- **Rule Triggered**: `R-001: Port scan detection`
- **ML Classification**: `port_scan` (Confidence: > 98%)
- **Alert Created**: Severity `high`, Risk Score `75`.

#### 3. Authentication Brute-Force
Simulates high-frequency connection attempts targeting SSH port 22.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=brute_force&count=5" -Method Post | ConvertTo-Json -Depth 4
```
- **Rule Triggered**: `R-003: Repeated authentication failures`
- **ML Classification**: `brute_force` (Confidence: > 95%)
- **Alert Created**: Severity `high`, Risk Score `80`.

#### 4. Anomalous Beaconing (C2 / Tunneling)
Simulates low-frequency periodic beaconing with fixed inter-arrival times.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=anomalous_beacon&count=3" -Method Post | ConvertTo-Json -Depth 4
```
- **Anomaly Model**: Isolation Forest identifies structural anomaly (anomaly score < 0).
- **Alert Created**: Severity `medium`, Risk Score `60`.

---

### Scenario C: Alert Deduplication Verification

To prove the system does not flood the SOC analyst with redundant alerts:

```powershell
# Send 2 successive bursts of the same attack within 15 seconds
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=dos_syn_flood&count=2" -Method Post
Start-Sleep -Seconds 2
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/events/simulate?scenario=dos_syn_flood&count=2" -Method Post
```

**Observation:**
- Navigate to **Threats** (`http://localhost:8080/threats`).
- Only **one** alert exists for `198.51.100.99` with category `DoS-like traffic`.
- Inspecting the alert details reveals an `occurrence_count` incremented to `4` with updated `last_seen` timestamp, preserving database storage and analyst attention.

---

### Scenario D: Controlled Firewall Response (Approval & Rollback)

Demonstrate the two-person rule enforcement, safety guardrails, and rollback capability.

#### Step 1: Attempt to Block a Protected Target (Safety Guardrail Test)
Test that loopback or DNS servers cannot be blocked:

```powershell
$badPayload = @{
    sourceIp = "127.0.0.1"
    reason = "Testing safety guardrail"
    direction = "inbound"
    durationMin = 60
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/firewall/requests" -Method Post `
        -Headers @{ Authorization = "Bearer $analystToken" } `
        -ContentType "application/json" -Body $badPayload
} catch {
    Write-Host "Guardrail succeeded! Protected IP rejected: $($_.Exception.Message)" -ForegroundColor Green
}
```
**Expected Outcome:** HTTP `400 Bad Request` with detail `"protected_target"`.

#### Step 2: Submit Valid Block Request (Analyst Role)
Submit a block request for the attacker IP `198.51.100.99`:

```powershell
$requestPayload = @{
    sourceIp = "198.51.100.99"
    reason = "Automated mitigation for critical DoS SYN Flood attack"
    direction = "inbound"
    durationMin = 30
} | ConvertTo-Json

$blockReq = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/firewall/requests" -Method Post `
    -Headers @{ Authorization = "Bearer $analystToken" } `
    -ContentType "application/json" -Body $requestPayload

$reqId = $blockReq.id
Write-Host "Created Block Request ID: $reqId with status: $($blockReq.status)" -ForegroundColor Yellow
```

#### Step 3: Administrator Review & Approval
Approve the request using the Administrator token:

```powershell
$approvalPayload = @{
    reviewer_note = "Confirmed malicious SYN flood in telemetry logs. Approved for 30m."
} | ConvertTo-Json

$approvalResult = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/firewall/requests/$reqId/approve" -Method Post `
    -Headers @{ Authorization = "Bearer $adminToken" } `
    -ContentType "application/json" -Body $approvalPayload

Write-Host "Approval result: $($approvalResult.status) - Rule executed in $($approvalResult.execution_mode) mode" -ForegroundColor Green
$actionId = $approvalResult.action.id
```

#### Step 4: Verify Active Firewall Rule
Check the list of active firewall rules:

```powershell
$activeRules = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/firewall/rules" -Method Get
$activeRules | Format-Table id, source_ip, direction, status, expires_at
```

#### Step 5: Rollback Firewall Rule
Demonstrate immediate rollback of the active block rule:

```powershell
$rollbackResult = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/firewall/actions/$actionId/rollback" -Method Post `
    -Headers @{ Authorization = "Bearer $adminToken" }

Write-Host "Rollback result: $($rollbackResult.status) - Action state: $($rollbackResult.action.status)" -ForegroundColor Cyan
```

#### Step 6: Verify Immutable Audit Trail
Verify that all creation, approval, and rollback operations are permanently recorded in the audit log:

```powershell
$auditLogs = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/audit" -Method Get
$auditLogs | Select-Object -First 5 | Format-Table timestamp, actor, action, target, result
```

---

## 7. Explaining Suricata Status ("Disconnected")

In the SOC Dashboard, the collector telemetry card for **Suricata NIDS** may show `Disconnected` or `Sensor Offline`.

### Technical Rationale for Viva Presentation:
1. **Physical Architecture**: Suricata is an external binary requiring kernel packet-capture drivers (WinPcap / Npcap on Windows or AF_PACKET on Linux) and an active socket or file pipe to `eve.json`.
2. **Current Environment**: The project demonstration workstation runs SentinelAI's native **Windows Socket Collector** (`netstat -n -o` telemetry parser), which actively captures real host socket connections.
3. **Graceful Degradation**: SentinelAI's collector layer is loosely coupled. When an external engine like Suricata is not locally running, the system accurately reports `Disconnected` rather than fabricating simulated telemetry as live IDS captures.
4. **Integration Readiness**: The backend includes a complete `SuricataEveCollector` parser ready to tail `/var/log/suricata/eve.json` as soon as Suricata is deployed in a Linux sensor VM or appliance.

---

## 8. Summary Checklist for Demonstration

| Feature | Endpoint / UI Action | Expected Result | Verified |
| :--- | :--- | :--- | :---: |
| **Backend Health** | `GET /api/v1/health/ready` | HTTP 200, DB connected, models loaded | [x] |
| **Frontend UI** | `http://localhost:8080` | Clean SOC dashboard, KPI cards loaded | [x] |
| **Benign Traffic** | `POST /api/v1/events/simulate?scenario=benign_web` | Traffic logged, 0 alerts raised | [x] |
| **Attack Detection** | `POST /api/v1/events/simulate?scenario=dos_syn_flood` | Alert created, RF confidence > 99% | [x] |
| **Deduplication** | Rapid repeated attack bursts | Occurrence count increments, 1 alert | [x] |
| **Protected Target** | Block request for `127.0.0.1` | HTTP 400 `protected_target` rejected | [x] |
| **Analyst Request** | Submit block request | Status: `pending` | [x] |
| **Admin Approval** | Approve block request | Status: `active`, simulated command executed | [x] |
| **Rollback Action** | Rollback active rule | Status: `rolled_back`, unblock executed | [x] |
| **Audit Logging** | `GET /api/v1/audit` | Immutable records for request, approve, rollback | [x] |
