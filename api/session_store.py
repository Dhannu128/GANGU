"""Thread-safe, bounded-lifetime state for active GANGU sessions and quotes.

This store provides correct single-process behavior. Production multi-worker
deployments should replace it with the same interface backed by MongoDB/Redis.
"""
from __future__ import annotations

import os
import secrets
import threading
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Optional

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError


@dataclass
class PendingQuote:
    quote_id: str
    session_id: str
    user_id: str
    products: list[dict[str, Any]]
    recommendation: dict[str, Any]
    created_at: float
    expires_at: float
    consumed: bool = False


class SessionStore:
    def __init__(self, quote_ttl_seconds: int = 10 * 60, session_ttl_seconds: int = 24 * 60 * 60) -> None:
        self._quote_ttl_seconds = quote_ttl_seconds
        self._session_ttl_seconds = session_ttl_seconds
        self._owners: dict[str, tuple[str, float]] = {}
        self._quotes: dict[str, PendingQuote] = {}
        self._session_quotes: dict[str, str] = {}
        self._lock = threading.RLock()

    def claim_session(self, session_id: str, user_id: str) -> None:
        with self._lock:
            self._purge_locked()
            owner_record = self._owners.get(session_id)
            owner = owner_record[0] if owner_record else None
            if owner is not None and owner != user_id:
                raise PermissionError("Session belongs to another user")
            self._owners[session_id] = (user_id, time.time() + self._session_ttl_seconds)

    def assert_owner(self, session_id: str, user_id: str) -> None:
        with self._lock:
            self._purge_locked()
            owner_record = self._owners.get(session_id)
            if owner_record is None or owner_record[0] != user_id:
                raise PermissionError("Session not found or access denied")

    def owner_of(self, session_id: str) -> Optional[str]:
        with self._lock:
            self._purge_locked()
            owner_record = self._owners.get(session_id)
            return owner_record[0] if owner_record else None

    def create_quote(
        self,
        session_id: str,
        user_id: str,
        products: list[dict[str, Any]],
        recommendation: dict[str, Any],
    ) -> PendingQuote:
        now = time.time()
        quote = PendingQuote(
            quote_id=secrets.token_urlsafe(24),
            session_id=session_id,
            user_id=user_id,
            products=deepcopy(products),
            recommendation=deepcopy(recommendation),
            created_at=now,
            expires_at=now + self._quote_ttl_seconds,
        )
        with self._lock:
            self._purge_locked()
            old_quote_id = self._session_quotes.get(session_id)
            if old_quote_id:
                self._quotes.pop(old_quote_id, None)
            self._quotes[quote.quote_id] = quote
            self._session_quotes[session_id] = quote.quote_id
        return deepcopy(quote)

    def consume_quote(
        self,
        quote_id: str,
        session_id: str,
        user_id: str,
        selected_index: int,
    ) -> tuple[PendingQuote, dict[str, Any]]:
        with self._lock:
            quote = self._quotes.get(quote_id)
            if not quote or quote.session_id != session_id or quote.user_id != user_id:
                raise PermissionError("Quote not found or access denied")
            if quote.consumed:
                raise ValueError("Quote has already been used")
            if quote.expires_at < time.time():
                raise TimeoutError("Quote has expired")
            if selected_index < 0 or selected_index >= len(quote.products):
                raise IndexError("Selected product is outside the quoted options")
            quote.consumed = True
            return deepcopy(quote), deepcopy(quote.products[selected_index])

    def _purge_locked(self) -> None:
        now = time.time()
        stale_sessions = [session_id for session_id, (_, expiry) in self._owners.items() if expiry < now]
        for session_id in stale_sessions:
            self._owners.pop(session_id, None)
            quote_id = self._session_quotes.pop(session_id, None)
            if quote_id:
                self._quotes.pop(quote_id, None)

        stale_quotes = [
            quote_id
            for quote_id, quote in self._quotes.items()
            if quote.consumed and quote.expires_at < now
        ]
        for quote_id in stale_quotes:
            quote = self._quotes.pop(quote_id, None)
            if quote and self._session_quotes.get(quote.session_id) == quote_id:
                self._session_quotes.pop(quote.session_id, None)


class MongoSessionStore:
    """Durable state store for deployments with multiple API workers."""

    def __init__(
        self,
        mongo_uri: str,
        database_name: str = "gangu",
        quote_ttl_seconds: int = 10 * 60,
        session_ttl_seconds: int = 24 * 60 * 60,
    ) -> None:
        self._quote_ttl_seconds = quote_ttl_seconds
        self._session_ttl_seconds = session_ttl_seconds
        database = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)[database_name]
        self._owners = database.session_owners
        self._quotes = database.pending_quotes
        self._owners.create_index("expires_at")
        self._quotes.create_index("expires_at")
        self._quotes.create_index("session_id")

    def claim_session(self, session_id: str, user_id: str) -> None:
        now = time.time()
        try:
            self._owners.update_one(
                {
                    "_id": session_id,
                    "$or": [{"user_id": user_id}, {"expires_at": {"$lt": now}}],
                },
                {"$set": {"user_id": user_id, "expires_at": now + self._session_ttl_seconds}},
                upsert=True,
            )
        except DuplicateKeyError as exc:
            raise PermissionError("Session belongs to another user") from exc

    def assert_owner(self, session_id: str, user_id: str) -> None:
        owner = self._owners.find_one(
            {"_id": session_id, "user_id": user_id, "expires_at": {"$gte": time.time()}},
            {"_id": 1},
        )
        if owner is None:
            raise PermissionError("Session not found or access denied")

    def owner_of(self, session_id: str) -> Optional[str]:
        owner = self._owners.find_one(
            {"_id": session_id, "expires_at": {"$gte": time.time()}}, {"user_id": 1}
        )
        return str(owner["user_id"]) if owner else None

    def create_quote(
        self,
        session_id: str,
        user_id: str,
        products: list[dict[str, Any]],
        recommendation: dict[str, Any],
    ) -> PendingQuote:
        self.assert_owner(session_id, user_id)
        now = time.time()
        quote = PendingQuote(
            quote_id=secrets.token_urlsafe(24),
            session_id=session_id,
            user_id=user_id,
            products=deepcopy(products),
            recommendation=deepcopy(recommendation),
            created_at=now,
            expires_at=now + self._quote_ttl_seconds,
        )
        self._quotes.update_many(
            {"session_id": session_id, "consumed": False}, {"$set": {"consumed": True}}
        )
        self._quotes.insert_one({"_id": quote.quote_id, **quote.__dict__})
        return deepcopy(quote)

    def consume_quote(
        self,
        quote_id: str,
        session_id: str,
        user_id: str,
        selected_index: int,
    ) -> tuple[PendingQuote, dict[str, Any]]:
        existing = self._quotes.find_one({"_id": quote_id})
        if not existing or existing.get("session_id") != session_id or existing.get("user_id") != user_id:
            raise PermissionError("Quote not found or access denied")
        if existing.get("consumed"):
            raise ValueError("Quote has already been used")
        if float(existing["expires_at"]) < time.time():
            raise TimeoutError("Quote has expired")
        products = existing.get("products", [])
        if selected_index < 0 or selected_index >= len(products):
            raise IndexError("Selected product is outside the quoted options")

        consumed = self._quotes.find_one_and_update(
            {
                "_id": quote_id,
                "session_id": session_id,
                "user_id": user_id,
                "consumed": False,
                "expires_at": {"$gte": time.time()},
            },
            {"$set": {"consumed": True}},
            return_document=ReturnDocument.AFTER,
        )
        if consumed is None:
            raise ValueError("Quote has already been used or expired")
        consumed.pop("_id", None)
        quote = PendingQuote(**consumed)
        return quote, deepcopy(quote.products[selected_index])


def create_session_store() -> SessionStore | MongoSessionStore:
    backend = os.getenv("GANGU_STATE_BACKEND", "memory").strip().lower()
    if backend == "memory":
        return SessionStore()
    if backend == "mongodb":
        mongo_uri = os.getenv("MONGODB_URI", "").strip()
        if not mongo_uri:
            raise RuntimeError("MONGODB_URI is required when GANGU_STATE_BACKEND=mongodb")
        return MongoSessionStore(mongo_uri, os.getenv("MONGODB_DATABASE", "gangu"))
    raise RuntimeError(f"Unsupported GANGU_STATE_BACKEND: {backend}")


session_store = create_session_store()
