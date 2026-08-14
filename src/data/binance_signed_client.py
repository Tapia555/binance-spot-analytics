from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import aiohttp


class BinanceSignedClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binance.vision/api",
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

    def _signed_params(self, params: dict[str, Any]) -> dict[str, Any]:
        payload = dict(params)
        payload["timestamp"] = int(time.time() * 1000)

        query_string = urlencode(payload)
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        payload["signature"] = signature
        return payload

    async def get_account(self) -> dict[str, Any]:
        params = self._signed_params({})

        headers = {
            "X-MBX-APIKEY": self.api_key,
        }

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{self.base_url}/v3/account",
                params=params,
                headers=headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def test_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: str,
        price: str,
    ) -> dict[str, Any]:
        params = self._signed_params(
            {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": quantity,
                "price": price,
            }
        )

        headers = {
            "X-MBX-APIKEY": self.api_key,
        }

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/v3/order/test",
                params=params,
                headers=headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_order(
        self,
        symbol: str,
        order_id: int,
    ) -> dict[str, Any]:
        params = self._signed_params(
            {
                "symbol": symbol,
                "orderId": order_id,
            }
        )

        headers = {
            "X-MBX-APIKEY": self.api_key,
        }

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{self.base_url}/v3/order",
                params=params,
                headers=headers,
            ) as response:
                response.raise_for_status()
                return await response.json()
