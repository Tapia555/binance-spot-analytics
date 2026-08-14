from execution.order_events import parse_order_event


def test_parse_execution_report():
    event = parse_order_event(
        {
            "e": "executionReport",
            "s": "BTCUSDT",
            "i": 913476,
            "X": "CANCELED",
            "S": "BUY",
            "o": "LIMIT",
            "p": "50000.00000000",
            "q": "0.00100000",
            "z": "0.00000000",
        }
    )

    assert event is not None
    assert event.symbol == "BTCUSDT"
    assert event.order_id == 913476
    assert event.status == "CANCELED"
    assert event.side == "BUY"


def test_ignore_non_order_event():
    assert (
        parse_order_event(
            {
                "e": "outboundAccountPosition",
            }
        )
        is None
    )
