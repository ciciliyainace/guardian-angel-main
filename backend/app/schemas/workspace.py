from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.common import BaseSchema


class WorkspaceMember(BaseSchema):
    user_id: int
    role: str = "analyst"
    added_at: Optional[str] = None


class WorkspaceResponse(BaseSchema):
    id: str
    name: str
    owner_user_id: int = Field(..., alias="ownerUserId")
    description: Optional[str] = ""
    is_active: bool = Field(True, alias="isActive")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    member_count: int = Field(1, alias="memberCount")
    settings: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceCreateRequest(BaseSchema):
    name: str = Field(..., min_length=2, max_length=64)
    description: Optional[str] = Field("", max_length=256)


class WorkspaceUpdateRequest(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=64)
    description: Optional[str] = Field(None, max_length=256)
    settings: Optional[Dict[str, Any]] = None
