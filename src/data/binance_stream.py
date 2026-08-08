from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

import websockets


class BinanceKlineStream:
    def __init__(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1m",
        *,
        reconnect_delay: float = 5.0,
        open_timeout: float = 10.0,
    ) -> None:
        self.symbol = symbol.lower()
        self.interval = interval
        self.reconnect_delay = reconnect_delay
        self.open_timeout = open_timeout

    @property
    def url(self) -> str:
        return (
            "wss://stream.testnet.binance.vision/ws/"
            f"{self.symbol}@kline_{self.interval}"
        )

    async def messages(
        self,
        *,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        received = 0

        while limit is None or received < limit:
            try:
                async with websockets.connect(
                    self.url,
                    open_timeout=self.open_timeout,
                    ping_interval=20,
                    ping_timeout=60,
                ) as websocket:
                    async for raw_message in websocket:
                        message = json.loads(raw_message)

                        if message.get("e") == "serverShutdown":
                            break

                        yield message
                        received += 1

                        if limit is not None and received >= limit:
                            return

            except (
                asyncio.TimeoutError,
                TimeoutError,
                OSError,
                websockets.exceptions.WebSocketException,
            ):
                if limit is not None and received >= limit:
                    return

                await asyncio.sleep(self.reconnect_delay)

