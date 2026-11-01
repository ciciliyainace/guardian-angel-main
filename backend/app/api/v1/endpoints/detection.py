from typing import Any, List
from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.core.database import get_db
from app.services.detection_service import DetectionService
from app.schemas.detection import AnalyzeRequest, AnalyzeResponse, DetectionStatusResponse
from app.schemas.rule import RuleResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_traffic(payload: AnalyzeRequest, db: Database = Depends(get_db)) -> Any:
    service = DetectionService(db)
    res = service.analyze_event({
        "source_ip": payload.sourceIp,
        "dest_ip": payload.destIp,
        "src_port": payload.srcPort,
        "dst_port": payload.dstPort,
        "protocol": payload.protocol,
        "flow_features": payload.flowFeatures,
        "metadata": {"signature": payload.signatureName} if payload.signatureName else {},
    })
    return {
        "eventId": res["event_id"],
        "detectionSources": res["detection_sources"],
        "predictedCategory": res["predicted_category"],
        "severity": res["severity"],
        "riskScore": res["risk_score"],
        "evidence": res["evidence"],
        "modelVersions": res["model_versions"],
        "ruleIds": res["rule_ids"],
        "recommendedAction": res["recommended_action"],
        "timestamp": res["timestamp"],
    }


@router.get("/status", response_model=DetectionStatusResponse)
def get_detection_status(db: Database = Depends(get_db)) -> Any:
    service = DetectionService(db)
    st = service.get_status()
    return {
        "ruleEngineStatus": st["rule_engine_status"],
        "rfStatus": st["rf_status"],
        "ifStatus": st["if_status"],
        "hybridStatus": st["hybrid_status"],
        "activeRulesCount": st["active_rules_count"],
        "loadedModelsCount": st["loaded_models_count"],
    }


@router.get("/rules", response_model=List[RuleResponse])
def get_detection_rules(db: Database = Depends(get_db)) -> Any:
    service = DetectionService(db)
    rules = service.list_rules()
    return [r.to_dict() for r in rules]
