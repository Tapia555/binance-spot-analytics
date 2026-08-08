from __future__ import annotations

import hashlib
import hmac
import os
import time
from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


BASE_URL = "https://testnet.binance.vision/api"


def get_current_price(symbol: str) -> str:
    response = requests.get(
        f"{BASE_URL}/v3/ticker/price",
        params={"symbol": symbol},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["price"]


def round_price(price: str, tick_size: str) -> str:
    price_decimal = Decimal(price)
    tick_decimal = Decimal(tick_size)

    rounded = (
        price_decimal / tick_decimal
    ).to_integral_value(rounding=ROUND_DOWN) * tick_decimal

    return format(rounded, "f")


def main() -> None:
    load_dotenv()

    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    secret = os.getenv("BINANCE_TESTNET_SECRET")

    if not api_key or not secret:
        raise RuntimeError("Testnet credentials are missing")

    if not api_key.isascii() or not secret.isascii():
        raise RuntimeError("API key and secret must contain ASCII characters")

    symbol = "BTCUSDT"
    current_price = get_current_price(symbol)

    info_response = requests.get(
        f"{BASE_URL}/v3/exchangeInfo",
        params={"symbol": symbol},
        timeout=15,
    )
    info_response.raise_for_status()

    symbol_info = info_response.json()["symbols"][0]

    filters = {
        item["filterType"]: item
        for item in symbol_info["filters"]
    }

    tick_size = filters["PRICE_FILTER"]["tickSize"]
    step_size = filters["LOT_SIZE"]["stepSize"]

    notional_filter = filters.get("NOTIONAL")
    min_notional_filter = filters.get("MIN_NOTIONAL")

    if notional_filter:
        min_notional = Decimal(notional_filter["minNotional"])
    elif min_notional_filter:
        min_notional = Decimal(min_notional_filter["minNotional"])
    else:
        raise RuntimeError("No NOTIONAL or MIN_NOTIONAL filter found")

    price = round_price(current_price, tick_size)
    price_decimal = Decimal(price)
    step_decimal = Decimal(step_size)

    required_quantity = min_notional / price_decimal

    quantity_decimal = (
        required_quantity / step_decimal
    ).to_integral_value(rounding=ROUND_DOWN) * step_decimal

    if quantity_decimal * price_decimal < min_notional:
        quantity_decimal += step_decimal

    quantity = format(quantity_decimal, "f")

    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": price,
        "recvWindow": 5000,
        "timestamp": int(time.time() * 1000),
    }

    query = urlencode(params)

    signature = hmac.new(
        secret.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    response = requests.post(
        f"{BASE_URL}/v3/order/test",
        headers={"X-MBX-APIKEY": api_key},
        params={**params, "signature": signature},
        timeout=15,
    )

    print("Current price:", current_price)
    print("Order price:", price)
    print("Minimum notional:", min_notional)
    print("Quantity:", quantity)
    print(
        "Order notional:",
        format(quantity_decimal * price_decimal, "f"),
    )
    print("HTTP status:", response.status_code)
    print(response.json())

    response.raise_for_status()


if __name__ == "__main__":
    main()
