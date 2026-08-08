from src.execution.order_store import OrderStore


def execution_event(
    order_id: int = 123,
    status: str = "NEW",
) -> dict:
    return {
        "subscriptionId": 0,
        "event": {
            "e": "executionReport",
            "E": 1786180000000,
            "s": "BTCUSDT",
            "c": "client-order-1",
            "S": "BUY",
            "o": "LIMIT",
            "X": status,
            "i": order_id,
            "z": "0.00000",
            "Z": "0.00000000",
        },
    }


def test_store_saves_order_update():
    store = OrderStore()

    update = store.apply_event(execution_event())

    assert update is not None
    assert update.order_id == 123
    assert store.get(123) == update


def test_store_replaces_previous_status():
    store = OrderStore()

    store.apply_event(execution_event(status="NEW"))
    canceled = store.apply_event(
        execution_event(status="CANCELED")
    )

    assert canceled is not None
    assert store.get(123).status == "CANCELED"


def test_store_ignores_other_events():
    store = OrderStore()

    result = store.apply_event(
        {
            "subscriptionId": 0,
            "event": {
                "e": "outboundAccountPosition",
            },
        }
    )

    assert result is None
    assert store.all() == []


def test_store_removes_order():
    store = OrderStore()
    store.apply_event(execution_event())

    store.remove(123)

    assert store.get(123) is None
