from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SupportCreateRequest(BaseModel):
    subject: str = Field(..., min_length=3, max_length=150, description="Brief description of the inquiry")
    category: str = Field(
        default="General",
        description="Category: Account, Verification, Telemetry, Sensor, General"
    )
    message: str = Field(..., min_length=10, max_length=5000, description="Detailed explanation")
    email: Optional[EmailStr] = Field(None, description="Contact email if unauthenticated")
    name: Optional[str] = Field(None, max_length=100, description="Contact name")


class SupportResponse(BaseModel):
    status: str
    ticket_id: str
    message: str
    category: str
    subject: str
    contact_email: str
    support_contact: str = "revenreven287@gmail.com"
