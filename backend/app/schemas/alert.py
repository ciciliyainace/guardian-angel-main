from typing import Optional, List, Dict, Any
from pydantic import Field
from app.schemas.common import BaseSchema
from app.schemas.event import SeverityType, AlertStatusType


class AlertResponse(BaseSchema):
    id: str
    relatedEventId: Optional[str] = Field(None, alias="related_event_id", serialization_alias="relatedEventId")
    timestamp: int
    category: str
    severity: SeverityType
    riskScore: int = Field(..., alias="risk_score", serialization_alias="riskScore")
    status: AlertStatusType
    detectionSources: List[str] = Field(default_factory=list, alias="detection_sources", serialization_alias="detectionSources")
    evidence: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = ""
    modelVersions: Dict[str, str] = Field(default_factory=dict, alias="model_versions", serialization_alias="modelVersions")
    ruleIds: List[str] = Field(default_factory=list, alias="rule_ids", serialization_alias="ruleIds")


class AlertUpdateStatus(BaseSchema):
    status: AlertStatusType
    notes: Optional[str] = None


class AlertSummaryResponse(BaseSchema):
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    high_alerts: int
    resolved_alerts: int
