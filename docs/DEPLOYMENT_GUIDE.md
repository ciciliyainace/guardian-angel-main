# SentinelAI — Production Cloud Deployment & Operations Guide

This guide details the complete production architecture, configuration, deployment procedures, and troubleshooting steps for hosting **SentinelAI — AI-Powered Firewall Attack Detection System** in a low-cost, high-reliability cloud environment.

---

## 1. Production Architecture Overview

The production architecture is decoupled into three independent, specialized cloud layers:

```
┌─────────────────────────────────┐
│     Client Browser (HTTPS)      │
└────────────────┬────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  Presentation Layer: Cloudflare Pages / Workers Edge   │
│  - Host: https://<your-subdomain>.pages.dev            │
│  - Framework: React 19 + TanStack Start (Nitro)        │
│  - Asset CDN: Global Anycast CDN with automatic TLS    │
└────────────────┬───────────────────────────────────────┘
                 │ REST API Calls (VITE_API_BASE_URL)
                 ▼
┌────────────────────────────────────────────────────────┐
│  Application Layer: Render / Railway Web Service       │
│  - Host: https://<your-backend-app>.onrender.com       │
│  - Runtime: Python 3.12 + FastAPI + Uvicorn            │
│  - Engine: Rule Engine + Random Forest + Isolation F.  │
│  - Reverse Proxy: Forwarded HTTPS with CORS Validation │
└────────────────┬───────────────────────────────────────┘
                 │ Encrypted TLS Connection (PyMongo)
                 ▼
┌────────────────────────────────────────────────────────┐
│  Persistence Layer: MongoDB Atlas M0 Cluster           │
│  - Host: cluster0.mongodb.net (Replica Set)            │
│  - Collections: 10 Indexed Collections                 │
│  - Security: TLS 1.3 in transit, AES-256 at rest       │
└────────────────────────────────────────────────────────┘
```

---

## 2. Hosting Provider Selection & Economics

| Tier / Layer | Recommended Cloud Provider | Free-Tier Limitations & Behavior | Estimated Monthly Cost |
| :--- | :--- | :--- | :---: |
| **Frontend** | **Cloudflare Pages** | Unlimited bandwidth, 500 builds/month, global edge CDN. Zero sleep behavior. | **$0.00** |
| **Backend** | **Render (Web Service)** | 512 MB RAM, shared CPU. Spins down after 15 minutes of inactivity (50s cold start). | **$0.00** |
| *(Alternative)* | **Railway (Hobby)** | 512 MB RAM, no sleep, requires credit card ($5 free credit granted monthly). | ~$0.00 - $3.00 |
| **Database** | **MongoDB Atlas (M0)** | 512 MB storage, shared RAM, replica set. No expiration, always online. | **$0.00** |

> [!TIP]
> **Mitigating Render Cold Starts**:
> Render's free tier sleeps when inactive. When loading the SOC dashboard after a period of dormancy, the initial API call may take 45–60 seconds to spin up. You can keep the service warm using a free uptime ping service (such as [UptimeRobot](https://uptimerobot.com)) pointing to `https://<your-backend-app>.onrender.com/api/v1/health/ping` every 10 minutes.

---

## 3. Production Environment Variables Reference

All sensitive secrets must be entered directly into the cloud provider's web console. **Never commit real values to version control.**

### Backend Environment Variables (Configured in Render / Railway)

| Variable Name | Required | Example Production Value / Description |
| :--- | :---: | :--- |
| `DATABASE_TYPE` | Yes | `mongodb` |
| `MONGODB_URI` | Yes | `mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority` |
| `MONGODB_DATABASE` | Yes | `sentinelai` |
| `SECRET_KEY` | Yes | High-entropy random string (at least 32 characters long) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | `1440` (24-hour token validity) |
| `CORS_ORIGINS` | Yes | `["https://<your-frontend>.pages.dev", "http://localhost:8080"]` |
| `HOST` | Yes | `0.0.0.0` |
| `PORT` | Yes | `8000` (Render/Railway sets `$PORT` dynamically) |
| `ENABLE_BACKGROUND_WORKERS` | Yes | `true` |
| `LOG_LEVEL` | No | `INFO` |
| `FIREWALL_MODE` | Yes | `simulation` *(Crucial: keep in simulation mode)* |
| `ALLOW_FIREWALL_BLOCKING`| Yes | `false` |
| `ALERT_ONLY_MODE` | Yes | `true` |
| `DEFAULT_BLOCK_DURATION_MINUTES` | No | `60` |
| `PROTECTED_IPS` | No | `["127.0.0.1","::1","192.168.1.1","192.168.0.1","10.0.0.1","8.8.8.8","8.8.4.4","1.1.1.1"]` |
| `PROTECTED_NETWORKS` | No | `["127.0.0.0/8","::1/128","169.254.0.0/16","224.0.0.0/4","255.255.255.255/32"]` |

### Frontend Environment Variables (Configured in Cloudflare Pages)

| Variable Name | Required | Example Production Value / Description |
| :--- | :---: | :--- |
| `VITE_API_BASE_URL` | Yes | `https://<your-backend-app>.onrender.com/api/v1` |

---

## 4. Step-by-Step Deployment Instructions

### Step 4.1: Configure MongoDB Atlas Network Access

Because PaaS providers (Render, Railway, Fly.io) use dynamic outbound IP pools for their free tier:

1. Sign in to the [MongoDB Atlas Console](https://cloud.mongodb.com).
2. In the left navigation bar, navigate to **Security** $\to$ **Network Access**.
3. Click **Add IP Address**:
   - For cloud PaaS compatibility: add `0.0.0.0/0` (Allow Access from Anywhere) with a description: `Cloud PaaS Access`.
   - Ensure you use a strong, unique database user password.
4. Verify database user privileges under **Security** $\to$ **Database Access**:
   - User should have `readWrite` role on the `sentinelai` database.

---

### Step 4.2: Deploy Backend to Render

1. Sign in to [Render](https://render.com) using your GitHub account.
2. Click **New +** $\to$ **Web Service**.
3. Select your GitHub repository: `<YOUR_GITHUB_USERNAME>/sentinelai`.
4. Configure service parameters:
   - **Name**: `sentinelai-backend`
   - **Region**: Select the region closest to you (e.g., `Oregon (US West)` or `Frankfurt (EU)`).
   - **Branch**: `main`
   - **Root Directory**: Leave blank (uses repo root).
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Expand **Advanced** $\to$ **Health Check Path**:
   - Set to `/api/v1/health/ping`
6. Add **Environment Variables** (from the table in Section 3):
   - Add `DATABASE_TYPE`, `MONGODB_URI`, `MONGODB_DATABASE`, `SECRET_KEY`, `CORS_ORIGINS`, `FIREWALL_MODE`, `ALLOW_FIREWALL_BLOCKING`, `ALERT_ONLY_MODE`.
7. Click **Create Web Service**.
8. Monitor the deployment log. Once deployed, note your public URL:
   `https://sentinelai-backend.onrender.com`

---

### Step 4.3: Verify Backend Health

From your terminal or PowerShell, test the hosted health endpoint:

```bash
# 1. Ping test
curl -i https://sentinelai-backend.onrender.com/api/v1/health/ping
# Expected: HTTP 200 {"status":"ok","timestamp":...}

# 2. Database readiness check
curl -i https://sentinelai-backend.onrender.com/api/v1/health/ready
# Expected: HTTP 200 {"status":"ready","database":"connected",...}
```

---

### Step 4.4: Deploy Frontend to Cloudflare Pages

1. Sign in to the [Cloudflare Dashboard](https://dash.cloudflare.com).
2. In the sidebar, select **Workers & Pages** $\to$ **Create application** $\to$ **Pages** tab.
3. Click **Connect to Git** and authorize your GitHub account.
4. Select the `sentinelai` repository.
5. In the **Set up builds and deployments** screen:
   - **Project name**: `sentinelai`
   - **Production branch**: `main`
   - **Framework preset**: Select **None** (or **Vite**).
   - **Build command**: `npm run build`
   - **Build output directory**: `.output/public`
6. Expand **Environment variables (advanced)**:
   - Variable name: `VITE_API_BASE_URL`
   - Value: `https://sentinelai-backend.onrender.com/api/v1`
7. Click **Save and Deploy**.
8. Cloudflare will install dependencies, compile the TypeScript bundle, and publish your site at:
   `https://sentinelai.pages.dev`

---

### Step 4.5: Update Backend CORS Origins

Now that Cloudflare has assigned your official frontend URL:

1. Return to the [Render Dashboard](https://dashboard.render.com).
2. Open your `sentinelai-backend` service $\to$ **Environment**.
3. Edit `CORS_ORIGINS`:
   ```json
   ["https://sentinelai.pages.dev", "http://localhost:8080"]
   ```
4. Click **Save Changes**. Render will automatically reload the application.

---

## 5. Production Health Check & Verification Checklist

Once both services are online, verify the complete security flow:

| Verification Step | Target URL / Action | Expected Result |
| :--- | :--- | :--- |
| **HTTPS Certificate** | `https://sentinelai.pages.dev` | Valid TLS 1.3 certificate with padlock icon |
| **SPA Route Refresh** | Refresh browser on `/threats` or `/settings` | Page renders cleanly without 404 Not Found |
| **Backend Ping** | `GET /api/v1/health/ping` | `HTTP 200 {"status": "ok"}` |
| **Database Readiness** | `GET /api/v1/health/ready` | `HTTP 200 {"database": "connected"}` |
| **Analyst Profile** | `GET /api/v1/profile` | Shows `Ciciliya Inace` / `ciciliya-inace` |
| **Simulated Detection** | `POST /api/v1/events/simulate?scenario=dos_syn_flood` | Alert created, RF score $> 90$ |
| **Protected Target** | Block request for `127.0.0.1` | Rejected with `HTTP 400 protected_target` |
| **Approval & Rollback** | Approve rule $\to$ Rollback rule | State transitions: `pending` $\to$ `active` $\to$ `rolled_back` |
| **Audit Log Integrity** | `GET /api/v1/audit` | Immutable audit entries for all actions |

---

## 6. Troubleshooting Common Issues

### 1. CORS Error in Browser Console (`Access-Control-Allow-Origin`)
- **Symptom**: Browser red console error: *CORS policy: No 'Access-Control-Allow-Origin' header is present*.
- **Fix**: Verify that the exact domain of your Cloudflare Pages URL (e.g. `https://sentinelai.pages.dev` without trailing slash) is included in the backend's `CORS_ORIGINS` environment variable in Render.

### 2. Backend Health Check Reports Database Disconnected
- **Symptom**: `/api/v1/health/ready` returns `status: degraded`, `database: disconnected`.
- **Fix**:
  1. In MongoDB Atlas, verify that `0.0.0.0/0` is active in **Network Access**.
  2. Verify that `MONGODB_URI` contains valid credentials and that special characters in the password are URL-encoded if applicable.

### 3. Frontend Route Refresh Returns 404 on Cloudflare
- **Symptom**: Navigating within the dashboard works, but refreshing on `https://sentinelai.pages.dev/settings` displays a 404.
- **Fix**: The project build output includes `.output/public/_headers` and routing configurations. If using standard static hosting, ensure a `_redirects` or `404.html` fallback rule redirects `/* /index.html 200`.

### 4. Render Cold Start Latency
- **Symptom**: First request after a break takes 40–50 seconds.
- **Fix**: This is expected on free-tier instances. Keep the instance warm using an external periodic ping to `/api/v1/health/ping`.

---

## 7. Redeployment & Rollback Procedures

### Redeploying New Changes
1. On your development machine, make and test your changes locally (`pytest backend/tests` and `npm run build`).
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "fix: updated detection threshold"
   git push origin main
   ```
3. Cloudflare Pages and Render will automatically trigger new builds from the `main` branch.

### Rolling Back a Failed Release
- **In Render**: Navigate to **Deploys** $\to$ click the previous successful build $\to$ click **Rollback to this deploy**.
- **In Cloudflare Pages**: Navigate to **Deployments** $\to$ click the previous working deployment $\to$ click **Rollback**.
