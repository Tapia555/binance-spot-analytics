from execution.order_store import OrderStore


def event(status: str, event_time: int) -> dict:
    return {
        "event": {
            "e": "executionReport",
            "E": event_time,
            "s": "BTCUSDT",
            "S": "BUY",
            "o": "LIMIT",
            "X": status,
            "i": 123,
            "z": "0.00000",
            "Z": "0.00000000",
        }
    }


def test_order_history_contains_transitions():
    store = OrderStore()

    store.apply_event(event("NEW", 100))
    store.apply_event(event("PARTIALLY_FILLED", 200))
    store.apply_event(event("FILLED", 300))

    history = store.history(123)

    assert len(history) == 3

    assert history[0].previous_status is None
    assert history[0].current_status == "NEW"

    assert history[1].previous_status == "NEW"
    assert history[1].current_status == "PARTIALLY_FILLED"

    assert history[2].previous_status == "PARTIALLY_FILLED"
    assert history[2].current_status == "FILLED"
