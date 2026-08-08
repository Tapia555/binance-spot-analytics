from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderValidationResult:
    valid: bool
    errors: tuple[str, ...]


def _decimal(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def _aligned(value: Decimal, step: Decimal) -> bool:
    if step == 0:
        return True
    return (value / step).to_integral_value() * step == value


def validate_limit_order(
    *,
    price: str,
    quantity: str,
    filters: dict[str, dict[str, str]],
) -> OrderValidationResult:
    errors: list[str] = []

    price_decimal = _decimal(price)
    quantity_decimal = _decimal(quantity)
    notional = price_decimal * quantity_decimal

    price_filter = filters.get("PRICE_FILTER")
    if price_filter:
        min_price = _decimal(price_filter["minPrice"])
        max_price = _decimal(price_filter["maxPrice"])
        tick_size = _decimal(price_filter["tickSize"])

        if price_decimal < min_price:
            errors.append("price below minPrice")

        if max_price != 0 and price_decimal > max_price:
            errors.append("price above maxPrice")

        if not _aligned(price_decimal, tick_size):
            errors.append("price violates tickSize")

    lot_filter = filters.get("LOT_SIZE")
    if lot_filter:
        min_qty = _decimal(lot_filter["minQty"])
        max_qty = _decimal(lot_filter["maxQty"])
        step_size = _decimal(lot_filter["stepSize"])

        if quantity_decimal < min_qty:
            errors.append("quantity below minQty")

        if max_qty != 0 and quantity_decimal > max_qty:
            errors.append("quantity above maxQty")

        if not _aligned(quantity_decimal, step_size):
            errors.append("quantity violates stepSize")

    notional_filter = (
        filters.get("NOTIONAL")
        or filters.get("MIN_NOTIONAL")
    )

    if notional_filter:
        min_notional_key = (
            "minNotional"
            if "minNotional" in notional_filter
            else "notional"
        )
        min_notional = _decimal(
            notional_filter[min_notional_key]
        )

        if notional < min_notional:
            errors.append("order notional below minimum")

    return OrderValidationResult(
        valid=not errors,
        errors=tuple(errors),
    )
