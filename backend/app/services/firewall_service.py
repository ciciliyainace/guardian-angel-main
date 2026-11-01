from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from pymongo.database import Database
from app.models.firewall_request import FirewallRequest
from app.models.firewall_action import FirewallAction
from app.repositories.firewall_repository import FirewallRepository
from app.firewall import get_firewall_adapter, target_validator, RollbackManager
from app.services.audit_service import AuditService
from app.core.exceptions import (
    PermissionDeniedError,
    NotFoundError,
    ValidationError,
    ProtectedTargetError,
    FirewallExecutionError,
)
from app.core.logging_config import logger
from app.utils.time_utils import current_epoch_ms


class FirewallService:
    def __init__(self, db: Database):
        self.db = db
        self.repo = FirewallRepository(db)
        self.adapter = get_firewall_adapter()
        self.rollback_mgr = RollbackManager(self.adapter)
        self.audit_service = AuditService(db)

    def list_requests(self, status: Optional[str] = None) -> List[FirewallRequest]:
        return self.repo.list_requests(status)

    def create_block_request(
        self,
        source_ip: str,
        reason: str,
        alert_id: Optional[str] = None,
        duration_min: int = 60,
        direction: str = "Inbound",
        requested_by: str = "analyst",
    ) -> FirewallRequest:
        # 1. Target validation (raises ProtectedTargetError if invalid or protected)
        target_validator.validate_target(source_ip)

        now_ms = current_epoch_ms()
        req_id = f"BLK-{now_ms % 100000}"

        req = FirewallRequest(
            id=req_id,
            source_ip=source_ip,
            reason=reason,
            alert_id=alert_id or "",
            requested_by=requested_by,
            requested_at=now_ms,
            duration_min=duration_min,
            status="pending",
            direction=direction,
        )
        saved = self.repo.create_request(req)

        self.audit_service.log(
            actor=requested_by,
            action="Create block request",
            target=req_id,
            result="Success",
            reason=reason,
            related=alert_id or "—",
        )
        return saved

    def approve_block_request(
        self,
        request_id: str,
        reviewer_username: str,
        reviewer_role: str,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve block request.
        Requires Administrator role.
        An analyst cannot self-approve their own request.
        """
        # Role check
        if reviewer_role.lower() not in ("admin", "administrator"):
            raise PermissionDeniedError(
                "Firewall rule approval strictly requires Administrator privileges."
            )

        req = self.repo.get_request_by_id(request_id)
        if not req:
            raise NotFoundError(f"Block request {request_id} not found.")

        if req.status != "pending":
            raise ValidationError(f"Block request is already {req.status}.")

        # Self-approval prohibition check
        if req.requested_by == reviewer_username and reviewer_username.lower() != "system":
            raise PermissionDeniedError(
                "Policy violation: Users cannot self-approve their own firewall block requests."
            )

        # Re-validate target IP safety
        target_validator.validate_target(req.source_ip)

        now = datetime.now(timezone.utc)
        now_ms = int(now.timestamp() * 1000)
        expires_at = now + timedelta(minutes=req.duration_min)

        managed_rule_name = f"SentinelAI_Block_{req.source_ip.replace(':', '_')}_{req.id}"

        # Execute block via adapter (simulation or Windows Defender)
        try:
            exec_res = self.adapter.block_ip(
                target_ip=req.source_ip,
                rule_name=managed_rule_name,
                direction=req.direction,
                duration_min=req.duration_min,
            )
        except Exception as e:
            logger.error(f"Firewall execution failed during approval of {request_id}: {e}")
            self.audit_service.log(
                actor=reviewer_username,
                action="Approve block",
                target=request_id,
                result="Failed",
                reason=str(e),
                related=req.source_ip,
            )
            raise FirewallExecutionError(f"Firewall block execution failed: {e}")

        # Record action in DB
        action_id = f"ACT-{now_ms % 100000}"
        is_verified = exec_res.get("verification_status") in ("verified", "simulated")
        action = FirewallAction(
            id=action_id,
            managed_rule_name=managed_rule_name,
            request_id=req.id,
            target_ip=req.source_ip,
            direction=req.direction,
            action_type="block",
            status="verified" if is_verified else "created",
            duration_min=req.duration_min,
            created_at=now,
            expires_at=expires_at,
            verification_status=exec_res.get("verification_status", "simulated"),
        )
        self.repo.create_action(action)

        # Update request
        req.status = "approved"
        req.reviewed_by = reviewer_username
        req.reviewed_at = now_ms
        self.repo.update_request(req)

        self.audit_service.log(
            actor=reviewer_username,
            action="Approve block",
            target=req.id,
            result="Success",
            reason=note or "Administrator approved block request",
            related=managed_rule_name,
        )

        return {
            "request": req.to_dict(),
            "action": action.to_dict(),
            "execution": exec_res,
        }

    def reject_block_request(
        self,
        request_id: str,
        reviewer_username: str,
        reviewer_role: str,
        reason: Optional[str] = None,
    ) -> FirewallRequest:
        if reviewer_role.lower() not in ("admin", "administrator"):
            raise PermissionDeniedError("Firewall request rejection requires Administrator privileges.")

        req = self.repo.get_request_by_id(request_id)
        if not req:
            raise NotFoundError(f"Block request {request_id} not found.")

        req.status = "rejected"
        req.reviewed_by = reviewer_username
        req.reviewed_at = current_epoch_ms()
        self.repo.update_request(req)

        self.audit_service.log(
            actor=reviewer_username,
            action="Reject block",
            target=req.id,
            result="Success",
            reason=reason or "False positive or policy exception",
            related=req.source_ip,
        )
        return req

    def rollback_action(self, action_id: str, actor: str = "administrator") -> Dict[str, Any]:
        action = self.repo.get_action_by_id(action_id)
        if not action:
            raise NotFoundError(f"Firewall action {action_id} not found.")

        res = self.rollback_mgr.rollback_rule(action.managed_rule_name)
        if res.get("success"):
            action.status = "rolled_back"
            action.rollback_status = "completed"
            self.repo.update_action(action)

            # Update related request status if expired or rolled back
            if action.request_id:
                req = self.repo.get_request_by_id(action.request_id)
                if req and req.status == "approved":
                    req.status = "expired"
                    self.repo.update_request(req)

            self.audit_service.log(
                actor=actor,
                action="Rollback action",
                target=action.managed_rule_name,
                result="Success",
                reason="Manual rollback executed",
                related=action.id,
            )
        else:
            action.rollback_status = "failed"
            action.failure_details = res.get("error", "Unknown rollback error")
            self.repo.update_action(action)

        return res

    def list_actions(self, status: Optional[str] = None) -> List[FirewallAction]:
        return self.repo.list_actions(status)

    def process_expired_rules(self) -> int:
        """Called periodically by background worker to clean up expired rules."""
        expired_actions = self.repo.list_expired_actions()
        count = 0
        for act in expired_actions:
            try:
                res = self.rollback_mgr.rollback_rule(act.managed_rule_name)
                act.status = "expired"
                act.rollback_status = "completed" if res.get("success") else "failed"
                self.repo.update_action(act)

                if act.request_id:
                    req = self.repo.get_request_by_id(act.request_id)
                    if req and req.status == "approved":
                        req.status = "expired"
                        self.repo.update_request(req)

                self.audit_service.log(
                    actor="system",
                    action="Expire rule",
                    target=act.managed_rule_name,
                    result="Success" if res.get("success") else "Failed",
                    reason="Duration expired",
                    related=act.id,
                )
                count += 1
            except Exception as e:
                logger.error(f"Error expiring rule {act.managed_rule_name}: {e}")
        return count
