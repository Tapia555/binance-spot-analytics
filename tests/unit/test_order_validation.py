from decimal import Decimal

import pytest

from risk.order_validation import (
    OrderValidationError,
    round_down_to_step,
    validate_limit_order,
)


def test_round_down_to_step():
    assert round_down_to_step("64857.999", "0.01") == Decimal("64857.99")
    assert round_down_to_step("0.123456", "0.00001") == Decimal("0.12345")


def test_validate_limit_order():
    price, quantity = validate_limit_order(
        price="64857.999",
        quantity="0.00010",
        min_price="0.01",
        max_price="1000000",
        tick_size="0.01",
        min_qty="0.00001",
        max_qty="9000",
        step_size="0.00001",
        min_notional="5",
    )

    assert price == Decimal("64857.99")
    assert quantity == Decimal("0.00010")


def test_reject_small_notional():
    with pytest.raises(OrderValidationError):
        validate_limit_order(
            price="64857.99",
            quantity="0.00001",
            min_price="0.01",
            max_price="1000000",
            tick_size="0.01",
            min_qty="0.00001",
            max_qty="9000",
            step_size="0.00001",
            min_notional="5",
        )
