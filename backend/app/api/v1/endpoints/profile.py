from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.schemas.settings import ProfileResponse, ProfileUpdate
from app.api.dependencies import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    if current_user:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "displayName": current_user.display_name,
            "role": current_user.role,
        }
    return {
        "id": 1,
        "email": "analyst@sentinelai.local",
        "username": "ciciliya-inace",
        "displayName": "Ciciliya Inace",
        "role": "analyst",
    }


@router.patch("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    if not current_user:
        # In demo fallback mode without login
        return {
            "id": 1,
            "email": payload.email or "analyst@sentinelai.local",
            "username": "ciciliya-inace",
            "displayName": payload.displayName or "Ciciliya Inace",
            "role": "analyst",
        }

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
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "displayName": current_user.display_name,
        "role": current_user.role,
    }
