from __future__ import annotations

from typing import Any

import aiohttp


class BinanceClient:
    def __init__(
        self,
        base_url: str = "https://testnet.binance.vision/api",
    ) -> None:
        self.base_url = base_url.rstrip("/")

    async def get_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1m",
        limit: int = 3,
    ) -> list[list[Any]]:
        url = f"{self.base_url}/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
