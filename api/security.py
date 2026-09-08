"""Authentication helpers for the GANGU API.

Firebase ID tokens protect HTTP endpoints. WebSockets use short-lived,
single-use tickets so long-lived ID tokens are not placed in socket URLs.
"""
from __future__ import annotations

import os
import json
import logging
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException, WebSocket


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


AUTH_REQUIRED = _env_flag("GANGU_AUTH_REQUIRED", True)
DEFAULT_FIREBASE_PROJECT_ID = "gangu-adffd"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthenticatedUser:
    uid: str
    email: Optional[str] = None
    phone_number: Optional[str] = None


def _verify_firebase_token(token: str) -> AuthenticatedUser:
    try:
        # Firebase's web project id is public configuration. Keeping the known
        # GANGU id as a local fallback lets verification work before a root
        # .env has been filled in. Deployments should still set the variable.
        project_id = os.getenv("FIREBASE_PROJECT_ID", DEFAULT_FIREBASE_PROJECT_ID).strip()
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if service_account_json:
            # Admin credentials permit revocation checking in production.
            import firebase_admin
            from firebase_admin import auth, credentials

            if not firebase_admin._apps:
                firebase_admin.initialize_app(
                    credential=credentials.Certificate(json.loads(service_account_json)),
                    options={"projectId": project_id},
                )
            decoded = auth.verify_id_token(token, check_revoked=True)
        else:
            # Local development and credential-free deployments can securely
            # validate signature, issuer, audience and expiry against Google's
            # Firebase public certificates. Revocation checks require Admin
            # credentials and are therefore unavailable in this branch.
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token

            decoded = id_token.verify_firebase_token(
                token,
                Request(),
                audience=project_id,
            )
        uid = decoded.get("uid") or decoded.get("sub")
        if not uid:
            raise ValueError("Firebase token does not contain a user id")
        return AuthenticatedUser(
            uid=str(uid),
            email=decoded.get("email"),
            phone_number=decoded.get("phone_number"),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Firebase ID token verification failed (%s): %s", type(exc).__name__, exc)
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token") from exc


def get_current_user(authorization: Optional[str] = Header(default=None)) -> AuthenticatedUser:
    """Validate a Firebase bearer token or use an explicit local-dev identity."""
    if not AUTH_REQUIRED:
        return AuthenticatedUser(uid="local-development-user")

    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Bearer authentication is required")
    return _verify_firebase_token(token)


class WebSocketTicketStore:
    def __init__(self, ttl_seconds: int = 60) -> None:
        self._ttl_seconds = ttl_seconds
        self._tickets: dict[str, tuple[AuthenticatedUser, float]] = {}
        self._lock = threading.Lock()

    def issue(self, user: AuthenticatedUser) -> tuple[str, int]:
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + self._ttl_seconds
        with self._lock:
            self._purge_locked()
            self._tickets[token] = (user, expires_at)
        return token, self._ttl_seconds

    def consume(self, token: str) -> Optional[AuthenticatedUser]:
        with self._lock:
            self._purge_locked()
            record = self._tickets.pop(token, None)
        if not record:
            return None
        user, expires_at = record
        return user if expires_at >= time.time() else None

    def _purge_locked(self) -> None:
        now = time.time()
        expired = [token for token, (_, expiry) in self._tickets.items() if expiry < now]
        for token in expired:
            self._tickets.pop(token, None)


ws_tickets = WebSocketTicketStore()


async def authenticate_websocket(websocket: WebSocket) -> Optional[AuthenticatedUser]:
    if not AUTH_REQUIRED:
        return AuthenticatedUser(uid="local-development-user")
    ticket = websocket.query_params.get("ticket", "")
    return ws_tickets.consume(ticket)
