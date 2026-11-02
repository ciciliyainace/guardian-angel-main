from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.schemas.settings import ProfileResponse, ProfileUpdate
from app.api.dependencies import require_authenticated_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository

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
        "email_verified": current_user.email_verified,
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

    if payload.displayName:
        current_user.display_name = payload.displayName
    if payload.email:
        current_user.email = payload.email

    if payload.newPassword:
        if not payload.currentPassword or not verify_password(payload.currentPassword, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password verification failed.",
            )
        current_user.hashed_password = hash_password(payload.newPassword)

    repo = UserRepository(db)
    repo.update(current_user)
    ws = ws_repo.get_by_id(current_user.default_workspace_id) if current_user.default_workspace_id else None
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "displayName": current_user.display_name,
        "role": current_user.role,
        "email_verified": current_user.email_verified,
        "auth_providers": current_user.auth_providers,
        "default_workspace_id": current_user.default_workspace_id,
        "workspace_name": ws.name if ws else f"{current_user.username.capitalize()}'s Workspace",
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
    }
