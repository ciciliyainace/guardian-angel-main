from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pymongo.database import Database
from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: Database = Depends(get_db),
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[User]:
    """
    Extract and validate current authenticated user from Bearer token.
    If no token is provided, returns demo user or None depending on endpoint requirements.
    """
    if not auth or not auth.credentials:
        return None

    try:
        payload = decode_access_token(auth.credentials)
        username = payload.get("sub")
        if not username:
            return None
        user_repo = UserRepository(db)
        user = user_repo.get_by_username(username) or user_repo.get_by_username_or_email(username)
        return user
    except Exception:
        return None


def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """Enforce that the caller is authenticated."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )
    return current_user


def require_admin(
    current_user: User = Depends(require_authenticated_user),
) -> User:
    """Enforce that the caller has administrator privileges."""
    if current_user.role.lower() not in ("admin", "administrator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator role required for this action.",
        )
    return current_user
