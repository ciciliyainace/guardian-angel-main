from typing import List, Dict, Any, Optional
from app.schemas.common import BaseSchema


class TrafficPoint(BaseSchema):
    time: str
    benign: int
    suspicious: int
    total: int


class CategoryCount(BaseSchema):
    category: str
    count: int


class SeverityCount(BaseSchema):
    severity: str
    count: int


class FirewallHistoryItem(BaseSchema):
    day: str
    approved: int
    rejected: int
    expired: int


class ModelMetricSummary(BaseSchema):
    precision: float
    recall: float
    f1: float
    fpr: float
    latencyMs: float


class PerClassRecall(BaseSchema):
    cls: str
    recall: float


class ConfusionMatrix(BaseSchema):
    labels: List[str]
    matrix: List[List[int]]


class AnomalyBucket(BaseSchema):
    bucket: str
    normal: int
    anomalous: int


class OverviewSummary(BaseSchema):
    totalEvents: int
    activeAlerts: int
    criticalThreats: int
    suspiciousConnections: int
    managedBlocks: int
    detectionRecall: str
    eventsDelta: Optional[int] = 0
    alertsDelta: Optional[int] = 0
    threatsDelta: Optional[int] = 0
    suspiciousDelta: Optional[int] = 0
