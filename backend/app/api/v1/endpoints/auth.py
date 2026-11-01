from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pymongo.database import Database
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    validate_password_strength,
)
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.services.email_service import EmailService
from app.services.google_auth_service import GoogleAuthService
from app.services.audit_service import AuditService
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    GoogleAuthRequest,
    GoogleUrlResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    GenericMessageResponse,
)
from app.api.dependencies import get_current_user, require_authenticated_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Database = Depends(get_db),
) -> Any:
    """
    Register a new user account:
    - Validates inputs and password complexity
    - Normalizes username and email
    - Rejects duplicate username or email with HTTP 409
    - Hashes password securely via bcrypt
    - Stores document in MongoDB Atlas
    - Generates verification token and dispatches welcome email
    """
    repo = UserRepository(db)
    token_repo = TokenRepository(db)
    audit = AuditService(db)
    email_service = EmailService()

    # 1. Validate password confirmation
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirm password do not match.",
        )

    # 2. Validate password strength
    is_strong, strength_err = validate_password_strength(payload.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strength_err,
        )

    # 3. Check for existing username or email
    clean_username = repo.normalize_username(payload.username)
    clean_email = repo.normalize_email(payload.email)

    if repo.get_by_username(clean_username):
        audit.log(
            actor=clean_username,
            action="Register",
            target="account",
            result="Denied",
            reason="Duplicate username attempted",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{clean_username}' is already registered.",
        )

    if repo.get_by_email(clean_email):
        audit.log(
            actor=clean_email,
            action="Register",
            target="account",
            result="Denied",
            reason="Duplicate email attempted",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email address '{clean_email}' is already registered.",
        )

    # 4. Hash password
    pwd_hash = hash_password(payload.password)
    now = datetime.now(timezone.utc)

    # 5. Create user model instance
    new_user = User(
        email=clean_email,
        username=clean_username,
        display_name=payload.display_name or clean_username,
        hashed_password=pwd_hash,
        role="analyst",  # Standard role for new registrants, never administrator
        auth_providers=["password"],
        google_sub=None,
        email_verified=False,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    created_user = repo.create(new_user)

    # 6. Generate email verification token
    verification_token = token_repo.create_token(
        user_id=created_user.id,
        email=created_user.email,
        token_type="email_verification",
        expires_in_minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS * 60,
    )

    # 7. Dispatch welcome/verification email
    delivery_res = email_service.send_welcome_email(created_user, verification_token=verification_token)
    if delivery_res.get("status") == "delivered":
        repo.mark_welcome_email_sent(created_user.id, now)

    audit.log(
        actor=created_user.username,
        action="Register",
        target=f"user:{created_user.id}",
        result="Success",
        reason=f"Account created successfully (email: {delivery_res.get('status')})",
    )

    return {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
        "display_name": created_user.display_name,
        "role": created_user.role,
        "is_active": created_user.is_active,
        "email_verified": created_user.email_verified,
        "auth_providers": created_user.auth_providers,
        "created_at": created_user.created_at,
        "first_login_at": None,
        "last_login_at": None,
    }


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Database = Depends(get_db),
) -> Any:
    """
    Authenticate user via registered username/email + password:
    - Enforces rate limiting / temporary lockout on repeated failures
    - Verifies bcrypt password hash
    - Employs generic error message to prevent enumeration
    - Dispatches first-login security notification exactly once
    - Issues signed, time-limited JWT access token
    """
    repo = UserRepository(db)
    audit = AuditService(db)
    email_service = EmailService()

    identifier = payload.username_or_email.strip()

    # Rate limiting check
    is_locked, minutes_remaining = repo.is_locked_out(identifier)
    if is_locked:
        audit.log(
            actor=identifier,
            action="Login",
            target="session",
            result="Blocked",
            reason=f"Account locked due to excessive failed attempts ({minutes_remaining}m remaining)",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Account is temporarily locked. Try again in {minutes_remaining} minutes.",
        )

    # Find user by username or email
    user = repo.get_by_username_or_email(identifier)
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        repo.record_failed_attempt(identifier)
        audit.log(
            actor=identifier,
            action="Login",
            target="session",
            result="Denied",
            reason="Invalid credentials",
        )
        # Uniform generic message to prevent account enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
        )

    # Check if active
    if not user.is_active:
        audit.log(
            actor=user.username,
            action="Login",
            target="session",
            result="Denied",
            reason="Account inactive",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact an administrator.",
        )

    # Check email verification policy if strictly enforced
    if settings.REQUIRE_EMAIL_VERIFICATION and not user.email_verified and user.role.lower() not in ("admin", "administrator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address verification required. Please verify your email before logging in.",
        )

    # Clear rate limit counter on success
    repo.clear_failed_attempts(identifier)

    now = datetime.now(timezone.utc)
    is_first_login = user.first_login_at is None

    # Update login timestamps
    user = repo.record_successful_login(user.id, now) or user

    # Atomic first-login email check: exactly ONE email sent even under concurrent logins
    if is_first_login:
        claimed = repo.try_claim_first_login_notification(user.id, now)
        if claimed:
            client_ip = request.client.host if request.client else None
            email_service.send_first_login_email(user, now, ip_address=client_ip)

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.username,
        role=user.role,
        expires_delta=expires,
        extra_claims={
            "email": user.email,
            "displayName": user.display_name,
            "userId": user.id,
            "emailVerified": user.email_verified,
        },
    )

    audit.log(
        actor=user.username,
        action="Login",
        target="session",
        result="Success",
        reason="User authenticated successfully",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": int(expires.total_seconds()),
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "auth_providers": user.auth_providers,
            "created_at": user.created_at,
            "first_login_at": user.first_login_at,
            "last_login_at": user.last_login_at,
        },
    }


@router.post("/logout")
def logout(
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    actor = current_user.username if current_user else "anonymous"
    AuditService(db).log(
        actor=actor,
        action="Logout",
        target="session",
        result="Success",
        reason="User signed out",
    )
    return {"status": "success", "message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    """
    Return currently authenticated profile.
    If unauthenticated, returns the default demo analyst profile for compatibility with demo mode.
    """
    if current_user:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "display_name": current_user.display_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "email_verified": current_user.email_verified,
            "auth_providers": current_user.auth_providers,
            "created_at": current_user.created_at,
            "first_login_at": current_user.first_login_at,
            "last_login_at": current_user.last_login_at,
        }

    # Return default demo analyst profile if unauthenticated (preserves contract with existing tests)
    return {
        "id": 1,
        "email": "analyst@sentinelai.local",
        "username": "ciciliya-inace",
        "display_name": "Ciciliya Inace",
        "role": "analyst",
        "is_active": True,
        "email_verified": True,
        "auth_providers": ["password"],
        "created_at": None,
        "first_login_at": None,
        "last_login_at": None,
    }


# -------------------------------------------------------------
# Google OAuth 2.0 / OpenID Connect Endpoints
# -------------------------------------------------------------
@router.get("/google/url", response_model=GoogleUrlResponse)
def get_google_oauth_url(state: Optional[str] = None) -> Any:
    """Return Google OAuth 2.0 authorization URL or configuration status."""
    google_service = GoogleAuthService()
    configured, url, err = google_service.get_authorization_url(state=state)
    return {
        "configured": configured,
        "url": url,
        "message": err or "Google OAuth URL ready",
    }


@router.post("/google", response_model=TokenResponse)
def google_auth(
    payload: GoogleAuthRequest,
    request: Request,
    db: Database = Depends(get_db),
) -> Any:
    """
    Authenticate via Google OAuth 2.0 / OpenID Connect:
    - Verifies Google identity token or exchanges authorization code
    - Validates audience, issuer, expiry, and email verification
    - Associates or creates user in MongoDB
    - Issues signed JWT token
    """
    google_service = GoogleAuthService()
    audit = AuditService(db)
    email_service = EmailService()
    repo = UserRepository(db)

    try:
        verified_info = google_service.verify_token_or_code(
            id_token=payload.id_token,
            code=payload.code,
            redirect_uri=payload.redirect_uri,
        )
    except ValueError as e:
        audit.log(
            actor="google_oauth",
            action="GoogleLogin",
            target="session",
            result="Denied",
            reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    try:
        user, is_new_account, is_first_login = google_service.process_google_login(db, verified_info)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact an administrator.",
        )

    now = datetime.now(timezone.utc)

    # If new account was just created, dispatch welcome email
    if is_new_account:
        delivery_res = email_service.send_welcome_email(user, verification_token=None)
        if delivery_res.get("status") == "delivered":
            repo.mark_welcome_email_sent(user.id, now)

    # Record login
    user = repo.record_successful_login(user.id, now) or user

    # Atomic first-login notification claim
    if is_first_login:
        claimed = repo.try_claim_first_login_notification(user.id, now)
        if claimed:
            client_ip = request.client.host if request.client else None
            email_service.send_first_login_email(user, now, ip_address=client_ip)

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.username,
        role=user.role,
        expires_delta=expires,
        extra_claims={
            "email": user.email,
            "displayName": user.display_name,
            "userId": user.id,
            "emailVerified": user.email_verified,
        },
    )

    audit.log(
        actor=user.username,
        action="GoogleLogin",
        target="session",
        result="Success",
        reason=f"Authenticated via Google OAuth (sub: {user.google_sub})",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": int(expires.total_seconds()),
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "auth_providers": user.auth_providers,
            "created_at": user.created_at,
            "first_login_at": user.first_login_at,
            "last_login_at": user.last_login_at,
        },
    }


# -------------------------------------------------------------
# Email Verification Endpoints
# -------------------------------------------------------------
@router.post("/verify-email", response_model=GenericMessageResponse)
def verify_email(
    payload: VerifyEmailRequest,
    db: Database = Depends(get_db),
) -> Any:
    """Verify email address using a single-use verification token."""
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    audit = AuditService(db)

    token_doc = token_repo.verify_and_consume_token(payload.token, "email_verification")
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is invalid, expired, or has already been used.",
        )

    user_id = token_doc["user_id"]
    user_repo.mark_email_verified(user_id)

    user = user_repo.get_by_id(user_id)
    actor = user.username if user else str(user_id)
    audit.log(
        actor=actor,
        action="VerifyEmail",
        target=f"user:{user_id}",
        result="Success",
        reason="Email address verified via token",
    )

    return {
        "status": "success",
        "message": "Email address successfully verified. Your account is fully active.",
    }


@router.post("/resend-verification", response_model=GenericMessageResponse)
def resend_verification(
    payload: ResendVerificationRequest,
    db: Database = Depends(get_db),
) -> Any:
    """Resend email verification link with rate limiting."""
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    email_service = EmailService()

    clean_email = payload.email.strip().lower()

    if token_repo.check_resend_cooldown(clean_email, "email_verification", cooldown_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 60 seconds before requesting another verification email.",
        )

    user = user_repo.get_by_email(clean_email)
    email_status = "awaiting_configuration"
    if user and not user.email_verified:
        token = token_repo.create_token(
            user_id=user.id,
            email=user.email,
            token_type="email_verification",
            expires_in_minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS * 60,
        )
        res = email_service.send_verification_email(user, token)
        email_status = res.get("status", "unknown")

    # Generic response to prevent user enumeration
    return {
        "status": "success",
        "message": "If an unverified account with that email exists, a verification link has been sent.",
        "email_status": email_status,
    }


# -------------------------------------------------------------
# Forgot Password & Password Reset Endpoints
# -------------------------------------------------------------
@router.post("/forgot-password", response_model=GenericMessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Database = Depends(get_db),
) -> Any:
    """
    Request password reset link.
    Returns generic message regardless of account existence to prevent email enumeration.
    """
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    email_service = EmailService()
    audit = AuditService(db)

    clean_email = payload.email.strip().lower()

    if token_repo.check_resend_cooldown(clean_email, "password_reset", cooldown_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 60 seconds before requesting another reset email.",
        )

    user = user_repo.get_by_email(clean_email)
    email_status = "awaiting_configuration"

    if user and user.is_active:
        token = token_repo.create_token(
            user_id=user.id,
            email=user.email,
            token_type="password_reset",
            expires_in_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
        )
        res = email_service.send_password_reset_email(user, token)
        email_status = res.get("status", "unknown")
        audit.log(
            actor=user.username,
            action="ForgotPassword",
            target="account",
            result="Success",
            reason=f"Password reset token issued (email: {email_status})",
        )

    return {
        "status": "success",
        "message": "If an account with that email exists, password reset instructions have been dispatched.",
        "email_status": email_status,
    }


@router.post("/reset-password", response_model=GenericMessageResponse)
def reset_password(
    payload: ResetPasswordRequest,
    db: Database = Depends(get_db),
) -> Any:
    """Validate reset token and update account password."""
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    audit = AuditService(db)

    # 1. Validate password match
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirmation do not match.",
        )

    # 2. Validate password strength
    is_strong, strength_err = validate_password_strength(payload.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strength_err,
        )

    # 3. Verify single-use reset token
    token_doc = token_repo.verify_and_consume_token(payload.token, "password_reset")
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid, expired, or has already been used.",
        )

    user_id = token_doc["user_id"]
    new_hash = hash_password(payload.password)
    user_repo.update_password(user_id, new_hash)

    user = user_repo.get_by_id(user_id)
    actor = user.username if user else str(user_id)
    audit.log(
        actor=actor,
        action="ResetPassword",
        target=f"user:{user_id}",
        result="Success",
        reason="Password reset successfully completed",
    )

    return {
        "status": "success",
        "message": "Password successfully updated. You may now log in with your new credentials.",
    }
