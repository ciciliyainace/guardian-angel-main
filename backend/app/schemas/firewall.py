from typing import Optional, Literal
from pydantic import Field, field_validator
from app.schemas.common import BaseSchema

BlockStatusType = Literal["pending", "approved", "rejected", "expired"]
DirectionType = Literal["Inbound", "Outbound"]


class BlockRequestResponse(BaseSchema):
    id: str
    sourceIp: str = Field(..., alias="source_ip", serialization_alias="sourceIp")
    reason: str
    alertId: str = Field("", alias="alert_id", serialization_alias="alertId")
    requestedBy: str = Field(..., alias="requested_by", serialization_alias="requestedBy")
    requestedAt: int = Field(..., alias="requested_at", serialization_alias="requestedAt")
    durationMin: int = Field(..., alias="duration_min", serialization_alias="durationMin")
    status: BlockStatusType
    direction: DirectionType = "Inbound"
    reviewedBy: Optional[str] = Field(None, alias="reviewed_by", serialization_alias="reviewedBy")
    reviewedAt: Optional[int] = Field(None, alias="reviewed_at", serialization_alias="reviewedAt")


class BlockRequestCreate(BaseSchema):
    sourceIp: str = Field(..., alias="source_ip")
    reason: str
    alertId: Optional[str] = Field("", alias="alert_id")
    durationMin: int = Field(60, alias="duration_min", ge=5, le=1440)  # Between 5 min and 24 hours
    direction: DirectionType = "Inbound"

    @field_validator("direction", mode="before")
    @classmethod
    def normalize_direction(cls, v: str) -> str:
        if isinstance(v, str):
            s = v.strip().capitalize()
            if s in ("Inbound", "Outbound"):
                return s
        return v

    @field_validator("sourceIp")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        import ipaddress
        try:
            ipaddress.ip_address(v.strip())
            return v.strip()
        except ValueError:
            raise ValueError(f"'{v}' is not a valid IPv4 or IPv6 address")


class FirewallApprovalRequest(BaseSchema):
    reviewer_note: Optional[str] = None


class FirewallRejectionRequest(BaseSchema):
    reason: Optional[str] = "False positive or administrative exception"


class FirewallActionResponse(BaseSchema):
    id: str
    managedRuleName: str = Field(..., alias="managed_rule_name", serialization_alias="managedRuleName")
    requestId: Optional[str] = Field(None, alias="request_id", serialization_alias="requestId")
    targetIp: str = Field(..., alias="target_ip", serialization_alias="targetIp")
    direction: str
    status: str
    durationMin: int = Field(..., alias="duration_min", serialization_alias="durationMin")
    verificationStatus: str = Field(..., alias="verification_status", serialization_alias="verificationStatus")
    rollbackStatus: Optional[str] = Field(None, alias="rollback_status", serialization_alias="rollbackStatus")
    failureDetails: Optional[str] = Field(None, alias="failure_details", serialization_alias="failureDetails")
