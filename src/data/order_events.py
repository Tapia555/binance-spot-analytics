from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class OrderUpdate:
    symbol: str
    order_id: int
    status: OrderStatus
    side: str
    order_type: str
    price: float
    quantity: float
    executed_quantity: float
    event_time: int


def parse_execution_report(payload: dict) -> OrderUpdate:
    if payload.get("e") != "executionReport":
        raise ValueError("unsupported event type")

    return OrderUpdate(
        symbol=payload["s"],
        order_id=int(payload["i"]),
        status=OrderStatus(payload["X"]),
        side=payload["S"],
        order_type=payload["o"],
        price=float(payload["p"]),
        quantity=float(payload["q"]),
        executed_quantity=float(payload["z"]),
        event_time=int(payload["E"]),
    )
