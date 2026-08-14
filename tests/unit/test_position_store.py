from __future__ import annotations

from decimal import Decimal

from execution.position_store import PositionStore


def test_apply_execution_report_creates_position():
    store = PositionStore()

    store.apply_execution_report(
        {
            "s": "BTCUSDT",
            "S": "BUY",
            "X": "NEW",
            "q": "0.00020",
            "z": "0.00000",
            "Z": "0.00000",
        }
    )

    pos = store.get("BTCUSDT")
    assert pos is not None
    assert pos.symbol == "BTCUSDT"
    assert pos.side == "BUY"
    assert pos.quantity == Decimal("0.00020")
    assert pos.filled_quantity == Decimal("0.00000")
    assert pos.average_price == Decimal("0")
    assert pos.status == "NEW"
    assert not pos.is_open


def test_apply_execution_report_updates_partial_fill():
    store = PositionStore()

    store.apply_execution_report(
        {
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
    assert pos.filled_quantity == Decimal("0.00010")
    assert pos.average_price == Decimal("50000")
    assert pos.is_open


def test_apply_execution_report_marks_filled():
    store = PositionStore()

    store.apply_execution_report(
        {
            "s": "BTCUSDT",
            "S": "BUY",
            "X": "FILLED",
            "q": "0.00020",
            "z": "0.00020",
            "Z": "10.00000",
        }
    )

    pos = store.get("BTCUSDT")
    assert pos is not None
    assert pos.status == "FILLED"
    assert pos.filled_quantity == Decimal("0.00020")
    assert pos.average_price == Decimal("50000")
    assert pos.is_open
