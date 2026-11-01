from typing import Any, List
from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.core.database import get_db
from app.services.settings_service import SettingsService
from app.schemas.settings import SettingItem, SettingUpdate
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[SettingItem])
def get_settings(db: Database = Depends(get_db)) -> Any:
    service = SettingsService(db)
    items = service.list_settings()
    return [s.to_dict() for s in items]


@router.patch("/{key}", response_model=SettingItem)
def update_setting(
    key: str,
    payload: SettingUpdate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = SettingsService(db)
    actor = current_user.username if current_user else "admin"
    updated = service.update_setting(key, payload.value, actor=actor)
    return updated.to_dict()
