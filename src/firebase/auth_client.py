"""
Firebase Authentication Client
"""

import time
from datetime import timedelta
from typing import Any
import firebase_admin
from pydantic import SecretStr
from firebase_admin import auth as fb_auth
from firebase_admin import credentials
from src.firebase.constants import MAX_SESSION_TTL, MIN_SESSION_TTL
from src.shared.cookie import CookieSettings
from src.firebase.exceptions import (
    InvalidCredential,
    StaleSignIn,
    handle_firebase_auth_error,
)
from src.config import settings
from src.firebase.utils import normalize_private_key


class FirebaseAuthClient:

    def __init__(
        self,
        *,
        project_id: str = settings.FIREBASE_PROJECT_ID,
        client_email: str = settings.FIREBASE_CLIENT_EMAIL,
        private_key: SecretStr = settings.FIREBASE_PRIVATE_KEY,
        session_ttl: timedelta = timedelta(days=14),
        max_auth_age_seconds: int = 5 * 60,
        cookie: CookieSettings | None = None,
        app_name: str = settings.FIREBASE_APP_NAME,
    ):

        if not (MIN_SESSION_TTL <= session_ttl <= MAX_SESSION_TTL):
            raise ValueError(
                f"session_ttl must be between {MIN_SESSION_TTL} and "
                f"{MAX_SESSION_TTL}; got {session_ttl}"
            )

        self.project_id = project_id
        self.session_ttl = session_ttl
        self.max_auth_age_seconds = max_auth_age_seconds
        self.cookie = cookie or CookieSettings()
        self._app = self._init_app(
            project_id=project_id,
            client_email=client_email,
            private_key=private_key,
            app_name=app_name,
        )

    @staticmethod
    def _init_app(
        *, project_id: str, client_email: str, private_key: SecretStr, app_name: str
    ) -> firebase_admin.App:
        "@staticmethod means it is living inside the class but does not touch the instance"

        try:
            return firebase_admin.get_app(app_name)
        except ValueError:
            pass  # not initialised yet

        cert = credentials.Certificate(
            {
                "type": "service_account",
                "project_id": project_id,
                "client_email": client_email,
                "private_key": normalize_private_key(private_key.get_secret_value()),
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        try:
            return firebase_admin.initialize_app(cert, name=app_name)
        except ValueError:
            # Lost an init race (uvicorn reload, threaded startup).
            return firebase_admin.get_app(app_name)

    # === Client helpers ==============================================

    # Verify ID token
    @handle_firebase_auth_error
    def verify_id_token(
        self, id_token: str, *, check_revoked: bool = True
    ) -> dict[str, Any]:
        """Verify a client-minted ID token (the ``Authorization: Bearer`` path)."""
        if not id_token:
            raise InvalidCredential(message="No token provided")

        return fb_auth.verify_id_token(
            id_token, app=self._app, check_revoked=check_revoked
        )

    # === Methods for authentication service ==========================

    # Create firebase session
    @handle_firebase_auth_error
    def create_session(self, *, id_token: str) -> tuple[str, dict[str, Any]]:
        """Mint a session cookie, returning it with the token's verified claims.

        The claims are returned rather than discarded because they are the only
        trustworthy source of the caller's identity — the request body is not.
        """
        decoded = self.verify_id_token(id_token, check_revoked=True)

        auth_time = decoded.get("auth_time")
        if auth_time is None or time.time() - auth_time > self.max_auth_age_seconds:
            raise StaleSignIn()

        cookie = fb_auth.create_session_cookie(
            id_token, expires_in=self.session_ttl, app=self._app
        )
        return (cookie.decode() if isinstance(cookie, bytes) else cookie), decoded
