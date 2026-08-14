import os

import pytest

from data.binance_stream import BinanceKlineStream

RUN_LIVE_TESTS = os.getenv("RUN_LIVE_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_LIVE_TESTS,
    reason="Set RUN_LIVE_TESTS=1 to run live Binance tests",
)


@pytest.mark.asyncio
async def test_binance_kline_stream():
    stream = BinanceKlineStream()

    async for message in stream.messages(limit=1):
        assert isinstance(message, dict)
        assert message
        break
