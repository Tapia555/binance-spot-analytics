from decimal import Decimal

import pytest

from risk.position_sizer import calculate_position_size


def test_calculate_position_size():
    plan = calculate_position_size(
        equity=1000,
        risk_percent=0.01,
        atr_value=100,
        stop_atr_multiplier=1.5,
        entry_price=65000,
        step_size="0.00001",
    )

    assert plan.equity == Decimal(1000)
    assert plan.risk_amount == Decimal("10.00")
    assert plan.stop_distance == Decimal("150.0")
    assert plan.quantity == Decimal("0.06666")


def test_max_notional_limits_quantity():
    plan = calculate_position_size(
        equity=100000,
        risk_percent=0.01,
        atr_value=100,
        stop_atr_multiplier=1,
        entry_price=65000,
        step_size="0.00001",
        max_notional=1000,
    )

    assert plan.quantity == Decimal("0.01538")


def test_reject_invalid_values():
    with pytest.raises(ValueError):
        calculate_position_size(
            equity=0,
            risk_percent=0.01,
            atr_value=100,
            stop_atr_multiplier=1,
            entry_price=65000,
        )

    with pytest.raises(ValueError):
        calculate_position_size(
            equity=1000,
            risk_percent=1,
            atr_value=100,
            stop_atr_multiplier=1,
            entry_price=65000,
        )

    with pytest.raises(ValueError):
        calculate_position_size(
            equity=1000,
            risk_percent=0.01,
            atr_value=0,
            stop_atr_multiplier=1,
            entry_price=65000,
        )
