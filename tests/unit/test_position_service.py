from __future__ import annotations

from execution.position_service import PositionService
from execution.position_store import PositionStore


def test_handle_event_ignores_non_execution_report():
    store = PositionStore()
    service = PositionService(store=store)

    service.handle_event({"e": "outboundAccountPosition", "s": "BTCUSDT"})

    assert store.get("BTCUSDT") is None


def test_handle_event_updates_store_on_execution_report():
    store = PositionStore()
    service = PositionService(store=store)

    service.handle_event(
        {
            "e": "executionReport",
            "s": "BTCUSDT",
            "S": "BUY",
            "X": "PARTIALLY_FILLED",
            "q": "0.00020",
            "z": "0.00010",
            "Z": "5.00000",
        }
    )

    pos = store.get("BTCUSDT")
    assert pos is not None
    assert pos.status == "PARTIALLY_FILLED"
    assert pos.filled_quantity.to_eng_string() == "0.00010"
    assert pos.average_price.to_eng_string() == "50000"
