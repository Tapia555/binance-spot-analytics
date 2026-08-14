from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Candle:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int


class MarketDataService:
    def __init__(self, client: Any) -> None:
        self.client = client

    def get_closes(
        self, symbol: str, interval: str = "1m", limit: int = 100
    ) -> list[float]:
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return [float(item[4]) for item in klines]

    def get_candles(
        self, symbol: str, interval: str = "1m", limit: int = 100
    ) -> list[Candle]:
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        candles: list[Candle] = []
        for item in klines:
            candles.append(
                Candle(
                    open_time=int(item[0]),
                    open=float(item[1]),
                    high=float(item[2]),
                    low=float(item[3]),
                    close=float(item[4]),
                    volume=float(item[5]),
                    close_time=int(item[6]),
                )
            )
        return candles
