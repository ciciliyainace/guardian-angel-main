import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging_config import logger
from app.models.user import User
from app.models.email_delivery_log import EmailDeliveryLog
from app.repositories.email_delivery_repository import EmailDeliveryRepository


class EmailService:
    """
    Enterprise Email Notification Service for SentinelAI SOC.
    Designated Primary Sender and Support Address: revenreven287@gmail.com
    Supports Gmail SMTP (smtp.gmail.com:587 STARTTLS / 465 SSL) and transactional providers.
    Safe-mode fallback when credentials are not configured in environment.
    """
    def __init__(self, db: Optional[Any] = None):
        self.smtp_host = settings.SMTP_HOST or "smtp.gmail.com"
        self.smtp_port = int(settings.SMTP_PORT or 587)
        self.smtp_username = settings.SMTP_USERNAME or "revenreven287@gmail.com"
        self.smtp_password = settings.SMTP_PASSWORD or ""
        self.smtp_security = (settings.SMTP_SECURITY or "starttls").lower().strip()
        self.use_tls = self.smtp_security == "starttls" or settings.SMTP_USE_TLS
        self.use_ssl = self.smtp_security == "ssl" or settings.SMTP_USE_SSL or self.smtp_port == 465
        self.from_email = settings.MAIL_FROM_EMAIL or "revenreven287@gmail.com"
        self.from_name = settings.MAIL_FROM_NAME or "SentinelAI Security Team"
        self.support_email = settings.SUPPORT_EMAIL or "revenreven287@gmail.com"
        self.frontend_base_url = (settings.FRONTEND_BASE_URL or "https://guardian-angel-main.vercel.app").rstrip("/")
        self.db = db
        self.delivery_repo = EmailDeliveryRepository(db) if db is not None else None

    def is_configured(self) -> bool:
        """
        Check if SMTP credentials are fully configured.
        Requires valid host, username, password, and sender address.
        """
        return bool(
            self.smtp_host
            and self.smtp_host.strip()
            and self.smtp_password
            and self.smtp_password.strip()
            and self.from_email
            and self.from_email.strip()
        )

    def _render_base_template(self, title: str, subtitle: str, content_html: str) -> str:
        """Render high-contrast, cyber-defense themed dark HTML email template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #0b0f17;
      color: #cbd5e1;
      margin: 0;
      padding: 24px;
      line-height: 1.6;
    }}
    .email-container {{
      max-width: 600px;
      margin: 0 auto;
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }}
    .header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      border-bottom: 2px solid #06b6d4;
      padding: 28px 24px;
      text-align: center;
    }}
    .logo-badge {{
      display: inline-block;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 700;
      font-size: 11px;
      letter-spacing: 2px;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 4px 10px;
      border-radius: 4px;
      margin-bottom: 12px;
    }}
    .title {{
      margin: 0;
      color: #f8fafc;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .subtitle {{
      margin: 6px 0 0 0;
      color: #94a3b8;
      font-size: 13px;
    }}
    .body {{
      padding: 28px 24px;
      color: #cbd5e1;
      font-size: 14px;
    }}
    .btn {{
      display: inline-block;
      background: #0284c7;
      color: #ffffff !important;
      text-decoration: none;
      padding: 12px 26px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 6px;
      text-align: center;
      margin: 18px 0;
      letter-spacing: 0.2px;
    }}
    .btn:hover {{
      background: #0369a1;
    }}
    .info-card {{
      background: #0b0f17;
      border: 1px solid #1e293b;
      border-left: 3px solid #06b6d4;
      border-radius: 4px;
      padding: 14px;
      margin: 18px 0;
      font-size: 13px;
    }}
    .security-notice {{
      background: rgba(234, 179, 8, 0.08);
      border: 1px solid rgba(234, 179, 8, 0.3);
      border-radius: 4px;
      padding: 12px;
      margin: 20px 0;
      font-size: 12px;
      color: #facc15;
    }}
    .footer {{
      padding: 20px 24px;
      border-top: 1px solid #1e293b;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      background: #0b0f17;
      line-height: 1.7;
    }}
    .footer a {{
      color: #38bdf8;
      text-decoration: none;
    }}
    .footer a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <div class="logo-badge">SENTINEL AI — SOC DEFENSE PLATFORM</div>
      <h1 class="title">{title}</h1>
      <div class="subtitle">{subtitle}</div>
    </div>
    <div class="body">
      {content_html}
    </div>
    <div class="footer">
      This is an automated transmission from <strong>SentinelAI Security Team</strong>.<br>
      For security inquiries or account support, contact: <a href="mailto:{self.support_email}">{self.support_email}</a><br>
      © {datetime.now(timezone.utc).year} SentinelAI Defense Center · <a href="{self.frontend_base_url}">Open Security Console</a>
    </div>
  </div>
</body>
</html>"""

    # -------------------------------------------------------------------------
    # 1. Welcome Email (Provisioning Isolated SOC Workspace)
    # -------------------------------------------------------------------------
    def send_welcome_email(self, user: User, verification_token: Optional[str] = None) -> Dict[str, Any]:
        """Send account creation welcome email with isolated workspace info and verification link."""
        login_url = f"{self.frontend_base_url}/login"
        verify_url = f"{self.frontend_base_url}/verify-email?token={verification_token}" if verification_token else None

        verify_section = ""
        if verify_url:
            verify_section = f"""
            <p>To verify your email address and activate your security analyst operations, click the link below:</p>
            <div style="text-align: center;">
              <a href="{verify_url}" class="btn">Verify Email Address</a>
            </div>
            <p style="font-size: 12px; color: #94a3b8; word-break: break-all;">
              Or copy and paste this link in your browser:<br>
              <a href="{verify_url}" style="color: #38bdf8;">{verify_url}</a>
            </p>
            """

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>Your analyst account on the <strong>SentinelAI Network Firewall Attack Detection System</strong> has been provisioned successfully.</p>
        
        <div class="info-card">
          <strong>Workspace & Identity Provisioning:</strong><br>
          • <strong>Username:</strong> {user.username}<br>
          • <strong>Assigned Workspace:</strong> {user.default_workspace_id or 'Private Workspace'}<br>
          • <strong>Assigned Role:</strong> {user.role.capitalize()}<br>
          • <strong>Registered Email:</strong> {user.email}<br>
          • <strong>Timestamp (UTC):</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        </div>

        {verify_section}

        <div style="text-align: center;">
          <a href="{login_url}" class="btn" style="background: #1e293b; border: 1px solid #334155;">Access SOC Portal</a>
        </div>

        <div class="security-notice">
          <strong>Security Guidance:</strong><br>
          • SentinelAI administrators will NEVER request your password.<br>
          • Keep your workspace credentials confidential.<br>
          • If you did not register this account, report it to <a href="mailto:{self.support_email}" style="color: #facc15; font-weight: 600;">{self.support_email}</a>.
        </div>
        """

        text_content = f"""Welcome to SentinelAI SOC Defense System

Hello {user.display_name or user.username},

Your analyst account has been registered on SentinelAI Network Firewall Attack Detection System.

Account Details:
- Username: {user.username}
- Registered Email: {user.email}
- Assigned Workspace: {user.default_workspace_id or 'Private Workspace'}
- Role: {user.role}
- Provisioned: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

Login Portal: {login_url}
{f'Verification URL: {verify_url}' if verify_url else ''}

SentinelAI Security Team Contact: {self.support_email}
"""
        return self._send_email(
            to_email=user.email,
            subject="Welcome to SentinelAI — SOC Account Provisioned",
            html_content=self._render_base_template("Welcome to SentinelAI", "Account Successfully Provisioned", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="welcome",
        )

    # -------------------------------------------------------------------------
    # 2. Email Verification Email
    # -------------------------------------------------------------------------
    def send_verification_email(self, user: User, verification_token: str) -> Dict[str, Any]:
        """Send cryptographically secure, high-entropy email verification link."""
        verify_url = f"{self.frontend_base_url}/verify-email?token={verification_token}"
        expire_hours = settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>A request was received to verify the email address for your SentinelAI SOC account (<strong>{user.username}</strong>).</p>

        <p>Click below to verify your email address. This single-use link will expire in <strong>{expire_hours} hours</strong>.</p>

        <div style="text-align: center;">
          <a href="{verify_url}" class="btn">Verify Email Address</a>
        </div>

        <p style="font-size: 12px; color: #94a3b8; word-break: break-all;">
          Or copy and paste this verification URL into your browser:<br>
          <a href="{verify_url}" style="color: #38bdf8;">{verify_url}</a>
        </p>

        <div class="security-notice">
          <strong>Security Notice:</strong><br>
          If you did not request this email verification, please contact SentinelAI security support immediately at <a href="mailto:{self.support_email}" style="color: #facc15;">{self.support_email}</a>.
        </div>
        """

        text_content = f"""SentinelAI — Verify Your Email Address

Hello {user.display_name or user.username},

Please verify your email address on SentinelAI SOC Platform:
{verify_url}

This single-use cryptographic token expires in {expire_hours} hours.

SentinelAI Security Team: {self.support_email}
"""
        return self._send_email(
            to_email=user.email,
            subject="SentinelAI — Verify Your Email Address",
            html_content=self._render_base_template("Verify Email Address", "Identity Confirmation Required", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="email_verification",
        )

    # -------------------------------------------------------------------------
    # 3. Verification Reminder Email
    # -------------------------------------------------------------------------
    def send_verification_reminder_email(self, user: User, verification_token: str) -> Dict[str, Any]:
        """Send verification reminder email to unverified accounts."""
        verify_url = f"{self.frontend_base_url}/verify-email?token={verification_token}"
        expire_hours = settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>This is a reminder to verify your email address for your SentinelAI SOC account (<strong>{user.username}</strong>).</p>

        <p>Unverified accounts may experience restricted telemetry operations or session limitations. Click below to verify now:</p>

        <div style="text-align: center;">
          <a href="{verify_url}" class="btn">Confirm Email Verification</a>
        </div>

        <p style="font-size: 12px; color: #94a3b8; word-break: break-all;">
          Fallback URL:<br>
          <a href="{verify_url}" style="color: #38bdf8;">{verify_url}</a>
        </p>

        <div class="security-notice">
          This single-use verification link expires in <strong>{expire_hours} hours</strong>.
        </div>
        """

        text_content = f"""SentinelAI — Reminder: Verify Your Email Address

Hello {user.display_name or user.username},

Please verify your email address for SentinelAI SOC account ({user.username}):
{verify_url}

Expires in {expire_hours} hours.
Support: {self.support_email}
"""
        return self._send_email(
            to_email=user.email,
            subject="SentinelAI — Reminder: Verify Your Email Address",
            html_content=self._render_base_template("Email Verification Reminder", "Action Required for Full SOC Access", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="verification_reminder",
        )

    # -------------------------------------------------------------------------
    # 4. First Successful Login Security Notification
    # -------------------------------------------------------------------------
    def send_first_login_email(
        self,
        user: User,
        login_time_utc: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send atomic once-per-user security notification on their first successful sign-in."""
        formatted_time = login_time_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        dashboard_url = self.frontend_base_url

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>This is a confirmation that your account has just completed its <strong>first successful sign-in</strong> to SentinelAI.</p>

        <div class="info-card">
          <strong>First Authentication Session Details:</strong><br>
          • <strong>Account:</strong> {user.username} ({user.email})<br>
          • <strong>Timestamp:</strong> {formatted_time}<br>
          {f'• <strong>Origin IP Address:</strong> {ip_address}<br>' if ip_address else ''}
          {f'• <strong>Browser / Client:</strong> {user_agent}<br>' if user_agent else ''}
          • <strong>Session State:</strong> Active Authenticated Session
        </div>

        <div style="text-align: center;">
          <a href="{dashboard_url}" class="btn">Open SentinelAI Dashboard</a>
        </div>

        <div class="security-notice">
          <strong>Security Advisory:</strong><br>
          If you performed this login, no action is required.<br>
          If you did <strong>NOT</strong> initiate this session, your credentials may be compromised. Please reset your password immediately and contact support at <a href="mailto:{self.support_email}" style="color: #facc15;">{self.support_email}</a>.
        </div>
        """

        text_content = f"""Security Alert: New Sign-In to Your SentinelAI Account

Hello {user.display_name or user.username},

Your account completed its first successful sign-in to SentinelAI.

Session Details:
- Username: {user.username}
- Timestamp: {formatted_time}
{f'- Origin IP: {ip_address}' if ip_address else ''}
{f'- Client: {user_agent}' if user_agent else ''}

Dashboard: {dashboard_url}

If you did not perform this login, contact {self.support_email} immediately.
"""
        return self._send_email(
            to_email=user.email,
            subject="Security Alert: New Sign-In to Your SentinelAI Account",
            html_content=self._render_base_template("First Login Detected", "Security Authentication Alert", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="first_login",
        )

    # -------------------------------------------------------------------------
    # 5. Password Reset Email
    # -------------------------------------------------------------------------
    def send_password_reset_email(self, user: User, reset_token: str) -> Dict[str, Any]:
        """Send password reset link containing a single-use token."""
        reset_url = f"{self.frontend_base_url}/reset-password?token={reset_token}"
        expire_minutes = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>We received a request to reset the password for your SentinelAI account (<strong>{user.username}</strong>).</p>

        <p>Click the button below to establish a new password. This single-use link will expire in <strong>{expire_minutes} minutes</strong>.</p>

        <div style="text-align: center;">
          <a href="{reset_url}" class="btn" style="background: #dc2626;">Reset Account Password</a>
        </div>

        <p style="font-size: 12px; color: #94a3b8; word-break: break-all;">
          Or copy and paste this URL directly into your browser:<br>
          <a href="{reset_url}" style="color: #38bdf8;">{reset_url}</a>
        </p>

        <div class="security-notice">
          <strong>Security Advisory:</strong><br>
          • SentinelAI will never send your password or password hash over email.<br>
          • If you did not request a password reset, you can safely ignore this email. Your existing credentials remain secure.
        </div>
        """

        text_content = f"""SentinelAI — Password Reset Request

Hello {user.display_name or user.username},

We received a request to reset your SentinelAI password.

Reset URL: {reset_url}
(Expires in {expire_minutes} minutes, single-use only)

If you did not request this, please ignore this email.
Support: {self.support_email}
"""
        return self._send_email(
            to_email=user.email,
            subject="SentinelAI — Password Reset Instructions",
            html_content=self._render_base_template("Password Reset Request", "Security Authentication Verification", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="password_reset",
        )

    # -------------------------------------------------------------------------
    # 6. Account Security Alert Email
    # -------------------------------------------------------------------------
    def send_security_alert_email(
        self,
        user: User,
        action_name: str,
        details: str,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send critical security notification when account credentials, email, or settings change."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>A critical security action was recently performed on your SentinelAI account:</p>

        <div class="info-card">
          <strong>Security Action Details:</strong><br>
          • <strong>Action:</strong> {action_name}<br>
          • <strong>Details:</strong> {details}<br>
          • <strong>Timestamp (UTC):</strong> {now_str}<br>
          {f'• <strong>Origin IP:</strong> {ip_address}<br>' if ip_address else ''}
        </div>

        <div class="security-notice">
          If you performed this action, no further action is necessary.<br>
          If you did <strong>NOT</strong> authorize this change, please contact SentinelAI security support immediately at <a href="mailto:{self.support_email}" style="color: #facc15;">{self.support_email}</a>.
        </div>
        """

        text_content = f"""SentinelAI — Account Security Alert

Hello {user.display_name or user.username},

A critical security action occurred on your account:
Action: {action_name}
Details: {details}
Timestamp: {now_str}
{f'Origin IP: {ip_address}' if ip_address else ''}

If unauthorized, contact {self.support_email} immediately.
"""
        return self._send_email(
            to_email=user.email,
            subject=f"SentinelAI Security Alert — {action_name}",
            html_content=self._render_base_template("Account Security Alert", "Important Account Activity", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="security_alert",
        )

    # -------------------------------------------------------------------------
    # 7. Support Message Receipt & Staff Notification
    # -------------------------------------------------------------------------
    def send_support_receipt_email(
        self,
        user_email: str,
        ticket_id: str,
        subject: str,
        category: str,
        user_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Acknowledge receipt of a support inquiry to the user."""
        content_html = f"""
        <p>Hello <strong>{user_name or 'Analyst'}</strong>,</p>
        <p>We have received your support message regarding <strong>{subject}</strong>. Your ticket identifier is <code>{ticket_id}</code>.</p>

        <div class="info-card">
          <strong>Ticket Information:</strong><br>
          • <strong>Reference ID:</strong> {ticket_id}<br>
          • <strong>Category:</strong> {category}<br>
          • <strong>Subject:</strong> {subject}<br>
          • <strong>Assigned Team:</strong> SentinelAI SOC Security & Support<br>
          • <strong>Designated Support:</strong> <a href="mailto:{self.support_email}">{self.support_email}</a>
        </div>

        <p>Our security engineers review inquiries in priority order. For urgent access issues or incident escalations, reply directly to this email or contact <a href="mailto:{self.support_email}">{self.support_email}</a>.</p>
        """

        text_content = f"""SentinelAI Support — Ticket Received [{ticket_id}]

Hello {user_name or 'Analyst'},

We received your support inquiry regarding '{subject}'.
Ticket ID: {ticket_id}
Category: {category}
Direct Support Contact: {self.support_email}

SentinelAI Security Team
"""
        return self._send_email(
            to_email=user_email,
            subject=f"SentinelAI Support Receipt [{ticket_id}] — {subject}",
            html_content=self._render_base_template("Support Inquiry Received", f"Ticket Reference: {ticket_id}", content_html),
            text_content=text_content,
            notification_type="support_acknowledgment",
        )

    def send_support_staff_notification(
        self,
        ticket_id: str,
        sender_email: str,
        subject: str,
        category: str,
        message: str,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Dispatch notification of new user inquiry to designated support address (revenreven287@gmail.com)."""
        content_html = f"""
        <p>A new support request has been submitted through the SentinelAI Security Console:</p>

        <div class="info-card">
          <strong>Ticket Details:</strong><br>
          • <strong>Ticket ID:</strong> {ticket_id}<br>
          • <strong>Sender Email:</strong> <a href="mailto:{sender_email}">{sender_email}</a><br>
          • <strong>User ID:</strong> {user_id or 'Anonymous / Unauthenticated'}<br>
          • <strong>Category:</strong> {category}<br>
          • <strong>Subject:</strong> {subject}<br>
          • <strong>Submitted:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        </div>

        <p><strong>Message Content:</strong></p>
        <div style="background: #0b0f17; border: 1px solid #1e293b; padding: 14px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; font-size: 13px;">
{message}
        </div>
        """

        text_content = f"""New SentinelAI Support Ticket [{ticket_id}]

From: {sender_email}
User ID: {user_id}
Category: {category}
Subject: {subject}

Message:
{message}
"""
        return self._send_email(
            to_email=self.support_email,
            subject=f"[SentinelAI Support] [{category}] {subject} ({ticket_id})",
            html_content=self._render_base_template("New Support Ticket", f"Ticket ID: {ticket_id}", content_html),
            text_content=text_content,
            notification_type="support_inquiry",
        )

    # -------------------------------------------------------------------------
    # Core Delivery Engine
    # -------------------------------------------------------------------------
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        user_id: Optional[int] = None,
        workspace_id: Optional[str] = None,
        notification_type: str = "generic",
    ) -> Dict[str, Any]:
        """
        Internal delivery method with robust error handling and audit logging.
        Never exposes SMTP passwords in logs or exception messages.
        If SMTP is not configured in backend environment:
          - Records log entry with status 'awaiting_configuration'
          - Returns structured dict with status 'awaiting_configuration'
        If configured:
          - Connects via STARTTLS (587) or SSL (465)
          - Dispatches message
          - Records log entry with status 'delivered'
        """
        now = datetime.now(timezone.utc)

        def record_audit(
            status_val: str,
            error_msg: Optional[str] = None,
            provider_status: Optional[str] = None,
            attempt_count: int = 1,
        ):
            try:
                if self.delivery_repo:
                    log_entry = EmailDeliveryLog(
                        user_id=user_id,
                        workspace_id=workspace_id,
                        recipient_email=to_email,
                        sender=self.from_email,
                        subject=subject,
                        template_name=notification_type,
                        notification_type=notification_type,
                        provider="smtp",
                        provider_response_status=provider_status,
                        attempt_count=attempt_count,
                        status=status_val,
                        error_message=error_msg,
                        attempted_at=now,
                        created_at=now,
                        updated_at=now,
                    )
                    self.delivery_repo.record_delivery(log_entry)
            except Exception as audit_err:
                logger.warning(f"[EmailService] Failed to record email delivery log: {audit_err}")

        # Check configuration
        if not self.is_configured():
            unconf_msg = "SMTP unconfigured in environment (SMTP_PASSWORD not configured on host)"
            logger.info(
                f"[EmailService] SMTP unconfigured. Email '{subject}' to <{to_email}> recorded as awaiting_configuration."
            )
            record_audit("awaiting_configuration", unconf_msg, provider_status="unconfigured")
            return {
                "status": "awaiting_configuration",
                "message": (
                    f"Email delivery service is awaiting SMTP credentials on the hosting provider. "
                    f"Set SMTP_PASSWORD for '{self.from_email}' in your backend environment settings."
                ),
                "recipient": to_email,
                "subject": subject,
                "sender": self.from_email,
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Reply-To"] = self.support_email

            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=15)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)

            if self.use_tls and not self.use_ssl:
                server.starttls()

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            send_result = server.sendmail(self.from_email, [to_email], msg.as_string())
            server.quit()

            logger.info(f"[EmailService] Delivered '{subject}' to <{to_email}> via SMTP.")
            record_audit("delivered", provider_status="250_OK")
            return {
                "status": "delivered",
                "message": "Email dispatched successfully",
                "recipient": to_email,
                "subject": subject,
                "sender": self.from_email,
            }
        except smtplib.SMTPAuthenticationError as auth_err:
            sanitized_err = f"SMTP Authentication failed for {self.smtp_username}. Check Google App Password."
            logger.error(f"[EmailService] {sanitized_err}")
            record_audit("failed", sanitized_err, provider_status="auth_error")
            return {
                "status": "failed",
                "message": sanitized_err,
                "recipient": to_email,
                "subject": subject,
            }
        except Exception as e:
            err_str = str(e)
            # Never leak password in case it was in error string
            if self.smtp_password:
                err_str = err_str.replace(self.smtp_password, "[REDACTED]")
            logger.error(f"[EmailService] SMTP delivery failed to <{to_email}>: {err_str}", exc_info=False)
            record_audit("failed", err_str, provider_status="network_error")
            return {
                "status": "failed",
                "message": f"SMTP delivery failed: {err_str}",
                "recipient": to_email,
                "subject": subject,
            }
