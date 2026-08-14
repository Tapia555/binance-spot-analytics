from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from execution.execution_service import ExecutionService, TradeSignal
from strategy.ma_crossover_strategy import MACrossoverStrategy, StrategyAction


class TradingEngine:
    def __init__(
        self,
        strategy: MACrossoverStrategy,
        execution_service: ExecutionService,
    ) -> None:
        self.strategy = strategy
        self.execution_service = execution_service

    def on_closes(self, symbol: str, closes: Sequence[float]) -> dict[str, Any] | None:
        signal = self.strategy.generate(symbol, closes)
        if signal.action == StrategyAction.HOLD:
            return None

        side = signal.action.value
        price = str(closes[-1])
        quantity = self._default_quantity()

        trade_signal = TradeSignal(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
        )
        return self.execution_service.place_limit_order(trade_signal)

    @staticmethod
    def _default_quantity() -> str:
        return "0.00020"
