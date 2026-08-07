import pandas as pd
import pytest

from src.data.candle_store import CandleStore
from src.data.kline_stream import Kline


def make_kline(
    open_time: int,
    close: float,
    closed: bool = True,
) -> Kline:
    return Kline(
        open_time=open_time,
        close_time=open_time + 59_999,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=10.0,
        closed=closed,
    )


def test_store_ignores_open_candle():
    store = CandleStore()

    store.add(make_kline(1700000000000, 64000.0, closed=False))

    assert store.frame.empty


def test_store_adds_closed_candles():
    store = CandleStore(max_size=2)

    store.add(make_kline(1700000000000, 64000.0))
    store.add(make_kline(1700000060000, 64100.0))
    store.add(make_kline(1700000120000, 64200.0))

    assert len(store.frame) == 2
    assert list(store.closes()) == [64100.0, 64200.0]
    assert store.latest()["close"] == pytest.approx(64200.0)


def test_store_replaces_duplicate_candle():
    store = CandleStore()

    store.add(make_kline(1700000000000, 64000.0))
    store.add(make_kline(1700000000000, 64100.0))

    assert len(store.frame) == 1
    assert store.latest()["close"] == pytest.approx(64100.0)


def test_store_rejects_invalid_size():
    with pytest.raises(ValueError):
        CandleStore(max_size=0)
