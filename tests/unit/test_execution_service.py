from unittest.mock import Mock

import pytest

from src.execution.execution_service import ExecutionService
from src.execution.order_store import OrderStore


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


def test_submit_limit_order():
    client = Mock()

    client.place_limit_order.return_value = {
        "symbol": "BTCUSDT",
        "orderId": 123,
        "status": "NEW",
        "side": "BUY",
        "origQty": "0.00012",
        "price": "50000.00",
    }

    service = ExecutionService(
        client=client,
        order_store=OrderStore(),
    )

    result = service.submit_limit_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity="0.00012",
        price="50000.00",
        filters=FILTERS,
    )

    assert result.order_id == 123
    assert result.status == "NEW"
    client.place_limit_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        quantity="0.00012",
        price="50000.00",
    )


def test_submit_rejects_invalid_order_before_api_call():
    client = Mock()

    service = ExecutionService(
        client=client,
        order_store=OrderStore(),
    )

    with pytest.raises(ValueError, match="notional"):
        service.submit_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity="0.00008",
            price="50000.00",
            filters=FILTERS,
        )

    client.place_limit_order.assert_not_called()
