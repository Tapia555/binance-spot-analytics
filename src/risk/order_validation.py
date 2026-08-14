from __future__ import annotations

from decimal import ROUND_DOWN, Decimal


class OrderValidationError(ValueError):
    pass


def _decimal(value: str | float) -> Decimal:
    return Decimal(str(value))


def round_down_to_step(
    value: str | float,
    step: str | float,
) -> Decimal:
    number = _decimal(value)
    increment = _decimal(step)

    if increment <= 0:
        raise ValueError("step must be positive")

    units = (number / increment).to_integral_value(rounding=ROUND_DOWN)
    return units * increment


def validate_limit_order(
    price: str | float,
    quantity: str | float,
    *,
    min_price: str | float,
    max_price: str | float,
    tick_size: str | float,
    min_qty: str | float,
    max_qty: str | float,
    step_size: str | float,
    min_notional: str | float,
) -> tuple[Decimal, Decimal]:
    normalized_price = round_down_to_step(price, tick_size)
    normalized_quantity = round_down_to_step(quantity, step_size)

    if normalized_price < _decimal(min_price):
        raise OrderValidationError("price is below min_price")

    if normalized_price > _decimal(max_price):
        raise OrderValidationError("price is above max_price")

    if normalized_quantity < _decimal(min_qty):
        raise OrderValidationError("quantity is below min_qty")

    if normalized_quantity > _decimal(max_qty):
        raise OrderValidationError("quantity is above max_qty")

    notional = normalized_price * normalized_quantity

    if notional < _decimal(min_notional):
        raise OrderValidationError("order notional is below min_notional")

    return normalized_price, normalized_quantity
