from decimal import Decimal

from src.execution.execution_state import ExecutionState


def test_state_applies_order_event():
    state = ExecutionState()

    event = {
        "subscriptionId": 0,
        "event": {
            "e": "executionReport",
            "E": 1786180000000,
            "s": "BTCUSDT",
            "c": "client-order-1",
            "S": "BUY",
            "o": "LIMIT",
            "X": "NEW",
            "x": "NEW",
            "i": 123,
            "z": "0.00000",
            "Z": "0.00000000",
        },
    }

    assert state.apply_event(event) == "executionReport"

    snapshot = state.snapshot()

    assert len(snapshot.orders) == 1
    assert snapshot.orders[0].order_id == 123
    assert snapshot.orders[0].status == "NEW"


def test_state_applies_balance_event():
    state = ExecutionState()

    event = {
        "subscriptionId": 0,
        "event": {
            "e": "outboundAccountPosition",
            "E": 1786180000000,
            "u": 1786180000000,
            "B": [
                {
                    "a": "USDT",
                    "f": "9994.00000000",
                    "l": "6.00000000",
                },
            ],
        },
    }

    assert state.apply_event(event) == (
        "outboundAccountPosition"
    )

    snapshot = state.snapshot()

    assert len(snapshot.balances) == 1
    assert snapshot.balances[0].asset == "USDT"
    assert snapshot.balances[0].free == Decimal("9994.00000000")
    assert snapshot.balances[0].locked == Decimal("6.00000000")


def test_state_ignores_unknown_event():
    state = ExecutionState()

    assert state.apply_event({"event": {"e": "unknown"}}) is None
    assert state.snapshot().orders == ()
    assert state.snapshot().balances == ()
