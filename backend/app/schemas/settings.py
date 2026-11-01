from typing import Any, Optional
from pydantic import Field, EmailStr
from app.schemas.common import BaseSchema


class SettingItem(BaseSchema):
    key: str
    value: Any
    category: str
    description: Optional[str] = None
    updatedAt: Optional[str] = None
    updatedBy: Optional[str] = None


class SettingUpdate(BaseSchema):
    value: Any


class ProfileResponse(BaseSchema):
    id: int
    email: str
    username: str
    displayName: str = Field(..., alias="display_name", serialization_alias="displayName")
    role: str


class ProfileUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    displayName: Optional[str] = Field(None, alias="display_name")
    currentPassword: Optional[str] = Field(None, alias="current_password")
    newPassword: Optional[str] = Field(None, alias="new_password")


class FeedbackCreate(BaseSchema):
    category: str = "general"
    message: str = Field(..., min_length=3, max_length=2000)


class FeedbackResponse(BaseSchema):
    id: int
    category: str
    message: str
    status: str
    createdAt: Optional[str] = None
