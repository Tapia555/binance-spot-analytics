import pytest

from src.data.binance_client import BinanceClient


@pytest.mark.asyncio
async def test_get_klines():
    client = BinanceClient()
    klines = await client.get_klines(limit=1)

    assert len(klines) == 1
    assert len(klines[0]) == 12
    assert klines[0][0] > 0
