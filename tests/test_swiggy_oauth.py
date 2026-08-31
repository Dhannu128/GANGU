from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException
from cryptography.fernet import Fernet

from api import swiggy_oauth


def test_oauth_configuration_requires_https_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWIGGY_CLIENT_ID", "test-client")
    monkeypatch.setenv(
        "SWIGGY_REDIRECT_URI", "http://localhost:8000/api/auth/callback/swiggy"
    )

    with pytest.raises(HTTPException) as exc_info:
        swiggy_oauth.create_authorization_url("user-a")

    assert exc_info.value.status_code == 503


def test_oauth_authorization_url_uses_pkce_and_exact_redirect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redirect_uri = "https://api.example.com/api/auth/callback/swiggy"
    store = swiggy_oauth.SwiggyOAuthStore()
    monkeypatch.setenv("SWIGGY_CLIENT_ID", "test-client")
    monkeypatch.setenv("SWIGGY_REDIRECT_URI", redirect_uri)
    monkeypatch.setattr(swiggy_oauth, "swiggy_oauth_store", store)

    url = swiggy_oauth.create_authorization_url("user-a")
    query = parse_qs(urlparse(url).query)

    assert query["client_id"] == ["test-client"]
    assert query["redirect_uri"] == [redirect_uri]
    assert query["code_challenge_method"] == ["S256"]
    assert len(query["code_challenge"][0]) >= 43
    assert "code_verifier" not in query
    assert store.consume_state(query["state"][0]).user_id == "user-a"


def test_oauth_state_is_single_use_and_expires() -> None:
    store = swiggy_oauth.SwiggyOAuthStore()
    state, _ = store.create_state("user-a")
    assert store.consume_state(state).user_id == "user-a"
    with pytest.raises(ValueError, match="invalid or expired"):
        store.consume_state(state)

    expiring_store = swiggy_oauth.SwiggyOAuthStore(state_ttl_seconds=-1)
    expired_state, _ = expiring_store.create_state("user-a")
    with pytest.raises(ValueError, match="invalid or expired"):
        expiring_store.consume_state(expired_state)


class _TokenCollection:
    def __init__(self) -> None:
        self.document: dict | None = None

    def update_one(self, query: dict, update: dict, upsert: bool) -> None:
        self.document = {"_id": query["_id"], **update["$set"]}

    def find_one(self, query: dict, projection: dict) -> dict | None:
        return self.document if self.document and self.document["_id"] == query["_id"] else None


def test_mongodb_oauth_tokens_are_encrypted_at_rest() -> None:
    store = object.__new__(swiggy_oauth.MongoSwiggyOAuthStore)
    store._cipher = Fernet(Fernet.generate_key())
    store._tokens = _TokenCollection()

    store.save_token("user-a", {"access_token": "secret-access-token"})

    assert store._tokens.document is not None
    encrypted = store._tokens.document["encrypted_token"]
    assert "secret-access-token" not in encrypted
    assert store.access_token_for("user-a") == "secret-access-token"
