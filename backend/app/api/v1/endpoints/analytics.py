from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, Query
from pymongo.database import Database
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    OverviewSummary,
    CategoryCount,
    SeverityCount,
    TrafficPoint,
    FirewallHistoryItem,
)

router = APIRouter()


@router.get("/summary", response_model=OverviewSummary)
def get_overview_summary(
    origin: Optional[str] = Query("live", description="Data origin: live, simulated, or all"),
    time_range: Optional[str] = Query("24h", alias="range", description="Time window: 15m, 1h, 24h, 7d, all"),
    db: Database = Depends(get_db),
) -> Any:
    service = AnalyticsService(db)
    return service.get_overview_summary(data_origin=origin or "live", time_range=time_range or "24h")


@router.get("/categories", response_model=List[CategoryCount])
def get_categories(
    origin: Optional[str] = Query("live", description="Data origin: live, simulated, or all"),
    time_range: Optional[str] = Query("24h", alias="range", description="Time window: 15m, 1h, 24h, 7d, all"),
    db: Database = Depends(get_db),
) -> Any:
    service = AnalyticsService(db)
    return service.get_categories(data_origin=origin or "live", time_range=time_range or "24h")


@router.get("/severity", response_model=List[SeverityCount])
def get_severity(
    origin: Optional[str] = Query("live", description="Data origin: live, simulated, or all"),
    time_range: Optional[str] = Query("24h", alias="range", description="Time window: 15m, 1h, 24h, 7d, all"),
    db: Database = Depends(get_db),
) -> Any:
    service = AnalyticsService(db)
    return service.get_severities(data_origin=origin or "live", time_range=time_range or "24h")


@router.get("/traffic-series", response_model=List[TrafficPoint])
def get_traffic_series(db: Database = Depends(get_db)) -> Any:
    service = AnalyticsService(db)
    return service.get_traffic_series()


@router.get("/firewall-history", response_model=List[FirewallHistoryItem])
def get_firewall_history(db: Database = Depends(get_db)) -> Any:
    service = AnalyticsService(db)
    return service.get_firewall_history()


@router.get("/model-metrics", response_model=Dict[str, Any])
def get_model_metrics(db: Database = Depends(get_db)) -> Any:
    service = AnalyticsService(db)
    return service.get_model_metrics()
