from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


class ValidationResult:
    def __init__(
        self,
        *,
        valid: bool,
        message: str = "",
        errors: list[str] | None = None,
    ) -> None:
        self.valid = valid
        self.message = message
        self.errors = errors or ([message] if message else [])


class OrderValidationError(ValueError):
    pass


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise OrderValidationError(
            f"Invalid numeric value: {value!r}"
        ) from error


def _is_step_aligned(
    value: Decimal,
    minimum: Decimal,
    step: Decimal,
) -> bool:
    if step == 0:
        return True
    return (value - minimum) % step == 0


class OrderValidator:
    def __init__(self, symbol_info: dict[str, Any]):
        self.symbol_info = symbol_info
        self.filters = {
            item["filterType"]: item
            for item in symbol_info.get("filters", [])
        }

    def validate(
        self,
        *,
        order_type: str,
        quantity: str | Decimal,
        price: str | Decimal | None = None,
    ) -> None:
        order_type = order_type.upper()
        qty = _decimal(quantity)

        if qty <= 0:
            raise OrderValidationError(
                "quantity must be greater than zero"
            )

        lot_filter = self.filters.get(
            "MARKET_LOT_SIZE"
            if order_type == "MARKET"
            else "LOT_SIZE"
        )

        if lot_filter:
            self._validate_quantity(qty, lot_filter)

        if order_type == "LIMIT":
            if price is None:
                raise OrderValidationError(
                    "price is required for LIMIT orders"
                )

            price_value = _decimal(price)
            if price_value <= 0:
                raise OrderValidationError(
                    "price must be greater than zero"
                )

            self._validate_price(price_value)
            self._validate_notional(price_value, qty)

    def _validate_quantity(
        self,
        quantity: Decimal,
        rule: dict[str, Any],
    ) -> None:
        minimum = _decimal(rule["minQty"])
        maximum = _decimal(rule["maxQty"])
        step = _decimal(rule["stepSize"])

        if quantity < minimum:
            raise OrderValidationError(
                f"quantity {quantity} is below minQty {minimum}"
            )

        if quantity > maximum:
            raise OrderValidationError(
                f"quantity {quantity} exceeds maxQty {maximum}"
            )

        if not _is_step_aligned(quantity, minimum, step):
            raise OrderValidationError(
                f"quantity {quantity} does not match stepSize {step}"
            )

    def _validate_price(self, price: Decimal) -> None:
        rule = self.filters.get("PRICE_FILTER")
        if not rule:
            return

        minimum = _decimal(rule["minPrice"])
        maximum = _decimal(rule["maxPrice"])
        step = _decimal(rule["tickSize"])

        if minimum != 0 and price < minimum:
            raise OrderValidationError(
                f"price {price} is below minPrice {minimum}"
            )

        if maximum != 0 and price > maximum:
            raise OrderValidationError(
                f"price {price} exceeds maxPrice {maximum}"
            )

        if not _is_step_aligned(price, minimum, step):
            raise OrderValidationError(
                f"price {price} does not match tickSize {step}"
            )

    def _validate_notional(
        self,
        price: Decimal,
        quantity: Decimal,
    ) -> None:
        rule = self.filters.get("NOTIONAL")
        if rule is None:
            rule = self.filters.get("MIN_NOTIONAL")

        if not rule:
            return

        notional = price * quantity
        minimum = _decimal(
            rule.get("minNotional", "0")
        )

        if notional < minimum:
            raise OrderValidationError(
                f"notional {notional} is below minimum {minimum}"
            )

        maximum = rule.get("maxNotional")
        if maximum is not None:
            maximum_value = _decimal(maximum)
            if maximum_value != 0 and notional > maximum_value:
                raise OrderValidationError(
                    f"notional {notional} exceeds maximum "
                    f"{maximum_value}"
                )


def validate_limit_order(
    *,
    quantity: str | Decimal,
    price: str | Decimal,
    filters: dict[str, dict[str, str]] | None = None,
) -> ValidationResult:
    try:
        if filters is None:
            qty = _decimal(quantity)
            price_value = _decimal(price)

            if qty <= 0:
                raise OrderValidationError(
                    "quantity must be greater than zero"
                )

            if price_value <= 0:
                raise OrderValidationError(
                    "price must be greater than zero"
                )
        else:
            symbol_info = {
                "filters": [
                    {"filterType": name, **rule}
                    for name, rule in filters.items()
                ]
            }

            OrderValidator(symbol_info).validate(
                order_type="LIMIT",
                quantity=quantity,
                price=price,
            )

    except OrderValidationError as error:
        return ValidationResult(
            valid=False,
            message=str(error),
        )

    return ValidationResult(valid=True)
