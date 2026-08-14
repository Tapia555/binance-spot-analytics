from __future__ import annotations

import os

import pytest

from data.candle_store import CandleStore
from data.kline_client import KlineClient
from strategy.ema_strategy import EmaStrategy


@pytest.mark.asyncio
async def test_live_data_reaches_strategy():
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("set RUN_LIVE_TESTS=1 to call Binance Testnet")

    client = KlineClient(
        base_url="https://testnet.binance.vision/api",
    )

    frame = await client.fetch(
        symbol="BTCUSDT",
        interval="1m",
        limit=40,
    )

    store = CandleStore(max_size=100)

    for row in frame.itertuples(index=False):
        from data.kline_stream import Kline

        store.add(
            Kline(
                open_time=int(row.open_time.timestamp() * 1000),
                close_time=int(row.close_time.timestamp() * 1000),
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=float(row.volume),
                closed=True,
            )
        )

    strategy = EmaStrategy(
        fast_period=12,
        slow_period=26,
    )

    signal = strategy.evaluate(store.closes())

    assert signal.side.value in {"BUY", "SELL", "HOLD"}
    assert signal.price is not None
    assert signal.price > 0
    assert signal.reason
