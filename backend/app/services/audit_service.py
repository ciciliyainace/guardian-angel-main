from typing import Optional, Dict, Any, List, Tuple
from pymongo.database import Database
from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository
from app.utils.time_utils import current_epoch_ms
from app.utils.correlation import generate_correlation_id


class AuditService:
    def __init__(self, db: Database):
        self.db = db
        self.repo = AuditRepository(db)

    def log(
        self,
        actor: str,
        action: str,
        target: str,
        result: str = "Success",
        reason: str = "—",
        related: str = "—",
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        # Sanitize metadata to never record passwords or tokens
        safe_meta = None
        if metadata:
            safe_meta = {
                k: v for k, v in metadata.items()
                if not any(secret in k.lower() for secret in ("password", "token", "secret", "hash", "key"))
            }

        log_id = f"AUD-{current_epoch_ms() % 1000000}"
        log_entry = AuditLog(
            id=log_id,
            timestamp=current_epoch_ms(),
            actor=actor,
            action=action,
            target=target,
            result=result,
            reason=reason or "—",
            related=related or "—",
            correlation_id=correlation_id or generate_correlation_id(),
            extra_metadata=safe_meta,
        )
        return self.repo.create(log_entry)

    def list_logs(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AuditLog], int, int, int]:
        return self.repo.list_logs(actor=actor, action=action, page=page, page_size=page_size)
