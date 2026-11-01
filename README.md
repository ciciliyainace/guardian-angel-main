# SentinelAI — AI-Powered Network Firewall Attack Detection System

SentinelAI is an intelligent Cybersecurity Defense System that continuously monitors computer network telemetry, detects sophisticated attacks using ensemble Machine Learning (Random Forest, Decision Tree, Isolation Forest), and automates firewall mitigation with zero-lockout safeguards.

## Features
- **Intelligent Threat Detection**: Multiclass cyberattack detection (DDoS, Port Scan, Brute Force, Web Attacks, Infiltration) and anomaly detection.
- **Enterprise Authentication**: User registration with password strength analysis, email & username login, rate limiting / brute-force lockout, single-use hashed verification tokens, and Google OAuth 2.0 / OpenID Connect identity federation.
- **Persistent Storage**: MongoDB Atlas cluster with unique indexes and TTL collections.
- **Notification Engine**: Transactional email notification service for welcome registration, first-time login security alerts, email verification, and password recovery.
- **Safe Firewall Execution**: Simulation mode with Windows Defender Firewall execution adapter and protected subnet safeguards.

## Architecture & Authentication Documentation
Detailed setup guides are available in:
- [Authentication & Notification Guide](docs/AUTHENTICATION.md)
- [Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- MongoDB Atlas cluster URI

### 2. Backend Setup
```powershell
# Copy environment configuration
cp backend/.env.example backend/.env

# Run backend API server (FastAPI on port 8000)
.\backend\run_backend.bat
# Or manually:
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```powershell
# Install frontend dependencies
npm install

# Start Vite dev server on port 5173
npm run dev
```

### 4. Running Automated Tests
```powershell
# Run backend pytest suite (61 tests covering auth, ml, firewall, and collectors)
.venv\Scripts\pytest -v backend/tests/test_auth_system.py

# Run frontend Vitest suite (10 tests covering auth routes and validation)
npm test

# Run frontend production build
npm run build
```

## Authentication Routes
- **Login**: `http://localhost:5173/login`
- **Register**: `http://localhost:5173/register`
- **Forgot Password**: `http://localhost:5173/forgot-password`
- **Reset Password**: `http://localhost:5173/reset-password`
- **Email Verification**: `http://localhost:5173/verify-email`
- **Google OAuth Callback**: `http://localhost:5173/auth/google/callback`
- **Security Dashboard**: `http://localhost:5173/` (Protected)
