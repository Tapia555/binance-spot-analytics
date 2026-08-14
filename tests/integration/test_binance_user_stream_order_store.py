from __future__ import annotations

import os
import threading
import time

import pytest

from execution.binance_testnet import BinanceTestnetClient
from execution.order_store import OrderStore
from execution.user_stream import BinanceUserStream


@pytest.mark.integration
def test_user_stream_updates_order_store():
    if os.getenv("RUN_TESTNET_USER_STREAM_TEST") != "1":
        pytest.skip(
            "set RUN_TESTNET_USER_STREAM_TEST=1 "
            "to run Testnet user stream test"
        )

    if os.getenv("CONFIRM_TESTNET_ORDER") != "yes":
        pytest.skip(
            "set CONFIRM_TESTNET_ORDER=yes "
            "to place a Testnet order"
        )

    store = OrderStore()
    client = BinanceTestnetClient()
    stream = BinanceUserStream(on_message=store.apply_event)

    errors: list[BaseException] = []

    def run_stream() -> None:
        try:
            stream.subscribe()
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(
        target=run_stream,
        daemon=True,
    )
    thread.start()

    try:
        time.sleep(3)

        placed = client.place_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.00012",
            price="50000.00",
        )
        order_id = int(placed["orderId"])

        deadline = time.time() + 20
        while time.time() < deadline:
            if errors:
                raise errors[0]
            history = store.history(order_id)
            if history and history[-1].current_status == "NEW":
                break
            time.sleep(0.25)

        assert not errors
        assert store.get(order_id) is not None
        assert store.get(order_id).status == "NEW"

        canceled = client.cancel_order(
            symbol="BTCUSDT",
            order_id=order_id,
        )
        assert canceled["status"] == "CANCELED"

        deadline = time.time() + 20
        while time.time() < deadline:
            if errors:
                raise errors[0]
            history = store.history(order_id)
            if history and history[-1].current_status == "CANCELED":
                break
            time.sleep(0.25)

        history = store.history(order_id)
        assert [item.current_status for item in history][-2:] == [
            "NEW",
            "CANCELED",
        ]

        open_orders = client.get_open_orders(symbol="BTCUSDT")
        store.sync_rest_orders(open_orders)

        assert store.get(order_id) is not None
        assert store.get(order_id).status == "CANCELED"
    finally:
        try:
            thread.join(timeout=1)
        except Exception:
            pass
