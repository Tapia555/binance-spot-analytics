from __future__ import annotations

import json
from collections.abc import AsyncIterator

import websockets


class BinanceKlineStream:
    def __init__(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1m",
        base_url: str = "wss://stream.testnet.binance.vision/ws",
    ) -> None:
        stream = f"{symbol.lower()}@kline_{interval}"
        self.url = f"{base_url.rstrip('/')}/{stream}"

    async def messages(self, limit: int = 1) -> AsyncIterator[dict]:
        received = 0

        async with websockets.connect(self.url) as websocket:
            while received < limit:
                raw_message = await websocket.recv()
                received += 1
                yield json.loads(raw_message)
