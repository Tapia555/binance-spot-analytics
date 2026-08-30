from __future__ import annotations

from decimal import Decimal
from typing import Tuple

from .balance_store import BalanceStore
from .position_store import PositionStore


class RiskManager:
    """Проверяет риск перед исполнением ордера."""

    def __init__(
        self,
        balances: BalanceStore,
        positions: PositionStore,
        max_portfolio_quote_pct: str = "0.10",
        max_loss_per_trade_pct: str = "0.02",
    ) -> None:
        self.balances = balances
        self.positions = positions
        self.max_portfolio_pct = Decimal(max_portfolio_quote_pct)
        self.max_loss_pct = Decimal(max_loss_per_trade_pct)

    def can_open_position(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal,
    ) -> Tuple[bool, str]:
        """Проверяет, можно ли открыть позицию."""
        quote_asset = "USDT"

        # Проверка баланса
        required_quote = quantity * price
        available_quote = self.balances.get_free(quote_asset)

        if required_quote > available_quote:
            return False, f"insufficient_{quote_asset.lower()}"

        # Проверка лимита на портфель
        total_portfolio_value = self.balances.get_total(quote_asset)
        max_allowed = total_portfolio_value * self.max_portfolio_pct

        if required_quote > max_allowed:
            return False, "exceeds_portfolio_limit"

        # Проверка существующей позиции
        existing = self.positions.get(symbol)
        if existing and existing.side != side:
            return False, "opposite_position_open"

        return True, "ok"

    def can_close_position(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
    ) -> Tuple[bool, str]:
        """Проверяет, можно ли закрыть позицию."""
        position = self.positions.get(symbol)

        if not position:
            return False, "no_position"

        if position.side == side:
            return False, "same_side_as_position"

        if quantity > position.quantity:
            return False, "quantity_exceeds_position"

        return True, "ok"
