from typing import Optional, Dict, Any, Literal
from pydantic import Field
from app.schemas.common import BaseSchema

SeverityType = Literal["critical", "high", "medium", "low"]
AlertStatusType = Literal["new", "acknowledged", "investigating", "resolved"]
ProtocolType = Literal["TCP", "UDP", "ICMP", "Other"]


class EventResponse(BaseSchema):
    id: str
    timestamp: int
    sourceIp: str = Field(..., alias="source_ip", serialization_alias="sourceIp")
    destIp: str = Field(..., alias="dest_ip", serialization_alias="destIp")
    protocol: str
    category: str
    source: str
    severity: SeverityType
    riskScore: int = Field(..., alias="risk_score", serialization_alias="riskScore")
    status: AlertStatusType
    srcPort: int = Field(0, alias="src_port", serialization_alias="srcPort")
    dstPort: int = Field(0, alias="dst_port", serialization_alias="dstPort")
    duplicates: int = 0
    isSimulated: bool = Field(False, alias="is_simulated", serialization_alias="isSimulated")
    eventSource: Optional[str] = Field("collector", alias="event_source", serialization_alias="eventSource")


class EventCreate(BaseSchema):
    sourceIp: str = Field(..., alias="source_ip")
    destIp: str = Field(..., alias="dest_ip")
    protocol: str = "TCP"
    srcPort: Optional[int] = Field(None, alias="src_port")
    dstPort: Optional[int] = Field(None, alias="dst_port")
    category: Optional[str] = "Anomalous traffic"
    source: Optional[str] = "Live ingestion"
    severity: Optional[SeverityType] = "low"
    riskScore: Optional[int] = Field(0, alias="risk_score")
    duplicates: Optional[int] = 0
    flowFeatures: Optional[Dict[str, Any]] = Field(None, alias="flow_features")
    metadata: Optional[Dict[str, Any]] = None


class EventFilterParams(BaseSchema):
    query: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    range_hours: Optional[int] = None
    page: int = 1
    page_size: int = 50
    sort_by: str = "timestamp"
    sort_dir: str = "desc"
