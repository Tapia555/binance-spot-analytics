from execution.execution_service import ExecutionService
from execution.trade_signal import TradeSignal


class RulesStub:
    def get_rules(self, symbol: str):
        return {
            "baseAsset": "BTC",
            "quoteAsset": "USDT",
            "priceFilter": {"tickSize": "0.01"},
            "lotSize": {"stepSize": "0.00001"},
        }


class OrderValidatorStub:
    def validate(self, price: str, quantity: str, rules: dict):
        pass


class RiskManagerStub:
    def require_allowed(self, symbol: str, quote_asset: str, rules: dict):
        pass


class ClientStub:
    def __init__(self):
        self.calls = []

    def place_limit_order(self, symbol, side, quantity, price):
        self.calls.append((symbol, side, quantity, price))
        return {"orderId": 123}


def test_place_limit_order_is_idempotent_for_same_signal():
    client = ClientStub()
    rules = RulesStub()
    validator = OrderValidatorStub()
    risk = RiskManagerStub()
    svc = ExecutionService(
        client,
        store=None,
        symbol_rules_service=rules,
        order_validator=validator,
        risk_manager=risk,
    )

    sig = TradeSignal(symbol="BTCUSDT", side="BUY", quantity="0.001", price="100000")
    r1 = svc.place_limit_order(sig)
    r2 = svc.place_limit_order(sig)

    assert r1["order_id"] == 123
    assert r2 == {"status": "duplicate_skipped"}
    assert len(client.calls) == 1
