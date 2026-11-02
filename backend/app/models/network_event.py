from datetime import datetime, timezone
from typing import Optional, Dict, Any


class NetworkEvent:
    def __init__(
        self,
        id: str = "",
        timestamp: int = 0,
        source_ip: str = "",
        dest_ip: str = "",
        src_port: Optional[int] = None,
        dst_port: Optional[int] = None,
        protocol: str = "TCP",
        category: str = "Anomalous traffic",
        source: str = "Rule engine",
        severity: str = "low",
        risk_score: int = 0,
        status: str = "new",
        duplicates: int = 0,
        event_source: str = "json_file",
        flow_features: Optional[Dict[str, Any]] = None,
        collector_metadata: Optional[Dict[str, Any]] = None,
        ingestion_status: str = "processed",
        is_simulated: bool = False,
        sensor_id: Optional[str] = None,
        data_origin: Optional[str] = None,
        created_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.timestamp = timestamp
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.category = category
        self.source = source
        self.severity = severity
        self.risk_score = risk_score
        self.status = status
        self.duplicates = duplicates
        self.event_source = event_source
        self.flow_features = flow_features or {}
        self.collector_metadata = collector_metadata or {}
        self.ingestion_status = ingestion_status
        self.sensor_id = sensor_id
        
        sim = is_simulated or ("SIM-" in str(id)) or (data_origin == "simulated")
        self.is_simulated = sim
        self.data_origin = data_origin if data_origin in ("live", "simulated") else ("simulated" if sim else "live")
        self.created_at = created_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "category": self.category,
            "source": self.source,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "status": self.status,
            "duplicates": self.duplicates,
            "event_source": self.event_source,
            "flow_features": self.flow_features,
            "collector_metadata": self.collector_metadata,
            "ingestion_status": self.ingestion_status,
            "is_simulated": self.is_simulated,
            "data_origin": self.data_origin,
            "sensor_id": self.sensor_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["NetworkEvent"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            timestamp=doc.get("timestamp", 0),
            source_ip=doc.get("source_ip", ""),
            dest_ip=doc.get("dest_ip", ""),
            src_port=doc.get("src_port"),
            dst_port=doc.get("dst_port"),
            protocol=doc.get("protocol", "TCP"),
            category=doc.get("category", "Anomalous traffic"),
            source=doc.get("source", "Rule engine"),
            severity=doc.get("severity", "low"),
            risk_score=doc.get("risk_score", 0),
            status=doc.get("status", "new"),
            duplicates=doc.get("duplicates", 0),
            event_source=doc.get("event_source", "json_file"),
            flow_features=doc.get("flow_features"),
            collector_metadata=doc.get("collector_metadata"),
            ingestion_status=doc.get("ingestion_status", "processed"),
            is_simulated=doc.get("is_simulated", False),
            data_origin=doc.get("data_origin"),
            sensor_id=doc.get("sensor_id"),
            created_at=doc.get("created_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "sourceIp": self.source_ip,
            "destIp": self.dest_ip,
            "srcPort": self.src_port or 0,
            "dstPort": self.dst_port or 0,
            "protocol": self.protocol,
            "category": self.category,
            "source": self.source,
            "severity": self.severity,
            "riskScore": self.risk_score,
            "status": self.status,
            "duplicates": self.duplicates,
            "isSimulated": self.is_simulated,
            "dataOrigin": self.data_origin,
            "sensorId": self.sensor_id,
            "eventSource": self.event_source,
        }
