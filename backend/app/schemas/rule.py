from typing import Optional, Dict, Any
from pydantic import Field
from app.schemas.common import BaseSchema
from app.schemas.event import SeverityType


class RuleResponse(BaseSchema):
    id: str
    name: str
    description: str
    category: str
    severity: SeverityType
    enabled: bool
    threshold: int
    windowSec: int = Field(..., alias="window_sec", serialization_alias="windowSec")
    lastTriggered: int = Field(0, alias="last_triggered", serialization_alias="lastTriggered")
    matches: int = 0
    ruleType: Optional[str] = Field("threshold", alias="rule_type", serialization_alias="ruleType")
    config: Optional[Dict[str, Any]] = None


class RuleCreate(BaseSchema):
    id: Optional[str] = None
    name: str
    description: str
    category: str
    severity: SeverityType = "medium"
    enabled: bool = True
    threshold: int = 10
    windowSec: int = Field(60, alias="window_sec")
    ruleType: str = Field("threshold", alias="rule_type")
    config: Optional[Dict[str, Any]] = None


class RuleUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[SeverityType] = None
    enabled: Optional[bool] = None
    threshold: Optional[int] = None
    windowSec: Optional[int] = Field(None, alias="window_sec")
    config: Optional[Dict[str, Any]] = None
