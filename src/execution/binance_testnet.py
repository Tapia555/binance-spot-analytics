from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientError, ClientTimeout

logger = logging.getLogger(__name__)


class BinanceAPIError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg}")


class BinanceRateLimitError(BinanceAPIError):
    pass


class BinanceTestnetClient:
    def __init__(
        self,
        base_url: str = "https://testnet.binance.vision",
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        session = await self._get_session()
        url = f"{self.base_url}{path}"

        for attempt in range(self.max_retries):
            try:
                if signed:
                    if params is None:
                        params = {}
                    params["timestamp"] = int(asyncio.get_event_loop().time() * 1000)

                async with session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers={"X-MBX-APIKEY": self.api_key} if self.api_key else {},
                ) as resp:
                    result = await resp.json()

                    if resp.status >= 400:
                        code = result.get("code", resp.status)
                        msg = result.get("msg", str(result))

                        if code in (-1003, -1015, 429):
                            raise BinanceRateLimitError(code, msg)

                        raise BinanceAPIError(code, msg)

                    return result

            except (ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

            except BinanceRateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1) * 2)
                else:
                    raise

        raise BinanceAPIError(-1, "Max retries exceeded")

    async def get_account_balance(self, asset: str = "USDT") -> Dict[str, Any]:
        """Получает баланс счёта."""
        return await self._request("GET", "/api/v3/account")

    async def get_symbol_rules(self, symbol: str) -> Dict[str, Any]:
        """Получает правила для символа."""
        data = await self._request("GET", "/api/v3/exchangeInfo")
        for s in data.get("symbols", []):
            if s["symbol"] == symbol:
                return s
        raise ValueError(f"Symbol {symbol} not found")

    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        """Создаёт ордер."""
        data = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timeInForce": time_in_force,
        }
        if price:
            data["price"] = price

        return await self._request("POST", "/api/v3/order", data=data, signed=True)

    async def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Отменяет ордер."""
        return await self._request(
            "DELETE",
            "/api/v3/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    async def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получает открытые ордера."""
        params = {"symbol": symbol} if symbol else {}
        return await self._request(
            "GET", "/api/v3/openOrders", params=params, signed=True
        )

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[List[Any]]:
        """Получает клайн-данные."""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        return await self._request("GET", "/api/v3/klines", params=params)
