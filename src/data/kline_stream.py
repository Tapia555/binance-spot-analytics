from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
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

    async def listen(
        self,
        on_kline: Callable[[Kline], Awaitable[None]],
        *,
        reconnect_delay: float = 5.0,
        stop_event: asyncio.Event | None = None,
    ) -> None:
        while stop_event is None or not stop_event.is_set():
            try:
                await self._listen_once(
                    on_kline,
                    stop_event=stop_event,
                )
            except (TimeoutError, aiohttp.ClientError, ConnectionError):
                if stop_event is not None and stop_event.is_set():
                    break

                await asyncio.sleep(reconnect_delay)

    async def _listen_once(
        self,
        on_kline: Callable[[Kline], Awaitable[None]],
        *,
        stop_event: asyncio.Event | None,
    ) -> None:
        timeout = aiohttp.ClientTimeout(total=None)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.ws_connect(
                self.url,
                heartbeat=20.0,
            ) as websocket:
                while stop_event is None or not stop_event.is_set():
                    message = await websocket.receive()

                    if message.type == aiohttp.WSMsgType.TEXT:
                        kline = self.parse_message(
                            json.loads(message.data),
                        )
                        await on_kline(kline)

                    elif message.type == aiohttp.WSMsgType.PING:
                        await websocket.pong(message.data)

                    elif message.type in {
                        aiohttp.WSMsgType.CLOSE,
                        aiohttp.WSMsgType.CLOSED,
                        aiohttp.WSMsgType.ERROR,
                    }:
                        raise ConnectionError(
                            "websocket connection closed",
                        )
