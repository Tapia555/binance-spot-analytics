from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from collections.abc import Callable
from typing import Any

import websocket
from dotenv import load_dotenv
from websocket import WebSocketTimeoutException


WS_URL = "wss://ws-api.testnet.binance.vision/ws-api/v3"

MessageHandler = Callable[[dict[str, Any]], None]


class BinanceUserStream:
    def __init__(
        self,
        *,
        on_message: MessageHandler | None = None,
    ) -> None:
        load_dotenv()

        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.secret = os.getenv("BINANCE_TESTNET_SECRET")
        self.on_message = on_message or self.handle_message

        if not self.api_key or not self.secret:
            raise RuntimeError("Testnet credentials are missing")

        if not self.api_key.isascii() or not self.secret.isascii():
            raise RuntimeError(
                "Credentials must contain ASCII characters"
            )

    def _signature(self, params: dict[str, Any]) -> str:
        payload = "&".join(
            f"{key}={params[key]}"
            for key in sorted(params)
        )

        return hmac.new(
            self.secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def handle_message(self, message: dict[str, Any]) -> None:
        print(json.dumps(message, indent=2))

    def _subscription_request(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "apiKey": self.api_key,
            "timestamp": int(time.time() * 1000),
        }

        params["signature"] = self._signature(params)

        return {
            "id": "user-stream-1",
            "method": "userDataStream.subscribe.signature",
            "params": params,
        }

    def subscribe(self) -> None:
        connection = websocket.create_connection(
            WS_URL,
            timeout=30,
        )

        try:
            connection.send(
                json.dumps(self._subscription_request())
            )

            while True:
                try:
                    raw_message = connection.recv()
                except WebSocketTimeoutException:
                    connection.ping()
                    continue

                if not raw_message:
                    break

                message = json.loads(raw_message)

                if message.get("status", 0) >= 400:
                    raise RuntimeError(message)

                self.on_message(message)

        finally:
            connection.close()
