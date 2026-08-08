import pytest

from src.execution.order_validator import (
    OrderValidationError,
    OrderValidator,
)


FILTERS = {
    "symbol": "BTCUSDT",
    "filters": [
        {
            "filterType": "PRICE_FILTER",
            "minPrice": "0.01",
            "maxPrice": "1000000",
            "tickSize": "0.01",
        },
        {
            "filterType": "LOT_SIZE",
            "minQty": "0.00001",
            "maxQty": "9000",
            "stepSize": "0.00001",
        },
        {
            "filterType": "NOTIONAL",
            "minNotional": "5",
            "maxNotional": "9000000",
        },
    ],
}


def test_valid_limit_order():
    OrderValidator(FILTERS).validate(
        order_type="LIMIT",
        quantity="0.001",
        price="50000",
    )


@pytest.mark.parametrize(
    ("quantity", "price", "message"),
    [
        ("0.000001", "50000", "minQty"),
        ("0.001001", "50000", "stepSize"),
        ("0.001", "50000.001", "tickSize"),
        ("0.00001", "50000", "notional"),
    ],
)
def test_invalid_limit_order(quantity, price, message):
    with pytest.raises(
        OrderValidationError,
        match=message,
    ):
        OrderValidator(FILTERS).validate(
            order_type="LIMIT",
            quantity=quantity,
            price=price,
        )


def test_limit_requires_price():
    with pytest.raises(
        OrderValidationError,
        match="price is required",
    ):
        OrderValidator(FILTERS).validate(
            order_type="LIMIT",
            quantity="0.001",
        )
