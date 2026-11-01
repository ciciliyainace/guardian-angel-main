# SentinelAI — Manual GitHub Upload & Transfer Guide

This guide provides step-by-step instructions for copying this project to another device and manually pushing it to a new GitHub repository using your own personal Git account.

---

## 1. File Inclusion & Exclusion Rules

Before transferring or committing files, review what must be included and what must **never** be uploaded.

### What MUST Be Included in GitHub:
- `src/` — Complete React + TypeScript frontend components, routes, and styles.
- `backend/` — FastAPI application, API routes, detection rules, services, models, and test suite.
- `artifacts/` — Machine learning model joblib binaries (`random_forest.joblib`, `decision_tree.joblib`, `isolation_forest.joblib`).
- `docs/` — Full project report, architecture diagrams, demonstration guide, and viva questions.
- `package.json` & `package-lock.json` — Frontend package specifications and reproducible dependency lockfile.
- `vite.config.ts`, `tsconfig.json`, `eslint.config.js` — Frontend build tools and TypeScript configuration.
- `backend/requirements.txt` — Python backend dependency declarations.
- `backend/Dockerfile`, `backend/Procfile`, `Procfile`, `render.yaml` — Production container and PaaS deployment manifests.
- `.gitignore` & `backend/.gitignore` — Security exclusion filters.
- `.env.example` & `backend/.env.example` — Configuration templates containing safe placeholders only.
- `README.md` & `backend/README.md` — Project documentation.

### What Must NEVER Be Uploaded (Strictly Excluded):
| File / Directory | Reason for Exclusion | Filter Rule in `.gitignore` |
| :--- | :--- | :--- |
| `.env`, `backend/.env` | Contains real MongoDB connection strings and secret keys | `.env`, `*.env`, `backend/.env` |
| `node_modules/` | Large external JavaScript packages (re-installed via `npm install`) | `node_modules/` |
| `.venv/`, `venv/`, `env/` | Local Python virtual environment (re-installed via `pip install`) | `.venv/`, `venv/` |
| `.output/`, `dist/`, `.nitro/` | Temporary compiled frontend build output | `.output/`, `dist/` |
| `logs/`, `*.log` | Local execution logs and diagnostic output | `logs/`, `*.log` |
| `.pytest_cache/`, `.coverage` | Local Python test caches and coverage reports | `.pytest_cache/`, `.coverage` |
| `artifacts/suricata_checkpoint.json` | Local sensor checkpoint file with local file offsets | `*checkpoint.json` |
| `*.db`, `*.sqlite`, `*.sqlite3` | Local SQLite database files | `*.db`, `*.sqlite3` |
| `.DS_Store`, `Thumbs.db` | Operating system metadata files | `.DS_Store`, `Thumbs.db` |

---

## 2. Preparing the Project for Transfer

### Option A: Transfer via USB Drive or Cloud Storage Archive

When copying the project folder to your other device, either:

1. **Delete or exclude the generated directories** before copying:
   - Delete `node_modules/` (saves ~300 MB of transfer size).
   - Delete `.venv/` (saves ~400 MB of transfer size).
   - Delete `.output/` (saves build caches).
   - Ensure you **do NOT copy** `.env` or `backend/.env` if using a shared drive.
2. Alternatively, create a clean ZIP archive excluding ignored folders using PowerShell:

```powershell
# From the parent directory (guardian-angel-main):
# Exclude node_modules, .venv, .output, and .env files
Compress-Archive -Path `
    .\guardian-angel-main\src, `
    .\guardian-angel-main\backend, `
    .\guardian-angel-main\artifacts, `
    .\guardian-angel-main\docs, `
    .\guardian-angel-main\public, `
    .\guardian-angel-main\package.json, `
    .\guardian-angel-main\package-lock.json, `
    .\guardian-angel-main\vite.config.ts, `
    .\guardian-angel-main\tsconfig.json, `
    .\guardian-angel-main\render.yaml, `
    .\guardian-angel-main\Procfile, `
    .\guardian-angel-main\.env.example, `
    .\guardian-angel-main\.gitignore, `
    .\guardian-angel-main\README.md `
    -DestinationPath ".\sentinelai_clean_source.zip"
```

---

## 3. Creating a New Empty Repository on GitHub

1. Open your web browser on your other device and sign in to [GitHub](https://github.com).
2. Click the **`+`** icon in the top right corner and select **New repository**.
3. Configure repository settings:
   - **Repository name**: `sentinelai` (or `sentinelai-defense-system`).
   - **Description**: `SentinelAI — AI-Powered Firewall Attack Detection System for Computer Networks`.
   - **Visibility**: Select **Private** (recommended until viva completion) or **Public**.
   - **Initialize this repository with**:
     - [ ] **Do NOT check** "Add a README file".
     - [ ] **Do NOT check** "Add .gitignore".
     - [ ] **Do NOT check** "Choose a license".
   *(Leaving these unchecked ensures the repository starts completely empty, preventing merge conflicts).*
4. Click **Create repository**.
5. Copy the HTTPS repository URL (e.g., `https://github.com/<YOUR_GITHUB_USERNAME>/sentinelai.git`).

---

## 4. Pushing from the Other Device

Open your terminal or PowerShell on your other device, navigate to the extracted `sentinelai` project directory, and execute the following exact commands:

```bash
# 1. Navigate into the project folder
cd /path/to/sentinelai

# 2. Verify that .env is NOT present (it should not be committed)
# Ensure only .env.example exists

# 3. Initialize a clean local Git repository
git init

# 4. Check that .gitignore is actively filtering node_modules, .venv, and logs
git status

# 5. Stage all clean source files
git add .

# 6. Verify staged files before committing (ensure no .env or credentials appear)
git status

# 7. Create the initial commit
git commit -m "feat: initial commit of SentinelAI hybrid defense system"

# 8. Set the default branch name to main
git branch -M main

# 9. Link to your new empty GitHub repository (replace with your actual GitHub username and repo)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git

# 10. Push the code to GitHub
git push -u origin main
```

---

## 5. Post-Upload Verification on GitHub

After the push completes, open your repository on GitHub and verify:

1. **Root Directory**:
   - `.env` must **NOT** be visible.
   - `.env.example` **MUST** be visible (containing placeholders only).
   - `node_modules/` and `.venv/` must **NOT** be present.
   - `artifacts/` must contain `random_forest.joblib`, `decision_tree.joblib`, and `isolation_forest.joblib`.
   - `docs/` must contain all project documentation.
2. **Search Verification**:
   - In the GitHub repository search bar, search for `mongodb+srv://` or your database password to verify zero credentials were leaked.

---

## 6. Cloud Deployment from GitHub

Once your repository is on GitHub, you can link it directly to hosting providers for automated builds and HTTPS hosting:

### A. Deploy FastAPI Backend on Render (Free Tier)
1. Sign in to [Render](https://render.com) using your GitHub account.
2. Click **New +** $\to$ **Blueprint** (or **Web Service**).
3. Connect your `sentinelai` repository.
4. Render detects [`render.yaml`](file:///d:/project/unexpected/New%20folder/guardian-angel-main/guardian-angel-main/render.yaml) automatically:
   - **Runtime**: Python 3.12
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
5. In the **Environment Variables** tab in Render, enter your secrets:
   - `MONGODB_URI`: `mongodb+srv://<user>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority`
   - `MONGODB_DATABASE`: `sentinelai`
   - `CORS_ORIGINS`: `["https://<your-frontend>.pages.dev"]`
6. Click **Create Web Service**. Once deployed, Render provides your backend public URL (e.g., `https://sentinelai-backend.onrender.com`).

### B. Deploy React Frontend on Cloudflare Pages (Free Tier)
1. Sign in to [Cloudflare Dashboard](https://dash.cloudflare.com) $\to$ **Workers & Pages**.
2. Click **Create Application** $\to$ **Pages** $\to$ **Connect to Git**.
3. Select your `sentinelai` repository.
4. Configure Build Settings:
   - **Framework Preset**: `None` (or `Vite`)
   - **Build command**: `npm run build`
   - **Build output directory**: `.output/public`
5. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://sentinelai-backend.onrender.com/api/v1` (your Render backend URL).
6. Click **Save and Deploy**.
7. Cloudflare automatically compiles the application and assigns a public HTTPS URL (e.g., `https://sentinelai.pages.dev`).

### C. Update Backend CORS Origin
After Cloudflare assigns your frontend URL (`https://<app>.pages.dev`):
1. Go back to Render Dashboard $\to$ **Environment Variables**.
2. Update `CORS_ORIGINS` to include your new frontend URL:
   ```json
   ["https://<app>.pages.dev", "http://localhost:8080"]
   ```
3. Save and trigger a quick reload in Render. Your production deployment is now live and secured with end-to-end HTTPS.
