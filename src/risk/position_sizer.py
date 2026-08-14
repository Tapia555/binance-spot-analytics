from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal


@dataclass(frozen=True)
class PositionPlan:
    equity: Decimal
    risk_amount: Decimal
    stop_distance: Decimal
    quantity: Decimal


def _decimal(value: str | float) -> Decimal:
    return Decimal(str(value))


def calculate_position_size(
    equity: str | float,
    risk_percent: str | float,
    atr_value: str | float,
    stop_atr_multiplier: str | float,
    *,
    entry_price: str | float,
    step_size: str | float = "0.00001",
    max_notional: str | float | None = None,
) -> PositionPlan:
    equity_decimal = _decimal(equity)
    risk_percent_decimal = _decimal(risk_percent)
    atr_decimal = _decimal(atr_value)
    multiplier_decimal = _decimal(stop_atr_multiplier)
    entry_decimal = _decimal(entry_price)
    step_decimal = _decimal(step_size)

    if equity_decimal <= 0:
        raise ValueError("equity must be positive")

    if not 0 < risk_percent_decimal < 1:
        raise ValueError("risk_percent must be between 0 and 1")

    if atr_decimal <= 0:
        raise ValueError("atr_value must be positive")

    if multiplier_decimal <= 0:
        raise ValueError("stop_atr_multiplier must be positive")

    if entry_decimal <= 0:
        raise ValueError("entry_price must be positive")

    if step_decimal <= 0:
        raise ValueError("step_size must be positive")

    risk_amount = equity_decimal * risk_percent_decimal
    stop_distance = atr_decimal * multiplier_decimal
    raw_quantity = risk_amount / stop_distance

    if max_notional is not None:
        max_quantity = _decimal(max_notional) / entry_decimal
        raw_quantity = min(raw_quantity, max_quantity)

    units = (raw_quantity / step_decimal).to_integral_value(
        rounding=ROUND_DOWN,
    )
    quantity = units * step_decimal

    return PositionPlan(
        equity=equity_decimal,
        risk_amount=risk_amount,
        stop_distance=stop_distance,
        quantity=quantity,
    )
