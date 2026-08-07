from __future__ import annotations

from typing import Any

import aiohttp
import pandas as pd


class KlineClient:
    def __init__(
        self,
        base_url: str = "https://testnet.binance.vision/api",
    ) -> None:
        self.base_url = base_url.rstrip("/")

    async def fetch(
        self,
        symbol: str,
        interval: str,
        limit: int = 200,
    ) -> pd.DataFrame:
        if limit <= 0 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")

        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit,
        }

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{self.base_url}/v3/klines",
                params=params,
            ) as response:
                response.raise_for_status()
                payload: list[list[Any]] = await response.json()

        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trade_count",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ]

        frame = pd.DataFrame.from_records(
            payload,
            columns=columns,
        )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
        ]

        frame[numeric_columns] = frame[numeric_columns].astype(float)
        frame["trade_count"] = frame["trade_count"].astype(int)

        frame["open_time"] = pd.to_datetime(
            frame["open_time"],
            unit="ms",
            utc=True,
        )
        frame["close_time"] = pd.to_datetime(
            frame["close_time"],
            unit="ms",
            utc=True,
        )

        return frame
