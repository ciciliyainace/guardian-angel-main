from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SensorEnrollRequest(BaseModel):
    sensor_id: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")
    name: str = Field(..., min_length=2, max_length=128)
    hostname: Optional[str] = None
    collector_types: List[str] = Field(default_factory=lambda: ["windows_sockets"])


class SensorEnrollResponse(BaseModel):
    sensor_id: str
    name: str
    api_key: str
    status: str
    message: str


class SensorRevokeResponse(BaseModel):
    sensor_id: str
    status: str
    message: str


class SensorHeartbeatRequest(BaseModel):
    metrics: Dict[str, Any] = Field(default_factory=dict)
    collectors: Dict[str, str] = Field(default_factory=dict)
    last_event_time: Optional[int] = None


class SensorHeartbeatResponse(BaseModel):
    acknowledged: bool
    timestamp: int
    server_status: str


class TelemetryBatchIngestRequest(BaseModel):
    events: List[Dict[str, Any]] = Field(..., max_length=1000)
    batch_id: Optional[str] = None
    sequence: Optional[int] = None


class TelemetryBatchIngestResponse(BaseModel):
    status: str
    received: int
    ingested: int
    duplicates: int
    alerts_generated: int


class SensorListItem(BaseModel):
    sensor_id: str
    name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    collector_types: List[str]
    status: str
    enrolled_by: str
    created_at: Optional[str] = None
    last_heartbeat_at: Optional[str] = None
    last_telemetry_at: Optional[str] = None
    total_events_ingested: int
    is_alive: bool
    collector_details: Dict[str, Any] = Field(default_factory=dict)
