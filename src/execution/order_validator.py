from __future__ import annotations

from decimal import Decimal, InvalidOperation

from execution.symbol_rules_service import SymbolRules


class OrderValidationError(ValueError):
    pass


class OrderValidator:
    def validate(self, price: str, quantity: str, rules: SymbolRules) -> None:
        p = self._dec(price)
        q = self._dec(quantity)

        if rules.min_price is not None and p < rules.min_price:
            raise OrderValidationError("price below min_price")
        if rules.max_price is not None and p > rules.max_price:
            raise OrderValidationError("price above max_price")
        if rules.tick_size is not None and not self._is_multiple(
            p, rules.min_price or Decimal(0), rules.tick_size
        ):
            raise OrderValidationError("price not aligned to tick_size")

        if rules.min_qty is not None and q < rules.min_qty:
            raise OrderValidationError("quantity below min_qty")
        if rules.max_qty is not None and q > rules.max_qty:
            raise OrderValidationError("quantity above max_qty")
        if rules.step_size is not None and not self._is_multiple(
            q, rules.min_qty or Decimal(0), rules.step_size
        ):
            raise OrderValidationError("quantity not aligned to step_size")

        notional = p * q
        if rules.min_notional is not None and notional < rules.min_notional:
            raise OrderValidationError("notional below min_notional")

    @staticmethod
    def _dec(value: str) -> Decimal:
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise OrderValidationError(f"invalid decimal: {value}") from exc

    @staticmethod
    def _is_multiple(value: Decimal, base: Decimal, step: Decimal) -> bool:
        if step == 0:
            return True
        return ((value - base) % step) == 0
