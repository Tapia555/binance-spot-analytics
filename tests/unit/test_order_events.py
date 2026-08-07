import pytest

from src.data.order_events import (
    OrderStatus,
    parse_execution_report,
)


def test_parse_execution_report():
    payload = {
        "e": "executionReport",
        "E": 1700000000000,
        "s": "BTCUSDT",
        "S": "BUY",
        "o": "LIMIT",
        "X": "FILLED",
        "i": 12345,
        "p": "64000.00",
        "q": "0.00100",
        "z": "0.00100",
    }

    update = parse_execution_report(payload)

    assert update.symbol == "BTCUSDT"
    assert update.order_id == 12345
    assert update.status is OrderStatus.FILLED
    assert update.price == pytest.approx(64000.0)
    assert update.quantity == pytest.approx(0.001)
    assert update.executed_quantity == pytest.approx(0.001)


def test_reject_unknown_event():
    with pytest.raises(ValueError):
        parse_execution_report({"e": "kline"})
