from typing import Any, List, Dict
from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.core.database import get_db
from app.services.traffic_service import TrafficService
from app.schemas.analytics import TrafficPoint

router = APIRouter()


@router.get("/timeseries", response_model=List[TrafficPoint])
def get_traffic_timeseries(db: Database = Depends(get_db)) -> Any:
    service = TrafficService(db)
    return service.get_timeseries_24h()


@router.get("/summary", response_model=Dict[str, Any])
def get_traffic_summary(db: Database = Depends(get_db)) -> Any:
    service = TrafficService(db)
    return service.get_summary()
