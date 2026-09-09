"""Short-lived, in-memory Zepto MCP order sessions for OTP continuation."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from mcp_clients.zepto_mcp_client import ZeptoMCPClient


class ZeptoOrderRuntime:
    """Keep the stdio MCP process alive only while an order awaits OTP."""

    def __init__(self, server_path: Path) -> None:
        self.server_path = server_path
        self._clients: dict[tuple[str, str], ZeptoMCPClient] = {}
        self._lock = asyncio.Lock()

    async def start(
        self,
        user_id: str,
        session_id: str,
        product_name: str,
        item_url: str | None,
        phone_number: str,
        address: str,
    ) -> dict[str, Any]:
        key = (user_id, session_id)
        async with self._lock:
            await self._close(key, stop=True)
            client = ZeptoMCPClient(str(self.server_path))
            await client.connect()
            try:
                result = await client.start_zepto_order(
                    product_name,
                    item_url=item_url,
                    phone_number=phone_number,
                    address=address,
                )
            except Exception:
                await client.disconnect()
                raise
            if result.get("requires_otp"):
                self._clients[key] = client
            else:
                await client.disconnect()
            return result

    async def submit_otp(
        self, user_id: str, session_id: str, otp: str, otp_type: str
    ) -> dict[str, Any]:
        key = (user_id, session_id)
        async with self._lock:
            client = self._clients.get(key)
            if client is None:
                raise LookupError("No Zepto order is waiting for an OTP")
            try:
                result = (
                    await client.submit_payment_otp(otp)
                    if otp_type == "payment"
                    else await client.submit_login_otp(otp)
                )
            except Exception:
                await self._close(key, stop=True)
                raise
            if not result.get("requires_otp"):
                await self._close(key, stop=not result.get("success"))
            return result

    async def cancel(self, user_id: str, session_id: str) -> None:
        async with self._lock:
            await self._close((user_id, session_id), stop=True)

    async def close_all(self) -> None:
        async with self._lock:
            for key in list(self._clients):
                await self._close(key, stop=True)

    async def _close(self, key: tuple[str, str], stop: bool) -> None:
        client = self._clients.pop(key, None)
        if client is None:
            return
        if stop:
            try:
                await client.stop_order()
            except Exception:
                pass
        await client.disconnect()
