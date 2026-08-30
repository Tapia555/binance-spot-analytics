from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import aiohttp

from .config import settings

logger = logging.getLogger(__name__)


class BybitClient:
    """Клиент для Bybit API (REST) - public endpoints only."""

    def __init__(self):
        self.testnet = settings.bybit.testnet
        self.base_url = (
            "https://api-testnet.bybit.com"
            if self.testnet
            else "https://api.bybit.com"
        )
        self.timeout = settings.execution.timeout

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Выполняет HTTP запрос (public endpoints)."""
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                data = await response.json()
                return data

    async def get_balance(self, coin: str = "USDT") -> Optional[float]:
        """Получает баланс (mock для тестов)."""
        # Mock balance для тестов
        logger.info("Using mock balance for testing")
        return 1000.0

    async def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Получает тикер инструмента."""
        try:
            data = await self._request(
                "GET", 
                "/v5/market/tickers",
                params={"category": "spot", "symbol": symbol}
            )
            
            if data and data.get("retCode") == 0:
                ticker_list = data.get("result", {}).get("list", [])
                if ticker_list:
                    return ticker_list_list[0]
            
            return None
        except Exception as e:
            logger.error(f"Error getting ticker: {e}")
            return None

    async def get_klines(
        self,
        symbol: str,
        interval: str = "1",
        limit: int = 200,
    ) -> Optional[list]:
        """Получает свечи (klines)."""
        try:
            data = await self._request(
                "GET",
                "/v5/market/kline",
                params={
                    "category": "spot",
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit,
                },
            )
            
            if data and data.get("retCode") == 0:
                return data.get("result", {}).get("list", [])
            
            return None
        except Exception as e:
            logger.error(f"Error getting klines: {e}")
            return None

    async def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: Optional[float] = None,
        order_type: str = "Market",
    ) -> Optional[Dict[str, Any]]:
        """Mock order для тестов."""
        logger.info(f"MOCK ORDER: {side} {qty} {symbol} @ {price or 'MARKET'}")
        return {"orderId": "MOCK123", "orderStatus": "Filled"}

    async def cancel_order(
        self,
        symbol: str,
        order_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mock cancel."""
        logger.info(f"MOCK CANCEL: {order_id}")
        return {"orderId": order_id}

    async def get_order_status(
        self,
        symbol: str,
        order_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mock status."""
        return {"orderId": order_id, "orderStatus": "Filled"}
