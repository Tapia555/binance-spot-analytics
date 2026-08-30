from __future__ import annotations

from typing import Any

from .position_store import PositionStore


class PositionService:
    def __init__(self, store: PositionStore) -> None:
        self.store = store

    def handle_event(self, event: dict[str, Any]) -> None:
        if event.get("e") != "executionReport":
            return
        self.store.apply_execution_report(event)
