from __future__ import annotations

from market_data.market_data_service import MarketDataService


class DummyClient:
    def get_klines(self, symbol: str, interval: str, limit: int):
        return [
            [1, "10", "11", "9", "10.5", "100", 2],
            [3, "10.5", "12", "10", "11.2", "120", 4],
        ]


def test_get_closes_returns_close_prices():
    service = MarketDataService(client=DummyClient())

    closes = service.get_closes("BTCUSDT", "1m", 2)

    assert closes == [10.5, 11.2]


def test_get_candles_parses_kline_rows():
    service = MarketDataService(client=DummyClient())

    candles = service.get_candles("BTCUSDT", "1m", 2)

    assert len(candles) == 2
    assert candles[0].open_time == 1
    assert candles[0].close == 10.5
    assert candles[1].high == 12.0
