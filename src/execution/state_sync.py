from __future__ import annotations

from src.execution.account_store import AccountStore
from src.execution.binance_testnet import BinanceTestnetClient
from src.execution.execution_state import ExecutionState
from src.execution.order_store import OrderStore


class StateSynchronizer:
    def __init__(
        self,
        client,
        state: ExecutionState | None = None,
        order_store: OrderStore | None = None,
        account_store: AccountStore | None = None,
    ) -> None:
        self.client = client

        if state is not None:
            self.state = state
        else:
            self.state = ExecutionState(
                order_store=order_store,
                account_store=account_store,
            )

    def sync(self, symbol: str) -> None:
        account = self.client.get_account()

        self.state.account.apply_snapshot(
            balances={
                item["asset"]: item
                for item in account["balances"]
            },
            update_time_ms=account.get("updateTime"),
        )

        for order in self.client.get_open_orders(symbol=symbol):
            self.state.orders.apply_rest_order(order)
