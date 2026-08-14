from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    min_price: Decimal | None
    max_price: Decimal | None
    tick_size: Decimal | None
    min_qty: Decimal | None
    max_qty: Decimal | None
    step_size: Decimal | None
    min_notional: Decimal | None


class SymbolRulesService:
    def __init__(self, client: Any) -> None:
        self.client = client

    def get_rules(self, symbol: str) -> SymbolRules:
        exchange_info = self.client.get_exchange_info()
        for item in exchange_info.get("symbols", []):
            if item.get("symbol") != symbol:
                continue

            filters = {f["filterType"]: f for f in item.get("filters", [])}

            price_filter = filters.get("PRICE_FILTER", {})
            lot_size = filters.get("LOT_SIZE", {})
            min_notional = filters.get("MIN_NOTIONAL", {})

            return SymbolRules(
                symbol=symbol,
                min_price=self._dec(price_filter.get("minPrice")),
                max_price=self._dec(price_filter.get("maxPrice")),
                tick_size=self._dec(price_filter.get("tickSize")),
                min_qty=self._dec(lot_size.get("minQty")),
                max_qty=self._dec(lot_size.get("maxQty")),
                step_size=self._dec(lot_size.get("stepSize")),
                min_notional=self._dec(min_notional.get("minNotional")),
            )

        raise ValueError(f"symbol not found: {symbol}")

    @staticmethod
    def _dec(value: str | None) -> Decimal | None:
        return Decimal(value) if value is not None else None
