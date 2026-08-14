from __future__ import annotations

from decimal import Decimal

import pytest

from execution.order_validator import OrderValidationError, OrderValidator
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


def test_validate_accepts_valid_order():
    validator = OrderValidator()

    validator.validate(
        price="50000.00",
        quantity="0.00020",
        rules=RULES,
    )


@pytest.mark.parametrize(
    "price,quantity,expected",
    [
        ("0.001", "0.00020", "price below min_price"),
        ("50000.005", "0.00020", "price not aligned to tick_size"),
        ("50000.00", "0.00000100", "quantity below min_qty"),
        ("50000.00", "0.00001500", "quantity not aligned to step_size"),
        ("50000.00", "0.00010", "notional below min_notional"),
    ],
)
def test_validate_rejects_invalid_order(price, quantity, expected):
    validator = OrderValidator()

    with pytest.raises(OrderValidationError, match=expected):
        validator.validate(price=price, quantity=quantity, rules=RULES)
