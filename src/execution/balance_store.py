from __future__ import annotations

from decimal import Decimal
from typing import Dict


class BalanceStore:
    """Хранит балансы по активам (в памяти)."""

    def __init__(self) -> None:
        self._balances: Dict[str, Decimal] = {}
        self._locked: Dict[str, Decimal] = {}

    def set(self, asset: str, free: str, locked: str = "0") -> None:
        self._balances[asset] = Decimal(free)
        self._locked[asset] = Decimal(locked)

    def get_free(self, asset: str) -> Decimal:
        return self._balances.get(asset, Decimal("0"))

    def get_locked(self, asset: str) -> Decimal:
        return self._locked.get(asset, Decimal("0"))

    def get_total(self, asset: str) -> Decimal:
        return self.get_free(asset) + self.get_locked(asset)

    def update(self, asset: str, free: str, locked: str) -> None:
        self._balances[asset] = Decimal(free)
        self._locked[asset] = Decimal(locked)

    def lock(self, asset: str, amount: Decimal) -> bool:
        """Блокирует баланс для ордера."""
        if self.get_free(asset) >= amount:
            self._balances[asset] -= amount
            self._locked[asset] = self.get_locked(asset) + amount
            return True
        return False

    def unlock(self, asset: str, amount: Decimal) -> None:
        """Разблокирует баланс."""
        if self._locked.get(asset, Decimal("0")) >= amount:
            self._locked[asset] -= amount
            self._balances[asset] += amount

    def __repr__(self) -> str:
        items = []
        for asset in self._balances:
            free = self.get_free(asset)
            locked = self.get_locked(asset)
            items.append(f"{asset}: free={free}, locked={locked}")
        return "BalanceStore(" + ", ".join(items) + ")"
