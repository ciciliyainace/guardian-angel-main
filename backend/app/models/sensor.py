from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class Sensor:
    """
    Model representing an authorized telemetry sensor (e.g. Windows host sensor).
    Sensors authenticate via an API key whose SHA-256 hash is verified against api_key_hash.
    """
    def __init__(
        self,
        sensor_id: str,
        name: str,
        api_key_hash: str,
        hostname: Optional[str] = None,
        ip_address: Optional[str] = None,
        collector_types: Optional[List[str]] = None,
        status: str = "active",
        enrolled_by: str = "admin",
        created_at: Optional[datetime] = None,
        revoked_at: Optional[datetime] = None,
        revoked_by: Optional[str] = None,
        last_heartbeat_at: Optional[datetime] = None,
        last_telemetry_at: Optional[datetime] = None,
        total_events_ingested: int = 0,
        collector_details: Optional[Dict[str, Any]] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.sensor_id = sensor_id
        self.name = name
        self.api_key_hash = api_key_hash
        self.hostname = hostname or ""
        self.ip_address = ip_address or ""
        self.collector_types = collector_types or ["windows_sockets"]
        self.status = status
        self.enrolled_by = enrolled_by
        self.created_at = created_at or datetime.now(timezone.utc)
        self.revoked_at = revoked_at
        self.revoked_by = revoked_by
        self.last_heartbeat_at = last_heartbeat_at
        self.last_telemetry_at = last_telemetry_at
        self.total_events_ingested = total_events_ingested
        self.collector_details = collector_details or {}
        self._id = _id

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
            "created_at": self.created_at,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
            "last_heartbeat_at": self.last_heartbeat_at,
            "last_telemetry_at": self.last_telemetry_at,
            "total_events_ingested": self.total_events_ingested,
            "collector_details": self.collector_details,
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
            collector_types=doc.get("collector_types") or [],
            status=doc.get("status", "active"),
            enrolled_by=doc.get("enrolled_by", "admin"),
            created_at=doc.get("created_at"),
            revoked_at=doc.get("revoked_at"),
            revoked_by=doc.get("revoked_by"),
            last_heartbeat_at=doc.get("last_heartbeat_at"),
            last_telemetry_at=doc.get("last_telemetry_at"),
            total_events_ingested=doc.get("total_events_ingested", 0),
            collector_details=doc.get("collector_details") or {},
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
            "enrolledBy": self.enrolled_by,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "lastHeartbeatAt": self.last_heartbeat_at.isoformat() if self.last_heartbeat_at else None,
            "lastTelemetryAt": self.last_telemetry_at.isoformat() if self.last_telemetry_at else None,
            "totalEventsIngested": self.total_events_ingested,
            "collectorDetails": self.collector_details,
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
        self.created_at = created_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "collectors": self.collectors,
            "ip_address": self.ip_address,
            "created_at": self.created_at,
        }
