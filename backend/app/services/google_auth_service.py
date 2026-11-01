from typing import Optional, Dict, Any, Tuple
import httpx
from datetime import datetime, timezone
from pymongo.database import Database
from app.core.config import settings
from app.core.logging_config import logger
from app.models.user import User
from app.repositories.user_repository import UserRepository


class GoogleAuthService:
    TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def is_configured(self) -> bool:
        """Check if Google OAuth credentials are fully provided."""
        return bool(self.client_id and self.client_id.strip() and self.client_secret and self.client_secret.strip())

    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate Google OAuth 2.0 authorization URL for OpenID Connect flow.
        Returns (configured, auth_url, error_message).
        """
        if not self.client_id or not self.client_id.strip():
            return False, None, "Google OAuth 2.0 credentials (GOOGLE_CLIENT_ID) are not configured in backend/.env"

        import urllib.parse
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
        }
        if state:
            params["state"] = state

        query = urllib.parse.urlencode(params)
        auth_url = f"{self.AUTH_ENDPOINT}?{query}"
        return True, auth_url, None

    def verify_token_or_code(
        self,
        id_token: Optional[str] = None,
        code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify Google identity securely.
        Accepts either an OpenID Connect ID token directly or an OAuth authorization code to exchange.
        Verifies:
        - Audience matches GOOGLE_CLIENT_ID
        - Issuer is Google
        - Email is verified by Google
        - Token is not expired
        Raises ValueError on verification failure.
        """
        if not self.is_configured():
            raise ValueError(
                "Google Sign-In is unavailable: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured in backend/.env"
            )

        token_to_verify = id_token

        # If authorization code was provided, exchange it for tokens first
        if code and not token_to_verify:
            target_redirect_uri = redirect_uri or self.redirect_uri
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        self.TOKEN_ENDPOINT,
                        data={
                            "code": code,
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "redirect_uri": target_redirect_uri,
                            "grant_type": "authorization_code",
                        },
                    )
                    if resp.status_code != 200:
                        logger.error(f"[GoogleAuth] Token exchange failed ({resp.status_code}): {resp.text}")
                        raise ValueError("Failed to exchange Google authorization code for authentication tokens.")
                    token_data = resp.json()
                    token_to_verify = token_data.get("id_token")
            except httpx.RequestError as exc:
                logger.error(f"[GoogleAuth] Network error exchanging code: {exc}")
                raise ValueError("Could not connect to Google authentication service.")

        if not token_to_verify:
            raise ValueError("No Google ID token or valid authorization code was provided.")

        # Verify Google ID token via Google's tokeninfo endpoint
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self.TOKENINFO_URL, params={"id_token": token_to_verify})
                if resp.status_code != 200:
                    logger.warning(f"[GoogleAuth] Token validation rejected by Google ({resp.status_code}): {resp.text}")
                    raise ValueError("Invalid, expired, or malformed Google ID token.")
                payload = resp.json()
        except httpx.RequestError as exc:
            logger.error(f"[GoogleAuth] Network error calling tokeninfo: {exc}")
            raise ValueError("Could not reach Google verification servers.")

        # Audience Verification
        aud = payload.get("aud")
        if aud != self.client_id:
            logger.warning(f"[GoogleAuth] Token audience mismatch: {aud} != {self.client_id}")
            raise ValueError("Google token audience mismatch.")

        # Issuer Verification
        iss = payload.get("iss")
        if iss not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("Google token issuer is not trusted.")

        # Email Verification flag check
        email_verified = payload.get("email_verified")
        if isinstance(email_verified, str):
            email_verified = email_verified.lower() == "true"
        if not email_verified:
            raise ValueError("Google account email address is not verified by Google.")

        email = payload.get("email")
        sub = payload.get("sub")
        if not email or not sub:
            raise ValueError("Google token does not contain a valid email or subject identifier.")

        return {
            "google_sub": str(sub),
            "email": email.strip().lower(),
            "name": payload.get("name", ""),
            "picture": payload.get("picture", ""),
            "email_verified": True,
        }

    def process_google_login(
        self,
        db: Database,
        verified_payload: Dict[str, Any],
    ) -> Tuple[User, bool, bool]:
        """
        Look up or create user based on verified Google payload.
        Rules:
        - If user with matching `google_sub` exists: sign in.
        - If user with matching email exists:
          - If already has Google provider or google_sub matches: sign in.
          - If only has password provider and unlinked: DO NOT automatically merge without verified ownership.
            Raise ValueError requiring existing user to authenticate and link.
        - If neither exists: create new user with google_sub, role='analyst', auth_providers=['google'].
        Returns (user, is_new_account, is_first_login).
        """
        repo = UserRepository(db)
        google_sub = verified_payload["google_sub"]
        email = verified_payload["email"]
        name = verified_payload.get("name", "")

        # 1. Check existing user by google_sub
        user = repo.get_by_google_sub(google_sub)
        if user:
            is_first_login = user.first_login_at is None
            return user, False, is_first_login

        # 2. Check existing user by email
        existing_email_user = repo.get_by_email(email)
        if existing_email_user:
            # If account has google provider already linked
            if "google" in existing_email_user.auth_providers or existing_email_user.google_sub == google_sub:
                linked_user = repo.link_google_account(existing_email_user.id, google_sub) or existing_email_user
                is_first_login = linked_user.first_login_at is None
                return linked_user, False, is_first_login

            # Security requirement: Do not automatically link an existing password account simply because email matches
            # without prior verification
            raise ValueError(
                f"An account with email '{email}' already exists with password authentication. "
                "For your security, please sign in with your password first to link Google Sign-In in Account Settings."
            )

        # 3. Create brand new account for verified Google user
        # Generate base username from email or name
        base_username = email.split("@")[0].replace(".", "-").replace("_", "-")
        # Ensure alphanumeric and hyphens
        import re
        base_username = re.sub(r"[^a-zA-Z0-9\-]", "", base_username)[:40] or "google-user"

        candidate_username = base_username
        suffix = 1
        while repo.get_by_username(candidate_username) is not None:
            candidate_username = f"{base_username}-{suffix}"
            suffix += 1

        new_user = User(
            email=email,
            username=candidate_username,
            display_name=name or candidate_username,
            hashed_password="",  # No password for Google-only authentication
            role="analyst",  # Standard analyst role, never admin automatically
            auth_providers=["google"],
            google_sub=google_sub,
            email_verified=True,  # Verified by Google OIDC
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        created_user = repo.create(new_user)
        return created_user, True, True
