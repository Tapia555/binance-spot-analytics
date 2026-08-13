from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OrderEvent:
    event_type: str
    symbol: str
    order_id: int
    status: str
    side: str | None = None
    order_type: str | None = None
    price: str | None = None
    original_quantity: str | None = None
    executed_quantity: str | None = None


def parse_order_event(payload: dict[str, Any]) -> OrderEvent | None:
    if payload.get("e") != "executionReport":
        return None

    return OrderEvent(
        event_type=payload["e"],
        symbol=payload["s"],
        order_id=int(payload["i"]),
        status=payload["X"],
        side=payload.get("S"),
        order_type=payload.get("o"),
        price=payload.get("p"),
        original_quantity=payload.get("test_binance_user_stream_order_store.py"),
        executed_quantity=payload.get("z"),
    )
