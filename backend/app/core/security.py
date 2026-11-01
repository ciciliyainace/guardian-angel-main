from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a cryptographically signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token signature has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid authentication token")


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a cryptographically secure, random URL-safe token."""
    import secrets
    return secrets.token_urlsafe(nbytes)


def hash_token(raw_token: str) -> str:
    """Hash a token using SHA-256 for secure database storage."""
    import hashlib
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets cybersecurity complexity requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit or special character
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters in length."
    if not any(c.isupper() for c in password):
        return False, "Password must include at least one uppercase letter (A-Z)."
    if not any(c.islower() for c in password):
        return False, "Password must include at least one lowercase letter (a-z)."
    if not (any(c.isdigit() for c in password) or any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)):
        return False, "Password must include at least one number (0-9) or special symbol."
    return True, "Password meets security requirements."

