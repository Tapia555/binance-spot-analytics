from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class KlineUpdate:
    symbol: str
    interval: str
    is_closed: bool
    close: float


class LiveTradingLoop:
    def __init__(self, trading_engine: Any, max_closes: int = 200) -> None:
        self.trading_engine = trading_engine
        self.max_closes = max_closes
        self.closes: dict[str, deque[float]] = {}
        self._seen: set[tuple[str, str, float]] = set()

    def on_kline(self, update: KlineUpdate) -> Any | None:
        buf = self.closes.setdefault(update.symbol, deque(maxlen=self.max_closes))
        buf.append(update.close)
        if not update.is_closed:
            return None
        key = (update.symbol, update.interval, update.close)
        if key in self._seen:
            return None
        self._seen.add(key)
        return self.trading_engine.on_closes(update.symbol, list(buf))
