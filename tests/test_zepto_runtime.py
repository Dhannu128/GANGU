from __future__ import annotations

import asyncio
from pathlib import Path

from api import zepto_runtime as runtime_module


class FakeZeptoClient:
    disconnected = 0
    stopped = 0

    def __init__(self, _server_path: str) -> None:
        pass

    async def connect(self) -> None:
        return None

    async def start_zepto_order(self, *_args, **_kwargs):
        return {"success": False, "status": "login_otp_required", "requires_otp": True}

    async def submit_login_otp(self, _otp: str):
        return {"success": True, "status": "completed", "message": "Order placed"}

    async def submit_payment_otp(self, _otp: str):
        return {"success": True, "status": "completed", "message": "Order placed"}

    async def stop_order(self):
        type(self).stopped += 1
        return {"success": False, "status": "pending"}

    async def disconnect(self) -> None:
        type(self).disconnected += 1


def test_runtime_keeps_client_for_otp_then_closes(monkeypatch) -> None:
    FakeZeptoClient.disconnected = 0
    FakeZeptoClient.stopped = 0
    monkeypatch.setattr(runtime_module, "ZeptoMCPClient", FakeZeptoClient)
    runtime = runtime_module.ZeptoOrderRuntime(Path("server.py"))

    async def scenario() -> None:
        started = await runtime.start("user", "session", "milk", None, "9000000000", "Home")
        assert started["status"] == "login_otp_required"
        assert FakeZeptoClient.disconnected == 0

        completed = await runtime.submit_otp("user", "session", "123456", "login")
        assert completed["status"] == "completed"
        assert FakeZeptoClient.disconnected == 1
        assert FakeZeptoClient.stopped == 0

    asyncio.run(scenario())


def test_runtime_cancel_stops_active_order(monkeypatch) -> None:
    FakeZeptoClient.disconnected = 0
    FakeZeptoClient.stopped = 0
    monkeypatch.setattr(runtime_module, "ZeptoMCPClient", FakeZeptoClient)
    runtime = runtime_module.ZeptoOrderRuntime(Path("server.py"))

    async def scenario() -> None:
        await runtime.start("user", "session", "milk", None, "9000000000", "Home")
        await runtime.cancel("user", "session")

    asyncio.run(scenario())
    assert FakeZeptoClient.stopped == 1
    assert FakeZeptoClient.disconnected == 1
