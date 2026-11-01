from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from pymongo.database import Database
from app.core.database import get_db
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("", response_model=List[dict])
def get_audit_logs(
    actor: Optional[str] = None,
    action: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500, alias="pageSize"),
    db: Database = Depends(get_db),
) -> Any:
    service = AuditService(db)
    items, _, _, _ = service.list_logs(actor=actor, action=action, page=page, page_size=page_size)
    return [l.to_dict() for l in items]
