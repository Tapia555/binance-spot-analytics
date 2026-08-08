from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class OrderUpdate:
    symbol: str
    order_id: int
    status: str
    side: str
    order_type: str
    executed_quantity: Decimal
    cumulative_quote_quantity: Decimal
    event_time_ms: int


def parse_execution_report(payload: dict[str, Any]) -> OrderUpdate:
    if payload.get("e") != "executionReport":
        raise ValueError("expected executionReport event")

    return OrderUpdate(
        symbol=str(payload["s"]),
        order_id=int(payload["i"]),
        status=str(payload["X"]),
        side=str(payload["S"]),
        order_type=str(payload["o"]),
        executed_quantity=Decimal(str(payload["z"])),
        cumulative_quote_quantity=Decimal(str(payload["Z"])),
        event_time_ms=int(payload["E"]),
    )
