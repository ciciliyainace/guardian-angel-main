import secrets
import hashlib
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pymongo.database import Database

from app.core.database import get_db
from app.api.dependencies import require_admin, require_authenticated_user
from app.models.user import User
from app.models.sensor import Sensor, SensorHeartbeat
from app.repositories.user_repository import UserRepository
from app.repositories.sensor_repository import SensorRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.event_service import EventService
from app.detection.flow_aggregator import FlowAggregator
from app.schemas.sensor import (
    SensorEnrollRequest,
    SensorEnrollResponse,
    SensorRevokeResponse,
    SensorHeartbeatRequest,
    SensorHeartbeatResponse,
    TelemetryBatchIngestRequest,
    TelemetryBatchIngestResponse,
    SensorListItem,
)

router = APIRouter()


def authenticate_sensor(
    x_sensor_key: Optional[str] = Header(None, alias="X-Sensor-Key"),
    db: Database = Depends(get_db),
) -> Sensor:
    """Validate sensor API token via SHA-256 constant-time hash comparison."""
    if not x_sensor_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Sensor-Key header.",
        )
    key_hash = hashlib.sha256(x_sensor_key.encode("utf-8")).hexdigest()
    sensor_repo = SensorRepository(db)
    sensor = sensor_repo.get_by_key_hash(key_hash)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked sensor API key.",
        )
    return sensor


@router.post("/enroll", response_model=SensorEnrollResponse, status_code=status.HTTP_201_CREATED)
def enroll_sensor(
    req: SensorEnrollRequest,
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
):
    """
    Enrolls a new genuine network sensor into the caller's verified workspace.
    Generates a secure API key returned once to the caller.
    """
    sensor_repo = SensorRepository(db)
    ws_repo = WorkspaceRepository(db)
    user_repo = UserRepository(db)

    ws = None
    if current_user.default_workspace_id:
        ws = ws_repo.get_by_id(current_user.default_workspace_id)
    if not ws:
        ws = ws_repo.get_or_create_default_workspace(current_user.id, current_user.username)
        current_user.default_workspace_id = ws.id
        user_repo.update(current_user)

    existing = sensor_repo.get_by_id(req.sensor_id)
    if existing and existing.status == "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Active sensor with ID '{req.sensor_id}' already exists.",
        )

    raw_token = f"sen_live_{secrets.token_hex(24)}"
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    sensor = Sensor(
        sensor_id=req.sensor_id,
        name=req.name,
        api_key_hash=token_hash,
        hostname=req.hostname,
        collector_types=req.collector_types,
        status="active",
        workspace_id=ws.id,
        owner_user_id=current_user.id,
        enrolled_by=current_user.username,
        created_at=datetime.now(timezone.utc),
    )
    sensor_repo.enroll(sensor)

    return SensorEnrollResponse(
        sensor_id=sensor.sensor_id,
        name=sensor.name,
        api_key=raw_token,
        status="active",
        message="Sensor enrolled successfully. Store this API key securely; it will not be displayed again.",
    )


@router.get("", response_model=List[SensorListItem])
def list_sensors(
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
):
    """Lists enrolled sensors scoped to the caller's workspace (or all for admin)."""
    sensor_repo = SensorRepository(db)
    sensors = sensor_repo.list_sensors()
    now = datetime.now(timezone.utc)

    # Multi-tenant workspace filtering
    is_admin = current_user.role.lower() in ("admin", "administrator")
    user_ws = current_user.default_workspace_id

    items: List[SensorListItem] = []
    for s in sensors:
        # If not admin, restrict to caller's workspace or enrollment
        if not is_admin:
            if s.workspace_id and s.workspace_id != user_ws and s.owner_user_id != current_user.id:
                continue

        is_alive = False
        if s.last_heartbeat_at:
            delta = (now - s.last_heartbeat_at.replace(tzinfo=timezone.utc)).total_seconds()
            is_alive = delta <= 60 and s.status == "active"

        items.append(
            SensorListItem(
                sensor_id=s.sensor_id,
                name=s.name,
                hostname=s.hostname,
                ip_address=s.ip_address,
                collector_types=s.collector_types,
                status=s.status,
                enrolled_by=s.enrolled_by,
                created_at=s.created_at.isoformat() if s.created_at else None,
                last_heartbeat_at=s.last_heartbeat_at.isoformat() if s.last_heartbeat_at else None,
                last_telemetry_at=s.last_telemetry_at.isoformat() if s.last_telemetry_at else None,
                total_events_ingested=s.total_events_ingested,
                is_alive=is_alive,
                collector_details=s.collector_details or {},
            )
        )
    return items


@router.post("/{sensor_id}/revoke", response_model=SensorRevokeResponse)
def revoke_sensor(
    sensor_id: str,
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
):
    """Revokes an enrolled sensor immediately. Authorized for sensor owner or administrator."""
    sensor_repo = SensorRepository(db)
    sensor = sensor_repo.get_by_id(sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor '{sensor_id}' not found.",
        )

    is_admin = current_user.role.lower() in ("admin", "administrator")
    is_owner = (sensor.owner_user_id == current_user.id) or (sensor.enrolled_by == current_user.username)
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to revoke sensors in another workspace.",
        )

    sensor_repo.revoke(sensor_id, revoked_by=current_user.username)
    return SensorRevokeResponse(
        sensor_id=sensor_id,
        status="revoked",
        message=f"Sensor '{sensor_id}' has been permanently revoked.",
    )


@router.post("/heartbeat", response_model=SensorHeartbeatResponse)
def sensor_heartbeat(
    req: SensorHeartbeatRequest,
    request: Request,
    sensor: Sensor = Depends(authenticate_sensor),
    db: Database = Depends(get_db),
):
    """Record periodic heartbeat and collector health status from an active sensor."""
    sensor_repo = SensorRepository(db)
    client_ip = request.client.host if request.client else None

    heartbeat = SensorHeartbeat(
        sensor_id=sensor.sensor_id,
        timestamp=datetime.now(timezone.utc),
        ip_address=client_ip,
        metrics=req.metrics,
        collectors=req.collectors,
    )
    sensor_repo.record_heartbeat(sensor.sensor_id, heartbeat, remote_ip=client_ip)

    return SensorHeartbeatResponse(
        acknowledged=True,
        timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
        server_status="ready",
    )


@router.post("/telemetry", response_model=TelemetryBatchIngestResponse)
def ingest_telemetry_batch(
    req: TelemetryBatchIngestRequest,
    sensor: Sensor = Depends(authenticate_sensor),
    db: Database = Depends(get_db),
):
    """
    Ingest a batch of genuine network telemetry events from an enrolled sensor.
    Dispatches to flow aggregator, normalizer, and hybrid detection pipeline.
    """
    event_service = EventService(db)
    sensor_repo = SensorRepository(db)

    received = len(req.events)
    ingested = 0
    duplicates = 0
    alerts_generated = 0

    for raw_event in req.events:
        try:
            # Check event format
            collector = raw_event.get("collector") or ("suricata" if "event_type" in raw_event else "windows_sockets")
            if collector == "suricata" or "event_type" in raw_event:
                normalized = FlowAggregator.parse_suricata_eve(raw_event, sensor_id=sensor.sensor_id)
            else:
                normalized = FlowAggregator.parse_windows_socket(raw_event, sensor_id=sensor.sensor_id)

            # Strictly bind to sensor's verified workspace and owner in DB, never trusting client payload
            normalized["workspace_id"] = sensor.workspace_id
            normalized["owner_user_id"] = sensor.owner_user_id

            prev_alert_count = db.alerts.count_documents({})
            saved = event_service.ingest_event(normalized, run_detection=True)

            if saved.duplicates > 0:
                duplicates += 1
            else:
                ingested += 1

            new_alert_count = db.alerts.count_documents({})
            if new_alert_count > prev_alert_count:
                alerts_generated += (new_alert_count - prev_alert_count)
        except Exception as e:
            from app.core.logging_config import logger
            logger.exception(f"Failed to ingest raw telemetry event: {e}")
            continue

    if ingested > 0 or duplicates > 0:
        sensor_repo.record_telemetry_batch(sensor.sensor_id, ingested + duplicates)

    return TelemetryBatchIngestResponse(
        status="success",
        received=received,
        ingested=ingested,
        duplicates=duplicates,
        alerts_generated=alerts_generated,
    )
