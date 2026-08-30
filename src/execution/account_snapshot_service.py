from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .balance_store import BalanceStore


@dataclass(frozen=True)
class AssetBalance:
    asset: str
    free: str
    locked: str


class AccountSnapshotService:
    def __init__(self, client: Any, store: BalanceStore) -> None:
        self.client = client
        self.store = store

    def refresh(self) -> list[AssetBalance]:
        account = self.client.get_account()
        balances = []
        for item in account.get("balances", []):
            balance = AssetBalance(
                asset=item["asset"],
                free=item["free"],
                locked=item["locked"],
            )
            balances.append(balance)
        self.store.apply_snapshot(balances)
        return balances
