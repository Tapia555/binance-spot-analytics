from decimal import Decimal

from src.execution.account_store import AccountStore


def test_account_store_updates_balances():
    store = AccountStore()

    accepted = store.apply_event(
        {
            "subscriptionId": 0,
            "event": {
                "e": "outboundAccountPosition",
                "E": 1786188488068,
                "u": 1786188488068,
                "B": [
                    {
                        "a": "BTC",
                        "f": "1.00000000",
                        "l": "0.00000000",
                    },
                    {
                        "a": "USDT",
                        "f": "9994.00000000",
                        "l": "6.00000000",
                    },
                ],
            },
        }
    )

    assert accepted is True

    usdt = store.get("USDT")

    assert usdt is not None
    assert usdt.free == Decimal("9994.00000000")
    assert usdt.locked == Decimal("6.00000000")
    assert store.last_update_ms == 1786188488068


def test_account_store_ignores_other_events():
    store = AccountStore()

    accepted = store.apply_event(
        {
            "event": {
                "e": "executionReport",
            }
        }
    )

    assert accepted is False
    assert store.all() == []
