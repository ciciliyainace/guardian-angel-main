from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class Sensor:
    """
    Model representing an authorized telemetry sensor (e.g. Windows host sensor).
    Sensors authenticate via a one-time enrollment credential which is consumed
    during initial desktop setup to negotiate a long-lived sensor API token.
    Both token hashes are SHA-256 protected at rest.
    """
    def __init__(
        self,
        sensor_id: str,
        name: str,
        api_key_hash: str,
        hostname: Optional[str] = None,
        ip_address: Optional[str] = None,
        collector_types: Optional[List[str]] = None,
        status: str = "pending_enrollment",
        enrolled_by: str = "admin",
        workspace_id: Optional[str] = None,
        owner_user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        enrolled_at: Optional[datetime] = None,
        revoked_at: Optional[datetime] = None,
        revoked_by: Optional[str] = None,
        last_heartbeat_at: Optional[datetime] = None,
        last_telemetry_at: Optional[datetime] = None,
        total_events_ingested: int = 0,
        collector_details: Optional[Dict[str, Any]] = None,
        enrollment_credential_hash: Optional[str] = None,
        enrollment_credential_expires_at: Optional[datetime] = None,
        enrollment_credential_consumed: bool = False,
        enrollment_credential_consumed_at: Optional[datetime] = None,
        sensor_token_hash: Optional[str] = None,
        suricata_running: Optional[bool] = None,
        npcap_running: Optional[bool] = None,
        agent_version: Optional[str] = None,
        uptime_seconds: Optional[int] = 0,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.sensor_id = sensor_id
        self.name = name
        self.api_key_hash = api_key_hash
        self.hostname = hostname or ""
        self.ip_address = ip_address or ""
        self.collector_types = collector_types or ["windows_sockets", "suricata"]
        self.status = status
        self.enrolled_by = enrolled_by
        self.workspace_id = workspace_id
        self.owner_user_id = owner_user_id
        self.created_at = created_at or datetime.now(timezone.utc)
        self.enrolled_at = enrolled_at
        self.revoked_at = revoked_at
        self.revoked_by = revoked_by
        self.last_heartbeat_at = last_heartbeat_at
        self.last_telemetry_at = last_telemetry_at
        self.total_events_ingested = total_events_ingested
        self.collector_details = collector_details or {}
        self.enrollment_credential_hash = enrollment_credential_hash or api_key_hash
        self.enrollment_credential_expires_at = enrollment_credential_expires_at
        self.enrollment_credential_consumed = enrollment_credential_consumed
        self.enrollment_credential_consumed_at = enrollment_credential_consumed_at
        self.sensor_token_hash = sensor_token_hash
        self.suricata_running = suricata_running
        self.npcap_running = npcap_running
        self.agent_version = agent_version
        self.uptime_seconds = uptime_seconds or 0
        self._id = _id

    def get_connectivity_status(self, now: Optional[datetime] = None) -> str:
        """
        Derive distinct operational connectivity status:
        - 'revoked': Permanently deactivated.
        - 'pending_enrollment': Web credential generated; awaiting Windows desktop setup.
        - 'awaiting_first_heartbeat': Windows desktop setup completed; awaiting first background beacon.
        - 'online': Authenticated heartbeat received within last 90 seconds.
        - 'offline': Agent previously registered but no heartbeat in >90 seconds.
        """
        if self.status == "revoked":
            return "revoked"

        if not self.last_heartbeat_at:
            if not self.enrollment_credential_consumed and self.status == "pending_enrollment":
                return "pending_enrollment"
            return "awaiting_first_heartbeat"

        current_time = now or datetime.now(timezone.utc)
        hb_time = self.last_heartbeat_at
        if getattr(hb_time, "tzinfo", None) is None:
            hb_time = hb_time.replace(tzinfo=timezone.utc)

        delta = (current_time - hb_time).total_seconds()
        return "online" if delta <= 90 else "offline"

    def to_doc(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "name": self.name,
            "api_key_hash": self.api_key_hash,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "collector_types": self.collector_types,
            "status": self.status,
            "enrolled_by": self.enrolled_by,
            "workspace_id": self.workspace_id,
            "owner_user_id": self.owner_user_id,
            "created_at": self.created_at,
            "enrolled_at": self.enrolled_at,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
            "last_heartbeat_at": self.last_heartbeat_at,
            "last_telemetry_at": self.last_telemetry_at,
            "total_events_ingested": self.total_events_ingested,
            "collector_details": self.collector_details,
            "enrollment_credential_hash": self.enrollment_credential_hash,
            "enrollment_credential_expires_at": self.enrollment_credential_expires_at,
            "enrollment_credential_consumed": self.enrollment_credential_consumed,
            "enrollment_credential_consumed_at": self.enrollment_credential_consumed_at,
            "sensor_token_hash": self.sensor_token_hash,
            "suricata_running": self.suricata_running,
            "npcap_running": self.npcap_running,
            "agent_version": self.agent_version,
            "uptime_seconds": self.uptime_seconds,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["Sensor"]:
        if not doc:
            return None
        return cls(
            sensor_id=doc.get("sensor_id", ""),
            name=doc.get("name", ""),
            api_key_hash=doc.get("api_key_hash", ""),
            hostname=doc.get("hostname"),
            ip_address=doc.get("ip_address"),
            collector_types=doc.get("collector_types") or ["windows_sockets", "suricata"],
            status=doc.get("status", "pending_enrollment"),
            enrolled_by=doc.get("enrolled_by", "admin"),
            workspace_id=doc.get("workspace_id"),
            owner_user_id=doc.get("owner_user_id"),
            created_at=doc.get("created_at"),
            enrolled_at=doc.get("enrolled_at"),
            revoked_at=doc.get("revoked_at"),
            revoked_by=doc.get("revoked_by"),
            last_heartbeat_at=doc.get("last_heartbeat_at"),
            last_telemetry_at=doc.get("last_telemetry_at"),
            total_events_ingested=doc.get("total_events_ingested", 0),
            collector_details=doc.get("collector_details") or {},
            enrollment_credential_hash=doc.get("enrollment_credential_hash") or doc.get("api_key_hash"),
            enrollment_credential_expires_at=doc.get("enrollment_credential_expires_at"),
            enrollment_credential_consumed=doc.get("enrollment_credential_consumed", False),
            enrollment_credential_consumed_at=doc.get("enrollment_credential_consumed_at"),
            sensor_token_hash=doc.get("sensor_token_hash"),
            suricata_running=doc.get("suricata_running"),
            npcap_running=doc.get("npcap_running"),
            agent_version=doc.get("agent_version"),
            uptime_seconds=doc.get("uptime_seconds", 0),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensorId": self.sensor_id,
            "name": self.name,
            "hostname": self.hostname,
            "ipAddress": self.ip_address,
            "collectorTypes": self.collector_types,
            "status": self.status,
            "connectivityStatus": self.get_connectivity_status(),
            "enrolledBy": self.enrolled_by,
            "workspaceId": self.workspace_id,
            "ownerUserId": self.owner_user_id,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "enrolledAt": self.enrolled_at.isoformat() if self.enrolled_at else None,
            "lastHeartbeatAt": self.last_heartbeat_at.isoformat() if self.last_heartbeat_at else None,
            "lastTelemetryAt": self.last_telemetry_at.isoformat() if self.last_telemetry_at else None,
            "totalEventsIngested": self.total_events_ingested,
            "collectorDetails": self.collector_details,
            "suricataRunning": self.suricata_running,
            "npcapRunning": self.npcap_running,
            "agentVersion": self.agent_version,
            "uptimeSeconds": self.uptime_seconds,
        }


class SensorHeartbeat:
    """Telemetry heartbeat record from an active sensor agent."""
    def __init__(
        self,
        sensor_id: str,
        timestamp: Optional[Any] = None,
        metrics: Optional[Dict[str, Any]] = None,
        collectors: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None,
        suricata_running: Optional[bool] = None,
        npcap_running: Optional[bool] = None,
        uptime_seconds: Optional[int] = None,
        agent_version: Optional[str] = None,
        created_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
    ):
        self.sensor_id = sensor_id
        if isinstance(timestamp, (int, float)):
            self.timestamp = int(timestamp)
        elif isinstance(timestamp, datetime):
            self.timestamp = int(timestamp.timestamp() * 1000)
        else:
            self.timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        self.metrics = metrics or {}
        self.collectors = collectors or {}
        self.ip_address = ip_address or ""
        self.suricata_running = suricata_running
        self.npcap_running = npcap_running
        self.uptime_seconds = uptime_seconds or 0
        self.agent_version = agent_version
        self.created_at = created_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "collectors": self.collectors,
            "ip_address": self.ip_address,
            "suricata_running": self.suricata_running,
            "npcap_running": self.npcap_running,
            "uptime_seconds": self.uptime_seconds,
            "agent_version": self.agent_version,
            "created_at": self.created_at,
        }
