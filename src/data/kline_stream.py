from __future__ import annotations

import json
from dataclasses import dataclass

import aiohttp


@dataclass(frozen=True)
class Kline:
    open_time: int
    close_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    closed: bool


class KlineStream:
    def __init__(
        self,
        symbol: str = "btcusdt",
        interval: str = "1m",
        base_url: str = "wss://stream.testnet.binance.vision/ws",
    ) -> None:
        self.symbol = symbol.lower()
        self.interval = interval
        self.base_url = base_url.rstrip("/")

    @property
    def url(self) -> str:
        return f"{self.base_url}/{self.symbol}@kline_{self.interval}"

    @staticmethod
    def parse_message(payload: dict) -> Kline:
        if payload.get("e") != "kline":
            raise ValueError("unsupported event type")

        data = payload["k"]

        return Kline(
            open_time=int(data["t"]),
            close_time=int(data["T"]),
            open=float(data["o"]),
            high=float(data["h"]),
            low=float(data["l"]),
            close=float(data["c"]),
            volume=float(data["v"]),
            closed=bool(data["x"]),
        )

    async def receive_once(self) -> Kline:
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.ws_connect(self.url) as websocket:
                message = await websocket.receive()

                if message.type != aiohttp.WSMsgType.TEXT:
                    raise RuntimeError(
                        f"unexpected websocket message: {message.type}"
                    )

                return self.parse_message(json.loads(message.data))
