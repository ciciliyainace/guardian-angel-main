from typing import Generator, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pymongo.database import Database
from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.workspace import Workspace

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: Database = Depends(get_db),
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[User]:
    """
    Extract and validate current authenticated user from Bearer token.
    Identifies the user via immutable user ID in JWT 'sub' with username fallback.
    Never falls back to hardcoded default user.
    """
    if not auth or not auth.credentials:
        return None

    try:
        payload = decode_access_token(auth.credentials)
        sub = payload.get("sub")
        if not sub:
            return None
        user_repo = UserRepository(db)
        # Primary lookup: by immutable integer/string user ID
        user = None
        if isinstance(sub, int) or (isinstance(sub, str) and sub.isdigit()):
            user = user_repo.get_by_id(int(sub))
        # Secondary lookup: for backward compatibility if sub was username/email
        if not user:
            user = user_repo.get_by_username(str(sub)) or user_repo.get_by_username_or_email(str(sub))
        return user
    except Exception:
        return None


def get_optional_user_unlocked(
    request: Request,
    db: Database = Depends(get_db),
) -> Optional[User]:
    """
    Extract and validate current authenticated user from request Authorization header
    WITHOUT declaring an OpenAPI SecurityBase scheme. This avoids Swagger UI placing
    a misleading lock icon on dual-mode endpoints (such as Mode 1 sensor enrollment).
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    raw_token = auth[7:].strip()
    try:
        payload = decode_access_token(raw_token)
        sub = payload.get("sub")
        if not sub:
            return None
        user_repo = UserRepository(db)
        user = None
        if isinstance(sub, int) or (isinstance(sub, str) and sub.isdigit()):
            user = user_repo.get_by_id(int(sub))
        if not user:
            user = user_repo.get_by_username(str(sub)) or user_repo.get_by_username_or_email(str(sub))
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


def get_current_workspace(
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
) -> Workspace:
    """
    Resolves the authenticated user's active private workspace.
    Guarantees tenant isolation: all queries bind to the verified workspace.
    """
    from app.repositories.workspace_repository import WorkspaceRepository
    ws_repo = WorkspaceRepository(db)

    ws = None
    if current_user.default_workspace_id:
        ws = ws_repo.get_by_id(current_user.default_workspace_id)
    if not ws:
        ws = ws_repo.get_or_create_default_workspace(current_user.id, current_user.username)
        if current_user.default_workspace_id != ws.id:
            current_user.default_workspace_id = ws.id
            UserRepository(db).update(current_user)
    return ws
