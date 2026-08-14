from collections import namedtuple
from live.live_trading_loop import LiveTradingLoop

KlineUpdate = namedtuple("KlineUpdate", "symbol interval is_closed close")


class EngineStub:
    def __init__(self):
        self.calls = []

    def on_closes(self, symbol, closes):
        self.calls.append((symbol, list(closes)))
        return {"ok": True}


def test_closed_kline_processed_once():
    engine = EngineStub()
    loop = LiveTradingLoop(engine, max_closes=50)

    u = KlineUpdate("BTCUSDT", "1m", True, 100.0)
    loop.on_kline(u)
    loop.on_kline(u)

    assert len(engine.calls) == 1
