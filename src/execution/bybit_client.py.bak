from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientError, ClientTimeout

logger = logging.getLogger(__name__)


class BybitAPIError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Bybit API error {code}: {msg}")


class BybitRateLimitError(BybitAPIError):
    pass


class BybitClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = True,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
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

    def _sign(self, params: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            params.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

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
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
        }
        
        if signed:
            if method == "GET" and params:
                query_string = urlencode(params)
            elif data:
                query_string = urlencode(data)
            else:
                query_string = ""
            
            sign_str = f"{timestamp}{self.api_key}{recv_window}{query_string}"
            signature = self._sign(sign_str)
            headers["X-BAPI-SIGN"] = signature

        for attempt in range(self.max_retries):
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                ) as resp:
                    result = await resp.json()
                    logger.info(f"RAW RESULT: {result}")
                    
                    if result is None:
                        raise BybitAPIError(resp.status, f"Empty response: {await resp.text()}")
                    
                    if resp.status >= 400:
                        code = result.get("retCode", resp.status)
                        msg = result.get("retMsg", str(result))
                        
                        if code in (-1003, -1015, 429, 10001, 10002, 10003):
                            raise BybitRateLimitError(code, msg)
                        
                        raise BybitAPIError(code, msg)

                    logger.info(f"API RESPONSE: {result}")
                    return result

            except (ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

            except BybitRateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1) * 2)
                else:
                    raise

        raise BybitAPIError(-1, "Max retries exceeded")

    async def get_account_balance(self, account_type: str = "UNIFIED") -> Dict[str, Any]:
        # For Unified Trading Account
        return await self._request("GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"}, signed=True)

    async def get_symbol_rules(self, symbol: str) -> Dict[str, Any]:
        return {"symbol": symbol, "baseCoin": symbol.split("USDT")[0], "quoteCoin": "USDT"}

    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: str,
        price: Optional[str] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        data = {
            "category": "spot",
            "symbol": symbol,
            "side": side.upper(),
            "orderType": order_type.upper(),
            "qty": qty,
            "timeInForce": time_in_force,
        }
        if price:
            data["price"] = price

        return await self._request("POST", "/v5/order/create", data=data, signed=True)

    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        data = {
            "category": "spot",
            "symbol": symbol,
            "orderId": order_id,
        }
        return await self._request("POST", "/v5/order/cancel", data=data, signed=True)

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"category": "spot"}
        if symbol:
            params["symbol"] = symbol
        
        result = await self._request("GET", "/v5/order/realtime", params=params, signed=True)
        return result.get("result", {}).get("list", [])

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
    ) -> List[List[Any]]:
        params = {
            "category": "spot",
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        
        result = await self._request("GET", "/v5/market/kline", params=params)
        return result.get("result", {}).get("list", [])

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        params = {"category": "spot", "symbol": symbol}
        result = await self._request("GET", "/v5/market/tickers", params=params)
        return result.get("result", {}).get("list", [{}])[0]
