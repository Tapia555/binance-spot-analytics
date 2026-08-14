from __future__ import annotations

from decimal import Decimal

import pytest

from execution.balance_store import BalanceRecord, BalanceStore
from execution.execution_service import ExecutionService, TradeSignal
from execution.order_store import OrderStore
from execution.order_validator import OrderValidator
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


class DummyClient:
    def __init__(self):
        self.placed = None

    def place_limit_order(self, symbol: str, side: str, quantity: str, price: str):
        self.placed = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }
        return {"orderId": "12345", "status": "NEW"}


class DummyRulesService:
    def get_rules(self, symbol: str):
        return RULES


def build_balances(usdt_free: str) -> BalanceStore:
    store = BalanceStore()
    store._balances["USDT"] = BalanceRecord(
        asset="USDT",
        free=Decimal(usdt_free),
        locked=Decimal("0"),
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
            average_price=Decimal("50000"),
            status="FILLED",
        )
    return store


def make_service(usdt_free: str, opened: bool = False):
    client = DummyClient()
    service = ExecutionService(
        client=client,
        store=OrderStore(),
        symbol_rules_service=DummyRulesService(),
        order_validator=OrderValidator(),
        risk_manager=RiskManager(
            balances=build_balances(usdt_free),
            positions=build_positions(opened),
            max_portfolio_quote_pct="0.10",
        ),
    )
    return service, client


def test_pipeline_blocks_order_when_position_is_open():
    service, client = make_service("1000", opened=True)

    with pytest.raises(RiskRejected, match="open_position_exists"):
        service.place_limit_order(
            TradeSignal(
                symbol="BTCUSDT",
                side="BUY",
                quantity="0.00020",
                price="50000.00",
            )
        )

    assert client.placed is None


def test_pipeline_places_order_when_risk_is_ok():
    service, client = make_service("1000", opened=False)

    result = service.place_limit_order(
        TradeSignal(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.00020",
            price="50000.00",
        )
    )

    assert result["order_id"] == 12345
    assert client.placed == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": "0.00020",
        "price": "50000.00",
    }
