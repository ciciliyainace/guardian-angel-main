import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, field_validator
from app.schemas.common import BaseSchema

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class LoginRequest(BaseSchema):
    username_or_email: str = Field(..., min_length=1, description="Registered username or email address")
    password: str = Field(..., min_length=1, description="Account password")


class RegisterRequest(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_\-\.]+$", description="Unique alphanumeric username")
    email: str = Field(..., min_length=5, max_length=255, pattern=EMAIL_REGEX, description="Valid corporate or user email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong password (min 8 chars)")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")
    display_name: Optional[str] = Field(None, max_length=100, description="Optional profile display name")
    terms_accepted: bool = Field(True, description="Terms of Service & Security Policy acceptance")

    @field_validator("username")
    @classmethod
    def clean_username(cls, v: str) -> str:
        return v.strip()

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(EMAIL_REGEX, clean):
            raise ValueError("Invalid email address format.")
        return clean


class UserResponse(BaseSchema):
    id: int
    email: str
    username: str
    display_name: str
    role: str
    is_active: bool
    email_verified: bool = False
    auth_providers: List[str] = ["password"]
    created_at: Optional[Any] = None
    first_login_at: Optional[Any] = None
    last_login_at: Optional[Any] = None


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class GoogleAuthRequest(BaseSchema):
    id_token: Optional[str] = Field(None, description="Google OpenID Connect identity token")
    code: Optional[str] = Field(None, description="Google OAuth authorization code")
    redirect_uri: Optional[str] = Field(None, description="Client redirect URI used for authorization code")


class GoogleUrlResponse(BaseSchema):
    configured: bool
    url: Optional[str] = None
    message: Optional[str] = None


class VerifyEmailRequest(BaseSchema):
    token: str = Field(..., min_length=16, description="Cryptographic verification token")


class ResendVerificationRequest(BaseSchema):
    email: str = Field(..., min_length=5, max_length=255, pattern=EMAIL_REGEX, description="Registered email address requiring verification")

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()


class ForgotPasswordRequest(BaseSchema):
    email: str = Field(..., min_length=5, max_length=255, pattern=EMAIL_REGEX, description="Registered account email address")

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseSchema):
    token: str = Field(..., min_length=16, description="Cryptographic password reset token")
    password: str = Field(..., min_length=8, max_length=128, description="New strong password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirmation of new password")


class GenericMessageResponse(BaseSchema):
    status: str = "success"
    message: str
    email_status: Optional[str] = None


class UserCreate(BaseSchema):
    email: str = Field(..., pattern=EMAIL_REGEX)
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: str = "analyst"


class UserUpdate(BaseSchema):
    email: Optional[str] = Field(None, pattern=EMAIL_REGEX)
    display_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
