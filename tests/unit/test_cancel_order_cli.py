from unittest.mock import patch

from cli.cancel_order import main


def test_cancel_preview_does_not_send():
    with patch("cli.cancel_order.BinanceTestnetClient") as client_class:
        result = main(
            [
                "--symbol",
                "btcusdt",
                "--order-id",
                "123",
            ]
        )

    assert result == 0
    client_class.assert_not_called()


def test_cancel_confirm_sends_request(capsys):
    response = {
        "orderId": 123,
        "status": "CANCELED",
        "symbol": "BTCUSDT",
        "side": "BUY",
    }

    with patch("cli.cancel_order.BinanceTestnetClient") as client_class:
        client_class.return_value.cancel_order.return_value = response

        result = main(
            [
                "--symbol",
                "BTCUSDT",
                "--order-id",
                "123",
                "--confirm",
            ]
        )

    assert result == 0
    client_class.return_value.cancel_order.assert_called_once_with(
        symbol="BTCUSDT",
        order_id=123,
    )

    output = capsys.readouterr().out
    assert "CANCELED" in output


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
