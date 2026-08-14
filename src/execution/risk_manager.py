from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from execution.balance_store import BalanceStore
from execution.position_store import PositionStore
from execution.symbol_rules_service import SymbolRules


class RiskRejected(ValueError):
    pass


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    max_notional: Decimal
    reason: str = ""


class RiskManager:
    def __init__(
        self,
        balances: BalanceStore,
        positions: PositionStore,
        max_portfolio_quote_pct: str = "0.10",
    ) -> None:
        self.balances = balances
        self.positions = positions
        self.max_portfolio_quote_pct = Decimal(max_portfolio_quote_pct)

    def evaluate(self, symbol: str, quote_asset: str, rules: SymbolRules) -> RiskDecision:
        position = self.positions.get(symbol)
        if position is not None and position.is_open:
            return RiskDecision(False, Decimal("0"), "open_position_exists")

        quote_balance = self.balances.get(quote_asset)
        if quote_balance is None:
            return RiskDecision(False, Decimal("0"), "missing_quote_balance")

        available = quote_balance.free
        max_notional = available * self.max_portfolio_quote_pct

        if rules.min_notional is not None and max_notional < rules.min_notional:
            return RiskDecision(False, max_notional, "below_min_notional")

        return RiskDecision(True, max_notional)

    def require_allowed(self, symbol: str, quote_asset: str, rules: SymbolRules) -> RiskDecision:
        decision = self.evaluate(symbol=symbol, quote_asset=quote_asset, rules=rules)
        if not decision.allowed:
            raise RiskRejected(decision.reason)
        return decision
