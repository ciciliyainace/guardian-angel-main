from typing import Optional, List, Tuple, Dict, Any
from pymongo.database import Database
from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository
from app.repositories.event_repository import EventRepository
from app.services.audit_service import AuditService


class AlertService:
    def __init__(self, db: Database):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.event_repo = EventRepository(db)
        self.audit_service = AuditService(db)

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        return self.alert_repo.get_by_id(alert_id)

    def list_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Alert], int, int, int]:
        return self.alert_repo.filter_alerts(
            status=status,
            severity=severity,
            category=category,
            page=page,
            page_size=page_size,
        )

    def update_status(
        self,
        alert_id: str,
        new_status: str,
        notes: Optional[str] = None,
        actor: str = "analyst",
    ) -> Optional[Alert]:
        alert = self.alert_repo.update_status(alert_id, new_status, notes)
        if alert:
            # Also keep related event status synchronized
            if alert.related_event_id:
                self.event_repo.update_status(alert.related_event_id, new_status)

            self.audit_service.log(
                actor=actor,
                action=f"{new_status.capitalize()} alert",
                target=alert_id,
                result="Success",
                reason=notes or f"Status changed to {new_status}",
                related=alert.related_event_id or "—",
            )
        return alert

    def get_summary(self) -> Dict[str, int]:
        return self.alert_repo.count_by_status()
