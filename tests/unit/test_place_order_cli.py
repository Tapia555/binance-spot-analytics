from unittest.mock import patch

from cli.place_order import main


def test_preview_does_not_send_order(capsys):
    with patch("cli.place_order.BinanceTestnetClient") as client_class:
        result = main(
            [
                "--symbol",
                "BTCUSDT",
                "--side",
                "BUY",
                "--type",
                "LIMIT",
                "--quantity",
                "0.001",
                "--price",
                "50000",
            ]
        )

    output = capsys.readouterr().out

    assert result == 0
    assert "Order preview only" in output
    client_class.assert_not_called()


def test_confirm_sends_order():
    response = {
        "orderId": 123,
        "status": "NEW",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
    }

    with patch("cli.place_order.BinanceTestnetClient") as client_class:
        client_class.return_value._signed_request.return_value = response

        result = main(
            [
                "--symbol",
                "BTCUSDT",
                "--side",
                "BUY",
                "--type",
                "LIMIT",
                "--quantity",
                "0.001",
                "--price",
                "50000",
                "--confirm",
            ]
        )

    assert result == 0

    client_class.return_value._signed_request.assert_called_once_with(
        "POST",
        "/v3/order",
        params={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": "0.001",
            "newOrderRespType": "RESULT",
            "price": "50000",
            "timeInForce": "GTC",
        },
    )
