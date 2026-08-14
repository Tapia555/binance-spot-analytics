from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class KlineUpdate:
    symbol: str
    interval: str
    is_closed: bool
    close: float


class WSMarketDataService:
    def __init__(self, ws_client: Any) -> None:
        self.ws_client = ws_client

    def subscribe_kline(self, symbol: str, interval: str, on_update: Callable[[KlineUpdate], None]) -> None:
        stream = f"{symbol.lower()}@kline_{interval}"

        def handler(message: str | dict[str, Any]) -> None:
            payload = json.loads(message) if isinstance(message, str) else message
            data = payload.get("data", payload)
            k = data.get("k", {})
            update = KlineUpdate(
                symbol=data.get("s", symbol),
                interval=k.get("i", interval),
                is_closed=bool(k.get("x", False)),
                close=float(k.get("c", 0)),
            )
            on_update(update)

        self.ws_client.subscribe(stream=stream, on_message=handler)
