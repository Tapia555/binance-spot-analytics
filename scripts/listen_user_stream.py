from __future__ import annotations

import json

from src.execution.account_store import AccountStore
from src.execution.order_store import OrderStore
from src.execution.user_stream import BinanceUserStream


class TrackingUserStream(BinanceUserStream):
    def __init__(
        self,
        order_store: OrderStore,
        account_store: AccountStore,
    ) -> None:
        super().__init__()
        self.order_store = order_store
        self.account_store = account_store

    def handle_message(self, message: dict) -> None:
        if self.order_store.apply_event(message) is not None:
            update = self.order_store.all()[-1]
            print(
                "ORDER UPDATE:",
                update.order_id,
                update.symbol,
                update.status,
            )
            return

        if self.account_store.apply_event(message):
            usdt = self.account_store.get("USDT")

            if usdt is not None:
                print(
                    "BALANCE UPDATE:",
                    "USDT",
                    "free=",
                    usdt.free,
                    "locked=",
                    usdt.locked,
                )
            return

        print(json.dumps(message, indent=2))


if __name__ == "__main__":
    TrackingUserStream(
        order_store=OrderStore(),
        account_store=AccountStore(),
    ).subscribe()
