from __future__ import annotations

from decimal import Decimal

import pytest

from execution.balance_store import BalanceRecord, BalanceStore
from execution.position_store import Position, PositionStore
from execution.risk_manager import RiskManager, RiskRejected
from execution.symbol_rules_service import SymbolRules

RULES = SymbolRules(
    symbol="BTCUSDT",
    min_price=Decimal("0.01"),
    max_price=Decimal("1000000.00"),
    tick_size=Decimal("0.01"),
    min_qty=Decimal("0.00001000"),
    max_qty=Decimal("1000.00000000"),
    step_size=Decimal("0.00001000"),
    min_notional=Decimal("10.00"),
)


def build_balances(usdt_free: str) -> BalanceStore:
    store = BalanceStore()
    store._balances["USDT"] = BalanceRecord(
        asset="USDT",
        free=Decimal(usdt_free),
        locked=Decimal(0),
    )
    return store


def build_positions(opened: bool = False) -> PositionStore:
    store = PositionStore()
    if opened:
        store._positions["BTCUSDT"] = Position(
            symbol="BTCUSDT",
            side="BUY",
            quantity=Decimal("0.00020"),
            filled_quantity=Decimal("0.00020"),
            average_price=Decimal(50000),
            status="FILLED",
        )
    return store


def test_evaluate_allows_when_balance_sufficient_and_no_position():
    manager = RiskManager(
        balances=build_balances("1000"),
        positions=build_positions(False),
        max_portfolio_quote_pct="0.10",
    )

    decision = manager.evaluate("BTCUSDT", "USDT", RULES)

    assert decision.allowed
    assert decision.max_notional == Decimal(100)


def test_evaluate_rejects_when_open_position_exists():
    manager = RiskManager(
        balances=build_balances("1000"),
        positions=build_positions(True),
        max_portfolio_quote_pct="0.10",
    )

    decision = manager.evaluate("BTCUSDT", "USDT", RULES)

    assert not decision.allowed
    assert decision.reason == "open_position_exists"


def test_evaluate_rejects_when_below_min_notional():
    manager = RiskManager(
        balances=build_balances("50"),
        positions=build_positions(False),
        max_portfolio_quote_pct="0.10",
    )

    decision = manager.evaluate("BTCUSDT", "USDT", RULES)

    assert not decision.allowed
    assert decision.reason == "below_min_notional"


def test_require_allowed_raises():
    manager = RiskManager(
        balances=build_balances("1000"),
        positions=build_positions(True),
        max_portfolio_quote_pct="0.10",
    )

    with pytest.raises(RiskRejected, match="open_position_exists"):
        manager.require_allowed("BTCUSDT", "USDT", RULES)
