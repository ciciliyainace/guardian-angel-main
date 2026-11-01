from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    health,
    events,
    traffic,
    alerts,
    detection,
    analytics,
    models,
    rules,
    firewall,
    audit,
    reports,
    settings,
    profile,
    feedback,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["traffic"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(detection.router, prefix="/detection", tags=["detection"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(firewall.router, prefix="/firewall", tags=["firewall"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
