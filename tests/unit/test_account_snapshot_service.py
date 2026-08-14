from __future__ import annotations

from execution.account_snapshot_service import AccountSnapshotService
from execution.balance_store import BalanceStore


class DummyClient:
    def get_account(self):
        return {
            "balances": [
                {"asset": "BTC", "free": "0.01000000", "locked": "0.00000000"},
                {"asset": "USDT", "free": "1000.00000000", "locked": "25.00000000"},
            ]
        }


def test_refresh_updates_balance_store():
    store = BalanceStore()
    service = AccountSnapshotService(client=DummyClient(), store=store)

    balances = service.refresh()

    assert len(balances) == 2
    btc = store.get("BTC")
    usdt = store.get("USDT")

    assert btc is not None
    assert str(btc.free) == "0.01000000"
    assert str(btc.locked) == "0E-8"
    assert str(btc.total) == "0.01000000"

    assert usdt is not None
    assert str(usdt.free) == "1000.00000000"
    assert str(usdt.locked) == "25.00000000"
    assert str(usdt.total) == "1025.00000000"
