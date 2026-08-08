from __future__ import annotations

from src.execution.account_store import AccountStore
from src.execution.binance_testnet import BinanceTestnetClient
from src.execution.order_store import OrderStore


class StateSynchronizer:
    def __init__(
        self,
        client: BinanceTestnetClient,
        order_store: OrderStore,
        account_store: AccountStore,
    ) -> None:
        self.client = client
        self.order_store = order_store
        self.account_store = account_store

    def sync(self, symbol: str) -> None:
        account = self.client.get_account()

        balances = {
            item["asset"]: item
            for item in account["balances"]
        }

        self.account_store.apply_snapshot(
            balances=balances,
            update_time_ms=account.get("updateTime"),
        )

        open_orders = self.client.get_open_orders(
            symbol=symbol,
        )

        for order in open_orders:
            self.order_store.apply_rest_order(order)
