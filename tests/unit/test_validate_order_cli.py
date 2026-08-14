from unittest.mock import patch

import pytest

from cli.validate_order import main


def test_validate_limit_order():
    with patch(
        "cli.validate_order.BinanceTestnetClient"
    ) as client_class:
        result = main(
            [
                "--symbol",
                "btcusdt",
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

    assert result == 0

    client_class.return_value.test_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        type="LIMIT",
        quantity="0.001",
        price="50000",
        timeInForce="GTC",
    )


def test_market_order_does_not_send_price():
    with patch(
        "cli.validate_order.BinanceTestnetClient"
    ) as client_class:
        result = main(
            [
                "--symbol",
                "BTCUSDT",
                "--side",
                "SELL",
                "--type",
                "MARKET",
                "--quantity",
                "0.001",
            ]
        )

    assert result == 0

    client_class.return_value.test_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="SELL",
        type="MARKET",
        quantity="0.001",
    )


def test_limit_order_requires_price():
    with pytest.raises(SystemExit, match="--price is required"):
        main(
            [
                "--side",
                "BUY",
                "--type",
                "LIMIT",
                "--quantity",
                "0.001",
            ]
        )


def test_quantity_must_be_positive():
    with pytest.raises(SystemExit, match="quantity"):
        main(
            [
                "--side",
                "BUY",
                "--type",
                "MARKET",
                "--quantity",
                "0",
            ]
        )
