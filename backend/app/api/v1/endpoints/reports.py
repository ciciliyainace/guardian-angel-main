from typing import Any, Dict
from fastapi import APIRouter, Depends, Response
from pymongo.database import Database
from app.core.database import get_db
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/summary", response_model=Dict[str, Any])
def get_report_summary(db: Database = Depends(get_db)) -> Any:
    service = ReportService(db)
    return service.generate_summary()


@router.get("/export")
def export_reports_csv(db: Database = Depends(get_db)) -> Any:
    service = ReportService(db)
    csv_data = service.export_events_csv(limit=1000)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentinel-ai-events.csv"},
    )
