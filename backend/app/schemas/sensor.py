from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HostSystemInfo(BaseModel):
    machine_name: Optional[str] = None
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    adapter_name: Optional[str] = None
    adapter_mac: Optional[str] = None
    suricata_version: Optional[str] = None
    npcap_version: Optional[str] = None
    agent_version: Optional[str] = "1.0.0"


class SensorEnrollRequest(BaseModel):
    # Web dashboard fields
    sensor_id: Optional[str] = Field(None, min_length=2, max_length=128)
    name: Optional[str] = Field(None, min_length=2, max_length=128)
    hostname: Optional[str] = None
    collector_types: Optional[List[str]] = Field(default_factory=lambda: ["windows_sockets", "suricata"])

    # Windows desktop setup fields
    sensor_name: Optional[str] = None
    sensor_description: Optional[str] = None
    enrollment_credential: Optional[str] = None
    host_info: Optional[Dict[str, Any]] = None


class SensorEnrollResponse(BaseModel):
    success: bool = True
    sensor_id: str
    name: Optional[str] = None
    api_key: Optional[str] = None
    enrollment_credential: Optional[str] = None
    sensor_token: Optional[str] = None
    workspace_id: str
    workspace_name: str
    status: str
    message: str
    expires_at: Optional[str] = None


class SensorKeyGenerationRequest(BaseModel):
    sensor_id: str = Field(..., min_length=2, max_length=128)
    name: Optional[str] = Field(None, max_length=128)
    collector_types: List[str] = Field(default_factory=lambda: ["windows_sockets", "suricata"])
    hostname: Optional[str] = None


class SensorRevokeResponse(BaseModel):
    sensor_id: str
    status: str
    message: str


class SensorHeartbeatRequest(BaseModel):
    sensor_id: Optional[str] = None
    timestamp: Optional[Any] = None
    status: Optional[str] = "online"
    suricata_running: Optional[bool] = None
    npcap_running: Optional[bool] = None
    uptime_seconds: Optional[int] = 0
    queued_events: Optional[int] = 0
    transmitted_events: Optional[int] = 0
    dropped_events: Optional[int] = 0
    agent_version: Optional[str] = "1.0.0"
    selected_interface: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    collectors: Dict[str, str] = Field(default_factory=dict)
    last_event_time: Optional[int] = None


class SensorHeartbeatResponse(BaseModel):
    success: bool = True
    acknowledged: bool = True
    timestamp: int
    server_time: Optional[str] = None
    command: Optional[str] = "none"
    server_status: str = "ready"
    message: Optional[str] = "Heartbeat acknowledged"


class TelemetryBatchIngestRequest(BaseModel):
    sensor_id: Optional[str] = None
    batch_id: Optional[str] = None
    sequence_number: Optional[int] = None
    timestamp: Optional[str] = None
    event_count: Optional[int] = None
    checksum: Optional[str] = None
    events: List[Dict[str, Any]] = Field(default_factory=list, max_length=2000)


class TelemetryBatchIngestResponse(BaseModel):
    success: bool = True
    status: str = "success"
    batch_id: Optional[str] = None
    processed_count: int = 0
    rejected_count: int = 0
    received: int = 0
    ingested: int = 0
    duplicates: int = 0
    alerts_generated: int = 0
    server_timestamp: Optional[str] = None
    message: Optional[str] = "Batch processed successfully"


class SensorListItem(BaseModel):
    sensor_id: str
    name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    collector_types: List[str]
    status: str
    connectivity_status: str
    enrolled_by: str
    workspace_id: Optional[str] = None
    created_at: Optional[str] = None
    enrolled_at: Optional[str] = None
    last_heartbeat_at: Optional[str] = None
    last_telemetry_at: Optional[str] = None
    total_events_ingested: int
    is_alive: bool
    collector_details: Dict[str, Any] = Field(default_factory=dict)
