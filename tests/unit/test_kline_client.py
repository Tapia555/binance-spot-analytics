from __future__ import annotations


import pandas as pd
import pytest

from data.kline_client import KlineClient


class FakeResponse:
    def __init__(self, payload: list[list[object]]) -> None:
        self.payload = payload

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        pass

    async def json(self) -> list[list[object]]:
        return self.payload


class FakeSession:
    def __init__(self, payload: list[list[object]]) -> None:
        self.payload = payload
        self.requested_url: str | None = None
        self.requested_params: dict[str, object] | None = None

    async def __aenter__(self) -> "FakeSession":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    def get(
        self,
        url: str,
        *,
        params: dict[str, object],
    ) -> FakeResponse:
        self.requested_url = url
        self.requested_params = params
        return FakeResponse(self.payload)


def sample_payload() -> list[list[object]]:
    return [
        [
            1700000000000,
            "64000.00",
            "64100.00",
            "63900.00",
            "64050.00",
            "12.5",
            1700000059999,
            "800625.00",
            100,
            "6.0",
            "384300.00",
            "0",
        ],
        [
            1700000060000,
            "64050.00",
            "64200.00",
            "64000.00",
            "64150.00",
            "10.0",
            1700000119999,
            "641500.00",
            80,
            "5.0",
            "320750.00",
            "0",
        ],
    ]


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


@pytest.mark.asyncio
async def test_fetch_parses_klines(monkeypatch):
    fake_session = FakeSession(sample_payload())

    def session_factory(*args: object, **kwargs: object) -> FakeSession:
        return fake_session

    monkeypatch.setattr(
        "data.kline_client.aiohttp.ClientSession",
        session_factory,
    )

    client = KlineClient()
    frame = await client.fetch(
        symbol="btcusdt",
        interval="1m",
        limit=2,
    )

    assert isinstance(frame, pd.DataFrame)
    assert len(frame) == 2
    assert list(frame["close"]) == [64050.0, 64150.0]
    assert list(frame["trade_count"]) == [100, 80]
    assert str(frame["open_time"].dt.tz) == "UTC"

    assert fake_session.requested_url == (
        "https://testnet.binance.vision/api/v3/klines"
    )
    assert fake_session.requested_params == {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 2,
    }
