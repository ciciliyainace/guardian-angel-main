from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.services.firewall_service import FirewallService
from app.schemas.firewall import (
    BlockRequestResponse,
    BlockRequestCreate,
    FirewallApprovalRequest,
    FirewallRejectionRequest,
    FirewallActionResponse,
)
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/requests", response_model=List[BlockRequestResponse])
def get_block_requests(
    status: Optional[str] = None,
    db: Database = Depends(get_db),
) -> Any:
    service = FirewallService(db)
    items = service.list_requests(status)
    return [r.to_dict() for r in items]


@router.post("/requests", response_model=BlockRequestResponse, status_code=status.HTTP_201_CREATED)
def create_block_request(
    payload: BlockRequestCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = FirewallService(db)
    actor = current_user.username if current_user else "ciciliya-inace"
    req = service.create_block_request(
        source_ip=payload.sourceIp,
        reason=payload.reason,
        alert_id=payload.alertId,
        duration_min=payload.durationMin,
        direction=payload.direction,
        requested_by=actor,
    )
    return req.to_dict()


@router.post("/requests/{request_id}/approve", response_model=Dict[str, Any])
def approve_block_request(
    request_id: str,
    payload: Optional[FirewallApprovalRequest] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = FirewallService(db)
    # Default to administrator if in demo/local mode without auth
    reviewer = current_user.username if current_user else "admin"
    role = current_user.role if current_user else "administrator"

    note = payload.reviewer_note if payload else None
    return service.approve_block_request(
        request_id=request_id,
        reviewer_username=reviewer,
        reviewer_role=role,
        note=note,
    )


@router.post("/requests/{request_id}/reject", response_model=BlockRequestResponse)
def reject_block_request(
    request_id: str,
    payload: Optional[FirewallRejectionRequest] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = FirewallService(db)
    reviewer = current_user.username if current_user else "admin"
    role = current_user.role if current_user else "administrator"
    reason = payload.reason if payload else "False positive"

    req = service.reject_block_request(
        request_id=request_id,
        reviewer_username=reviewer,
        reviewer_role=role,
        reason=reason,
    )
    return req.to_dict()


@router.get("/rules", response_model=List[FirewallActionResponse])
def get_active_firewall_rules(db: Database = Depends(get_db)) -> Any:
    service = FirewallService(db)
    actions = service.repo.list_active_actions()
    return [a.to_dict() for a in actions]


@router.get("/actions", response_model=List[FirewallActionResponse])
def get_firewall_actions(
    status: Optional[str] = None,
    db: Database = Depends(get_db),
) -> Any:
    service = FirewallService(db)
    actions = service.list_actions(status)
    return [a.to_dict() for a in actions]


@router.post("/actions/{action_id}/rollback")
def rollback_firewall_action(
    action_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    service = FirewallService(db)
    actor = current_user.username if current_user else "administrator"
    return service.rollback_action(action_id, actor=actor)
