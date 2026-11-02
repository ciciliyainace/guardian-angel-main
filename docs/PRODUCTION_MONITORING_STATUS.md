# SentinelAI Production Monitoring Status & Deployment Resolution

## 1. Audit Report: Code Tracing of Demo Numbers

Prior to Phase 10, the dashboard displayed numbers that originated from mock data fallbacks in the frontend and unconstrained aggregations in the backend. Below is the comprehensive trace:

| Value Shown in Demo UI | Trace in Codebase | Classification | Replacement in Phase 10 |
| :--- | :--- | :--- | :--- |
| **Total network events: 49,728** | `src/lib/mock-data.ts:16` (`trafficSeries.reduce(...)`) & `src/lib/api.ts:149` | Hardcoded Static Seed | Genuine count of live events in MongoDB Atlas filtered by `data_origin="live"` and time range (`15m`, `1h`, `24h`, `7d`). Returns 0 when no events are present. |
| **Active alerts: 94** | `src/lib/mock-data.ts:25-30` (`mockEvents`) & `src/lib/api.ts:151` | Hardcoded Seed Events | Live active alerts generated from genuine intrusion rules, Suricata alerts, or validated ML classifications. |
| **Critical threats: 13** | `src/lib/mock-data.ts:31` (`mockEvents.severity === 'critical'`) & `src/lib/api.ts:152` | Hardcoded Seed Events | Genuine count of live alerts with `severity="critical"` in the active time window. |
| **Suspicious connections: 3,026** | `src/lib/api.ts:157` (`total - benign` on mock series) | Derived from Mock Data | Genuine count of host connections flagged with medium/high/critical severity in MongoDB Atlas. |
| **Detection recall: 91%** | `backend/app/services/analytics_service.py:33` & `src/lib/api.ts:159` | Hardcoded String | Real model recall pulled directly from loaded scikit-learn registry metrics (`registry.rf.metrics["recall"]`), or `--` if models are unloaded or uncalibrated. |
| **SIMULATION MODE Badge** | `src/components/app-header.tsx:70` | Static Hardcoded HTML | Dynamic monitoring beacon querying `/api/v1/health/detailed` (`LIVE`, `STANDBY`, `NO_LIVE_SENSOR`). |
| **Monitoring (demo)** | `src/components/app-header.tsx:73` | Static Hardcoded HTML | Active host sensor count display (`X Host Sensor(s)`). |
| **Demo data · v0.1.0** | `src/components/app-sidebar.tsx:70` | Static Hardcoded HTML | Dynamic footer status `SentinelAI · Host Telemetry`. |

---

## 2. Troubleshooting the User's Deployment Screenshots

### Screenshot 1: Vercel "Environment Variables" (`EXAMPLE_NAME`)
- **What to configure**:
  - **Key**: `VITE_API_BASE_URL`
  - **Value**: `https://<your-render-backend-name>.onrender.com/api/v1`
  - **Environments**: Select both **Production** and **Preview**.
  - *Why*: Without this environment variable, the Vercel frontend defaults to `http://127.0.0.1:8000/api/v1`, causing browser `Failed to fetch` errors on login and registration.

### Screenshot 2: Render Settings (`$ bun install` / `$ yarn start`)
- **Why it failed**: Render auto-detected `package.json` in the root and configured a Node/Bun web service instead of a Python FastAPI web service.
- **Correct Render Settings**:
  - **Environment / Runtime**: `Python 3`
  - **Root Directory**: Leave empty (repository root).
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
  - **Environment Variables on Render**:
    - `PYTHON_VERSION`: `3.12.0`
    - `DATABASE_TYPE`: `mongodb`
    - `MONGODB_URI`: `<Your MongoDB Atlas connection string>`
    - `MONGODB_DATABASE`: `sentinelai`
    - `SECRET_KEY`: `<Random 32-character string>`
    - `FIREWALL_MODE`: `simulation`
    - `ALLOW_FIREWALL_BLOCKING`: `false`
    - `ALERT_ONLY_MODE`: `true`
    - `CORS_ORIGINS`: `["https://guardian-angel-main.vercel.app"]`

### Screenshots 3, 4, 5: Vercel 500 Error & "Deployment Blocked"
- **Cause 1**: The SSR build previously crashed because `.vercel` artifacts were committed into Git.
  - *Resolution*: Added `.vercel/` to `.gitignore`, cleaned cached files, and configured Nitro preset to `"vercel"` in `vite.config.ts`.
- **Cause 2**: Vercel Hobby plan blocks commits authored by a different GitHub username than the Vercel project owner (`ciciliyainace`).
  - *Resolution*: Git commits are now authored by `ciciliyainace <ciciliyainace2210@gmail.com>`.

### Screenshots 6 & 7: "Failed to fetch" on Registration / Google Sign-In
- **Cause**: The live frontend on HTTPS (`https://guardian-angel-main.vercel.app`) attempted to connect to `http://127.0.0.1:8000` because `VITE_API_BASE_URL` was not yet pointing to the deployed Render backend.
- **Resolution**:
  1. Once Render backend is running, set `VITE_API_BASE_URL` in Vercel settings (as explained in Screenshot 1).
  2. Frontend authentication includes graceful offline detection and clear guidance if the backend is unreachable.

---

## 3. Production Readiness Verification Checklist

- [x] Dedicated host sensor agent created in `sensor_agent/` with Windows socket inspection and Suricata EVE tailing.
- [x] Secure sensor enrollment and SHA-256 hashed API token authentication.
- [x] Safe flow aggregation with feature validity flags (no synthetic numbers for missing packet features).
- [x] Full isolation between live telemetry (`data_origin="live"`) and simulation scenarios (`data_origin="simulated"`).
- [x] Real database-driven analytics returning 0 when empty and real counts when telemetry arrives.
- [x] Real-time monitoring status bar and time-range filtering (`15m`, `1h`, `24h`, `7d`) on frontend dashboard.
- [x] 100% of backend pytest suite passing (64/64 tests).
- [x] Frontend builds cleanly with zero errors.
