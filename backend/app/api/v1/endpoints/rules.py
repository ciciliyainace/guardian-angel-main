from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.models.detection_rule import DetectionRule
from app.repositories.rule_repository import RuleRepository
from app.schemas.rule import RuleResponse, RuleCreate, RuleUpdate
from app.services.audit_service import AuditService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[RuleResponse])
def get_rules(db: Database = Depends(get_db)) -> Any:
    repo = RuleRepository(db)
    return [r.to_dict() for r in repo.list_all()]


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: str, db: Database = Depends(get_db)) -> Any:
    repo = RuleRepository(db)
    rule = repo.get_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule {rule_id} not found")
    return rule.to_dict()


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    payload: RuleCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    repo = RuleRepository(db)
    rule_id = payload.id or f"R-{len(repo.list_all()) + 1:03d}"
    if repo.get_by_id(rule_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Rule {rule_id} already exists")

    rule = DetectionRule(
        id=rule_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        severity=payload.severity,
        enabled=payload.enabled,
        threshold=payload.threshold,
        window_sec=payload.windowSec,
        rule_type=payload.ruleType,
        config=payload.config,
    )
    saved = repo.create(rule)

    actor = current_user.username if current_user else "admin"
    AuditService(db).log(
        actor=actor,
        action="Create rule",
        target=rule_id,
        result="Success",
        reason=f"Created rule {payload.name}",
    )
    return saved.to_dict()


@router.patch("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: str,
    payload: RuleUpdate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    repo = RuleRepository(db)
    rule = repo.get_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule {rule_id} not found")

    if payload.name is not None:
        rule.name = payload.name
    if payload.description is not None:
        rule.description = payload.description
    if payload.category is not None:
        rule.category = payload.category
    if payload.severity is not None:
        rule.severity = payload.severity
    if payload.enabled is not None:
        rule.enabled = payload.enabled
    if payload.threshold is not None:
        rule.threshold = payload.threshold
    if payload.windowSec is not None:
        rule.window_sec = payload.windowSec
    if payload.config is not None:
        rule.config = payload.config

    updated = repo.update(rule)
    actor = current_user.username if current_user else "admin"
    AuditService(db).log(
        actor=actor,
        action="Edit rule",
        target=rule_id,
        result="Success",
        reason=f"Updated rule {rule.name}",
    )
    return updated.to_dict()


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    repo = RuleRepository(db)
    success = repo.delete(rule_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule {rule_id} not found")

    actor = current_user.username if current_user else "admin"
    AuditService(db).log(
        actor=actor,
        action="Delete rule",
        target=rule_id,
        result="Success",
        reason="Rule removed",
    )
    return {"status": "success", "message": f"Rule {rule_id} deleted"}
