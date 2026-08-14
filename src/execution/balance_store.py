from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BalanceRecord:
    asset: str
    free: Decimal
    locked: Decimal

    @property
    def total(self) -> Decimal:
        return self.free + self.locked


class BalanceStore:
    def __init__(self) -> None:
        self._balances: dict[str, BalanceRecord] = {}

    def apply_snapshot(self, balances: Iterable[object]) -> None:
        for item in balances:
            asset = item.asset
            free = Decimal(str(item.free))
            locked = Decimal(str(item.locked))
            self._balances[asset] = BalanceRecord(asset=asset, free=free, locked=locked)

    def get(self, asset: str) -> BalanceRecord | None:
        return self._balances.get(asset)

    def all(self) -> dict[str, BalanceRecord]:
        return dict(self._balances)
