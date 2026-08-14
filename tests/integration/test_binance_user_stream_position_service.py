from __future__ import annotations

from execution.position_service import PositionService
from execution.position_store import PositionStore


def test_position_service_handles_execution_report_from_stream_shape():
    store = PositionStore()
    service = PositionService(store=store)

    event = {
        "e": "executionReport",
        "s": "BTCUSDT",
        "S": "BUY",
        "X": "FILLED",
        "q": "0.00020",
        "z": "0.00020",
        "Z": "10.00000",
    }

    service.handle_event(event)

    pos = store.get("BTCUSDT")
    assert pos is not None
    assert pos.status == "FILLED"
    assert pos.filled_quantity.to_eng_string() == "0.00020"
    assert pos.average_price.to_eng_string() == "50000"
