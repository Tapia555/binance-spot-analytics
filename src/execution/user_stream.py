from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any

import websocket
from websocket import WebSocketTimeoutException
from dotenv import load_dotenv


WS_URL = "wss://ws-api.testnet.binance.vision/ws-api/v3"


class BinanceUserStream:
    def __init__(self) -> None:
        load_dotenv()

        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.secret = os.getenv("BINANCE_TESTNET_SECRET")

        if not self.api_key or not self.secret:
            raise RuntimeError("Testnet credentials are missing")

        if not self.api_key.isascii() or not self.secret.isascii():
            raise RuntimeError("Credentials must contain ASCII characters")

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

    def subscribe(self) -> None:
        timestamp = int(time.time() * 1000)

        params = {
            "apiKey": self.api_key,
            "timestamp": timestamp,
        }

        params["signature"] = self._signature(params)

        request = {
            "id": "user-stream-1",
            "method": "userDataStream.subscribe.signature",
            "params": params,
        }

        connection = websocket.create_connection(
            WS_URL,
            timeout=30,
        )

        try:
            connection.send(json.dumps(request))

            while True:
                try:
                    raw_message = connection.recv()
                except WebSocketTimeoutException:
                    connection.ping()
                    print("No event yet; ping sent")
                    continue

                if not raw_message:
                    print("Connection closed by server")
                    break

                message = json.loads(raw_message)

                print(json.dumps(message, indent=2))

                if message.get("status", 0) >= 400:
                    raise RuntimeError(message)



        finally:
            connection.close()
