from unittest.mock import Mock

from execution.account_store import AccountStore
from execution.order_store import OrderStore
from execution.state_sync import StateSynchronizer


def test_state_sync_loads_account_and_open_orders():
    client = Mock()

    client.get_account.return_value = {
        "updateTime": 123456,
        "balances": [
            {
                "asset": "USDT",
                "free": "10000.00000000",
                "locked": "0.00000000",
            },
        ],
    }

    client.get_open_orders.return_value = [
        {
            "symbol": "BTCUSDT",
            "orderId": 99,
            "status": "NEW",
            "side": "BUY",
            "type": "LIMIT",
            "executedQty": "0.00000",
            "cummulativeQuoteQty": "0.00000000",
            "updateTime": 123456,
            "time": 123456,
        },
    ]

    account_store = AccountStore()
    order_store = OrderStore()

    StateSynchronizer(
        client=client,
        order_store=order_store,
        account_store=account_store,
    ).sync("BTCUSDT")

    assert account_store.get("USDT").free == 10000
    assert order_store.get(99).status == "NEW"
    client.get_open_orders.assert_called_once_with(
        symbol="BTCUSDT",
    )
