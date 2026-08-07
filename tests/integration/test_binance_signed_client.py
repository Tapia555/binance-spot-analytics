import os

import pytest

from src.data.binance_signed_client import BinanceSignedClient


@pytest.mark.asyncio
async def test_get_account():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        pytest.skip("Binance API keys are not configured")

    client = BinanceSignedClient(api_key, api_secret)
    account = await client.get_account()

    assert account["canTrade"] is not None
    assert "balances" in account
