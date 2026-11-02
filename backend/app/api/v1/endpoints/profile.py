from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, hash_password
from app.schemas.settings import ProfileResponse, ProfileUpdate
from app.api.dependencies import require_authenticated_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.token_repository import TokenRepository
from app.services.email_service import EmailService

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
) -> Any:
    """Return the authenticated user's actual database record."""
    ws_repo = WorkspaceRepository(db)
    ws = None
    if current_user.default_workspace_id:
        ws = ws_repo.get_by_id(current_user.default_workspace_id)
    if not ws:
        ws = ws_repo.get_or_create_default_workspace(current_user.id, current_user.username)
        current_user.default_workspace_id = ws.id
        UserRepository(db).update(current_user)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "displayName": current_user.display_name,
        "role": current_user.role,
        "email_verified": bool(current_user.email_verified),
        "emailVerified": bool(current_user.email_verified),
        "auth_providers": current_user.auth_providers,
        "default_workspace_id": ws.id,
        "workspace_name": ws.name,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
    }


@router.patch("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
) -> Any:
    user_repo = UserRepository(db)
    ws_repo = WorkspaceRepository(db)

    email_changed = False
    if payload.displayName:
        current_user.display_name = payload.displayName.strip()
    if payload.email and payload.email.strip().lower() != current_user.email.lower():
        clean_email = payload.email.strip().lower()
        existing = user_repo.get_by_email(clean_email)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered to another account.",
            )
        current_user.email = clean_email
        current_user.email_verified = False
        email_changed = True

    if payload.newPassword:
        if not payload.currentPassword or not verify_password(payload.currentPassword, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password verification failed.",
            )
        current_user.hashed_password = hash_password(payload.newPassword)

    user_repo.update(current_user)

    if email_changed:
        token_repo = TokenRepository(db)
        verification_token = token_repo.create_token(
            user_id=current_user.id,
            email=current_user.email,
            token_type="email_verification",
            expires_in_minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS * 60,
        )
        EmailService(db).send_verification_email(current_user, verification_token)

    ws = ws_repo.get_by_id(current_user.default_workspace_id) if current_user.default_workspace_id else None
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "displayName": current_user.display_name,
        "role": current_user.role,
        "email_verified": bool(current_user.email_verified),
        "emailVerified": bool(current_user.email_verified),
        "auth_providers": current_user.auth_providers,
        "default_workspace_id": current_user.default_workspace_id,
        "workspace_name": ws.name if ws else f"{current_user.username.capitalize()}'s Workspace",
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
    }
