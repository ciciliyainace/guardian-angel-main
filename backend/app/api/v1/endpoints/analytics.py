from typing import Any, List, Dict
from fastapi import APIRouter, Depends
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
def get_overview_summary(db: Database = Depends(get_db)) -> Any:
    service = AnalyticsService(db)
    return service.get_overview_summary()


@router.get("/categories", response_model=List[CategoryCount])
def get_categories(db: Database = Depends(get_db)) -> Any:
    service = AnalyticsService(db)
    return service.get_categories()


@router.get("/severity", response_model=List[SeverityCount])
def get_severity(db: Database = Depends(get_db)) -> Any:
    service = AnalyticsService(db)
    return service.get_severities()


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
