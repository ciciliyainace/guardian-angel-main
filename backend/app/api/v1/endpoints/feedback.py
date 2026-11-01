from typing import Any
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.database import get_db
from app.services.settings_service import SettingsService
from app.schemas.settings import FeedbackCreate, FeedbackResponse
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = SettingsService(db)
    user_id = current_user.id if current_user else None
    email = current_user.email if current_user else "anonymous@sentinelai.local"

    fb = service.submit_feedback(
        category=payload.category,
        message=payload.message,
        user_id=user_id,
        user_email=email,
    )
    return fb.to_dict()
