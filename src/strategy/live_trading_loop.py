from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from market_data.ws_market_data_service import KlineUpdate
from strategy.trading_engine import TradingEngine


class LiveTradingLoop:
    def __init__(
        self,
        trading_engine: TradingEngine,
        max_closes: int = 200,
    ) -> None:
        self.trading_engine = trading_engine
        self.closes: dict[str, deque[float]] = {}
        self.max_closes = max_closes

    def on_kline(self, update: KlineUpdate) -> Any | None:
        buffer = self.closes.setdefault(update.symbol, deque(maxlen=self.max_closes))
        buffer.append(update.close)

        if not update.is_closed:
            return None

        return self.trading_engine.on_closes(update.symbol, list(buffer))
