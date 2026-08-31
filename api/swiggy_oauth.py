"""Swiggy OAuth 2.1/PKCE flow for the future production MCP connection."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import HTTPException
from cryptography.fernet import Fernet, InvalidToken
from pymongo import MongoClient


AUTHORIZATION_URL = os.getenv("SWIGGY_AUTHORIZATION_URL", "https://mcp.swiggy.com/auth/authorize")
TOKEN_URL = os.getenv("SWIGGY_TOKEN_URL", "https://mcp.swiggy.com/auth/token")


@dataclass(frozen=True)
class PendingAuthorization:
    user_id: str
    verifier: str
    expires_at: float


class SwiggyOAuthStore:
    def __init__(self, state_ttl_seconds: int = 10 * 60) -> None:
        self._state_ttl_seconds = state_ttl_seconds
        self._states: dict[str, PendingAuthorization] = {}
        self._tokens: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_state(self, user_id: str) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        with self._lock:
            self._purge_locked()
            self._states[state] = PendingAuthorization(
                user_id=user_id,
                verifier=verifier,
                expires_at=time.time() + self._state_ttl_seconds,
            )
        return state, verifier

    def consume_state(self, state: str) -> PendingAuthorization:
        with self._lock:
            self._purge_locked()
            pending = self._states.pop(state, None)
        if pending is None:
            raise ValueError("OAuth state is invalid or expired")
        return pending

    def save_token(self, user_id: str, token_response: dict[str, Any]) -> None:
        token = token_response.get("access_token")
        if not token:
            raise ValueError("Swiggy token response did not contain an access token")
        stored = dict(token_response)
        stored["stored_at"] = time.time()
        with self._lock:
            self._tokens[user_id] = stored

    def access_token_for(self, user_id: str) -> Optional[str]:
        with self._lock:
            record = self._tokens.get(user_id)
            return str(record["access_token"]) if record and record.get("access_token") else None

    def _purge_locked(self) -> None:
        now = time.time()
        for state in [key for key, value in self._states.items() if value.expires_at < now]:
            self._states.pop(state, None)


class MongoSwiggyOAuthStore:
    """Multi-worker OAuth state with encrypted-at-rest token storage."""

    def __init__(self, mongo_uri: str, database_name: str, encryption_key: str) -> None:
        if not encryption_key:
            raise RuntimeError(
                "SWIGGY_TOKEN_ENCRYPTION_KEY is required for MongoDB OAuth storage"
            )
        try:
            self._cipher = Fernet(encryption_key.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise RuntimeError("SWIGGY_TOKEN_ENCRYPTION_KEY must be a valid Fernet key") from exc
        database = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)[database_name]
        self._states = database.swiggy_oauth_states
        self._tokens = database.swiggy_oauth_tokens
        self._states.create_index("expires_at")

    def create_state(self, user_id: str) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        self._states.insert_one(
            {
                "_id": state,
                "user_id": user_id,
                "verifier": verifier,
                "expires_at": time.time() + 10 * 60,
            }
        )
        return state, verifier

    def consume_state(self, state: str) -> PendingAuthorization:
        pending = self._states.find_one_and_delete(
            {"_id": state, "expires_at": {"$gte": time.time()}}
        )
        if pending is None:
            raise ValueError("OAuth state is invalid or expired")
        return PendingAuthorization(
            user_id=str(pending["user_id"]),
            verifier=str(pending["verifier"]),
            expires_at=float(pending["expires_at"]),
        )

    def save_token(self, user_id: str, token_response: dict[str, Any]) -> None:
        if not token_response.get("access_token"):
            raise ValueError("Swiggy token response did not contain an access token")
        payload = json.dumps(token_response).encode("utf-8")
        self._tokens.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "encrypted_token": self._cipher.encrypt(payload).decode("ascii"),
                    "stored_at": time.time(),
                }
            },
            upsert=True,
        )

    def access_token_for(self, user_id: str) -> Optional[str]:
        record = self._tokens.find_one({"_id": user_id}, {"encrypted_token": 1})
        if not record:
            return None
        try:
            payload = self._cipher.decrypt(record["encrypted_token"].encode("ascii"))
            token_response = json.loads(payload)
        except (InvalidToken, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Stored Swiggy token could not be decrypted") from exc
        token = token_response.get("access_token")
        return str(token) if token else None


def create_oauth_store() -> SwiggyOAuthStore | MongoSwiggyOAuthStore:
    backend = os.getenv("GANGU_STATE_BACKEND", "memory").strip().lower()
    if backend == "memory":
        return SwiggyOAuthStore()
    if backend == "mongodb":
        mongo_uri = os.getenv("MONGODB_URI", "").strip()
        if not mongo_uri:
            raise RuntimeError("MONGODB_URI is required when GANGU_STATE_BACKEND=mongodb")
        return MongoSwiggyOAuthStore(
            mongo_uri,
            os.getenv("MONGODB_DATABASE", "gangu"),
            os.getenv("SWIGGY_TOKEN_ENCRYPTION_KEY", ""),
        )
    raise RuntimeError(f"Unsupported GANGU_STATE_BACKEND: {backend}")


swiggy_oauth_store = create_oauth_store()


def _configuration() -> tuple[str, str]:
    client_id = os.getenv("SWIGGY_CLIENT_ID", "").strip()
    redirect_uri = os.getenv("SWIGGY_REDIRECT_URI", "").strip()
    parsed = urlparse(redirect_uri)
    if not client_id or parsed.scheme != "https" or not parsed.netloc:
        raise HTTPException(
            status_code=503,
            detail="Swiggy OAuth requires SWIGGY_CLIENT_ID and an HTTPS SWIGGY_REDIRECT_URI",
        )
    return client_id, redirect_uri


def create_authorization_url(user_id: str) -> str:
    client_id, redirect_uri = _configuration()
    state, verifier = swiggy_oauth_store.create_state(user_id)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    parameters = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
        'state': state,
        'scope': 'mcp:tools',
    }
    return f"{AUTHORIZATION_URL}?{urlencode(parameters)}"


async def exchange_callback(code: str, state: str) -> str:
    client_id, redirect_uri = _configuration()
    try:
        pending = swiggy_oauth_store.consume_state(state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "code_verifier": pending.verifier,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                },
            )
            response.raise_for_status()
            token_response = response.json()
        swiggy_oauth_store.save_token(pending.user_id, token_response)
        return pending.user_id
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Swiggy token exchange failed") from exc
