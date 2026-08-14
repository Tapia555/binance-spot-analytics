from __future__ import annotations

from typing import Any

from market_data.market_data_service import MarketDataService
from strategy.trading_engine import TradingEngine


class TradingLoop:
    def __init__(
        self,
        market_data: MarketDataService,
        trading_engine: TradingEngine,
    ) -> None:
        self.market_data = market_data
        self.trading_engine = trading_engine

    def run_once(self, symbol: str, interval: str = "1m", limit: int = 100) -> Any:
        closes = self.market_data.get_closes(symbol=symbol, interval=interval, limit=limit)
        return self.trading_engine.on_closes(symbol, closes)
