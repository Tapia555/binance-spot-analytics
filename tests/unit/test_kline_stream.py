from data.kline_stream import KlineStream


def test_kline_url():
    stream = KlineStream(
        symbol="BTCUSDT",
        interval="1m",
    )

    assert stream.url == ("wss://stream.testnet.binance.vision/ws/" "btcusdt@kline_1m")


def test_parse_kline():
    payload = {
        "e": "kline",
        "E": 1700000000000,
        "s": "BTCUSDT",
        "k": {
            "t": 1700000000000,
            "T": 1700000059999,
            "o": "64000.00",
            "h": "64100.00",
            "l": "63900.00",
            "c": "64050.00",
            "v": "12.5",
            "x": True,
        },
    }

    kline = KlineStream.parse_message(payload)

    assert kline.open_time == 1700000000000
    assert kline.close_time == 1700000059999
    assert kline.open == 64000.0
    assert kline.high == 64100.0
    assert kline.low == 63900.0
    assert kline.close == 64050.0
    assert kline.volume == 12.5
    assert kline.closed is True


def test_symbol_and_interval_are_normalized():
    stream = KlineStream(
        symbol="BTCUSDT",
        interval="5m",
    )

    assert stream.url.endswith("/btcusdt@kline_5m")
