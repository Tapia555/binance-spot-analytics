import pytest

from src.data.kline_client import KlineClient


def test_kline_client_url():
    client = KlineClient(
        base_url="https://testnet.binance.vision/api/",
    )

    assert client.base_url == (
        "https://testnet.binance.vision/api"
    )


@pytest.mark.asyncio
async def test_fetch_rejects_invalid_limit():
    client = KlineClient()

    with pytest.raises(ValueError):
        await client.fetch(
            symbol="BTCUSDT",
            interval="1m",
            limit=0,
        )

    with pytest.raises(ValueError):
        await client.fetch(
            symbol="BTCUSDT",
            interval="1m",
            limit=1001,
        )
