from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pymongo.database import Database
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.support_message import SupportMessage
from app.repositories.support_repository import SupportRepository
from app.services.email_service import EmailService
from app.services.audit_service import AuditService
from app.schemas.support import SupportCreateRequest, SupportResponse

router = APIRouter()


@router.post("/messages", response_model=SupportResponse, status_code=status.HTTP_201_CREATED)
def submit_support_message(
    payload: SupportCreateRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> Any:
    """
    Submit a support inquiry or assistance request:
    - Supports authenticated analysts or unauthenticated users
    - Validates email address and inquiry content
    - Enforces rate limiting (max 5 requests per 15 minutes per email)
    - Persists message in MongoDB Atlas 'support_messages' collection
    - Records entry in 'audit_logs'
    - Dispatches receipt email to user and notification to revenreven287@gmail.com
    """
    repo = SupportRepository(db)
    audit = AuditService(db)
    email_service = EmailService(db)

    # 1. Determine user identity and contact email
    user_id = current_user.id if current_user else None
    workspace_id = current_user.default_workspace_id if current_user else "ws_public"
    contact_email = (current_user.email if current_user else (payload.email or "")).strip().lower()
    contact_name = current_user.display_name if current_user else (payload.name or "Analyst")

    if not contact_email or "@" not in contact_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid contact email address is required to submit support messages.",
        )

    # 2. Rate limiting check (max 5 inquiries per 15 mins)
    fifteen_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
    recent_count = db.support_messages.count_documents({
        "email": contact_email,
        "created_at": {"$gte": fifteen_mins_ago},
    })
    if recent_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait 15 minutes before submitting another support inquiry.",
        )

    # 3. Create SupportMessage instance
    msg = SupportMessage(
        user_id=user_id,
        workspace_id=workspace_id,
        email=contact_email,
        name=contact_name,
        subject=payload.subject.strip(),
        category=payload.category,
        message=payload.message.strip(),
        status="open",
    )
    saved_msg = repo.create(msg)

    # 4. Log in audit trail
    actor_str = current_user.username if current_user else f"anon:{contact_email}"
    audit.log(
        actor=actor_str,
        action="SubmitSupportMessage",
        target=f"ticket:{saved_msg.id}",
        result="Success",
        reason=f"Support ticket submitted under category '{saved_msg.category}'",
    )

    # 5. Dispatch confirmation email to user & notification to support team (revenreven287@gmail.com)
    email_service.send_support_receipt_email(
        user_email=contact_email,
        ticket_id=saved_msg.id,
        subject=saved_msg.subject,
        category=saved_msg.category,
        user_name=contact_name,
    )

    email_service.send_support_staff_notification(
        ticket_id=saved_msg.id,
        sender_email=contact_email,
        subject=saved_msg.subject,
        category=saved_msg.category,
        message=saved_msg.message,
        user_id=user_id,
    )

    return {
        "status": "success",
        "ticket_id": saved_msg.id,
        "message": "Your support message has been logged. Our security team will review it shortly.",
        "category": saved_msg.category,
        "subject": saved_msg.subject,
        "contact_email": contact_email,
        "support_contact": "revenreven287@gmail.com",
    }

