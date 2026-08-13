from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from threading import Lock


@dataclass(frozen=True)
class OrderUpdate:
    order_id: int
    symbol: str
    status: str
    side: str
    order_type: str
    executed_quantity: Decimal
    cumulative_quote_quantity: Decimal
    event_time_ms: int


@dataclass(frozen=True)
class OrderTransition:
    order_id: int
    previous_status: str | None
    current_status: str
    event_time_ms: int


class OrderStore:
    def __init__(self) -> None:
        self._orders: dict[int, OrderUpdate] = {}
        self._history: dict[int, list[OrderTransition]] = {}
        self._lock = Lock()

    def apply_event(self, payload: dict) -> OrderUpdate | None:
        event = payload.get("event", payload)

        if event.get("e") != "executionReport":
            return None

        update = OrderUpdate(
            order_id=int(event["i"]),
            symbol=str(event["s"]),
            status=str(event["X"]),
            side=str(event["S"]),
            order_type=str(event["o"]),
            executed_quantity=Decimal(str(event["z"])),
            cumulative_quote_quantity=Decimal(str(event["Z"])),
            event_time_ms=int(event["E"]),
        )

        with self._lock:
            previous = self._orders.get(update.order_id)
            last_transition = self._history.get(update.order_id, [])[-1] if self._history.get(update.order_id) else None
            if last_transition is not None and update.event_time_ms < last_transition.event_time_ms:
                return previous if previous is not None else update

            self._orders[update.order_id] = update
            self._history.setdefault(update.order_id, []).append(
                OrderTransition(
                    order_id=update.order_id,
                    previous_status=(
                        previous.status
                        if previous is not None
                        else None
                    ),
                    current_status=update.status,
                    event_time_ms=update.event_time_ms,
                )
            )

        return update

    def get(self, order_id: int) -> OrderUpdate | None:
        with self._lock:
            return self._orders.get(order_id)

    def all(self) -> list[OrderUpdate]:
        with self._lock:
            return list(self._orders.values())

    def history(self, order_id: int) -> list[OrderTransition]:
        with self._lock:
            return list(self._history.get(order_id, []))

    def remove(self, order_id: int) -> None:
        with self._lock:
            self._orders.pop(order_id, None)
            self._history.pop(order_id, None)

    def sync_rest_orders(self, payloads: list[dict]) -> None:
        for payload in payloads:
            self.apply_rest_order(payload)

    def apply_rest_order(self, payload: dict) -> OrderUpdate:
        update_time = payload.get("updateTime")
        if update_time is None:
            update_time = payload["time"]

        update = OrderUpdate(
            symbol=str(payload["symbol"]),
            order_id=int(payload["orderId"]),
            status=str(payload["status"]),
            side=str(payload["side"]),
            order_type=str(payload["type"]),
            executed_quantity=Decimal(
                str(payload["executedQty"])
            ),
            cumulative_quote_quantity=Decimal(
                str(payload["cummulativeQuoteQty"])
            ),
            event_time_ms=int(update_time),
        )

        with self._lock:
            previous = self._orders.get(update.order_id)
            if previous is not None and update.event_time_ms < previous.event_time_ms:
                return previous
            self._orders[update.order_id] = update

        return update
