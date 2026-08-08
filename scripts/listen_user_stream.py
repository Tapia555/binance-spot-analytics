from __future__ import annotations

import json

from src.execution.order_store import OrderStore
from src.execution.user_stream import BinanceUserStream


class TrackingUserStream(BinanceUserStream):
    def __init__(self, store: OrderStore) -> None:
        super().__init__()
        self.store = store

    def handle_message(self, message: dict) -> None:
        update = self.store.apply_event(message)

        if update is not None:
            print(
                "ORDER UPDATE:",
                update.order_id,
                update.symbol,
                update.status,
            )
        else:
            print(json.dumps(message, indent=2))


if __name__ == "__main__":
    store = OrderStore()
    TrackingUserStream(store).subscribe()
