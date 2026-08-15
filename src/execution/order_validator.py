from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Tuple

from execution.symbol_rules_service import SymbolRules


class OrderValidationError(ValueError):
    pass


class OrderValidator:
    def validate(
        self,
        price: str,
        quantity: str,
        side: str,
        rules: SymbolRules,
    ) -> Tuple[bool, str]:
        """Валидирует ордер. Возвращает (ok, error_message)."""
        try:
            p = self._dec(price)
            q = self._dec(quantity)
        except OrderValidationError as e:
            return False, str(e)

        # Проверка стороны
        if side not in ("BUY", "SELL"):
            return False, f"invalid_side: {side}"

        # Проверка цены
        if rules.min_price is not None and p < rules.min_price:
            return False, "price_below_min"
        if rules.max_price is not None and p > rules.max_price:
            return False, "price_above_max"
        if rules.tick_size is not None and not self._is_multiple(
            p, rules.min_price or Decimal(0), rules.tick_size
        ):
            return False, "price_not_aligned"

        # Проверка количества
        if rules.min_qty is not None and q < rules.min_qty:
            return False, "quantity_below_min"
        if rules.max_qty is not None and q > rules.max_qty:
            return False, "quantity_above_max"
        if rules.step_size is not None and not self._is_multiple(
            q, rules.min_qty or Decimal(0), rules.step_size
        ):
            return False, "quantity_not_aligned"

        # Проверка минимального размера ордера (notional)
        notional = p * q
        if rules.min_notional is not None and notional < rules.min_notional:
            return False, f"notional_below_min ({notional} < {rules.min_notional})"

        # Проверка на ноль
        if q <= 0:
            return False, "quantity_must_be_positive"
        if p <= 0:
            return False, "price_must_be_positive"

        return True, "ok"

    @staticmethod
    def _dec(value: str) -> Decimal:
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise OrderValidationError(f"invalid_decimal: {value}") from exc

    @staticmethod
    def _is_multiple(value: Decimal, base: Decimal, step: Decimal) -> bool:
        if step == 0:
            return True
        return ((value - base) % step) == 0
