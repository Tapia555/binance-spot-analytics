from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class Position:
    symbol: str
    side: str
    quantity: Decimal
    filled_quantity: Decimal
    average_price: Decimal
    status: str

    @property
    def is_open(self) -> bool:
        return (
            self.status in {"NEW", "PARTIALLY_FILLED", "FILLED"}
            and self.filled_quantity > 0
        )


class PositionStore:
    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}

    def apply_execution_report(self, event: dict[str, Any]) -> None:
        symbol = event.get("s")
        if not symbol:
            return

        side = event.get("S", "")
        status = event.get("X", "")
        qty = Decimal(str(event.get("q", "0")))
        filled_qty = Decimal(str(event.get("z", "0")))
        cum_quote = Decimal(str(event.get("Z", "0")))

        avg_price = Decimal(0)
        if filled_qty > 0:
            avg_price = cum_quote / filled_qty

        self._positions[symbol] = Position(
            symbol=symbol,
            side=side,
            quantity=qty,
            filled_quantity=filled_qty,
            average_price=avg_price,
            status=status,
        )

    def get(self, symbol: str) -> Position | None:
        return self._positions.get(symbol)

    def all(self) -> dict[str, Position]:
        return dict(self._positions)

    def open_positions(self) -> list[Position]:
        return [p for p in self._positions.values() if p.is_open]
