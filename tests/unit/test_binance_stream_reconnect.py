from unittest.mock import AsyncMock, patch

import pytest

from data.binance_stream import BinanceKlineStream


@pytest.mark.asyncio
async def test_stream_reconnects_after_timeout():
    first_connection = AsyncMock()
    first_connection.__aenter__.side_effect = TimeoutError()

    second_connection = AsyncMock()
    second_connection.__aenter__.return_value = second_connection
    second_connection.__aiter__.return_value = iter(
        [
            '{"e":"kline","s":"BTCUSDT"}',
        ]
    )

    stream = BinanceKlineStream(
        reconnect_delay=0,
        open_timeout=0.01,
    )

    with patch(
        "data.binance_stream.websockets.connect",
        side_effect=[
            first_connection,
            second_connection,
        ],
    ):
        messages = [
            message
            async for message in stream.messages(limit=1)
        ]

    assert messages == [{"e": "kline", "s": "BTCUSDT"}]
