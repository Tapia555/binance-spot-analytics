from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from threading import Lock


@dataclass(frozen=True)
class Balance:
    asset: str
    free: Decimal
    locked: Decimal


class AccountStore:
    def __init__(self) -> None:
        self._balances: dict[str, Balance] = {}
        self._last_update_ms: int | None = None
        self._lock = Lock()

    def apply_event(self, payload: dict) -> bool:
        event = payload.get("event", payload)

        if event.get("e") != "outboundAccountPosition":
            return False

        balances = {
            item["a"]: Balance(
                asset=item["a"],
                free=Decimal(item["f"]),
                locked=Decimal(item["l"]),
            )
            for item in event.get("B", [])
        }

        with self._lock:
            self._balances.update(balances)
            self._last_update_ms = int(event["u"])

        return True

    def get(self, asset: str) -> Balance | None:
        with self._lock:
            return self._balances.get(asset)

    def all(self) -> list[Balance]:
        with self._lock:
            return list(self._balances.values())

    def apply_snapshot(
        self,
        *,
        balances: dict[str, dict],
        update_time_ms: int | None,
    ) -> None:
        snapshot = {
            asset: Balance(
                asset=asset,
                free=Decimal(str(item["free"])),
                locked=Decimal(str(item["locked"])),
            )
            for asset, item in balances.items()
        }

        with self._lock:
            self._balances = snapshot
            self._last_update_ms = update_time_ms

    @property
    def last_update_ms(self) -> int | None:
        with self._lock:
            return self._last_update_ms
