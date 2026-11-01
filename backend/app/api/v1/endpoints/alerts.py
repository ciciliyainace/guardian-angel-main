from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AlertResponse, AlertUpdateStatus, AlertSummaryResponse
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500, alias="pageSize"),
    db: Database = Depends(get_db),
) -> Any:
    service = AlertService(db)
    items, _, _, _ = service.list_alerts(
        status=status,
        severity=severity,
        category=category,
        page=page,
        page_size=page_size,
    )
    return [a.to_dict() for a in items]


@router.get("/summary", response_model=AlertSummaryResponse)
def get_alerts_summary(db: Database = Depends(get_db)) -> Any:
    service = AlertService(db)
    return service.get_summary()


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Database = Depends(get_db)) -> Any:
    service = AlertService(db)
    alert = service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found")
    return alert.to_dict()


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: str,
    payload: AlertUpdateStatus,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = AlertService(db)
    actor = current_user.username if current_user else "ciciliya-inace"
    alert = service.update_status(
        alert_id=alert_id,
        new_status=payload.status,
        notes=payload.notes,
        actor=actor,
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found")
    return alert.to_dict()
