from __future__ import annotations

from threading import Lock

from src.execution.order_event_parser import (
    OrderUpdate,
    parse_execution_report,
)


class OrderStore:
    def __init__(self) -> None:
        self._orders: dict[int, OrderUpdate] = {}
        self._lock = Lock()

    def apply_event(self, payload: dict) -> OrderUpdate | None:
        if payload.get("event", payload).get("e") != "executionReport":
            return None

        event = payload.get("event", payload)
        update = parse_execution_report(event)

        with self._lock:
            self._orders[update.order_id] = update

        return update

    def get(self, order_id: int) -> OrderUpdate | None:
        with self._lock:
            return self._orders.get(order_id)

    def all(self) -> list[OrderUpdate]:
        with self._lock:
            return list(self._orders.values())

    def remove(self, order_id: int) -> None:
        with self._lock:
            self._orders.pop(order_id, None)
