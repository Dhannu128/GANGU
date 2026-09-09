from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi import HTTPException

os.environ.setdefault("GANGU_AUTH_REQUIRED", "false")
os.environ["GANGU_DRY_RUN"] = "true"
os.environ["ENABLE_REAL_PURCHASES"] = "false"

from api.main import OrderConfirmationRequest, confirm_order, zepto_integration_status
from api import security
from api.security import AuthenticatedUser
from api import session_store as session_store_module
from api.session_store import SessionStore, session_store
from orchestration.gangu_graph import purchase_agent


def test_session_owner_isolation() -> None:
    store = SessionStore()
    store.claim_session("session-safe-123", "user-a")
    with pytest.raises(PermissionError):
        store.claim_session("session-safe-123", "user-b")


def test_unknown_state_backend_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GANGU_STATE_BACKEND", "unknown")
    with pytest.raises(RuntimeError, match="Unsupported GANGU_STATE_BACKEND"):
        session_store_module.create_session_store()


def test_authentication_fails_closed_without_bearer_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security, "AUTH_REQUIRED", True)
    with pytest.raises(HTTPException) as exc_info:
        security.get_current_user(None)
    assert exc_info.value.status_code == 401


def test_quote_honors_selection_and_is_single_use() -> None:
    store = SessionStore()
    store.claim_session("session-safe-456", "user-a")
    quote = store.create_quote(
        "session-safe-456",
        "user-a",
        [{"product_id": "first"}, {"product_id": "second"}],
        {},
    )

    _, selected = store.consume_quote(
        quote.quote_id, "session-safe-456", "user-a", selected_index=1
    )
    assert selected["product_id"] == "second"

    with pytest.raises(ValueError, match="already been used"):
        store.consume_quote(quote.quote_id, "session-safe-456", "user-a", 1)


def test_expired_quote_is_rejected() -> None:
    store = SessionStore(quote_ttl_seconds=-1)
    store.claim_session("session-safe-789", "user-a")
    quote = store.create_quote("session-safe-789", "user-a", [{}], {})
    with pytest.raises(TimeoutError, match="expired"):
        store.consume_quote(quote.quote_id, "session-safe-789", "user-a", 0)


def test_graph_never_executes_purchase_before_confirmation() -> None:
    state = {
        "decision_type": "auto_buy",
        "selected_option": {"platform": "Zepto", "price": 50},
    }
    result = purchase_agent(state)
    assert result["purchase_status"] == "pending_confirmation"
    assert "order_id" not in result


def test_confirm_endpoint_returns_explicit_dry_run_for_exact_selection() -> None:
    user = AuthenticatedUser(uid=f"test-{uuid.uuid4()}")
    session_id = f"session-{uuid.uuid4().hex}"
    session_store.claim_session(session_id, user.uid)
    quote = session_store.create_quote(
        session_id,
        user.uid,
        [
            {"product_id": "one", "platform": "Zepto", "source": "catalog_estimate"},
            {"product_id": "two", "platform": "Swiggy", "source": "mock_swiggy_mcp"},
        ],
        {},
    )
    request = OrderConfirmationRequest(
        session_id=session_id,
        quote_id=quote.quote_id,
        selected_product_index=1,
        delivery_address="12 Test Street, Indore",
        payment_method="cod",
    )

    result = asyncio.run(confirm_order(request, user))

    assert result["success"] is True
    assert result["simulated"] is True
    assert result["product"]["product_id"] == "two"
    assert result["order_id"].startswith("DRY-RUN-")


def test_estimated_product_cannot_become_real_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GANGU_DRY_RUN", "false")
    monkeypatch.setenv("ENABLE_REAL_PURCHASES", "true")
    user = AuthenticatedUser(uid=f"test-{uuid.uuid4()}")
    session_id = f"session-{uuid.uuid4().hex}"
    session_store.claim_session(session_id, user.uid)
    quote = session_store.create_quote(
        session_id,
        user.uid,
        [{"product_id": "estimate", "platform": "Zepto", "source": "catalog_estimate"}],
        {},
    )
    request = OrderConfirmationRequest(
        session_id=session_id,
        quote_id=quote.quote_id,
        selected_product_index=0,
        delivery_address="12 Test Street, Indore",
        payment_method="cod",
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(confirm_order(request, user))
    assert exc_info.value.status_code == 409


def test_zepto_status_never_exposes_secret_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEPTO_PHONE_NUMBER", "9000000000")
    monkeypatch.setenv("ZEPTO_DEFAULT_ADDRESS", "Private Home Address")
    status = asyncio.run(zepto_integration_status())
    assert status["phone_configured"] is True
    assert status["address_configured"] is True
    assert "9000000000" not in str(status)
    assert "Private Home Address" not in str(status)
