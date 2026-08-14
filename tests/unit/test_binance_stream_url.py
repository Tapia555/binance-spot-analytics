from data.binance_stream import BinanceKlineStream


def test_stream_url():
    stream = BinanceKlineStream("BTCUSDT", "1m")

    assert stream.url == ("wss://stream.testnet.binance.vision/ws/btcusdt@kline_1m")
