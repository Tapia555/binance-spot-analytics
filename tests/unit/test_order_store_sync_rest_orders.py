from execution.order_store import OrderStore


def test_sync_rest_orders_updates_store():
    store = OrderStore()

    store.sync_rest_orders(
        [
            {
                "symbol": "BTCUSDT",
                "orderId": 123,
                "status": "NEW",
                "side": "BUY",
                "type": "LIMIT",
                "executedQty": "0.00000",
                "cummulativeQuoteQty": "0.00000000",
                "updateTime": 1786180000000,
            }
        ]
    )

    update = store.get(123)
    assert update is not None
    assert update.status == "NEW"
