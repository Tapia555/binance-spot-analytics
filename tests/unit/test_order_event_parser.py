from decimal import Decimal

from src.execution.order_event_parser import parse_execution_report


def test_parse_execution_report():
    payload = {
        "e": "executionReport",
        "E": 1786180000000,
        "s": "BTCUSDT",
        "c": "client-order-1",
        "S": "BUY",
        "o": "LIMIT",
        "f": "GTC",
        "q": "0.00008",
        "p": "50000.00000000",
        "x": "NEW",
        "X": "NEW",
        "i": 12345,
        "l": "0.00000",
        "z": "0.00000",
        "L": "0.00000",
        "n": "0.00000000",
        "N": "BTC",
        "Z": "0.00000000",
    }

    update = parse_execution_report(payload)

    assert update.symbol == "BTCUSDT"
    assert update.order_id == 12345
    assert update.status == "NEW"
    assert update.side == "BUY"
    assert update.order_type == "LIMIT"
    assert update.executed_quantity == Decimal("0")
    assert update.cumulative_quote_quantity == Decimal("0")


def test_rejects_other_event_type():
    try:
        parse_execution_report({"e": "outboundAccountPosition"})
    except ValueError as error:
        assert "executionReport" in str(error)
    else:
        raise AssertionError("ValueError was not raised")
