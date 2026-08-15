from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class Position:
    symbol: str
    side: str  # "BUY" или "SELL"
    quantity: Decimal
    entry_price: Decimal
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")


class PositionStore:
    """Хранит открытые позиции."""

    def __init__(self) -> None:
        self._positions: Dict[str, Position] = {}

    def get(self, symbol: str) -> Optional[Position]:
        return self._positions.get(symbol)

    def set(self, position: Position) -> None:
        if position.quantity > 0:
            self._positions[position.symbol] = position
        elif position.symbol in self._positions:
            del self._positions[position.symbol]

    def close(self, symbol: str) -> Optional[Position]:
        """Закрывает позицию и возвращает её."""
        return self._positions.pop(symbol, None)

    def all(self) -> List[Position]:
        return list(self._positions.values())

    def __repr__(self) -> str:
        if not self._positions:
            return "PositionStore(no positions)"
        items = [
            f"{p.symbol}: {p.side} {p.quantity}@{p.entry_price}"
            for p in self._positions.values()
        ]
        return "PositionStore(" + ", ".join(items) + ")"
