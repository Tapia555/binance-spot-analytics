from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"))

import os

import pytest

from data.binance_signed_client import BinanceSignedClient


@pytest.mark.asyncio
async def test_get_account():
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_SECRET")

    if not api_key or not api_secret:
        pytest.skip("Binance Testnet API keys are not configured")

    client = BinanceSignedClient(api_key, api_secret)
    account = await client.get_account()

    assert account["canTrade"] is not None
    assert "balances" in account
