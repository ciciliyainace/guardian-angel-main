# SentinelAI — Complete Authentication & Notification Architecture Guide

## 1. System Overview

SentinelAI incorporates a multi-layer cybersecurity authentication, Google OAuth 2.0 / OpenID Connect identity federation, MongoDB Atlas persistence, and transactional email notification service.

```
                    ┌───────────────────────────────────────────────┐
                    │               Frontend (React)                │
                    │  Login / Register / Forgot / Reset / Verify   │
                    └──────────────────────┬────────────────────────┘
                                           │
                           REST API + Bearer JWT / JSON
                                           │
                    ┌──────────────────────▼────────────────────────┐
                    │          FastAPI Backend Application          │
                    ├───────────────────────────────────────────────┤
                    │ • Rate Limiting & Account Lockout Guard       │
                    │ • Bcrypt Password Hashing & Salt (12 rounds)  │
                    │ • Single-Use Cryptographic SHA-256 Tokens     │
                    │ • Role-Based Access Control (Analyst / Admin) │
                    └───────┬───────────────────────────────┬───────┘
                            │                               │
             PyMongo Driver │                               │ TLS / SMTP
                            ▼                               ▼
       ┌───────────────────────────────┐        ┌─────────────────────────┐
       │         MongoDB Atlas         │        │    SMTP Email Provider  │
       │ • users (unique index)        │        │ • Welcome Notification  │
       │ • auth_tokens (TTL index)     │        │ • First Login Alert     │
       │ • login_attempts (TTL index)  │        │ • Password Reset Token  │
       │ • audit_logs (traceability)   │        │ • Email Verification    │
       └───────────────────────────────┘        └─────────────────────────┘
```

---

## 2. Environment Variables Specification

Configure the following parameters in `backend/.env` (and root `.env`):

```env
# Database (MongoDB Atlas)
DATABASE_TYPE=mongodb
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=sentinelai

# Security & JWT Tokens
SECRET_KEY=sentinelai-secret-key-change-in-production-must-be-at-least-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REQUIRE_EMAIL_VERIFICATION=false
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=15

# SMTP Email Notification Service
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-soc-alerts@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
MAIL_FROM_EMAIL=your-soc-alerts@gmail.com
MAIL_FROM_NAME="SentinelAI SOC"
FRONTEND_BASE_URL=http://localhost:5173

# Google OAuth 2.0 / OpenID Connect
GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback
```

---

## 3. MongoDB Atlas Configuration & Unique Indexes

### Schema Design (`users` collection)
```json
{
  "id": 1,
  "username": "sarah_connor",
  "email": "sarah@cyberdyne.com",
  "display_name": "Sarah Connor",
  "hashed_password": "$2b$12$e8Yy8...",
  "password_hash": "$2b$12$e8Yy8...",
  "role": "analyst",
  "auth_providers": ["password"],
  "google_sub": null,
  "email_verified": false,
  "is_active": true,
  "created_at": "2026-11-02T01:30:00Z",
  "updated_at": "2026-11-02T01:30:00Z",
  "first_login_at": null,
  "last_login_at": null,
  "welcome_email_sent_at": "2026-11-02T01:30:02Z",
  "first_login_email_sent_at": null,
  "failed_login_attempts": 0,
  "lockout_until": null
}
```

### Auto-Initialized Indexes:
- `db.users.create_index("username", unique=True)`
- `db.users.create_index("email", unique=True)`
- `db.users.create_index("google_sub", sparse=True)`
- `db.auth_tokens.create_index("token_hash", unique=True)`
- `db.auth_tokens.create_index([("expires_at", 1)], expireAfterSeconds=0)` (MongoDB automatic TTL cleanup)
- `db.login_attempts.create_index("key", unique=True)`
- `db.login_attempts.create_index([("expires_at", 1)], expireAfterSeconds=0)`

---

## 4. Google Cloud OAuth 2.0 Setup

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **APIs & Services** > **OAuth consent screen**:
   - Select **External** (or **Internal** if using Google Workspace).
   - Enter App Name: `SentinelAI Defense System`.
   - Add scopes: `.../auth/userinfo.email`, `.../auth/userinfo.profile`, `openid`.
3. Navigate to **Credentials** > **Create Credentials** > **OAuth client ID**:
   - Application type: **Web application**.
   - Name: `SentinelAI Web Client`.
   - **Authorized JavaScript origins**:
     - `http://localhost:5173`
     - `http://127.0.0.1:5173`
     - `https://your-production-domain.com`
   - **Authorized redirect URIs**:
     - `http://localhost:5173/auth/google/callback`
     - `https://your-production-domain.com/auth/google/callback`
4. Copy the generated **Client ID** and **Client Secret** into your `backend/.env`.

---

## 5. SMTP Email Provider Setup

### Option A: Gmail SMTP (Development / Small Teams)
1. Go to your Google Account > **Security** > **2-Step Verification**.
2. Scroll down to **App Passwords**.
3. Generate an App Password for `SentinelAI`.
4. Set in `backend/.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-account@gmail.com
   SMTP_PASSWORD=<16-character-app-password>
   SMTP_USE_TLS=true
   MAIL_FROM_EMAIL=your-account@gmail.com
   ```

### Option B: SendGrid / Mailgun / AWS SES
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
SMTP_USE_TLS=true
MAIL_FROM_EMAIL=no-reply@yourverifieddomain.com
```

> **Safe Offline Mode**: If `SMTP_HOST` is omitted, the email service records delivery as `awaiting_configuration`. Registrations and logins proceed safely without blocking.

---

## 6. How to Create the First Administrator Securely

To provision the initial administrator account without exposing plaintext credentials:

### Method 1: Using Python Interactive CLI
In PowerShell:
```powershell
.venv\Scripts\python -c "from app.core.database import get_database; from app.core.security import hash_password; from app.repositories.user_repository import UserRepository; from app.models.user import User; db = get_database(); repo = UserRepository(db); u = User(email='admin@sentinelai.local', username='admin_soc', display_name='Chief SOC Admin', hashed_password=hash_password('AdminMasterKey2026!'), role='administrator', email_verified=True); repo.create(u); print('Admin provisioned successfully!')"
```

### Method 2: Promoting an Existing Analyst
```powershell
.venv\Scripts\python -c "from app.core.database import get_database; db = get_database(); res = db.users.update_one({'username': 'sarah_connor'}, {'$set': {'role': 'administrator', 'email_verified': True}}); print('Updated count:', res.modified_count)"
```

---

## 7. Testing Registration, Login & Email Delivery

### Automated Tests
```powershell
# Run backend pytest suite (all 61 tests)
.venv\Scripts\pytest -v backend/tests/test_auth_system.py

# Run frontend Vitest suite (10 tests)
npm test

# Run production build
npm run build
```

### Manual Verification Flow
1. Start Backend:
   ```powershell
   .\backend\run_backend.bat
   ```
2. Start Frontend:
   ```powershell
   npm run dev
   ```
3. Navigate to `http://localhost:5173/register`:
   - Fill in username, email, password. Notice real-time password strength meter and confirmation check.
   - Click **Create Account**. Notice success confirmation view.
4. Check your inbox for the welcome email with link.
5. Navigate to `http://localhost:5173/login`:
   - Sign in using your registered username or email.
   - Upon first successful sign in, the backend sends the single first-login security notification.
   - You are redirected to the protected SOC Overview Dashboard.
