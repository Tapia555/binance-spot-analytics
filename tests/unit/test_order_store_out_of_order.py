from src.execution.order_store import OrderStore


def test_apply_event_ignores_older_event():
    store = OrderStore()

    store.apply_event({
        "event": {
            "e": "executionReport",
            "s": "BTCUSDT",
            "i": 1,
            "X": "NEW",
            "S": "BUY",
            "o": "LIMIT",
            "z": "0.0",
            "Z": "0.0",
            "E": 2000,
        }
    })

    store.apply_event({
        "event": {
            "e": "executionReport",
            "s": "BTCUSDT",
            "i": 1,
            "X": "CANCELED",
            "S": "BUY",
            "o": "LIMIT",
            "z": "0.0",
            "Z": "0.0",
            "E": 1000,
        }
    })

    update = store.get(1)
    history = store.history(1)

    assert update is not None
    assert update.status == "NEW"
    assert update.event_time_ms == 2000
    assert len(history) == 1
    assert history[0].current_status == "NEW"
