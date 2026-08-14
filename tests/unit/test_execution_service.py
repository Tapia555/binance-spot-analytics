from __future__ import annotations

from decimal import Decimal

from execution.execution_service import ExecutionService, TradeSignal
from execution.order_store import OrderStore
from execution.order_validator import OrderValidator
from execution.risk_manager import RiskManager
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
    def __init__(self) -> None:
        self.placed = None

    def place_limit_order(self, symbol: str, side: str, quantity: str, price: str):
        self.placed = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }
        return {"orderId": "12345", "status": "NEW"}

    def cancel_order(self, symbol: str, order_id: int):
        return {"status": "CANCELED"}


class DummyRulesService:
    def get_rules(self, symbol: str):
        return RULES


class DummyRiskManager:
    def require_allowed(self, symbol: str, quote_asset: str, rules):
        return None


def test_place_limit_order_builds_request():
    client = DummyClient()
    service = ExecutionService(
        client=client,
        store=OrderStore(),
        symbol_rules_service=DummyRulesService(),
        order_validator=OrderValidator(),
        risk_manager=DummyRiskManager(),
    )

    result = service.place_limit_order(
        TradeSignal(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.00020",
            price="50000.00",
        )
    )

    assert result["order_id"] == 12345
    assert result["raw"]["status"] == "NEW"
    assert client.placed == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": "0.00020",
        "price": "50000.00",
    }


def test_cancel_order_delegates_to_client():
    client = DummyClient()
    service = ExecutionService(
        client=client,
        store=OrderStore(),
        symbol_rules_service=DummyRulesService(),
        order_validator=OrderValidator(),
        risk_manager=DummyRiskManager(),
    )

    result = service.cancel_order(symbol="BTCUSDT", order_id=12345)

    assert result["status"] == "CANCELED"
