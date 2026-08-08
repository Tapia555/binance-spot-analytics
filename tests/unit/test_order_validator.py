from src.execution.order_validator import validate_limit_order


FILTERS = {
    "PRICE_FILTER": {
        "minPrice": "0.01000000",
        "maxPrice": "1000000.00000000",
        "tickSize": "0.01000000",
    },
    "LOT_SIZE": {
        "minQty": "0.00001000",
        "maxQty": "9000.00000000",
        "stepSize": "0.00001000",
    },
    "NOTIONAL": {
        "minNotional": "5.00000000",
    },
}


def test_valid_order():
    result = validate_limit_order(
        price="50000.00",
        quantity="0.00012",
        filters=FILTERS,
    )

    assert result.valid is True
    assert result.errors == ()


def test_rejects_small_notional():
    result = validate_limit_order(
        price="50000.00",
        quantity="0.00008",
        filters=FILTERS,
    )

    assert result.valid is False
    assert "order notional below minimum" in result.errors


def test_rejects_bad_price_step():
    result = validate_limit_order(
        price="50000.001",
        quantity="0.00012",
        filters=FILTERS,
    )

    assert result.valid is False
    assert "price violates tickSize" in result.errors


def test_rejects_bad_quantity_step():
    result = validate_limit_order(
        price="50000.00",
        quantity="0.000121",
        filters=FILTERS,
    )

    assert result.valid is False
    assert "quantity violates stepSize" in result.errors
