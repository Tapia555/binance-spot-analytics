from __future__ import annotations

import os

import pytest

from execution.binance_testnet import BinanceTestnetClient


@pytest.mark.integration
def test_create_query_cancel_testnet_order():
    if os.getenv("RUN_TESTNET_ORDER_TEST") != "1":
        pytest.skip("set RUN_TESTNET_ORDER_TEST=1 to place a Testnet order")

    if os.getenv("CONFIRM_TESTNET_ORDER") != "yes":
        pytest.skip("set CONFIRM_TESTNET_ORDER=yes to place a Testnet order")

    client = BinanceTestnetClient()

    placed = client.place_limit_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity="0.00012",
        price="50000.00",
    )

    order_id = int(placed["orderId"])

    try:
        current = client.get_order(
            symbol="BTCUSDT",
            order_id=order_id,
        )

        assert current["symbol"] == "BTCUSDT"
        assert current["orderId"] == order_id
        assert current["status"] in {
            "NEW",
            "PARTIALLY_FILLED",
            "FILLED",
        }
    finally:
        if current["status"] in {"NEW", "PARTIALLY_FILLED"}:
            canceled = client.cancel_order(
                symbol="BTCUSDT",
                order_id=order_id,
            )
            assert canceled["status"] == "CANCELED"
