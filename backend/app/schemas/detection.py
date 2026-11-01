from typing import Dict, Any, List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema
from app.schemas.event import SeverityType


class AnalyzeRequest(BaseSchema):
    sourceIp: str = Field(..., alias="source_ip")
    destIp: str = Field(..., alias="dest_ip")
    srcPort: Optional[int] = Field(None, alias="src_port")
    dstPort: Optional[int] = Field(None, alias="dst_port")
    protocol: str = "TCP"
    flowFeatures: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="flow_features")
    signatureName: Optional[str] = Field(None, alias="signature_name")


class AnalyzeResponse(BaseSchema):
    eventId: str = Field(..., alias="event_id", serialization_alias="eventId")
    detectionSources: List[str] = Field(..., alias="detection_sources", serialization_alias="detectionSources")
    predictedCategory: str = Field(..., alias="predicted_category", serialization_alias="predictedCategory")
    severity: SeverityType
    riskScore: int = Field(..., alias="risk_score", serialization_alias="riskScore")
    confidence: Optional[float] = 1.0
    reason: Optional[str] = None
    evidence: Dict[str, Any]
    modelVersions: Dict[str, str] = Field(..., alias="model_versions", serialization_alias="modelVersions")
    ruleIds: List[str] = Field(default_factory=list, alias="rule_ids", serialization_alias="ruleIds")
    recommendedAction: str = Field(..., alias="recommended_action", serialization_alias="recommendedAction")
    timestamp: int


class DetectionStatusResponse(BaseSchema):
    ruleEngineStatus: str = Field(..., alias="rule_engine_status", serialization_alias="ruleEngineStatus")
    rfStatus: str = Field(..., alias="rf_status", serialization_alias="rfStatus")
    ifStatus: str = Field(..., alias="if_status", serialization_alias="ifStatus")
    hybridStatus: str = Field(..., alias="hybrid_status", serialization_alias="hybridStatus")
    activeRulesCount: int = Field(..., alias="active_rules_count", serialization_alias="activeRulesCount")
    loadedModelsCount: int = Field(..., alias="loaded_models_count", serialization_alias="loadedModelsCount")
