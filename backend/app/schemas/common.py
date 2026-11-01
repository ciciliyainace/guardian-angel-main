from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class StatusResponse(BaseSchema):
    status: str = "success"
    message: str
    detail: Optional[Any] = None


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
