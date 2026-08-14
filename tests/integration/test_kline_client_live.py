from __future__ import annotations

import os

import pytest

from data.kline_client import KlineClient


@pytest.mark.asyncio
async def test_fetch_real_btcusdt_klines():
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("set RUN_LIVE_TESTS=1 to call Binance Testnet")

    client = KlineClient(
        base_url="https://testnet.binance.vision/api",
    )

    frame = await client.fetch(
        symbol="BTCUSDT",
        interval="1m",
        limit=5,
    )

    assert len(frame) == 5
    assert list(frame.columns) == [
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

    assert frame["open_time"].notna().all()
    assert frame["close_time"].notna().all()
    assert (frame["high"] >= frame["low"]).all()
    assert (frame["volume"] >= 0).all()
    assert (frame["trade_count"] >= 0).all()


@pytest.mark.asyncio
async def test_fetch_real_klines_into_store():
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("set RUN_LIVE_TESTS=1 to call Binance Testnet")

    from data.candle_store import CandleStore
    from data.kline_stream import Kline

    client = KlineClient(
        base_url="https://testnet.binance.vision/api",
    )
    frame = await client.fetch(
        symbol="BTCUSDT",
        interval="1m",
        limit=3,
    )

    store = CandleStore()

    for row in frame.itertuples(index=False):
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

    assert len(store.frame) == 3
    assert len(store.closes()) == 3
    assert store.latest()["close"] > 0
