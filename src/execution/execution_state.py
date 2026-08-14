from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from execution.account_store import AccountStore, Balance
from execution.order_event_parser import OrderUpdate
from execution.order_store import OrderStore


@dataclass(frozen=True)
class StateSnapshot:
    orders: tuple[OrderUpdate, ...]
    balances: tuple[Balance, ...]


class ExecutionState:
    def __init__(
        self,
        *,
        order_store: OrderStore | None = None,
        account_store: AccountStore | None = None,
    ) -> None:
        self.orders = order_store or OrderStore()
        self.account = account_store or AccountStore()
        self._lock = Lock()

    def apply_event(self, payload: dict) -> str | None:
        event = payload.get("event", payload)
        event_type = event.get("e")

        with self._lock:
            if event_type == "executionReport":
                self.orders.apply_event(payload)
                return event_type

            if event_type == "outboundAccountPosition":
                self.account.apply_event(payload)
                return event_type

        return None

    def snapshot(self) -> StateSnapshot:
        with self._lock:
            return StateSnapshot(
                orders=tuple(self.orders.all()),
                balances=tuple(self.account.all()),
            )

    def clear(self) -> None:
        with self._lock:
            for order in self.orders.all():
                self.orders.remove(order.order_id)

            self.account = AccountStore()
