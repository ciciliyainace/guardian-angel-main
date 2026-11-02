from typing import Any, List, Optional, Union
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pymongo.database import Database
from app.core.database import get_db
from app.services.event_service import EventService
from app.schemas.event import EventResponse, EventCreate
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=Union[List[EventResponse], PaginatedResponse[EventResponse]])
def get_events(
    query: Optional[str] = Query(None, alias="q"),
    severity: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    origin: Optional[str] = Query(None, description="Data origin: live, simulated, or all"),
    range: Optional[str] = Query(None, description="1h, 6h, 24h, all"),
    page: int = Query(1, ge=1),
    page_size: int = Query(500, ge=1, le=1000, alias="pageSize"),
    sort_by: str = Query("timestamp", alias="sortBy"),
    sort_dir: str = Query("desc", alias="sortDir"),
    paginated: bool = Query(False, description="Set true to return paginated wrapper"),
    db: Database = Depends(get_db),
) -> Any:
    range_hours = None
    if range:
        range_map = {"1h": 1, "6h": 6, "24h": 24}
        range_hours = range_map.get(range)

    service = EventService(db)
    items, total, p, pages = service.filter_events(
        query=query,
        severity=severity,
        category=category,
        status=status,
        range_hours=range_hours,
        origin=origin,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    result_items = [ev.to_dict() for ev in items]
    if paginated:
        return {
            "items": result_items,
            "total": total,
            "page": p,
            "page_size": page_size,
            "pages": pages,
        }
    return result_items


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Database = Depends(get_db)) -> Any:
    service = EventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found")
    return event.to_dict()


@router.post("/ingest", response_model=EventResponse)
def ingest_event(payload: EventCreate, db: Database = Depends(get_db)) -> Any:
    service = EventService(db)
    ev = service.ingest_event(payload.model_dump(), run_detection=True)
    return ev.to_dict()


@router.get("/scenarios/list")
def list_simulation_scenarios() -> Any:
    """Return available safe attack simulation scenarios for development and demonstration."""
    from app.services.sample_generator import SampleEventGenerator
    return SampleEventGenerator.list_scenarios()


@router.post("/simulate")
def simulate_events(
    scenario: str = Query("port_scan", description="port_scan, dos_syn_flood, brute_force, anomalous_beacon, benign_web"),
    count: int = Query(3, ge=1, le=25),
    db: Database = Depends(get_db),
) -> Any:
    """
    Generate and ingest safe, simulated attack flows into the live detection pipeline.
    Persists events and correlated alerts into MongoDB Atlas.
    """
    from app.services.sample_generator import SampleEventGenerator
    service = EventService(db)
    generated = SampleEventGenerator.generate_events(scenario_key=scenario, count=count)
    initial_alert_ids = set(a["id"] for a in db.alerts.find({}, {"id": 1}))
    ingested = [service.ingest_event(ev, run_detection=True, actor="api_simulation").to_dict() for ev in generated]

    event_ids = [e["id"] for e in ingested]
    related_alerts = list(db.alerts.find({"related_event_id": {"$in": event_ids}}))
    new_alerts = [a for a in related_alerts if a["id"] not in initial_alert_ids]

    return {
        "status": "success",
        "scenario": scenario,
        "events_count": len(ingested),
        "events": ingested,
        "alerts_count": len(new_alerts),
        "total_related_alerts": len(related_alerts),
        "alert_ids": [a["id"] for a in (new_alerts if new_alerts else related_alerts)],
    }


@router.get("/collectors/status")
def get_collectors_status() -> Any:
    """Inspect collector health, last ingestion timestamp, and collector states."""
    from app.workers.ingestion_worker import ingestion_worker
    return [c.get_health_status() for c in ingestion_worker.collectors]


@router.post("/collectors/{collector_name}/poll")
def poll_collector_manually(collector_name: str, db: Database = Depends(get_db)) -> Any:
    """Trigger an on-demand poll of a specific collector for testing."""
    from app.workers.ingestion_worker import ingestion_worker
    matching = next((c for c in ingestion_worker.collectors if collector_name.lower() in c.name.lower()), None)
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collector '{collector_name}' not found. Available: {[c.name for c in ingestion_worker.collectors]}",
        )

    records = matching.collect()
    service = EventService(db)
    ingested = [service.ingest_event(r, run_detection=True, actor="manual_poll").to_dict() for r in records]

    return {
        "collector": matching.name,
        "polled_count": len(records),
        "ingested_count": len(ingested),
        "status": matching.status,
        "detail": matching.detail,
    }
