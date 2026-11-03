import secrets
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pymongo.database import Database

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_authenticated_user
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
    SensorKeyGenerationRequest,
    SensorRevokeResponse,
    SensorHeartbeatRequest,
    SensorHeartbeatResponse,
    TelemetryBatchIngestRequest,
    TelemetryBatchIngestResponse,
    SensorListItem,
)

router = APIRouter()


def authenticate_sensor(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_sensor_key: Optional[str] = Header(None, alias="X-Sensor-Key"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Database = Depends(get_db),
) -> Sensor:
    """
    Validate sensor API token via constant-time SHA-256 hash lookup.
    Supports:
      1. Authorization: Bearer <sensor_token>
      2. X-Sensor-Key: <sensor_token>
      3. X-API-Key: <sensor_token>
    Strictly forbids user JWTs from accessing sensor collector endpoints.
    """
    raw_token = None
    if authorization and authorization.lower().startswith("bearer "):
        raw_token = authorization[7:].strip()
    elif x_sensor_key:
        raw_token = x_sensor_key.strip()
    elif x_api_key:
        raw_token = x_api_key.strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sensor authentication required. Provide Authorization: Bearer <sensor_token> or X-Sensor-Key header.",
        )

    # Reject user JWT tokens from sensor endpoints (zero token cross-use)
    if raw_token.startswith("ey"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication tokens cannot be used as sensor API tokens. Please use your enrolled sensor token.",
        )

    key_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    sensor_repo = SensorRepository(db)
    sensor = sensor_repo.get_by_key_hash(key_hash)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked sensor credential.",
        )
    if sensor.status == "revoked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This sensor has been permanently revoked by an administrator.",
        )
    return sensor


@router.post("/enroll", response_model=SensorEnrollResponse, status_code=status.HTTP_201_CREATED)
def enroll_sensor(
    req: SensorEnrollRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Dual-mode sensor enrollment endpoint:
    
    Mode 1 (Desktop Agent):
      Submits `enrollment_credential` + `sensor_name` + `host_info`.
      Does NOT require a user JWT.
      Validates the one-time enrollment credential, atomically consumes it,
      issues a long-lived `sensor_token`, activates sensor to 'registered',
      and binds to the pre-authorized workspace.
      
    Mode 2 (Web Dashboard):
      Authenticated user with JWT creates or rotates a sensor credential.
      Generates a one-time enrollment credential valid for 7 days.
    """
    sensor_repo = SensorRepository(db)
    ws_repo = WorkspaceRepository(db)
    user_repo = UserRepository(db)
    client_ip = request.client.host if request.client else None
    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------
    # Mode 1: Desktop Agent Setup Enrollment (One-time credential exchange)
    # -------------------------------------------------------------
    if req.enrollment_credential and req.enrollment_credential.strip():
        cred = req.enrollment_credential.strip()
        cred_hash = hashlib.sha256(cred.encode("utf-8")).hexdigest()

        sensor = sensor_repo.get_by_enrollment_credential_hash(cred_hash)
        if not sensor:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid sensor enrollment credential. Please generate a new key from your SentinelAI Web Dashboard.",
            )

        if sensor.status == "revoked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sensor '{sensor.sensor_id}' has been permanently revoked.",
            )

        if sensor.enrollment_credential_consumed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This enrollment credential has already been consumed. Please generate a fresh credential from your SentinelAI Web Dashboard.",
            )

        if sensor.enrollment_credential_expires_at:
            exp = sensor.enrollment_credential_expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if now > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Enrollment credential has expired. Please generate a fresh credential from your SentinelAI Web Dashboard.",
                )

        # Generate uncompromised long-lived sensor API token
        raw_sensor_token = f"sen_live_{secrets.token_hex(24)}"
        token_hash = hashlib.sha256(raw_sensor_token.encode("utf-8")).hexdigest()

        # Atomically consume credential and bind host details
        host_info_dict = req.host_info or {}
        if req.sensor_description and "description" not in host_info_dict:
            host_info_dict["description"] = req.sensor_description

        activated = sensor_repo.consume_enrollment_and_activate(
            sensor_id=sensor.sensor_id,
            sensor_token_hash=token_hash,
            host_info=host_info_dict,
            remote_ip=client_ip,
        )

        ws = ws_repo.get_by_id(sensor.workspace_id) if sensor.workspace_id else None
        workspace_name = ws.name if ws else "Default Workspace"

        return SensorEnrollResponse(
            success=True,
            sensor_id=sensor.sensor_id,
            name=sensor.name,
            sensor_token=raw_sensor_token,
            api_key=raw_sensor_token,
            workspace_id=sensor.workspace_id or "",
            workspace_name=workspace_name,
            status="registered",
            message=f"Sensor '{sensor.sensor_id}' successfully enrolled into workspace '{workspace_name}'.",
        )

    # -------------------------------------------------------------
    # Mode 2: Web Dashboard Sensor Key Generation
    # -------------------------------------------------------------
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in or provide a valid sensor enrollment credential.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sensor_id = (req.sensor_id or req.sensor_name or "").strip()
    if not sensor_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sensor identifier is required.",
        )

    sensor_name = (req.name or req.sensor_name or sensor_id).strip()

    # Workspace resolution
    ws = None
    if current_user.default_workspace_id:
        ws = ws_repo.get_by_id(current_user.default_workspace_id)
    if not ws:
        ws = ws_repo.get_or_create_default_workspace(current_user.id, current_user.username)
        current_user.default_workspace_id = ws.id
        user_repo.update(current_user)

    existing = sensor_repo.get_by_id(sensor_id)
    raw_enrollment_key = f"sen_enroll_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(raw_enrollment_key.encode("utf-8")).hexdigest()
    expires_at = now + timedelta(days=7)

    if existing:
        # Cross-tenant ownership check
        if existing.workspace_id and existing.workspace_id != ws.id and existing.owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Sensor identifier '{sensor_id}' is already registered in another workspace.",
            )

        # Re-enrollment / credential rotation in caller's workspace
        updated = sensor_repo.rotate_enrollment_credential(
            sensor_id=sensor_id,
            new_credential_hash=key_hash,
            expires_at=expires_at,
        )
        return SensorEnrollResponse(
            success=True,
            sensor_id=sensor_id,
            name=existing.name or sensor_name,
            enrollment_credential=raw_enrollment_key,
            api_key=raw_enrollment_key,
            workspace_id=ws.id,
            workspace_name=ws.name,
            status="pending_enrollment",
            message="Enrollment credential refreshed. Enter this credential into your Windows Sensor Setup application.",
            expires_at=expires_at.isoformat(),
        )

    # Brand new sensor record creation in caller's workspace
    new_sensor = Sensor(
        sensor_id=sensor_id,
        name=sensor_name,
        api_key_hash=key_hash,
        enrollment_credential_hash=key_hash,
        enrollment_credential_expires_at=expires_at,
        enrollment_credential_consumed=False,
        hostname=req.hostname or "",
        collector_types=req.collector_types or ["windows_sockets", "suricata"],
        status="pending_enrollment",
        workspace_id=ws.id,
        owner_user_id=current_user.id,
        enrolled_by=current_user.username,
        created_at=now,
    )
    sensor_repo.enroll(new_sensor)

    return SensorEnrollResponse(
        success=True,
        sensor_id=sensor_id,
        name=sensor_name,
        enrollment_credential=raw_enrollment_key,
        api_key=raw_enrollment_key,
        workspace_id=ws.id,
        workspace_name=ws.name,
        status="pending_enrollment",
        message="Sensor created successfully. Enter this enrollment credential into your Windows Sensor Setup application.",
        expires_at=expires_at.isoformat(),
    )


@router.post("/keys", response_model=SensorEnrollResponse)
def generate_sensor_key(
    req: SensorKeyGenerationRequest,
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
):
    """Explicit authenticated endpoint for web dashboard sensor key generation and rotation."""
    enroll_req = SensorEnrollRequest(
        sensor_id=req.sensor_id,
        name=req.name or req.sensor_id,
        hostname=req.hostname,
        collector_types=req.collector_types,
    )
    return enroll_sensor(enroll_req, Request({"type": "http"}), current_user=current_user, db=db)


@router.post("/{sensor_id}/rotate-key", response_model=SensorEnrollResponse)
def rotate_sensor_key_endpoint(
    sensor_id: str,
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
):
    """Explicit authenticated key rotation for an existing sensor in caller's workspace."""
    sensor_repo = SensorRepository(db)
    sensor = sensor_repo.get_by_id(sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor '{sensor_id}' not found.",
        )

    is_admin = current_user.role.lower() in ("admin", "administrator")
    is_owner = (sensor.owner_user_id == current_user.id) or (sensor.workspace_id == current_user.default_workspace_id)
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to rotate credentials for sensors in another workspace.",
        )

    raw_enrollment_key = f"sen_enroll_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(raw_enrollment_key.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    sensor_repo.rotate_enrollment_credential(
        sensor_id=sensor_id,
        new_credential_hash=key_hash,
        expires_at=expires_at,
    )

    ws_repo = WorkspaceRepository(db)
    ws = ws_repo.get_by_id(sensor.workspace_id) if sensor.workspace_id else None
    ws_name = ws.name if ws else "Workspace"

    return SensorEnrollResponse(
        success=True,
        sensor_id=sensor_id,
        name=sensor.name,
        enrollment_credential=raw_enrollment_key,
        api_key=raw_enrollment_key,
        workspace_id=sensor.workspace_id or "",
        workspace_name=ws_name,
        status="pending_enrollment",
        message="A fresh enrollment credential has been generated. Use it in the Windows Sensor Setup application.",
        expires_at=expires_at.isoformat(),
    )


@router.get("", response_model=List[SensorListItem])
def list_sensors(
    current_user: User = Depends(require_authenticated_user),
    db: Database = Depends(get_db),
):
    """
    Lists sensors scoped to the caller's workspace (or all for system admin).
    Reports both registration state and real-time connectivity status.
    """
    sensor_repo = SensorRepository(db)
    sensors = sensor_repo.list_sensors()
    now = datetime.now(timezone.utc)

    is_admin = current_user.role.lower() in ("admin", "administrator")
    user_ws = current_user.default_workspace_id

    items: List[SensorListItem] = []
    for s in sensors:
        if not is_admin:
            if s.workspace_id and s.workspace_id != user_ws and s.owner_user_id != current_user.id:
                continue

        conn_status = s.get_connectivity_status(now)
        is_alive = conn_status == "online"

        items.append(
            SensorListItem(
                sensor_id=s.sensor_id,
                name=s.name,
                hostname=s.hostname,
                ip_address=s.ip_address,
                collector_types=s.collector_types,
                status=s.status,
                connectivity_status=conn_status,
                enrolled_by=s.enrolled_by,
                workspace_id=s.workspace_id,
                created_at=s.created_at.isoformat() if s.created_at else None,
                enrolled_at=s.enrolled_at.isoformat() if s.enrolled_at else None,
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
    is_owner = (sensor.owner_user_id == current_user.id) or (sensor.workspace_id == current_user.default_workspace_id)
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
    """
    Record periodic heartbeat and collector status from an active Windows sensor.
    Transitions sensor connectivity status to 'online'.
    """
    sensor_repo = SensorRepository(db)
    client_ip = request.client.host if request.client else None
    now = datetime.now(timezone.utc)

    # Build collector details from request
    collectors = dict(req.collectors)
    if req.selected_interface:
        collectors["interface"] = req.selected_interface
    if req.suricata_running is not None:
        collectors["suricata"] = "running" if req.suricata_running else "stopped"
    if req.npcap_running is not None:
        collectors["npcap"] = "active" if req.npcap_running else "missing"

    metrics = dict(req.metrics)
    if req.queued_events is not None:
        metrics["queued_events"] = req.queued_events
    if req.transmitted_events is not None:
        metrics["transmitted_events"] = req.transmitted_events
    if req.dropped_events is not None:
        metrics["dropped_events"] = req.dropped_events

    heartbeat = SensorHeartbeat(
        sensor_id=sensor.sensor_id,
        timestamp=now,
        ip_address=client_ip,
        metrics=metrics,
        collectors=collectors,
        suricata_running=req.suricata_running,
        npcap_running=req.npcap_running,
        uptime_seconds=req.uptime_seconds,
        agent_version=req.agent_version,
    )
    sensor_repo.record_heartbeat(sensor.sensor_id, heartbeat, remote_ip=client_ip)

    return SensorHeartbeatResponse(
        success=True,
        acknowledged=True,
        timestamp=int(now.timestamp() * 1000),
        server_time=now.isoformat(),
        command="none",
        server_status="ready",
        message="Heartbeat acknowledged",
    )


@router.post("/telemetry", response_model=TelemetryBatchIngestResponse)
@router.post("/events/batch", response_model=TelemetryBatchIngestResponse)
def ingest_telemetry_batch(
    req: TelemetryBatchIngestRequest,
    sensor: Sensor = Depends(authenticate_sensor),
    db: Database = Depends(get_db),
):
    """
    Ingest a batch of genuine network telemetry events from an enrolled sensor.
    Available under both /telemetry and /events/batch.
    Dispatches to flow aggregator, normalizer, and hybrid detection pipeline.
    Tenant workspace and owner are strictly bound from the sensor record.
    """
    event_service = EventService(db)
    sensor_repo = SensorRepository(db)

    received = len(req.events)
    ingested = 0
    duplicates = 0
    alerts_generated = 0

    for raw_event in req.events:
        try:
            collector = raw_event.get("collector") or ("suricata" if "event_type" in raw_event else "windows_sockets")
            if collector == "suricata" or "event_type" in raw_event:
                normalized = FlowAggregator.parse_suricata_eve(raw_event, sensor_id=sensor.sensor_id)
            else:
                normalized = FlowAggregator.parse_windows_socket(raw_event, sensor_id=sensor.sensor_id)

            # Strictly bind to sensor's verified workspace and owner in DB
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
            logger.exception(f"Failed to ingest raw telemetry event from sensor '{sensor.sensor_id}': {e}")
            continue

    if ingested > 0 or duplicates > 0:
        sensor_repo.record_telemetry_batch(sensor.sensor_id, ingested + duplicates)

    now_iso = datetime.now(timezone.utc).isoformat()
    return TelemetryBatchIngestResponse(
        success=True,
        status="success",
        batch_id=req.batch_id,
        processed_count=ingested + duplicates,
        rejected_count=received - (ingested + duplicates),
        received=received,
        ingested=ingested,
        duplicates=duplicates,
        alerts_generated=alerts_generated,
        server_timestamp=now_iso,
        message=f"Processed {ingested} events ({duplicates} duplicate flows ignored).",
    )
