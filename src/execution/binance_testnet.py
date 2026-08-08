from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


class BinanceTestnetClient:
    def __init__(self, base_url: str = "https://testnet.binance.vision/api"):
        load_dotenv()

        self.base_url = base_url.rstrip("/")
        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.secret = os.getenv("BINANCE_TESTNET_SECRET")

        if not self.api_key or not self.secret:
            raise RuntimeError("Testnet credentials are missing")

        if not self.api_key.isascii() or not self.secret.isascii():
            raise RuntimeError("Credentials must contain ASCII characters")

    def _signed_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        signed_params = {
            **params,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000,
        }

        query = urlencode(signed_params)

        signature = hmac.new(
            self.secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers={"X-MBX-APIKEY": self.api_key},
            params={**signed_params, "signature": signature},
            timeout=15,
        )

        data = response.json()

        if not response.ok:
            raise RuntimeError(
                f"Binance API error {data.get('code')}: "
                f"{data.get('msg')}"
            )

        return data

    def test_limit_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: str,
        price: str,
    ) -> dict[str, Any]:
        return self._signed_request(
            "POST",
            "/v3/order/test",
            {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": quantity,
                "price": price,
            },
        )
