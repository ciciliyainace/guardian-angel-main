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
    def __init__(self, db: Optional[Any] = None):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.use_ssl = settings.SMTP_USE_SSL
        self.from_email = settings.MAIL_FROM_EMAIL
        self.from_name = settings.MAIL_FROM_NAME
        self.frontend_base_url = settings.FRONTEND_BASE_URL.rstrip("/")
        self.db = db
        self.delivery_repo = EmailDeliveryRepository(db) if db is not None else None

    def is_configured(self) -> bool:
        """Check if SMTP credentials are fully configured."""
        return bool(self.smtp_host and self.smtp_host.strip() and self.from_email)

    def _render_base_template(self, title: str, subtitle: str, content_html: str) -> str:
        """Render high-tech cyber defense dark HTML email template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #0d1117;
      color: #c9d1d9;
      margin: 0;
      padding: 24px;
      line-height: 1.6;
    }}
    .email-container {{
      max-width: 600px;
      margin: 0 auto;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }}
    .header {{
      background: linear-gradient(135deg, #1f293d 0%, #111827 100%);
      border-bottom: 2px solid #38bdf8;
      padding: 28px;
      text-align: center;
    }}
    .logo-badge {{
      display: inline-block;
      font-family: monospace;
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
      color: #ffffff;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .subtitle {{
      margin: 6px 0 0 0;
      color: #8b949e;
      font-size: 13px;
    }}
    .body {{
      padding: 28px;
      color: #c9d1d9;
      font-size: 14px;
    }}
    .btn {{
      display: inline-block;
      background: #2563eb;
      color: #ffffff !important;
      text-decoration: none;
      padding: 12px 24px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 6px;
      text-align: center;
      margin: 18px 0;
      letter-spacing: 0.2px;
    }}
    .btn:hover {{
      background: #1d4ed8;
    }}
    .info-card {{
      background: #0d1117;
      border: 1px solid #30363d;
      border-left: 3px solid #38bdf8;
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
      color: #fbbf24;
    }}
    .footer {{
      padding: 20px;
      border-top: 1px solid #21262d;
      text-align: center;
      font-size: 12px;
      color: #6e7681;
      background: #0d1117;
    }}
    .footer a {{
      color: #58a6ff;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <div class="logo-badge">SENTINEL AI — DEFENSE SYSTEM</div>
      <h1 class="title">{title}</h1>
      <div class="subtitle">{subtitle}</div>
    </div>
    <div class="body">
      {content_html}
    </div>
    <div class="footer">
      This is an automated security transmission from SentinelAI.<br>
      © {datetime.now(timezone.utc).year} SentinelAI SOC. All rights reserved.<br>
      <a href="{self.frontend_base_url}">Open Security Console</a>
    </div>
  </div>
</body>
</html>"""

    def send_welcome_email(self, user: User, verification_token: Optional[str] = None) -> Dict[str, Any]:
        """Send account creation welcome email with optional verification link."""
        login_url = f"{self.frontend_base_url}/login"
        verify_url = f"{self.frontend_base_url}/verify-email?token={verification_token}" if verification_token else None

        verify_section = ""
        if verify_url:
            verify_section = f"""
            <p>To verify your email address and enable full administrative or analyst operations, please click below:</p>
            <div style="text-align: center;">
              <a href="{verify_url}" class="btn">Verify Email Address</a>
            </div>
            <p style="font-size: 12px; color: #8b949e; word-break: break-all;">
              Or copy and paste this link in your browser: <br>
              <a href="{verify_url}" style="color: #38bdf8;">{verify_url}</a>
            </p>
            """

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>Your account on <strong>SentinelAI AI-Powered Network Firewall Attack Detection System</strong> has been successfully registered.</p>
        
        <div class="info-card">
          <strong>Account Details:</strong><br>
          • <strong>Username:</strong> {user.username}<br>
          • <strong>Registered Email:</strong> {user.email}<br>
          • <strong>Assigned Role:</strong> {user.role.capitalize()}<br>
          • <strong>Created At (UTC):</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        </div>

        {verify_section}

        <div style="text-align: center;">
          <a href="{login_url}" class="btn" style="background: #334155;">Go to SentinelAI Login</a>
        </div>

        <div class="security-notice">
          <strong>Security Guidance:</strong><br>
          • Always ensure you access SentinelAI via an authorized HTTPS domain.<br>
          • SentinelAI administrators will NEVER ask for your password.<br>
          • Never share your credentials or multi-factor authentication codes with anyone.<br>
          • If you did not create this account, please notify your SOC security lead immediately.
        </div>
        """

        text_content = f"""Welcome to SentinelAI — Account Created

Hello {user.display_name or user.username},

Your account has been registered on SentinelAI AI-Powered Network Firewall Attack Detection System.

Account Details:
- Username: {user.username}
- Email: {user.email}
- Role: {user.role}
- Created: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

Login URL: {login_url}
{f'Verification URL: {verify_url}' if verify_url else ''}

Security Notice:
SentinelAI administrators will never ask for your password. If you did not create this account, contact SOC administrators immediately.
"""
        return self._send_email(
            to_email=user.email,
            subject="Welcome to SentinelAI — Account Created",
            html_content=self._render_base_template("Welcome to SentinelAI", "Account Successfully Provisioned", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="welcome",
        )

    def send_first_login_email(self, user: User, login_time_utc: datetime, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Send notification on the user's very first successful login."""
        formatted_time = login_time_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        dashboard_url = self.frontend_base_url

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>This is a confirmation that your account has just authenticated successfully for the <strong>first time</strong> on SentinelAI.</p>

        <div class="info-card">
          <strong>First Authentication Event:</strong><br>
          • <strong>Username:</strong> {user.username}<br>
          • <strong>Timestamp (UTC):</strong> {formatted_time}<br>
          {f'• <strong>Origin IP Address:</strong> {ip_address}<br>' if ip_address else ''}
          • <strong>Security Status:</strong> Authenticated Active Session
        </div>

        <div style="text-align: center;">
          <a href="{dashboard_url}" class="btn">Open SentinelAI Dashboard</a>
        </div>

        <div class="security-notice">
          <strong>Security Notice:</strong><br>
          If you performed this login, no further action is required.<br>
          If you did <strong>NOT</strong> authorize this session, change your password immediately and contact your cybersecurity response team.
        </div>
        """

        text_content = f"""SentinelAI — First Successful Login Notification

Hello {user.display_name or user.username},

Your SentinelAI account logged in successfully for the first time.

Details:
- Username: {user.username}
- Timestamp: {formatted_time}
{f'- Origin IP: {ip_address}' if ip_address else ''}

Access Dashboard: {dashboard_url}

If you did not perform this login, contact your security administrator immediately.
"""
        return self._send_email(
            to_email=user.email,
            subject="SentinelAI — First Successful Login Notification",
            html_content=self._render_base_template("First Login Detected", "Security Notification", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="first_login",
        )

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

        <p style="font-size: 12px; color: #8b949e; word-break: break-all;">
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
(This link expires in {expire_minutes} minutes and can only be used once.)

If you did not request this, please ignore this email.
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

    def send_verification_email(self, user: User, verification_token: str) -> Dict[str, Any]:
        """Send standalone email verification link."""
        verify_url = f"{self.frontend_base_url}/verify-email?token={verification_token}"
        expire_hours = settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS

        content_html = f"""
        <p>Hello <strong>{user.display_name or user.username}</strong>,</p>
        <p>Please verify your email address to confirm your identity on <strong>SentinelAI</strong>.</p>

        <div style="text-align: center;">
          <a href="{verify_url}" class="btn">Verify Email Address</a>
        </div>

        <p style="font-size: 12px; color: #8b949e; word-break: break-all;">
          Or open this link: <br>
          <a href="{verify_url}" style="color: #38bdf8;">{verify_url}</a>
        </p>

        <div class="security-notice">
          This link will expire in {expire_hours} hours.
        </div>
        """

        text_content = f"""SentinelAI — Email Verification

Hello {user.display_name or user.username},

Please verify your email address on SentinelAI:
{verify_url}

This link expires in {expire_hours} hours.
"""
        return self._send_email(
            to_email=user.email,
            subject="SentinelAI — Verify Your Email Address",
            html_content=self._render_base_template("Verify Email Address", "Identity Confirmation", content_html),
            text_content=text_content,
            user_id=user.id,
            workspace_id=user.default_workspace_id,
            notification_type="email_verification",
        )

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
        Internal delivery method. If SMTP is unconfigured, logs and returns 'awaiting_configuration'.
        If configured, connects to SMTP server with TLS and dispatches the email.
        Logs every attempt in email_delivery_logs collection.
        """
        def record_audit(status: str, error_msg: Optional[str] = None):
            try:
                if self.delivery_repo:
                    log_entry = EmailDeliveryLog(
                        user_id=user_id,
                        workspace_id=workspace_id,
                        recipient_email=to_email,
                        notification_type=notification_type,
                        provider="smtp",
                        status=status,
                        error_message=error_msg,
                        attempted_at=datetime.now(timezone.utc),
                    )
                    self.delivery_repo.record_delivery(log_entry)
            except Exception as audit_err:
                logger.warning(f"[EmailService] Failed to record email audit log: {audit_err}")

        if not self.is_configured():
            logger.info(
                f"[EmailService] SMTP unconfigured. Email '{subject}' to <{to_email}> queued as awaiting_configuration."
            )
            record_audit("awaiting_configuration", "SMTP unconfigured in environment")
            return {
                "status": "awaiting_configuration",
                "message": "Email delivery service is awaiting SMTP credentials in backend/.env",
                "recipient": to_email,
                "subject": subject,
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=12)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=12)

            if self.use_tls and not self.use_ssl:
                server.starttls()

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            server.sendmail(self.from_email, [to_email], msg.as_string())
            server.quit()

            logger.info(f"[EmailService] Successfully delivered '{subject}' to <{to_email}>.")
            record_audit("delivered")
            return {
                "status": "delivered",
                "message": "Email dispatched successfully",
                "recipient": to_email,
                "subject": subject,
            }
        except Exception as e:
            logger.error(f"[EmailService] Failed to send email to <{to_email}>: {e}", exc_info=False)
            record_audit("failed", str(e))
            return {
                "status": "failed",
                "message": f"SMTP delivery failed: {str(e)}",
                "recipient": to_email,
                "subject": subject,
            }
