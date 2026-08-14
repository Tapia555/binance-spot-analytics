from __future__ import annotations

import json

from market_data.ws_market_data_service import KlineUpdate, WSMarketDataService


class DummyWSClient:
    def __init__(self):
        self.stream = None
        self.on_message = None

    def subscribe(self, stream: str, on_message):
        self.stream = stream
        self.on_message = on_message


def test_subscribe_kline_registers_stream():
    ws = DummyWSClient()
    service = WSMarketDataService(ws_client=ws)

    updates = []

    service.subscribe_kline("BTCUSDT", "1m", updates.append)

    assert ws.stream == "btcusdt@kline_1m"
    assert callable(ws.on_message)

    ws.on_message(
        json.dumps(
            {
                "data": {
                    "s": "BTCUSDT",
                    "k": {
                        "i": "1m",
                        "x": True,
                        "c": "123.45",
                    },
                }
            }
        )
    )

    assert len(updates) == 1
    assert updates[0] == KlineUpdate(
        symbol="BTCUSDT",
        interval="1m",
        is_closed=True,
        close=123.45,
    )


def test_subscribe_kline_handles_raw_payload():
    ws = DummyWSClient()
    service = WSMarketDataService(ws_client=ws)

    updates = []

    service.subscribe_kline("BTCUSDT", "1m", updates.append)

    ws.on_message(
        {
            "s": "BTCUSDT",
            "k": {
                "i": "1m",
                "x": False,
                "c": "100.10",
            },
        }
    )

    assert updates[0].close == 100.10
    assert updates[0].is_closed is False
