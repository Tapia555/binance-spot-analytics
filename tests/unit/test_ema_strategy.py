import pandas as pd

from strategy.ema_strategy import EmaStrategy
from strategy.models import SignalSide


def test_strategy_holds_with_insufficient_data():
    strategy = EmaStrategy(fast_period=2, slow_period=3)
    close = pd.Series([100.0, 101.0])

    signal = strategy.evaluate(close)

    assert signal.side is SignalSide.HOLD
    assert signal.reason == "not enough data"


def test_strategy_returns_signal():
    strategy = EmaStrategy(fast_period=2, slow_period=3)
    close = pd.Series(
        [100.0, 99.0, 98.0, 99.0, 101.0, 103.0],
    )

    signal = strategy.evaluate(close)

    assert signal.side in {
        SignalSide.BUY,
        SignalSide.SELL,
        SignalSide.HOLD,
    }
    assert signal.price == 103.0
