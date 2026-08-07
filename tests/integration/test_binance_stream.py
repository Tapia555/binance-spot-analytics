import pytest

from src.data.binance_stream import BinanceKlineStream


@pytest.mark.asyncio
async def test_binance_kline_stream():
    stream = BinanceKlineStream()

    async for message in stream.messages(limit=1):
        assert message["e"] == "kline"
        assert message["s"] == "BTCUSDT"
        assert message["k"]["i"] == "1m"
        assert "c" in message["k"]
        break
