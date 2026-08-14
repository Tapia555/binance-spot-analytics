from __future__ import annotations

from strategy.trading_loop import TradingLoop


class DummyMarketData:
    def __init__(self):
        self.calls = []

    def get_closes(self, symbol: str, interval: str = "1m", limit: int = 100):
        self.calls.append((symbol, interval, limit))
        return [1.0, 2.0, 3.0, 4.0, 5.0]


class DummyEngine:
    def __init__(self):
        self.received = None

    def on_closes(self, symbol: str, closes):
        self.received = (symbol, closes)
        return {"status": "ok"}


def test_run_once_passes_closes_to_engine():
    market_data = DummyMarketData()
    engine = DummyEngine()
    loop = TradingLoop(market_data=market_data, trading_engine=engine)

    result = loop.run_once("BTCUSDT", "1m", 5)

    assert result == {"status": "ok"}
    assert market_data.calls == [("BTCUSDT", "1m", 5)]
    assert engine.received == ("BTCUSDT", [1.0, 2.0, 3.0, 4.0, 5.0])
