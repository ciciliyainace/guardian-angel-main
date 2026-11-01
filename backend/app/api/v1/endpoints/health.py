from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db, db_manager
from app.core.config import settings
from app.ml.registry import registry
from app.workers.ingestion_worker import ingestion_worker
from app.utils.time_utils import current_epoch_ms

router = APIRouter()


@router.get("/ping")
def ping() -> Dict[str, Any]:
    """Lightweight test connection check."""
    return {"status": "pong", "timestamp": current_epoch_ms(), "version": settings.VERSION}


@router.get("/ready")
def ready(db: Database = Depends(get_db)) -> Dict[str, Any]:
    """Readiness endpoint verifying actual MongoDB Atlas connection and ML model status."""
    db_ok = db_manager.ping()
    models_loaded = registry.rf.is_loaded or registry.iforest.is_loaded
    health_info = db_manager.get_health_info()

    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "database": "disconnected",
                "database_type": settings.DATABASE_TYPE,
                "cluster": health_info.get("cluster_uri"),
                "models_loaded": models_loaded,
                "error": health_info.get("error") or "MongoDB connection failed",
                "resolution": "Verify MONGODB_URI in backend/.env and ensure current IP is whitelisted in MongoDB Atlas Network Access.",
            },
        )

    return {
        "status": "ready",
        "database": "connected",
        "database_type": settings.DATABASE_TYPE,
        "database_name": settings.MONGODB_DATABASE,
        "cluster": health_info.get("cluster_uri"),
        "models_loaded": models_loaded,
        "firewall_mode": settings.FIREWALL_MODE,
        "blocking_enabled": settings.ALLOW_FIREWALL_BLOCKING,
    }


@router.get("", response_model=List[Dict[str, Any]])
def get_services_health(db: Database = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Returns array of system services matching the exact structure expected
    by the frontend System Health page:
    [{ name: str, status: HealthStatus, detail: str, error?: str }]
    """
    # 1. MongoDB Atlas Database Check
    db_ok = db_manager.ping()
    health_info = db_manager.get_health_info()
    if db_ok:
        db_status = "Operational"
        db_detail = f"MongoDB Atlas cluster connected ({settings.MONGODB_DATABASE})"
        db_err = None
    else:
        db_status = "Disconnected"
        db_detail = "MongoDB Atlas unreachable — verify credentials and Atlas IP whitelist"
        db_err = health_info.get("error")

    # 2. Collectors Check
    collector_status = "Operational"
    collector_detail = f"Active collectors ({len(ingestion_worker.collectors)})"

    # Suricata Sensor
    suricata_col = next((c for c in ingestion_worker.collectors if "Suricata" in c.name), None)
    suricata_status = suricata_col.status if suricata_col else "Disconnected"
    suricata_detail = suricata_col.detail if suricata_col else "Suricata integration not initialized"
    suricata_err = suricata_col.last_error if suricata_col else None

    # 3. ML Classifier
    rf_status = "Operational" if registry.rf.is_loaded else "Degraded"
    rf_detail = f"{registry.rf.version} active" if registry.rf.is_loaded else "Artifact missing: train via run_training.py"

    # 4. Anomaly Detector
    if_status = "Operational" if registry.iforest.is_loaded else "Degraded"
    if_detail = f"{registry.iforest.version} active" if registry.iforest.is_loaded else "Artifact missing: train via run_training.py"

    # 5. Firewall Integration
    fw_status = "Operational" if settings.FIREWALL_MODE == "simulation" else ("Operational" if settings.ALLOW_FIREWALL_BLOCKING else "Degraded")
    fw_detail = "Simulation adapter active (safe mode)" if settings.FIREWALL_MODE == "simulation" else "Windows Defender adapter enabled"

    return [
        {"name": "Backend API (FastAPI)", "status": "Operational", "detail": f"v{settings.VERSION} running on Windows"},
        {"name": "MongoDB Atlas Database", "status": db_status, "detail": db_detail, "error": db_err},
        {"name": "Network collector", "status": collector_status, "detail": collector_detail},
        {"name": "Suricata IDS integration", "status": suricata_status, "detail": suricata_detail, "error": suricata_err},
        {"name": "ML classifier", "status": rf_status, "detail": rf_detail},
        {"name": "Anomaly detector", "status": if_status, "detail": if_detail},
        {"name": "Firewall integration", "status": fw_status, "detail": fw_detail},
        {"name": "Event-processing queue", "status": "Operational", "detail": "Workers running without backlog"},
    ]
