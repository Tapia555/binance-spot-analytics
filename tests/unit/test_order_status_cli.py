from unittest.mock import patch

from cli.order_status import main


def test_order_status_queries_order(capsys):
    response = {
        "orderId": 913476,
        "status": "CANCELED",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "price": "50000.00000000",
        "origQty": "0.00100000",
        "executedQty": "0.00000000",
    }

    with patch("cli.order_status.BinanceTestnetClient") as client_class:
        client_class.return_value.get_order.return_value = response

        result = main(
            [
                "--symbol",
                "btcusdt",
                "--order-id",
                "913476",
            ]
        )

    assert result == 0
    client_class.return_value.get_order.assert_called_once_with(
        symbol="BTCUSDT",
        order_id=913476,
    )

    output = capsys.readouterr().out
    assert "CANCELED" in output
    assert "913476" in output


def test_order_id_must_be_positive():
    try:
        main(
            [
                "--symbol",
                "BTCUSDT",
                "--order-id",
                "0",
            ]
        )
    except SystemExit as error:
        assert "order-id" in str(error)
    else:
        raise AssertionError("Expected SystemExit")
