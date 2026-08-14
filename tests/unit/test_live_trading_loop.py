from __future__ import annotations

from market_data.ws_market_data_service import KlineUpdate
from strategy.live_trading_loop import LiveTradingLoop


class DummyEngine:
    def __init__(self):
        self.calls = []

    def on_closes(self, symbol, closes):
        self.calls.append((symbol, closes))
        return {"status": "executed"}


def test_on_kline_ignores_unclosed_candle():
    engine = DummyEngine()
    loop = LiveTradingLoop(trading_engine=engine, max_closes=3)

    result = loop.on_kline(
        KlineUpdate(
            symbol="BTCUSDT",
            interval="1m",
            is_closed=False,
            close=100.0,
        )
    )

    assert result is None
    assert engine.calls == []
    assert list(loop.closes["BTCUSDT"]) == [100.0]


def test_on_kline_runs_engine_on_closed_candle():
    engine = DummyEngine()
    loop = LiveTradingLoop(trading_engine=engine, max_closes=3)

    loop.on_kline(KlineUpdate("BTCUSDT", "1m", False, 100.0))
    result = loop.on_kline(KlineUpdate("BTCUSDT", "1m", True, 101.0))

    assert result == {"status": "executed"}
    assert engine.calls == [("BTCUSDT", [100.0, 101.0])]


def test_on_kline_keeps_only_recent_closes():
    engine = DummyEngine()
    loop = LiveTradingLoop(trading_engine=engine, max_closes=2)

    loop.on_kline(KlineUpdate("BTCUSDT", "1m", False, 100.0))
    loop.on_kline(KlineUpdate("BTCUSDT", "1m", False, 101.0))
    loop.on_kline(KlineUpdate("BTCUSDT", "1m", True, 102.0))

    assert list(loop.closes["BTCUSDT"]) == [101.0, 102.0]
