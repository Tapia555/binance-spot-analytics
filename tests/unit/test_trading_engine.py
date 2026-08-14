from __future__ import annotations

from strategy.ma_crossover_strategy import StrategyAction, StrategySignal
from strategy.trading_engine import TradingEngine


class DummyStrategy:
    def __init__(self, action: StrategyAction):
        self.action = action

    def generate(self, symbol, closes):
        return StrategySignal(self.action, symbol, "test")


class DummyExecutionService:
    def __init__(self):
        self.received = None

    def place_limit_order(self, trade_signal):
        self.received = trade_signal
        return {"order_id": 12345, "raw": {"status": "NEW"}}


def test_on_closes_holds_on_hold_signal():
    engine = TradingEngine(
        strategy=DummyStrategy(StrategyAction.HOLD),
        execution_service=DummyExecutionService(),
    )

    result = engine.on_closes("BTCUSDT", [1, 2, 3, 4, 5])

    assert result is None


def test_on_closes_places_order_on_buy_signal():
    execution = DummyExecutionService()
    engine = TradingEngine(
        strategy=DummyStrategy(StrategyAction.BUY),
        execution_service=execution,
    )

    result = engine.on_closes("BTCUSDT", [1, 2, 3, 4, 5, 6])

    assert result["order_id"] == 12345
    assert execution.received.symbol == "BTCUSDT"
    assert execution.received.side == "BUY"
    assert execution.received.quantity == "0.00020"
    assert execution.received.price == "6"


def test_on_closes_places_order_on_sell_signal():
    execution = DummyExecutionService()
    engine = TradingEngine(
        strategy=DummyStrategy(StrategyAction.SELL),
        execution_service=execution,
    )

    result = engine.on_closes("BTCUSDT", [1, 2, 3, 4, 5, 6])

    assert result["order_id"] == 12345
    assert execution.received.side == "SELL"
