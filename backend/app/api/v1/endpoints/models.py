from typing import Any, List, Dict
from fastapi import APIRouter
from app.ml.registry import registry

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]])
def list_models() -> Any:
    return registry.get_models_metadata()
